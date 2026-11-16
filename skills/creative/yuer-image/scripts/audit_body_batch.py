#!/usr/bin/env python3
"""跨批次身材体检 = 回答「你写宽了 / 你没锁肩胯」的横向事实。

为什么需要它：
    check_body_anchors.py 是单稿体检（主人报某一张粗壮时用）。
    主人质疑的其实是「我一贯的写法」= 只看最新一张 = 猜 = 改单张稿 = 下一张照旧。
    本脚本扫落盘目录最近 N 张 .prompt.txt，横向统计三样：
      ① 每个部位名词跨批次的词频分布（谁在叠写 = 写法习惯问题）
      ② 锚组缺件分布（哪一项我老漏 = 锚组 / 写法问题）
      ③ 宽肩 / 宽胯 / 粗壮词命中（写宽了 vs 没锁 = 两种完全不同的修法）

用法：
    python3 audit_body_batch.py --dir /path/to/media --n 20
    python3 audit_body_batch.py --dir <目录> --n 20 --json

退出码：0 = 干净；1 = 有叠写 / 缺锚 / 宽壮词命中（报告里逐条列了）。
注意：只读，不改任何文件。
"""

import argparse
import json
import os
import re
import sys

# 部位词表 + 锚组 = 真值 = references/铁律/02-身材特征档.md §5（0 第二份口径）
PART_WORDS = [
    "her waist", "her bust", "her hips", "her chest", "her thigh", "her knee",
    "her leg", "her feet", "her breast", "her hip", "her arm", "her shoulder",
    "her back", "her belly", "her buttocks", "her face", "her eyes", "her hair",
    "her hand", "her neck", "her stomach",
]

SCALE_ANCHORS = [
    ("社区词", r"hourglass|slim yet voluptuous"),
    ("腿比躯干长", r"legs are longer than her torso"),
    ("围度数字", r"92-60-92|60-92-92|92cm|60cm|\b92 cm\b|\b60 cm\b"),
    ("腰臀胸句", r"waist is very slim|waist very slim"),
    ("宽胯", r"hips are wide|hips wide|wide hips|hips flaring out|peach shaped bottom|peach-like swell"),
    ("大胸紧翘", r"breasts are large|breasts large|sit high and firm|sitting high and firm"),
]

# 宽 / 壮类词 = 「写宽了」的证据；跟「没锁」是两回事
WIDE_RES = [
    (r"broad shoulder|wide shoulder|strong shoulder|square shoulder|muscular shoulder", "宽肩词"),
    (r"hips are wide|wide hips|hips wide", "宽胯词"),
    (r"\bheavy\s+(breasts?|ass|thighs?|hips?|body|build)\b|bubble butt|huge ass|thick thighs?|wasp waist", "粗壮禁词"),
]

# 肩锚 = 只锁「窄肩线」的词；泛写 her shoulder 不算锚（那只是部位名）
SHOULDER_ANCHOR_RE = re.compile(
    r"(shoulders?\s+(are\s+)?(narrow|slim|sloping|delicate|soft|slender))"
    r"|((narrow|slim|sloping|delicate|soft|slender)\s+shoulders?)", re.I)
NEG_RE = re.compile(r"\b(no|not|without|never|avoid|lacking)\b", re.I)
NEG_EXEMPT_RE = re.compile(r"no\s+pubic\s+hair\s+at\s+all", re.I)
HEAD_RATIO_RE = re.compile(r"ten head-lengths|ten head lengths|10 head-lengths", re.I)


def audit_one(text):
    low = text.lower()
    part_counts = {w: low.count(w) for w in PART_WORDS}
    dup = {w: n for w, n in part_counts.items() if n > 1}
    missing = [name for name, pat in SCALE_ANCHORS if not re.search(pat, low, re.I)]
    wide = [label for rx, label in WIDE_RES if re.search(rx, low, re.I)]
    stripped = NEG_EXEMPT_RE.sub("", text)
    neg = sorted({m.group(0).lower() for m in NEG_RE.finditer(stripped)})
    return {
        "chars": len(text),
        "dup": dup,
        "missing": missing,
        "wide": wide,
        "neg": neg,
        "head_ratio": bool(HEAD_RATIO_RE.search(text)),
        "shoulder_anchor": bool(SHOULDER_ANCHOR_RE.search(text)),
        "hip_width": bool(re.search(r"hips are wide|wide hips|hips wide", low, re.I)),
    }


def list_prompts(d, n):
    if not os.path.isdir(d):
        return []
    files = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".prompt.txt")]
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="/path/to/media")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    files = list_prompts(args.dir, args.n)
    if not files:
        print(f"目录里没有 .prompt.txt：{args.dir}")
        return 0

    rows = []
    for p in files:
        try:
            text = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        r = audit_one(text)
        r["file"] = os.path.basename(p)
        rows.append(r)

    agg = {
        "files": len(rows),
        "dup_files": sum(1 for r in rows if r["dup"]),
        "missing_files": sum(1 for r in rows if r["missing"]),
        "wide_files": sum(1 for r in rows if r["wide"]),
        "shoulder_anchor_files": sum(1 for r in rows if r["shoulder_anchor"]),
        "hip_width_files": sum(1 for r in rows if r["hip_width"]),
        "part_files": {},
        "missing_by_anchor": {},
    }
    for w in PART_WORDS:
        hit = sum(1 for r in rows if w in r["dup"])
        if hit:
            agg["part_files"][w] = hit
    for r in rows:
        for name in r["missing"]:
            agg["missing_by_anchor"][name] = agg["missing_by_anchor"].get(name, 0) + 1

    if args.json:
        print(json.dumps({"agg": agg, "rows": rows}, ensure_ascii=False, indent=2))
        return 1 if (agg["dup_files"] or agg["missing_files"] or agg["wide_files"]) else 0

    print(f"=== 跨批次身材体检：{agg['files']} 张（{args.dir} 最近 {args.n} 张）===")
    print(f"  叠写命中的稿：{agg['dup_files']}/{agg['files']}"
          f" | 缺锚的稿：{agg['missing_files']}/{agg['files']}"
          f" | 宽壮词命中的稿：{agg['wide_files']}/{agg['files']}")
    print(f"  有窄肩锚的稿：{agg['shoulder_anchor_files']}/{agg['files']}"
          f" | 写了宽胯词的稿：{agg['hip_width_files']}/{agg['files']}")
    if agg["part_files"]:
        print("  叠写部位（出现份数）：" + "，".join(f"{w}×{n}" for w, n in
                                                   sorted(agg["part_files"].items(), key=lambda kv: -kv[1])))
    if agg["missing_by_anchor"]:
        print("  常缺锚（缺件次数）：" + "，".join(f"{k}×{v}" for k, v in
                                                  sorted(agg["missing_by_anchor"].items(), key=lambda kv: -kv[1])))
    print("  ── 逐张 ──")
    for r in rows:
        flags = []
        if r["dup"]:
            flags.append("叠写 " + "，".join(f"{w}×{n}" for w, n in r["dup"].items()))
        if r["missing"]:
            flags.append("缺 " + "，".join(r["missing"]))
        if r["wide"]:
            flags.append("宽壮 " + "，".join(r["wide"]))
        if r["neg"]:
            flags.append("负向 " + "，".join(r["neg"]))
        if r["head_ratio"]:
            flags.append("十头身比")
        if not r["shoulder_anchor"]:
            flags.append("无肩锚")
        print(f"  {r['file'][:52]:52} {r['chars']:5}c  " + ("；".join(flags) if flags else "OK"))
    return 1 if (agg["dup_files"] or agg["missing_files"] or agg["wide_files"]) else 0


if __name__ == "__main__":
    sys.exit(main())
