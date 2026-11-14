#!/usr/bin/env python3
"""对照库牌成品提示词 = 量我自己写的 prompt 缺哪些维度。

用法：
  python3 measure_card_baseline.py                 # 只出库牌基线
  python3 measure_card_baseline.py p1.txt p2.txt    # 库牌基线 + 我的这批

为什么需要它：
  「我的提示词比不上抽卡」是主观判断，但差距落在可测的字段命中率上
  （景别词 / 道具清单 / 材质对比 / 氛围句 / 景深 / 质量词 / 首句是不是主体 / 句数 / 字符数）。
  写完一批先跑这个 = 知道这一批缺哪几维 = 补那几维 = 不用整篇重写。
"""
import os
import re
import statistics as st
import sys

# 🔴 11-09 22:20 提示词池 = 一行一条完整英文提示词
LIB = "~/.hermes/skills/creative/yuer-image/references/提示词库-nsfw.txt"

FIELDS = {
    "景别词": r"\b(close-up|closeup|medium shot|full-length|full length|waist-up|half-body|bust shot|wide shot)\b",
    "道具清单": r"\b(gloves?|stockings?|heels?|boots?|sneakers?|hat|beret|headband|earrings?|necklace|choker|bracelet|nail polish|lipstick)\b",
    "材质对比": r"\b(matte|glossy|satin|sheer|velvet|silk|leather|lace|contrasting|contrast with)\b",
    "氛围句": r"\b(mood|overall (look|feeling|ambiance)|atmosphere|color grading|colour grading|tone of)\b",
    "景深": r"\b(bokeh|depth of field|shallow focus|blurred background)\b",
    "质量词": r"\b(8K|4K|ultra-HD|ultra HD|hyper-realistic|photorealistic|cinematic photography)\b",
    "光位": r"\b(backlit|rim light|side light|key light|window light|golden hour|overhead light)\b",
    "表情物理化": r"\b(eyelid|lids|lips?|chin|jaw)\b",
    "私处锚": r"\b(innie|labia|pubic|pussy)\b",
}


def load_lib():
    """🔴 11-09 22:20 新池 = 一行一条 `N|<整段英文提示词>`"""
    if not os.path.exists(LIB):
        sys.exit(f"找不到库牌文件：{LIB}")
    text = open(LIB, encoding="utf-8").read()
    out = []
    for ln in text.split("\n"):
        m = re.match(r"^(\d+)\|(.+)$", ln.strip())
        if m and m.group(2).strip():
            out.append(m.group(2).strip())
    return out


def stats(prompts, label):
    if not prompts:
        print(f"{label}: 0 条")
        return None
    lens = [len(p) for p in prompts]
    sents = [len([s for s in re.split(r"[.!?]", p) if s.strip()]) for p in prompts]
    print(f"\n=== {label}（{len(prompts)} 条）===")
    print(f"字符数 中位 {st.median(lens):.0f} / 句数 中位 {st.median(sents):.0f}")
    for name, rx in FIELDS.items():
        hits = sum(1 for p in prompts if re.search(rx, p, re.I))
        per = sum(len(re.findall(rx, p, re.I)) for p in prompts) / len(prompts)
        print(f"{name:12s} 命中 {hits * 100 // len(prompts):3d}%   平均 {per:.2f} 处/条")
    first_is_subject = sum(
        1 for p in prompts if re.match(r"^\s*(a|an|the)\s+\w+[^.]*\b(woman|girl|young|lady)\b", p, re.I)
    )
    print(f"{'首句是主体':12s} 命中 {first_is_subject * 100 // len(prompts):3d}%")
    return {"lens": lens, "sents": sents}


def main():
    lib = load_lib()
    base = stats(lib, "库牌成品")
    mine = [open(p, encoding="utf-8").read().strip() for p in sys.argv[1:]]
    if mine:
        m = stats(mine, "我这批")
        if base and m:
            print("\n=== 差距（我 - 库牌，命中率百分点）===")
            for name in FIELDS:
                b = sum(1 for p in lib if re.search(FIELDS[name], p, re.I)) * 100 / len(lib)
                q = sum(1 for p in mine if re.search(FIELDS[name], p, re.I)) * 100 / len(mine)
                flag = "  ← 缺" if q < b - 5 else ""
                print(f"{name:12s} 库牌 {b:5.1f}%  我 {q:5.1f}%{flag}")


if __name__ == "__main__":
    main()
