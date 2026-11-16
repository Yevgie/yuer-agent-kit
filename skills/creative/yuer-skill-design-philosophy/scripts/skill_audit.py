#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill_audit.py · 技能臃肿体检器

唯一职责 = 量一个 SKILL.md 到底哪里在膨胀，输出可执行的减法清单。
不删任何东西 = 只体检 = 主人/语儿看了清单再拍板。

用法:
    python3 skill_audit.py                       # 全库体检榜 (Top 30)
    python3 skill_audit.py <skill_dir_or_path>   # 单份体检 + 逐段明细
    python3 skill_audit.py --top 10              # 只看最大的 N 份
    python3 skill_audit.py --json                # 机读输出

指标定义:
    重复标题组   = 去掉版本号/实战号后标题完全相同的组数 = 只增不减的证据
    重复段字数   = 重复标题组的正文总长 = 直接可砍的字节
    升版流水段   = 标题含 vX.Y 的段数 = 改一次加一段的证据
    撞车表段     = 标题含「撞车/反例/反模式」且内含表格的段 = 整改履历堆积
    五段骨架     = 主协议/主体/服装/场景/尾参 = yuer-prompt-writer 用
"""
import os
import re
import sys
import json
from collections import defaultdict

SKILLS_ROOT = os.path.expanduser("~/.hermes/skills")

# 规矩类关键词 = 该留的
RULE_HINTS = ("铁律", "必须", "必走", "必填", "禁", "0 ", "✅", "正解", "金标准", "SOP", "铁则")
# 履历类关键词 = 该删的（整改历史 / 版本对比 / 实测流水）
HISTORY_HINTS = ("真根因", "撞车原话", "打脸原话", "升级真根因", "已落地", "实测数据", "本次升级不修改",
                 "vs v", "关键差异", "整改清单", "整改复盘", "版本对比", "实战档（references/）")


def load_headings(text):
    """返回 [(标题行号, 标题, 该段正文)]，代码块内的 # 不算标题。"""
    lines = text.split("\n")
    inblock = False
    heads = [(-1, "(前言)", "\n".join(lines))]
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("```"):
            inblock = not inblock
            continue
        if inblock:
            continue
        if re.match(r"^#{1,4} ", ln):
            heads.append((i, ln.strip(), ""))
    out = []
    for k, (i, h, _) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        body = "\n".join(lines[i + 1:end])
        out.append((i + 1, h, body))
    return out


def norm_title(h):
    t = re.sub(r"^#+\s*", "", h)
    t = re.sub(r"v\d+(\.\d+)*", "", t)          # v4.5.72
    t = re.sub(r"实战\s*\d+[A-Za-z\-]*", "", t)   # 实战 494g
    t = re.sub(r"\d{2}-\d{2}", "", t)            # 09-26
    t = re.sub(r"[（）()·、,，。：:\-—/|\[\]]", "", t)
    return t.strip()


def audit_file(path):
    text = open(path, encoding="utf-8", errors="ignore").read()
    chars = len(text)
    lines = text.count("\n") + 1
    heads = load_headings(text)

    # 重复标题组
    groups = defaultdict(list)
    for ln, h, body in heads:
        groups[norm_title(h)].append((ln, h, body))
    dup_groups = {k: v for k, v in groups.items() if len(v) > 1}
    dup_chars = sum(len(b) for v in dup_groups.values() for _, _, b in v[1:])

    # 分类统计
    hist_chars = 0
    rule_chars = 0
    hist_segs = []
    for ln, h, body in heads:
        hk = " ".join(HISTORY_HINTS)
        if hk and any(x in h for x in HISTORY_HINTS) and len(body) > 200:
            hist_chars += len(body)
            hist_segs.append((ln, h, len(body)))
    for ln, h, body in heads:
        if any(x in h for x in RULE_HINTS) or any(x in body[:400] for x in RULE_HINTS):
            rule_chars += len(body)

    versions = re.findall(r"v\d+\.\d+", text)
    uniq_versions = sorted(set(versions), key=lambda s: [int(x) for x in s.lstrip("v").split(".")])

    return {
        "path": path,
        "chars": chars,
        "lines": lines,
        "headings": len(heads),
        "dup_groups": len(dup_groups),
        "dup_chars": dup_chars,
        "dup_pct": round(dup_chars * 100 / chars, 1) if chars else 0,
        "history_chars": hist_chars,
        "history_pct": round(hist_chars * 100 / chars, 1) if chars else 0,
        "rule_chars": rule_chars,
        "uniq_versions": len(uniq_versions),
        "top_versions": uniq_versions[-6:],
        "hist_segs": sorted(hist_segs, key=lambda x: -x[2])[:8],
        "dup_detail": sorted(
            [(" ×%d  %s" % (len(v), v[0][1][:70]), len("".join(b for _, _, b in v)))
             for k, v in dup_groups.items()],
            key=lambda x: -x[1])[:6],
    }


def all_skills():
    out = []
    for root, dirs, files in os.walk(SKILLS_ROOT):
        if "SKILL.md" in files:
            out.append(os.path.join(root, "SKILL.md"))
    return out


def fmt_full(r):
    L = []
    L.append("=" * 72)
    L.append("%s" % r["path"])
    L.append("  %d 行 / %d 字 / %d 个标题" % (r["lines"], r["chars"], r["headings"]))
    L.append("  重复标题组 %d 个 = 可砍 %d 字 (%s%%)" % (r["dup_groups"], r["dup_chars"], r["dup_pct"]))
    L.append("  履历段(真根因/对比/已落地) %d 字 (%s%%)" % (r["history_chars"], r["history_pct"]))
    L.append("  规矩段 %d 字 (%s%%)" % (r["rule_chars"], 100 - r["history_pct"] if r["history_pct"] < 100 else 0))
    L.append("  不同版本号 %d 个：%s" % (r["uniq_versions"], ", ".join(r["top_versions"])))
    if r["dup_detail"]:
        L.append("")
        L.append("  ── 重复标题（只增不减的直接证据）")
        for t, c in r["dup_detail"]:
            L.append("    %6d 字  %s" % (c, t))
    if r["hist_segs"]:
        L.append("")
        L.append("  ── 履历段 TOP（整改历史 = 该删）")
        for ln, h, c in r["hist_segs"]:
            L.append("    %6d 字  L%-5d %s" % (c, ln, h[:66]))
    L.append("")
    return "\n".join(L)


def main():
    args = [a for a in sys.argv[1:]]
    as_json = "--json" in args
    args = [a for a in args if not a.startswith("--")]
    top = 30
    if "--top" in sys.argv:
        top = int(sys.argv[sys.argv.index("--top") + 1])
        args = [a for a in args if a != str(top)]
    if args:
        p = args[0]
        path = p if os.path.isfile(p) else os.path.join(p, "SKILL.md")
        if not os.path.exists(path):
            path = os.path.join(SKILLS_ROOT, p, "SKILL.md")
        if not os.path.exists(path):
            print("找不到: %s" % p)
            sys.exit(1)
        r = audit_file(path)
        print(json.dumps(r, ensure_ascii=False, indent=2) if as_json else fmt_full(r))
        return

    rows = [audit_file(p) for p in all_skills()]
    rows.sort(key=lambda r: -r["chars"])
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    total = sum(r["chars"] for r in rows)
    print("技能总数 %d 份 / 合计 %d 字" % (len(rows), total))
    print()
    print("%-52s %7s %6s %6s %6s %5s" % ("SKILL", "字数", "行数", "重复%", "履历%", "版本号"))
    print("-" * 92)
    for r in rows[:top]:
        name = r["path"].replace(SKILLS_ROOT + "/", "")
        print("%-52s %7d %6d %5s%% %5s%% %5d" % (
            name, r["chars"], r["lines"], r["dup_pct"], r["history_pct"], r["uniq_versions"]))
    print("-" * 92)
    big = [r for r in rows if r["chars"] >= 50000]
    print("超 5 万字: %d 份 = 合计 %d 字 (%d%%)" % (
        len(big), sum(r["chars"] for r in big), sum(r["chars"] for r in big) * 100 // total))
    savable = sum(r["dup_chars"] for r in rows)
    print("全库重复段可砍: %d 字 = %d%%" % (savable, savable * 100 // total))


if __name__ == "__main__":
    main()
