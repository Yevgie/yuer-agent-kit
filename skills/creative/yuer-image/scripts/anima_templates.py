#!/usr/bin/env python3
"""Anima 正向模板层（10-31 语儿）

🔴 铁律背景 = CFG=1 + Turbo LoRA 下负向完全无效（实测像素差 0.00）
🔴 = 所有约束必须写成正向的"要什么"

🔴 本模块解决 = 正向提示词的组织方式
   法典 224 条「tag + 自然语言」写法规律：
   ① tag 串在前（身份/服饰/身体/姿势/表情/场景/视角/光/效果）
   ② 自然语言段【按语义组边界插在 tag 串中间】，不是全堆末尾
   ③ 每段 5-8 词 = 一句一个画面细节
   ④ 句尾落在具体物件（frame / wall / floor / body / face / hand）

用法：
  from anima_templates import build_prompt, TEMPLATE_PRESETS
  p = build_prompt(preset="youth_vitality", rnd=random.Random(7))
  p = build_prompt(tags="1girl, solo, nude, running, beach",
                    scene="a sunny beach", action="running along the shore",
                    camera="low angle", light="golden hour")
"""

import json, os, random, re

FRAG_LIB = "/path/to/nai_codex/derived/nl_segments.json"
_frags = None


def _load_frags():
    global _frags
    if _frags is None:
        try:
            with open(FRAG_LIB, encoding="utf-8") as f:
                _frags = json.load(f)
        except Exception:
            _frags = {}
    return _frags


# ══════════════════════════════════════════════════════════════
# 🔴 正向约束层 = 法典负向 11 组的语义反向（CFG=1 下唯一有效的通道）
# ══════════════════════════════════════════════════════════════
POS_CONSTRAINTS = {
    "anatomy": (
        "anatomically correct human body, correct human proportions, "
        "natural human joints, two arms and two legs, five fingers on each hand, "
        "well drawn anatomy, correctly drawn hands and feet"
    ),
    "quality": (
        "clean anime lineart, vibrant cel shading, sharp clear details, "
        "high quality anime illustration"
    ),
    "style_lock": (
        "pure 2D anime illustration, hand drawn anime style, "
        "not photorealistic, not a photograph"
    ),
    "composition": (
        "well composed image, clear subject, uncluttered composition"
    ),
}

# ══════════════════════════════════════════════════════════════
# 🔴 tag 语义分组 = 法典写法规律的底层结构
# ══════════════════════════════════════════════════════════════
TAG_GROUP_RULES = [
    ("identity", r"^(1girl|1boy|2girls|2boys|1other|solo|multiple girls|female focus|male focus|person|others?|no humans?|guy|girl)$"),
    ("cloth", r"(uniform|dress|skirt|shirt|blouse|blazer|coat|apron|lingerie|panties|\bra\b|bikini|swimsuit|kimono|maid|nurse|school uniform|ribbon|collar|tie|stockings|socks?|shoes|boots|sandals|hat|gloves|thighhighs|knee socks|barefoot|naked|nude|topless|bottomless|underwear|bikini bottom|sports bra|shirtless|unclothed|torn clothes|open shirt|jeans|t-shirt|hoodie|white shirt|pleated skirt|miniskirt)"),
    ("body", r"^(breasts?|huge breasts|large breasts|medium breasts|small breasts|flat chest|cleavage|nipples?|areola|abs?|muscular|slim|curvy|slender|petite|tall|large ass|ass focus|buttocks?|thighs?|hips?|waist|belly|navel|pussy|labia|clitoris)"),
    ("pose", r"(standing|sitting|kneeling|crouching|squatting|lying|on back|on stomach|spread legs|bent over|arched back|arms up|raised arms|knees to chest|legs apart|crossed legs|hugging|leaning forward|from behind|looking back|looking at viewer|on all fours|crawling|mid-jump|stepping|hand on|holding|arms behind back|hand on hip|hand up|arms crossed)"),
    ("expression", r"^(blush|smile|big smile|open mouth|closed mouth|closed eyes|half-closed eyes|expressionless|tears|sweat|panting|heavy breathing|trembling|aroused|smug|innocent|serious|sad|angry|embarrassed|tongue out|narrow eyes|drooling|orgasm|ahegao)"),
    ("scene", r"(indoors?|outdoors?|bedroom|living room|bathroom|kitchen|classroom|school hallway|clubroom|library|gymnasium|changing room|rooftop|beach|pool|shrine|garden|stage|festival|night|day|dusk|dawn|sunset|sunrise|simple background|detailed background|on bed|on chair|hotel room|school|balcony|aisle|corridor)"),
    ("view", r"(pov|from above|from below|from side|from behind|straight-on|dutch angle|close-up|wide shot|cowboy shot|full body|upper body|lower body|face focus|ass focus|foot focus|pussy focus|portrait|bust shot|profile|extreme close-up|first-person view|extreme perspective|low angle|high angle|foreshortening|wide-angle perspective)"),
    ("light", r"(sunlight|soft lighting|warm lighting|cool lighting|dim lighting|backlighting|rim lighting|volumetric lighting|neon lights|golden hour|blurry foreground|bokeh|depth of field|shiny skin|steaming body|motion blur|motion lines|speed lines|impact frame|smear|grain)"),
]

# 🔴 自然语言段 → 挂到哪个语义组后面
SEG_GROUP = {
    "scene": "scene", "action": "pose", "expression": "expression",
    "camera": "view", "light": "light", "cloth": "cloth",
    "motion": "light", "mood": "light", "anatomy": "body", "quality": "misc",
}

# ══════════════════════════════════════════════════════════════
# 🔴 段落模板 = 每段 5-8 词 = 一句一个画面细节
# ══════════════════════════════════════════════════════════════
SEGMENT_PATTERNS = {
    "scene":      "{subject} in {scene}",  # scene 文案自带 a 时自动去重
    "action":     "{subject} {action}",
    "expression": "{subject} {expression}",
    "camera":     "{camera}",
    "light":      "{light}",
    "cloth":      "{subject} wearing {cloth}",
    "motion":     "{motion}",
    "mood":       "{mood}",
    "anatomy":    "{anatomy}",
    "quality":    "{quality}",
}

SUBJECTS = ["the girl", "she", "the young woman", "her"]

# ══════════════════════════════════════════════════════════════
# 🔴 组合预设 = 法典「青春活力 NSFW」那条线的规律提炼
# ══════════════════════════════════════════════════════════════
TEMPLATE_PRESETS = {
    "youth_vitality": {
        "tags": "1girl, solo, completely nude, dynamic pose, running, mid-jump, "
                "outdoors, sweat, panting, big smile, laughing, blush, open mouth, "
                "sunlight, hair blowing, full body",
        "scene": "a sunlit school rooftop at golden hour, deep orange and blue dusk sky",
        "action": "sprinting across the rooftop and twisting her upper body back to look over her shoulder",
        "expression": "laughing openly with a wide bright smile, teeth showing, eyes bright with joy",
        "camera": "low angle looking up, dynamic diagonal composition",
        "light": "warm orange sunset backlight, hard rim light along her hair and body",
        "mood": "youthful energy and freedom",
        "motion": "her hair and clothes swept sideways by the wind, sweat flying off her",
    },
    "summer_pool": {
        "tags": "1girl, solo, completely nude, mid-jump, arched back, outdoors, "
                "pool, swimming pool, water, splashing, sweat, big smile, sunlight, "
                "dynamic pose, low angle, full body",
        "scene": "a swimming pool under a bright midday sun, turquoise water and white spray",
        "action": "arching back mid-dive into the water, arms thrown wide",
        "expression": "laughing with pure exhilaration, mouth wide open",
        "camera": "low angle, full body, frozen at the peak of the dive",
        "light": "bright midday sun, hard light, strong highlights on wet skin",
        "mood": "total youthful joy, a frozen moment of summer freedom",
        "motion": "water droplets frozen in the air around her, toes pointed tight",
    },
    "sakura_spring": {
        "tags": "1girl, solo, completely nude, sitting, outdoors, sakura, petals falling, "
                "long hair, sweat, blush, big smile, soft lighting, looking at viewer, medium shot",
        "scene": "a sunlit garden under a cherry blossom tree, pink petals drifting down",
        "action": "sitting on the grass laughing openly at the viewer",
        "expression": "laughing openly, cheeks flushed, wet hair clinging to her shoulders",
        "camera": "medium shot, soft depth of field, gentle composition",
        "light": "dappled sunlight through the branches, soft warm glow",
        "mood": "a fresh spring afternoon, playful and light",
        "motion": "pink petals drifting down around her, gentle breeze",
    },
    # ══════════════════════════════════════════════════════
    # 🔴 法典分类对应预设（10-31 新增）
    # ══════════════════════════════════════════════════════

    # ── 足底强调（法典「视角/强调」= 33 条，toes/feet/soles/foot focus 高频）──
    "foot_focus_soles": {
        "tags": "1girl, solo, indoors, hotel room, bed, night, "
                "1.35::selfie,holding phone,smartphone,covering face::, "
                "1.4::from above,lying on back,legs up,feet,soles,foot focus,spread legs,thighs::, "
                "barefoot,toes,5 toes,foot,leg focus,full body, "
                "masterpiece, best quality, highres",
        "scene": "a hotel room at night, white bedsheets and pillows, dark wooden nightstand behind her",
        "action": "lying on her back with both legs raised toward the camera, both soles pointed straight at the lens",
        "expression": "her face hidden behind the phone she is holding up",
        "camera": "extreme low angle from the foot of the bed, wide angle, the soles filling the foreground with strong foreshortening",
        "light": "warm dim bedside lamp, soft shadows on the sheets",
        "mood": "an intimate late night private photo",
    },
    # ── 挑逗诱惑姿态（法典「1girl系列」= 146 条，shiny skin/steam/blush/half-closed eyes）──
    "teasing_sensual": {
        "tags": "1girl, solo, indoors, nsfw, uncensored, blush, looking at viewer, "
                "half-closed eyes, open mouth, smile, sweat, steam, shiny skin, depth of field, "
                "nude, upper body, cowboy shot, large breasts, cleavage, navel, "
                "masterpiece, best quality, highres",
        "scene": "a dimly lit bedroom, rumpled sheets behind her, soft haze in the air",
        "action": "leaning back on her elbows with her chest lifted and her chin tilted up",
        "expression": "half-closed eyes and a slow teasing smile, lips parted, cheeks flushed",
        "camera": "cowboy shot, slightly low angle, shallow depth of field",
        "light": "warm soft light from one side, glossy highlights on damp skin",
        "mood": "lazy confident invitation",
    },
    # ── 公共场合露出（主人偏好：公共场所里露出才成立）──
    "public_exposure": {
        "tags": "1girl, solo, outdoors, daytime, crowds, public place, "
                "1.3::from below,low angle::, "
                "undressing, shirt lifted, exposed midriff, bare belly, navel, "
                "1.2::censored,mosaic::, open shirt, no bra, cleavage, "
                "masterpiece, best quality, highres",
        "scene": "a crowded shopping street at midday, blurred passersby all around her",
        "action": "lifting her shirt up with one hand while walking through the crowd",
        "expression": "a calm unbothered face, glancing down at her phone",
        "camera": "low angle shot from the pavement looking up, unnoticed candid angle",
        "light": "bright midday sunlight, hard shadows on the pavement",
        "mood": "public anonymity in broad daylight",
    },
    # ── 三人行 yuri（法典「2+girl」= 161 条，yuri/pov/tongue out/saliva）──
    "yuri_trio": {
        "tags": "2girls, yuri, indoors, bedroom, night, uncensored, nude, "
                "1.25::from above,depth of field::, "
                "blush, open mouth, panting, heavy breathing, saliva, tongue out, "
                "1.3::full body::, "
                "masterpiece, best quality, highres",
        "scene": "a bedroom at night, soft warm light spilling across the sheets",
        "action": "the two of them leaning into each other, faces pressed close, sharing one long kiss",
        "expression": "both mouths open, tongues touching, flushed cheeks, a strand of saliva between them",
        "camera": "from above, medium shot, shallow depth of field",
        "light": "warm dim lamp light, soft glow on their skin",
        "mood": "intimate tangled closeness",
    },
    # ══════════════════════════════════════════════════════
    # 🔴 分镜式漫画预设（10-31 实测：显式 NxM 网格才生效）
    # ══════════════════════════════════════════════════════

    # ── 竖排三格（实测成功：分格线清晰均匀、三格内容逐格递进）──
    "comic_3koma_vertical": {
        "tags": "comic, 3koma, three panels stacked vertically, 3x1 vertical layout, "
                "panel border, black border, 1girl, solo, "
                "a three panel vertical manga page: panel one she runs down a school corridor, "
                "panel two she stops and turns back, panel three she is laughing openly with her shirt lifted. "
                "same girl, same angle, three sequential states. "
                "monochrome, greyscale, screentone, hatched shading, lineart, no color, "
                "masterpiece, best quality, highres",
        "scene": "a japanese school corridor with metal lockers on one side and tall windows on the other",
        "action": "three sequential moments of her running down the corridor, stopping, then turning back to laugh",
        "expression": "in the last panel her eyes are closed and her mouth is wide open in a big laugh",
        "camera": "fixed eye-level medium shot, identical framing in all three panels",
        "light": "flat even indoor light, monochrome greyscale rendering",
        "mood": "a sequential manga narrative",
    },
    # ── 2x2 四格（法典原句，实测成功）──
    "comic_4koma_grid": {
        "tags": "location, comic, 4koma, 2x2 grid, four panels, panel border, 1girl, solo, "
                "a four panel comic about one girl: in the first panel she is a proper student in her school uniform, "
                "in the second panel she is flustered after class, "
                "in the third panel she is being touched in a dark room, "
                "and in the last panel she is a broken mess. "
                "it is the same single girl in every panel, drawn from the same angle each time, "
                "only her state changes from pure to ruined. depthness, dramatic lighting. "
                "masterpiece, best quality, highres, pure 2D anime illustration, hand drawn manga style",
        "scene": "a classroom, then a corridor, then a dim private room, then the same room ruined",
        "action": "four sequential states of the same girl in the same framing",
        "expression": "composed, then flustered, then overwhelmed, then completely broken",
        "camera": "identical medium shot in all four panels",
        "light": "daylight through the window, then orange sunset, then dim pink light, then neon",
        "mood": "a descent from pure to ruined",
    },
    # ── 黑白网点纸（法典 manga 标签路线）──
    "manga_bw_screentone": {
        "tags": "2girls, yuri, monochrome, greyscale, black and white, manga page, comic, border, "
                "screentone, lineart, hatched shading, no color, "
                "traditional japanese room, tatami floor, shoji screens, paper lantern, "
                "high contrast lantern light, french kiss, saliva string, nude, blush, sweat, "
                "masterpiece, best quality, highres, hand drawn manga style",
        "scene": "a traditional japanese room at night, tatami floor, shoji screens, a paper lantern casting hard light",
        "action": "the two of them leaning into each other, faces pressed close in a deep kiss",
        "expression": "mouths open, tongues touching, a strand of saliva between them",
        "camera": "medium shot, symmetrical composition",
        "light": "hard blacks and screentone shadows, strong ink contrast",
        "mood": "printed manga page, ink and screentone only",
    },
    # ══════════════════════════════════════════════════════
    # 🔴 SM / 成人向预设（10-31 实测，法典三个分类）
    # ══════════════════════════════════════════════════════

    # ── 捆绑拘束（法典「杂项涩涩/捆绑拘束」78 条）──
    "bondage_shibari": {
        "tags": "1girl, solo, nude, shibari, bondage, bdsm, red thick rope, "
                "bound arms, bound wrists, bound legs, crotch rope, arms behind back, "
                "bound ankles, saliva, trembling, motion lines, sweat, tears, "
                "1.3::from above,full body,full shot::, "
                "masterpiece, best quality, highres",
        "scene": "a dark room with a worn wooden floor, the light falling from above onto a round table",
        "action": "lying on her back on the table with both legs opened wide in an M shape, knees bent and lower legs lifted, feet pointing up",
        "expression": "tears at the corners of her eyes, trembling, biting her lip",
        "camera": "top down from directly above, wide angle, centred symmetrical composition",
        "light": "a single hard light from above, deep shadows, glossy sweat on her skin",
        "mood": "helplessly restrained",
    },
    # ── 服饰改造（法典「涩涩服饰/色情改造」26 条）──
    "outfit_rework": {
        "tags": "1girl, solo, looking at viewer, blush, navel, nipples, sweat, "
                "school uniform, serafuku, blue serafuku, white shirt, "
                "black gloves, fingerless gloves, elbow pads, armband, backpack, helmet, "
                "bike shorts, black shorts, pink panties, pink bra, "
                "clothes lift, shirt lift, clothes pull, shorts pull, panty pull, "
                "bicycle, 1.3::from below,low angle::, "
                "masterpiece, best quality, highres",
        "scene": "a sunny street corner with grey concrete walls, a bicycle handlebar at the edge of frame",
        "action": "lifting her blue top up with one hand and pulling her shorts down with the other",
        "expression": "a defiant look straight at the viewer, cheeks flushed",
        "camera": "low angle from below waist height, medium shot",
        "light": "harsh midday sunlight, strong contrast",
        "mood": "public defiance",
    },
    # ── 各种体位（法典「基础涩涩/各种体位」65 条 = 俯视正身位）──
    "missionary_topdown": {
        "tags": "1girl, 1boy, from above, 2::foreshortening::, "
                "2::face focus,face close-up::, "
                "nsfw, uncensored, vaginal, sex, missionary, full body, nude, "
                "blush, open mouth, sweat, motion lines, "
                "1.3::school gym,dim lighting,bird's eye view::, "
                "masterpiece, best quality, highres",
        "scene": "a school gym at night seen straight down from the ceiling",
        "action": "the girl is on her back with the boy above her, both seen from directly overhead",
        "expression": "her mouth open, brows drawn, eyes half closed",
        "camera": "extreme top down bird's eye view, heavy foreshortening, face close up",
        "light": "dim single overhead light, deep shadows",
        "mood": "intimate overhead",
    },
    "festival_night": {
        "tags": "1girl, solo, completely nude, mid-jump, raised arms, outdoors, "
                "festival, crowd, sweat, panting, big smile, impact frame, smear, from below",
        "scene": "a summer school festival at night, paper lanterns and fireworks behind her",
        "action": "leaping into the air with both arms thrown up in triumph",
        "expression": "cheering with her mouth wide open, flushed with excitement",
        "camera": "low angle looking up, dynamic smear lines trailing her motion",
        "light": "warm lantern light from below, saturated festival colours",
        "mood": "the peak of a summer night celebration",
        "motion": "confetti and paper lanterns drifting, sweat catching the lights",
    },
}


def _split_top(s):
    """🔴 按逗号切，但保护 :: 权重组和 {{{}}} 嵌套组不被切碎"""
    out, buf, dep = [], "", 0
    i = 0
    while i < len(s):
        ch = s[i]
        if s.startswith("{{{", i):
            j = s.find("}}}", i)
            if j < 0:
                buf += s[i:]; break
            buf += s[i:j+3]; i = j+3; continue
        if ch == ":" and s.startswith("::", i):
            j = s.find("::", i+2)
            if j < 0:
                buf += s[i:]; break
            buf += s[i:j+2]; i = j+2; continue
        if ch == ",":
            if buf.strip():
                out.append(buf.strip())
            buf = ""
        else:
            buf += ch
        i += 1
    if buf.strip():
        out.append(buf.strip())
    return out


def _group_tags(tag_list):
    """🔴 把 tag 串切成语义组 = [(组名, [tag...]), ...]

    🔴 同名组不切断 = 一个语义组只能出现一次
       （否则 expression 组被 misc 隔开 = 段被插两次 = 重复）
    """
    groups, cur_name, cur = [], None, []
    for t in tag_list:
        name = "misc"
        for gname, pat in TAG_GROUP_RULES:
            if re.search(pat, t, re.I):
                name = gname
                break
        if name != cur_name:
            if cur:
                groups.append((cur_name, cur))
            cur_name, cur = name, [t]
        else:
            cur.append(t)
    if cur:
        groups.append((cur_name, cur))

    # 🔴 合并所有同名组（不管是否连续）= 一个语义组只能出现一次
    #    否则 expression 组被 misc 隔开 = 段被插两次 = 同一句出现两遍
    order, buckets = [], {}
    for g, toks in groups:
        if g not in buckets:
            buckets[g] = []
            order.append(g)
        buckets[g].extend(toks)
    return [(g, buckets[g]) for g in order]


def _pick_frag(cat, rnd, lang="en"):
    """🔴 从法典片段库随机抽一条真实写法"""
    lib = _load_frags()
    pool = lib.get(cat, {}).get(lang, [])
    if not pool:
        return None
    return rnd.choice(pool)


# ══════════════════════════════════════════════════════════════
# 🔴🔴 法典语法层 = NovelAI 的 :: 权重语法在 Anima 上【0 改造直接可用】
# ══════════════════════════════════════════════════════════════
# 🔴 实测 = 同提示词同 seed
#   codex 版 = 1.35::selfie,...,1.4::from above,...,thighs::, 自然语言句
#   anima 版 = (selfie:1.35),...,(from above:1.4),...,thighs, 自然语言句
#   → 两张 md5 不同 = 权重都生效
#   → 但 codex 版画面更贴原意（极度低机位 + 前景双脚透视拉伸）
#   = 结论 = 直接用法典原语法，不要转 A1111 语法
#
# 🔴 法典 :: 用法统计（1047 条）
#   空权重 :: (纯分组)      1725 处
#   权重 2                    486 处   ← 最常用
#   权重 1.5                  300 处
#   权重 3                    174 处
#   权重 1.3 / 1.2 / 1.4      100/96/75 处
#   {{{ }}} 嵌套组（多选一）   61 条 (5%)
#   2::自然语言句:: 数字归属   482 条 (46%)  ← 标记这句话属于第几个人

def w(weight, *tags):
    """🔴 法典权重组 = 1.4::tag1,tag2::"""
    inner = ",".join(t.strip() for t in tags if t and t.strip())
    return f"{weight}::{inner}::"


def group(*tags):
    """🔴 法典分组 = 无权重 ::tag1,tag2::"""
    inner = ",".join(t.strip() for t in tags if t and t.strip())
    return f"::{inner}::"


def nested(*options):
    """🔴 法典嵌套组（多选一）= {{{a,b}},c}}"""
    inner = ",".join(o.strip() for o in options if o and o.strip())
    return f"{{{{{{{inner}}}}}}}"


def negw(*tags):
    """🔴 法典负权重 = -1::tag1,tag2::（Anima 生效但压制力弱 = 更像降权而非排斥）"""
    inner = ",".join(t.strip() for t in tags if t and t.strip())
    return f"-1::{inner}::"


def belong_to(n, text):
    """🔴 数字归属 = 2::这句话属于第二个人::"""
    return f"{n}::{text}::"


def build_prompt(tags="", scene="", action="", expression="", camera="",
                 light="", cloth="", motion="", mood="", anatomy="", quality="",
                 preset=None, subject="the girl", rnd=None,
                 constraints=("anatomy", "quality", "style_lock"),
                 use_frag_fallback=True, lang="en"):
    """🔴 生成 Anima 正向提示词

    🔴 顺序 = 画质前缀 → tag 串（按语义组）→ 自然语言段插在组边界 → 正向约束
    """
    rnd = rnd or random.Random()

    manual = {"scene": scene, "action": action, "expression": expression,
              "camera": camera, "light": light, "cloth": cloth,
              "motion": motion, "mood": mood, "anatomy": anatomy, "quality": quality}
    manual = {k: v for k, v in manual.items() if v}
    segs = {}

    if preset:
        P = TEMPLATE_PRESETS.get(preset)
        if P is None:
            raise ValueError(f"未知预设: {preset}（可选 {list(TEMPLATE_PRESETS)}）")
        for k, v in P.items():
            if k == "tags":
                tags = (tags + ", " + v).strip(", ") if tags else v
            else:
                segs[k] = v
    segs.update(manual)

    # 🔴 缺项时用法典真实片段兜底
    if use_frag_fallback:
        for cat, key in (("scene", "scene"), ("camera", "camera"), ("light", "light"),
                         ("motion", "motion"), ("pose", "action"), ("expression", "expression")):
            if not segs.get(key):
                f = _pick_frag(cat, rnd, lang)
                if f:
                    segs[key] = f

    # ① tag 串拆 token（保护 :: 权重组）
    tag_list = _split_top(tags) if tags else []

    # ② 组装自然语言段
    seg_order = ["scene", "action", "expression", "camera", "light", "cloth", "motion", "mood"]
    seg_texts = []
    for k in seg_order:
        v = segs.get(k)
        if not v:
            continue
        pat = SEGMENT_PATTERNS.get(k, "{subject} {scene}")
        fmt_args = dict(segs)
        fmt_args["subject"] = subject
        txt = " ".join(pat.format(**fmt_args).split())
        # 🔴 去重复冠词 = "the girl in a at night" → "the girl in a hotel room at night"
        txt = re.sub(r"\bin an? (?=a\b|an\b|the\b)", "in ", txt)
        # 🔴 段首就是 tag 组里已有的完整标签 → 删掉那个标签（例：camera 段 "cowboy shot, ..." 而 tag 里也有）
        if k in ("camera", "light", "motion", "mood") and tag_list:
            _tl = set(t.strip().lower() for t in tag_list)
            _ws = txt.split()
            while _ws and _ws[0].strip(",.").lower() in _tl and len(_ws) > 2:
                _tl.discard(_ws[0].strip(",.").lower())
                _ws = _ws[1:]
            txt = " ".join(_ws)
        # 🔴 段自带 her/his/its 主语时不再叠 "the girl"
        if re.match(r"^(the girl|she)\s+(her|his|its)\b", txt):
            txt = re.sub(r"^(the girl|she)\s+", "", txt)
        # 🔴 段以 her 开头 = 不加主语前缀
        if pat == "{subject} {expression}" and re.match(r"^(her|his|its)\b", segs.get("expression","")):
            txt = segs["expression"]
        if txt:
            seg_texts.append((k, txt))

    # ③ 🔴 自然语言段【按语义组边界插入】
    #    🔴 段级去重 = 段里的词如果 tag 串里已有，就从段里删掉那个词
    #    （例：tag 有 laughing + 段写 "laughing openly" → 段里删 laughing → "openly with a wide bright smile"）
    if False:  # 🔴 段级去重已关闭 = 法典本身就重复 = 重复即强调 = 保留
        # 🔴 只删【tag 串里【完整出现】的标签词】= 不动普通英文单词
        #    （"body" "hair" "smile" 这种是普通词，只有 "big smile" "sunlight" 这种完整标签才删）
        tag_words = set()
        for t in tag_list:
            key = re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()
            if key:
                tag_words.add(key)
        dedup_segs = []
        for k, txt in seg_texts:
            # 只删独立的完整标签短语（前后是词边界）
            new_txt = txt
            for w in sorted(tag_words, key=len, reverse=True):
                if " " in w:      # 多词标签 = 才删
                    new_txt = re.sub(r"(?<![\w])" + re.escape(w) + r"(?![\w])", "", new_txt, flags=re.I)
            new_txt = " ".join(new_txt.split())
            new_txt = re.sub(r"\s+([,.])", r"\1", new_txt)
            # 🔴 删太多就不删了 = 删完短于原文 60% = 句子会被读不通
            if len(new_txt) < len(txt) * 0.6 or len(new_txt) < 8:
                new_txt = txt
            dedup_segs.append((k, new_txt))
        seg_texts = dedup_segs

    parts = ["masterpiece, best quality, score_7, year 2025, newest, absurdres, highres"]
    if tag_list:
        groups = _group_tags(tag_list)
        seg_by_group = {}
        for k, txt in seg_texts:
            g = SEG_GROUP.get(k, "misc")
            seg_by_group.setdefault(g, []).append(txt)
        buf = []
        used_groups = set()
        for g, toks in groups:
            buf.extend(toks)
            for txt in seg_by_group.get(g, []):
                if buf:
                    parts.append(", ".join(buf))
                    buf = []
                parts.append(txt)
                used_groups.add(g)
        if buf:
            parts.append(", ".join(buf))
        # 🔴 没挂到任何组的段 = 落到末尾（不重复）
        leftover = [t for k, t in seg_texts if SEG_GROUP.get(k, "misc") not in used_groups]
        if leftover:
            parts.extend(leftover)
    else:
        parts.extend(t for _, t in seg_texts)

    # ④ 正向约束（CFG=1 下唯一有效的通道）
    for c in constraints:
        v = POS_CONSTRAINTS.get(c)
        if not v:
            continue
        for piece in [x.strip() for x in v.split(",")]:
            if piece and not any(piece in p for p in parts):
                parts.append(piece)

    return ", ".join(parts)



# ══════════════════════════════════════════════════════════════
# 🔴🔴 法典直出层（10-31 = 补齐法典三样资产：角色档案 / 画师比例 / 尺寸）
# ══════════════════════════════════════════════════════════════
# 🔴 之前只用了法典的「提示词骨架」= 丢掉了「画师比例」和「每张图用哪些人」
# 🔴 现在三层全接：
#    ① character_prompts.json = 2779 条角色档案（char1/char2/... 每人一段提示词）
#    ② artist_groups.json    = 15 套加权画师组（NAI5/NAI4.5/NAI3 各期，含负权重 artist collaboration）
#    ③ full_r18.index.json   = 11990 条全量 + 每张例图的尺寸（753x1100 竖 / 1100x753 横）

_CODEX_D = "/path/to/nai_codex/derived"
_CODEX_CACHE = {}

CODEX_QUAL_2D = ("anatomically correct human body, correct human proportions, "
                 "natural human joints, two arms and two legs, five fingers on each hand, "
                 "well drawn anatomy, correctly drawn hands and feet, clean anime lineart, "
                 "vibrant cel shading, sharp clear details, high quality anime illustration, "
                 "pure 2D anime illustration, hand drawn anime style, not photorealistic, "
                 "not a photograph")


def _codex_load(name):
    if name not in _CODEX_CACHE:
        p = os.path.join(_CODEX_D, name)
        try:
            with open(p, encoding="utf-8") as f:
                _CODEX_CACHE[name] = json.load(f)
        except Exception:
            _CODEX_CACHE[name] = None
    return _CODEX_CACHE[name]


def codex_artist_groups():
    """🔴 画师比例 = 加权画师组（15 套，含 -1~-5 的 artist collaboration 负权重）"""
    return _codex_load("artist_groups.json") or []


def codex_artist_line(group_title=None):
    """🔴 生成画师组提示词段 = `0.95::hyulla::, 0.9::artist:blue gk::, ...`"""
    groups = codex_artist_groups()
    if not groups:
        return ""
    g = None
    if group_title:
        g = next((x for x in groups if x["title"] == group_title), None)
    if g is None:
        g = groups[0]
    parts = []
    for a in g["artists"]:
        w = a["w"] if a.get("w") is not None else 1.0
        parts.append(f"{w}::{a['name']}::")
    return ", ".join(parts)


def codex_character_profiles(kw=None, n_roles=None, path=None, rnd=None):
    """🔴 每张图用到哪些人 = 角色档案检索"""
    cps = _codex_load("character_prompts.json") or []
    pool = cps
    if kw:
        k = kw.lower()
        pool = [c for c in pool if k in " ".join(
            [c.get("title") or ""] + [r["prompt"] for r in c["roles"]]).lower()]
    if n_roles:
        pool = [c for c in pool if c["n_roles"] == n_roles]
    if path:
        pool = [c for c in pool if path in "/".join(c.get("path") or [])]
    if not pool:
        return None
    return (rnd or random).choice(pool)


def build_from_codex(kw=None, n_roles=None, path=None, artist_group=None,
                     with_artists=True, extra="", rnd=None):
    """🔴🔴 法典直出 = 角色档案 + 画师组 + 尺寸 → 一条能直接喂 Anima 的提示词

    用法：
        p = build_from_codex(kw="护士", n_roles=2)
        p = build_from_codex(path="视角/强调/脚", artist_group="NAI5时期：3")
    """
    c = codex_character_profiles(kw=kw, n_roles=n_roles, path=path, rnd=rnd)
    if not c:
        return ""
    body = ", ".join(r["prompt"].strip().rstrip(",") for r in c["roles"])
    head = "masterpiece, best quality, score_7, year 2025, newest, absurdres, highres, "
    art = ""
    if with_artists:
        al = codex_artist_line(artist_group)
        if al:
            art = ", " + al
    tail = ", " + extra if extra else ""
    return head + body + art + tail + ", " + CODEX_QUAL_2D


def codex_size_of(profile):
    """🔴 每张例图的尺寸（753x1100 竖 / 1100x753 横）"""
    return profile.get("w"), profile.get("h")


# ══════════════════════════════════════════════════════════════
# 🔴🔴🔴 画风资产层（10-31 主人钦定 = 从法典原生提示词里提炼的稳定画风）
# ══════════════════════════════════════════════════════════════
# 🔴 主人原话：「这个画风效果出来非常好，你固定沉淀一下这个画风风格。」
#
# 🔴 结构 = 法典原生画师语法 + 胶片质感词 + 通用正向约束
# 🔴 画师段 = 主人原文 0 清洗（`((@diyokama))` 双括号 = 强权重，原样保留）

# ── 画风 1：电影胶片（painterly + 色差 + 重颗粒）──
# 🔴 主人实测认可 = 效果非常好
ART_STYLE_FILM = {
    "id": "film_painterly",
    "name": "电影胶片画风",
    "desc": "painterly 手绘感 + heavy chromatic aberration 色差 + heavy/film grain 重胶片颗粒",
    "artists": "(@iwonu), (@hanaseto:1.5), (@aizheajsee), @satsuki_kei, "
               "(@janis hainegom:0.6), (@christian_angel:1.5), ((@diyokama))",
    "texture": "painterly, heavy chromatic aberration, heavy grain, film grain, grainy",
    # 🔴 这几个词是画风核心 = 任何题材都用
    "core": ["painterly", "heavy chromatic aberration", "heavy grain", "film grain", "grainy"],
}

# 🔴 画风组 = 以后主人在别的提示词里认可了别的画风，往这里加
ART_STYLES = {
    "film_painterly": ART_STYLE_FILM,
}


def art_style_line(style_id="film_painterly", with_texture=True, with_artists=True):
    """🔴 生成画风段 = 画师 + 质感词（可拼进任何提示词）"""
    st = ART_STYLES.get(style_id)
    if not st:
        return ""
    parts = []
    if with_artists:
        parts.append(st["artists"])
    if with_texture:
        parts.append(st["texture"])
    return ", ".join(p for p in parts if p)


def build_with_style(tags="", style_id="film_painterly", with_artists=True,
                     with_texture=True, extra="", quality=True):
    """🔴 画风 + 内容 = 一条完整提示词

    用法：
        p = build_with_style(tags="1girl, solo, elf, white hair, twintails, ...")
        p = build_with_style(tags="1girl, nude, on bed", style_id="film_painterly")
    """
    parts = []
    if with_artists:
        parts.append(ART_STYLES[style_id]["artists"])
    if with_texture:
        parts.append(ART_STYLES[style_id]["texture"])
    if tags:
        parts.append(tags.strip().strip(","))
    if extra:
        parts.append(extra.strip().strip(","))
    body = ", ".join(p for p in parts if p)
    if quality:
        body += ", " + POS_CONSTRAINTS["anatomy"] + ", " + POS_CONSTRAINTS["quality"] + ", " + POS_CONSTRAINTS["style_lock"]
    return body


# ══════════════════════════════════════════════════════════════
# 🔴🔴🔴 渡鸦词库入口（10-31 = 渡鸦构图鉴 6633 条接入）
# ══════════════════════════════════════════════════════════════
# 🔴 raven_vocab.py 提供：pick_by_sub / subs / all_tags / search / note_of
# 🔴 用法：
#    build_raven("scene", sub="室内空间", n=2)     # 只抽室内场景
#    build_raven_style(style_id="film_painterly")  # 画风 + 渡鸦词

def _raven():
    import raven_vocab as RV
    return RV


def build_raven(groups="hair,eye,expression,pose,scene,view,light", n=2, seed=None,
                sub=None, head=None, extra_tags=""):
    """🔴🔴 用渡鸦词库组装一条 Anima 提示词（按二级分类抽 = 天然避互斥）

    🔴 groups = "hair,eye,expression,pose,scene,view,light"
    🔴 sub    = 指定某组的二级分类（如 "室内空间"），不填则每组随机一个子类
    """
    RV = _raven()
    r = random.Random(seed)
    parts = []
    for g in [x.strip() for x in groups.split(",") if x.strip()]:
        tags = RV.pick_by_sub(g, sub=sub, n=n, rnd=r)
        if tags:
            parts.append(", ".join(tags))
    body = ", ".join(parts)
    if extra_tags:
        body = extra_tags.strip().strip(",") + (", " + body if body else "")
    if head:
        body = head + ", " + body
    return body


def build_raven_style(style_id="film_painterly", groups="hair,eye,expression,pose,scene,view,light",
                      n=2, seed=None, sub=None, head=None, quality=True):
    """🔴🔴 渡鸦词库 + 画风层 = 完整 Anima 提示词"""
    RV = _raven()
    r = random.Random(seed)
    parts = []
    st = ART_STYLES.get(style_id)
    if st:
        parts.append(st["artists"])
        parts.append(st["texture"])
    for g in [x.strip() for x in groups.split(",") if x.strip()]:
        tags = RV.pick_by_sub(g, sub=sub, n=n, rnd=r)
        if tags:
            parts.append(", ".join(tags))
    body = ", ".join(p for p in parts if p)
    if head:
        body = head + ", " + body
    if quality:
        body += ", " + POS_CONSTRAINTS["anatomy"] + ", " + POS_CONSTRAINTS["quality"] + ", " + POS_CONSTRAINTS["style_lock"]
    return body


def raven_notes(tags, groups="expression,pose,eye,hair,view,light,scene"):
    """🔴 给一组 tag 附上渡鸦的中文说明（做笔记/查证用）"""
    RV = _raven()
    out = {}
    for g in [x.strip() for x in groups.split(",") if x.strip()]:
        for t in tags:
            n = RV.note_of(g, t)
            if n:
                out[t] = n
    return out

if __name__ == "__main__":
    import sys
    for pre in sys.argv[1:] or ["youth_vitality"]:
        p = build_prompt(preset=pre, rnd=random.Random(7))
        print(f"=== {pre} [{len(p)} chars]")
        print(p)
        print()
