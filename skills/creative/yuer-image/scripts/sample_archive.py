#!/usr/bin/env python3
"""从语儿图库抽旧图给主人（随机 N 张 / 按时间 / 按关键词）。

用法：
    python3 sample_archive.py --n 5
    python3 sample_archive.py --n 5 --seed 20261019
    python3 sample_archive.py --n 3 --exclude 猫系 日常 yuer_ka
    python3 sample_archive.py --n 3 --since 2026-08-01 --before 2026-09-01
    python3 sample_archive.py --n 3 --match 泳池
    python3 sample_archive.py --count-only

输出：
    绝对路径一行一个（stdout）
    stderr 打印库内总数 + 本次抽样数

铁律：
  · 图库 = /path/to/media/ = 唯一真相源
  · 不解析命名规律 = 命名是历史混合的 = 抽签走文件名匹配
  · --exclude 传前缀 = 排除今天刚出的新系列
  · 不写库、不改名、不删任何文件（只读）
"""
import argparse
import os
import random
import re
import sys
from datetime import datetime

ARCHIVE = "/path/to/media"


def mtime_date(path: str) -> str:
    return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5, help="抽几张")
    ap.add_argument("--seed", type=int, default=None, help="随机种子（可复现）")
    ap.add_argument("--exclude", nargs="*", default=[], help="文件名要排除的前缀")
    ap.add_argument("--since", default=None, help="只抽该日期之后的（YYYY-MM-DD）")
    ap.add_argument("--before", default=None, help="只抽该日期之前的（YYYY-MM-DD）")
    ap.add_argument("--match", default=None, help="只抽文件名含该关键词的")
    ap.add_argument("--count-only", action="store_true", help="只打印总数，不抽")
    ap.add_argument("--archive", default=ARCHIVE, help="图库目录")
    args = ap.parse_args()

    if not os.path.isdir(args.archive):
        print(f"ERR: 图库不存在: {args.archive}", file=sys.stderr)
        return 2

    all_png = sorted(
        os.path.join(args.archive, f)
        for f in os.listdir(args.archive)
        if f.lower().endswith(".png")
    )
    # 主人发来的参考图不在语儿自己出的图库里 = 排除
    pool = [p for p in all_png if "主人发图" not in os.path.basename(p)]

    if args.exclude:
        pool = [
            p for p in pool
            if not any(os.path.basename(p).startswith(x) for x in args.exclude)
        ]
    if args.since:
        pool = [p for p in pool if mtime_date(p) >= args.since]
    if args.before:
        pool = [p for p in pool if mtime_date(p) < args.before]
    if args.match:
        pool = [p for p in pool if args.match in os.path.basename(p)]

    print(f"图库总数 {len(all_png)} 张 / 候选池 {len(pool)} 张", file=sys.stderr)
    if args.count_only:
        return 0
    if not pool:
        print("ERR: 候选池为空", file=sys.stderr)
        return 1

    rng = random.Random(args.seed)
    picked = rng.sample(pool, min(args.n, len(pool)))
    for p in picked:
        print(p)
    print(f"抽中 {len(picked)} 张", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
