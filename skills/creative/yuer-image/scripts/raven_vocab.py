#!/usr/bin/env python3
"""渡鸦构图鉴 → Anima 词库模块（10-31 语儿）

🔴 来源 = /path/to/nai_codex/raven_composition.json（6633 条）
🔴 每条 = Danbooru tag + 中文说明 + 例图 + 分类路径

🔴 核心用法：
  ① 按语义组抽词 = 表达/姿势/视角/光影/眼色/场景…
  ② 自动生成互斥组 = 同组内大部分 tag 互斥（表情只能一个、姿势只能一个）
  ③ 中文反查 = 「腋下」→ armpits

用法：
  from raven_vocab import pick, mutex_for, zh_to_tag, vocab
  pick("expression", n=3)                  # 抽 3 个表情 tag
  mutex_for("expression")                  # 该组的互斥候选集
  zh_to_tag("腋下")                        # → armpits
"""
import json, os, re, random, collections

D = "/path/to/nai_codex"
DER = f"{D}/derived"
_cache = {}

# 🔴 Anima 语义组 = 渡鸦顶层分类的映射（与 nai_codex3 一致）
GROUP_MAP = {
    "identity": ["身份设定", "角色图鉴", "二次元属性", "二创属性", "招牌梗"],
    "cloth": ["泳装", "衬衫", "裙子", "鞋子", "袜子", "套装", "裤子", "上衣",
              "礼服", "传统服饰", "发饰", "头饰", "耳饰", "面部配饰", "颈部配饰", "手部配饰"],
    "pose": ["姿势-基础姿势", "手臂姿势", "腿部姿势与移动", "手势", "日常行为"],
    "scene": ["背景"],
    "view": ["视角构图"],
    "expression": ["面部表情"],
    "body": ["身体部位", "身体配饰"],
    "light": ["色彩光影"],
    "multi": ["多人互动"],
    "prop": ["物体互动"],
    "weapon": ["武器"],
    "hair": ["发型"],
    "eye": ["眼睛"],
    "style": ["画风"],
}


def _load(path, key):
    if key not in _cache:
        try:
            with open(path, encoding="utf-8") as f:
                _cache[key] = json.load(f)
        except Exception:
            _cache[key] = None
    return _cache[key]


def vocab():
    """🔴 全量 = {group: [条目...]}"""
    return _load(f"{DER}/raven_anima_groups.json", "raven_g") or {}


def zh_index():
    d = _load(f"{DER}/tag_zh_index.json", "tzh") or {}
    return d.get("zh2en", {}) or {}


def clean_tag(t):
    if t is None:
        return ""
    s = str(t).strip()
    if not s or s.startswith(";") or s.startswith("="):
        return ""
    if not re.match(r'^[0-9a-zA-Z_ ,:.\-()\[\]{}<>\'"*]+$', s):
        return ""
    return s


def zh_to_tag(kw):
    """🔴 中文 → 英文 tag 列表（近似包含兜底）"""
    idx = zh_index()
    out = list(idx.get(kw, []))
    if not out:
        for cn, ens in idx.items():
            if kw and (kw in cn or cn in kw) and len(cn) <= len(kw) + 3:
                out.extend(ens)
    return list(dict.fromkeys(out))


def pick(group, n=3, seed=None, rnd=None, exclude=()):
    """🔴 从某语义组抽 n 个 tag"""
    items = vocab().get(group) or []
    tags = []
    for it in items:
        t = clean_tag(it.get("tag"))
        if not t or t in exclude:
            continue
        if t not in tags:
            tags.append(t)
    if not tags:
        return []
    r = rnd or random.Random(seed)
    return r.sample(tags, min(n, len(tags)))


def all_tags(group):
    items = vocab().get(group) or []
    out = []
    for it in items:
        t = clean_tag(it.get("tag"))
        if t and t not in out:
            out.append(t)
    return out


def mutex_for(group, max_items=200):
    """🔴 自动生成互斥组 = 该组内的 tag 集合

    🔴 依据 = 渡鸦同一分类下的条目本质上是「同一维度的不同取值」
    （表情只能一个 / 站姿只能一个 / 眼色只能一个 / 场景只能一个）
    """
    return all_tags(group)[:max_items]


def search(kw, group=None, limit=20, loose_limit=3):
    """🔴 渡鸦组内搜索（中英文都行）

    🔴 🔴 两级命中：
       **强命中** = tag 或 title 直接等于关键词（或 tag 精确等于英文变体）
                   = onsen / 浴衣 / swimsuit / 泳装 …
       **弱命中** = 只在 note 里提到关键词
                   = spank_skirt 的 note 提到「温泉」这种 = 语义污染，降权限量

    🔴 同二级分类只保留一条 = 避免同类堆叠
    """
    cands = set([kw]) if kw else set()
    cands.update(zh_to_tag(kw) if kw else [])
    cands_l = {c.lower() for c in cands if c}
    exact_hits = []
    loose_hits = []
    seen_subs = set()
    for grp, items in vocab().items():
        if group and grp != group:
            continue
        for it in items:
            tag = clean_tag(it.get("tag"))
            title = str(it.get("title") or "")
            note = str(it.get("note") or "")
            path = str(it.get("path") or "")
            # 🔴 强命中 = tag/title 精确
            is_exact = bool(kw) and (tag.lower() == kw.lower() or title == kw or
                                     tag.lower() in cands_l)
            if not is_exact:
                blob = " ".join([tag, title, note, path]).lower()
                if not any(c and c.lower() in blob for c in cands):
                    continue
            key = (grp, it.get("sub") or "")
            if key in seen_subs:
                continue
            seen_subs.add(key)
            (exact_hits if is_exact else loose_hits).append((grp, it))
    # 🔴 弱命中限量 = 防语义污染
    hits = exact_hits + loose_hits[:loose_limit]
    return hits[:limit]


def note_of(group, tag):
    for it in vocab().get(group) or []:
        if clean_tag(it.get("tag")) == tag:
            return it.get("note") or ""
    return ""


def title_of(group, tag):
    for it in vocab().get(group) or []:
        if clean_tag(it.get("tag")) == tag:
            return it.get("title") or ""
    return ""


def stats():
    v = vocab()
    print("=== 渡鸦 Anima 词库 ===")
    for g, items in sorted(v.items(), key=lambda x: -len(x[1])):
        tops = collections.Counter(x.get("top") for x in items)
        print(f"  {g:12s} {len(items):>5d}  " + ", ".join(f"{k}×{n}" for k, n in tops.most_common(3)))
    print(f"  合计 {sum(len(x) for x in v.values()):,}")
    print(f"  中文对照 {len(zh_index()):,} 键")



def subs(group):
    """🔴 二级分类 = {sub: [条目]}"""
    out = collections.defaultdict(list)
    for it in vocab().get(group) or []:
        out[it.get("sub") or ""].append(it)
    return dict(out)


def pick_by_sub(group, sub=None, n=2, rnd=None, seed=None, dedup_top=True):
    """🔴 从指定二级分类抽 n 个 = 同类互斥，不会出现 brown_background + transparent_background

    🔴 dedup_top = 额外按**同一 top 内的互斥维度**去重
       （例：scene 组里 aqua_background / brown_background / mosaic_background 分属不同二级，
        但都是「背景」= 同一维度 = 只能留一个）

    🔴 用法：
        pick_by_sub("scene", sub="室内空间", n=2)   # 两个室内场景
        pick_by_sub("expression", sub="情绪/基础表情", n=1)
    """
    ss = subs(group)
    if not ss:
        return []
    if sub:
        if sub not in ss:
            cand = [k for k in ss if sub in k or k in sub]
            if not cand:
                return []
            sub = cand[0]
        items = ss[sub]
    else:
        r = rnd or random.Random(seed)
        sub = r.choice(list(ss.keys()))
        items = ss[sub]
    tags = []
    for it in items:
        t = clean_tag(it.get("tag"))
        if t and t not in tags:
            tags.append(t)
    r = rnd or random.Random(seed)
    sel = r.sample(tags, min(n, len(tags)))
    if dedup_top and len(sel) > 1:
        # 🔴 同一 top 内只留一个（背景只能一个 / 眼型只能一个）
        tops = {}
        keep = []
        for it in items:
            t = clean_tag(it.get("tag"))
            if t in sel and it.get("top") not in tops:
                tops[it.get("top")] = t
                keep.append(t)
        sel = keep or sel
    return sel


def mutex_subs(group):
    """🔴 该组的所有二级分类（每个 = 一个互斥单位）"""
    return {k: [clean_tag(x.get("tag")) for x in v if clean_tag(x.get("tag"))]
            for k, v in subs(group).items()}


def build_prompt(groups=None, n=2, seed=None, rnd=None, extra_tags="", head=None):
    """🔴🔴 用渡鸦词库组装一条 Anima 提示词

    🔴 groups = "identity,hair,eye,expression,pose,scene,view,light"
    🔴 每组内部按二级分类抽 = 天然避免互斥冲突
    """
    r = rnd or random.Random(seed)
    if groups is None:
        groups = ["hair", "eye", "expression", "pose", "scene", "view", "light"]
    parts = []
    for g in groups:
        tags = pick_by_sub(g, n=n, rnd=r)
        if tags:
            parts.append(", ".join(tags))
    body = ", ".join(parts)
    if extra_tags:
        body = extra_tags.strip().strip(",") + (", " + body if body else "")
    if head:
        body = head + ", " + body
    return body


if __name__ == "__main__":
    import sys
    stats()
    if len(sys.argv) > 1:
        kw = sys.argv[1]
        print(f"\n🔴 搜索 [{kw}]")
        for grp, it in search(kw, limit=12):
            print(f"  [{grp}] {it.get('tag')}  |  {it.get('title')}  |  {str(it.get('note'))[:60]}")
