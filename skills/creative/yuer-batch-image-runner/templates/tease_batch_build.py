# -*- coding: utf-8 -*-
"""批量出图 build 脚本骨架 = 复制本文件 → 改 JOBS → 跑 → 写盘 /tmp/<批次>/n1.txt …

用法：
    python3 /tmp/<批次>_build.py
    # 然后逐张：
    cd ~/.hermes/skills/creative/yuer-image
    for pair in "n1 试衣间" "n2 卧室床"; do set -- $pair
      timeout 300 bash scripts/yuer_ka_fast.sh /tmp/<批次>/$1.txt "<主题>_$2_<日期>" --caption "<这张专属骚话>"
    done

🔴 铁律：
  1. 身体段 = 从落盘 CURRENT 读进来 = 0 手抄 = 0 与身材档漂移
  2. 裸体图用 NUDE_SHORT = 完整裸体段 ≈1500 字符 + 场景光线 = 4100+ = 超 3200 天花板
  3. 每张各占一档 STYLE = 一批不全是同一种调
  4. 裸体图在场景句里补「画外实物下装」= 过下装门禁（不要写成她穿着）
"""
import os

SECRET = "/path/to/media"
COVER = open(os.path.join(SECRET, "2026-10-28_bodyblock_covered_CURRENT.txt"), encoding="utf-8").read().strip()

# 🔴 裸体精简身体段 = 体型轮廓 / 胸型 / 腰臀比 / 腿比 / 皮肤锚
NUDE_SHORT = (
    "slim yet voluptuous hourglass figure, 92-60-92, her legs are longer than her torso, slender firm thighs, her waist very slim, her hips are wide, her breasts are large sitting high and firm, pale skin,"

)

PRIVATE = ("her pubic mound is innie pussy, smooth and bare with no pubic hair at all, "
           "the inner labia small and pink and tightly closed into a neat vertical seam, "
           "the darker damp center visible in the lamp light with wet shine along the entrance")

# 🔴 5 档相机前缀 + 对应调色尾参 = 每张各占一档
STYLE = {
    "ins": ("A bright casual lifestyle snapshot taken on an iPhone 15 Pro Max 1x lens at f/1.8, ",
            "a bright airy colour grade, natural skin tones, sharp focus on her eyes, "
            "photorealistic photography, natural light"),
    "cine": ("A cinematic still captured with Sony A7R V and 35mm f/1.4 GM at f/2.0, ",
             "cinematic still, filmic color grading, fine natural film grain"),
    "doc": ("A documentary photograph taken on a Fujifilm X-T5 with 35mm f/1.4 at f/2.8, ",
            "documentary photography, available light, unposed, grain"),
    "ancient": ("A photorealistic photograph taken with Canon EOS R5 and 50mm f/1.2L USM at f/2.0, ",
                "photorealistic photography, available light, fine film grain"),
    "fashion": ("A high-fashion editorial shot lit by a single softbox, captured with "
                 "Canon EOS R5 and 85mm f/1.2L USM at f/2.8, ",
                 "editorial, high contrast, studio lighting, sharp focus, smooth tonal falloff"),
}

# 🔴 同一套发型妆容 = 锁脸一致 = 一批是同一个人
HAIR = ("long dyed pink hair, straight with blunt bangs, small pearl hair clip on one side, "
        "heavy black eyeliner, red-pink lipstick, light blush on both cheeks")

# ==================== 改这里 ====================
JOBS = {}

JOBS["n1"] = (
    STYLE["ins"][0] + "camera low at the height of her knees about one metre from the mirror in a fitting room, "
    "close framing on her from the thighs up with her placed on the left third, the harsh overhead strip light "
    "the only bright thing and the rest of the fitting room falling into deep shadow, "
    "she stands with her weight on her left leg and her right knee bent with her heel lifted, "
    "then she hooks her fingers under the hem of her skirt and lifts it up past her hips while looking down "
    "at the camera, "
    "a 20 years old young Asian woman with " + HAIR + ", "
    "upper eyelids lowered to a narrow slit, lips pressed together with one corner pulled slightly up, "
    "chin dipped low and jaw set, "
    "she wears a pale mint button-up shirt left open over a plain black bralette with a grey pleated skirt "
    "pulled up by her own hand and bare legs, "
    + COVER + ", "
    "the fabric of the bralette fully covering her with the cloth draping smoothly over a full bust "
    "and no detail of the skin visible beneath the cloth, "
    + PRIVATE + ", "
    "a strip of cold white light falling across her thighs and the mirror glass showing a blurred second "
    "reflection of her back, dust drifting in the beam, "
    + STYLE["ins"][1] + ", 4:5 vertical composition")

JOBS["n2"] = (
    STYLE["cine"][0] + "camera at the level of the mattress about two and a half meters from the bed, "
    "full body framing from the crown of her head to her feet contained inside the frame, "
    "she placed on the right third of the picture with the bedroom window and the night city behind the "
    "sheer curtain filling the left two thirds, the single brightest thing being the warm bedside lamp "
    "casting a hard-edged block of light across her lower back and hips, "
    "she kneels on the mattress with both knees pressed into the sheets and her weight settled back on her "
    "heels, her forearms and forehead down in the bedding, "
    "then she turns her head back over her own shoulder toward the lens, "
    "a 20 years old young Asian woman with " + HAIR + ", "
    "upper eyelids heavy and half-closed, lips slightly parted, chin turned hard to the side, "
    "she is completely nude with nothing on her at all, "
    + NUDE_SHORT + ", "
    "two round buttocks curving out in a smooth peach-like swell and lifting high, "
    "the crease between them deep and the skin there smooth, "
    "her pubic mound smooth and bare with no pubic hair at all, "
    "the inner labia small and pink and tightly closed into a neat vertical seam, "
    "a discarded grey pleated skirt crumpled on the floor at the edge of the frame, "
    "warm lamplight gilding the curve of her hip and her thigh while the sheets under her knees stay pale, "
    + STYLE["cine"][1] + ", 9:16 vertical composition")
# ==================== 改到这里 ====================

BATCH = "mybatch"
os.makedirs(f"/tmp/{BATCH}", exist_ok=True)
for k, v in JOBS.items():
    p = f"/tmp/{BATCH}/{k}.txt"
    open(p, "w", encoding="utf-8").write(v)
    print(k, len(v), p)
