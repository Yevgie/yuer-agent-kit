# -*- coding: utf-8 -*-
"""批量出图 = 一个 build 脚本生成 N 份 prompt + 一次性落盘 + 一次性跑。

用法：
    /usr/bin/python3 build_batch.py <batch_id>     # 写 prompt 文件 + 归档
    然后串行跑 yuer_ka_fast.sh（或后台跑一批）

🔴 三条硬规则（都来自实战撞车）：
1. **生成名 = 跑名必须同一份** = build 脚本里 emit() 写的文件名 = 跑循环里读的文件名
   = 靠同一个 job 的 name 字段串起来 = 0 手抄两遍路径。
   实战踩过：生成时叫 prompt_b4_n1.txt、循环里去读 prompt_b4_1.txt = 全批 FileNotFound = 白跑一轮。
2. **先全部过门禁再开跑** = 逐张跑 check_prompt_subject.py + check_outfit_lock.py
   = 边出边查 = 中途 FAIL = 已花掉的出图开销作废。
3. **批量收尾必附每张的胸区异常率表** = 见 references/铁律/02-身材特征档.md v2.4 脚本。
4. **ast.parse 只验语法，不验内容** = 多行 replace 常把后半句吃掉（逗号位置错 = 尾段整段丢失）
   = 语法照样通过 = 门禁照样过 = 图却少了动作/光线段。**机械门 = 落盘后逐份核对字符数落在带内
   （600~3200）+ grep 一句关键短语确认在** = 0 凭「我写了」的印象往下走。
"""
import os
import shutil
import sys

# 🔴 身体段真值 = 落盘的 CURRENT 文件（带版本号的旧名 = 历史快照 = 会漂 = 0 直接用）
SECRET = "/path/to/media"
COVER = open(os.path.join(SECRET, "2026-10-28_bodyblock_covered_CURRENT.txt"), encoding="utf-8").read().strip()
NUDE = open(os.path.join(SECRET, "2026-10-28_bodyblock_nude_CURRENT.txt"), encoding="utf-8").read().strip()

# 🔴 裸体那张专用 = 完整 CURRENT 裸体段 ≈1500 字符 → 加场景/光线就 4100+ = 超 3200 天花板。
#    解法 = 精简版（保体型轮廓/胸型/腰臀比/腿比/皮肤锚，删私处三锚/围度数字/重复皮肤）。
NUDE_SHORT = ("a tall slender build with elongated vertical proportions, slim yet voluptuous body, "
              "hourglass figure, her legs longer than her torso reaching up to her chest, smooth long "
              "legs with slender firm thighs, a tiny sharply defined waistline that flares out to the hip, "
              "wide hips, a high tight peach shaped bottom, two round buttocks that curve out in a smooth "
              "peach-like swell, large full breasts held up in a lifted rounded shape, a deep natural "
              "cleavage, pale porcelain skin, luminous ivory skin, smooth soft skin texture, "
              "natural skin pores visible")

# 🔴 五风格档 = 相机前缀 + 调色尾参成对取 = 每张各占一档
#    （见 references/无限勾引批次-时空题材池与五风格档.md）
STYLE = {
    "ins": ("A bright casual lifestyle snapshot taken on an iPhone 15 Pro Max 1x lens at f/1.8, ",
            "a bright airy cheerful colour grade, natural skin tones, sharp focus on her eyes, "
            "photorealistic photography, natural light, no harsh shadows"),
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


def head(style, hair, scene):
    """机位 + 身份锚 + 发型 + 场景。6 句一组、句句接着说 = 0 分段。"""
    return (STYLE[style][0] + "a 20 years old young Asian woman with " + hair + ", " + scene)


def emit(batch, jobs, body=COVER):
    """jobs = [(name, style_key, head段, 服装段, 情绪动作段, 光线段, 背景道具段[, body]), ...]

    服装段必须含：下装词（门禁白名单内）+ 内层 + 鞋履 + 妆容。
    情绪动作段 = 露出动作（走光 > 主动脱光）。

    🔴 元组长度必须自适应 = 固定拆包 = 批次里混用不同长度就整批崩。
    机制 = 一批 5 张里有的行少写了「背景道具段」= 固定解包直接抛错
    = 整批一个 prompt 都没落盘 = 白跑一轮。
    正解 = emit() 按实际长度拼（tail 用切片拼），0 在数据里凑长度。

    🔴 末项 = 这一张专用 body（裸体那张传 NUDE_SHORT）= 0 把全批 body 换成精简版。
    🔴 民族服装必在同句挂白名单下装词（qipao dress / the long skirt falling to her ankles /
       over black string bikini bottoms）= qipao / ruqun / hakama / towel 全不在白名单 = 必 FAIL。
    """
    for job in jobs:
        name = job[0]
        style = job[1]
        head = job[2]
        costume = job[3]
        mood = job[4]
        # 🔴 末项到底是 body 还是尾参句 = 按内容判定，不按元组长度判定
        #    长度判定（len(job) > 7）曾让 7 元素裸体 job 的 NUDE_SHORT 当成尾参句拼到句尾
        #    = prompt 尾部混入一整段裸体身体描述 = 构图/动作段被挤掉 = 门禁照样过 = 图却废了。
        last = job[-1]
        is_body = isinstance(last, str) and ("hourglass" in last or "slender build" in last)
        if is_body:
            tail = " ".join(job[5:-1])
            this_body = last
        else:
            tail = " ".join(job[5:])
            this_body = body
        s = (head + this_body + ", " + costume + mood + tail
             + ", " + STYLE[style][1] + ", 9:16 vertical composition")
        path = "/tmp/prompt_%s_%s.txt" % (batch, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(s)
        shutil.copy2(path, os.path.join(SECRET, "2026-10-28_%s_%s.prompt.txt" % (batch, name)))
        # 🔴 字符数落在带外 = 多半是 replace 吃掉了半句（语法仍合法）= 当场报，别等门禁才发现
        if not (600 <= len(s) <= 3200):
            print("⚠️ %s %s 字符数异常 = %d（内容可能被截断，查 prompt 尾段）" % (batch, name, len(s)))
        print("%s %s [%s] %d" % (batch, name, style, len(s)))
    return ["/tmp/prompt_%s_%s.txt" % (batch, j[0]) for j in jobs]


# ===== 模板示例：一批 5 张 = 5 个风格档各占一档 =====
BATCH = [
    ("n1", "ins",
     head("ins", "loose falling over one shoulder",
          "standing outside a convenience store on a wet city street at night, "
          "full body framing her entire body from the crown of her head to the soles of both feet "
          "contained inside the frame, turned in full side profile facing left, "),
     "a loose white long sleeve shirt worn open over a plain black bralette with no other layer under it, "
     "a very short denim skirt, bare legs, white canvas low-top sneakers, "
     "light waterproof mascara and a soft coral tint on her lips, ",
     "the hem of the shirt blown by the wind and she looks at the lens with a small closed mouth smile, ",
     "the cold white light of the convenience store sign spilling onto the wet pavement, ",
     "rain streaks in the air, the glowing shop sign behind her, a puddle reflecting the sign, "),
    # ... 其余 4 张同理：每张换【时空 / 服装 / 姿态 / 机位 / 唯一亮部】+ style 各占一档
]

if __name__ == "__main__":
    batch = sys.argv[1]
    files = emit(batch, BATCH)
    print("\n".join(files))

# ===== 🔴 每张的六维设计（设计层，不是机械填表）=====
# 环境场景 / 服装 / 动作 / 表情 / 机位 / 景别 = 六行全部从同一个「主角光源」长出来。
# 一批 5 张 = 六维至少换 4 维 = 只换场景名词而其余照抄 = 同一个壳子换标签 = 批次退化。
# 一批至少覆盖 3 种景别；远景纯侧身必留一格（已知易发区 = 主动压住不是绕开）。
# 完整速查表 + 主角光源×场景速配表 = references/六维场景设计.md
#
# 六维速记：
#   环境 = 时段 + 天气 + 唯一最亮的东西 + 硬边光块落点 + 光里飘什么
#   服装 = 材质 + 穿着方式 + 一个透光/反光材质 + 为什么这身衣服出现在这个场景
#   动作 = 一个动作一句 + then 串时间顺序 + 自然产生露出
#   表情 = 物理化 ≥3 项 + 视线落点
#   机位 = 相机高度 + 距离 + 焦段 + 主体在画面哪 + 留白在哪一边
#   景别 = 这张的焦点是哪一块身体
