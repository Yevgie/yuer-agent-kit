#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量门禁 = 一批 N 份 prompt 一次性跑完三道门禁 + 汇总 FAIL 行。

用法:
  /usr/bin/python3 batch_gate_check.py <batch_tag>          # /tmp/prompt_<tag>_n*.txt
  /usr/bin/python3 batch_gate_check.py --files a.txt b.txt  # 指定文件

机制 = 三道门禁逐份跑（count_prompt_chars / check_prompt_subject / check_outfit_lock），
       每份单独抓 stdout + exit code，任一 FAIL = 该份不通过。
退出码: 0 = 全过；1 = 有不通过（打印每份的 FAIL 行）；2 = 找不到 prompt 文件。

为什么需要它 = 一批 5 份手敲三条命令 = 15 次调用 + 漏看一份 = 带着一份 FAIL 开跑 = 白跑一轮。
门禁必须全批过再开跑（见 SKILL.md 7ah2）。
"""
import glob
import os
import subprocess
import sys

SCRIPTS = "~/.hermes/skills/creative/yuer-image/scripts"
PY = "/usr/bin/python3"


def run(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 99, "TIMEOUT"


def check(path):
    res = {"file": os.path.basename(path), "chars": 0, "sub": 0, "fit": 0, "fails": [], "warns": []}
    rc, out = run([PY, os.path.join(SCRIPTS, "count_prompt_chars.py"), path])
    res["chars_rc"] = rc
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("字符数"):
            import re as _re
            m = _re.search(r"字符数:\s*(\d+)", s)
            if m:
                res["chars"] = int(m.group(1))
        if s.startswith("FAIL"):
            res["fails"].append(s)
    rc, out = run([PY, os.path.join(SCRIPTS, "check_prompt_subject.py"), path])
    res["sub"] = rc
    if rc != 0:
        res["fails"].append("主体门禁 exit=%s" % rc)
    rc, out = run([PY, os.path.join(SCRIPTS, "check_outfit_lock.py"), path])
    res["fit"] = rc
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("FAIL"):
            res["fails"].append(s)
        elif s.startswith("WARN"):
            res["warns"].append(s)
    return res


def main():
    args = sys.argv[1:]
    if args and args[0] == "--files":
        files = args[1:]
    elif args:
        pat = "/tmp/prompt_%s_n*.txt" % args[0]
        files = sorted(glob.glob(pat))
    else:
        print("用法: batch_gate_check.py <batch_tag> | --files <f...>")
        return 2
    if not files:
        print("找不到 prompt 文件 = 0 出图（先跑 build 脚本生成）")
        return 2

    bad = 0
    for f in files:
        r = check(f)
        ok = not r["fails"]
        if not ok:
            bad += 1
        print("%s %-28s chars=%-5s sub=%s fit=%s" % (
            "PASS" if ok else "FAIL", r["file"], r["chars"], r["sub"], r["fit"]))
        for x in r["fails"]:
            print("      ! %s" % x)
        for x in r["warns"]:
            print("      ~ %s" % x)
    print("\n%d/%d 通过" % (len(files) - bad, len(files)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
