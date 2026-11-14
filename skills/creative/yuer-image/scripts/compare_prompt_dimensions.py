#!/usr/bin/env python3
"""提示词维度覆盖自检 = 「我写的比不上抽卡」的机械判据。

为什么需要这个脚本：
    「我写的提示词总比不上抽卡」不是玄学 = 是**维度覆盖度**不够。
    量化对照（参考库成品提示词 vs 自己写的）：
        库牌命中率高 = 景别 / 道具清单 / 材质对比 / 氛围句 / 景深 / 质量词
        自己写的 = 这些维度整类为 0，字符全砸在私处锚 + 身材上
    = 画面「更色情但更不好看」= 砍字时砍的顺序反了。

用法：
    python3 compare_prompt_dimensions.py /tmp/prompt_a.txt /tmp/prompt_b.txt
    python3 compare_prompt_dimensions.py --lib <参考库.md>        # 只出库牌基线
    python3 compare_prompt_dimensions.py --lib <参考库.md> --quiet # 库牌基线只打汇总

退出码：0 = 每个文件都覆盖了「必写维度」；1 = 有文件缺维度（缺哪几项会打出来）。

维度判定 = 正则命中 = 与库牌统计同一套正则 = 0 凭印象说「我写了景别」。
"""
import argparse
import re
import statistics as st
import sys

# 维度 = 正则 = 「这一层画面信息有没有被写到」
# 必写维度 = 参考库成品提示词里命中率 >= 40% 的那些（基线由 --lib 现算，这里是常量）
DIMS = [
    ("表情物理化", r"\beyes\b|\blips\b|\bchin\b|\bmouth\b|corner of her|eyelids"),
    ("景别", r"close-up|full-length|full body|medium (?:close-)?shot|waist-up|half-body|bust shot"),
    ("机位角度", r"low angle|high angle|eye level|looking up|looking down|from below|from above|from behind"),
    ("镜头焦段", r"\d{2,3}mm f/"),
    ("相机型号", r"(?:Shot on|shot on|Captured on|captured on|taken with|photograph taken on) [A-Z]"),
    ("唯一光源+光位", r"[Ll]ighting .{0,90}from|single .*light|one .*lamp|backlight|rim light"),
    ("材质对比", r"contrasting|contrast(?:ing)? |texture|matte|glossy|sheen|reflective|shimmer"),
    ("氛围/调色", r"[Mm]ood|[Aa]tmosphere|overall|tone|color grading|cinematic"),
    ("道具清单", r"gloves?|heels?|boots?|\bhat\b|\bcap\b|nail polish|necklace|earrings|bracelet|belt|scarf|ribbon|brooch"),
    ("皮肤质感", r"\bskin\b"),
    ("景深/虚化", r"bokeh|depth of field|shallow focus|out of focus"),
    ("质量词", r"8K|ultra-HD|hyper-realistic|ultra-sharp|photorealistic|8k"),
    ("身材锚", r"hourglass|waist|breast|buttock|thigh"),
    ("私处锚", r"innie|labia|pubic"),
]

# 参考库成品提示词的抽取方式（两种排版都接）
FULL_PROMPT_ROW = re.compile(r'\| \*\*Full Prompt\*\* \| (.+)')
CN_PROMPT_ROW = re.compile(r'\*\*成品提示词\*\*\s*(.+)')

# 库牌基线（参考库 684 条实测）
LIB_BASELINE = {
    "表情物理化": 45, "景别": 26, "机位角度": 40, "镜头焦段": 55,
    "相机型号": 49, "唯一光源+光位": 35, "材质对比": 67, "氛围/调色": 67,
    "道具清单": 66, "皮肤质感": 112, "景深/虚化": 46, "质量词": 172,
    "身材锚": 119, "私处锚": 2,
}
# 必写 = 库牌命中率 >= 40%（低于 40% = 该维度在牌库里本来就不是每条都有 = 不强制）
REQUIRED = [n for n, v in LIB_BASELINE.items() if v >= 40]


def read_lib(path):
    s = open(path, encoding="utf-8", errors="ignore").read()
    out = []
    for rx in (FULL_PROMPT_ROW, CN_PROMPT_ROW):
        for m in rx.finditer(s):
            t = m.group(1).strip()
            if len(t) > 200:
                out.append(t)
    seen, cards = set(), []
    for t in out:
        if t[:80] in seen:
            continue
        seen.add(t[:80])
        cards.append(t)
    return cards


def hit(p, pat):
    return bool(re.search(pat, p, re.I | re.S))


def score(text):
    return {name: hit(text, pat) for name, pat in DIMS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="prompt 文件；- 表示 stdin")
    ap.add_argument("--lib", default="", help="参考库 md 路径（出库牌基线）")
    ap.add_argument("--quiet", action="store_true", help="库牌基线只打汇总")
    args = ap.parse_args()

    if args.lib:
        cards = read_lib(args.lib)
        if not cards:
            print("库牌基线：0 条 = 路径不对或排版不同", file=sys.stderr)
            return 2
        print(f"库牌基线 = {len(cards)} 条成品提示词\n")
        print("维度".ljust(18) + "命中率".rjust(8) + "   必写")
        for name, pat in DIMS:
            r = len([c for c in cards if hit(c, pat)]) / len(cards) * 100
            flag = "★" if name in REQUIRED else ""
            if not args.quiet:
                print(name.ljust(18) + f"{r:>7.0f}%".rjust(8) + "   " + flag)
        lens = [len(c) for c in cards]
        sents = [len([x for x in re.split(r'(?<=[.!?])\s+', c) if x.strip()]) for c in cards]
        print()
        print(f"长度中位 {int(st.median(lens))}  句数中位 {st.median(sents):.0f}"
              f"  平均句长 {int(st.median([l / max(1, n) for l, n in zip(lens, sents)]))}")
        if not args.files:
            return 0

    if not args.files:
        print("用法: compare_prompt_dimensions.py <prompt 文件...> [--lib 参考库.md]", file=sys.stderr)
        return 2

    rc = 0
    for f in args.files:
        text = sys.stdin.read() if f == "-" else open(f, encoding="utf-8").read()
        sc = score(text)
        miss = [n for n in REQUIRED if not sc[n]]
        sents = len([x for x in re.split(r'(?<=[.!?])\s+', text.strip()) if x.strip()])
        print(f"\n=== {f}  ({len(text)} 字符 / {sents} 句) ===")
        for name, _ in DIMS:
            mark = "OK  " if sc[name] else "MISS"
            print(f"  {mark} {name}")
        if miss:
            rc = 1
            print(f"  → 缺必写维度: {', '.join(miss)}")
            print("    修法 = 每缺一维补一句（景别/道具/材质对比/氛围/景深/质量词/光位）"
                  " = 0 砍别的地方凑字数 = 0 认「我写了景别」")
        else:
            print("  → 必写维度全齐")
    return rc


if __name__ == "__main__":
    sys.exit(main())