#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""机位 × 景别 × 焦段 = 正规摄影分类引擎

🔴 11-01 主人钦定分类法（原文）：
   「机位是高机位俯视，平视，仰视，低机位虫眼视角，监控俯视等等，
     景别是超广角全景，远景，50mm 全身照，半身照，120mm 特写，微距特写等等」

🔴 我上一版自造了 26 种「摄影师处境」= 野路子 = 不是摄影分类 = 已废弃。
   正解 = 机位五档 × 景别六档 × 焦段 = 正规分类 + **组合可行性校验**。

🔴 机位五档（由高到低）：
   high_above   高机位俯视 = 站在高处往下拍 = 权力俯视
   eye_level    平视       = 与被摄者等高 = 平等/记录
   low_angle    仰视       = 相机低于主体 = 仰慕/强势
   worm_eye     低机位虫眼 = 贴地极低仰拍 = 戏剧夸张 / 腿被拉长
   surveillance 监控俯视   = 天花板固定机位 = 无人视角 / 证据感

🔴 景别六档（焦段绑定 = 焦段必须跟景别一起走 = 写错就物理不成立）：
   ultra_wide_full  超广角全景 = 12-16mm + 极近 = 环境吞掉人
   wide_full        远景       = 24-35mm + 远     = 人在环境里
   full_50          50mm 全身照 = 50mm + 中距离   = 标准全身
   half_body        半身照     = 85mm + 1.5-2m     = 齐胯
   portrait_120     120mm 特写 = 120mm + 2.5-3m   = 胸部以上，背景压缩
   macro_close      微距特写   = 100mm 微距 + 极近 = 皮肤/眼睛/局部
"""
import re

# ═══════════════════════════════════════════════════════════════
# 机位五档
# ═══════════════════════════════════════════════════════════════
CAMERA_HEIGHT = {
    "high_above": dict(
        cn="高机位俯视",
        en="high above her looking steeply down",
        physics="the photographer is standing on a ledge well above her and points the camera down",
        effect="her whole body is seen from above and she looks small and pinned to the ground",
        lighting="the light falls on the top of her shoulders and her hair, and her shadow falls "
                 "away from the camera",
    ),
    "eye_level": dict(
        cn="平视",
        en="at her own eye level",
        physics="the photographer is standing the same height as her and the camera is level",
        effect="she fills the frame with no distortion and the picture is at her own height",
        lighting="the light falls across her at a natural angle and the shadow falls behind her",
    ),
    "low_angle": dict(
        cn="仰视",
        en="below her looking up at her",
        physics="the camera is held lower than her and angled up at her face",
        effect="she towers above the camera and her legs converge upward",
        lighting="the light comes from above and behind her so her jaw and the front of her body "
                 "fall into shadow",
    ),
    "worm_eye": dict(
        cn="低机位虫眼",
        en="almost on the floor looking up at her from her feet",
        physics="the photographer is lying flat on the ground with the lens a few centimetres off "
                "the floor",
        effect="her legs are enormously foreshortened and stretched toward the camera and the "
               "ceiling opens up behind her",
        lighting="the light comes from high above so the underside of her body is dark and the "
                 "space above her is bright",
    ),
    "surveillance": dict(
        cn="监控俯视",
        en="from a ceiling mounted camera looking straight down",
        physics="a fixed camera is bolted to the ceiling and cannot be moved or angled",
        effect="the entire floor is visible around her with no perspective correction and she is "
               "a shape seen from directly overhead",
        lighting="the light is completely even with no shadows anywhere under her",
    ),
}

# ═══════════════════════════════════════════════════════════════
# 景别六档（焦段绑定）
# ═══════════════════════════════════════════════════════════════
FRAMING = {
    "ultra_wide_full": dict(
        cn="超广角全景",
        en="an ultra wide full body shot",
        lens="an ultra wide lens at 14mm",
        distance="the camera is almost against her, about half a metre away",
        crop="her entire body is inside the frame but she is dwarfed by the space around her and "
             "the edges of the room bend outward",
        effect="the environment swallows her and the wide angle stretches the space out sideways",
    ),
    "wide_full": dict(
        cn="远景",
        en="a wide full shot",
        lens="a wide lens at 28mm",
        distance="the camera is far back, about eight metres away",
        crop="her whole body is a small figure inside a large amount of the scene",
        effect="she is a person inside a place rather than the subject of a portrait",
    ),
    "full_50": dict(
        cn="50mm 全身照",
        en="a full body shot",
        lens="a normal lens at 50mm",
        distance="the camera is about four metres away at waist height",
        crop="her entire body from the crown of her head to the soles of both feet fits inside the "
             "frame with a little room above her head",
        effect="no distortion and the classic standing figure",
    ),
    "half_body": dict(
        cn="半身照",
        en="a half body shot",
        lens="a short telephoto at 85mm",
        distance="the camera is about two metres away",
        crop="the frame runs from the crown of her head down to her hips",
        effect="the background is gently compressed behind her and her waist and chest dominate",
    ),
    "portrait_120": dict(
        cn="120mm 特写",
        en="a tight portrait",
        lens="a telephoto at 120mm",
        distance="the camera is about three metres away",
        crop="the frame runs from her chest up to just above her head",
        effect="the background is flattened into a soft wall and her face and collarbones carry "
               "the whole picture",
    ),
    "macro_close": dict(
        cn="微距特写",
        en="an extreme macro close up",
        lens="a 100mm macro lens at its closest focus",
        distance="the camera is a few centimetres from her",
        crop="only a small part of her fills the frame, the skin and the eye and the sheen of it",
        effect="every pore and every fine hair is resolved and the whole world is that one patch "
               "of her",
    ),
}

# ═══════════════════════════════════════════════════════════════
# 组合可行性 = 机位 × 景别 × 焦段 必须物理成立
# ═══════════════════════════════════════════════════════════════

# 焦段 ↔ 距离 ↔ 景别的合法配对区间（相对距离倍数）
DISTANCE_SCALE = {
    "ultra_wide_full": 0.15,     # 0.5m
    "wide_full": 1.0,            # 8m
    "full_50": 0.5,              # 4m
    "half_body": 0.25,           # 2m
    "portrait_120": 0.375,       # 3m
    "macro_close": 0.02,         # 0.16m
}

# 🔴 机位自带镜头能力 = 监控是固定超广角 = 拍不出特写 = 但能拍到"俯视远景"
#    = 0 用「禁止」硬砍 = 0 换成「这台机器只能这样拍」的写法
CAMERA_LENS_CONSTRAINT = {
    "surveillance": "shot through a fixed ultra wide bullet camera with no zoom at all",
    "worm_eye": "shot with the lens almost touching the floor",
    "high_above": "shot from a great height with a wide lens so nothing is cropped",
}

# 机位 ↔ 景别 = 有些搭配必然不合理（例：监控俯视 + 微距特写 = 监控机位没那个能力）
IMPOSSIBLE = {
    ("surveillance", "macro_close"): "监控是固定广角 = 不可能做微距特写",
    ("surveillance", "portrait_120"): "监控是固定广角 = 不可能有 120mm 长焦",
    ("surveillance", "half_body"): "监控俯视 = 画面里她是俯视全身 = 不存在半身",
    ("surveillance", "ultra_wide_full"): "监控本身就是超广角俯视 = 两层广角 = 变形失真",
    ("worm_eye", "macro_close"): "贴地虫眼与微距同轴 = 底模只会画成畸变怪物",
    ("worm_eye", "portrait_120"): "虫眼与 120mm 焦段互斥 = 长焦会拉平透视",
    ("worm_eye", "wide_full"): "虫眼贴地与远景互斥 = 贴地就退不开",
    ("high_above", "macro_close"): "高机位俯视与微距互斥 = 俯拍角度拍不到 100mm 微距",
    ("high_above", "portrait_120"): "高机位俯视 + 120mm = 变成鸟瞰压缩 = 不成肖像",
    ("low_angle", "macro_close"): "仰拍与微距同轴 = 变形到无法辨认",
}


def build_camera(height_key, framing_key, full=True):
    """机位 + 景别 = 一段完整的摄影说明（焦段 + 距离 + 裁法 + 物理理由 + 效果）

    🔴 full=False（11-01 主人钦定资源梳理时发现）= **精简模式**
    完整模式的 crop + effect + physics + lighting 四段常常 300-450 字符
    = 挤爆 3200 字符上限 = 逼我删掉真正重要的内容。
    **精简 = 只留 机位 + 景别 + 焦段 + 距离 + 物理理由**（物理理由不能删 = 它是机位合法性的来源）
    = 其余（裁法/效果/通用光线句）由我在 prompt 里按画面自己写 = 更准 + 更省字符。
    """
    h = CAMERA_HEIGHT[height_key]
    f = FRAMING[framing_key]
    if not full:
        return ("The camera is %s, %s, %s, %s. %s"
                % (h["en"], f["en"], f["lens"], f["distance"], h["physics"]))
    return (
        "The camera is %s, %s, %s, %s. %s %s %s %s"
        % (
            h["en"],
            f["en"],
            f["lens"],
            f["distance"],
            f["crop"],
            f["effect"],
            h["physics"],
            h["lighting"],
        )
    )


def check(height_key, framing_key):
    """机械校验 = 这个机位 + 这个景别 + 这支镜头物理上成不成立"""
    problems = []
    if (height_key, framing_key) in IMPOSSIBLE:
        problems.append(IMPOSSIBLE[(height_key, framing_key)])
    h = CAMERA_HEIGHT[height_key]
    f = FRAMING[framing_key]
    # 距离 vs 机位 = 高机位俯视需要高度差 = 微距/特写在高位拍会变成鸟瞰
    if height_key == "high_above" and framing_key in ("macro_close", "portrait_120"):
        problems.append("高机位俯视 + 近景 = 变成俯拍局部 = 不成脸")
    if height_key == "worm_eye" and framing_key in ("full_50", "half_body"):
        problems.append("虫眼贴地 + 中远景 = 透视变形会破坏身体比例")
    if height_key == "low_angle" and framing_key == "wide_full":
        problems.append("仰拍 + 远景 = 主体在画面里太小 = 看不清")
    return problems


def header(height_key):
    """prompt 开头的一句 = 机位"""
    return "The photograph is shot %s" % CAMERA_HEIGHT[height_key]["en"]


if __name__ == "__main__":
    print("机位 %d 档 / 景别 %d 档 / 禁止组合 %d 对"
          % (len(CAMERA_HEIGHT), len(FRAMING), len(IMPOSSIBLE)))
    print("\n=== 机位 ===")
    for k, v in CAMERA_HEIGHT.items():
        print("  %-14s %s" % (k, v["cn"]))
    print("\n=== 景别 ===")
    for k, v in FRAMING.items():
        print("  %-18s %s  [%s]" % (k, v["cn"], v["lens"]))
    print("\n=== 合法组合示例 ===")
    for hk in CAMERA_HEIGHT:
        row = []
        for fk in FRAMING:
            p = check(hk, fk)
            row.append("OK " if not p else "X  ")
        print("  %-14s %s" % (hk, " ".join(row)))
    print("  景别:", " ".join("%-2s" % k[:2] for k in FRAMING))
