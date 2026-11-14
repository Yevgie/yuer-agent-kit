#!/usr/bin/env python3
"""身材锚自检 = 「主人报身材粗壮/太胖/腿短」时的机械分诊工具。

为什么需要它：
    身材不对有四个可测根因，全部落在稿子上，不在底模上：
      ① 锚组缺件（社区词 / 腿比躯干长 / 92-60-92 围度 / 腰臀胸句）= 体型没锁 = 底模自由发挥 = 粗壮或平板
      ② 同部位名词叠写 = 底模把该部位权重调 N 倍 = 胯宽身粗 / 大腿变粗
      ③ 稿里有腿词（thigh/knee/toe/leg）却没有腿长锚 = 底模收到"腿"的重量、收不到"腿长腿细"的限定 = 粗壮大腿
      ④ 负向词 / 十头身比 / 禁词 = 反向提示或比例拉伸
    所以主人的反馈是"身材" → 第一动作 = 跑这个脚本拿事实，不是先换景别、先怀疑底模。

用法：
    python3 check_body_anchors.py /tmp/prompt_xxx.txt [更多文件...]
    python3 check_body_anchors.py --selfcheck        # 内置正/负样例自测（脚本自己也要被验一次）

退出码：0 = 无 FAIL（可带 WARN）；1 = 有 FAIL = 别出图，先按报告改稿。
注意：常态出图链路 0 跑脚本（11-12 主人钦定"把提示词写好就行"）= 本脚本是「主人报身材不对」时的分诊工具 + 手动自查工具。
真值 = references/铁律/02-身材特征档.md（部位词表 / 锚组 / 禁词都从那儿来 = 0 第二份正文）。
"""

import argparse
import os
import re
import sys

# ── 锚组四件套（真值 = references/铁律/02-身材特征档.md）──
SCALE_ANCHORS = [
    ("社区词", r"hourglass|slim yet voluptuous"),
    ("腿比躯干长", r"legs are longer than her torso"),
    ("围度数字", r"92-60-92|60-92-92|92cm|60cm|\b92 cm\b|\b60 cm\b"),
    ("腰臀胸句", r"waist is very slim|waist very slim"),
    ("宽胯", r"hips are wide|hips wide"),
    ("大胸紧翘", r"breasts are large|breasts large|sit high and firm|sitting high and firm"),
]

# 同部位叠写门 = 部位词表（真值 = 02-身材特征档 §5 的 21 个）
PART_WORDS = [
    "her waist", "her bust", "her hips", "her chest", "her thigh", "her knee",
    "her leg", "her feet", "her breast", "her hip", "her arm", "her shoulder",
    "her back", "her belly", "her buttocks", "her face", "her eyes", "her hair",
    "her hand", "her neck", "her stomach",
]

# 腿族词 = 出现即代表画面里有腿 = 必须有腿长锚
LEG_WORDS = r"\bthighs?\b|\bknees?\b|\btoes?\b|\blegs?\b|\bfeet\b|\bfoot\b|\bcalf"

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

    status = "FAIL" if fails else ("WARN" if warns else "OK  ")
    print(f"\n=== {path} — {status} ===")
    print(f"  {len(text)} 字符 | 锚组 {len(SCALE_ANCHORS)-len(missing)}/{len(SCALE_ANCHORS)} "
          f"| 负向词 {len(neg_hits)}")
    for f in fails:
        print(f"  [FAIL] {f}")
    for w in warns:
        print(f"  [WARN] {w}")
    if not fails and not warns:
        print("  → 身材段齐了（社区词 + 腿长锚 + 围度 + 腰臀胸句 + 无叠写）")
    return 1 if fails else 0


SELF_GOOD = (
    "a 20 years old young Asian woman with long black hair spread loose across a white pillow, "
    "a tall slender build with elongated vertical proportions, slim yet voluptuous body, hourglass figure, "
    "92-60-92 figure, her legs are longer than her torso reaching up to her chest, smooth long legs with slender firm thighs, "
    "her waist is very slim and narrow, her hips are wide, her breasts are large (92cm) sitting high and firm with a lifted tight curve, "
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
        ok = (rc_good == 0 and rc_bad == 1)
        print(f"\n自测：正样例 rc={rc_good}（应 0）| 负样例 rc={rc_bad}（应 1）=> {'通过' if ok else '失败'}")
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
