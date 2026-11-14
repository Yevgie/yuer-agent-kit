#!/usr/bin/env python3
# prompt 错词自检脚本 - 调 comfyui 出图前必跑
# 用法: python3 prompt_blacklist_check.py /tmp/yuer_prompt.txt
import sys

BLACKLIST = [
    "tear mole",  # v5.19 tear 被误解为 tears 画泪痕
    "anime", "2D", "flat shading",  # 防 anime 化
    "low quality", "worst quality", "normal quality",  # v1.3 反向约束违规
    "no ", "not ", "without ",  # v1.3 绝不写禁词
]

SOUL_FACE_3 = [
    "signature small beauty mole under left eye",
    "cold elegant aura",
    "pale porcelain skin",
]

def check(prompt_path):
    with open(prompt_path) as f:
        p = f.read()

    errors = []

    # 灵魂脸 3 项
    for sf in SOUL_FACE_3:
        if sf not in p:
            errors.append(f"❌ 缺灵魂脸项: {sf}")

    # 错词
    for bad in BLACKLIST:
        if bad in p.lower():
            errors.append(f"❌ 含错词: {bad}")

    # trigger 词前置检查
    if not p.startswith("sugar_face_z"):
        errors.append("❌ trigger 词 sugar_face_z 必须放最前")

    if errors:
        print("\n".join(errors))
        return False
    else:
        print("✅ 自检通过")
        return True

if __name__ == "__main__":
    sys.exit(0 if check(sys.argv[1]) else 1)