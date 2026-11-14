#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pose_gallery_search.py · 姿势图库检索（ai-pose-gallery-zh）。

用法:
    # 列出体系 / 分类 / 角度（先摸清库长什么样）
    /usr/bin/python3 scripts/pose_gallery_search.py --systems
    /usr/bin/python3 scripts/pose_gallery_search.py --cats
    /usr/bin/python3 scripts/pose_gallery_search.py --angles

    # 按中文姿势名 / 关键词搜（可多个词 = 同时命中）
    /usr/bin/python3 scripts/pose_gallery_search.py 跪立 跪 --limit 8

    # 组合过滤：体系 + 分类 + 角度
    /usr/bin/python3 scripts/pose_gallery_search.py --system 全身单人・性感系 --cat 骑乘位 --angle 侧面

    # 出用法 B 需要的线稿路径（img = 原图 png，thumbs = 缩略图 jpg）
    /usr/bin/python3 scripts/pose_gallery_search.py 骑乘 --paths

    # 看库里有多少个「不同的姿势」（姿势名去重，不是姿势编号去重）
    /usr/bin/python3 scripts/pose_gallery_search.py --unique

坑:
    · 姿势编号 P001~P080 **不是** 每个姿势一个编号 = 同名姿势会被拆到不同编号
      （例：P001 与另一个编号共用「S形站姿・胯部侧顶」）→ 去重统计必须用「姿势名称」，
      用「姿势编号」去重会得到错的姿势数。
    · pose-zh.json 全中文键（id/体系/姿势编号/分类/姿势名称/角度/缩略图/原图/检索），
      天气/其他脚本里的英文键在这套 JSON 里不存在。
    · 库根目录写死在 GAL_ROOT，可用环境变量 POSE_GALLERY_ROOT 覆盖。
"""
import json
import os
import sys

GAL_ROOT = os.environ.get(
    "POSE_GALLERY_ROOT", "/vol2/1000/pose_gallery/ai-pose-gallery-zh"
)
ZH = os.path.join(GAL_ROOT, "data", "pose-zh.json")
EN = os.path.join(GAL_ROOT, "data", "pose.json")


def load():
    if not os.path.exists(ZH):
        raise SystemExit(f"找不到 {ZH} = 库没装好 = 先跑 scripts/download.py + verify.py")
    with open(ZH, encoding="utf-8") as f:
        return json.load(f)


def uniq_names(rows):
    return sorted({r.get("姿势名称", "") for r in rows if r.get("姿势名称")})


def main():
    argv = sys.argv[1:]
    data = load()

    if "--systems" in argv:
        seen = []
        for r in data:
            v = r.get("体系")
            if v not in seen:
                seen.append(v)
        for v in seen:
            n = sum(1 for r in data if r.get("体系") == v)
            print(f"{v}\t{n}")
        return
    if "--cats" in argv:
        counts = {}
        for r in data:
            counts[r.get("分类")] = counts.get(r.get("分类"), 0) + 1
        for k, v in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"{k}\t{v}")
        return
    if "--angles" in argv:
        counts = {}
        for r in data:
            counts[r.get("角度")] = counts.get(r.get("角度"), 0) + 1
        for k, v in counts.items():
            print(f"{k}\t{v}")
        return
    if "--unique" in argv:
        names = uniq_names(data)
        codes = sorted({r.get("姿势编号", "") for r in data})
        print(f"记录数\t{len(data)}")
        print(f"不同姿势名\t{len(names)}")
        print(f"姿势编号数\t{len(codes)}")
        print("去重键 = 姿势名称（编号有重名，0 用编号统计姿势数）")
        return

    words = [a for a in argv if not a.startswith("--")]
    system = cat = angle = None
    limit = 8
    want_paths = False
    want_en = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--system":
            i += 1
            system = argv[i]
        elif a == "--cat":
            i += 1
            cat = argv[i]
        elif a == "--angle":
            i += 1
            angle = argv[i]
        elif a == "--limit":
            i += 1
            limit = int(argv[i])
        elif a == "--paths":
            want_paths = True
        elif a == "--english":
            want_en = True
        i += 1

    rows = data
    if system:
        rows = [r for r in rows if r.get("体系") == system]
    if cat:
        rows = [r for r in rows if r.get("分类") == cat]
    if angle:
        rows = [r for r in rows if r.get("角度") == angle]
    if words:
        def hit(r):
            hay = " ".join(
                str(r.get(k, "")) for k in ("姿势名称", "分类", "体系", "角度", "检索")
            )
            return all(w in hay for w in words)
        rows = [r for r in rows if hit(r)]

    if not rows:
        print("0 命中 = 换个词 / 用 --cats 看分类名")
        return

    # 同一个姿势名只出一次（同名的多角度当成一条姿势列出）
    shown = set()
    printed = 0
    for r in rows:
        key = (r.get("姿势名称"), r.get("姿势编号"))
        if key in shown:
            continue
        shown.add(key)
        printed += 1
        if printed > limit:
            break
        line = f"{r.get('姿势编号')}\t{r.get('姿势名称')}\t[{r.get('体系')} / {r.get('分类')} / {r.get('角度')}]"
        if want_paths:
            line += f"\n  原图 {os.path.join(GAL_ROOT, r.get('原图', ''))}"
            line += f"\n  缩略 {os.path.join(GAL_ROOT, r.get('缩略图', ''))}"
        if want_en and os.path.exists(EN):
            line += f"\n  id {r.get('id')}"
        print(line)
    print(f"--- 命中 {len(rows)} 条（去重后显示 {min(printed, len(shown))} 条，限 {limit}）")


if __name__ == "__main__":
    main()
