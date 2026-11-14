#!/usr/bin/env python3
"""🔴🔴🔴 中文混合描述解析器（10-31 语儿）

🔴 **主人说**「红黑魔女风格的猫耳腋下少女，夜晚室内，跪姿」
🔴 **我拆成三层**
   ① 解构配方层 = 匹配到解构原典的标题 → 「红黑魔女」整套配方
   ② 渡鸦细节层 = 匹配到渡鸦词库的 tag/title → 精确 Danbooru tag
   ③ 普通翻译层 = 剩下的中文 → 官方 tag_zh 词库翻英文

🔴 **分流判据**（按优先级，先命中先占位）
   ① 解构原典标题（最长匹配，优先长标题）
   ② 渡鸦词库精确命中（tag 或 title 等于该词）= 拿它的原始 tag（带下划线的 Danbooru 原形）
   ③ tag_zh 翻译 = 通用英文 tag

🔴 **为什么要 ③ 让位给 ②** = 渡鸦的 tag 是 Danbooru 权威写法
   （`cat_ears` 比 `cat ear` 更准 = 社区用得更多）

🔴 用法：
  from cn_desc import parse_desc
  r = parse_desc("红黑魔女风格的猫耳腋下少女，夜晚室内，跪姿")
  r["recipe"], r["raven"], r["plain"]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_LIB = os.path.expanduser("~/.hermes/skills/creative/yuer-style-library")
for _p in (HERE, STYLE_LIB):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_cache = {}

# 🔴 中文 → Danbooru 权威写法（渡鸦未命中时，用这张表保证下划线风格）
DANBOORU_FIX = {
    "cat ear": "cat_ears",
    "cat ears": "cat_ears",
    "black pantyhose": "black_pantyhose",
    "white pantyhose": "white_pantyhose",
    "pointy ears": "pointy_ears",
    "red eyes": "red_eyes",
    "green eyes": "green_eyes",
    "blue eyes": "blue_eyes",
    "long hair": "long_hair",
    "short hair": "short_hair",
    "twintails": "twintails",
    "looking at viewer": "looking_at_viewer",
    "looking down": "looking_down",
    "looking up": "looking_up",
    "close-up": "close-up",
    "full body": "full_body",
    "upper body": "upper_body",
    "simple background": "simple_background",
    "detailed background": "detailed_background",
    "closed eyes": "closed_eyes",
    "open mouth": "open_mouth",
    "closed mouth": "closed_mouth",
    "half-closed eyes": "half-closed_eyes",
    "from above": "from_above",
    "from below": "from_below",
    "from behind": "from_behind",
    "sitting": "sitting",
    "standing": "standing",
    "lying": "lying",
    "kneeling": "kneeling",
    "on the floor": "on_the_floor",
    "hands over head": "hands_over_head",
    "hair over eyes": "hair_over_eyes",
    "bare shoulders": "bare_shoulders",
    "bare legs": "bare_legs",
    "barefoot": "barefoot",
    "white dress": "white_dress",
    "black dress": "black_dress",
    "school uniform": "school_uniform",
    "nurse costume": "nurse_costume",
    "swimsuit": "swimsuit",
    "bikini": "bikini",
    "nude": "nude",
    "large breasts": "large_breasts",
    "medium breasts": "medium_breasts",
    "small breasts": "small_breasts",
    "long legs": "long_legs",
    "high heels": "high_heels",
    "see through": "see-through",
    "high heels": "high_heels",
    "high heels": "high_heels",
    "red hair": "red_hair",
    "sheer top": "sheer_top",
    "sheer bra": "sheer_bra",
    "see-through dress": "see-through_dress",
    "white top": "white_top",
    "black top": "black_top",
    "straight hair": "straight_hair",
    "curly hair": "curly_hair",
    "blonde hair": "blonde_hair",
    "silver hair": "silver_hair",
    "black hair": "black_hair",
    "white hair": "white_hair",
    "huge breasts": "huge_breasts",
    "medium breasts": "medium_breasts",
    "small breasts": "small_breasts",
    "large breasts": "large_breasts",
    "hands over head": "hands_over_head",
    "looking down": "looking_down",
    "looking up": "looking_up",
    "see through": "see-through",
}


def _jiegao():
    if "jg" not in _cache:
        import nai_codex3 as NC
        _cache["jg"] = NC.jiegao_chapters()
    return _cache["jg"]


def _raven():
    if "rv" not in _cache:
        import raven_vocab as RV
        _cache["rv"] = RV
    return _cache["rv"]


def _zh():
    if "zh" not in _cache:
        import zh_translate as ZT
        _cache["zh"] = ZT
    return _cache["zh"]


# 🔴 停用词 = 这些中文单独翻出来是噪声
#   （「风格」→style · 「少女」→shojo 二次元画风 · 「风格」已被配方占用）
STOPWORDS = {
    "风格", "的", "了", "和", "与", "及", "以", "感觉", "样子", "风格感",
    "少女", "少年", "女生", "男孩", "女性", "男性", "人物", "角色",
    "一个", "这个", "那个", "画", "感觉", "氛围", "构图", "镜头",
}


def _norm(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def seg_zh(text, maxlen=8):
    """🔴🔴🔴 词典最长匹配分词 = 用官方 tag_zh 词典（12.5 万键）当分词器

    🔴 为什么不用 jieba = tag_zh 词典本身就是 Danbooru tag 的中文名
       = 天然分词边界 = 「猫耳腋下少女」→ 猫耳 / 腋下 / 少女 ✓
       「跪姿双手举过头顶」→ 跪姿 / 双手举过头顶 ✓
    """
    ZT = _zh()
    zh2en, _ = ZT._index()
    out = []
    for seg in re.findall(r"[\u4e00-\u9fff]+|[^\u4e00-\u9fff]+", text or ""):
        if not re.match(r"^[\u4e00-\u9fff]+$", seg):
            out.append(seg)
            continue
        i = 0
        while i < len(seg):
            hit = None
            # 🔴🔴 歧义表优先 = 「高跟」不在 tag_zh 词典里但必须整体识别
            for L in range(min(maxlen, len(seg) - i), 0, -1):
                w = seg[i:i + L]
                if w in ZT.AMBIGUOUS:
                    hit = w
                    break
            if not hit:
                for L in range(min(maxlen, len(seg) - i), 0, -1):
                    w = seg[i:i + L]
                    if w in zh2en:
                        hit = w
                        break
            if hit:
                out.append(hit)
                i += len(hit)
            else:
                out.append(seg[i])
                i += 1
    return out


# 🔴 通用词标题 = 不能当配方用
#   解构原典里有「夜晚」「白天」「室内」「室外」这种标题 = 通用词 = 误匹配元凶
GENERIC_TITLES = {
    "夜晚", "白天", "室内", "室外", "泳装", "猫耳", "室内空间", "户外",
    "夜景", "白天室内", "夜晚室内", "少女", "少年", "少女风格", "人物",
    "室内场景", "室外场景", "构图", "光影", "表情", "姿势",
}


def match_recipes(text, limit=2):
    """🔴 匹配解构原典标题 = 最长优先（避免「魔女」抢走「红黑魔女」）

    🔴 🔴 通用词标题必须排除 = 解构原典有「夜晚」「室内」这种标题
       = 不排除的话「猫耳腋下夜晚室内」会匹配到「夜晚」那套 = 完全跑偏
    """
    jg = _jiegao()
    norm = _norm(text)
    hits = []
    for e in jg:
        t = _norm(e.get("title"))
        if not t or len(t) < 2:
            continue
        if t in GENERIC_TITLES or t in STOPWORDS:
            continue
        if t in norm:
            hits.append((len(t), e))
    hits.sort(key=lambda x: -x[0])
    # 去重叠（已被更长标题覆盖的短标题丢掉）
    chosen = []
    for ln, e in hits:
        t = _norm(e.get("title"))
        if any(t in _norm(c.get("title")) for c in chosen):
            continue
        chosen.append(e)
        if len(chosen) >= limit:
            break
    return chosen


# 🔴 滑窗噪声 = 这些 4 字片段在 note 里出现但本身不是 tag
SLIDE_NOISE = {
    "冻结水滴", "睡觉的猫", "风格的黑", "魔女风格", "的黑魔", "猫耳腋下",
    "腋下少女", "的黑衣", "的黑丝", "的胸部", "的裙子",
}

# 🔴 精确白名单 = 这些 4 字词确实是 Danbooru tag 概念
EXACT_OK = {
    "猫耳腋下", "腋下少女", "黑色丝袜", "白色丝袜", "黑色内衣",
    "红色眼睛", "蓝色眼睛", "绿色眼睛", "金色头发", "银色头发",
    "黑色头发", "白色头发", "粉色头发", "紫色头发", "蓝色头发",
    "长直发", "双马尾", "高马尾", "短发卷发", "波浪卷发",
    "绝对领域", "透视上衣", "透明上衣", "吊带睡裙", "黑色长袜",
    "白色长袜", "黑色内裤", "白色内裤", "黑色胸罩", "白色胸罩",
}


def match_raven(text, limit=8):
    """🔴 匹配渡鸦词库 = 只取精确命中 = 拿权威 Danbooru tag

    🔴🔴 用**词典分词**逐词查（不是滑窗）= 滑窗会抽出噪声
       （「红黑魔女风格的猫耳腋下少女」滑窗 → `droplets frozen` `sleeping cat`）
    🔴 返回 [(tag, 中文片段)] = 片段要回填并从文本挖掉
    """
    RV = _raven()
    out = []
    seen = set()
    used_frag = []
    for frag in seg_zh(text):
        if not re.match(r"^[\u4e00-\u9fff]+$", frag):
            continue
        if frag in used_frag or frag in STOPWORDS:
            continue
        if frag in (_cache.get("recipe_chars") or set()):
            continue
        # 🔴🔴 单字中文不去查渡鸦 = 「跟」「的」「高」这类会误命中
        #    （实测「高跟」切成「高」「跟」后「跟」命中 `gundam` = 高达 = 完全跑偏）
        if len(frag) < 2:
            continue
        hits = RV.search(frag, limit=4, loose_limit=0)
        for grp, it in hits:
            tag = RV.clean_tag(it.get("tag"))
            title = _norm(it.get("title"))
            if not tag or tag in seen:
                continue
            if _norm(tag) != _norm(frag) and title != _norm(frag):
                continue
            seen.add(tag)
            used_frag.append(frag)
            out.append((tag, frag))
            if len(out) >= limit:
                return out
    return out


def parse_desc(text):
    """🔴🔴 解析中文混合描述 → 三层

    返回 dict:
      recipe  = 解构原典配方串（可空）
      raven   = 渡鸦权威 tag 列表
      plain   = 普通翻译 tag 列表
      used    = 已占位的中文片段（避免重复翻译）
    """
    if not text:
        return {"recipe": "", "raven": [], "plain": [], "used": []}
    recipes = match_recipes(text)
    # 🔴🔴🔴 配方标题的分字要先算出来（match_raven 之前）= 禁给渡鸦
    #    （「红黑」在渡鸦里 = 明日方舟角色 projekt_red / schwarz = 完全跑偏）
    recipe_chars = set()
    for e in recipes:
        for c in re.findall(r"[\u4e00-\u9fff]+", e.get("title") or ""):
            recipe_chars.add(_norm(c))
    _cache["recipe_chars"] = recipe_chars

    raven = match_raven(text)
    used = []
    for e in recipes:
        used.append(_norm(e.get("title")))
        for c in recipe_chars:
            used.append(c)
    for t, frag in raven:
        used.append(_norm(t))
        used.append(_norm(frag))
    used_set = set(used)

    # 🔴 剩下的中文 → 普通翻译
    #    🔴 关键 = 先把**已占位的中文原文**从文本里挖掉
    ZT = _zh()
    plain = []
    rest = text or ""
    for e in recipes:
        title = e.get("title") or ""
        if title:
            rest = rest.replace(title, " ")
            for c in re.findall(r"[\u4e00-\u9fff]+", title):
                rest = rest.replace(c, " ")
    for t, frag in raven:
        rest = rest.replace(t, " ")
        rest = rest.replace(frag, " ")

    # 🔴🔴🔴 剩下的中文 → 普通翻译
    #    🔴 关键 = 先把**已占位的中文原文**从文本里挖掉
    #    （不然「红黑魔女风格」整段被抓 → 配方标题的分字全被单独翻 = 噪声）
    ZT = _zh()
    plain = []
    rest = text or ""
    for e in recipes:
        title = e.get("title") or ""
        if title:
            rest = rest.replace(title, " ")
            # 标题里的中文分字也去掉（「红黑魔女」→ 去掉「红」「黑」「魔女」）
            for c in re.findall(r"[\u4e00-\u9fff]+", title):
                rest = rest.replace(c, " ")
    for t, frag in raven:
        rest = rest.replace(t, " ")
        rest = rest.replace(frag, " ")

    for c in seg_zh(rest):
        if not re.match(r"^[\u4e00-\u9fff]+$", c):
            continue
        cn = _norm(c)
        if not cn or cn in STOPWORDS or cn in used_set:
            continue
        got = ZT.translate_term(c)
        if got and any(got == t for t, _ in raven):
            continue
        if not got:
            continue
        if got not in plain:
            plain.append(got)

    # 🔴 统一 Danbooru 下划线写法
    plain = [DANBOORU_FIX.get(p, p) for p in plain]

    recipe = ""
    if recipes:
        import nai_codex3 as NC
        recipe = NC.jiegao_build(title=recipes[0].get("title"))
    return {"recipe": recipe, "raven": [t for t, _ in raven], "plain": plain, "used": used}


def build(desc, style=None, groups=None, n=1, seed=7, head=None):
    """🔴🔴🔴 一条命令 = 中文描述 → 完整提示词

    🔴 层序 = ① 解构配方 ② 渡鸦细节 ③ 普通翻译 ④ 画风层
    """
    import anima_templates as AT
    d = parse_desc(desc)
    layers = []
    if d["recipe"]:
        layers.append(d["recipe"])
    if d["raven"]:
        layers.append(", ".join(d["raven"]))
    if d["plain"]:
        layers.append(", ".join(d["plain"]))
    if style:
        gs = groups or ""
        st = AT.build_raven_style(style_id=style, groups=gs, n=0, seed=seed, head=head)
        if st:
            layers.append(st)
    prompt = ", ".join(x for x in layers if x)
    # 去重
    seen = set()
    keep = []
    for t in [x.strip() for x in prompt.split(",") if x.strip()]:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            keep.append(t)
    return ", ".join(keep), d


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("desc")
    ap.add_argument("--style")
    ap.add_argument("--head")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out")
    a = ap.parse_args()
    p, d = build(a.desc, style=a.style, head=a.head, seed=a.seed)
    print(f"🔴 配方: {d['recipe'][:80] or '(无)'}")
    print(f"🔴 渡鸦: {d['raven']}")
    print(f"🔴 翻译: {d['plain']}")
    print(f"\n[{len(p)} chars]\n{p}")
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(p)
        print(f"\n✅ 已存 {a.out}")
