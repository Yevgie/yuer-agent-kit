#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""costume_gallery_search.py · 服装图库检索（ai-costume-gallery / COSTUME-DB-01）。

同源作者的姊妹库：姿势库管「身体怎么摆」，服装库管「穿什么」。
1407 套，1366×2048 webp，幽灵人台（无头无手臂），浅冷灰纯背景，**纯服装无人物**。

用法:
    # 列分类
    /usr/bin/python3 scripts/costume_gallery_search.py --cats

    # 按关键词搜（多词 = 同时命中；中英都行，英文关键词库原生就是英文）
    /usr/bin/python3 scripts/costume_gallery_search.py lace white --limit 8
    /usr/bin/python3 scripts/costume_gallery_search.py 泳装 --limit 5

    # 组合过滤：分类 + 关键词
    /usr/bin/python3 scripts/costume_gallery_search.py --cat ランジェリー --kw stockings

    # 只出路径（出图链路要贴进 prompt 的服饰描述）
    /usr/bin/python3 scripts/costume_gallery_search.py --cat セクシー --paths

    # 随机抽一套（系列出图用）
    /usr/bin/python3 scripts/costume_gallery_search.py --random 5

坑:
    · 分类是**日文**原文：春/夏/秋/冬/ランジェリー/パーティ/水着/セクシー
    · 关键词是**英文**（原库就用英文），中文搜不到，只能搜英文单词
    · id 前缀 = 分类：SPR春 SUM夏 AUT秋 WIN冬 LNGランジェリー PTYパーティ SWM水着 SXYセクシー
    · 库根写死在 GAL_ROOT，可用环境变量 COSTUME_GALLERY_ROOT 覆盖
"""
import json
import os
import random
import sys

GAL_ROOT = os.environ.get(
    "COSTUME_GALLERY_ROOT", "/path/to/data/costume_gallery/ai-costume-gallery"
)
DB = os.path.join(GAL_ROOT, "data", "costume.json")

CAT_ZH = {
    "春": "春",
    "夏": "夏",
    "秋": "秋",
    "冬": "冬",
    "ランジェリー": "内衣/睡衣",
    "パーティ": "派对",
    "水着": "泳装",
    "セクシー": "性感",
}


def load():
    if not os.path.exists(DB):
        raise SystemExit(f"找不到 {DB} = 库没装好")
    with open(DB, encoding="utf-8") as f:
        return json.load(f)


def match(row, words):
    blob = (row.get("キーワード", "") + " " + row.get("カテゴリ", "")).lower()
    return all(w.lower() in blob for w in words)


def main():
    argv = sys.argv[1:]
    rows = load()

    if "--cats" in argv:
        counts = {}
        for r in rows:
            counts[r["カテゴリ"]] = counts.get(r["カテゴリ"], 0) + 1
        for c, n in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"{c} ({CAT_ZH.get(c, c)}) = {n}")
        return

    if "--random" in argv:
        n = 5
        if "--random" in argv:
            i = argv.index("--random")
            if i + 1 < len(argv) and argv[i + 1].isdigit():
                n = int(argv[i + 1])
        for r in random.sample(rows, min(n, len(rows))):
            print(f"{r['id']} | {r['カテゴリ']}({CAT_ZH.get(r['カテゴリ'], '')}) | {r['キーワード']}")
            print(f"    {os.path.join(GAL_ROOT, 'img', r['id'] + '.webp')}")
        return

    cat = None
    kw = []
    paths_only = False
    limit = 10
    words = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--cat" and i + 1 < len(argv):
            cat = argv[i + 1]
            i += 2
            continue
        if a == "--kw" and i + 1 < len(argv):
            kw.append(argv[i + 1])
            i += 2
            continue
        if a == "--paths":
            paths_only = True
            i += 1
            continue
        if a == "--limit" and i + 1 < len(argv):
            limit = int(argv[i + 1])
            i += 2
            continue
        words.append(a)
        i += 1

    words += kw
    sel = rows
    if cat:
        sel = [r for r in sel if r["カテゴリ"] == cat]
    if words:
        sel = [r for r in sel if match(r, words)]

    print(f"命中 {len(sel)} 条 / 库 {len(rows)} 条")
    for r in sel[:limit]:
        if paths_only:
            print(os.path.join(GAL_ROOT, "img", r["id"] + ".webp"))
        else:
            print(f"{r['id']} | {r['カテゴリ']}({CAT_ZH.get(r['カテゴリ'], '')}) | {r['キーワード']}")


if __name__ == "__main__":
    main()
