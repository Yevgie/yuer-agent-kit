#!/usr/bin/env python3
"""跨技能矛盾探针 = 反模式 21 / 22 的机械入口。

查两类病（都跨文件，单份四项自查查不出）：
  21 = 两处同时活着的对打规则
  22 = 机制变了，旧规则的前提没了但它还活着

用法：
  python3 cross_skill_conflict_probe.py                       # 默认动作组 × 全库
  python3 cross_skill_conflict_probe.py --skills a b c         # 只比指定技能
  python3 cross_skill_conflict_probe.py --matrix-only          # 只打命中矩阵
  python3 cross_skill_conflict_probe.py --topic 发图 --matrix-only  # 自定义动作词

输出两部分：命中矩阵（哪一行密集 = 职责重叠区）+ 重叠区的硬约束行并排。
命中矩阵只告诉你「哪里重叠」，**对打点靠人读并排的硬约束行**——脚本不猜结论。
"""
import argparse
import os
import re
import sys

DEFAULT_ACTIONS = {
    "出图/看图": r"看看你|出图|看图",
    "继续": r"「继续」|'继续'|说「继续」",
    "洗图": r"洗图",
    "存档": r"存档",
    "抽卡": r"抽卡",
    "reply格式": r"reply.*(格式|铁律|纪律)",
    "发图": r"真发飞书|发图铁律|必发图|投递",
    "门禁": r"门禁|count_prompt_chars",
    "prompt结构": r"结构段|分段|段落|6\s*句|背景:|Background:",
}

# 硬约束行 = 命令式短行（不看解释段，只看规定本身）
HARD = re.compile(r"(❌|✅|🔴|必须|0\s*MEDIA|禁止|禁\s|不许|必带|必走|一律|盖过)")


def skill_paths(base: str):
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if "bak" not in d and d not in (".archive", ".git")]
        if "SKILL.md" in files and os.path.basename(root) != "scripts":
            yield os.path.join(root, "SKILL.md")


def load(paths):
    out = {}
    for p in paths:
        try:
            out[p] = open(p, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
    return out


def matrix(docs, actions, width=44):
    names = list(docs)
    print(f"{'动作':<14}" + "".join(f"{os.path.basename(os.path.dirname(p))[:9]:>11}" for p in names))
    print("-" * (14 + 11 * len(names)))
    dense = []
    for act, pat in actions.items():
        row = [len(re.findall(pat, docs[p])) for p in names]
        print(f"{act:<14}" + "".join(f"{v:>11}" for v in row))
        if sum(1 for v in row if v > 0) >= 3:
            dense.append(act)
    return dense


def hard_lines(docs, dense, top=16):
    """只对重叠区里出现的技能打硬约束行——全库打印没人看得完。

    对打点靠人读；脚本不猜结论。
    """
    if not dense:
        return []
    pats = {a: re.compile(p) for a, p in DEFAULT_ACTIONS.items() if a in dense}
    shown = 0
    for p, text in docs.items():
        name = os.path.basename(os.path.dirname(p))
        if not any(rx.search(text) for rx in pats.values()):
            continue
        lines = [l.strip() for l in text.split("\n")]
        hits = [l for l in lines if HARD.search(l) and 12 < len(l) < 190]
        if not hits:
            continue
        print(f"\n{'#' * 10} {name}  ({len(lines)}行) 命中 {len(hits)}")
        seen = set()
        for h in hits:
            if h in seen:
                continue
            seen.add(h)
            print(f"    {h[:150]}")
            if len(seen) >= top:
                break
        shown += 1
    return shown


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills", nargs="*", default=None, help="只比这几个技能目录名")
    ap.add_argument("--base", default=os.path.expanduser("~/.hermes/skills"))
    ap.add_argument("--matrix-only", action="store_true")
    ap.add_argument("--topic", help="自定义动作词，逗号分隔")
    args = ap.parse_args()

    paths = sorted(skill_paths(args.base))
    if args.skills:
        paths = [p for p in paths if os.path.basename(os.path.dirname(p)) in args.skills]
    if not paths:
        print("没找到技能", file=sys.stderr)
        return 2

    docs = load(paths)
    actions = dict(DEFAULT_ACTIONS)
    if args.topic:
        actions = {t: t for t in args.topic.split(",") if t}

    print(f"扫描 {len(docs)} 份技能\n")
    dense = matrix(docs, actions)
    print("\n职责重叠区 = " + (", ".join(dense) if dense else "无"))

    if args.matrix_only or not dense:
        return 0

    print("\n" + "=" * 66)
    print("重叠区硬约束行并排——**对打点靠人读，脚本不猜结论**")
    print("=" * 66)
    n = hard_lines(docs, dense)
    print(f"\n（共 {n} 份技能落在重叠区）")
    print("下一步（反模式 22）：对每条对打规则问「它依赖的前提现在还成立吗」，")
    print("前提不成立的整条删，不是加一句新禁令盖住。")
    return 0


if __name__ == "__main__":
    sys.exit(main())