#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验「抽到的卡 = 原样喂」= 两条证据 = 0 改写

证据 ① 链路零查档：抽卡链路脚本里**0 处**引用提示词档
        （出图速查卡 / 身材档 / 脸部硬锚 / 九维体系 / prompt-writer）
证据 ② 落盘逐字一致：抽到的牌落盘后 = 池内【完整 Prompt】原文 = 逐字 diff = 0 处差异

用法
----
    /usr/bin/python3 ~/.hermes/skills/creative/yuer-character-roster/scripts/verify_card_verbatim.py
    /usr/bin/python3 .../verify_card_verbatim.py --prompt /tmp/ka_<REC>_prompt.txt

退出码 0 = 两条证据都过；1 = 有一条不成立（= 有人在链路里动手了）。
"""
import argparse
import difflib
import glob
import os
import re
import subprocess

SK = os.path.expanduser("~/.hermes/skills")
PICK = os.path.join(SK, "creative/yuer-character-roster/scripts/ka_batch_pick.py")
POOL_DIR = "/path/to/promptlib"

CHAIN = [
    SK + "/creative/yuer-character-roster/scripts/yuer_card_fast.sh",
    SK + "/creative/yuer-character-roster/scripts/ka_batch_pick.py",
    SK + "/creative/yuer-character-roster/scripts/ka_pick_clean.py",
    SK + "/creative/yuer-character-roster/scripts/pick_ka_prompt.py",
    SK + "/creative/yuer-image/scripts/yuer_ka_pai_zhi_chu.py",
]
DOC_KEYWORDS = ["速查卡", "出图速查卡", "语儿专属硬锚", "身材特征档",
                "身材描述实测表", "yuer-prompt-writer", "九维体系"]


def evidence_chain() -> bool:
    """证据 ① = 链路脚本 0 处引用提示词档。"""
    bad = 0
    for f in CHAIN:
        if not os.path.exists(f):
            print(f"  (缺) {os.path.basename(f)}")
            continue
        t = open(f, encoding="utf-8", errors="replace").read()
        hits = [k for k in DOC_KEYWORDS if k in t]
        if hits:
            bad += 1
            print(f"  ✗ {os.path.basename(f)} 引用了 {hits}")
        else:
            print(f"  ✓ {os.path.basename(f)} 0 处引用提示词档")
    return bad == 0


def evidence_verbatim(prompt_file: str) -> bool:
    """证据 ② = 落盘 = 池内原文 = 逐字 diff 0 处。"""
    if not prompt_file:
        man = f"/tmp/ka_verify_{os.getpid()}.tsv"
        subprocess.run(["/usr/bin/python3", PICK, "1", "--manifest", man],
                       capture_output=True, text=True)
        raw = open(man, encoding="utf-8").read().strip()
        prompt_file = raw.split("\t")[1].strip()
    out = open(prompt_file, encoding="utf-8").read().strip()
    head = out[:80]
    for pool in sorted(glob.glob(os.path.join(POOL_DIR, "*.txt"))):
        txt = open(pool, encoding="utf-8", errors="replace").read()
        i = txt.find(head)
        if i < 0:
            continue
        seg = txt[i:i + len(out) + 80]
        diffs = [d for d in difflib.SequenceMatcher(None, seg[:len(out)], out)
                 .get_opcodes() if d[0] != "equal"]
        print(f"  池 = {os.path.basename(pool)} | 落盘 = {len(out)} 字 | "
              f"逐字差异 = {len(diffs)} 处")
        for d in diffs[:6]:
            print(f"    {d[0]:8} 池={seg[d[1]:d[2]][:60]!r} → 落盘={out[d[3]:d[4]][:60]!r}")
        return len(diffs) == 0
    print("  ✗ 池里定位不到这张牌的原文")
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", default="", help="已落盘的 prompt 文件（不给 = 自己抽一张）")
    args = ap.parse_args()

    print("证据 ① 链路零查档：")
    ok1 = evidence_chain()
    print("证据 ② 落盘逐字一致：")
    ok2 = evidence_verbatim(args.prompt)

    if ok1 and ok2:
        print("\n✅ 两条证据都过 = 抽到的卡就是原样喂 = 0 查档 0 核对 0 重写")
        return 0
    print("\n❌ 有证据不成立 = 链路上有人动手了")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
