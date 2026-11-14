#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔴 语儿风格资产库（10-30 主人钦定「风格资产的沉淀看起来很有价值」）

═══════════════════════════════════════════════════════════════════════
🔴 铁律一：风格 ≠ 题材
   风格 = 怎么拍（机位 / 光线 / 画质 / 色调 / UI 叠加）
   题材 = 拍谁拍哪（人物身份 / 场景 / 服装 / 动作）
   = 两层**完全解耦** = 任意组合
═══════════════════════════════════════════════════════════════════════

主人原话（10-30 打脸修正）：
  「这 f 类，不是说绑定了学生主题，不是的。f 类本就是一个风格主题，
    你应该根据需求分析选择使用，不是绑定学生或者 cos，这是不对的。
    cos 可以是监控 G 类，也可以是写真艺术感。」

→ 所以：**0 靠提示词关键词猜风格**。风格 = 显式 `--style <id>`。
→ 每个风格 = 一个资产（一份可复用的片段 + 一组替换规则）。

用法：
  from yuer_styles import get_style, apply_style
  st = get_style("f")
  prompt = apply_style(st, prompt)
"""

import re
import random
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════
# 🔴 画质片段库 = 风格之间共用/差异的零件
# ══════════════════════════════════════════════════════════════════════

# F 风格画质 = 低画质低解析力（主人钦定「很棒 非常棒」）
LOW_QUALITY = (
    "low-quality amateur recording, very low resolution, soft blurry focus, "
    "heavy JPEG compression artifacts, blocky pixelation, washed-out pale colors, "
    "undersaturated muted tones, visible compression noise, degraded detail, "
    "poor sharpness."
)

# E 风格画质 = 监控绿调 + 传感器噪点 + 隔行扫描线
E_QUALITY = (
    "raw amateur aesthetic, heavy digital sensor noise, interlaced scanlines. "
    "Hyper-detailed skin textures: visible pores, goosebumps, realistic skin folding. "
    "Authentic green-tinted security feed."
)

# G 风格画质 = 监控 UI 叠加 + 粗糙颗粒
G_QUALITY = (
    "grainy low quality CCTV footage, low resolution, slight motion smearing, "
    "muted washed-out colors, visible compression noise, degraded detail."
)

# 艺术感画质 = 高画质浅景深（cos 写真艺术感用）
ART_QUALITY = (
    "professional full-frame photography, 85mm lens, f/2.0, shallow depth of field, "
    "creamy smooth bokeh, natural skin rendering with visible fine texture, "
    "soft diffused key light, high dynamic range, filmic color grading, "
    "subtle halation on highlights, no noise, tack sharp focus on the eyes."
)

# ══════════════════════════════════════════════════════════════════════
# 🔴 机位片段库
# ══════════════════════════════════════════════════════════════════════

CAM_E = ("A photo taken from a rear viewpoint, phone flash photography, "
         "strong direct flash light source, (Extreme low-angle POV), "
         "looking up from the {carrier}. "
         "(Captured with a grainy, bad quality spy voyeur camera), "
         "(distorted fisheye lens).")

CAM_G = ("Fixed wide-angle security camera view from a high corner of the {room}, "
         "static CCTV mount, slightly elevated downward angle, entire room in frame, "
         "no photographer present, the subject unaware of the camera.")

CAM_ART = ("Artistic portrait photograph, three-quarter rear angle, "
           "shot on medium format, subject placed slightly off-centre, "
           "shallow focus falloff into a soft interior.")

CAM_F = CAM_E  # F 和 E 共用低角机位 = 只差光线和画质层

# ══════════════════════════════════════════════════════════════════════
# 🔴 光线片段库
# ══════════════════════════════════════════════════════════════════════

LIGHT_BRIGHT = ("Bright clear daylight, harsh direct flash creating high-contrast "
                "oily shadows, sharp reflections on nearby surfaces.")

LIGHT_G_DAY = ("Soft natural daylight filtering through a small gap in the curtains, "
               "gentle interior ambient light, no harsh shadows, calm ordinary "
               "household lighting.")

LIGHT_G_NIGHT = ("Dim interior light from a single hallway lamp, weak warm spill, "
                 "heavy shadows across the room, muted color.")

LIGHT_ART = ("Soft diffused window light with a large octabox fill, gentle shadow "
             "edges, creamy highlight rolloff, natural warm skin tones.")

# ══════════════════════════════════════════════════════════════════════
# 🔴 UI 叠加片段库（监控 UI = G 风格核心）
# ══════════════════════════════════════════════════════════════════════

def _cctv_ui():
    """生成带真实时间的 CCTV UI 叠加层 = 每个时间点画面都不一样"""
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M")
    cam_id = random.choice(["A-ing", "CAM-02", "LIVING-1", "CAM-04", "HALL-01"])
    ch = random.choice(["CH-01", "CH-02", "CH-03"])
    return (f'daytime indoor CCTV footage, grainy low quality, '
            f'white digital timestamp in the top-left corner reading "{ts}", '
            f'camera ID text "{cam_id}" in the top-right corner, '
            f'overlay text "{ch}" and "REC" indicator in the bottom corner.')

# ══════════════════════════════════════════════════════════════════════
# 🔴 风格资产本体
# ══════════════════════════════════════════════════════════════════════

STYLES = {
    # ────────────────────────────────────────────────────────────────
    "e": {
        "name": "低角夜场监控绿调",
        "desc": "极度写实 + 代入感 POV 低角度仰拍 + 监控绿调 + 颗粒 + 桶形畸变。唯一 Moss 能出。",
        "camera": CAM_E,
        "quality": E_QUALITY,
        "light": None,          # 用原文的光线描写
        "ui": None,
        "bright_fix": False,    # 不动光线
        "strip_monitor": False, # 保留监控味（这是 E 的卖点）
        "needs_stand_anchor": True,
        "negative_extra": ("kneeling, kneeling pose, kneeling on escalator, crouching, squatting, "
                           "bent knees, hyper-extended knees, broken joints, twisted joints, "
                           "extra legs, extra limbs, fused fingers, mutated hands, "
                           "broken feet, deformed feet, malformed feet, "
                           "no head, cropped head, cut off head, out of frame"),
        "examples": ["1244 机场扶梯", "1245 地铁楼梯", "1248 便利店过道", "1252 洗衣房"],
    },

    # ────────────────────────────────────────────────────────────────
    "f": {
        "name": "明亮低画质",
        "desc": "光线明亮 + 0 绿调 0 扫描线 + 低画质低解析力。风格与题材无关，任意题材可套。",
        "camera": CAM_F,
        "quality": LOW_QUALITY,
        "light": LIGHT_BRIGHT,
        "ui": None,
        "bright_fix": True,      # 暗光词 → 明亮光
        "strip_monitor": True,   # 删绿调/扫描线/监控味
        "needs_stand_anchor": True,
        "negative_extra": ("kneeling, kneeling pose, crouching, squatting, "
                           "bent knees, hyper-extended knees, broken joints, twisted joints, "
                           "extra legs, extra limbs, fused fingers, mutated hands, "
                           "broken feet, deformed feet, malformed feet, "
                           "no head, cropped head, cut off head, out of frame"),
        "examples": ["1276 阶梯教室", "1272 阶梯教室(初版)"],
    },

    # ────────────────────────────────────────────────────────────────
    "g": {
        "name": "室内白天CCTV",
        "desc": "室内固定高位机位 + 白天自然光 + CCTV UI（时间戳/摄像头ID/CH-01/REC）+ 极度写实日常。",
        "camera": CAM_G,
        "quality": G_QUALITY,
        "light": LIGHT_G_DAY,
        "ui": "cctv",             # 特殊标记 = 动态生成
        "camera_replace": True,   # 🔴 核心 = 机位必须换成固定高位 CCTV（不能「有就不补」）
        "bright_fix": False,
        "strip_monitor": False,
        "needs_stand_anchor": False,   # G 是坐着/躺着，不强制站姿
        "negative_extra": ("extra legs, extra limbs, fused fingers, mutated hands, "
                           "deformed feet, malformed feet, extra fingers, "
                           "no head, cropped head, cut off head"),
        "examples": ["1275 韩国公寓客厅"],
    },

    # ────────────────────────────────────────────────────────────────
    "art": {
        "name": "写真艺术感",
        "desc": "高画质 + 浅景深 + 柔光 + 胶片调色。cos 写真/艺术向用（主人：cos 也可以是写真艺术感）。",
        "camera": CAM_ART,
        "quality": ART_QUALITY,
        "light": LIGHT_ART,
        "ui": None,
        "camera_replace": True,   # 🔴 核心 = 换成写真机位（不能「有就不补」）
        "bright_fix": False,
        "strip_monitor": True,    # 艺术感 0 监控味
        "needs_stand_anchor": False,
        "negative_extra": ("deformed, ugly, bad anatomy, bad hands, missing fingers, "
                           "extra limbs, mutated hands, extra fingers, "
                           "no head, cropped head, cut off head"),
        "examples": [],
    },
}

# ══════════════════════════════════════════════════════════════════════
# 🔴 暗光词 → 明亮光（只在 bright_fix 的风格里生效）
# ══════════════════════════════════════════════════════════════════════

DARK_WORDS = [
    ("night pohot", "bright daylight photo"),
    ("night photo", "bright daylight photo"),
    ("at night", "in bright daylight"),
    ("night", "bright daylight"),
    ("neon", "bright daylight"),
    ("emergency", "bright daylight"),
    ("dim", "bright"),
    ("dusk", "bright afternoon"),
    ("twilight", "bright afternoon"),
    ("dark", "bright"),
]

DARK_PHRASES = [
    ("Harsh, clinical fluorescent overhead lighting creating high-contrast oily shadows and sharp reflections on chrome.",
     "Bright clear daylight streaming through tall windows, harsh direct flash creating high-contrast oily shadows, sharp reflections on the lacquered desks and polished floor."),
    ("Harsh fluorescent overhead lighting", "Bright clear daylight streaming through tall windows"),
    ("harsh fluorescent overhead lighting", "bright clear daylight streaming through tall windows"),
    ("clinical fluorescent overhead lighting", "clear daylight streaming through tall windows"),
]

# 监控味词组（strip_monitor 的风格要删掉）
MONITOR_PHRASES = [
    "Authentic green-tinted security feed.",
    "Authentic green-tinted security feed",
    "interlaced scanlines",
    "heavy digital sensor noise",
    "raw amateur aesthetic",
]

# ══════════════════════════════════════════════════════════════════════
# 🔴 对外接口
# ══════════════════════════════════════════════════════════════════════


def get_style(style_id):
    """按 id 取风格资产。未知 id 返回 None（= 不套任何风格层）"""
    if not style_id:
        return None
    return STYLES.get(str(style_id).strip().lower())


# ══════════════════════════════════════════════════════════════════════
# 🔴 2D 动漫（Anima）美学体系 —— 独立于写实线（10-30 主人钦定「动漫的美感和写真风格很不一样」）
#
# 资料来源（已查证）：
#   · CircleStone Labs 官方 model card（huggingface.co/circlestone-labs/Anima）
#   · Yu1Ko/Anima-Prompt 社区 prompting reference
#   · Reddit r/StableDiffusion 实测讨论
#
# 🔴 核心差异（写实线的规则**全部不适用**）：
#   1. 标签全小写 + **空格代替下划线**（只有 score_1~9 保留下划线）
#   2. 画质前缀 = "masterpiece, best quality, score_7, safe"（Turbo 版）
#   3. 负向 = "worst quality, low quality, score_1, score_2, score_3, artist name,
#              blurry, jpeg artifacts, chromatic aberration"
#   4. 标签顺序 = [画质/元/年份/安全] [1girl] [角色] [系列] [画师] [通用标签]
#   5. 画师标签**必须带 @** = "@big chungus"（不带 = 效果极弱）
#   6. 权重要比 SDXL 高 = "(chibi:2)" 这种量级
#   7. Danbooru 与 Gelbooru 拼写冲突时**用 Gelbooru**
#   8. 混写自然语言可以，但**纯自然语言至少 2 句**（太短会出意外）
#   9. 多角色必须**每个角色绑外观描述**（只列名字 = 身份混乱）
#   10. Turbo = CFG 1 + 8-12 步；er_sde = 中性平涂锐线（默认）
#   11. 训练用了 tag dropout = **不需要穷举所有相关标签**，留高信息量的
#   12. Anima 官方说：Turbo 蒸馏 = 稳定性↑ + 默认风格强 + 多样性↓
#   13. ⚠️ 负向里**别加 score_1/2/3** 到 Aesthetic 版（会推太狠进 slop）
#       但我们跑的是 Turbo 版 + pornmaster 底模 = score_7 正向是对的
# ══════════════════════════════════════════════════════════════════════

ANIMA_POSITIVE_PREFIX = "masterpiece, best quality, score_7, "
ANIMA_NEGATIVE_BASE = ("worst quality, low quality, score_1, score_2, score_3, "
                       "artist name, blurry, jpeg artifacts, chromatic aberration")

# 画师标签（带 @ = 官方强调「不带 @ 效果极弱」）
ANIMA_ARTIST_TAGS = [
    "@askyasky", "@muryou", "@redjuice", "@nekomura1134", "@tiv", "@konami",
    "@dishwasher1910", "@torino aqua", "@mika pikazo", "@lack", "@swd3e2",
    "@kamishiro115", "@koyurin", "@ciloranko", "@mignon", "@mizuchi",
    "@sakimichan", "@rella", "@yom ", "@ilya kuvshinov", "@alphonse Mucha",
]

# 2D 线常用的风格标签（画师之外的通用风格描述）
ANIMA_STYLE_TAGS = [
    "anime screenshot", "official art", "absurdres", "highres",
    "masterpiece", "best quality", "very aesthetic", "watercolor",
    "traditional media", "film grain", "grainy", "chromatic aberration",
    "light effects", "depth of field", "rim lighting", "sunlight",
    "dappled sunlight", "partially lit", "backlighting", "hourglass",
]


def build_anima_prompt(quality="score_7", safety="explicit", artist=None,
                       year="2025", period="newest", meta=None,
                       subject="1girl", body=None, character=None,
                       series=None, artist_pool=True, extra=None,
                       natural_language=None, artist_weight=None):
    """🔴 构建 Anima（2D 动漫）提示词 = 按官方标签顺序拼

    参数：
      quality  = 画质标签串（"score_7" / "score_9" / None）
      safety   = "explicit" / "nsfw" / "sensitive" / "safe"
      artist   = 指定画师（不带 @ 自动加）/ None = 随机
      body     = 身体/服装/场景/构图等通用标签（逗号分隔）
      character= 角色名（可带外观描述）
      series   = 系列名
      natural_language = 自然语言补充段（官方说混写更好，纯自然语言至少 2 句）
    """
    parts = []

    # ① 画质 / 元 / 年份 / 安全
    q = f"masterpiece, best quality"
    if quality:
        q += f", {quality}"
    parts.append(q)
    if year:
        parts.append(f"year {year}")
    if period:
        parts.append(period)
    for m in (meta or ["absurdres", "highres"]):
        parts.append(m)
    if safety:
        parts.append(safety)

    # ② 主体数
    if subject:
        parts.append(subject)

    # ③ 角色（🔴 必须带外观描述，否则身份混乱）
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
    elif artist_pool:
        import random as _r
        a = _r.choice(ANIMA_ARTIST_TAGS)
        parts.append(a)

    # ⑥ 通用标签（外观/姿势/服装/场景/光影/构图）
    if body:
        parts.append(body)
    if extra:
        parts.append(extra)

    # 🔴 自然语言段 = 官方建议放最后（也可放开头）
    if natural_language:
        parts.append(natural_language)

    out = ", ".join(p for p in parts if p)
    return out


def build_anima_negative(base=None, extra=None):
    """Anima 负向 = 官方基线 + 画风负向（写实线的负向不适用）"""
    neg = base or ANIMA_NEGATIVE_BASE
    # ⚠️ 画风负向 = 2D 线专用（防止跑偏成 3D/写实）
    style_neg = ("3d, photorealistic, realistic, photo, photography, semi-realistic, "
                 "western cartoon, oil painting, sketch, unfinished, "
                 "bad anatomy, bad hands, extra fingers, fewer digits, "
                 "extra limbs, missing limbs, fused fingers, bad feet, "
                 "text, watermark, signature, username")
    out = neg + ", " + style_neg
    if extra:
        out += ", " + extra
    return out


# ══════════════════════════════════════════════════════════════════════
# 🔴 风格可调参数（10-30 主人钦定「风格库效果更好·可变性通用性更强」）
#
# 每个风格 = 不只一套固定提示词 = **一组可调的档位**
# 主人一句话就能把风格推到想要的强度，不用改提示词本身。
# 例：--style f --light bright_mid --quality low_hard
# ══════════════════════════════════════════════════════════════════════

LIGHT_LEVELS = {
    "bright_max":  ("Brilliant harsh midday sunlight, bleached highlights, "
                    "hard-edged shadows, high overall exposure, vivid brightness"),
    "bright":      ("Bright clear daylight, harsh direct flash creating high-contrast "
                    "oily shadows, sharp reflections on nearby surfaces."),
    "bright_mid":  ("Soft bright overcast daylight, gentle even illumination, "
                    "low contrast, pale washed-out tonal range"),
    "bright_soft": ("Diffused morning light through thin curtains, very soft shadows, "
                    "low contrast, gentle highlight rolloff, creamy pale tones"),
}

QUALITY_LEVELS = {
    "low_hard":    ("very low resolution, harsh JPEG block artifacts, severe pixelation, "
                    "choppy compression, badly degraded detail, muddied colors, "
                    "bleached washed-out colors, visible blocky noise"),
    "low":         ("low-quality amateur recording, very low resolution, soft blurry focus, "
                    "heavy JPEG compression artifacts, blocky pixelation, "
                    "washed-out pale colors, undersaturated muted tones, "
                    "visible compression noise, degraded detail, poor sharpness."),
    "low_mild":    ("slightly low resolution amateur footage, mild JPEG compression, "
                    "slight softness, light pixelation, faint noise, slightly muted colors"),
    "clean":       ("crisp full-resolution detail, tack sharp, clean digital rendering, "
                    "accurate color, no visible artifacts"),
}

# G 风格的 UI 变体
UI_VARIANTS = {
    "cctv":        "cctv",
    "cctv_zh":     "cctv_zh",
    "cctv_night":  "cctv_night",
    "none":        None,
}


def _cctv_ui_zh():
    """国内监控 UI 变体 = 中文叠加"""
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M:%S")
    cam = random.choice(["前门", "客厅", "走廊", "后院", "车库"])
    return (f'监控画面, 画质低, 左上角白色数字时间戳显示 "{ts}", '
            f'右上角摄像头名称 "{cam}", 底部叠加 "录像中" 和 "CAM-{random.randint(1,8)}" 标识。')


def _cctv_ui_night():
    """夜间监控 UI 变体 = 红外 + 更强的噪点"""
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M")
    cam = random.choice(["A-ing", "CAM-02", "HALL-01", "NIGHT-1"])
    return (f'nighttime infrared security camera footage, monochrome greenish night vision, '
            f'heavy grain, low resolution, black and white infrared image, '
            f'white digital timestamp in the top-left corner reading "{ts}", '
            f'camera ID text "{cam}" in the top-right corner, '
            f'overlay text "CH-{random.randint(1,4)}" and "REC" indicator in the bottom corner.')


def get_style(style_id, light=None, quality=None, ui=None):
    """按 id 取风格资产。未知 id 返回 None（= 不套任何风格层）

    🔴 可调参数（10-30）：light / quality / ui = 档位名 = 覆盖风格默认档
    """
    if not style_id:
        return None
    st = STYLES.get(str(style_id).strip().lower())
    if st is None:
        return None
    # 浅拷贝 = 不污染全局资产
    st = dict(st)
    if light and light in LIGHT_LEVELS:
        st["light"] = LIGHT_LEVELS[light]
    if quality and quality in QUALITY_LEVELS:
        st["quality"] = QUALITY_LEVELS[quality]
    if ui:
        if ui == "cctv_zh":
            st["ui"] = "cctv_zh"
        elif ui == "cctv_night":
            st["ui"] = "cctv_night"
        elif ui == "none":
            st["ui"] = None
    return st


def list_styles():
    """列出所有风格资产 = 给主人看「我有哪些拍法」"""
    return {k: {"name": v["name"], "desc": v["desc"], "examples": v["examples"]}
            for k, v in STYLES.items()}


def _tidy(text):
    """清理替换后残留的多余空格和连续标点"""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;])", r"\1", text)
    text = re.sub(r"([,.])\s*([,.;])", r"\1", text)
    text = re.sub(r"^\s*[.,]\s*", "", text)
    return text.strip()


def apply_style(style, prompt, slots=None):
    """把风格资产套到提示词上。返回 (新提示词, 变更说明列表)

    slots = {"room": "living room", "carrier": "metal steps"} = 机位里的占位符
    """
    if style is None:
        return prompt, []

    changes = []
    text = prompt
    slots = slots or {}

    # ① 暗光 → 明亮光（只在 bright_fix 的风格）
    if style.get("bright_fix"):
        for dark_p, bright_p in DARK_PHRASES:
            if dark_p in text:
                text = text.replace(dark_p, bright_p)
                changes.append(f"暗光句→明亮光: {dark_p[:40]}...")
        for dark, bright in DARK_WORDS:
            pat = re.compile(r"\b" + re.escape(dark) + r"\b", re.IGNORECASE)
            if pat.search(text):
                text = pat.sub(lambda m: bright, text)
                changes.append(f"暗光词→明亮: {dark} → {bright}")

    # ② 删监控味（只在 strip_monitor 的风格）
    if style.get("strip_monitor"):
        for ph in MONITOR_PHRASES:
            if ph in text:
                text = text.replace(ph, "")
                changes.append(f"删监控味: {ph[:40]}")

    # ③ 画质层 = 替换掉原描述里的画质短语，追加风格画质
    q = style.get("quality")
    if q:
        # 删掉原提示词里常见的画质短语（避免两套打架）
        for old in ("raw amateur aesthetic, heavy digital sensor noise, interlaced scanlines.",
                    "Hyper-detailed skin textures: visible pores, goosebumps, realistic skin folding.",
                    "Realistic, detailed, natural skin texture,",
                    "photorealistic."):
            if old in text:
                text = text.replace(old, "")
        # 🔴 去重 = 画质层和原文已有片段重叠时不重复追加
        _key = q.split(",")[0].strip().lower()
        if _key not in text.lower():
            text = text.rstrip() + " " + q
            changes.append(f"加画质层: {q[:50]}...")

    # ④ 光线层 = 没光线词才补
    light = style.get("light")
    if light:
        low = text.lower()
        has_light = any(w in low for w in ("light", "sun", "daylight", "sky", "bright",
                                           "golden", "lamp", "glow", "shadow"))
        if not has_light:
            text = text.rstrip() + " " + light
            changes.append("加光线层")

    # ⑤ UI 叠加层
    ui = style.get("ui")
    if ui == "cctv":
        text = text.rstrip() + " " + _cctv_ui()
        changes.append("加CCTV UI（时间戳/ID/CH/REC）")
    elif ui == "cctv_zh":
        text = text.rstrip() + " " + _cctv_ui_zh()
        changes.append("加中文CCTV UI")
    elif ui == "cctv_night":
        text = text.rstrip() + " " + _cctv_ui_night()
        changes.append("加夜间红外CCTV UI")

    # ⑥ 机位层
    # 🔴 G 风格的核心 = 把低角偷拍机位**换成**固定高位 CCTV 机位 = 必须替换，不能「有就不补」
    cam = style.get("camera")
    if cam:
        low = text.lower()
        if style.get("camera_replace"):
            # 替换掉原有的低角偷拍机位声明 + 清掉与之矛盾的碎片
            for old_cam in ("A photo taken from a rear viewpoint, phone flash photography, "
                            "strong direct flash light source,",
                            "A photo taken from a rear viewpoint, phone flash photography,"):
                if old_cam in text:
                    text = text.replace(old_cam, "")
                    changes.append("换机位: 低角偷拍 → 风格机位")
                    break
            # 🔴 清掉与新机位矛盾的 E 风格碎片（低角 POV / 从下往上 / 鱼眼偷拍设备）
            for frag in ("(Extreme low-angle POV), ", "(Extreme low-angle POV),",
                         "Extreme low-angle POV, ", "Extreme low-angle POV,",
                         "(Captured with a grainy, bad quality spy voyeur camera), ",
                         "(Captured with a grainy, bad quality spy voyeur camera),",
                         "(distorted fisheye lens). ", "(distorted fisheye lens).",
                         "(distorted fisheye lens)",
                         "phone flash photography, "):
                if frag in text:
                    text = text.replace(frag, "")
                    changes.append(f"清E风格碎片: {frag.strip()[:40]}")
            # 🔴 清掉 E 风格的载体短语整段（low-angle POV 从「looking up from the X」来）
            text = re.sub(r"looking up from (the|a|an)?\s*[^.,;]*[.,;]?", "", text)
            text = re.sub(r"\bnight pohot\b,?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\bnight photo\b,?\s*", "", text, flags=re.IGNORECASE)
            text = _tidy(text)
            for _k, _v in slots.items():
                cam = cam.replace("{" + _k + "}", _v)
            text = text.rstrip() + " " + cam
            changes.append("加风格机位层")
        else:
            has_cam = ("viewpoint" in low or "looking up from" in low
                       or "camera view" in low or "cctv" in low
                       or "fixed wide-angle" in low or "photograph" in low)
            if not has_cam:
                text = text.rstrip() + " " + cam
                changes.append("加机位层")

    text = _tidy(text)
    return text, changes


def style_negative(style, base_negative):
    """风格 = 负向词叠加（去重）"""
    if style is None:
        return base_negative
    extra = style.get("negative_extra")
    if not extra:
        return base_negative
    return base_negative + ", " + extra
