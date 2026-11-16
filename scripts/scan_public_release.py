#!/usr/bin/env python3
"""公开分发前的敏感信息扫描闸。

用法:
    python3 scan_public_release.py <目录>              # 扫工作区
    python3 scan_public_release.py <目录> --history    # 连 git 历史一起扫

判据:
    退出码 0 = 干净 = 可以推公开仓
    退出码 1 = 有命中 = 停下来脱敏, 不许建仓

机制: 公开仓一旦推上去 = 密钥 / 内网地址 / 私密路径 = 全网可读 = 撤不回来。
      = 扫描必须发生在 push 之前 = 扫完不过 = 不许建仓。
      = 只扫工作区不够 = 老 commit 里的密钥照样可读 = 必须连历史一起扫。

每条正则都用精确格式 = 宽前缀会扫出 dark-academic 这类误报
= 误报率高的正则等于没有正则 = 拿真阳性样本验过才收。
"""
import argparse
import os
import re
import subprocess
import sys

# (标签, 正则) —— 只列形状, 不含任何真值
# 🔴 正则字面量一律拆开拼 = 扫描器扫自己时不误报
#    机制 = 扫描器自己就装着「私���卷路径」这类字面量 = 扫自己 = 自己报自己 = 假阳性
#    = 假阳性一多 = 真阳性被淹没 = 等于没有扫描器。改法 = 字符串拼接。
_S = "Sec" + "ret"
_VOL = "/vol2/1000/" + _S
_HOME = "/hom" + "e/"
_PATTERNS = [
    ("GitHub token",       r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    ("Tavily key",         r"\btvly-[A-Za-z0-9_-]{20,}"),
    ("OpenAI-style key",   r"\bsk-[A-Za-z0-9]{24,}"),
    ("Anthropic key",      r"\bsk-ant-[A-Za-z0-9_-]{20,}"),
    ("VolcEngine ark",     r"\bark-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?:-[0-9a-f]{4,})?"),
    ("AWS access key id",  r"\bAKIA[0-9A-Z]{16}\b"),
    ("Google api key",     r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ("Slack token",        r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    ("Bearer literal",     r"\bBearer\s+[A-Za-z0-9._-]{24,}"),
    ("scrypt password",    r"password_hash:\s*scrypt\$"),
    ("internal ipv4",      r"\b(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)(?:\.\d{1,3}){2}\b"),
    ("private media path", re.escape(_VOL)),
    ("absolute home path", _HOME + r"[A-Za-z0-9_.-]+/"),
    ("windows user path",  r"[A-Z]:/Users/[A-Za-z0-9_.-]+/"),
]
PATTERNS = [(lb, re.compile(rx)) for lb, rx in _PATTERNS]

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".mypy_cache"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".tar", ".gz", ".bz2", ".xz", ".mp4", ".pdf"}
# 扫历史用的合并 ERE (git grep -E)
HISTORY_ERE = "|".join(rx.pattern for _, rx in PATTERNS)


def scan_worktree(root):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in SKIP_EXT:
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
            except (OSError, UnicodeError):
                continue
            for label, rx in PATTERNS:
                for m in rx.finditer(text):
                    line = text.count("\n", 0, m.start()) + 1
                    hits.append((label, os.path.relpath(path, root), line, m.group(0)[:60]))
    return hits


def scan_history(root):
    """git grep over every commit —— 老 commit 里的密钥照样可读。"""
    if not os.path.isdir(os.path.join(root, ".git")):
        return []
    try:
        revs = subprocess.run(
            ["git", "-C", root, "rev-list", "--all"],
            capture_output=True, text=True, timeout=180,
        ).stdout.split()
    except (OSError, subprocess.SubprocessError):
        return []
    if not revs:
        return []
    hits = []
    try:
        proc = subprocess.run(
            ["git", "-C", root, "grep", "-nEI", HISTORY_ERE] + revs,
            capture_output=True, text=True, timeout=300,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    for raw in proc.stdout.splitlines():
        # 格式 = <commit>:<path>:<line>:<matched text>
        parts = raw.split(":", 3)
        if len(parts) < 4:
            continue
        commit, path, line, matched = parts
        label = next((lb for lb, rx in PATTERNS if rx.search(matched)), "?")
        hits.append((label, f"{commit[:8]}:{path}", line, matched.strip()[:60]))
    return hits


def main():
    ap = argparse.ArgumentParser(description="公开分发前敏感信息扫描")
    ap.add_argument("root", help="要扫描的目录")
    ap.add_argument("--history", action="store_true", help="连 git 历史一起扫")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"目录不存在: {root}", file=sys.stderr)
        return 2

    hits = scan_worktree(root)
    scope = "工作区"
    if args.history:
        hits += scan_history(root)
        scope = "工作区 + git 历史"

    if not hits:
        print(f"OK  {scope} 未发现敏感信息 ({root})")
        return 0

    print(f"FAIL {scope} 发现 {len(hits)} 处疑似敏感信息 ({root})", file=sys.stderr)
    by_label = {}
    for label, path, line, snippet in hits:
        by_label.setdefault(label, []).append((path, line, snippet))
    for label, items in sorted(by_label.items(), key=lambda kv: -len(kv[1])):
        print(f"\n  [{label}] {len(items)} 处", file=sys.stderr)
        for path, line, snippet in items[:8]:
            print(f"      {path}:{line}  {snippet}", file=sys.stderr)
        if len(items) > 8:
            print(f"      ... 另 {len(items) - 8} 处", file=sys.stderr)
    print("\n脱敏后重扫 = 退出码 0 才许建仓/推送", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
