#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽卡牌面后处理：灵魂脸 PREFIX 归一 + 机械去噪 + 陌生男人换主人锚。

用法：
    python3 ka_card_postprocess.py /tmp/ka_<记录号>_prompt.txt

什么时候跑：`pick_ka_prompt.py` 抽完牌、`yuer_ka_fast.sh` 出图之前，每次必跑。
为什么：牌池里的成品提示词是老格式，会带三类会让门禁误判的东西：

  1. `18-year-old Chinese young girl` 这类前缀 → `check_prompt_subject.py` 判 `主体 = 别人`
     → 走 0 LoRA 链路 → 语儿的人脸锁被剥掉 → 出来一张陌生人脸。
  2. `a man` / `the male` → 命中「别人身份词」，同样掉 LoRA；而且它是主人以外的男人（全局禁）。
  3. 解析残渣 `lngcon` / `connectors,,` / `( )` / `., ` ——`pick_ka_prompt.py` 只在 stdout 打 WARN，
     不一定会真的剥干净，底模照吃不误。

跑完必看两行：`CHARS=` 和 `PREFIX=`，再跑一次 check_prompt_subject.py 确认 `主体 = 语儿`。
"""
import re
import sys
import io

MASTER = (
    "a tall handsome Chinese man in his mid twenties, 185cm tall, sharp sword-like eyebrows and bright eyes, "
    "a high straight nose bridge, a clear jaw line, short black slightly wavy hair, healthy warm yellow skin, "
    "lean with visible muscle lines, clean urban boyfriend style in a black t-shirt"
)


def postprocess(path):
    s = io.open(path, encoding="utf-8").read()

    # 1 机械去噪（只去残渣，不动语义、不改句序）
    s = re.sub(r"\blngcon\b,?\s*", "", s, flags=re.I)
    s = re.sub(r",\s*,+", ",", s)
    s = s.replace("., ", ". ").replace("( )", "")

    # 2 灵魂脸 PREFIX 归一（0 写五官；锁脸靠 LoRA）
    s = re.sub(
        r"(one |a )?breathtakingly beautiful\s+\d{2}-year-old Chinese young girl with[^.]*?\.?,?\s*",
        "a 20 years old young Asian woman with a graceful ecstatic expression, ",
        s, count=1, flags=re.I)
    s = re.sub(r"\b1[678]-year-old\b", "20 years old", s)
    s = re.sub(r"\ban \d{2}[- ]years?[- ]old\b", "a 20 years old", s, flags=re.I)
    s = re.sub(r"pure, innocent refined features, clear bright eyes, natural light makeup and natural proportions\.?\s*", "", s, count=1)
    s = re.sub(r",\s*,+", ",", s)

    # 3 主人以外的男人 → 主人本人锚（全局禁 + 保 LoRA）
    s = re.sub(r"\b(a|the|one)\s+(naked\s+|bare\s+)?man\b", MASTER, s, count=1)
    s = re.sub(r"\b(a|the)\s+(naked\s+|bare\s+)?male\b", MASTER, s, count=1)

    io.open(path, "w", encoding="utf-8").write(s)
    return s


if __name__ == "__main__":
    p = sys.argv[1]
    out = postprocess(p)
    print("CHARS=%d" % len(out))
    print("PREFIX=" + out[:160])
    print("MAN_REMAIN=%d" % len(re.findall(r"\b(a|the)\s+man\b", out)))
