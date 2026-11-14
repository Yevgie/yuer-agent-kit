#!/usr/bin/env python3
"""🔴🔴🔴 中文 → 英文 tag 翻译层（10-31 语儿）

🔴 **为什么需要** = 主人说中文（「腋下 透视 猫耳」）我得能直接出图
🔴 **数据源** = 官方 tag_zh 社区中文词库（Auto-NovelAI-Refactor，GPL-3.0）
   = `derived/tag_zh_index.json` = 125,426 个中文键 · 142,826 个英文键
🔴 **思路** = 中文词 → 精确查 zh2en → 取最优英文 tag
   查不到 → 走法典中文对照（nai_codex3）→ 再不行 → 原样保留（Anima 能吃中文）

🔴 **用法**：
  from zh_translate import translate_prompt
  translate_prompt("腋下 透视 猫耳")   # → "armpits, see through, nekomimi"
  translate_prompt("1girl, 腋下, solo")  # → 混合输入，只翻中文段
"""
import os
import re
import sys

DER = "/path/to/nai_codex/derived"
STYLE_LIB = os.path.expanduser("~/.hermes/skills/creative/yuer-style-library")
if STYLE_LIB not in sys.path:
    sys.path.insert(0, STYLE_LIB)

_cache = {}

# 🔴 优先选这些 = 最标准最通用的写法（不是冷僻变体）
PREFERRED = [
    # 姿势 / 体位
    "standing", "sitting", "lying", "kneeling", "crouching", "squatting",
    # 视角
    "from above", "from below", "from behind", "from the front",
    # 表情
    "smile", "open mouth", "closed mouth", "blush", "tears", "closed eyes", "open eyes",
    # 衣物
    "naked", "topless", "bottomless", "lingerie", "bikini", "swimsuit",
    # 身体
    "large breasts", "small breasts", "medium breasts", "long hair", "short hair",
    # 场景
    "outdoors", "indoors", "night", "day", "sunset", "sunrise",
    # 通用
    "1girl", "solo", "looking at viewer", "simple background", "detailed background",
]

# 🔴 明确不想要的（社区符号 / 修饰性后缀 / 太泛）
BAD = {
    "", "text", "no text", "translated", "official", "comment",
}

# 🔴🔴 歧义中文 = 一个中文对应多个完全不同的概念 = 必须人工指定
#   （不能靠长度/频次猜 = 「透视」既是 perspective 又是 see through）
AMBIGUOUS = {
    "透视": "see through",          # 衣物透视 = see through（不是 perspective 视角）
    "透视法": "perspective",
    "腋下": "armpits",               # Danbooru 标准复数
    "腋毛": "armpit hair",
    "胸部": "breasts",
    "奶子": "breasts",
    "屁股": "ass",
    "内裤": "panties",
    "裸体": "nude",
    "全裸": "completely nude",
    # 🔴 视角/机位
    "低头": "looking down",
    "抬头": "looking up",
    "特写": "close-up",
    "全身": "full body",
    "全身照": "full body",
    "半身": "upper body",
    "前倾": "leaning forward",
    "后仰": "leaning back",
    "俯视": "from above",
    "仰视": "from below",
    "侧视": "from the side",
    "室外": "outdoors",
    "室外": "outdoors",
    "白天": "daytime",
    "夜晚": "night",
    "微笑": "smile",
    "大笑": "open mouth",
    # 🔴 渡鸦/词库里这些词有歧义或错译
    "高跟": "high heels",
    "高跟鞋": "high heels",
    "透视上衣": "sheer top",
    "透视内衣": "sheer bra",
    "透视裙": "see-through dress",
    "透明上衣": "sheer top",
    "白色上衣": "white top",
    "黑色上衣": "black top",
    "红发": "red hair",
    "红发色": "red hair",
    "黑发": "black hair",
    "白丝": "white pantyhose",
    "黑丝": "black pantyhose",
    "金发": "blonde hair",
    "银发": "silver hair",
    "双马尾": "twintails",
    "马尾": "ponytail",
    "直发": "straight hair",
    "卷发": "curly hair",
    "短发": "short hair",
    "长发": "long hair",
    "披肩发": "medium hair",
    "大胸": "large breasts",
    "小胸": "small breasts",
    "美乳": "large breasts",
    "巨乳": "huge breasts",
    # 🔴 写实线常用（直译会翻歪）
    "监控": "cctv",
    "监控偷拍": "candid",
    "偷拍": "candid",
    "写实": "realistic",
    "真实": "realistic",
    "照片": "photo",
    "实拍": "photorealistic",
    "自拍": "selfie",
    "路人": "passerby",
    "街边": "street",
    "街道": "street",
    "日常": "everyday",
    "网红": "instagram model",
    "精修": "beauty photo",
    "美颜": "beauty filter",
    "高清写真": "high resolution photo",
    "室内": "indoors",
    "室外": "outdoors",
    "夜晚": "night",
    "白天": "daytime",
}

# 🔴 Danbooru 标准复数 = 优先选这些（社区最通用）
STANDARD = [
    "armpits", "breasts", "nipples", "ears", "eyes", "hair", "hands", "feet",
    "knees", "thighs", "calves", "arms", "legs", "shoulders", "hips",
    "pussy", "pupils", "eyelashes", "freckles", "tears", "sweat",
]


def _index():
    if "idx" not in _cache:
        import json
        p = f"{DER}/tag_zh_index.json"
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            _cache["idx"] = (d.get("zh2en") or {}, d.get("en2zh") or {})
        except Exception:
            _cache["idx"] = ({}, {})
    return _cache["idx"]


def _pick(en_list, zh=""):
    """🔴 从多个英文候选里挑最优

    🔴 判据（按优先级）：
       ① 在 PREFERRED 白名单里 = 最标准写法
       ② 出现次数最多的 = 社区通用写法
       ③ 越短越好（长尾变体通常更长更冷僻）
    🔴 🔴 不再单纯按长度 = 会挑到 `x ray`（透视的错译）而不是 `see through`
    """
    if not en_list:
        return ""
    clean = []
    for t in en_list:
        t = (t or "").strip()
        if not t or t.lower() in BAD:
            continue
        # 🔴🔴🔴 11-14 修（社区词库脏数据）：tag_zh_index.json 的 zh2en 有 389 个键
        #    带 `}}}` / `]}` 这类抓取残留（社区原帖的括号注释没清干净）
        #    实测 = 「上身赤裸」模糊命中「袈裟且上身赤裸」→ 选出 "kasaya}topless"
        #    判据 = 候选里含 } ] 【 】 或其他闭合括号 = 不是 tag = 整条丢掉
        if re.search(r"[}\]【】]", t):
            continue
        # 🔴 过滤带权重/通配符的候选（`1.5:*full body` `close-up  2` 这类不能直接用）
        if re.search(r"[*\d]+:", t) or "::" in t:
            continue
        if re.search(r"\s{2,}", t):
            continue
        if t.endswith(".") or t.endswith(":"):
            continue
        # 🔴 过滤非拉丁（韩文/日文/中文候选 = 不是我要的 tag）
        if any(ord(c) > 0x2E7F and not c.isascii() for c in t):
            continue
        if t not in clean:
            clean.append(t)
    if not clean:
        return ""
    for p in PREFERRED:
        if p in clean:
            return p
    for p in STANDARD:
        if p in clean:
            return p
    # 🔴 频次高的优先（社区最常用写法）
    cnt = {}
    for t in clean:
        for w in t.replace("_", " ").split():
            cnt[w] = cnt.get(w, 0) + 1
    def score(t):
        words = t.replace("_", " ").split()
        # 单复数归一
        norm = " ".join(sorted({w.rstrip("s") for w in words}))
        return (len(t), -cnt.get(norm.split()[0], 0) if words else 0, t)
    return sorted(clean, key=score)[0]


def translate_term(zh):
    """🔴 单个中文词 → 英文 tag（查不到返回空）"""
    zh = (zh or "").strip()
    if not zh:
        return ""
    # 🔴 歧义词优先人工指定
    if zh in AMBIGUOUS:
        return AMBIGUOUS[zh]
    zh2en, _ = _index()
    if zh in zh2en:
        got = _pick(zh2en[zh], zh)
        if got:
            return got
    # 变体：去空格 / 加空格
    for variant in (zh.replace(" ", ""), zh.replace(" ", "_")):
        if variant in zh2en:
            got = _pick(zh2en[variant], zh)
            if got:
                return got
    # 模糊：中文键里包含
    hits = [k for k in zh2en if zh and zh in k and len(k) <= len(zh) + 3]
    if hits:
        best = sorted(hits, key=len)[0]
        got = _pick(zh2en[best], zh)
        if got:
            return got
    return ""


def translate_prompt(text, sep=",", keep_untranslated=True, report=None):
    """🔴🔴 整段提示词翻译 = 中文段翻英文，英文原样保留

    🔴 **分词策略**（关键）：
       ① 先按逗号切 = Anima 的标准分隔
       ② 每段里如果**整段是中文** = 再按空格切词逐个翻
          （否则「腋下 透视 猫耳」会被当成一个词 = 错）
       ③ 段里中英混合 = 只翻中文 token，英文 token 原样
       ④ 中文逗号（，）也当分隔符

    🔴 查不到的中文保留原样（Anima 吃中文）
    """
    if not text:
        return text
    # 🔴 中文逗号也当分隔
    text = text.replace("，", ",")
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    out = []
    changed = []
    for p in parts:
        if not re.search(r"[\u4e00-\u9fff]", p):
            out.append(p)
            continue
        # 🔴 整段中文 + 含空格 = 按空格拆词
        tokens = p.split()
        if len(tokens) > 1 and all(re.search(r"[\u4e00-\u9fff]", t) for t in tokens):
            new_toks = []
            hit = False
            for t in tokens:
                got = translate_term(t)
                if got:
                    new_toks.append(got)
                    hit = True
                else:
                    new_toks.append(t)
            np_ = ", ".join(new_toks) if hit else p
            if hit:
                changed.append((p, np_))
            out.append(np_)
            continue
        # 🔴 中英混合 = 逐 token 翻
        new_toks = []
        hit = False
        for t in tokens:
            if re.search(r"[\u4e00-\u9fff]", t):
                got = translate_term(t)
                if got:
                    new_toks.append(got)
                    hit = True
                else:
                    new_toks.append(t)
            else:
                new_toks.append(t)
        np_ = " ".join(new_toks)
        if hit:
            changed.append((p, np_))
        out.append(np_)
    if report is not None:
        report.extend(changed)
    return sep.join(out)


def translate_file(path_in, path_out=None):
    with open(path_in, encoding="utf-8") as f:
        t = f.read().strip()
    rep = []
    nt = translate_prompt(t, report=rep)
    if path_out:
        with open(path_out, "w", encoding="utf-8") as f:
            f.write(nt)
    return nt, rep


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?", help="要翻译的中文（留空则从 stdin）")
    ap.add_argument("--file", help="从文件读")
    ap.add_argument("--out", help="输出文件")
    a = ap.parse_args()

    if a.file:
        nt, rep = translate_file(a.file, a.out)
        print(f"🔴 翻了 {len(rep)} 段：")
        for o, n in rep:
            print(f"   {o}  →  {n}")
        print(f"\n{nt}")
    else:
        t = a.text or sys.stdin.read()
        rep = []
        print(translate_prompt(t, report=rep))
        for o, n in rep:
            print(f"   {o}  →  {n}", file=sys.stderr)
