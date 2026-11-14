#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽卡第 1+2 步 = 抽 1 条角色档案 + 把【成品提示词】原样落盘（一次做完）。

用法（抽卡 = 3 条命令，这条吃掉前两条）：
    /usr/bin/python3 ~/.hermes/skills/creative/yuer-character-roster/scripts/pick_ka_prompt.py

stdout：
    REC=<记录号>
    CHARS=<落盘字符数>
    PROMPT=<落盘路径>
    [牌面字段行原样打印 = 给人看抽到什么，不进提示词]
    WARN ...            ← 牌面残渣告警，有几条打几条

为什么必须是脚本（不是手打）：
  - pick_roster_record.py 每次调用都重新洗牌，多调一次 = 抽到另一张牌 = 白抽烧好牌；
  - 成品提示词上千字符，手打进 write_file = 人手过一遍 = 加工 = 违「0 加工」；
  - 脏 token / 双逗号 / 空括号要在**同一次**里剥完：分两趟 = 白多一轮工具调用
    + 白多一次改牌机会（这条复发过，改成脚本后想分两趟都没有分两趟的机会）。
"""
import os
import re
import subprocess
import sys

PICK = os.path.expanduser(
    "~/.hermes/skills/yuer-run-one-brief/scripts/pick_roster_record.py"
)
OUT_DIR = "/tmp"


def main() -> int:
    # ① 只调一次抽签脚本
    proc = subprocess.run(
        ["/usr/bin/python3", PICK],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    card = proc.stdout.decode("utf-8", "replace").strip()
    if not card:
        print("WARN 抽签脚本无输出（牌池空 / 脚本异常）", file=sys.stderr)
        return 1

    lines = card.splitlines()

    # ② 记录号（正则取，不靠固定位置）
    m = re.search(r"记录\s*(\d+)", card)
    if not m:
        print("WARN 牌面没有记录号 = 解析失败", file=sys.stderr)
        print(card)
        return 1
    rec = m.group(1)

    # ③ 成品提示词（库里已有成品 = 原文，不重写）
    p = None
    for line in lines:
        if line.lstrip().startswith("[成品提示词]"):
            p = line.split("[成品提示词]", 1)[1].strip()
            break
    if not p:
        print(f"WARN 记录 {rec} 的【成品提示词】为空 = 库里这格没写全", file=sys.stderr)
        print(card)
        return 1

    # ④ 机械去噪（0 语义加工：只剥解析残渣，不重写 / 不改结构 / 不翻译 / 不动语序）
    p = re.sub(r"\s*\b[a-z]{3,}con\b", "", p, flags=re.I)  # 脏 token（lngcon 那种）
    p = re.sub(r"\s*([,;:])\s*\1+", r"\1", p)               # ,, ;; :: 重复标点
    p = re.sub(r"\(\s*\)", "", p)                           # 空括号残片
    p = p.replace(" ,", ",").strip()

    dest = os.path.join(OUT_DIR, f"ka_{rec}_prompt.txt")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(p)

    print(f"REC={rec}")
    print(f"CHARS={len(p)}")
    print(f"PROMPT={dest}")

    # ⑤ 残渣告警：字段行自带 ⚠️ token 标记 / 提示词里残留中文 = 池子被解析器污染过
    for line in lines:
        if "⚠️" in line:
            print("WARN " + line.strip())
    cjk = re.findall(r"[\u4e00-\u9fff]", p)
    if cjk:
        print(f"WARN 提示词内残留 {len(cjk)} 个中文字符 = 牌面被污染 = 对照上面的牌面字段行")

    # ⑥ 牌面字段行原样打印
    for line in lines:
        if line.startswith("["):
            print(line)
    # 🔴 11-04 星级：牌面字段行循环已经会打印 `[星级] ★★★`（pick_roster_record.py 里加的）
    # = 这里 0 重复打印 = 之前我手加过一份 = 结果打了两遍 = 撤掉。

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
