#!/usr/bin/env python3
"""
dump_lora_config.py · 语儿当前出图工作流配置速查脚本（实战 359 钦定 · 08-12 · 灵魂级）

唯一职责：主人问「用的哪几个 LoRA / 现在配置是什么 / X 强度多少」时 =
- 第一动作 = 跑这个脚本 = 拿真凭实据
- 0 凭印象编答案（实战 359 反模式硬表）
- 输出 LoRA 槽位 + 强度 + sampler 参数 + system_prompt 字符数 = 一目了然

调用姿势（实战 332 + 实战 359 钦定）：
    /usr/bin/python3 ~/.hermes/skills/creative/yuer-image/scripts/dump_lora_config.py

输出：纯文本表格（master / registered 双目录自动选最大文件 = 防失同步）
"""
import json
import os
import sys
from pathlib import Path

# 双目录定位（实战 351 钦定主目录 vs 注册目录双备份）
MASTER_PATH = "/path/to/workflows/yuer_prompt moody fast.json"
REGISTERED_PATH = "~/.local/lib/python3.11/site-packages/comfyui/assets/workflows/yuer_moody_fast.json"


def pick_workflow_path() -> str:
    """实战 351 + 实战 359 钦定：双目录自动选最大文件 = 防主目录 vs 注册目录失同步。"""
    candidates = []
    for label, p in [("master", MASTER_PATH), ("registered", REGISTERED_PATH)]:
        if os.path.exists(p):
            size = os.path.getsize(p)
            candidates.append((label, p, size))

    if not candidates:
        print("❌ 双目录都找不到工作流文件 = 检查路径")
        sys.exit(1)

    # 选 size 最大的（防失同步时拿到旧版本）
    candidates.sort(key=lambda x: x[2], reverse=True)
    label, p, size = candidates[0]
    return p


def dump_lora_config():
    wf_path = pick_workflow_path()
    print(f"=== 当前出图工作流配置 · 实战 359 钦定版 ===")
    print(f"工作流文件: {wf_path}")
    print(f"文件大小: {os.path.getsize(wf_path)} bytes")
    print()

    with open(wf_path) as f:
        wf = json.load(f)

    # 找 Power Lora Loader 节点（实战 359 实测节点 822）
    lora_node = None
    for nid, node in wf.items():
        if "Power Lora Loader" in node.get("class_type", ""):
            lora_node = (nid, node)
            break

    if not lora_node:
        print("❌ 工作流里找不到 Power Lora Loader 节点")
        sys.exit(1)

    nid, node = lora_node
    inputs = node.get("inputs", {})
    print(f"Power Lora Loader 节点 = {nid}")
    print(f"节点 title = {node.get('_meta', {}).get('title', 'N/A')}")
    print()

    # 遍历 lora_1 / lora_2 / lora_3 ... 槽位
    lora_slots = []
    for k in sorted(inputs.keys()):
        if k.startswith("lora_") and isinstance(inputs[k], dict):
            lora_data = inputs[k]
            name = lora_data.get("lora", "N/A")
            strength = lora_data.get("strength", 0)
            on = lora_data.get("on", True)
            status = "ON" if on else "OFF"
            lora_slots.append((k, name, strength, status))

    if not lora_slots:
        print("❌ 工作流里没有 LoRA 槽位")
        sys.exit(1)

    print("LoRA 槽位（按 lora_N 顺序）：")
    for slot, name, strength, status in lora_slots:
        # 名字补齐字段宽度让输出对齐
        print(f"  {slot} = {name:<60} 强度 {strength:.2f}  [{status}]")

    print()

    # 找 KSampler 节点（节点 830）拿 sampler / steps / cfg
    sampler_info = None
    for nid, node in wf.items():
        ct = node.get("class_type", "")
        if "KSampler" in ct or "Sampler" in ct:
            inputs = node.get("inputs", {})
            sampler_info = {
                "node": nid,
                "sampler_name": inputs.get("sampler_name", "N/A"),
                "steps": inputs.get("steps", "N/A"),
                "cfg": inputs.get("cfg", "N/A"),
            }
            break

    if sampler_info:
        print("采样参数（KSampler 节点 {}）：".format(sampler_info["node"]))
        print(f"  sampler = {sampler_info['sampler_name']}")
        print(f"  steps   = {sampler_info['steps']}")
        print(f"  cfg     = {sampler_info['cfg']}")
        print()

    # 找 system_prompt 节点（节点 861）拿字符数
    sp_info = None
    for nid, node in wf.items():
        ct = node.get("class_type", "")
        title = node.get("_meta", {}).get("title", "")
        if ct == "get_string" or "system_prompt" in title:
            inputs = node.get("inputs", {})
            sp_str = inputs.get("input_string", "")
            if isinstance(sp_str, str) and len(sp_str) > 100:
                sp_info = {
                    "node": nid,
                    "title": title,
                    "chars": len(sp_str),
                }
                break

    if sp_info:
        print(f"system_prompt 节点 {sp_info['node']} ({sp_info['title']}):")
        print(f"  字符数 = {sp_info['chars']}")
        if sp_info["chars"] >= 2700:
            print(f"  版本 = 实战 351 灵魂注入版 (1179 → 2787 字符)")
        elif sp_info["chars"] >= 2200:
            print(f"  版本 = 实战 321 v2 增量版 (1718 → 2286 字符)")
        else:
            print(f"  版本 = 精简版 / 旧版（实战 341 撞车高风险）")

    print()
    print("=" * 60)
    print("调用姿势：/usr/bin/python3 ~/.hermes/skills/creative/yuer-image/scripts/dump_lora_config.py")


if __name__ == "__main__":
    dump_lora_config()