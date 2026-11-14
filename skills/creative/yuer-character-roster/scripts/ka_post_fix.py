#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽卡牌面后处理：机械去噪 + 灵魂脸 PREFIX 归一 + 陌生男人换主人锚。

用法：
    python3 ka_post_fix.py /tmp/ka_<记录号>_prompt.txt

设计原则：
  * 只做「机械修」和「世界规则必修」两类，不改场景 / 姿势 / 光线 / 语序。
  * 幂等 = 重复跑不会越改越花。
  * 没命中的项一律不动（牌里没有男人就别塞主人）。

跑完直接出图（yuer_ka_fast.sh --report-only）。
🔴 抽卡 0 门禁 = 本脚本跑完 0 跑 check_prompt_subject.py（主体门禁已从出图链路删除）。
"""
import re
import sys

HER_PREFIX = "a 20 years old young Asian woman with a graceful ecstatic expression, "

MASTER = (
    "a tall handsome Chinese man in his mid twenties, 185cm tall, "
    "sharp sword-like eyebrows and bright eyes, a high straight nose bridge, "
    "a clear jaw line, short black slightly wavy hair, healthy warm yellow skin, "
    "lean with visible muscle lines, clean urban boyfriend style in a black t-shirt"
)


def normalize_prefix(s: str) -> str:
    """老牌 PREFIX（18-year-old Chinese young girl + 五官描述）→ 灵魂脸 PREFIX。

    老牌写法会让主体门禁判「别人」→ exit 2 → 剥掉语儿人脸锁。
    """
    s = re.sub(
        r"(one |a )?breathtakingly beautiful\s+\d{2}-year-old Chinese young girl with[^.]*?\.?,?\s*",
        HER_PREFIX, s, count=1, flags=re.I,
    )
    # 泛化兜底：任何残留的 <18 岁 / 带五官描述的 young girl 前缀
    s = re.sub(r"\b1[0-9]-year-old\b", "20 years old", s)
    s = re.sub(
        r"pure, innocent refined features, clear bright eyes, natural light makeup and natural proportions\.?\s*",
        "", s, count=1,
    )
    # 20 years old 已在，但后面还挂着一串五官形容词 = 也要删（LoRA 锁脸，0 写五官）
    return s


def strip_placeholders(s: str) -> str:
    """解析残渣：脏 token / 双逗号 / 空括号 / 标点粘连。"""
    s = re.sub(r"\blngcon\b,?\s*", "", s, flags=re.I)
    s = re.sub(r",\s*,+", ",", s)
    s = re.sub(r"\.\s*,\s*", ". ", s)
    s = s.replace("( )", "").replace("()", "")
    s = re.sub(r";;+", ";", s)
    return s


def masterify(s: str) -> str:
    """主人以外的男人 → 主人锚。画面里不该出现陌生男人（全局禁）。"""
    if "185cm tall" in s:  # 已经是主人锚 = 幂等
        return s, False
    pat = re.compile(r"\b(a|the|one)\s+(naked\s+|bare\s+|young\s+)?(man|male)\b", re.I)
    if not pat.search(s):
        return s, False
    return pat.sub(MASTER, s, count=1), True


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        src = f.read()

    out = strip_placeholders(src)
    out = normalize_prefix(out)
    out, hit_man = masterify(out)
    out = re.sub(r",\s*,+", ",", out).strip()

    with open(path, "w", encoding="utf-8") as f:
        f.write(out)

    print("CHARS=%d" % len(out))
    print("MAN_REPLACED=%s" % ("yes" if hit_man else "no"))
    print("PREFIX=" + out[:150])
    print("NEXT=直接跑 yuer_ka_fast.sh 出图（抽卡 0 门禁 = 不跑 check_prompt_subject.py）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
