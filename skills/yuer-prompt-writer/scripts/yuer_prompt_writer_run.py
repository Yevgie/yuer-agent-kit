#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yuer_prompt_writer_run.py
实战 494j 新建：yuer-prompt-writer 技能专属出图脚本

唯一职责：
- 接收语儿在脑子里写好的英文 prompt（直接调 yuer-prompt-writer 技能产出的）
- 直接遍历第一个 CLIPTextEncode 节点写入 text 字段
- 不依赖 yuer_run_one_brief.run() 的 brife 节点识别逻辑（那个要求 title=提示词英文/prompt/nid=9）
- 适配所有用 CLIPTextEncode 节点的工作流（yuer_moody_fast.json 等）

跟 yuer_run_one_brief.run() 的区别：
- yuer_run_one_brief.run() = 写中文 brief 调 LLM 节点 / 写完整 prompt 调无 LLM 节点（要求 title 匹配）
- 本脚本 = 只接收完整英文 prompt（不调 LLM）= 直接写入 = 0 title 限制
"""
import json
import os
import sys
import time
import requests
import random

# ComfyUI 服务端
COMFYUI_SERVER = 'http://192.168.x.x:8188'

# 工作流路径
WORKFLOW_FAST = '/path/to/workflows/yuer_moody_fast.json'

# 留底目录
LEAVE_DIR = '/path/to/media'


def write_prompt_to_workflow(workflow_path: str, prompt_text: str) -> dict:
    """直接遍历第一个 CLIPTextEncode 节点写入 text 字段（无 title 限制）"""
    with open(workflow_path, 'r', encoding='utf-8') as f:
        wf = json.load(f)

    prompt_set = False
    for nid, node in wf.items():
        if node.get('class_type') == 'CLIPTextEncode':
            if 'text' in node.get('inputs', {}):
                node['inputs']['text'] = prompt_text
                prompt_set = True
                print(f"[yuer_prompt_writer_run] ✅ 节点 {nid} CLIPTextEncode.text ← prompt 写入")
                break

    if not prompt_set:
        raise RuntimeError(f"工作流 {workflow_path} 找不到 CLIPTextEncode 节点")

    return wf


def save_prefix(name: str) -> str:
    """🔴 统一落盘路径（10-29 主人钦定）= Hermes/Yuer%year%-%month%-%day%/<唯一名>

    🔴 工作流节点里存的是主人原写法「Hermes/Yuer%date:yyyy-MM-dd%/」= GUI 入口由前端 JS 展开。
      但脚本走 API = 不经过前端 = %date:...% 原样送到后端会变字面量。
      → 脚本侧这里必须客户端算实际日期，落盘结果与 GUI 完全一致（都是 Hermes/Yuer2026-10-29/）。
    """
    import datetime
    return "Hermes/Yuer" + datetime.date.today().isoformat() + "_" + name


def set_save_image_prefix(wf: dict, leave_name: str) -> dict:
    """改 SaveImage.filename_prefix → 统一到 Hermes/Yuer<日期>/<名>"""
    for nid, node in wf.items():
        if node.get('class_type') == 'SaveImage':
            prefix = save_prefix(leave_name)
            node['inputs']['filename_prefix'] = prefix
            print(f"[yuer_prompt_writer_run] ✅ 节点 {nid} SaveImage.filename_prefix = {prefix}")
            return wf
    return wf


def submit_to_comfyui(wf: dict, timeout: int = 180) -> dict:
    """提交工作流到 ComfyUI"""
    payload = {"prompt": wf}
    resp = requests.post(f"{COMFYUI_SERVER}/prompt", json=payload, timeout=30)
    resp.raise_for_status()
    prompt_id = resp.json().get("prompt_id")
    print(f"[yuer_prompt_writer_run] 📝 提交成功 prompt_id={prompt_id}")

    # 轮询结果
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(3)
        try:
            hist_resp = requests.get(f"{COMFYUI_SERVER}/history/{prompt_id}", timeout=10)
            hist_data = hist_resp.json()
            if prompt_id in hist_data:
                status = hist_data[prompt_id].get("status", {})
                if status.get("completed", False):
                    elapsed = time.time() - start
                    print(f"[yuer_prompt_writer_run] ✅ 完成 ({elapsed:.1f}s)")
                    return hist_data[prompt_id]
        except Exception as e:
            print(f"[yuer_prompt_writer_run] ⚠️ 轮询出错: {e}")

    raise TimeoutError(f"ComfyUI 执行超时（{timeout}s）")


def download_image(history: dict, leave_name: str) -> str:
    """下载 ComfyUI 输出的图片到本地"""
    os.makedirs(LEAVE_DIR, exist_ok=True)

    images = history.get("outputs", {})
    for nid, output in images.items():
        if "images" in output:
            for img in output["images"]:
                filename = img["filename"]
                subfolder = img.get("subfolder", "")
                img_url = f"{COMFYUI_SERVER}/view?filename={filename}&subfolder={subfolder}"
                img_resp = requests.get(img_url, timeout=30)
                img_resp.raise_for_status()

                local_path = os.path.join(LEAVE_DIR, f"{leave_name}.png")
                with open(local_path, 'wb') as f:
                    f.write(img_resp.content)
                print(f"[yuer_prompt_writer_run] 💾 落盘: {local_path}")
                return local_path

    raise RuntimeError("ComfyUI history 中找不到图片输出")


def save_prompt_txt(prompt_text: str, leave_name: str) -> str:
    """保存 prompt 留底"""
    prompt_txt_path = os.path.join(LEAVE_DIR, f"{leave_name}.prompt.txt")
    with open(prompt_txt_path, 'w', encoding='utf-8') as f:
        f.write(prompt_text)
    print(f"[yuer_prompt_writer_run] 📄 prompt 留底: {prompt_txt_path}")
    return prompt_txt_path


def run(prompt_text: str, leave_name: str, workflow: str = 'yuer_moody_fast') -> str:
    """主入口函数

    Args:
        prompt_text: 语儿在脑子里写好的英文 prompt（500-650 词）
        leave_name: 文件名前缀
        workflow: 工作流名称（默认 yuer_moody_fast 无 LLM 直出版）

    Returns:
        落盘图片绝对路径
    """
    # 1. 写入 prompt 到工作流
    wf = write_prompt_to_workflow(WORKFLOW_FAST, prompt_text)
    wf = set_save_image_prefix(wf, leave_name)

    # 2. 提交 ComfyUI
    history = submit_to_comfyui(wf)

    # 3. 下载图片
    local_path = download_image(history, leave_name)

    # 4. 保存 prompt 留底
    save_prompt_txt(prompt_text, leave_name)

    return local_path


if __name__ == '__main__':
    # CLI 模式
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', required=True, help='英文 prompt')
    parser.add_argument('--leave_name', required=True, help='文件名前缀')
    args = parser.parse_args()
    result = run(args.prompt, args.leave_name)
    print(f"\n✅ 完成: {result}")
