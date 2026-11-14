#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔴 Anima（2D 动漫）提示词生成器（10-30 主人钦定「先找找资料」）

═══════════════════════════════════════════════════════════════════════
🔴 为什么单独一个生成器（写实线的规则 100% 不适用）：
   1. 标签全小写 + **空格代替下划线**（只有 score_1~9 保留下划线）
   2. 画质前缀 = "masterpiece, best quality, score_7, <safety>"
   3. 标签顺序 = [画质/元/年份/安全] [1girl] [角色] [系列] [@画师] [通用标签]
   4. 画师标签**必须带 @**（官方：不带 @ 效果极弱）
   5. 权重要比 SDXL 高（官方例："(chibi:2)"）
   6. Danbooru vs Gelbooru 冲突时用 Gelbooru
   7. 纯自然语言至少 2 句（太短会出意外）
   8. 多角色每个都要绑外观（只列名字 = 身份混乱）
   9. tag dropout 训练 = 不需要穷举标签，留高信息量的
  10. Turbo = CFG 1 + 8-12 步 + er_sde（平涂锐线）

资料：circlestone-labs/Anima 官方 model card + Yu1Ko/Anima-Prompt + Reddit 实测
═══════════════════════════════════════════════════════════════════════

用法：
  from anima_prompt import build
  print(build(subject="1girl", body="long black hair, school uniform, ...",
               artist="@askyasky"))
"""

import random

# ── 画质 / 元 / 安全 ──────────────────────────────────────────
QUALITY = {
    "score_9":  "masterpiece, best quality, score_9",
    "score_7":  "masterpiece, best quality, score_7",
    "score_5":  "normal quality, score_5",
    "none":     "masterpiece, best quality",
}

SAFETY = {
    "explicit": "explicit",
    "nsfw":     "nsfw",
    "sensitive": "sensitive",
    "safe":     "safe",
}

META_DEFAULT = ["absurdres", "highres"]

# ── 画师（必须带 @）──────────────────────────────────────────
ARTISTS = [
    "@askyasky", "@muryou", "@redjuice", "@nekomura1134", "@tiv", "@konami",
    "@dishwasher1910", "@mika pikazo", "@lack", "@swd3e2", "@kamishiro115",
    "@koyurin", "@ciloranko", "@mignon", "@sakimichan", "@rella",
    "@ilya kuvshinov", "@alphonse Mucha", "@toho", "@soda sprites",
    "@matsuri", "@nana kagura", "@torino aqua",
]

# ── 通用风格标签（画师之外）──────────────────────────────────
STYLE_TAGS = [
    "anime screenshot", "official art", "absurdres", "highres", "very aesthetic",
    "traditional media", "watercolor", "oil painting", "grainy", "film grain",
    "chromatic aberration", "light effects", "depth of field", "rim lighting",
    "sunlight", "dappled sunlight", "backlighting", "blurry",
]

LIGHT_TAGS = [
    "sunlight", "dappled sunlight", "backlighting", "rim lighting", "night",
    "indoors", "outdoors", "cloudy sky", "sunset", "partially lit",
    "soft lighting", "hard lighting", "glowing",
]

CAMERA_TAGS = [
    "portrait", "close-up", "upper body", "full body", "cowboy shot",
    "from behind", "from below", "low angle", "high angle", "dutch angle",
    "wide shot", "centered composition", "rule of thirds", "atmospheric perspective",
    "depth of field", "blurry foreground", "extreme perspective",
]

# ── 2D 线专用负向（防跑偏成 3D/写实）───────────────────────
NEGATIVE = ("worst quality, low quality, score_1, score_2, score_3, artist name, "
            "blurry, jpeg artifacts, chromatic aberration, 3d, photorealistic, "
            "semi-realistic, western cartoon, oil painting, sketch, unfinished, "
            "bad anatomy, bad hands, extra fingers, fewer digits, extra limbs, "
            "missing limbs, fused fingers, bad feet, text, watermark, signature, username")

# ── 身体/服装标签库（2D 审美用词）───────────────────────────
BODY = {
    "hair": ["long black hair", "twintails", "short black hair", "ponytail",
             "blonde hair", "silver hair", "brown hair", "bob cut",
             "hime cut", "long hair", "short hair", "messy hair", "wet hair"],
    "eyes": ["green eyes", "blue eyes", "red eyes", "heterochromia", "golden eyes",
             "purple eyes", "amber eyes", "closed eyes", "half-closed eyes"],
    "chest": ["large breasts", "medium breasts", "small breasts", "huge breasts",
              "cleavage", "breasts apart", "flat chest"],
    "body": ["slim", "tall", "curvy", "slender", "petite", "muscular"],
    "nude": ["completely nude", "nude", "topless", "bottomless", "nude female",
             "bare back", "bare buttocks", "bare feet", "no bra", "no panties",
             "shaved", "pubic hair", "spread legs", "spread pussy", "pussy",
             "anus", "between legs", "labia"],
    "cloth": ["school uniform", "sailor uniform", "blazer", "white shirt",
              "pleated skirt", "miniskirt", "thighhighs", "knee socks", "panties",
              "bra", "bikini", "swimsuit", "maid outfit", "nurse outfit",
              "kimono", "lab coat", "hoodie", "t-shirt", "jeans", "dress",
              "shinier clothes", "wet clothes", "torn clothes", "open shirt"],
    "pose": ["standing", "sitting", "lying", "kneeling", "crouching", "squatting",
             "leaning forward", "arched back", "looking at viewer", "looking back",
             "from behind", "over shoulder", "head tilt", "arms behind back",
             "legs apart", "crossed legs", "raised arms", "hands on hips",
             "on all fours", "spread legs", "lying on back", "lying on stomach"],
    "scene": ["classroom", "bedroom", "living room", "bathroom", "rooftop",
              "school hallway", "clubroom", "pool", "beach", "seaside", "hot spring",
              "festival", "shrine", "night festival", "concert", "stage",
              "convenience store", "cafe", "train", "bus", "aisle", "library",
              "gymnasium", "changing room", "balcony", "staircase", "garden"],
    "mood": ["blush", "smile", "open mouth", "closed mouth", "expressionless",
             "tears", "sweat", "panting", "aroused", "embarrassed", "serious",
             "smug", "innocent", "seductive smile"],
}

GROUPS = {
    "hair": BODY["hair"], "eyes": BODY["eyes"], "chest": BODY["chest"],
    "body": BODY["body"], "nude": BODY["nude"], "cloth": BODY["cloth"],
    "pose": BODY["pose"], "scene": BODY["scene"], "mood": BODY["mood"],
    "style": STYLE_TAGS, "light": LIGHT_TAGS, "camera": CAMERA_TAGS,
    # 🔴 2D 专属组（主人钦定：表情/动作/画面元素/风格更多样）
    "face": [], "action": [], "elements": [], "style2d": [],
}

# 🔴 2D 专属组 = 特殊标记（走 FACE / ACTION / ELEMENTS / STYLE_TIERS 库）
def _group_pool(name):
    if name == "face":
        out = []
        for v in FACE.values():
            out.extend(v)
        return out
    if name == "action":
        out = []
        for v in ACTION.values():
            out.extend(v)
        return out
    if name == "elements":
        out = []
        for v in ELEMENTS.values():
            out.extend(v)
        return out
    if name == "style2d":
        return STYLE_TIERS["strong"] + STYLE_TIERS["medium"]
    return GROUPS.get(name, [])


# ══════════════════════════════════════════════════════════════════════
# 🔴 2D 表情库（Danbooru face_tags 全集 · 主人钦定「表情冲击力更强」）
#
# 2D 表情的杀伤力 = 夸张 + 漫画符号 + 生理反应
# 写实线只能写 "木然" / "挑逗" = 2D 完全不同的表达体系
# ══════════════════════════════════════════════════════════════════════

FACE = {
    # 惊讶/ shocked
    "shock": ["surprised", "wide-eyed", "raised eyebrows", "o_o", "shock",
              "open mouth", "dropped jaw", "constricted pupils", "dilated pupils"],
    # 恐惧/panic
    "fear": ["scared", "panicking", "horrified", "screaming", "trembling",
             "traumatized", "sweat", "sweatdrop", "chocolate sweat"],
    # 愤怒/anger
    "anger": ["angry", "anger vein", "annoyed", "furrowed brow", "clenched teeth",
              "scowl", "glaring", "shouting", "yelling", "bullied", "pout"],
    # 喜悦/joy
    "joy": ["laughing", "big smile", "open mouth", "smiling", "excited",
            "happy", "^_^", "eye smile", "joy", "cheerful"],
    # 得意/ smug
    "smug": ["smug", "smirk", "doyagao", "troll face", "evil grin", "self-satisfied"],
    # 害羞/ shy
    "shy": ["blush", "flustered", "embarrassed", "shy", "tension", "sweatdrop",
            "hushed", "shy smile"],
    # 情欲/arousal（2D 特有夸张）
    "aroused": ["aroused", "ahegao", "torogao", "narrowed eyes", "open mouth",
                "clenched teeth", "staring", "drooling", "lustful", "aroused expression"],
    "ecstasy": ["ahegao", "fucked silly", "in heat", "orgasm", "afterglow",
                "drooling", "tears", "rolling eyes", "arched back", "saliva"],
    # 疲惫/呆
    "dazed": ["dazed", "blank stare", "half-closed eyes", "sleepy", "expressionless",
              "tired", "droopy eyes", "light blush", "discontent"],
    # 坏/腹黑
    "evil": ["evil smile", "crazy smile", "forced smile", "glasgow smile",
             "evil", "mischievous", "sadistic", "smug grin", "fang", "sharp teeth"],
    # 哭/ sad
    "crying": ["crying", "sobbing", "tears", "teary eyes", "bawling",
               "crying with tears", "depressed", "despair", "gloom"],
    # 呆/懵
    "blank": ["blank stare", "expressionless", "half-closed eyes", "light blush",
              "dizzy", "confused", "dazed", "unimpressed"],
    # 痛苦
    "pain": ["pain", "grimacing", "clenched teeth", "tears", "sweat",
             "biting lip", "anguish", "writhing", "head thrown back"],
}

# 漫画符号/特效表情（2D 独有 = 写实线完全没有）
FACE_SYMBOLS = [":d", ":)", ":p", "^^", "@_@", "o_o", ">_<", "x_x", "T_T",
                 ":*", ">:3", "$_$", ":q"]

# ══════════════════════════════════════════════════════════════════════
# 🔴 2D 动作库（主人钦定「动作冲击力更强」）
#
# 关键 = 动作的【瞬间】不是【状态】
#   写实线 = 站/坐/走（静态）
#   2D 线 = 冲击帧 / 速度线 / 残像 / 定格瞬间 / 动态姿势
# ══════════════════════════════════════════════════════════════════════

ACTION = {
    # 动态冲击
    "impact": ["impact frame", "cross-shaped highlight", "hit", "punch",
               "collision", "frozen in motion", "burst", "explosion",
               "smear", "motion trail", "deformation"],
    # 速度感
    "speed": ["speed lines", "motion blur", "radial blur", "dynamic angle",
              "dutch angle", "blurry foreground", "movement", "running",
              "dash", "rush", "streaking"],
    # 姿态张力
    "dynamic": ["dynamic pose", "twist", "contrapposto", "extreme pose",
                "twisting torso", "arching back", "lunging", "leaping",
                "mid-jump", "mid-fall", "bending", "twisting", "flipping hair"],
    # 头发/衣物动态
    "follow_through": ["hair blowing", "wind in hair", "flying hair",
                       "clothes flying", "skirt flying", "coat billowing",
                       "ribbons flowing", "motion in clothing", "wind"],
    # 攻击/受击
    "attack": ["punching", "kicking", "swinging", "striking", "slashing",
               "throwing", "grabbing", "pulling", "pushing"],
    "recoil": ["recoiling", "knocked back", "staggering", "flinching",
               "arched back", "head thrown back", "convulsing"],
    # 慌乱/失衡
    "chaos": ["falling", "tumbling", "losing balance", "tripping",
              "scattered", "disarray", "messy", "panic"],
    # 常规动作（比写实线更夸张的版本）
    "reaching": ["reaching", "outstretched arm", "grabbing toward viewer",
                 "hand reaching out", "leaning forward", "lunging forward"],
    "twist_back": ["twisting to look back", "looking back over shoulder",
                   "hair flip", "turning around", "glancing back"],
}

# ══════════════════════════════════════════════════════════════════════
# 🔴 2D 风格库（按 Anima 实测有效度分级 · 108 风格同 seed 对比结论）
#
# 🔴 实测结论（关键！）：
#   · cel shading / flat color / 线条类 = **几乎无效**（Anima 默认就是赛璐璐）
#   · monochrome / halftone / 漫画 / 炭笔 = **高复现率·有效**
#   · digital painting / watercolor / oil painting / gouache = **效果明显**（但四者之间难区分）
#   · 80s / 90s / retro anime / VHS = **反应良好**
#   · 需要身体变形或加物体的（chibi/mecha/magical girl）= 弱
# ══════════════════════════════════════════════════════════════════════

STYLE_TIERS = {
    # 🟢 强（实测效果明显）
    "strong": [
        "monochrome", "greyscale", "halftone", "charcoal", "chalk drawing",
        "colored pencil", "crayon", "soft pastel", "oil pastel",
        "digital painting", "watercolor", "oil painting", "gouache",
        "painterly", "traditional media", "80s anime style", "90s anime style",
        "retro artstyle", "retro anime style", "VHS", "PC-98",
        "manga", "manga style", "monochrome manga", "shoujo manga",
        "shounen manga", "seinen manga", "doujinshi", "moe style",
        "cute style", "soft moe", "semi-realistic", "gothic",
    ],
    # 🟡 中（有用但有限）
    "medium": [
        "pastel", "ink and watercolor", "line and wash", "pen and wash",
        "painterly", "sketch", "rough sketch", "simple background",
        "colored lineart", "monochrome lineart", "black lineart",
        "flat color", "limited palette", "neon style", "vaporwave colors",
        "synthwave colors", "cyberpunk colors", "fantasy", "sci-fi",
        "post-apocalyptic", "cyberpunk", "steampunk", "gothic lolita",
    ],
    # 🔴 弱（Anima 默认就有 = 加了也看不出差别）
    "weak": [
        "cel shading", "hard cel shading", "soft cel shading",
        "flat colors", "no shading", "minimal shading", "anime render",
        "highres", "absurdres", "official art", "anime screenshot",
    ],
}

# 🔴 画面元素库（2D 特有 = 写实线完全没有的符号层）
ELEMENTS = {
    # 漫画符号
    "symbols": ["speech bubble", "thought bubble", "sound effect text",
                "onomatopoeia", "manga panel", "panel borders", "screentone",
                "speed lines", "focus lines", "cross-shaped highlight"],
    # 特效
    "fx": ["sparkles", "sparkling eyes", "swirling light", "aura",
           "glowing aura", "energy", "glowing", "lens flare", "bloom",
           "magic circle", "particles", "petals", "bokeh", "light rays",
           "god rays", "silhouette", "backlight"],
    # 场景装饰
    "decor": ["sakura", "petals falling", "falling leaves", "snow",
              "rain", "confetti", "fireworks", "lanterns", "bunting",
              "paper lanterns", "torii", "bamboo", "curtains",
              "blinds", "string lights", "fairy lights", "posters"],
    # 构图元素
    "frame": ["split screen", "diagonal composition", "radial composition",
              "close-up", "extreme close-up", "dutch angle", "bird's eye view",
              "worm's eye view", "fisheye", "wide angle", "tilted horizon",
              "framing", "cropped", "panel layout"],
    # 氛围
    "atmo": ["sweat drops", "steam", "smoke", "dust", "sparkles",
             "heart eyes", "sparkling", "halo", "god rays", "backlit"],
}


# ══════════════════════════════════════════════════════════════════════
# 🔴 语义一致性（2D 提示词的命门）
#
# 官方说 tag dropout = 不需要穷举标签。但**标签之间必须语义自洽**：
#   · safe + aroused = 打架 = 模型困惑
#   · school hallway + kimono = 打架
#   · 完全裸 + 泳衣 = 打架
# 解决 = 互斥组（互斥则只留一个）+ 共现组（该出现就一起出）
# ══════════════════════════════════════════════════════════════════════

# 互斥组 = 同组只允许出现一个
MUTEX = [
    ["safe", "sensitive", "nsfw", "explicit"],
    ["school uniform", "sailor uniform", "kimono", "maid outfit",
     "nurse outfit", "lab coat", "blazer", "bikini", "swimsuit",
     "hoodie", "t-shirt", "jeans", "dress", "shirt"],
    ["completely nude", "nude", "topless", "bottomless", "no bra",
     "no panties", "school uniform", "sailor uniform", "bikini",
     "swimsuit", "maid outfit", "nurse outfit", "kimono", "lab coat"],
    ["shaved", "pubic hair"],
    ["closed eyes", "looking at viewer", "half-closed eyes", "looking away"],
    ["sitting", "standing", "lying", "kneeling", "crouching", "squatting",
     "on all fours", "lying on back", "lying on stomach"],
    ["indoors", "outdoors"],
    ["smile", "expressionless"],
    ["school athletic field", "school gate", "school rooftop", "rooftop"],
    # 🔴 场景互斥 = 不同地点不共存（school hallway + convenience store = 打架）
    # 🔴 所有场景地点 = 一个大互斥组 = 画面只能有一个地点（must 优先）
    ["classroom", "school hallway", "clubroom", "library", "gymnasium",
     "changing room", "bedroom", "living room", "bathroom", "kitchen",
     "convenience store", "cafe", "train", "bus", "aisle", "rooftop",
     "pool", "beach", "shrine", "concert", "stage", "hot spring",
     "balcony", "staircase", "garden", "warehouse",
     "school athletic field", "school gate", "school rooftop",
     "city street", "park", "canyon", "bamboo forest", "rice paddy",
     "amusement park", "carnival", "snowy mountain", "seaside"],
    # 🔴 胸型互斥
    ["flat chest", "small breasts", "medium breasts", "large breasts", "huge breasts"],
    # 🔴 表情互斥（明确对立的基本表情 = 只能留一种）
    ["serious", "smile", "big smile", "laughing", "smug", "expressionless", "angry", "crying", "sad"],
    # 🔴 表情符号互斥
    ["o_o", "^^", ":d", ">_<", "@_@", "T_T", "o3"],
]

# 共现组 = 该组里出现一个，其它自动补齐
COOCUR = {
    "school uniform": ["sailor collar", "ribbon tie", "pleated skirt"],
    "sailor uniform": ["sailor collar", "ribbon tie", "pleated skirt"],
    "kimono": ["obi", "traditional"],
    "maid outfit": ["headdress", "apron", "frills"],
    "nurse outfit": ["nurse cap", "stethoscope"],
    "bikini": ["swimsuit"],
    "swimsuit": ["bikini"],
    "completely nude": ["nude"],
    "nude": ["nude"],
    "thighhighs": ["thigh highs"],
    "large breasts": ["big breasts"],
    "huge breasts": ["big breasts", "large breasts"],
    "cleavage": ["large breasts"],
    "twintails": ["twin tails", "hair buns"],
    "ponytail": ["hair tie"],
    "school hallway": ["school"],
    "rooftop": ["sky", "outdoors"],
    "beach": ["seaside", "outdoors", "swimsuit"],
    "pool": ["swimming pool", "indoors"],
    "hot spring": ["onsen", "outdoors"],
    "night festival": ["festival", "outdoors", "night"],
    "school hallway": ["school", "indoors"],
    "classroom": ["school", "indoors"],
    "clubroom": ["school", "indoors"],
    "library": ["indoors"],
    "gymnasium": ["school", "indoors"],
    "changing room": ["indoors"],
    "bedroom": ["indoors"],
    "living room": ["indoors"],
    "bathroom": ["indoors"],
    "convenience store": ["indoors"],
    "cafe": ["indoors"],
    "train": ["indoors"],
    "bus": ["indoors"],
    "rooftop": ["outdoors", "sky"],
    "school rooftop": ["outdoors", "sky"],
    "school athletic field": ["outdoors", "sunlight", "grass"],
    # 🔴 同向情绪共现（笑 + 喘息 + 脸红 = 同一张脸）
    "big smile": ["smile", "open mouth"],
    "laughing": ["smile", "open mouth", "blush"],
    "panting": ["open mouth", "blush"],
    "sweat": ["blush"],
    "school gate": ["outdoors", "sunlight"],
    "beach": ["outdoors", "seaside"],
    "shrine": ["outdoors", "torii"],
    "concert": ["indoors", "crowd"],
    "pool": ["indoors", "swimming pool"],
    "hot spring": ["outdoors", "onsen"],
    "staircase": ["indoors"],
}

# 排除词 = 某些标签出现时，禁掉另一些
EXCLUDE = {
    "aroused": ["innocent", "expressionless", "closed eyes", "safe"],
    "innocent": ["aroused", "panting", "embarrassed"],
    "embarrassed": ["aroused", "panting"],
    "panting": ["closed eyes"],
    "expressionless": ["smile", "blush"],
    # 🔴 姿势跟场景
    "lying on back": ["standing", "sitting", "kneeling", "school hallway"],
    "lying on stomach": ["standing", "sitting", "kneeling"],
    "on all fours": ["standing", "sitting"],
    "kneeling": ["standing"],
    # 🔴 动态动作跟静态姿势
    "running": ["lying on back", "sitting", "lying on stomach"],
    "falling": ["standing", "sitting"],
    "mid-jump": ["lying on back", "sitting"],
}


# ══════════════════════════════════════════════════════════════
# 🔴🔴🔴 渡鸦构图鉴 = 自动互斥组生成器（10-31 接入）
# ══════════════════════════════════════════════════════════════
# 🔴 原理 = 渡鸦每个二级分类下的 tag 本质是「同一维度的不同取值」
#    表情只能一个 / 站姿只能一个 / 眼色只能一个 / 场景只能一个
# 🔴 6470 条真实 tag = 我手写 13 组 MUTEX 的权威替代 + 补充
#
# 🔴 用法：
#    raven_mutex_groups()          → 所有组的互斥集
#    raven_mutex("expression")     → 该组的互斥集
#    raven_coocur_hint(tag)        → 该 tag 的建议共现（来自渡鸦同子类）
#
# 🔴 关键 = 渡鸦 tag 与手写 tag 大量重叠（standing/blush/closed eyes…）
#    两者合起来 = 互斥判定更准


def _raven_vocab():
    """🔴 懒加载渡鸦词库（避免循环 import）"""
    import raven_vocab as RV
    return RV


def raven_mutex(group, max_items=400):
    """🔴 渡鸦该组的互斥 tag 集合"""
    try:
        RV = _raven_vocab()
        return RV.all_tags(group)[:max_items]
    except Exception:
        return []


def raven_mutex_groups():
    """🔴 所有组的互斥集 = {group: [tag...]}"""
    try:
        RV = _raven_vocab()
        return {g: RV.all_tags(g) for g in RV.vocab().keys()}
    except Exception:
        return {}


def raven_subs(group):
    """🔴 渡鸦该组的二级分类 = {sub: [tag...]}"""
    try:
        RV = _raven_vocab()
        return RV.mutex_subs(group)
    except Exception:
        return {}


def raven_pick(group, n=2, sub=None, rnd=None, seed=None):
    """🔴 从渡鸦某组按二级分类抽词（天然避免互斥冲突）"""
    try:
        RV = _raven_vocab()
        return RV.pick_by_sub(group, sub=sub, n=n, rnd=rnd, seed=seed)
    except Exception:
        return []


def raven_note(group, tag):
    """🔴 查渡鸦某 tag 的中文说明"""
    try:
        RV = _raven_vocab()
        return RV.note_of(group, tag)
    except Exception:
        return ""


def apply_raven_semantics(tags, rnd=None, seed=None, groups=("expression", "eye", "hair", "pose"),
                          refill=True, n=1):
    """🔴🔴 用渡鸦词库做「同二级分类去重 + 同类补位」

    🔴 原理 = 渡鸦每个二级分类下的 tag = 同一维度的不同取值
       （表情只能一个 / 站姿只能一个 / 特殊眼型只能一个 / 特殊发型只能一个）

    🔴 🔴 定位 = **扩词 + 去重**，不是替代手写互斥
       渡鸦覆盖的是「特殊/特征标签」（heterochromia / closed_eyes / on_one_knee / twintails…）
       常规标签（red_eyes / green_eyes / long_hair / standing…）仍走手写 MUTEX

    🔴 只在**同一二级分类内**去重 = 不误伤不同维度的合法搭配
       （long_hair + twintails 不同子类 = 都留；blue_eyes + heterochromia 同子类 = 只留一个）
    """
    try:
        RV = _raven_vocab()
    except Exception:
        return list(tags)
    tags = list(tags)
    r = rnd or random.Random(seed)
    for g in groups:
        subs = RV.subs(g)
        if not subs:
            continue
        # tag → 所属二级分类
        tag2sub = {}
        for sname, items in subs.items():
            for it in items:
                t = RV.clean_tag(it.get("tag"))
                if t:
                    tag2sub.setdefault(t, sname)
        present = [t for t in tags if t in tag2sub]
        if not present:
            continue
        seen = set()
        keep = []
        removed = []
        for t in present:
            sname = tag2sub[t]
            if sname in seen:
                removed.append(t)
                continue
            seen.add(sname)
            keep.append(t)
        if not removed:
            continue
        for t in removed:
            if t in tags:
                tags.remove(t)
        # 🔴 补位 = 从被删掉的那个子类里补一个（不是随机全局）
        if refill:
            for t in removed:
                sname = tag2sub[t]
                cand = [RV.clean_tag(x.get("tag")) for x in subs[sname]]
                cand = [c for c in cand if c and c not in tags]
                if cand:
                    tags.append(r.choice(cand))
    return tags


def raven_expand(tags, group="expression", n=1, rnd=None, seed=None, sub=None):
    """🔴 用渡鸦词库给一组 tag 扩词（加同类的特殊标签）"""
    try:
        RV = _raven_vocab()
    except Exception:
        return list(tags)
    tags = list(tags)
    extra = RV.pick_by_sub(group, sub=sub, n=n, rnd=rnd, seed=seed)
    for e in extra:
        if e and e not in tags:
            tags.append(e)
    return tags


def _apply_semantics(tags, rnd, must=None, avoid=None):
    """🔴 把随机标签洗成语义自洽的一组

    🔴 顺序 = 排除 → 互斥(初) → 共现 → 互斥(收) → 孤儿清理
    🔴 must 必选 = 优先级最高 = 互斥时永远保留 must 那一侧
    """
    tags = [t for t in tags if t]
    must = list(must or [])
    avoid = set(avoid or [])

    # 🔴 禁选先清（🔴 子串匹配 = "half-closed eyes" 也要被 "closed eyes" 拦掉）
    if avoid:
        def _hit(tag, av):
            # 🔴 词边界匹配 = "half-closed eyes" 命中 "closed eyes"，但 "bra" 不命中 "braided hair"
            if tag == av:
                return True
            if av in tag:
                # av 是 tag 的完整词段（前面是空格或连字符）
                i = tag.find(av)
                return i > 0 and tag[i-1] in " -"
            return False
        tags = [t for t in tags if not any(_hit(t, a) for a in avoid)]

    # 🔴 互斥组 = 保留 must 优先，否则保留最后一个
    # 🔴 must 里的标签也要参与判定（它还没进 tags = 必须手动纳入 present）
    for grp in MUTEX:
        present = [t for t in tags if t in grp]
        must_in_grp = [m for m in must if m in grp]
        if must_in_grp:
            keep = must_in_grp[0]
        elif len(present) > 1:
            keep = present[-1]
        else:
            continue
        for t in present:
            if t != keep:
                tags.remove(t)

    # ① 排除规则（🔴 must 优先 = must 命中的那一侧永远保留）
    for keep in list(tags):
        if keep in EXCLUDE:
            for bad in EXCLUDE[keep]:
                if bad in tags and bad != keep:
                    # 🔴 如果 bad 是 must 指定 = 保留 bad，删掉 keep
                    if bad in must:
                        tags.remove(keep)
                        break
                    tags.remove(bad)

    # ② 互斥组 = 只留最后一个（后出现的赢 = 用户明确指定的在后）
    for grp in MUTEX:
        present = [t for t in tags if t in grp]
        if len(present) > 1:
            for t in present[:-1]:
                tags.remove(t)

    # ③ 共现补齐（🔴 must 的共现词强制补 = must 被清掉导致配套词缺失要补回来）
    for t in list(tags):
        for extra in COOCUR.get(t, []):
            if extra not in tags:
                tags.append(extra)
    for m in must:
        for extra in COOCUR.get(m, []):
            if extra not in tags:
                tags.append(extra)

    # ④ 🔴 共现补进来的也要过 avoid（"half-closed eyes" 会被 "closed eyes" 拦掉）
    if avoid:
        def _hit2(tag, av):
            if tag == av:
                return True
            if av in tag:
                i = tag.find(av)
                return i > 0 and tag[i-1] in " -"
            return False
        tags = [t for t in tags if not any(_hit2(t, a) for a in avoid)]

    # ⑤ 🔴 收尾再互斥一次 = 共现补进来的标签可能和已有标签打架
    for grp in MUTEX:
        present = [t for t in tags if t in grp]
        must_in_grp = [m for m in must if m in grp]
        if must_in_grp:
            keep = must_in_grp[0]
        elif len(present) > 1:
            keep = present[-1]
        else:
            continue
        for t in present:
            if t != keep:
                tags.remove(t)
    # 被移除的标签，它的共现词也要清（obi/traditional 是 kimono 的共现）
    _dropped = set()
    for grp in MUTEX:
        present = [t for t in tags if t in grp]
        if len(present) > 1:
            for t in present[:-1]:
                _dropped.add(t)
    if _dropped:
        _orphans = set()
        for d in _dropped:
            for e in COOCUR.get(d, []):
                _orphans.add(e)
        tags = [t for t in tags if t not in _orphans]

    return tags


def build(subject="1girl", groups=None, quality="score_7", safety="explicit",
          artist=None, artist_weight=None, year="2025", period="newest",
          meta=None, character=None, series=None, natural_language=None,
          extra=None, seed=None, rng_tags=0, negative=None,
          must=None, avoid=None):
    """🔴 生成一条 Anima 提示词

    groups = {"hair": 1, "nude": 2, "cloth": 1, "pose": 2, "scene": 1,
              "mood": 1, "light": 1, "camera": 2, "style": 0, "chest": 1}
              数字 = 从该组随机取几个标签
    must  = 必选标签（🔴 优先级最高 = 互斥/排除规则对它们无效）
    avoid = 禁掉的标签
    """
    rnd = random.Random(seed) if seed is not None else random
    parts = []

    # ① 画质 / 元 / 年份 / 安全
    parts.append(QUALITY.get(quality, quality))
    if year:
        parts.append(f"year {year}")
    if period:
        parts.append(period)
    for m in (meta if meta is not None else META_DEFAULT):
        parts.append(m)
    parts.append(SAFETY.get(safety, safety))

    # ② 主体
    if subject:
        parts.append(subject)

    # ③ 角色（🔴 带外观描述）
    if character:
        parts.append(character)
    # ④ 系列
    if series:
        parts.append(series)

    # ⑤ 画师（🔴 必须带 @）
    if artist:
        a = artist if artist.startswith("@") else "@" + artist
        if artist_weight:
            a = f"({a}:{artist_weight})"
        parts.append(a)
    else:
        parts.append(rnd.choice(ARTISTS))

    # ⑥ 通用标签
    _tags = []
    for g, n in (groups or {}).items():
        pool = _group_pool(g)
        if not pool:
            continue
        if n <= 0:
            continue
        picked = rnd.sample(pool, min(n, len(pool)))
        _tags.extend(picked)

    # 随机补充
    for _ in range(rng_tags):
        _tags.append(rnd.choice(STYLE_TAGS))

    # 🔴 用户指定的必选/禁选
    _must = list(must or [])
    _avoid = set(avoid or [])

    # 🔴 必选先入池 = 排除/互斥规则要能看到 must 那一侧
    for m in _must:
        if m not in _tags:
            _tags.append(m)

    # 🔴 语义自洽 = 互斥/共现/排除（must 参与互斥决策）
    _tags = _apply_semantics(_tags, rnd, must=_must, avoid=_avoid)

    # 🔴 必选补回（互斥时被误清也要补回）
    for m in _must:
        if m not in _tags:
            _tags.append(m)

    parts.extend(_tags)

    if extra:
        parts.append(extra)
    # 🔴 自然语言段放最后
    if natural_language:
        parts.append(natural_language)

    prompt = ", ".join(p for p in parts if p)
    neg = negative or NEGATIVE
    return prompt, neg


# ══════════════════════════════════════════════════════════════════════
# 🔴 2D 冲击力预设（主人钦定「表情和动作冲击力更强」）
#
# 写实线 = 一句话描述一个状态
# 2D 线 = 【表情强度档】+【动作强度档】+【元素档】三层叠加 = 冲击力
# ══════════════════════════════════════════════════════════════════════

IMPACT_PRESETS = {
    # ── 日常温柔（低冲击）────────────────────────────
    "soft": {
        "face": ["shy", "joy"],
        "action": ["twist_back", "reaching"],
        "elements": ["decor"],
        "note": "日常柔和 = 微笑回头 + 一点动态",
    },
    # ── 惊讶爆点（中冲击）────────────────────────────
    "shock": {
        "face": ["shock", "fear"],
        "action": ["impact", "dynamic"],
        "elements": ["symbols", "fx"],
        "note": "惊讶 = 瞪眼 + 冲击帧 + 漫画符号",
    },
    # ── 情欲爆发（高冲击）────────────────────────────
    "ecstatic": {
        "face": ["aroused", "ecstasy"],
        "action": ["dynamic", "follow_through"],
        "elements": ["fx", "symbols"],
        "note": "情欲 = ahegao/torogao + 夸张动态 + 特效",
    },
    # ── 战斗爆发（最高冲击）──────────────────────────
    "battle": {
        "face": ["anger", "shock"],
        "action": ["impact", "attack", "speed"],
        "elements": ["symbols", "fx", "atmo"],
        "note": "战斗 = 怒/惊 + 冲击帧 + 速度线 + 火花",
    },
    # ── 混乱崩坏（动态极限）──────────────────────────
    "chaos": {
        "face": ["dazed", "blank", "crying"],
        "action": ["chaos", "impact", "speed", "follow_through"],
        "elements": ["symbols", "fx", "atmo", "decor"],
        "note": "崩坏 = 失神/泪 + 混乱动态 + 全元素",
    },
    # ── 泣血悲鸣（情绪最烈）──────────────────────────
    "anguish": {
        "face": ["crying", "pain"] if "pain" in FACE else ["crying", "fear"],
        "action": ["recoil", "dynamic", "follow_through"],
        "elements": ["symbols", "atmo", "fx"],
        "note": "悲鸣 = 痛哭 + 后仰 + 泪与汗",
    },
    # ── 得意嘲弄（反差冲击）──────────────────────────
    "smug": {
        "face": ["smug", "evil"],
        "action": ["reaching", "twist_back"],
        "elements": ["symbols"],
        "note": "得意 = 坏笑 + 伸手/回头 + 符号",
    },
    # ── 恐惧崩溃（情绪最满）──────────────────────────
    "terror": {
        "face": ["fear", "crying", "shock"],
        "action": ["chaos", "recoil"],
        "elements": ["symbols", "atmo", "fx"],
        "note": "恐惧 = 惊恐/哭/瞪眼 + 失控 + 汗与符号",
    },
}


def impact(name, rnd=None):
    """🔴 取一个冲击力预设的标签集合"""
    import random as _r
    r = rnd or _r
    p = IMPACT_PRESETS[name]
    face = []
    for k in p["face"]:
        face.extend(r.sample(FACE[k], min(2, len(FACE[k]))))
    act = []
    for k in p["action"]:
        act.extend(r.sample(ACTION[k], min(2, len(ACTION[k]))))
    els = []
    for k in p["elements"]:
        els.extend(r.sample(ELEMENTS[k], min(2, len(ELEMENTS[k]))))
    return face, act, els


def build_impact(prompt_base, impact_name="shock", rnd=None, extra_tags=None,
                 extra_nl=None):
    """🔴 把冲击力预设叠加到一个已有的 2D 提示词上

    = 写实线的做法（写完整提示词）在这里换成：
      基础提示词 + 表情层 + 动作层 + 元素层 + 自然语言补充
    """
    import random as _r
    r = rnd or _r
    face, act, els = impact(impact_name, r)
    extra = []
    if extra_tags:
        extra = list(extra_tags)
    nl = extra_nl

    parts = [prompt_base.rstrip().rstrip(",")]
    if face:
        parts.append(", " + ", ".join(face))
    if act:
        parts.append(", " + ", ".join(act))
    if els:
        parts.append(", " + ", ".join(els))
    if extra:
        parts.append(", " + ", ".join(extra))
    out = "".join(parts)
    if nl:
        out = out.rstrip() + " " + nl
    return out


def quick(subject="1girl", **kw):
    """一句话版 = 只要 prompt"""
    return build(**kw)[0]


# ══════════════════════════════════════════════════════════════════
# 🔴🔴 CFG=1 正向约束层（10-31 主人钦定 · 实测证据）
# ══════════════════════════════════════════════════════════════════
# 🔴 实测 = 干净负向 vs 45 个人体崩坏词重负向，同提示词同 seed
#    → 像素差 0.00 = 图完全一致 = 负向在 CFG=1 + Turbo LoRA 下【完全不起作用】
# 🔴 原因 = CFG 1 = 正负向等权 = 负向没有"排斥"力度，只有提示词本身的语义在起作用
# 🔴 主人的方案 = 把负向要防的东西【写成正向的"要什么"】
# 🔴 Anima 官方建议"至少 2 句自然语言" = 正好用来写这些约束

POSITIVE_CONSTRAINTS = {
    # ── 人体结构（= 法典负向里的解剖畸变组 + 手部错误组 + 腿部错误组 反向）──
    "anatomy": (
        "anatomically correct human body, correct human proportions, "
        "natural human joints, two arms and two legs, five fingers on each hand, "
        "well drawn anatomy, correctly drawn hands and feet"
    ),
    # ── 画质（= 低质量组 + 画质动画组 反向）──
    "quality": (
        "clean anime lineart, vibrant cel shading, sharp clear details, "
        "high quality anime illustration, no grain, no noise"
    ),
    # ── 构图（= 构图问题组 反向）──
    "composition": (
        "well composed image, clear subject, uncluttered composition"
    ),
    # ── 画风锁定（= 排除画风组 反向 = 明确要什么画风）──
    "style_lock": (
        "pure 2D anime illustration, hand drawn anime style, "
        "not photorealistic, not a photograph"
    ),
}


def apply_positive_constraints(prompt: str, which=("anatomy", "quality"),
                               sep=", ") -> str:
    """🔴 把约束拼到【正向】提示词尾部

    🔴 为什么要这样 = CFG=1 + Turbo LoRA 下负向提示词完全不起作用
       （实测：45 个崩坏词的负向 vs 干净负向，同 seed 像素差 0.00）
       = 所有"不要什么"必须改写成"要什么"放进正向
    """
    if not prompt:
        return prompt
    parts = [p.strip() for p in prompt.rstrip().rstrip(",").split(sep) if p.strip()]
    for w in which:
        c = POSITIVE_CONSTRAINTS.get(w)
        if not c:
            continue
        for piece in [x.strip() for x in c.split(",")]:
            if piece and piece not in parts:
                parts.append(piece)
    return ", ".join(parts)
