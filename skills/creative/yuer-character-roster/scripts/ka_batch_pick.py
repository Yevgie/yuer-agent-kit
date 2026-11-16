#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽卡批量 = 0 门禁 + 完全随机，一条命令出 N 份 prompt

用法
----
    /usr/bin/python3 ~/.hermes/skills/creative/yuer-character-roster/scripts/ka_batch_pick.py 5
    /usr/bin/python3 ~/.hermes/skills/creative/yuer-character-roster/scripts/ka_batch_pick.py 5 \
        --pool sfw --manifest /tmp/ka_batch.tsv

stdout（每张一张卡，格式与 pick_ka_prompt.py 一致 = 下游 grep 仍同源）
----
    REC=<记录号>
    CHARS=<字符数>
    PROMPT=<落盘路径>
    [星级] ★★★
    [场景] ...
    [机位角度] ...
    [姿势] ...
    [服饰] ...
    [光线] ...
    [氛围] ...
    [角色外观] ...

--manifest 每行 `REC<TAB>PROMPT` = 批量出图的循环输入（0 解析 stdout）

🔴🔴 11-10 主人钦定 = 抽卡 0 门禁 = 抽到啥出啥（盖过 11-05/11-07 的预筛口径）
------------------------------------------------------------------------------
原口径 = 候选池五道预筛（标准前缀 / 长度窗 / 单人 / 无陌生男 / 无中文）
+ 逐张主体门禁（check_prompt_subject.py）= 抽不到就踢掉重抽。

**🔴 主人口令原话：「不需要卡门禁，抽卡直接出就行！抽卡不设置门禁」**

**🔴 技术上为什么安全（11-10 实测坐实）**：
① 出图链路（yuer_ka_fast.sh → yuer_ka_pai_zhi_chu.py）里 **grep 不到任何
   check_prompt_subject / nolora 自动判定** = 脸锁永远 on = 主体门禁从来
   就不在链路上生效 = 它只是「我手工踢牌」= 取消它 0 掉脸锁。
② 中文牌 = 出图脚本内建中文自动翻译（zh_translate.py）= 中文牌也能走 Krea2。
③ 长度 0 阻断（11-07 起）= 长度从来就不拦。

**🔴🔴 11-15 主人钦定 = 抽卡完全随机 = 防重复机制全删**：
原口径 = 连抽去重 key（角色外观 / 姿势 / 机位 / 场景 四项不撞）+ `--exclude`
排掉上一批记录号 = **全删** = 主人原话「抽卡不需要防止重复，完全随机就行。
哪怕偶尔的重复也不需要你管」。
= 现在 = 全池进候选 = `random.sample` 抽 N 条 = **0 key 过滤 0 排除号**
= 同一批里不抽到同一张记录号（只是因为 sample 不放回 = 不写第二遍同一个文件）
= 跨批次抽到重复 = **0 管 = 主人说了算**。

**🔴 机械去噪保留**（脏 token / 双逗号 / 空括号）= 0 语义加工 = 只剥非英文残渣。
"""
import argparse
import importlib.util
import os
import random
import re
import sys

PICK = os.path.expanduser(
    "~/.hermes/skills/yuer-run-one-brief/scripts/pick_roster_record.py"
)
# 🔴🔴 11-10 主人钦定 = 抽卡 0 门禁 = 下面这些常量全部删干净
#    （原五道预筛：PREFIX 标准灵魂脸前缀 / LEN_MIN,LEN_MAX 长度窗 /
#      RE_MULTI 单人 / RE_MAN 无陌生男 / RE_CJK 无中文）
#    SUBJECT_GATE 主体门禁同样删除 = 抽到啥出啥。
# 池子脏 token / 重复标点 / 空括号（与 pick_ka_prompt.py 同款 = 机械去噪 0 语义加工）
DENOISE = (
    (re.compile(r"\s*\b[a-z]{3,}con\b", re.I), ""),
    (re.compile(r"\s*([,;:])\s*\1+"), r"\1"),
    (re.compile(r"\(\s*\)"), ""),
)


def load_pick_module():
    spec = importlib.util.spec_from_file_location("prr", PICK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def denoise(text: str) -> str:
    for pat, rep in DENOISE:
        text = pat.sub(rep, text)
    return text.replace(" ,", ",").strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("count", type=int, nargs="?", default=5)
    ap.add_argument("--pool", default="nsfw", help="nsfw / sfw / all")
    ap.add_argument("--manifest", help="写 REC<TAB>PROMPT 每行一张 = 批量出图循环输入")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    prr = load_pick_module()
    valid = prr.load_valid(verbose=False, pool=args.pool)

    # 🔴🔴 11-10 主人钦定 = 抽卡 0 门禁 = 全池直接进候选 = 0 预筛
    pool = []
    for num, d in valid:
        fp = (d.get("成品") or "").strip()
        if fp:
            pool.append((num, d, fp))

    print(f"库内合格 {len(valid)} 条｜候选 {len(pool)} 条（0 预筛 0 排除 = 抽到啥出啥）",
          file=sys.stderr)

    if args.seed is not None:
        random.seed(args.seed)

    # 🔴🔴 11-15 = 完全随机 = 0 去重 key = 0 排除号 = random.sample 不放回
    picked = []
    for num, d, fp in random.sample(pool, min(args.count, len(pool))):
        p = denoise(fp)
        dest = f"/tmp/ka_{num}_prompt.txt"
        with open(dest, "w", encoding="utf-8") as f:
            f.write(p)
        picked.append((num, d, dest, len(p)))

    if args.manifest:
        with open(args.manifest, "w", encoding="utf-8") as f:
            for num, _d, dest, _n in picked:
                f.write(f"{num}\t{dest}\n")

    for num, d, dest, n in picked:
        print(f"REC={num}")
        print(f"CHARS={n}")
        print(f"PROMPT={dest}")
        print(f"[星级] {'★' * d.get('星级', 3)}")
        for k in ["场景", "机位角度", "姿势", "服饰", "光线", "氛围", "角色外观"]:
            print(f"[{k}] {d.get(k, '')}")
        print()

    print(f"✅ 抽出 {len(picked)} 张（0 门禁 = 抽到啥出啥 = 完全随机）", file=sys.stderr)
    return 0 if picked else 1


if __name__ == "__main__":
    raise SystemExit(main())
