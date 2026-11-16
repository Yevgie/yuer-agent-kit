#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽 N 张【干净牌】= 完全随机抽 + 抽到废牌自动再抽（0 去重 0 排除号）

用法
----
    /usr/bin/python3 ~/.hermes/skills/creative/yuer-character-roster/scripts/ka_pick_clean.py 5
    /usr/bin/python3 .../ka_pick_clean.py 5 --manifest /tmp/ka_clean.tsv

三类废牌 = 换牌再抽（**0 排除号** = 不靠排除号绕 = 抽到啥出啥原则只在牌能用时成立）：
    ① 非人主体（拟人猫 / 动物）= 脸锁 LoRA 只对人脸生效 = 套上去出猫
    ② 乱码（UTF-8 被当 Latin-1 又编了一遍，如 `cafÃ©`）= 底模当语义吃 = 画面漂
    ③ 视频规格牌（`[Shot 1]` / `<Subject 1>` / `<Picture 1>` / `overall_soundscape`）= 抽到的是分镜脚本不是画面

stdout = 每张一张卡（REC / CHARS / PROMPT）+ stderr 给 manifest 路径与收下计数。
manifest 两列 = 记录号<TAB>/tmp/ka_<记录号>_prompt.txt = 直接当出图脚本参数。
"""
import argparse
import os
import re
import subprocess
import sys

PICK = os.path.expanduser(
    "~/.hermes/skills/creative/yuer-character-roster/scripts/ka_batch_pick.py"
)
PY = "/usr/bin/python3"

FEMALE = re.compile(r"\b(1girl|1woman|girl|woman|female|she |she,|her )", re.I)
MOJI = re.compile(r"Ã|Â|â€|ï¿½")
VIDEO = re.compile(r"\[Shot \d+\]|<Subject \d+>|<Picture \d+>|overall_soundscape|<\d+ seconds>")
ANTHRO = re.compile(r"anthropomorphic", re.I)


def why_bad(text: str):
    """返回废牌原因列表 = 空列表 = 这张能用。"""
    bad = []
    if not FEMALE.search(text):
        bad.append("no-female-lead")
    if ANTHRO.search(text):
        bad.append("anthropomorphic")
    if MOJI.search(text):
        bad.append("mojibake")
    if VIDEO.search(text):
        bad.append("video-spec")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("count", type=int, nargs="?", default=5)
    ap.add_argument("--pool", default="nsfw", help="nsfw / sfw / all")
    ap.add_argument("--manifest", default="/tmp/ka_clean.tsv")
    ap.add_argument("--max-attempts", type=int, default=60)
    args = ap.parse_args()

    one = f"/tmp/ka_clean_one_{os.getpid()}.tsv"
    rows = []
    for attempt in range(1, args.max_attempts + 1):
        subprocess.run([PY, PICK, "1", "--pool", args.pool, "--manifest", one],
                       capture_output=True, text=True)
        try:
            raw = open(one, encoding="utf-8").read().strip()
            rec, pf = raw.split("\t")[0].strip(), raw.split("\t")[1].strip()
        except Exception:
            print(f"try{attempt} manifest 空 → retry", flush=True)
            continue
        text = open(pf, encoding="utf-8", errors="replace").read()
        bad = why_bad(text)
        if bad:
            print(f"try{attempt} REC={rec} 废牌({','.join(bad)}) → 再抽一张", flush=True)
            continue
        rows.append((rec, pf, len(text)))
        print(f"try{attempt} REC={rec} ✓ {len(text)} 字 → 收下", flush=True)
        if len(rows) >= args.count:
            break

    with open(args.manifest, "w", encoding="utf-8") as f:
        for rec, pf, _n in rows:
            f.write(f"{rec}\t{pf}\n")

    for rec, pf, n in rows:
        print(f"REC={rec}")
        print(f"CHARS={n}")
        print(f"PROMPT={pf}")

    print(f"MANIFEST={args.manifest}", file=sys.stderr)
    if len(rows) < args.count:
        print(f"⚠️ 只抽到 {len(rows)}/{args.count} 张干净牌（{args.max_attempts} 次内）",
              file=sys.stderr)
        return 1
    print(f"✅ 干净牌 {len(rows)}/{args.count} 张 = 完全随机 = 0 去重 0 排除号",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
