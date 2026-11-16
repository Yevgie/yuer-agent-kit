#!/usr/bin/env python3
"""身材锚自检 = 「主人报身材粗壮/太胖/腿短/肩宽胯宽」时的机械分诊工具。

为什么需要它：
    身材不对有五个可测根因，全部落在稿子上，不在底模上：
      ① 锚组缺件（社区词 / 腿比躯干长 / 92-60-92 围度 / 腰臀胸句 / 宽胯 / 大胸紧翘）
         = 体型没锁 = 底模自由发挥 = 粗壮或平板
      ② 同部位名词叠写 = 底模把该部位权重调 N 倍 = 胯宽身粗 / 大腿变粗 / 肩变宽
         🔴 槽位坑 = 部位词表按子串计数 = `her hips` 里已经包含 `her hip`
            = 锚句「her hips are wide」已占掉 hip 槽位 = 构图句再写一次 hip/hips = ×2
      ③ 稿里有腿词（thigh/knee/toe/leg）却没有腿长锚 = 底模收到"腿"的重量、收不到"腿长腿细"的限定 = 粗壮大腿
      ④ 负向词 / 十头身比 / 禁词 = 反向提示或比例拉伸
      ⑤ 肩宽类描述词在稿里 = 实测无效（底模不响应这个维度）= 写了也白写 = 反而肩相对胯更宽
         = 提示删掉（只报 WARN = 不阻断）
    所以主人的反馈是"身材" → 第一动作 = 跑这个脚本拿事实，不是先换景别、先怀疑底模。
    🔴 「肩窄/显宽」这类反馈 = 肩宽词无效 = 别再猜词 = 跑 scripts/body_wording_ab.py 同 seed 配对实测。

用法：
    python3 check_body_anchors.py /tmp/prompt_xxx.txt [更多文件...]
    python3 check_body_anchors.py --selfcheck        # 内置正/负样例自测（脚本自己也要被验一次）

退出码：0 = 无 FAIL（可带 WARN）；1 = 有 FAIL = 别出图，先按报告改稿。
注意：常态出图链路 0 跑脚本（11-12 主人钦定"把提示词写好就行"）= 本脚本是「主人报身材不对」时的分诊工具 + 手动自查工具。
跨批次体检（主人问"你有没有一直这么写"）= scripts/audit_body_batch.py。
真值 = references/铁律/02-身材特征档.md（部位词表 / 锚组 / 禁词都从那儿来 = 0 第二份正文）。
"""

import argparse
import os
import re
import sys

# ── 锚组六件套（真值 = references/铁律/02-身材特征档.md §1）──
SCALE_ANCHORS = [
    ("社区词", r"hourglass|slim yet voluptuous"),
    ("腿比躯干长", r"legs are longer than her torso"),
    ("围度数字", r"92-60-92|60-92-92|92cm|60cm|\b92 cm\b|\b60 cm\b"),
    ("腰臀胸句", r"waist is very slim|waist very slim"),
    # 🔴 宽胯锚认两条路线 = 铁律禁则「臀型词禁与 hips are wide / hourglass 叠写」
    #    = 走蜜桃翘臀路线就不写 hips are wide = 但锚组还得认得出胯宽已锁
    ("宽胯", r"hips are wide|hips wide|hips flaring out"),
    ("大胸紧翘", r"breasts are large|breasts large|sit high and firm|sitting high and firm"),
]

# 同部位叠写门 = 部位词表（真值 = 02-身材特征档 §5 的 22 个）
# 🔴 按子串计数 = `her hips` 含 `her hip` = 两者互相吃槽位 = 一个部位全稿只能出现 1 次
PART_WORDS = [
    "her waist", "her bust", "her hips", "her chest", "her thigh", "her knee",
    "her leg", "her feet", "her breast", "her hip", "her arm", "her shoulder",
    "her back", "her belly", "her buttocks", "her face", "her eyes", "her hair",
    "her hand", "her neck", "her stomach",
]

# 腿族词 = 出现即代表画面里有腿 = 必须有腿长锚
LEG_WORDS = r"\bthighs?\b|\bknees?\b|\btoes?\b|\blegs?\b|\bfeet\b|\bfoot\b|\bcalf"

# 🔴 肩锚 = 只认"窄肩/斜肩"这类收窄词 = 泛写 her shoulder 只是部位名 = 不算锚
SHOULDER_ANCHOR_RE = re.compile(
    r"(shoulders?\s+(are\s+)?(narrow|slim|sloping|delicate|soft|slender))"
    r"|((narrow|slim|sloping|delicate|soft|slender)\s+shoulders?)", re.I)

NEG_RE = re.compile(r"\b(no|not|without|never|avoid|lacking)\b", re.I)
NEG_EXEMPT_RE = re.compile(r"no\s+pubic\s+hair\s+at\s+all", re.I)   # 阴部锚唯一豁免
# 禁词 = 体积/比例类（heavy 只在紧挨身体词时算 = 0 误伤 heavy-lidded 这类非身体词）
BANNED_RES = [
    (r"wasp waist", "wasp waist"),
    (r"huge ass", "huge ass"),
    (r"bubble butt", "bubble butt"),
    (r"thick thighs?", "thick thigh(s)"),
    (r"resting low and heavy", "resting low and heavy"),
    (r"\bsagging\b", "sagging"),
    (r"\bdrooping\b", "drooping"),
    (r"\bpendulous\b", "pendulous"),
    (r"\bheavy\s+(breasts?|ass|thighs?|hips?|body|build)\b", "heavy + 身体词"),
]
HEAD_RATIO = re.compile(r"ten head-lengths|ten head lengths|10 head-lengths", re.I)
NIPPLE_WORDS = re.compile(r"\b(nipple|areola)\b", re.I)
CLOTHED = re.compile(
    r"\b(wearing|dress|top|shirt|blouse|bra|bralette|bikini|robe|kimono|gown|"
    r"blazer|hoodie|sweater|cardigan|lingerie|nightgown|slip dress)\b", re.I)
FRAMING = re.compile(
    r"(framing from[^,]*|framed[^,]*|waist-up|hip-up|head to her hips|"
    r"down to her hips|down past her knees|down to her knees)", re.I)


# 🔴 现役锚组 = 从唯一真值档【现场读】= 0 手抄副本 = 副本会漂 = 漂了 = 全库 prompt 一起 FAIL
ANCHOR_TRUTH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "references", "铁律", "references",
    "02-身材特征档-01-铁律-语儿身材参数-唯一真值.md")


def read_live_anchor():
    """读真值档里『现役锚组』那段代码块 = 自检要验的就是这一段 = 0 用手抄副本"""
    if not os.path.exists(ANCHOR_TRUTH):
        return None
    txt = open(ANCHOR_TRUTH, encoding="utf-8", errors="ignore").read()
    i = txt.find("现役锚组")
    if i < 0:
        return None
    m = re.search(r"```\n(.*?)```", txt[i:], re.S)
    return m.group(1) if m else None


def check(text, path):
    low = text.lower()
    fails, warns = [], []

    # ① 锚组缺件
    missing = [name for name, pat in SCALE_ANCHORS if not re.search(pat, low, re.I)]
    if missing:
        fails.append(f"锚组缺件：{', '.join(missing)}（体型没锁 = 底模自由发挥 = 粗壮/平板）")

    # ② 同部位叠写（子串命中 = 复数形态一并算上）
    for w in PART_WORDS:
        n = low.count(w)
        if n > 1:
            fails.append(f"同部位叠写：「{w}」×{n} = 该部位权重 ×{n} = 体积放大 = 换写法（不是删）")

    # ③ 腿词在但腿长锚缺
    has_leg = bool(re.search(LEG_WORDS, low))
    has_leg_anchor = bool(re.search(r"legs are longer than her torso", low, re.I))
    if has_leg and not has_leg_anchor:
        fails.append("稿里有腿词（thigh/knee/toe/leg）却没有腿长锚 = 底模只收到『腿』的重量 = 粗壮大腿 = 补腿长锚")
    if has_leg and not re.search(r"slender firm thighs|slim yet voluptuous|hourglass", low, re.I):
        warns.append("有腿词但没有『细腿』限定词（slender firm thighs / 社区词）= 粗壮风险")

    # ④ 负向词 / 十头身比 / 禁词
    stripped = NEG_EXEMPT_RE.sub("", text)          # 先摘掉唯一豁免句 = 不误伤
    neg_hits = sorted({m.group(0).lower() for m in NEG_RE.finditer(stripped)})
    if neg_hits:
        fails.append(f"负向词 {neg_hits} = CLIP 无否定语义 = 反向提示 = 全删改正面")
    if HEAD_RATIO.search(text):
        fails.append("十头身比 = 比例拉伸变形 = 删")
    bad = [label for rx, label in BANNED_RES if re.search(rx, low, re.I)]
    if bad:
        fails.append(f"禁词 {bad} = 粗壮/下垂/肥臀 = 删")

    # ⑤ 乳头词与穿着状态
    if NIPPLE_WORDS.search(text) and CLOTHED.search(text):
        warns.append("穿衣图出现 nipple/areola = 穿模高危 = 删（裸体才留）")

    # ⑥ 景别与身体词自相矛盾
    fm = FRAMING.search(text)
    if fm and has_leg and not has_leg_anchor:
        warns.append(f"景别句「{fm.group(0)[:40]}」与腿词冲突：裁切按『词』判 = 写了腿就得配腿长锚")

    # ⑦ 肩宽类描述词 = 实测无效（100+ 张同 seed 配对实测 = 肩宽 t<1.5）
    #    = 写了也白写 = 反而肩相对胯更宽（t 最高 +8.1）= 提示 = 删 = 精简身材段
    if SHOULDER_ANCHOR_RE.search(text):
        warns.append("稿里有肩宽类描述词（narrow/sloping/比胸窄/比头窄…）= 实测对肩宽无效 = "
                     "删 = 每多一句身体描述肩相对胯更宽 = 见 references/身材描述实测表.md")

    status = "FAIL" if fails else ("WARN" if warns else "OK  ")
    print(f"\n=== {path} — {status} ===")
    print(f"  {len(text)} 字符 | 锚组 {len(SCALE_ANCHORS)-len(missing)}/{len(SCALE_ANCHORS)} "
          f"| 负向词 {len(neg_hits)}")
    for f in fails:
        print(f"  [FAIL] {f}")
    for w in warns:
        print(f"  [WARN] {w}")
    if not fails and not warns:
        print("  → 身材段齐了（社区词 + 腿长锚 + 围度 + 腰臀胸句 + 宽胯 + 大胸紧翘 + 无叠写 + 0 肩宽废话）")
    return 1 if fails else 0


SELF_GOOD = (
    "a 20 years old young Asian woman with long black hair spread loose across a white pillow, "
    "slim yet voluptuous hourglass figure, 92-60-92, her legs are longer than her torso, "
    "slender firm thighs, her waist very slim, her hips are wide, "
    "her breasts are large sitting high and firm, pale skin, "
    "her pubic mound is innie pussy, smooth and bare with no pubic hair at all, "
    "the inner labia small and pink and tightly closed into a neat vertical seam"
)

SELF_BAD = (
    "a 20 years old young Asian woman lying on her side on a wide bed, "
    "her left leg drawn up and her right knee pushed forward so the sheets fall open between her thighs, "
    "her bare belly and navel fully exposed, her waist very slim and narrow, her hips are wide, her breasts are large (92cm), "
    "her waist is very slim, the silk bunched at her waist, across her open thighs, her open thighs, "
    "her pubic mound is innie pussy, smooth and bare with no pubic hair at all"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args()

    if args.selfcheck:
        rc_good = check(SELF_GOOD, "<内置正样例>")
        rc_bad = check(SELF_BAD, "<内置负样例：缺腿长锚 + 同部位叠写>")
        live = read_live_anchor()
        rc_live = None
        if live is None:
            print("  [selfcheck] 真值档里的『现役锚组』没读到 = 跳过这项（档路径变了？）")
        else:
            rc_live = check(live, "<真值档·现役锚组现场读>")
        ok = (rc_good == 0 and rc_bad == 1 and rc_live in (0, None))
        print(f"\n自测：正样例 rc={rc_good}（应 0）"
              f"| 负样例 rc={rc_bad}（应 1）| 现役锚组 rc={rc_live}（应 0）"
              f"=> {'通过' if ok else '失败'}")
        return 0 if ok else 1

    if not args.files:
        print(__doc__)
        return 2
    rc = 0
    for f in args.files:
        if not os.path.exists(f):
            print(f"\n=== {f} — 找不到文件")
            rc = 1
            continue
        rc |= check(open(f, encoding="utf-8", errors="ignore").read(), f)
    return rc


if __name__ == "__main__":
    sys.exit(main())
