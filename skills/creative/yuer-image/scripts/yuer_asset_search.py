#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""yuer_asset_search.py · 语儿出图资产统一检索器（11-01 主人钦定）

> 主人原话：「还有我们积累的提示词库和之前的姿势/服装参考库，都是你的资源」

**🔴 问题 = 资源存在 ≠ 我用得上**（四个池子、四套 CLI、四种参数格式 = 每次都要现查用法 = 检索成本 > 收益）
**🔴 正解 = 一个入口同时查四个池子 = 一次调用拿到全部候选**

四个池子：
  1. 提示词资产池  = `yuer_prompt_search.py`（参考库 1313 + 自出 1785 = 3098 条成品提示词）
  2. 姿势库         = `pose_gallery_search.py`（1439 条 / 287 个不同姿势）
  3. 服装库         = `costume_gallery_search.py`（1407 套，日文分类 + 英文关键词）
  4. 九维维度库     = `design_dimensions.py`（771 条：主题/角色外观/场景/机位/景别/光源/服装/姿态/观看关系）

用法：
    # 全池统一搜（关键词命中哪个池就返回哪个池）
    /usr/bin/python3 scripts/yuer_asset_search.py "腰 胯 侧"

    # 指定池
    /usr/bin/python3 scripts/yuer_asset_search.py --pool pose "跪"
    /usr/bin/python3 scripts/yuer_asset_search.py --pool costume "lace white"
    /usr/bin/python3 scripts/yuer_asset_search.py --pool prompt "wet shirt"
    /usr/bin/python3 scripts/yuer_asset_search.py --pool dim "民國"

    # 各池的统计（体检）
    /usr/bin/python3 scripts/yuer_asset_search.py --stats

    # 姿势库出路径（当 Qwen 编辑道参考图用）
    /usr/bin/python3 scripts/yuer_asset_search.py --pool pose --paths "跪"

    # 服装库出路径
    /usr/bin/python3 scripts/yuer_asset_search.py --pool costume --paths "lace"

🔴 使用铁律（配合九维体系）：
  · 库 = **灵感来源和查缺工具** = 0 直接把字段抄进 prompt（抄了就变模具）
  · 命中之后 = **我自己判断能不能用 + 怎么改** = 0 命中即用
  · 姿势库/服装库给的是**身体怎么摆 / 穿什么** = 我要自己写成**带情境的句子**
  · 提示词资产池给的是**成品结构** = 我借它的**句法组织**，不抄它的**具体内容**
"""
import json
import os
import subprocess
import sys

YUER = "~/.hermes/skills/creative/yuer-image"
SCRIPTS = os.path.join(YUER, "scripts")
POSE_ROOT = os.environ.get("POSE_GALLERY_ROOT", "/vol2/1000/pose_gallery/ai-pose-gallery-zh")
COSTUME_ROOT = os.environ.get("COSTUME_GALLERY_ROOT", "/vol2/1000/costume_gallery/ai-costume-gallery")


def _run(script, args):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + args,
                       capture_output=True, text=True)
    return (p.stdout or "") + (p.stderr or "")


def search_prompt(q, top=6, dump=None):
    if dump:
        return _run("yuer_prompt_search.py", ["--dump", str(dump)])
    return _run("yuer_prompt_search.py", [q, "--top", str(top)])


def search_pose(q, limit=8, paths=False, system=None, cat=None, angle=None):
    # 底层库多词=AND → 中文姿势名常是"跪立・四肢着地"这种复合词 = 必须拆词逐个试
    words = [w for w in q.replace(",", " ").split() if w]
    if len(words) > 1:
        out = []
        for w in words:
            r = _run("pose_gallery_search.py", [w, "--limit", str(limit)])
            out.append("[%s]" % w)
            out.append(r.strip())
        return "\n".join(out)
    args = [q, "--limit", str(limit)]
    if paths:
        args.append("--paths")
    if system:
        args += ["--system", system]
    if cat:
        args += ["--cat", cat]
    if angle:
        args += ["--angle", angle]
    return _run("pose_gallery_search.py", args)


def search_costume(q, limit=8, paths=False, cat=None):
    # 底层库多词=AND → 拆词分别搜 = 命中面更宽
    words = [w for w in q.replace(",", " ").split() if w]
    if len(words) > 1:
        out = []
        for w in words:
            r = _run("costume_gallery_search.py", [w, "--limit", str(limit)])
            out.append("[%s]" % w)
            out.append(r.strip())
        return "\n".join(out)
    args = []
    if q:
        args.append(q)
    args += ["--limit", str(limit)]
    if paths:
        args.append("--paths")
    if cat:
        args += ["--cat", cat]
    return _run("costume_gallery_search.py", args)


def _dims(dd):
    """维度库各维：名字 -> 列表。dim 值可能是 dict 或 list，dict 再取子分类。"""
    out = []
    for name in ("THEMES", "SHELLS", "CAMERA_HEIGHTS", "FRAMINGS", "LIGHTS",
                 "COSTUME_CATEGORIES", "POSES"):
        v = getattr(dd, name, None)
        if isinstance(v, dict):
            for sub, items in v.items():
                if isinstance(items, list):
                    out.append(("%s/%s" % (name, sub), items))
        elif isinstance(v, list):
            out.append((name, v))
    for name in ("SPACE_QUALITY", "VIEWERS"):
        v = getattr(dd, name, None)
        if isinstance(v, list):
            out.append((name, v))
    return out


def search_dim(q, top=8):
    try:
        sys.path.insert(0, SCRIPTS)
        import design_dimensions as dd
    except Exception as e:
        return "维度库载入失败: %s" % e
    words = [w.lower() for w in q.replace(",", " ").split() if w] or [q.lower()]
    out = []
    for dim, items in _dims(dd):
        for it in items:
            if isinstance(it, dict):
                s = " ".join(str(v) for v in it.values())
            elif isinstance(it, (list, tuple)):
                s = " ".join(str(v) for v in it)
            else:
                s = str(it)
            sl = s.lower()
            # 任一关键词命中即列出（多词=OR，主题词常常不同字面）
            if any(w in sl for w in words):
                out.append("[%s] %s" % (dim, s))
    return "\n".join(out[:top * 3]) if out else "维度库无命中"



def search_index(q, top=8, tags=None, dim=None, batch=None):
    """🔴 结构化索引检索 = 按维度过滤 + 关键词加权。

    这是"自出池"真正可用的入口：
      --tag cam:worm_eye   按维度标签过滤
      --dim cam            只看某维度
      --batch v130         按批次
    """
    import json as _json
    idx = os.path.join("/path/to/media", ".prompt_index.json")
    if not os.path.exists(idx):
        return "索引不存在，先跑 yuer_prompt_index.py --build"
    data = _json.load(open(idx, encoding="utf-8"))
    ents = data["entries"]
    words = [w.lower() for w in q.replace(",", " ").split() if w]
    if dim:
        ents = [e for e in ents if any(t.startswith(dim + ":") for t in e["tags"])]
    if tags:
        for tg in tags:
            ents = [e for e in ents if tg in e["tags"]]
    if batch:
        ents = [e for e in ents if e.get("batch") == batch]
    scored = []
    for e in ents:
        hay = e["text"].lower()
        score = sum(hay.count(w) for w in words)
        # 维度标签命中加权
        score += sum(3 for w in words if any(w in t for t in e["tags"]))
        # 🔴 verified 加权 = 这条真出过图 = 比没验证过的稿更可信
        if e.get("verified"):
            score += 5
        if score > 0:
            scored.append((score, e))
    scored.sort(key=lambda x: -x[0])
    out = []
    for s, e in scored[:top]:
        out.append("• [%s] %s  (score=%d%s)" % (e["batch"] or "-", e["file"], s,
                                              " ✓已出图" if e.get("verified") else ""))
        out.append("  cam: %s" % e["n"].get("camera", "")[:110])
        out.append("  scene: %s" % e["n"].get("scene", "")[:110])
        out.append("  costume: %s" % e["n"].get("costume", "")[:110])
        out.append("  tags: %s" % " ".join(e["tags"][:8]))
        out.append("  path: %s" % e["path"])
    return "\n".join(out) if out else "索引无命中（%d 条已扫）" % len(ents)


def stats():
    print("=== 提示词资产池 ===")
    print(_run("yuer_prompt_search.py", ["--stats"]).strip())
    print("\n=== 姿势库 ===")
    zp = os.path.join(POSE_ROOT, "data", "pose-zh.json")
    if os.path.exists(zp):
        d = json.load(open(zp, encoding="utf-8"))
        names = {r.get("姿势名称", "") for r in d if r.get("姿势名称")}
        print("姿势条目 %d / 不同姿势名 %d" % (len(d), len(names)))
    else:
        print("未安装")
    print("\n=== 服装库 ===")
    cd_ = os.path.join(COSTUME_ROOT, "data", "costume.json")
    if os.path.exists(cd_):
        d = json.load(open(cd_, encoding="utf-8"))
        print("服装 %d 套" % len(d))
    else:
        print("未安装")
    print("\n=== 九维维度库 ===")
    sys.path.insert(0, SCRIPTS)
    import design_dimensions as dd
    tot = 0
    for dim, items in _dims(dd):
        print("  %-28s %d" % (dim, len(items)))
        tot += len(items)
    print("  合计 %d" % tot)


def main():
    argv = sys.argv[1:]
    pool = "all"
    if "--pool" in argv:
        i = argv.index("--pool")
        pool = argv[i + 1]
        del argv[i:i + 2]
    paths = "--paths" in argv
    if paths:
        argv.remove("--paths")
    if "--stats" in argv:
        stats()
        return
    q = " ".join([a for a in argv if not a.startswith("--")])
    top = 8
    if "--top" in argv:
        i = argv.index("--top")
        top = int(argv[i + 1])
        del argv[i:i + 2]

    tags = None
    if "--tag" in argv:
        i = argv.index("--tag")
        tags = [x for x in argv[i + 1].split(",") if x]
        del argv[i:i + 2]
    dim = None
    if "--dim" in argv:
        i = argv.index("--dim")
        dim = argv[i + 1]
        del argv[i:i + 2]
    batch = None
    if "--batch" in argv:
        i = argv.index("--batch")
        batch = argv[i + 1]
        del argv[i:i + 2]
    if pool in ("all", "prompt"):
        print("── 提示词资产池（结构化索引）──")
        print(search_index(q, top, tags, dim, batch).strip())
        print("\n── 提示词资产池（关键词原文命中）──")
        print(search_prompt(q, top).strip())
    if pool in ("all", "pose"):
        print("\n── 姿势库 ──")
        print(search_pose(q, top, paths).strip())
    if pool in ("all", "costume"):
        print("\n── 服装库 ──")
        print(search_costume(q, top, paths).strip())
    if pool in ("all", "dim"):
        print("\n── 九维维度库 ──")
        print(search_dim(q, top).strip())


if __name__ == "__main__":
    main()
