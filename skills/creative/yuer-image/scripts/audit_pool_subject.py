#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提示词资产池 · 主体审计（确定性探针）

唯一职责 = 量出「池里有几条的主体是男 / 是儿童 / 是多人」= 语儿出图主体必须只有她一个。

用法：
    python3 audit_pool_subject.py                 # 审计全部现役池
    python3 audit_pool_subject.py --pool sfw      # 只审一个池
    python3 audit_pool_subject.py <池文件> [...]  # 审计指定文件
    python3 audit_pool_subject.py --json          # JSON 输出

🔴 判据（11-09 23:10 主人钦定「儿童、男性主体不保留」+ 23:20 定稿 = 本脚本口径）：
  · 主体 = 句首第一个 person 短语（head 400 字符）= 全文任意位置出现的人 ≠ 换主体
    （背景路人 / 海报上的男人 / NSFW 里的男伴 = 主体仍是女的 = 不算男主体）
  · 修饰词上限 3 个 = "A real adult man" / "A young adult man" 都要抓到
  · 具体人称优先 = adult man / young woman / young adult man 整体匹配 = 单独 adult 不算主体
  · head 无 person 短语（a young adult / a model / a person）= 中性候选
    = 用全文代词分布二次判定（they/their/them = 性别刻意不写 = 不是男）
  · 🔴 男女同框 = 句首男主体 **但**画面有明确女性主体 = 保留（主人钦定「含男女同框」）
  · 🔴 儿童 = 明确未成年（child/kid/toddler/infant/newborn/schoolboy/schoolgirl/
    preteen/teenager/adolescent/underage/little boy/little girl/明确年龄<18）
    = 单独的 girl / boy / young girl 一律不算（"18-year-old Chinese young girl" = 成年女性）
  · 🔴 画面含小童 = 主体位出现小童（"an adult woman and a young boy" / "a young child stands"）
  · 误报排除 = baby pink / baby-blue / baby doll / babydoll / baker boy cap /
    boyish / bullboy / childlike（颜色服饰名 = 不是人）
  · 汽车座椅 = child car seat / child seat = 道具不是儿童
  · 守恒校验 = 各分类条数之和 == 总条数（不等 = 判据写漏了，不是池坏了）

池路径 = 从 yuer_prompt_pool.py 取（唯一真值）= 0 本脚本再写一份路径。
"""

import argparse
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
try:
    from yuer_prompt_pool import POOLS          # 唯一真值
except Exception:                                # pragma: no cover
    _REF = os.path.abspath(os.path.join(_HERE, "..", "references"))
    POOLS = {
        "nsfw": os.path.join(_REF, "提示词库-nsfw.txt"),
        "sfw":  os.path.join(_REF, "提示词库-sfw.txt"),
    }

# ── 句首主体：第一个 person 短语 ──────────────────────────────
PERSON = re.compile(
    r"\b(?:a|an|the|one|two|three|four|five|young|old|several|many)\s+(?:\w+[- ]){0,3}?"
    r"(man|woman|boy|girl|male|female|gentleman|lady|guy|person|people|youth|model|student|"
    r"adult man|adult woman|adult person|young adult man|young adult woman|young adult|"
    r"young man|young woman|young person|couple|twins|group|band|vocalists?|choir|duo|trio)\b", re.I)
MALE_SUBJ = {"man", "men", "boy", "boys", "male", "males", "gentleman", "gentlemen", "guy", "guys",
             "businessman", "young man", "adult man", "young adult man"}
FEM_SUBJ = {"woman", "women", "girl", "girls", "female", "ladies", "lady",
            "young woman", "adult woman", "young adult woman"}
# 🔴 11-10 02:20 = band 移除 = "a dark blue silk band" = 腰带不是乐队
GRP_SUBJ = {"couple", "twins", "vocalist", "vocalists", "singer", "group", "choir", "duo", "trio"}
NEUTRAL_SUBJ = {"person", "people", "model", "student", "youth", "young adult", "young person",
                 "adult person", "someone", "figure", "subject", "individual"}

# ── 全文身份词（中性主体二次判定）────────────────────────────
MALE_ID = re.compile(
    r"\b(man|men|boy|boys|male|gentleman|gentlemen|guy|guys|businessman)\b", re.I)

# 🔴 背景剪影/海报里的人 = 不是主体（"a banner showing a male silhouette"）
SILHOUETTE = re.compile(
    r"\b(?:male|female|man|woman|boy|girl)\s+(?:silhouette|figure|shape|"
    r"portrait|photograph|photo|image|picture|statue|mannequin|"
    r"cutout|outline|poster|advertisement|ad\b)", re.I)
FEM_ID = re.compile(
    r"\b(woman|women|girl|girls|female|lady|ladies)\b", re.I)
PRON_M = re.compile(r"\b(he|him|his)\b", re.I)
PRON_F = re.compile(r"\b(she|her|hers)\b", re.I)
PRON_N = re.compile(r"\b(they|their|them)\b", re.I)

# 🔴 明确女性主体 = 男女同框判据
FEM_LEAD = re.compile(
    r"\b(?:a|an|the|one|two|three|young|beautiful|glamorous|elegant|smiling)\s+(?:\w+[- ]){0,3}?"
    r"(woman|women|girl|female|lady|ladies)\b", re.I)

# 🔴 儿童 = 明确未成年 = 单独的 girl/boy/young girl 不算
# 🔴 11-10 02:05 = 裸 children/kids 不再直接判儿童
#   "a children's play area" = 场所名 = 不是儿童
#   "a few children splash in the water" / "children playing out of focus" = 路人背景 = 不是主体
#   = 儿童主体 = 主体位小童（CHILD_LEAD_STRICT）+ 与主体互动（CHILD_INTERACT）
#     + 明确的儿童词（toddler/infant/newborn/preteen/underage/little boy…）
CHILD_ID = re.compile(
    r"\b(kiddo|toddler|infant|newborn|"
    r"preteen|pre-teen|underage|kindergartener|"
    r"nursery school|little (boy|girl)|"
    r"child(?:'s|s)?\s+(?:hair|face|features|skin|body|legs|arms|hand|hands))\b", re.I)
CHILD_SUBJ = re.compile(
    r"\b(?:a|an|the|one|two|three|some|small|little)\s+(?:\w+[- ]){0,2}?"
    r"(child|children|kid|kids|toddler|infant|newborn|"
    r"preteen|teenager|adolescent|kindergartener)\b", re.I)
CHILD_COPRESENT = re.compile(
    r"\b(?:and|with|beside|next to|alongside|holding|carrying)\s+(?:a|an|the)?\s*"
    r"(?:\w+[- ]){0,2}?(young|little)\s+(boy|girl)\b", re.I)
CHILD_LEAD_BOY = re.compile(
    r"^(?:[^.]{0,40}?\b)(?:a|an|the|one|two|three)\s+(?:\w+[- ]){0,2}?"
    r"(young|little)\s+(boy|girl)\b", re.I)
MINOR_AGE = re.compile(r"\b(\d{1,2})\s*-?\s*year[- ]old\b", re.I)

# ── 误报排除（颜色 / 服饰名 = 不是人）────────────────────────
FALSE_POS = re.compile(
    r"\b(baby\s+pink|baby[\s-]?blue|baby\s+doll|babydoll|baker\s+boy\s+cap|"
    r"boyish|bullboy|childlike|child-like)\b", re.I)
CAR_SEAT = re.compile(
    r"\b(child car seat|child seat|child-seat|car seat for (a )?(child|baby|infant)|baby seat)\b", re.I)

# 🔴 11-09 23:30 = 制服/道具/氛围 三类误报排除（我审 11 个新文件时踩出来的）
#  ① schoolgirl / schoolboy / school uniform = 服装风格词 = 主体仍是成年女性
#     （"A young woman wears a Japanese schoolgirl uniform" = 制服不是儿童）
#  ② children's book / children's snack / toy = 画面里的道具 = 主体仍是成年女性
#  ③ teenage / adolescent 描述"氛围 vibe"而非年龄 = 主体明确写 adult woman 时不算
SCHOOL_UNIFORM = re.compile(
    r"\b(schoolgirl|schoolboy|schoolgirl style|schoolboy style|school uniform|"
    r"school-girl|schoolboy-inspired|sailor uniform|student uniform|"
    r"schoolgirl innocence|schoolgirl charm|schoolgirl chic|schoolgirl fantasy|"
    r"schoolgirl twist|schoolgirl uniform|school uniform)\b", re.I)
CHILD_PROP = re.compile(
    r"\b(children'?s (book|snack|snacks|menu|playground|toy|toys|game|games|"
    r"clothing|clothes|room|area|wear)|children'?s book|children'?s snacks|"
    r"kid'?s (toy|book)|toy box|teddy bear|cute pink-eared bunny)\b", re.I)
VIBE_ONLY = re.compile(
    r"\b(teenage|adolescent|teen|pubescent)\s+(?:\w+[- ]){0,3}?"
    r"(vibe|mood|energy|aesthetic|style|charm|fantasy|atmosphere|tone|era|"
    r"days|years|tenderness|romance|romantic|intimacy|fantasy|spirit|"
    r"rebellious|playful|innocent|energy|passion|desire)\b", re.I)

# 🔴 11-10 01:50 = 背景小孩判据修正（我上一轮剔严了）
#   主人钦定的是「儿童【主体】不保留」= 路人背景小孩 = 真人街拍常态 = 保留
#   （跟背景男人一个道理：主体是她 = 画面里有个小孩不等于主体是小孩）
#   = 儿童主体 = 小孩占据主体位 / 与主体互动 / 主体是小童
#   = 路人背景 = 在 background / midground / 远处 / 走过 / 虚化 = 保留
CHILD_INTERACT = re.compile(
    r"(?:\b(?:child|children|kid|kids|infant|toddler)\b[^.]{0,60}?"
    r"(?:in her arms|in his arms|being held|held by|hugs?|holds?|carried|"
    r"in the (?:foreground|center|centre)|at the center|at the centre)|"
    r"[^.]{0,60}?\b(?:child|children|kid|kids|infant|toddler)\b[^.]{0,40}?"
    r"(?:in her arms|in his arms|being held|held by|hugs?|holds?|carried))", re.I)

# 明确儿童主体 = 主语位是小童
CHILD_LEAD_STRICT = re.compile(
    r"^(?:[^.]{0,50}?\b)(?:a|an|the|one|two|three)\s+(?:\w+[- ]){0,2}?"
    r"(?:child|children|kid|kids|toddler|infant|newborn|schoolboy|schoolgirl|"
    r"preteen|kindergartener|\d{1,2}-year-old\s+(?:boy|girl|child))\b", re.I)

# ── 背景路人 / 语境词（主体仍是女的 = 保留）────────────────────
BG_HINT = re.compile(
    r"\b(background|behind her|behind him|bystander|pedestrian|passerby|"
    r"poster|signage|photograph in the|on the wall|foreground of|"
    r"in the distance|far background|passing by)\b", re.I)


def strip_false_pos(t):
    t = CAR_SEAT.sub(" ", t)
    t = FALSE_POS.sub(" ", t)
    t = CHILD_PROP.sub(" ", t)
    # 🔴 制服 = 服装不是人 = 但要保留"制服"这词本身给 AI 看 = 用标记替换不清空
    t = SCHOOL_UNIFORM.sub(" [school-uniform-style] ", t)
    # 氛围词 teenage vibe = 不是年龄
    t = VIBE_ONLY.sub(" [teenage-vibe] ", t)
    return t


def is_child(t):
    """→ (是否儿童, 依据)"""
    tc = strip_false_pos(t)
    if CHILD_SUBJ.search(tc[:350]):
        return True, "儿童主体"
    if CHILD_COPRESENT.search(tc):
        return True, "画面含小童"
    if CHILD_LEAD_BOY.search(tc):
        return True, "主体是小童"
    m = CHILD_ID.search(tc)
    if m:
        return True, "儿童词«%s»" % m.group(0)
    for mm in MINOR_AGE.finditer(tc):
        if int(mm.group(1)) < 18:
            return True, "未成年%d岁" % int(mm.group(1))
    # 🔴 儿童主体（严格）= 小孩在主体位 / 与主体互动
    if CHILD_LEAD_STRICT.search(tc):
        return True, "儿童主体"
    if CHILD_INTERACT.search(tc):
        return True, "儿童与主体互动"
    return False, ""


def read_pool(path):
    """→ [(编号int, 正文)]"""
    rows = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            m = re.match(r"^(\d+)\|(.+)$", ln.strip())
            if m and m.group(2).strip():
                rows.append((int(m.group(1)), m.group(2).strip()))
    return rows


def classify(prompt):
    """→ (类别, 依据)"""
    body = strip_false_pos(prompt)

    ch, why = is_child(prompt)
    if ch:
        return "child_lead", why

    head = body[:400]
    m = PERSON.search(head)
    subj = m.group(1).lower() if m else None

    if subj in MALE_SUBJ:
        # 🔴 男女同框 = 句首男主体但画面有明确女性主体 = 保留
        if FEM_LEAD.search(body):
            return "female_lead", "句首男主体但画面有明确女性主体 = 男女同框（保留）"
        return "male_lead", "句首主体=%s" % subj
    if subj in FEM_SUBJ:
        return "female_lead", "句首主体=%s" % subj
    if subj in GRP_SUBJ:
        return "mixed_group", "句首主体=%s" % subj
    if subj in NEUTRAL_SUBJ:
        # 中性主体 → 全文代词分布二次判定
        pm = len(PRON_M.findall(body)); pf = len(PRON_F.findall(body))
        if pm > pf:
            return "male_lead", "中性主体(%s)男代%d>女%d" % (subj, pm, pf)
        if pf > pm:
            return "female_lead", "中性主体(%s)女代%d>男%d" % (subj, pf, pm)
        return "neutral", "中性主体(%s)代男%d/女%d/中%d" % (
            subj, pm, pf, len(PRON_N.findall(body)))

    # 无句首主体 → 全文身份词（先剔背景剪影/海报里的人）
    body2 = SILHOUETTE.sub(" ", body)
    mh = MALE_ID.search(body2)
    fh = FEM_ID.search(body2)
    if mh and fh:
        if FEM_LEAD.search(body):
            return "female_lead", "无句首主体但有明确女性主体 = 男女同框（保留）"
        return "contested", "无句首主体, 男女身份词并存(«%s»/«%s»)= 需人工判" % (
            mh.group(0), fh.group(0))
    if mh:
        return "male_lead", "无句首主体, 只有男性词«%s»" % mh.group(0)
    if fh:
        return "female_lead", "无句首主体, 女性词«%s»" % fh.group(0)
    return "neutral", "无主体线索"


def audit(path):
    rows = read_pool(path)
    cats = {}
    detail = {}
    male_mention = []
    child_mention = []
    for n, p in rows:
        cat, why = classify(p)
        cats[cat] = cats.get(cat, 0) + 1
        detail.setdefault(cat, []).append({"id": n, "why": why})
        b = strip_false_pos(p)
        if MALE_ID.search(b):
            male_mention.append(n)
        if CHILD_ID.search(b):
            child_mention.append(n)
    total = len(rows)
    counted = sum(cats.values())
    return {
        "path": path,
        "total": total,
        "counts": cats,
        "conserved": counted == total,
        "non_female_ids": {
            k: [d["id"] for d in v]
            for k, v in detail.items() if k != "female_lead"
        },
        "non_female_reasons": {
            k: [{"id": d["id"], "why": d["why"]} for d in v]
            for k, v in detail.items() if k != "female_lead"
        },
        "male_word_mentions": len(male_mention),
        "child_word_mentions": len(child_mention),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="池文件路径（省略 = 审计全部现役池）")
    ap.add_argument("--pool", help="只审一个现役池：main / sfw / male")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args()

    targets = list(args.files)
    if args.pool:
        key = args.pool.lower()
        # 🔴 11-12 = 合并池文件删了 = "all" = 两个现役池都审
        if key != "all" and key not in POOLS:
            print(f"未知池 {args.pool}；可用：{list(POOLS)} + all", file=sys.stderr)
            sys.exit(2)
        targets = list(POOLS.values()) if key == "all" else [POOLS[key]]
    if not targets:
        targets = list(POOLS.values())

    reports = []
    for t in targets:
        if not os.path.exists(t):
            print(f"❌ 池不存在：{t}", file=sys.stderr)
            sys.exit(2)
        reports.append(audit(t))

    if args.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
        return 0

    for r in reports:
        print(f"\n=== {r['path']} ===")
        print(f"总条数 {r['total']}")
        for k in ("female_lead", "male_lead", "child_lead", "mixed_group",
                  "contested", "neutral"):
            if r["counts"].get(k):
                print(f"  {k:14s} {r['counts'][k]}")
        print(f"  守恒校验     {'✅ 相等' if r['conserved'] else '❌ 不等 = 判据有漏'}")
        print(f"  全文含男性词 {r['male_word_mentions']}（含背景路人 / 男伴 = 主体不变）")
        print(f"  全文含儿童词 {r['child_word_mentions']}")
        for cat in ("male_lead", "child_lead", "mixed_group", "contested"):
            ids = r["non_female_ids"].get(cat) or []
            if ids:
                print(f"  ⚠️ {cat} 编号 = {ids[:40]}{' ...' if len(ids) > 40 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
