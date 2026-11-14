#!/usr/bin/env python3
"""
yuer_doubao_pipeline.py — 端到端：豆包反推 → yuer_moody_fast 出图（实战 493k 主人钦定）
==============================================================================

**职责**：主人发参考图 + 可选 brief → 豆包 vision 反推 → yuer_moody_fast 出图。
**触发**：主人说"豆包反推出图 / 豆包反推 + 出图 / doubao 出图"。
**链路**：
  1. 读图片 → base64
  2. 调豆包 Doubao Seed 2.0 Lite vision API（输出 600-1000 字中文 Krea 2 提示词）
  3. 加载 yuer_moody_fast.json 工作流
  4. 改节点 627 CLIPTextEncode.text = 豆包反推 prompt
  5. 改节点 732 SaveImage.filename_prefix
  6. 提交到 ComfyUI → 轮询 → 落盘
  7. 下载到 /path/to/media/
  8. 返回 MEDIA: 路径
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
import base64
import argparse
import requests
from pathlib import Path

# 引入豆包反推脚本
sys.path.insert(0, "~/.hermes/skills/creative/yuer-image/scripts")
from yuer_doubao_reverse import reverse as doubao_reverse, REVERSE_SYSTEM_PROMPT, DOUBAO_MODEL  # noqa

# ============ ComfyUI 配置 ============
COMFYUI_URL = os.environ.get('YUER_COMFYUI_URL', 'http://192.168.x.x:8188')
# 🔴🔴🔴 11-10 21:42 主人钦定「日常你自己决定这两个流你用哪个」= 我定的 = 默认档切 MOSS
#    （反推后出图 = 走同一条日常流 = 免得反推出来是 Krea2 味、直出是 Moss 味）
WORKFLOW_PATH = os.environ.get(
    'YUER_FAST_WORKFLOW',
    '/path/to/workflows/yuer_moodyMoss_fast.json'
)
OUTPUT_DIR = os.environ.get(
    'YUER_OUTPUT_DIR',
    '/path/to/media/'
)
# 节点 ID 钦定（实战 493k）
CLIP_TEXT_NODE_ID = '627'  # yuer_moodyMoss_fast.json 的 CLIPTextEncode 节点（Krea2 也是 627 = 一致）
SAVE_IMAGE_NODE_ID = '732'  # SaveImage 节点


def load_workflow(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"🔴 工作流不存在: {path}")
    with open(path) as f:
        return json.load(f)


def submit_and_poll(wf: dict, url: str, timeout: int = 180) -> dict:
    """提交工作流到 ComfyUI + 轮询完成"""
    print(f"[pipeline] 提交工作流到 {url}...")
    resp = requests.post(f"{url}/prompt", json={"prompt": wf}, timeout=30)
    resp.raise_for_status()
    prompt_id = resp.json()["prompt_id"]
    print(f"[pipeline] prompt_id={prompt_id}")

    for i in range(timeout // 3):
        time.sleep(3)
        h = requests.get(f"{url}/history/{prompt_id}", timeout=10).json()
        if prompt_id in h and h[prompt_id].get("status", {}).get("completed", False):
            print(f"[pipeline] ✅ 完成 ({i*3}s)")
            return h[prompt_id]
    raise RuntimeError(f"⏰ 工作流超时（{timeout}s）")


def download_image(url: str, filename: str, subfolder: str, dest_path: str) -> int:
    """从 ComfyUI /view 下载图片到指定路径"""
    params = {"filename": filename, "subfolder": subfolder, "type": "output"}
    resp = requests.get(f"{url}/view", params=params, timeout=30)
    resp.raise_for_status()
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'wb') as f:
        f.write(resp.content)
    return os.path.getsize(dest_path)


def run(image_path: str, leave_name: str = None, brief: str = "", caption: str = "") -> dict:
    """
    端到端主入口。

    Args:
        image_path: 参考图绝对路径
        leave_name: 输出文件名（不含 .png 后缀），默认 yuer_doubao_pipeline_{时间戳}
        brief: 可选中文需求
        caption: 可选 caption

    Returns:
        {"prompt": "...", "image_path": "...", "size_bytes": N}
    """
    # ============ 步骤 1: 豆包反推 ============
    print(f"[pipeline] STEP 1: 豆包反推 {image_path}")
    prompt = doubao_reverse(image_path, brief=brief)
    print(f"[pipeline] ✅ 豆包反推完成: {len(prompt)} 字符")

    # ============ 步骤 2: 加载工作流 ============
    print(f"\n[pipeline] STEP 2: 加载工作流 {WORKFLOW_PATH}")
    wf = load_workflow(WORKFLOW_PATH)

    # 验证关键节点存在
    if CLIP_TEXT_NODE_ID not in wf:
        raise RuntimeError(f"🔴 节点 {CLIP_TEXT_NODE_ID} 不存在（CLIPTextEncode）")
    if wf[CLIP_TEXT_NODE_ID].get('class_type') != 'CLIPTextEncode':
        raise RuntimeError(f"🔴 节点 {CLIP_TEXT_NODE_ID} 不是 CLIPTextEncode")
    if SAVE_IMAGE_NODE_ID not in wf:
        raise RuntimeError(f"🔴 节点 {SAVE_IMAGE_NODE_ID} 不存在（SaveImage）")

    # ============ 步骤 3: 改节点 ============
    print(f"[pipeline] STEP 3: 改节点 {CLIP_TEXT_NODE_ID} CLIPTextEncode.text = 豆包反推 prompt")
    wf[CLIP_TEXT_NODE_ID]['inputs']['text'] = prompt

    # 改 SaveImage filename_prefix
    ts = int(time.time())
    leave_name = leave_name or f"yuer_doubao_pipeline_{ts}"
    filename_prefix = save_prefix(f"{leave_name}_{ts}")
    wf[SAVE_IMAGE_NODE_ID]['inputs']['filename_prefix'] = filename_prefix
    print(f"[pipeline] STEP 3: 改节点 {SAVE_IMAGE_NODE_ID} SaveImage.filename_prefix = {filename_prefix}")

    # ============ 步骤 4: 提交 + 轮询 ============
    print(f"\n[pipeline] STEP 4: 提交到 ComfyUI")
    result = submit_and_poll(wf, COMFYUI_URL, timeout=180)

    # ============ 步骤 5: 提取输出文件名 ============
    outputs = result.get('outputs', {})
    if SAVE_IMAGE_NODE_ID not in outputs or 'images' not in outputs[SAVE_IMAGE_NODE_ID]:
        raise RuntimeError(f"🔴 工作流输出无图片: {outputs}")

    img_info = outputs[SAVE_IMAGE_NODE_ID]['images'][0]
    src_filename = img_info['filename']
    subfolder = img_info.get('subfolder', 'image')

    # ============ 步骤 6: 下载到安语儿目录 ============
    dest_filename = f"{leave_name}.png"
    dest_path = os.path.join(OUTPUT_DIR, dest_filename)
    print(f"\n[pipeline] STEP 6: 下载图片到 {dest_path}")
    size = download_image(COMFYUI_URL, src_filename, subfolder, dest_path)
    print(f"[pipeline] ✅ 下载成功: {dest_path} ({size} bytes)")

    return {
        "prompt": prompt,
        "image_path": dest_path,
        "size_bytes": size,
        "media_path": f"MEDIA:{dest_path}",
    }


def main():
    parser = argparse.ArgumentParser(description='豆包反推 + yuer_moody_fast 出图端到端')
    parser.add_argument('image', help='参考图路径')
    parser.add_argument('--brief', default='', help='可选中文需求')
    parser.add_argument('--leave_name', default=None, help='输出文件名（不含 .png）')
    parser.add_argument('--caption', default='', help='caption')
    args = parser.parse_args()

    result = run(
        image_path=args.image,
        leave_name=args.leave_name,
        brief=args.brief,
        caption=args.caption,
    )
    print(f"\n===== 豆包反推 prompt =====")
    print(result['prompt'][:500])
    print(f"\n===== 输出图 =====")
    print(f"路径: {result['image_path']}")
    print(f"大小: {result['size_bytes']} bytes")
    print(f"MEDIA: {result['media_path']}")


if __name__ == '__main__':
    main()