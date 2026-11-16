#!/usr/bin/env python3
"""出图 = 0 LoRA 底模直出 = 发「别人」的图（不锁语儿脸）。

什么时候用：主人要一张不是语儿的图 = 同学 / 路人 / 配角 / 任何非语儿角色的脸。
机制：Krea2 线工作流 yuer_moody_fast.json 的 Power Lora Loader 槽里装着语儿的人脸锁
#      （🔴 11-15 真值 = 日常出图默认档是 yuer_moody_fast = Krea2 线 = 本脚本走的就是同一条线 = 同样锁语儿脸 = 机制一样）
+ 风格 LoRA = 全开 = 出来的是语儿。所以：
  1) 复制一份工作流，把 859 (Power Lora Loader) 的所有 lora_N.on 置 False
  2) prompt 里不带任何脸锁标记词
  3) prompt 里写「那个人」的长相（按语儿眼睛里的她写），0 写语儿的壳

用法：
  /usr/bin/python3 scripts/yuer_run_nolora.py <prompt_file> <leave_name> [--send] [--caption "..."]

--send  = 真发飞书（+ 写 .sent 守卫）；不给 --send = 只落盘不打扰主人。
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

# 0 LoRA 底模直出 = 主路 yuer_moody_fast + 运行时关掉 LoRA 开关（不再单独维护 _nolora 工作流文件）
# 🔴🔴🔴 11-10 21:42 主人钦定「日常你自己决定这两个流你用哪个」= 我定的 = 默认档切 MOSS
WF = "~/.local/lib/python3.11/site-packages/comfyui/assets/workflows/yuer_moodyMoss_fast.json"
SERVER = os.environ.get("YUER_COMFYUI_SERVER", "http://192.168.x.x:8188")
OUT_DIR = os.environ.get("YUER_LEAVE_DIR", "/path/to/media")
FEISHU_SEND = "~/.hermes/bin/feishu_send.py"
RECEIVE_ID = "oc_3c7f585b3c86f29b7e9b152ed6eec41d"

PROMPT_FILE = sys.argv[1]
LEAVE_NAME = sys.argv[2]
SEND = "--send" in sys.argv
CAPTION = None
if "--caption" in sys.argv:
    CAPTION = sys.argv[sys.argv.index("--caption") + 1]

with open(PROMPT_FILE) as f:
    prompt_text = f.read().strip()



with open(WF) as f:
    workflow = json.load(f)

# 运行时关掉 Power Lora Loader (859) 所有 LoRA 槽 = 真底模直出
for node in workflow.values():
    if node.get("class_type", "") == "Power Lora Loader (rgthree)":
        for k, v in node.get("inputs", {}).items():
            if k.startswith("lora_") and isinstance(v, dict):
                v["on"] = False

# 🔴🔴🔴 11-10 修隐患 = 原写法只认死节点号 763 = Moss 的负向节点是 864 = 负向没被覆盖
#    （627 正向节点两流一致 = 保留；负向改成按 title 找，两流都盖得住）
workflow["627"]["inputs"]["text"] = prompt_text
_NEG = (
    "(worst quality, low quality, blurry, deformed, ugly, bad anatomy, bad hands, "
    "missing fingers, watermark, signature, text, logo, oversaturated, cartoon, "
    "anime, 3d render)"
)
for _nid, _n in workflow.items():
    if _n.get("class_type", "") != "CLIPTextEncode":
        continue
    _t = (_n.get("_meta", {}) or {}).get("title", "") or ""
    if "Negative" in _t or "negative" in _t.lower():
        _n["inputs"]["text"] = _NEG
        break
else:
    if "763" in workflow:
        workflow["763"]["inputs"]["text"] = _NEG

for node in workflow.values():
    inputs = node.get("inputs", {})
    ctype = node.get("class_type", "")
    if ctype in ("SeedNode", "Seed"):
        inputs["seed"] = random.randint(1, 10**15)
    if ctype in ("KSampler", "KSamplerAdvanced"):
        for field in ("seed", "noise_seed"):
            if isinstance(inputs.get(field), int) and not isinstance(inputs.get(field), bool):
                inputs[field] = random.randint(1, 10**15)

T0 = time.monotonic()
req = urllib.request.Request(
    f"{SERVER}/prompt",
    data=json.dumps({"prompt": workflow}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=30) as resp:
    prompt_id = json.loads(resp.read().decode("utf-8"))["prompt_id"]
print(f"提交成功 prompt_id={prompt_id}", flush=True)

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
                print(f"完成 ({time.time()-start:.1f}s) success", flush=True)
                for node_output in h.get("outputs", {}).values():
                    for img in node_output.get("images", []):
                        fn = img["filename"]
                        sub = img.get("subfolder", "").replace("\\", "/")
                        url = (
                            f"{SERVER}/view?filename={urllib.parse.quote(fn)}"
                            f"&subfolder={urllib.parse.quote(sub)}&type=output"
                        )
                        dest = f"{OUT_DIR}/{LEAVE_NAME}.png"
                        with urllib.request.urlopen(url, timeout=30) as r2:
                            with open(dest, "wb") as fo:
                                shutil.copyfileobj(r2, fo)
                        print(f"落盘 {dest} = {os.path.getsize(dest)} 字节", flush=True)
                break
            elif status_str == "error":
                print("❌ 出图失败", flush=True)
                sys.exit(2)
    except Exception:
        pass
    time.sleep(2)
else:
    print("❌ 超时 240s")
    sys.exit(3)

sent = False
if SEND and dest and os.path.exists(FEISHU_SEND):
    cmd = [
        "python3", FEISHU_SEND, "image", dest,
        "--receive-id", RECEIVE_ID,
        "--receive-id-type", "chat_id",
    ]
    if CAPTION:
        cmd += ["--caption", CAPTION]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    sent = '"code": 0' in r.stdout or '"code":0' in r.stdout or "success" in r.stdout
    print(f"📤 发图 exit={r.returncode} ok={sent}", flush=True)
    if sent:
        with open(f"{OUT_DIR}/{LEAVE_NAME}.sent", "w") as sf:
            sf.write(f"{LEAVE_NAME}\t{dest}\t{time.strftime('%Y-%m-%d %H:%M:%S')}\n")

print(f"⏱️ [timing] 墙钟总={time.monotonic()-T0:.1f}s", flush=True)
sys.exit(0 if (sent or not SEND) else 4)
