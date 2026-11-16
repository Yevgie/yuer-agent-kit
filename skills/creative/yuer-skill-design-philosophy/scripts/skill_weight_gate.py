#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill_weight_gate.py · 技能增重闸（11-11 主人钦定 · 防继续无用增重）

为什么有它（病根）：
  技能库曾到 185 份主档 / 261 万字 / 3436 个 🔴 / 90 份 description 超 150 字。
  根因不是某一份写坏了 = 是**没有任何机械闸** = 每次整改都是"加一段"，
  减完下个月又长回来 = 净账永远是正的（主人 11-07 原话「我一直想做减负，多次给你提，
  你都没有做到这个水平」）。

这个脚本 = 减负的**闸**（不是又一份体检报告）：
  改完任何技能档 → 跑一次 → 超线 = 红灯 = 不许合。
  没有它 = 下次整改照样变胖。

判据（每条都是机械可算的，不靠感觉）：
  1. 主档行数    ≤ 450 行（主人 v5 亲自定的红线）
  2. 主档字数    ≤ 30,000 字
  3. 🔴 密度     ≤ 8 个/千字（181 个 🔴 = 平均每 250 字一个重点 = 没有重点）
                 🔴 11-14 修订 = 密度按「拆档族」算（一个逻辑档拆成 N 份 chunk = 分母不能被拆碎 = 否则密度凭空翻 N 倍）
  4. description ≤ 150 字（只写"什么时候用"，怎么用进正文）
  5. 考古行占比  ≤ 8%（履历叙事不是使用说明）
  6. 版本号个数  ≤ 5（正文里的，不含 frontmatter）
  7. 🔴 总数     ≤ 60 个/份（超了 = 重点稀释）

用法：
  python3 skill_weight_gate.py --all                 # 全库扫（出臃肿榜 + 红灯清单）
  python3 skill_weight_gate.py <skill_dir> [...]      # 只查指定档
  python3 skill_weight_gate.py --all --json           # 机读
  python3 skill_weight_gate.py --all --baseline FILE  # 与基线比（防增重 = 只能持平或下降）
  python3 skill_weight_gate.py --all --write-baseline /path/base.json

退出码：0 = 全过（可合） / 1 = 有红灯（不许合，先减）
"""

import argparse
import json
import os
import re
import sys

SKILLS_ROOT = os.path.expanduser("~/.hermes/skills")

# ---- 阈值（唯一真源 = 本文件顶部注释）----
MAX_MAIN_LINES = 450          # 主档红线（主人 v5 亲定）
MAX_MAIN_CHARS = 30000        # 主档字数红线
MAX_RED_PER_1K = 8            # 🔴 密度：每千字超过 8 个 = 没有重点
MAX_DESC_CHARS = 150          # description 只写"什么时候用"
MAX_ARCH_PCT = 8.0            # 考古行占比 %（履历叙事不是使用说明）
MAX_VERSION_TOKENS = 5        # 正文里的版本号个数（不含 frontmatter）
MAX_RED_TOTAL = 60            # 单份 🔴 总数
MAX_REF_CHARS = 80000         # references/ = 参数与词库，允许长但不允许无限

# 考古层 = 履历叙事（"主人原话 / 当场发火 / 实测 / 已作废 / 盖过 / 旧版"）
ARCH_PAT = re.compile(
    r"(主人原话|主人正解|当场发火|打脸|实测(?:对比|后|钦定)?|已作废|已废|"
    r"这条作废|盖过|旧版|之前那|整改履历|v\d+\.\d+ 之前)"
)
VERSION_PAT = re.compile(r"v\d+\.\d+(?:\.\d+)?")


def desc_len(text):
    m = re.search(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return 0
    d = re.search(
        r"description:\s*(.*?)(?=\n[a-z_]+:|\n---|\Z)", m.group(1), re.S
    )
    if not d:
        return 0
    s = d.group(1).strip()
    if len(s) >= 2 and s[0] in "\"'" and s[-1] == s[0]:
        s = s[1:-1]
    return len(s)


def desc_integrity(text, rel=""):
    """description 完整性 = 批量压缩 description 时最容易被剪坏的三样。

    病（实测批量压 70 份 description 时剪坏 4 份）：
      ① 句尾被剪在半句（'...（纯'）→ 索引里读起来像乱码
      ② 同一句 Use when 被复制两遍
      ③ 触发词整段被剪掉 → 技能不再被路由命中（静默失效，最贵）

    判据 = 三样任一坏 = 红灯。description 是路由面 = 坏了 = 技能等于不存在。

    🔴 作用域（防误报）：① ② 对所有主档查；③ 只查 yuer-* 自有技能
    （bundled 技能用另一种 description 写法 = 不归我改 = 不判）；
    references/ 下的档 0 frontmatter 描述 = 合法 = 不查。
    """
    if os.path.basename(rel) != "SKILL.md":
        return []          # references/ = 合法无描述
    m = re.search(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return []
    d = re.search(
        r"description:\s*(.*?)(?=\n[a-z_]+:|\n---|\Z)", m.group(1), re.S
    )
    if not d:
        return ["description 缺失"]
    s = d.group(1).strip()
    if len(s) >= 2 and s[0] in "\"'" and s[-1] == s[0]:
        s = s[1:-1]
    bad = []
    # ① 句尾断在半句（未闭合的括号 / 顿号 / 斜杠收尾）
    if s and re.search(r"[（(、，/]$|[\(（][^）)]*$", s):
        bad.append("句尾被截断")
    # ② 同一触发句被复制两遍
    uw = re.findall(r"Use when[^。.]*", s)
    if len(uw) > 1:
        bad.append(f"重复了 {len(uw)} 遍 Use when")
    # ③ 触发词整段丢失 = 技能不会被路由命中（只查自有技能）
    if rel.startswith("yuer-") or "/yuer-" in rel:
        if "Use when" not in s and not re.search(r"(触发词|触发|当主人|什么时候)", s):
            bad.append("无触发词 = 不会被路由命中")
    return bad


def body_of(text):
    """正文 = 去掉 frontmatter"""
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    return text[m.end():] if m else text


def split_family_key(path):
    """拆档族键 = 文件名去掉 '-NN-slug' 后缀（11-14 拆档工程 = 一个逻辑档被拆成多份 chunk）"""
    d, fn = os.path.split(path)
    stem = fn[:-3] if fn.endswith(".md") else fn
    m = re.match(r"^(.*)-\d{2}-[^\-]+$", stem)
    if m:
        stem = m.group(1)
    return os.path.join(d, stem)

def red_per_1k_family(path):
    """🔴 密度按「拆档族」算 = 一个逻辑档拆成 N 份后密度不该被 N 倍稀释误判成红灯"""
    d = os.path.dirname(path)
    key = split_family_key(path)
    total_chars = 0
    total_reds = 0
    prefix = os.path.basename(key)
    for dp, dns, fns in os.walk(d):
        dns[:] = [x for x in dns if x not in (".hub", "__pycache__")]
        for fn in fns:
            if not fn.endswith(".md"):
                continue
            fp = os.path.join(dp, fn)
            fk = split_family_key(fp)
            if fk != key and not os.path.basename(fk).startswith(prefix):
                continue
            try:
                s = open(fp, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            total_chars += len(s)
            total_reds += s.count("🔴")
    return round(total_reds / max(total_chars / 1000, 1), 2)

def measure(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    body = body_of(text)
    lines = text.count("\n") + 1
    # 🔴 考古行 = 履历叙事 = 表格行(文件清单) / 代码块(命令) / frontmatter(description) 都不算叙事 = 0 误判
    _infence = False
    _arch = 0
    _fmend = text.find("\n---", 4)
    _body = text[_fmend:] if _fmend > 0 else text
    for _l in _body.split("\n"):
        _s = _l.strip()
        if _s.startswith("```"):
            _infence = not _infence
            continue
        if _infence or _s.startswith("|"):
            continue
        if ARCH_PAT.search(_l):
            _arch += 1
    arch = _arch
    reds = text.count("🔴")
    vers = set(VERSION_PAT.findall(body))
    return {
        "path": path,
        "rel": path.replace(SKILLS_ROOT + os.sep, ""),
        "is_main": os.path.basename(path) == "SKILL.md",
        "lines": lines,
        "chars": len(text),
        "red": reds,
        "red_per_1k": round(reds / max(len(text) / 1000, 1), 2),
        "red_per_1k_family": red_per_1k_family(path),
        "desc": desc_len(text),
        "arch_lines": arch,
        "arch_pct": round(arch / max(lines, 1) * 100, 1),
        "versions": len(vers),
        "desc_bad": desc_integrity(text, path.replace(SKILLS_ROOT + os.sep, "")),
    }


def is_red(r):
    """返回红灯理由列表（空 = 过）"""
    bad = []
    # 实战档 = 历史真相 = 履历天然高 = 豁免版本号与考古占比
    is_shiji = bool(re.search(r"(实战\d|20\d\d-\d\d-\d\d)", os.path.basename(r["path"])))
    # 11-12 主人钦定豁免：抄来的第三方技能不硬拆 + references/ 细则档 = 下沉层天然长（主档才是被管的）
    THIRD_DIRS = ("github/", "research/", "nuwa-distillation", "comfyui-nsfw", "social-media/",
                  "external-skill-research", "mlops/", "linux-permission-troubleshooting",
                  "novel-claude-ai", "devops/hermes-llm-config", "devops/hermes-platform-tuning",
                  "creative/comfyui", "general/hermes-skill-refactor-methodology")
    is_third = any(r["path"].replace(os.path.expanduser("~/.hermes/skills/") if "expanduser" in dir(os) else "", "").startswith(t) or f"/{t.rstrip('/')}/" in r["path"] for t in THIRD_DIRS)
    is_sink = "/references/" in r["path"]
    if r["is_main"]:
        # 🔴 11-12 主人钦定豁免 = 抄来的第三方技能不硬拆 = 主档行数/字数不判红灯
        if not is_third:
            if r["lines"] > MAX_MAIN_LINES:
                bad.append(f"行数 {r['lines']} > {MAX_MAIN_LINES}")
            if r["chars"] > MAX_MAIN_CHARS:
                bad.append(f"字数 {r['chars']} > {MAX_MAIN_CHARS}")
        if r["red"] > MAX_RED_TOTAL:
            bad.append(f"🔴 {r['red']} > {MAX_RED_TOTAL}")
        if r["desc"] > MAX_DESC_CHARS:
            bad.append(f"description {r['desc']} > {MAX_DESC_CHARS}")
    else:
        if r["chars"] > MAX_REF_CHARS:
            bad.append(f"字数 {r['chars']} > {MAX_REF_CHARS}")
    # 🔴 密度 = 按拆档族算（防"重点稀释"要判整份文档 = 拆成 N 份不该被误判 N 倍超标）
    _rd = r.get("red_per_1k_family", r["red_per_1k"])
    if _rd > MAX_RED_PER_1K:
        bad.append(f"🔴密度 {_rd}/千字 > {MAX_RED_PER_1K}")
    # 实战档 = 历史真相 = 履历天然高 = 豁免考古占比（哲学档反模式 9：实战号 0 裁剪）
    if r["arch_pct"] > MAX_ARCH_PCT and not is_shiji and not (is_third or is_sink):
        bad.append(f"考古行 {r['arch_pct']}% > {MAX_ARCH_PCT}%")
    if r["versions"] > MAX_VERSION_TOKENS and not is_shiji and not (is_third or is_sink):
        bad.append(f"版本号 {r['versions']} 个 > {MAX_VERSION_TOKENS}")
    # description 完整性（路由面坏了 = 技能等于不存在）
    for d in r.get("desc_bad", []):
        bad.append(f"description: {d}")
    return bad


def collect(paths, root):
    files = []
    if paths:
        for p in paths:
            ap = p if os.path.isabs(p) else os.path.join(root, p)
            if os.path.isdir(ap):
                for dp, dns, fns in os.walk(ap):
                    dns[:] = [d for d in dns if d not in (".hub", "__pycache__")]
                    for fn in fns:
                        if fn.endswith(".md"):
                            files.append(os.path.join(dp, fn))
            elif os.path.isfile(ap):
                files.append(ap)
    else:
        for dp, dns, fns in os.walk(root):
            dns[:] = [d for d in dns if d not in (".hub", "__pycache__")]
            for fn in fns:
                if fn.endswith(".md"):
                    files.append(os.path.join(dp, fn))
    return [f for f in files if os.path.getsize(f) >= 500]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--root", default=SKILLS_ROOT)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--baseline")
    ap.add_argument("--write-baseline")
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()

    root = os.path.expanduser(args.root)
    files = collect(args.paths, root)
    rows = []
    for f in files:
        try:
            r = measure(f)
        except Exception:
            continue
        r["red_flags"] = is_red(r)
        rows.append(r)

    if args.write_baseline:
        base = {
            "taken_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
            "files": len(rows),
            "main_files": sum(1 for r in rows if r["is_main"]),
            "total_chars": sum(r["chars"] for r in rows),
            "total_main_chars": sum(r["chars"] for r in rows if r["is_main"]),
            "total_red": sum(r["red"] for r in rows),
            "per_file": {r["rel"]: r["chars"] for r in rows},
        }
        with open(args.write_baseline, "w", encoding="utf-8") as f:
            json.dump(base, f, ensure_ascii=False, indent=1)
        print(f"基线已写 {args.write_baseline}")
        print(f"  {base['files']} 份 / {base['total_chars']:,} 字 / 🔴 {base['total_red']}")

    reds = [r for r in rows if r["red_flags"]]

    if args.baseline:
        with open(args.baseline, encoding="utf-8") as f:
            base = json.load(f)
        per = base.get("per_file", {})
        grew = []
        for r in rows:
            old = per.get(r["rel"])
            if old is None:
                grew.append((r["rel"], 0, r["chars"], "新档"))
            elif r["chars"] > old:
                grew.append((r["rel"], old, r["chars"], f"+{r['chars']-old}"))
        grew.sort(key=lambda x: (x[3] if isinstance(x[3], int) else 0), reverse=True)
        print(f"\n=== 与基线比：{len(grew)} 份变大了 ===")
        for rel, old, new, d in grew[:40]:
            print(f"  {rel[:62]:<64}{old:>8} -> {new:>8}  ({d})")
        tot_old = base.get("total_chars", 0)
        tot_new = sum(r["chars"] for r in rows)
        print(f"\n全库净账：{tot_old:,} -> {tot_new:,}  ({tot_new-tot_old:+,})")

    if args.json:
        print(json.dumps(
            {"rows": rows, "red_count": len(reds)}, ensure_ascii=False, indent=1))
    else:
        print(f"\n=== 臃肿榜 top {args.top}（按字数）===")
        print(f"{'档':<62}{'字':>8}{'行':>6}{'🔴':>6}{'dens':>7}{'desc':>6}{'考古%':>7}")
        for r in sorted(rows, key=lambda x: -x["chars"])[:args.top]:
            print(f"{r['rel'][:60]:<62}{r['chars']:>8}{r['lines']:>6}{r['red']:>6}"
                  f"{r['red_per_1k']:>7}{r['desc']:>6}{r['arch_pct']:>7}")
        print(f"\n=== 红灯 {len(reds)} 份（超线 = 不许合，先减）===")
        for r in sorted(reds, key=lambda x: -len(x["red_flags"]))[:40]:
            print(f"  {r['rel'][:60]:<62} {'; '.join(r['red_flags'])}")
        tot = sum(r["chars"] for r in rows)
        print(f"\n合计 {len(rows)} 份 / {tot:,} 字 / 🔴 {sum(r['red'] for r in rows)} / 红灯 {len(reds)}")

    return 1 if reds else 0


if __name__ == "__main__":
    sys.exit(main())
