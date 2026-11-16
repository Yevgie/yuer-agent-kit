#!/usr/bin/env python3
"""整改终检探针 = 体检器查不出的那四类 + 墓碑扫描（反模式 20 / 22 / 23 配套）。

体检器量的是冗余（重复段/履历段/版本号），这个脚本量的是**一致性**：
矛盾条款 / 悬空引用 / 编号断层 / 死规矩 / 活体墓碑。

用法：
    python3 dead_rule_sweep.py <skill_dir> [...]      # 逐份查
    python3 dead_rule_sweep.py --layered <skill_dir>  # 反模式 23：多道合一文件的三层验收
    python3 dead_rule_sweep.py --all                  # 全库扫一遍
"""
import os, re, sys, argparse

# 活体墓碑：留着 = 证明文件知道这件事存在过。这些必须归零。
TOMBSTONES = [
    "已作废", "已被 v", "已被 V", "盖过旧版", "盖过旧假设", "保留备查",
    "保留作为历史", "已废止", "演化时间线", "整改历史", "版本对比",
]

# 悬空引用：X.Y / 见第X部分
REF_SEC = re.compile(r"见\s*(\d+\.\d+)|按\s*(\d+\.\d+)\s*(?:走|执行|部分)")
REF_PART = re.compile(r"第([一二三四五六七八九十]+)部分")

CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
      "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def cn2int(s):
    if s == "十":
        return 10
    return CN.get(s, 0)


def check_skill(path):
    """返回 (问题列表, 统计)。问题列表每项 = (类别, 详情)。"""
    name = os.path.basename(os.path.dirname(path))
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    issues = []

    # ① 墓碑
    for t in TOMBSTONES:
        hits = [(i, l.strip()[:90]) for i, l in enumerate(lines, 1) if t in l]
        if hits:
            for i, snippet in hits:
                issues.append(("墓碑", f"{t!r} @行{i}: {snippet}"))

    # ② 悬空引用（小节号）
    subsections = set(re.findall(r"^#{2,4}\s*(\d+\.\d+)", text, re.M))
    for i, l in enumerate(lines, 1):
        for m in REF_SEC.finditer(l):
            ref = m.group(1) or m.group(2)
            if ref and subsections and ref not in subsections:
                issues.append(("悬空引用", f"引用 {ref} @行{i}，全文无此小节号"))

    # ③ 编号连续性
    nums = [cn2int(x) for x in re.findall(
        r"^#\s+(?:\U0001F534\s*)?第([一二三四五六七八九十]+)部分", text, re.M)]
    if nums:
        expect = list(range(1, max(nums) + 1))
        if nums != expect:
            dup = sorted({n for n in nums if nums.count(n) > 1})
            miss = sorted(set(expect) - set(nums))
            issues.append(("编号断层", f"实际 {nums}，跳号 {miss or '无'}，重复 {dup or '无'}"))

    # ④ 死规矩：frontmatter 里指向的脚本/技能是否还在
    for ref in sorted(set(re.findall(r"`(yuer-[a-z0-9-]+)`", text))):
        if not _skill_exists(ref):
            issues.append(("死规矩", f"指向不存在的技能 {ref}"))

    # ⑤ 可直接复制的实体路径（废弃规则最爱藏的地方）
    for i, l in enumerate(lines, 1):
        if re.search(r"MEDIA:(/vol2|/home|attachment)", l) and "❌" not in l and "|" not in l:
            issues.append(("可复制实体值", f"@行{i}: {l.strip()[:90]}"))

    stats = {"行": len(lines), "字": len(text),
             "部分号": nums, "小节": len(subsections)}
    return issues, stats


def check_layered(path):
    """反模式 23 验收：路由表是否在第一屏 + 共核规矩是否只写一份。"""
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    out = []

    # ① 路由表位置
    route_i = next((i for i, l in enumerate(lines, 1)
                    if re.search(r"路由表|路由速查|唯一路由", l)), None)
    if route_i is None:
        out.append(("缺路由表", "全文找不到路由表/路由速查 = 读者无法判断走哪条道"))
    elif route_i > max(30, len(lines) * 0.15):
        out.append(("路由表埋太深",
                    f"在行 {route_i}/{len(lines)} = {route_i*100//len(lines)}% 处，第一屏看不到"))

    # ② 共核规矩重复次数
    CORE = ["先动作", "exit 0", "MEDIA", "工具调用之前"]
    for c in CORE:
        n = text.count(c)
        if n > 4:
            out.append(("共核疑似复制", f"{c!r} 出现 {n} 次 = 共核可能被各道各写一遍"))
    return out


def _skill_exists(name):
    base = os.path.expanduser("~/.hermes/skills")
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if "bak" not in d and d != ".archive"]
        if os.path.basename(root) == name and "SKILL.md" in files:
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="*")
    ap.add_argument("--layered", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()

    paths = []
    if a.all:
        base = os.path.expanduser("~/.hermes/skills")
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if "bak" not in d and d != ".archive"]
            if "SKILL.md" in files:
                paths.append(os.path.join(root, "SKILL.md"))
    else:
        for d in a.dirs:
            p = d if d.endswith("SKILL.md") else os.path.join(d, "SKILL.md")
            if not os.path.exists(p):
                print(f"❌ 不存在: {p}", file=sys.stderr)
                sys.exit(2)
            paths.append(p)

    if not paths:
        print("用法: dead_rule_sweep.py <skill_dir> [...] | --layered <dir> | --all")
        sys.exit(2)

    total = 0
    for p in paths:
        issues, stats = check_skill(p)
        if a.layered:
            issues += [(c, d) for c, d in check_layered(p)]
        total += len(issues)
        flag = "✅" if not issues else "❌"
        print(f"\n{flag} {os.path.basename(os.path.dirname(p))}  "
              f"{stats['行']}行/{stats['字']}字  部分号={stats['部分号']}")
        for cat, det in issues:
            print(f"     [{cat}] {det}")

    print(f"\n{'='*46}\n合计 {len(paths)} 份，{total} 个问题")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()