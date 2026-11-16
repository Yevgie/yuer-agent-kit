#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prompt_asset_search.py · 开源素材库统一检索（姿势 / 发型 / 成套服装）

用法:
    # 列所有子库
    /usr/bin/python3 prompt_asset_search.py --libs

    # 姿势（中文名 / 分类 / 关键词）
    /usr/bin/python3 prompt_asset_search.py pose 跪立 --limit 5
    /usr/bin/python3 prompt_asset_search.py pose --cats

    # 发型（按发长 / 分区 / 名称查）
    /usr/bin/python3 prompt_asset_search.py hair 长发 --limit 8
    /usr/bin/python3 prompt_asset_search.py hair --cats

    # 服装（写实成套 / 二次元成套）
    /usr/bin/python3 prompt_asset_search.py costume 泳装 --limit 5
    /usr/bin/python3 prompt_asset_search.py costume --cats
    /usr/bin/python3 prompt_asset_search.py costume-anime 水手服 --limit 5

    # 输出可直接进 prompt 的英文关键词行（默认行为）
    /usr/bin/python3 prompt_asset_search.py costume 性感 --prompt

    # 要路径（拿去当参考图）
    /usr/bin/python3 prompt_asset_search.py hair 长发 --paths --limit 3

🔴 这三个库都是「成套现成的」= 服装条目自带上装+下装+鞋+配件，
  发型条目自带发型名 + 分区 + 发长，姿势条目自带骨架名 + 分类 + 机位。
  **直接抄库里的英文关键词进 prompt = 0 自己凭空编。**

坑:
    · 姿势库 pose-zh.json 全中文键；portrait-zh.json 键 = 分区/发长/发型名称/标题；
      costume-zh.json 键 = 分类/服装名称/标签/关键词；costume-anime-zh.json 键 =
      一级分类/分类/服装名称/日文名称/标签/关键词。**四套键名各不一样。**
    · 服装库的「关键词」是英文逗号串（可直接进 prompt）；中文「服装名称」是给人看的。
      姿势库没有英文关键词字段 → 姿势要自己翻成英文动作短语（库里只给中文骨架）。
    · 库根目录写死 GAL_ROOT，可用环境变量 POSE_GALLERY_ROOT 覆盖。
"""
import json
import os
import sys

GAL_ROOT = os.environ.get(
    "POSE_GALLERY_ROOT", "/path/to/data/pose_gallery/ai-pose-gallery-zh"
)
DATA = os.path.join(GAL_ROOT, "data")

LIBS = {
    "pose": ("pose-zh.json", "姿势", "姿势名称"),
    "hair": ("portrait-zh.json", "发型", "发型名称"),
    "costume": ("costume-zh.json", "服装", "服装名称"),
    "costume-anime": ("costume-anime-zh.json", "二次元服装", "服装名称"),
}


def load(fn):
    p = os.path.join(DATA, fn)
    if not os.path.exists(p):
        raise SystemExit(f"找不到 {p} = 库没装好")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def hay_of(lib, r):
    """把一条记录的所有可搜字段拼成一段文本。"""
    if lib == "pose":
        keys = ("姿势名称", "分类", "体系", "角度", "检索")
    elif lib == "hair":
        keys = ("发型名称", "标题", "发长", "分区", "检索")
    elif lib == "costume":
        keys = ("服装名称", "分类", "关键词", "检索")
    else:
        keys = ("服装名称", "日文名称", "分类", "一级分类", "关键词", "检索")
    return " ".join(str(r.get(k, "")) for k in keys)


# 🔴 发型库的真坑 = 「长发尾」里也含「长发」= 子串匹配会命中几百条短发
#    → 发长是**独立字段**，查发长必须按字段精确匹配，不能靠标题子串。
HAIR_LENGTHS = ("短发", "中发", "中长发", "长发")


def match(lib, r, words):
    if lib == "hair":
        for w in words:
            if w in HAIR_LENGTHS:
                if r.get("发长") != w:
                    return False
            elif w not in hay_of(lib, r):
                return False
        return True
    return all(w in hay_of(lib, r) for w in words)


def dedupe_key(lib, r):
    """同一个「名称」只出一次（同名的多张图当成一条列出）。"""
    if lib == "pose":
        return (r.get("姿势名称"), r.get("姿势编号"))
    if lib == "hair":
        return (r.get("发型名称"), r.get("发长"), r.get("分区"))
    return (r.get("id"), LIBS[lib][2])


def cat_field(lib):
    return "分类" if lib in ("pose", "costume", "costume-anime") else "发长"


def name_field(lib):
    return LIBS[lib][2]


def en_line(lib, r):
    """给可直接进 prompt 的英文串。"""
    if lib == "costume":
        return r.get("关键词", "")
    if lib == "costume-anime":
        return r.get("关键词", "")
    if lib == "hair":
        # portrait 库没有英文关键词 = 只能给中文名 + 发长，英文自己翻
        return f"{r.get('发型名称','')}（{r.get('发长','')}）"
    # pose = 库只给中文骨架，英文动作短语自己翻
    return f"{r.get('姿势名称','')}（{r.get('分类','')}/{r.get('角度','')}）"


def show(lib, r, want_paths, want_prompt):
    nid = r.get("id", "")
    nm = r.get(name_field(lib), "")
    line = f"{nid}\t{nm}"
    extra = ""
    if lib == "pose":
        extra = f"[{r.get('体系','')} / {r.get('分类','')} / {r.get('角度','')}]"
    elif lib == "hair":
        extra = f"[{r.get('分区','')} / {r.get('发长','')}]"
        if r.get("热门"):
            extra += " ★热门"
    elif lib == "costume":
        extra = f"[{r.get('分类','')}]"
    else:
        extra = f"[{r.get('一级分类','')} / {r.get('分类','')}]"
    line += "\t" + extra
    if want_prompt:
        line += f"\n  PROMPT: {en_line(lib, r)}"
    if want_paths:
        for k in ("原图", "预览图", "缩略图", "full", "thumb"):
            if r.get(k) and not str(r[k]).startswith("http"):
                line += f"\n  {k} {os.path.join(GAL_ROOT, r[k])}"
            elif r.get(k):
                line += f"\n  {k} {r[k]}"
    print(line)


def main():
    argv = sys.argv[1:]
    if not argv or "--libs" in argv:
        for k, (fn, label, _) in LIBS.items():
            p = os.path.join(DATA, fn)
            n = len(load(fn)) if os.path.exists(p) else "未安装"
            print(f"{k}\t{label}\t{fn}\t{n}")
        return

    lib = argv[0]
    if lib not in LIBS:
        print(f"未知子库 {lib} = 可用：" + " / ".join(LIBS))
        return
    argv = argv[1:]

    if "--cats" in argv:
        rows = load(LIBS[lib][0])
        f = cat_field(lib)
        counts = {}
        for r in rows:
            counts[r.get(f)] = counts.get(r.get(f), 0) + 1
        for k, v in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"{k}\t{v}")
        return

    want_paths = "--paths" in argv
    want_prompt = "--prompt" in argv
    limit = 8
    if "--limit" in argv:
        i = argv.index("--limit")
        limit = int(argv[i + 1])
    words = [a for a in argv if not a.startswith("--") and a != str(limit)]
    words = [w for w in words if w]

    rows = load(LIBS[lib][0])
    if words:
        rows = [r for r in rows if match(lib, r, words)]
    if not rows:
        print("0 命中 = 换个词 / 用 --cats 看真实分类名")
        return

    shown = set()
    printed = 0
    for r in rows:
        key = dedupe_key(lib, r)
        if key in shown:
            continue
        shown.add(key)
        printed += 1
        if printed > limit:
            break
        show(lib, r, want_paths, want_prompt)
    print(f"--- 命中 {len(rows)} 条（显示 {printed} 条，限 {limit}）")


if __name__ == "__main__":
    main()
