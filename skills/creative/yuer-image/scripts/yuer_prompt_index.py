#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""yuer_prompt_index.py · 自出 prompt 池 → 结构化索引（11-01 主人钦定「梳理资源，能更好使用和积累」）

🔴 问题 = 自出池 1842 条全是**无结构裸文本**（一坨英文 prompt，段间只有逗号没有句号）
          = 检索只能撞词 = 我自己半年多的产出 = 等于躺在垃圾场
🔴 参考库（1313 条）已经是九段结构 = Scene/Camera/Pose/Wardrobe/Lighting/Mood/Shell/Hook
🔴 正解 = 把自出池也解析成**同样维度** → 两条腿接上 → 检索有维度可过滤。

**🔴 解析方法 = 锚点序列定位，0 正则猜语义**
我自己的 prompt 是 builder 固定结构写出来的，段落顺序恒定：
  [主体+发型][场景] . [机位段] [身材锚] Wearing [服装] [动作] [光线] [道具] [表情] [观看关系] , 9:16
锚点：
  A. "The camera is"      → 机位段起
  B. "a tall slender build" → 身材锚起（我自己的身材锚首句恒定）
  C. "Wearing "          → 服装段起
  D. "the light" / "the single source of light" / "daylight" → 光线段起
  E. "her eyes" / "her mouth" / "her chin" → 表情段起
  F. "the photographer" / "this recording" / "the photograph was taken" / "this is what" → 观看关系起
  G. ", 9:16 vertical composition" → 尾参

**索引存哪** = `/path/to/media/.prompt_index.json`（跟图同目录 = 不散落）

用法:
    /usr/bin/python3 scripts/yuer_prompt_index.py --build       # 全量重建
    /usr/bin/python3 scripts/yuer_prompt_index.py --build --limit 200
    /usr/bin/python3 scripts/yuer_prompt_index.py --stats       # 维度分布
    /usr/bin/python3 scripts/yuer_prompt_index.py --check       # 增量补新文件
    /usr/bin/python3 scripts/yuer_prompt_index.py --show <idx>  # 看一条解析结果
"""
import datetime
import glob
import json
import os
import re
import sys

SECRET = "/path/to/media"
INDEX = os.path.join(SECRET, ".prompt_index.json")
OWN_GLOBS = [os.path.join(SECRET, "*.prompt.txt"), os.path.join(SECRET, "*.prompt.md")]

BODY_START = "a tall slender build"
COSTUME_START = "Wearing "
LIGHT_MARKERS = ["the single source of light", "the light comes from", "the light is",
                 "the light ", "daylight", "the ceiling light"]
EXPR_MARKERS = ["her eyes ", "her mouth ", "her chin ", "her lips "]
VIEWER_MARKERS = ["the photographer", "this recording", "the photograph was taken",
                   "the shop clerk", "this is what", "her friend", "her fellow disciple"]
TAIL = ", 9:16 vertical composition"

# 维度标签（检索按维度过滤用）
DIM_KEYS = {
    "cam": ["at her own eye level", "from a great height", "almost on the floor",
            "ceiling mounted camera", "from below", "high above her", "below her",
            "looking up at her", "looking steeply down"],
    "framing": ["ultra wide", "wide full shot", "full body shot", "tight portrait",
                "macro", "medium shot", "waist up", "full body", "from her chest up"],
    "lens": ["14mm", "28mm", "35mm", "50mm", "85mm", "100mm", "120mm", "24mm"],
    "light": ["sun", "daylight", "lamp", "neon", "bulb", "screen", "fire", "candle",
              "floodlight", "street light", "moonlight", "window"],
    "viewer": ["the photographer", "this recording", "the photograph was taken",
               "a stranger", "nobody", "asked her to hold still", "this is what",
               "her friend", "her colleague"],
    "aware": ["unaware", "no idea", "completely unaware", "turned away from the lens",
              "not on the camera", "has no idea"],
}


def _norm(text):
    return " ".join(text.split())


def _first(text, markers, start=0):
    """返回 markers 中最靠前的命中位置，未命中返回 -1。"""
    best = -1
    bm = None
    for m in markers:
        i = text.find(m, start)
        if i >= 0 and (best < 0 or i < best):
            best = i
            bm = m
    return best, bm



# ══════════════════════════════════════════════════════════════════
# 格式 B（历史批 v30-v116 等）= 另一种固定结构
#   [风格+机身+焦段], [主体+发型], [场景], [景别+距离+机位高度+背景],
#   [身材锚], [服装], [动作], [表情], [光线/最亮处], [道具], [尾参]
# ══════════════════════════════════════════════════════════════════
B_LIGHT = ["the single brightest thing", "the light ", "the only light", "light from",
           "the key light", "daylight", "the sun"]
B_EXPR = ["her eyes ", "her gaze ", "her expression", "her mouth ", "her lips ",
          "her eyelids", "her jaw "]
B_VIEWER = ["the photographer", "this recording", "the photograph was taken",
            "this is what", "her friend", "a stranger", "nobody"]


def _parse_b(t):
    """返回 dict 或 None。"""
    ci = t.find(", a 20 years old")
    if ci < 0:
        return None
    head = t[:ci].strip(" .")
    rest = t[ci + 1:]
    bi = rest.find(BODY_START)
    if bi < 0:
        return None
    mid = rest[:bi].strip(" ,.")
    body = rest[bi:]
    # 🔴 格式 B 的服装锚是小写 "wearing "（格式 A 是大写 "Wearing "）
    wl = body.find("wearing ")
    wu = body.find("Wearing ")
    cands = [(i, k) for i, k in ((wl, "wearing "), (wu, "Wearing ")) if i >= 0]
    if not cands:
        return None
    wi, wk = min(cands)
    body_seg = body[:wi].strip(" ,.")
    tail_txt = body[wi + len(wk):]

    # 主体/发型/场景：mid = "A <风格> ... , a 20 years old ... with <hair>, with a side part, <scene>, <framing>, <distance/height>, <background>"
    m = re.search(r"^(A .*? young Asian woman with .*?), (.*)$", mid, re.S)
    if m:
        subject = m.group(1).strip()
        scene = m.group(2).strip()
    else:
        # rest 从 ", a 20 years old" 之后开始 → mid 开头就是主体
        m2 = re.search(r"^(a 20 years old .*?with .*?), (.*)$", mid, re.S)
        if not m2:
            return None
        subject = m2.group(1).strip()
        scene = m2.group(2).strip()

    li, lm = _first(tail_txt, B_LIGHT)
    ei, em = _first(tail_txt, B_EXPR)
    vi, vm = _first(tail_txt, B_VIEWER)
    if li < 0:
        return None
    costume = tail_txt[:li].strip(" ,.")
    if ei >= 0 and (vi < 0 or ei < vi):
        expr = tail_txt[ei:vi] if vi >= 0 else tail_txt[ei:]
    else:
        expr = ""
    viewer = tail_txt[vi:] if vi >= 0 else ""
    tail = ""
    ti = viewer.rfind(", 9:16")
    if ti >= 0:
        tail = viewer[ti + 2:]
        viewer = viewer[:ti]
    sp = tail_txt.find(". ", li)
    light_end = sp + 1 if sp > 0 else len(tail_txt)
    light = tail_txt[li:light_end].strip(" ,.")
    prop_start = light_end
    prop_end = ei if (ei >= 0 and (vi < 0 or ei < vi)) else (vi if vi >= 0 else len(tail_txt))
    props = tail_txt[prop_start:prop_end].strip(" ,.")
    return {
        "subject": subject, "scene": scene, "camera": head,
        "body": body_seg, "costume": costume, "action": props,
        "light": light, "expr": expr.strip(" ,."), "viewer": viewer.strip(" ,."),
        "tail": tail,
    }


def parse(path):
    try:
        txt = open(path, encoding="utf-8", errors="ignore").read()
    except Exception:
        return None
    if len(txt) < 200:
        return None
    base = os.path.basename(path)

    # 🔴 格式 C = .prompt.md（markdown 元数据头 + 代码块散文）= 半结构化
    if path.endswith(".md") or txt.lstrip().startswith("**") or "```" in txt[:400]:
        rc = _parse_c(txt, path, base)
        if rc:
            return rc

    t = _norm(txt)

    # 🔴 格式 D = 相机参数开头 + 散段落（2026-10-27 那批）
    if BODY_START not in t and "a 20 years old young Asian woman" in t:
        rd = _parse_d(txt, path, base)
        if rd:
            return rd

    # 机位段起（格式 A）；格式 A 不命中则走格式 B
    ci = t.find("The camera is")
    if ci < 0:
        nb = _parse_b(t)
        if not nb:
            # 格式 D 再试
            rd = _parse_d(txt, path, base)
            if rd:
                return rd
            # 兜底格式 E = 0 丢数据
            return _parse_e(txt, path, base)
        return _finish(nb, t, path, base)
    # 🔴 格式 B 的特征 = ", a 20 years old" 出现在 "The camera is" 之前
    ti_a = t.find(", a 20 years old")
    if ti_a >= 0 and ti_a < ci:
        nb = _parse_b(t)
        if nb:
            return _finish(nb, t, path, base)
    # 场景 = 主体头 与 机位段 之间
    head = t[:ci].rstrip(" .")
    # 场景描述 = head 里最后一个 ", " 之后到句号前（场景句以 . 结尾）
    scene = ""
    subj = head
    m = re.search(r"^(A photograph shot .*? young Asian woman with .*?), (.*?)\.?$", head, re.S)
    if m:
        subj = m.group(1)
        scene = m.group(2).strip()

    # 身材锚起
    bi = t.find(BODY_START, ci)
    if bi < 0:
        # 格式 A 找不到身材锚 → 回退格式 B / D / E
        nb = _parse_b(t)
        if nb:
            return _finish(nb, t, path, base)
        rd = _parse_d(txt, path, base)
        if rd:
            return rd
        return _parse_e(txt, path, base)
    camera = t[ci:bi].strip(" .")

    # 服装段起
    wi = t.find(COSTUME_START, bi)
    if wi < 0:
        return None
    body = t[bi:wi].strip(" .")

    rest = t[wi + len(COSTUME_START):]

    # 🔴 所有锚点位置统一在 rest 坐标系里算（0 混用坐标系 = 位置全错）
    li, lm = _first(rest, LIGHT_MARKERS)
    ei, em = _first(rest, EXPR_MARKERS)
    vi, vm = _first(rest, VIEWER_MARKERS)
    if li < 0 or (ei < 0 and vi < 0):
        return None
    costume = rest[:li].strip(" ,.")

    # 表情起点 = 表情锚 与 观看锚 中靠前者；观看段永远在最后
    if ei >= 0 and (vi < 0 or ei < vi):
        expr = rest[ei:vi] if vi >= 0 else rest[ei:]
    else:
        expr = ""
    viewer = rest[vi:] if vi >= 0 else ""

    tail = ""
    ti = viewer.rfind(TAIL)
    if ti >= 0:
        tail = viewer[ti + 2:]
        viewer = viewer[:ti]

    # 光线句 = rest[li] 到下一个句号
    sp = rest.find(". ", li)
    light_end = sp + 1 if sp > 0 else len(rest)
    light = rest[li:light_end].strip(" ,.")
    # 道具 = 光线句之后 到 表情/观看起点之前
    prop_start = light_end
    prop_end = ei if (ei >= 0 and (vi < 0 or ei < vi)) else (vi if vi >= 0 else len(rest))
    props = rest[prop_start:prop_end].strip(" ,.")
    # 动作 = 服装段之前其实在 costume 描述里；这里把 props 前半当"动作+道具"
    action = props

    viewer = viewer.strip(" ,.")

    # 尾参剥离
    full_viewer = viewer
    viewer = viewer.strip(" ,.")

    low = t.lower()
    tags = []
    for dim, keys in DIM_KEYS.items():
        for k in keys:
            if k in low:
                tags.append("%s:%s" % (dim, k.replace(" ", "_")))
    nb = {
        "subject": subj.strip(), "scene": scene, "camera": camera,
        "body": body, "costume": costume, "action": props, "light": light,
        "expr": expr.strip(" ,."), "viewer": viewer, "tail": tail,
    }
    return _finish(nb, t, path, base, tags)




# ══════════════════════════════════════════════════════════════════
# 格式 C（.prompt.md 带元数据头 + ``` 代码块正文）= 自由散文式
#   🔴 切不动段落 → **半结构化** = 抽关键词标签 + 全文保留
#   🔴 原则 = 能切就切，切不了就抽标签 = 0 为了整齐丢数据
# ══════════════════════════════════════════════════════════════════
MD_RE = re.compile(r"```(?:[a-z]*)?\n(.*?)```", re.S)
MD_META_RE = re.compile(r"^\*\*[^*]+\*\*:\s*(.*)$", re.M)
# 散文里常见的维度信号词（抽标签用）
LOOSE_KEYS = {
    "cam": ["low angle", "high angle", "eye level", "from behind", "over the shoulder",
            "looking up", "looking down", "dutch angle", "close up", "full body",
            "medium shot", "wide shot", "overhead", "from below", "from above"],
    "lens": ["24mm", "28mm", "35mm", "50mm", "85mm", "105mm", "135mm", "200mm", "f/1.2", "f/1.4", "f/2.8"],
    "light": ["window light", "golden hour", "neon", "candlelight", "flashlight",
              "backlit", "rim light", "softbox", "streetlight", "moonlight", "firelight"],
    "viewer": ["the photographer", "the viewer", "the camera", "candid", "spy", "hidden",
               "captured", "taken by", "self-portrait", "selfie"],
    "aware": ["unaware", "unnoticed", "no idea", "oblivious", "absent-minded", "caught off guard"],
    "expose": ["midriff", "lower back", "waistline", "thigh", "cleavage", "backless",
               "off the shoulder", "riding up", "sheer", "translucent"],
}


def _strip_md(txt):
    """剥 markdown 头 + 取 ``` 代码块正文（没有代码块就用全文）。"""
    t = txt
    m = MD_RE.search(t)
    if m:
        return m.group(1).strip()
    # 无代码块：去掉 **key**: value 头部行
    lines = [ln for ln in t.splitlines() if not MD_META_RE.match(ln.strip())]
    body = "\n".join(lines).strip()
    return body if len(body) > 150 else t.strip()


def _parse_c(txt, path, base):
    body = _strip_md(txt)
    if len(body) < 120:
        return None
    low = body.lower()
    tags = []
    for dim, keys in DIM_KEYS.items():
        for k in keys:
            if k in low:
                tags.append("%s:%s" % (dim, k.replace(" ", "_")))
    for dim, keys in LOOSE_KEYS.items():
        for k in keys:
            if k in low:
                tags.append("%s:%s" % (dim, k.replace(" ", "_")))
    # 主题标签：命中九维主题池里任一主题名
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import design_dimensions as dd
        for name, items in dd.THEMES.items():
            for it in items:
                if it and it.lower() in low:
                    tags.append("theme:%s" % it)
    except Exception:
        pass
    meta = MD_META_RE.findall(txt)
    return {
        "path": path,
        "file": base,
        "date": base[:10] if base[:4].isdigit() else "",
        "batch": (re.search(r"_(v\d+|b\d+)_", base).group(1)
                  if re.search(r"_(v\d+|b\d+)_", base) else ""),
        "n": {
            "subject": "", "scene": body[:300], "camera": "", "body": "",
            "costume": "", "action": "", "light": "", "expr": "", "viewer": "",
            "tail": "",
        },
        "meta": meta,
        "tags": sorted(set(tags)),
        "verified": _verified(path),
        "text": " ".join(body.split()),
    }



# ══════════════════════════════════════════════════════════════════
# 格式 D（相机参数开头 + 自由散段落）= 2026-10-27 前后那批
#   例： "A candid low-angle street photograph taken on a Fujifilm X-T5 with a 50mm f/1.4 lens,
#        the camera placed below ..., a 20 years old young Asian woman with ..., wearing ..."
#   🔴 段落边界不固定 → 半结构化：抽 tag + 保留全文 + 抽"场景句/服装句"两个高频维度
# ══════════════════════════════════════════════════════════════════
D_HEAD_RE = re.compile(
    r"^(A [^,]{5,160}?)(,\s*(?:the camera|camera)[^,]{0,120},?)?"
    r"\s*(a 20 years old young Asian woman.*)$", re.S)


def _parse_d(txt, path, base):
    t = _norm(txt)
    if len(t) < 200:
        return None
    low = t.lower()
    tags = []
    for dim, keys in DIM_KEYS.items():
        for k in keys:
            if k in low:
                tags.append("%s:%s" % (dim, k.replace(" ", "_")))
    for dim, keys in LOOSE_KEYS.items():
        for k in keys:
            if k in low:
                tags.append("%s:%s" % (dim, k.replace(" ", "_")))
    m = re.search(r"a 20 years old young Asian woman with (.*?), (?:with a side part,)?(.*)$", t, re.S)
    if not m:
        return None
    hair = m.group(1).strip()
    rest = m.group(2).strip()
    # 场景 = 从 rest 开头到第一个 "wearing"/"she wears"/"dressed in" 之前
    mw = re.search(r"(wearing |she wears |dressed in |clad in )", rest, re.I)
    if mw:
        scene = rest[:mw.start()].strip(" ,.")
        costume = rest[mw.start():]
    else:
        scene = rest[:260].strip(" ,.")
        costume = ""
    # 相机段 = 开头到主体句之前
    camera = t[:t.find("a 20 years old young Asian woman")].strip(" ,.")
    return {
        "path": path,
        "file": base,
        "date": base[:10] if base[:4].isdigit() else "",
        "batch": (re.search(r"_(v\d+|b\d+)_", base).group(1)
                  if re.search(r"_(v\d+|b\d+)_", base) else ""),
        "n": {
            "subject": hair, "scene": scene, "camera": camera, "body": "",
            "costume": costume[:600], "action": "", "light": "", "expr": "",
            "viewer": "", "tail": "",
        },
        "tags": sorted(set(tags)),
        "verified": _verified(path),
        "text": t,
    }



# ══════════════════════════════════════════════════════════════════
# 格式 E（兜底）= 任何文本都入索引 + 抽 tag + 全文
#   🔴 原则 = **0 丢数据** = 切不动就半结构化 = 一条都不扔
#   （含测试文件 / 其他模型试稿 / 非语儿角色的稿 = 也要能被检索到）
# ══════════════════════════════════════════════════════════════════
def _theme_tags(low):
    """🔴 D1 主题标签 = 命中九维主题池里的题材名（中文）+ 英文信号词（THEME_EN）
    = 主题池是中文、我的 prompt 是英文 = 0 英文别名就永远匹配不上。"""
    out = []
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import design_dimensions as dd
        for name, items in dd.THEMES.items():
            for it in items:
                if it and it.lower() in low:
                    out.append("theme:%s" % it)
        en = getattr(dd, "THEME_EN", {})
        for cat, keys in en.items():
            for k in keys:
                if k.lower() in low:
                    out.append("theme:%s" % cat)
                    break
    except Exception:
        pass
    return out


def _verified(path):
    """🔴 verified = 这条 prompt 真出过图（.sent 守卫在）= 检索时优先选验证过的。"""
    try:
        stem = path[:-len(".prompt.txt")] if path.endswith(".prompt.txt") else path[:-len(".prompt.md")]
        for cand in (stem + ".sent", stem + ".png.sent"):
            if os.path.exists(cand):
                return True
        # 落盘图名带时间戳：同名前缀的 .png.sent
        d = os.path.dirname(path)
        base = os.path.basename(path).split(".prompt.")[0]
        for f in os.listdir(d):
            if f.startswith("yuer_") and f.endswith(".png.sent") and base in f:
                return True
    except Exception:
        pass
    return False


def _parse_e(txt, path, base):
    t = _norm(txt)
    if len(t) < 40:
        return None
    low = t.lower()
    tags = []
    for dim, keys in DIM_KEYS.items():
        for k in keys:
            if k in low:
                tags.append("%s:%s" % (dim, k.replace(" ", "_")))
    for dim, keys in LOOSE_KEYS.items():
        for k in keys:
            if k in low:
                tags.append("%s:%s" % (dim, k.replace(" ", "_")))
    tags += _theme_tags(low)
    return {
        "path": path,
        "file": base,
        "date": base[:10] if base[:4].isdigit() else "",
        "batch": (re.search(r"_(v\d+|b\d+)_", base).group(1)
                  if re.search(r"_(v\d+|b\d+)_", base) else ""),
        "n": {k: "" for k in ("subject", "scene", "camera", "body", "costume",
                              "action", "light", "expr", "viewer", "tail")},
        "tags": sorted(set(tags)),
        "text": t,
    }


def _finish(nb, t, path, base, tags=None):
    if tags is None:
        low = t.lower()
        tags = []
        for dim, keys in DIM_KEYS.items():
            for k in keys:
                if k in low:
                    tags.append("%s:%s" % (dim, k.replace(" ", "_")))
    m = re.search(r"_(v\d+|b\d+)_", base)
    tags = list(tags) + _theme_tags(t.lower())
    return {
        "path": path,
        "file": base,
        "date": base[:10],
        "batch": m.group(1) if m else "",
        "n": nb,
        "tags": sorted(set(tags)),
        "verified": _verified(path),
        "text": t,
    }


def build(limit=None):
    files = []
    for g in OWN_GLOBS:
        files += glob.glob(g)
    files = sorted(set(files))
    if limit:
        files = files[-limit:]
    out = []
    for f in files:
        r = parse(f)
        if r:
            out.append(r)
    data = {
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_files": len(files),
        "parsed": len(out),
        "entries": out,
    }
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("索引已写 %s" % INDEX)
    print("文件 %d / 解析成功 %d / 失败 %d" % (len(files), len(out), len(files) - len(out)))
    return data


def load():
    if not os.path.exists(INDEX):
        return None
    return json.load(open(INDEX, encoding="utf-8"))


def stats():
    d = load()
    if not d:
        print("索引不存在，先跑 --build")
        return
    print("索引生成于 %s" % d["generated"])
    print("文件 %d / 解析 %d" % (d["total_files"], d["parsed"]))
    from collections import Counter
    c = Counter()
    for e in d["entries"]:
        for t in e["tags"]:
            c[t] += 1
    print("\n=== 维度标签分布 ===")
    for k, v in c.most_common(40):
        print("  %-48s %d" % (k, v))
    print("\n=== 批次分布(近 12) ===")
    cb = Counter(e["batch"] for e in d["entries"] if e["batch"])
    print("  " + "  ".join("%s:%d" % (k, v) for k, v in cb.most_common(12)))
    print("\n=== 段落非空率 ===")
    for k in ("scene", "camera", "costume", "light", "expr", "viewer"):
        n = sum(1 for e in d["entries"] if e["n"].get(k))
        print("  %-10s %d/%d" % (k, n, len(d["entries"])))


def show(i):
    d = load()
    e = d["entries"][int(i)]
    print("FILE:", e["file"])
    for k, v in e["n"].items():
        print("  %-9s %s" % (k, v[:160]))
    print("  tags:", " ".join(e["tags"]))


def check():
    d = load()
    known = {e["path"] for e in d["entries"]} if d else set()
    files = []
    for g in OWN_GLOBS:
        files += glob.glob(g)
    files = sorted(set(files))
    new = [f for f in files if f not in known]
    print("总 %d / 已知 %d / 新增 %d" % (len(files), len(known), len(new)))
    if not new:
        return
    add = [r for r in (parse(f) for f in new) if r]
    if not d:
        d = {"generated": "", "total_files": len(files), "parsed": 0, "entries": []}
    d["entries"] += add
    d["total_files"] = len(files)
    d["parsed"] = len(d["entries"])
    d["generated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print("新增入库 %d 条 → 总 %d 条" % (len(add), len(d["entries"])))


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--build" in a:
        lim = int(a[a.index("--limit") + 1]) if "--limit" in a else None
        build(lim)
    elif "--stats" in a:
        stats()
    elif "--show" in a:
        show(a[a.index("--show") + 1])
    elif "--check" in a:
        check()
    else:
        print(__doc__)
