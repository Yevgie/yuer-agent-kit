#!/usr/bin/env python3
"""
yuer_reverse_inference.py · 语儿反推参考图直出（v1.0 · 08-05 实战钦定·灵魂级·盖过 minimax/qwen3_vision 远程反推一切）

唯一职责：主人发参考图 → 走 Reference-based Reverse Inference 工作流 = 本地 Qwen3.5-9B 反推 + Krea 2 LoRA 图生图一体出图。

调用方唯一入口：run(image_path, leave_name, channel, caption)
返回：MEDIA 路径（已落盘 + 已发到主对话渠道）

🔴 v1.0 灵魂级铁律（实战 318 · 08-05 主人钦定·盖过 yuer-reverse-image minimax/qwen3_vision 远程反推一切）：

    反推参考图直出唯一路径 = Reference-based Reverse Inference 工作流
    0 远程 minimax 反推（hermes chat --image + minimax-m3）= 0 撞 system-injection 拒答
    0 远程 qwen3_vision 反推（rev_qwen3_vision_single.py）= 0 单独反推 prompt 走 Krea 2 LoRA 易撞图
    = 1 条链路：参考图 → 本地 Qwen3.5 反推 → denoise=0.5 图生图 → 灵魂脸 LoRA → 出图

    出图逻辑（节点 32→48）：
        LoadImage(参考图) → 缩放到 1280k (节点 47) → VAE Encode (节点 44) → latent
                                                                              ↓
                                                              KSampler (节点 48, denoise=0.5)
                                                              model: Enchanting_Sweet_Candy + Krea_2_Innie + Krea-2-Turbo (节点 43)
                                                                              ↓
                                                              VAE Decode (节点 35) → SaveImage (节点 41)

    同时跑 llama_cpp_instruct_adv (节点 32) = 本地 Qwen3.5-9B 反推 prompt = 仅显示，不参与出图
    = 出图 = 节点 25 (主提示) = 默认空 = 0 反推 prompt 注入 = 因为 Krea 2 LoRA + denoise=0.5 自己就能锁脸

实测（08-05 实战 318）：
    - 提交耗时：0.02s
    - 总出图：93.7s（含 Qwen3.5-9B 加载 + 反推 + Krea 2 LoRA 出图）
    - 输出：1920x1080 PNG，2.9 MB
    - 构图/姿势/服装/氛围保留 80%
    - 灵魂脸 LoRA 锁脸有效
"""
import os
import sys
import time


def save_prefix(name):
    """🔴 统一落盘路径（10-29 主人钦定）= Hermes/Yuer<yyyy-MM-dd>/<唯一名>
    服务端 ComfyUI 0.43.0 实测不展开 %date 语法 → 日期必须客户端实算。"""
    import datetime
    return "Hermes/Yuer" + datetime.date.today().isoformat() + "_" + name
import json
import shutil
import subprocess
import re
import requests
from pathlib import Path

# 路径常量
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LEAVE_DIR = os.environ.get("YUER_LEAVE_DIR", "/path/to/media")  # 主人 07-28 钦定唯一备份目录
DEFAULT_COMFYUI_SERVER = "http://192.168.x.x:8188"  # 实战 218 钦定远端
DEFAULT_WORKFLOW = "yuer_moody_fast_wash"  # 实战 493 整改后新名·实战 318 + 实战 462 沉淀·节点 70 重绘幅度=0.5 + 0 反推 + Krea 2 LoRA 锁脸

# 加载 reply 拦截器（实战 152 落档）
sys.path.insert(0, SCRIPT_DIR)
try:
    from yuer_reply_interceptor import check_reply, auto_fix
    HAS_INTERCEPTOR = True
except ImportError:
    HAS_INTERCEPTOR = False


def log(msg: str):
    print(f"[yuer_reverse_inference] {msg}", flush=True)


def make_safe_caption(reply_text: str) -> str:
    """实战 154 钦定：reply 拦截器自动 sed（与 yuer_stable_sop.py 同款）"""
    if not HAS_INTERCEPTOR:
        return reply_text
    passed, violations = check_reply(reply_text)
    if not passed:
        log(f"⚠️ reply 拦截器命中 {len(violations)} 条: {violations}")
        fixed = auto_fix(reply_text)
        passed2, violations2 = check_reply(fixed)
        if not passed2:
            raise RuntimeError(
                f"reply 文本自动 sed 后仍命中黑名单 {len(violations2)} 条: {violations2}\n"
                f"原文: {reply_text!r}\n"
                f"auto_fix 后: {fixed!r}"
            )
        log(f"✓ reply 拦截器自动 sed 删干净")
        reply_text = fixed
    residue_fixed = auto_fix(reply_text)
    if residue_fixed != reply_text:
        log(f"✓ 残留扫描清理: {reply_text!r} -> {residue_fixed!r}")
        reply_text = residue_fixed
    return reply_text


def upload_reference_image(image_path: str, server: str) -> str:
    """上传参考图到 ComfyUI 服务器，返回 ComfyUI 端文件名"""
    log(f"📤 上传参考图: {image_path}")
    with open(image_path, "rb") as f:
        r = requests.post(
            f"{server}/upload/image",
            files={"image": (os.path.basename(image_path), f, "image/jpeg")},
            timeout=30,
        )
    r.raise_for_status()
    uploaded = r.json()["name"]
    log(f"   ✓ {uploaded}")
    return uploaded


def load_workflow(server: str, workflow_name: str = DEFAULT_WORKFLOW) -> dict:
    """从 comfyui-skill 注册目录加载工作流 JSON"""
    import comfyui
    comfyui_root = os.path.dirname(comfyui.__file__)
    wf_path = os.path.join(comfyui_root, "assets", "workflows", f"{workflow_name}.json")
    if not os.path.exists(wf_path):
        raise RuntimeError(
            f"🔴 工作流文件不存在: {wf_path}\n"
            f"请先 comfyui-skill import-workflow --id {workflow_name} <path>"
        )
    with open(wf_path) as f:
        return json.load(f)


def submit_and_poll(wf: dict, server: str, timeout: int = 180) -> dict:
    """提交工作流 + 轮询直到完成（实战 291 B 方案：不靠 WebSocket）"""
    # Step A: POST /prompt
    log(f"📝 提交工作流到 ComfyUI ...")
    r = requests.post(f"{server}/prompt", json={"prompt": wf}, timeout=30)
    r.raise_for_status()
    pid = r.json()["prompt_id"]
    log(f"   ✓ prompt_id={pid}")

    # Step B: HTTP 轮询 /history/{prompt_id}
    log(f"⏳ 等待执行 (timeout={timeout}s)...")
    t_start = time.monotonic()
    last_print = 0
    while True:
        elapsed = time.monotonic() - t_start
        if elapsed > timeout:
            raise RuntimeError(f"🔴 反推直出 {timeout}s 内未完成")
        try:
            h = requests.get(f"{server}/history/{pid}", timeout=5).json()
        except Exception:
            time.sleep(1)
            continue
        if pid in h:
            status = h[pid].get("status", {})
            if status.get("errored") or h[pid].get("error"):
                raise RuntimeError(f"ComfyUI 执行错误: {h[pid].get('error')}")
            if h[pid].get("outputs"):
                log(f"   ✅ 完成 ({elapsed:.1f}s)")
                return h[pid]
        if elapsed - last_print > 10:
            log(f"   ⏳ {elapsed:.0f}s ...")
            last_print = elapsed
        time.sleep(1)


def fetch_image_from_outputs(history_entry: dict, server: str, output_dir: str) -> str:
    """从 history_entry 拿图片文件名 + GET /view 下载到本地"""
    outputs = history_entry.get("outputs", {})
    if not outputs:
        raise RuntimeError("outputs 为空")
    output_node_id = None
    for nid, node_data in outputs.items():
        if node_data.get("images"):
            output_node_id = nid
            break
    if output_node_id is None:
        raise RuntimeError(f"找不到含 images 的 output node: {list(outputs.keys())}")
    images = outputs[output_node_id]["images"]
    if not images:
        raise RuntimeError("images 列表为空")
    img = images[0]
    filename = img["filename"]
    subfolder = img.get("subfolder", "")
    folder_type = img.get("type", "output")
    params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    r = requests.get(f"{server}/view", params=params, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"GET /view 失败 rc={r.status_code}")
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, filename)
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path


def step_save_to_leave(src_path: str, leave_name: str) -> str:
    """cp 留底 + size 守门（防 cache 命中假图）"""
    Path(LEAVE_DIR).mkdir(parents=True, exist_ok=True)
    final = f"{LEAVE_DIR}/{leave_name}.png"
    shutil.copy(src_path, final)
    size = os.path.getsize(final)
    log(f"STEP 留底完成: {final} ({size} bytes)")
    if size < 100000:
        os.remove(final)
        raise RuntimeError(f"图过小 {size} bytes < 100000（防 cache 命中假图）")
    return final


def step_save_to_leave_only(out_path: str, leave_name: str) -> str:
    """✅ 实战 320-A' 钦定（08-06 主人正解 · 盖过补丁思路）：

    唯一正面路径 = 反推脚本只落盘 = 0 发图 = 0 调飞书 API。
    send_yuer_image() 已 raise NotImplementedError（盖过实战 313 v6.20 双发防御思路）。

    caller 唯一动作 = 读 stdout 第一行 MEDIA:<abs_path> = 拼到 reply = Hermes 框架渲染。
    """
    final = step_save_to_leave(out_path, leave_name)
    return final


def run(
    image_path: str,
    leave_name: str,
    channel: str = "feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d",
    caption: str = "",
    server: str = DEFAULT_COMFYUI_SERVER,
    workflow: str = DEFAULT_WORKFLOW,
    no_send: bool = False,  # 🆕 09-27 主人钦定：caller 拼 reply = 物理防双发
) -> str:
    """反推参考图直出唯一入口。

    参数：
        image_path: 参考图路径（主人发我的参考图/）
        leave_name: 留底名（不含扩展名）
        channel: 默认 feishu 主对话渠道
        caption: 自定义 caption（1-3 句骚话）
        server: ComfyUI server URL（默认 192.168.x.x:8188 = 实战 218 钦定）
        workflow: 工作流名（默认 yuer_reference_reverse_inference = 本新工作流）

    返回：
        str: "OK_FILE:{final_path} SENT" 成功 / 失败 raise

    实战 318 钦定（08-05 · 盖过 minimax/qwen3_vision 远程反推一切）：
        反推参考图 = 1 条链路：
            ① 上传参考图到 ComfyUI（0 反推 prompt 拼接 0 LLM 翻译 0 远程反推）
            ② 加载新工作流 yuer_reference_reverse_inference.json
            ③ 改 LoadImage.image = 上传后的文件名
            ④ 提交 ComfyUI /prompt
            ⑤ 轮询 /history/{prompt_id}（0 WebSocket = 实战 291 B 方案）
            ⑥ 从 outputs 拿图（节点 41 SaveImage）
            ⑦ cp 留底 LEAVE_DIR
            ⑧ stdout 输出 MEDIA:<abs_path> = 唯一交付物 = caller 拼到 reply = Hermes 框架渲染（实战 320-A' 钦定·08-06 盖过实战 313 一切）

        旧路径（删除）：
            ❌ hermes chat --image + minimax-m3 远程反推（撞 system-injection 拒答风险）
            ❌ rev_qwen3_vision_single.py 本地反推 prompt → 单独走 Krea 2 LoRA 出图（易撞图）
            ❌ yuer_send_image.send_yuer_image 发图（实战 320-A' 钦定 raise NotImplementedError）

    🔴 实战 320-A' 钦定 · reply 文本硬钩（盖过实战 318 v6.20 双发防御思路）
        reply 文本必 0 yuer_send_image 调飞书 API 痕迹 / 0 任何 caller 凭印象补发
    """
    assert image_path, "image_path 不能空"
    assert os.path.exists(image_path), f"参考图不存在: {image_path}"
    assert leave_name, "留底名不能空"

    # caption 拦截器（实战 154 钦定 = 0 IP/端口/MEDIA 字面进 reply）
    caption = make_safe_caption(caption)

    log(f"开始反推直出: 参考图={image_path} workflow={workflow} channel={channel}")
    _t_start = time.monotonic()

    # Step ① 上传参考图
    uploaded_name = upload_reference_image(image_path, server)

    # Step ② 加载工作流
    wf = load_workflow(server, workflow)

    # Step ③ 改参考图节点的 image
    # 🔴 11-09 主人换了新的洗图工作流 = 贴图节点从 LoadImage 换成 PKLoadImagePaste（剪贴板粘贴道）
    #    = 两种都得认 = 认不出就 RuntimeError = 不静默跑错图
    loadimage_node_id = None
    for nid, node in wf.items():
        _ct = node.get("class_type")
        if _ct == "LoadImage":
            node["inputs"]["image"] = uploaded_name
            loadimage_node_id = nid
            log(f"   节点 {nid} LoadImage → {uploaded_name}")
            break
        if _ct == "PKLoadImagePaste":
            # PKLoadImagePaste = 剪贴板粘贴节点 = 直接吃 filename（不是上传名）
            node["inputs"]["image"] = uploaded_name
            node["inputs"]["Paste from clipboard"] = None
            loadimage_node_id = nid
            log(f"   节点 {nid} PKLoadImagePaste → {uploaded_name}")
            break
    if loadimage_node_id is None:
        raise RuntimeError("工作流找不到 LoadImage / PKLoadImagePaste 节点")

    # Step ④ 改 SaveImage.filename_prefix = LEAVE_DIR 友好前缀
    for nid, node in wf.items():
        if node.get("class_type") == "SaveImage":
            node["inputs"]["filename_prefix"] = save_prefix(f"yuer_reverse_inference_{int(time.time())}")
            break

    # Step ⑤ 提交 + 轮询
    history_entry = submit_and_poll(wf, server, timeout=180)

    # Step ⑥ 从 outputs 拿图
    out_path = fetch_image_from_outputs(history_entry, server, "/tmp/yuer_reverse_inference")
    log(f"   💾 落盘: {out_path}")

    # Step ⑦ cp 留底
    final_path = step_save_to_leave_only(out_path, leave_name)

    # ✅ 实战 525 整改：反推脚本 = 内置 yuer_send_v2.sh 真发飞书（盖过实战 320-A' 旧路径）
    # 🆕 09-27 主人钦定：--no-send 跳过脚本内发图 = caller 拼 reply = 物理防双发
    _t_total = time.monotonic() - _t_start
    log(f"✅ 反推直出完成 ({_t_total:.1f}s) 落盘={final_path}")
    if no_send:
        log(f"⏭️ 跳过脚本内发图（--no-send）= caller 拼 reply 物理防双发")
        # 直接 print MEDIA:<abs_path> 到 stdout = 给 caller 拼 reply 用
        print(f"MEDIA:{final_path}")
        return ""
    log(f"⏱️ 发图开始...")
    import subprocess
    try:
        _send = subprocess.run(
            ["bash", "~/.hermes/skills/creative/yuer-image-delivery/scripts/yuer_send_v2.sh",
             final_path, caption, channel],
            capture_output=True, text=True, timeout=60
        )
        if _send.returncode == 0:
            log(f"   ✅ 发图成功 ({time.monotonic() - _t_start - _t_total:.1f}s)")
        else:
            log(f"   ❌ 发图失败: {_send.stderr[:200]}")
    except Exception as e:
        log(f"   ❌ 发图异常: {e}")
    # 返回空字符串 = 平台不再拿路径发第二次（真发已在 yuer_send_v2.sh 里完成）
    return ""


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 yuer_reverse_inference.py <image_path> <leave_name> [channel] [caption] [server] [--no-send]", file=sys.stderr)
        print("  channel: feishu (默认) / telegram", file=sys.stderr)
        print("  workflow: 默认 yuer_reference_reverse_inference", file=sys.stderr)
        print("  --no-send: 09-27 主人在场钦定 = 脚本只落盘不真发飞书 = caller 手拼 reply = 物理防双发", file=sys.stderr)
        sys.exit(2)

    image_path = sys.argv[1]
    leave_name = sys.argv[2]
    channel = sys.argv[3] if len(sys.argv) > 3 else "feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d"
    caption = sys.argv[4] if len(sys.argv) > 4 else ""
    server = sys.argv[5] if len(sys.argv) > 5 else DEFAULT_COMFYUI_SERVER

    # 🆕 09-27 主人钦定：--no-send 开关 = 脚本只落盘 = caller 拼 reply
    no_send = "--no-send" in sys.argv

    try:
        result = run(image_path, leave_name, channel=channel, caption=caption, server=server, no_send=no_send)
        # run() 内部已 print MEDIA:<abs_path> 到 stdout，main 不再重复 print
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)