#!/usr/bin/env python3
"""🔴🔴🔴 中文描述一键出图（10-31 语儿·飞书直用入口）

🔴 **主人说**「红黑魔女风格的猫耳腋下少女，夜晚室内，跪姿」
🔴 **我跑一条命令就出图**

🔴 **三层拆解**
   ① 解构配方 = 解构原典 274 条标题匹配（作品级整套配方）
   ② 渡鸦细节 = 渡鸦 6470 条精确命中（权威 Danbooru tag）
   ③ 普通翻译 = tag_zh 125,426 键（剩余中文）

🔴 **自动选模型**
   - 中文描述含 2D/动漫/画风/插画 → anima
   - 含 写实/真实/照片/监控/偷拍 → moss
   - 含 网红/精修/ins → krea2
   - 默认 anima（法典资产都是 2D 语料）

🔴 **用法**
  python3 cn_gen.py "红黑魔女风格的猫耳腋下少女，夜晚室内，跪姿" --gen
  python3 cn_gen.py "猫耳 泳装 夜晚 室内" --model moss --seed 123 --gen
  python3 cn_gen.py "红发 猫耳 跪姿" --style film_painterly --gen
"""
import argparse
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SHOTS = "/path/to/media"
KA_RUN = os.path.join(HERE, "yuer_ka_fast.sh")

# 🔴 中文 → 模型
MODEL_HINTS = [
    ("moss", ["写实", "真实", "照片", "监控", "偷拍", "路人", "实拍", "日常", "自拍"]),
    ("krea2", ["网红", "精修", "ins风", "微博风", "美颜", "高清写真"]),
    ("anima", ["动漫", "2d", "插画", "画风", "二次元", "漫画", "赛璐璐", "厚涂"]),
]


def pick_model(desc, explicit=None):
    if explicit and explicit != "auto":
        return explicit
    low = (desc or "").lower()
    for m, kws in MODEL_HINTS:
        for k in kws:
            if k in low:
                return m
    return "anima"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("desc", help="中文描述")
    ap.add_argument("--model", default="auto", help="auto / anima / moss / krea2 / qwen")
    ap.add_argument("--style", help="画风层 ID，如 film_painterly")
    ap.add_argument("--head", help="固定开头，如 '1girl, solo'")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--out", help="落盘名（不含日期）")
    ap.add_argument("--gen", action="store_true", help="出图")
    ap.add_argument("--dump", action="store_true", help="只打印提示词")
    a = ap.parse_args()

    import cn_desc as CD
    prompt, d = CD.build(a.desc, style=a.style,
                         seed=a.seed if a.seed is not None else 7, head=a.head)

    print(f"🔴 配方: {(d['recipe'][:90] or '(无)')}")
    print(f"🔴 渡鸦: {d['raven']}")
    print(f"🔴 翻译: {d['plain']}")
    print(f"\n🔴 组装 [{len(prompt)} chars]")
    print(prompt)

    model = pick_model(a.desc, a.model)
    name = a.out or f"yuer_cn_{random.randint(1000, 9999)}"
    tmp = f"/tmp/anima_cli_{name}.txt"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"\n📝 提示词 → {tmp}")
    print(f"🎯 模型 = {model}  落盘名 = {name}")

    if a.dump:
        return
    if not a.gen:
        print("\n（加 --gen 出图）")
        return

    sent = os.path.join(SHOTS, f"{name}.sent")
    if os.path.exists(sent):
        os.remove(sent)
    cmd = ["bash", KA_RUN, tmp, name, "--model", model]
    if a.seed is not None:
        cmd += ["--seed", str(a.seed)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    out = r.stdout + r.stderr
    for line in out.splitlines():
        if any(k in line for k in ("落盘", "完成", "真发", "❌", "正向约束", "timing",
                                   "中文已翻译")):
            print("  " + line.strip())
    final = os.path.join(SHOTS, f"{name}.png")
    if os.path.exists(final):
        print(f"✅ 完成 = {final}")
    else:
        cand = sorted(x for x in os.listdir(SHOTS)
                      if x.startswith(name) and x.endswith(".png"))
        print(f"✅ 完成 = {os.path.join(SHOTS, cand[-1]) if cand else '未找到落盘'}")


if __name__ == "__main__":
    main()
