#!/usr/bin/env python3
"""出图 = 0 LoRA 底模直出 = 画「别人」（不是语儿）。

为什么需要这个入口：
  · yuer_ka_fast.sh / yuer_run_one_brief.run() 都只认唯一那份 yuer_moody_fast，
    且都会挂上人脸锁 LoRA = 出来必然是语儿的脸。
  · 主人要出「不是语儿的人」（同学 / 路人 / 闺蜜 / 配角）= 必须 ① 全关 LoRA
    ② 卸掉人脸锁 = 否则锁脸把外人扭成语儿。
  · 🔴 11-07 08:41 = 变体副本全删 = 这个脚本是画外人的**唯一**入口（不再有 yuer_moody_fast_nolora 副本）。

用法:
  /usr/bin/python3 yuer_run_nolora.py <prompt_file> <leave_name> [--send] [--caption "..."]

行为:
  · 读 yuer_moody_fast.json → 内存里把所有 lora_N 的 on 置 false（不改磁盘工作流，
    别的 agent 的目录不碰）

  · 随机 seed → 提交 → 轮询 → 落盘 /path/to/media/<leave_name>.png
  · --send = 发飞书 + 写 .sent 守卫标记（同一个 leave_name 已发过 = exit 5 拒发）

退出码: 0 = 出图成功（发了或没要求发）/ 2 = ComfyUI 报错 / 3 = 超时 / 4 = 发图失败 / 5 = .sent 守卫命中
"""
import json
import os
import random
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

# 🔴🔴🔴 11-10 21:42 主人钦定「日常你自己决定这两个流你用哪个」= 我定的 = 默认档切 MOSS
#    （画外人 = 画别人 = 0 锁脸 = 底模原味 = 跟日常出图同一条流 = 免得两套审美）
WF_PATH = os.environ.get(
    "YUER_NOLORA_WORKFLOW",
    "~/.local/lib/python3.11/site-packages/comfyui/assets/workflows/yuer_moodyMoss_fast.json",
)
SERVER = os.environ.get("YUER_COMFYUI_SERVER", "http://192.168.x.x:8188")
OUT_DIR = os.environ.get("YUER_LEAVE_DIR", "/path/to/media")
FEISHU_SEND = "~/.hermes/bin/feishu_send.py"
RECEIVE_ID = os.environ.get("YUER_RECEIVE_ID", "oc_3c7f585b3c86f29b7e9b152ed6eec41d")

NEGATIVE = ("(worst quality, low quality, blurry, deformed, ugly, bad anatomy, bad hands, "
            "missing fingers, watermark, signature, text, logo, oversaturated, cartoon, anime, 3d render)")


def arg_after(flag, default=None):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    prompt_file, leave_name = sys.argv[1], sys.argv[2]
    send = "--send" in sys.argv
    caption = arg_after("--caption")

    sent_mark = os.path.join(OUT_DIR, f"{leave_name}.sent")
    if os.path.exists(sent_mark) and "--force" not in sys.argv:
        print(f"❌ .sent 守卫：{leave_name} 已真发过飞书 = 不重复发图。换个 leave_name 或加 --force。")
        return 5

    with open(prompt_file, encoding="utf-8") as f:
        prompt_text = f.read().strip()

    with open(WF_PATH, encoding="utf-8") as f:
        workflow = json.load(f)

    # 全关 LoRA（内存副本 = 磁盘工作流不动）
    for node in workflow.values():
        for key, val in node.get("inputs", {}).items():
            if key.startswith("lora_") and isinstance(val, dict) and "on" in val:
                val["on"] = False

    # 🔴🔴🔴 11-10 修隐患 = 原写法把 prompt 写进【所有】CLIPTextEncode
    #    Krea2 只有 1 个 CLIPTextEncode（627）= 碰巧没事
    #    Moss 有 2 个（627 正 + 864 负 "CLIP Text Encode (Prompt) Negative"）
    #    = prompt 灌进负向节点 = 画面反向崩坏 = 现按 title 分流，只写正向
    _pos_id = None
    for nid, node in workflow.items():
        if node.get("class_type", "") != "CLIPTextEncode":
            continue
        _t = (node.get("_meta", {}) or {}).get("title", "") or ""
        if "Negative" in _t or "negative" in _t.lower():
            continue
        _pos_id = nid
        break
    if _pos_id is None:
        print("❌ 找不到正向 CLIPTextEncode 节点 = 中止", flush=True)
        return 2

    for nid, node in workflow.items():
        ctype = node.get("class_type", "")
        inputs = node.get("inputs", {})
        if ctype == "CLIPTextEncode" and nid == _pos_id:
            inputs["text"] = prompt_text
        if ctype in ("SeedNode", "Seed") or (
            isinstance(inputs.get("seed"), int) and not isinstance(inputs.get("seed"), bool)
        ):
            inputs["seed"] = random.randint(1, 10**15)
        if ctype in ("KSampler", "KSamplerAdvanced"):
            for field in ("seed", "noise_seed"):
                if isinstance(inputs.get(field), int) and not isinstance(inputs.get(field), bool):
                    inputs[field] = random.randint(1, 10**15)
    # 🔴 负向节点 = 按 title 找（Krea2 旧号 763 / Moss = 864）= 0 写死节点号
    for nid, node in workflow.items():
        if node.get("class_type", "") != "CLIPTextEncode":
            continue
        _t = (node.get("_meta", {}) or {}).get("title", "") or ""
        if "Negative" in _t or "negative" in _t.lower():
            node["inputs"]["text"] = NEGATIVE
            break

    t0 = time.monotonic()
    req = urllib.request.Request(
        f"{SERVER}/prompt",
        data=json.dumps({"prompt": workflow}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        prompt_id = json.loads(resp.read().decode("utf-8"))["prompt_id"]
    print(f"提交成功 prompt_id={prompt_id} (0 LoRA)", flush=True)

    dest = ""
    start = time.time()
    while time.time() - start < 240:
        try:
            with urllib.request.urlopen(f"{SERVER}/history/{prompt_id}", timeout=10) as resp:
                history = json.loads(resp.read().decode("utf-8"))
            if prompt_id in history:
                h = history[prompt_id]
                status_str = h.get("status", {}).get("status_str", "")
                if status_str == "success":
                    print(f"完成 ({time.time() - start:.1f}s) success", flush=True)
                    for node_output in h.get("outputs", {}).values():
                        for img in node_output.get("images", []):
                            fn = img["filename"]
                            sub = img.get("subfolder", "").replace("\\", "/")
                            url = (f"{SERVER}/view?filename={urllib.parse.quote(fn)}"
                                   f"&subfolder={urllib.parse.quote(sub)}&type=output")
                            dest = os.path.join(OUT_DIR, f"{leave_name}.png")
                            with urllib.request.urlopen(url, timeout=30) as r2:
                                with open(dest, "wb") as fo:
                                    shutil.copyfileobj(r2, fo)
                            print(f"落盘 {dest} = {os.path.getsize(dest)} 字节", flush=True)
                    break
                if status_str == "error":
                    print(f"❌ 出图失败: {status_str}", flush=True)
                    return 2
        except Exception:
            pass
        time.sleep(2)
    else:
        print("❌ 超时 240s")
        return 3

    if not send:
        print(f"⏱️ [timing] 墙钟总={time.monotonic() - t0:.1f}s (未发飞书)")
        return 0

    cmd = ["python3", FEISHU_SEND, "image", dest, "--receive-id", RECEIVE_ID,
           "--receive-id-type", "chat_id"]
    if caption:
        cmd += ["--caption", caption]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    ok = '"code": 0' in r.stdout or '"code":0' in r.stdout or "success" in r.stdout
    print(f"📤 发图 exit={r.returncode} ok={ok}", flush=True)
    if ok:
        with open(sent_mark, "w", encoding="utf-8") as sf:
            sf.write(f"{leave_name}\t{dest}\t{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"⏱️ [timing] 墙钟总={time.monotonic() - t0:.1f}s")
    return 0 if ok else 4


if __name__ == "__main__":
    sys.exit(main())
