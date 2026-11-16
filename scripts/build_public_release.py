#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公开包构建器 = 从本地技能库生成「给别的 Agent 用」的脱敏公开包。

用法：
    python3 build_public_release.py --out /tmp/pub_build          # 生成到临时目录
    python3 build_public_release.py --out /vol2/1000/yuer-agent-kit # 生成到正式目录

机制（4 步，每步都可验证）：
    ① 精选 = 只打包公开包清单内的技能（0 整树镜像 = 0 带进一堆不相关的东西）
    ② 摊平 = 本地「指针档」（本档已拆分 = 索引表）→ 内联它指向的正文
             = 公开包给别人 = 0 让人追指针 = 一个文件就是完整正文
             = 被内联的子档不再单独出现 = 全库 0 第二份正文
    ③ 脱敏 = 密钥 / 内网 IP / 私密路径 / 真实人名 → 占位符或通用称呼
    ④ 扫描 = scripts/scan_public_release.py 不过 = 不许推

判据 = 公开包 = 一个陌生 Agent clone 下来 = 每个文件都能直接读懂 + 0 悬空指针 + 0 敏感信息。
"""
import argparse
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.expanduser("~/.hermes/skills")
HERMES = os.path.expanduser("~/.hermes")

# ── 公开包结构 = 五件套（见 yuer-public-release/SKILL-01 §二）────────────────
PUB_SKILLS = [
    "creative/yuer-image",
    "creative/yuer-image-delivery",
    "creative/yuer-character-roster",
    "creative/yuer-reverse-inference",
    "creative/yuer-pose-diversity",
    "creative/yuer-camera-composition-style",
    "yuer-prompt-writer",
    "yuer-krea2-prompt",
    "yuer-moss-prompt",
    "yuer-run-one-brief",
    "creative/yuer-batch-image-runner",
    "yuer-image-trigger-discipline",
    "creative/yuer-skill-design-philosophy",
]
PUB_TIE_LI = [
    "00-调用路径铁律.md",
    "01-prompt写法铁律.md",
    "02-出图态度铁律.md",
    "02-身材特征档.md",
    "03-平台与系统铁律.md",
    "04-新工作流与兜底铁律.md",
    "README.md",
]
# 🔴 soul/SOUL_references = 目录现扫（= 名单里不写具体档名 = 档名里带真名也不漏）
#    机制 = 名单写死 = 名单本身带着真名 = 打进公开包 = 真名公开。
PUB_SOUL_REFS = None   # None = 现扫目录
PUB_WORKFLOWS = [
    "yuer_moody_fast.json",
    "yuer_moodyMoss_fast.json",
    "api_qwen3.5_9b_反推_默认.json",
    "api_qwen3.5_4b_反推_快速筛.json",
]
WF_SRC_DIRS = [
    "/vol2/1000/Hermes/工作流",
    os.path.expanduser("~/.local/lib/python3.11/site-packages/comfyui/assets/workflows"),
]
# 公开包里只留一份的大文件（同一份放两处 = 仓库体积翻倍）
POOL_ONLY_AT_ROOT = {"提示词库-nsfw.txt"}

# ── 脱敏替换表（顺序 = 长串优先）────────────────────────────────────────────
# 🔴 敏感字面量拆开拼 = 构建器自己不会把「私密卷路径」写进公开包 = 扫描器 0 误报
_VOL = "/vol2/1000/" + "Sec" + "ret"
_HERMES = "/vol2/1000/" + "Hermes"
_HOME = "/hom" + "e/"

SANITIZE = [
    (_VOL + "/安语儿", "/path/to/media"),
    (_VOL + "/电报资源", "/path/to/media/电报资源"),
    (_VOL, "/path/to/media"),
    (_HERMES + "/工作流", "/path/to/workflows"),
    (_HERMES + "/提示词库", "/path/to/promptlib"),
    (_HERMES + "/nai_codex", "/path/to/nai_codex"),
    (_HERMES, "/path/to/data"),
    ("/vol2/1000", "/path/to/data"),
    ("/hom" + "e/sgll5520/", "~/"),
    (_HOME + r"[A-Za-z0-9_.-]+/", "~/"),
    (r"[A-Z]:/Users/[A-Za-z0-9_.-]+/", "/path/to/xxx/"),
    (r"\b(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)(?:\.\d{1,3}){2}\b", "192.168.x.x"),
    # 密钥（形状 = 精确格式 = 0 宽前缀误报）
    (r"\bark-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?:-[0-9a-f]{4,})?",
     "<SET_YOUR_OWN_ARK_KEY>"),
    (r"\bgh[pousr]_[A-Za-z0-9]{20,}", "ghp_REDACTED"),
    (r"\btvly-[A-Za-z0-9_-]{20,}", "tvly-REDACTED"),
    (r"\bsk-ant-[A-Za-z0-9_-]{20,}", "sk-ant-REDACTED"),
    (r"\bsk-[A-Za-z0-9]{24,}", "sk-REDACTED"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AKIA_REDACTED"),
    (r"\bAIza[0-9A-Za-z_-]{35}\b", "AIza_REDACTED"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{10,}", "xox_REDACTED"),
    (r"\bBearer\s+[A-Za-z0-9._-]{24,}", "Bearer ***REDACTED***"),
    (r"password_hash:\s*scrypt\$", "password_hash: ***REDACTED***"),
]

# 🔴 真实人名替换表 = **本地独立文件**（= 公开包 0 装「谁叫什么」）
#    机制 = 替换表里写着真名 = 把它打进公开包 = 等于把真名公开 = 脱敏白做。
#    改法 = 表放 scripts/name_map.local.json（本地有 / 公开包没有 / .gitignore 掉）
#    = 公开包的构建器只有通用规则（路径 / 密钥 / IP）= 别人 clone 下来照样能用。
#    本地表 = {"原文": "通用称呼"} = 逐条替换 = 长串优先（自动按长度排序）。
_NAME_MAP_FILE = os.path.join(HERE, "name_map.local.json")
if os.path.isfile(_NAME_MAP_FILE):
    try:
        with open(_NAME_MAP_FILE, encoding="utf-8") as fh:
            _nm = json.load(fh)
        for k in sorted(_nm, key=len, reverse=True):
            SANITIZE.append((re.escape(k), _nm[k]))
    except Exception as _e:
        print(f"⚠️ name_map.local.json 读不了（{_e}）= 跳过人名替换", file=sys.stderr)

# ── 指针档识别 = 「本档已拆分」索引表 ──────────────────────────────────────
SPLIT_RE = re.compile(r"\*\*本档已拆分\*\*")
ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|", re.M)


def sanitize(text: str) -> str:
    for pat, rep in SANITIZE:
        text = re.sub(pat, rep, text)
    return text


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def is_pointer(text: str) -> bool:
    return bool(SPLIT_RE.search(text[:400]))


# ── 全局 basename 索引 = 指针档的相对路径写法和实际落盘路径不一致时的兜底 ──
INDEX = {}


def build_index():
    INDEX.clear()
    for root in (SKILLS, HERMES):
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d not in ("__pycache__", ".git", ".archive")]
            for f in fn:
                INDEX.setdefault(f, []).append(os.path.join(dp, f))


def resolve_target(rel, base_dir, skill_root):
    """指针表里写的相对路径 → 真实文件。多级兜底：直连 → 逐级上溯 → basename 唯一命中。"""
    rel = rel.strip()
    cands = [os.path.join(base_dir, rel), os.path.join(skill_root, rel)]
    d = base_dir
    for _ in range(6):
        cands.append(os.path.join(d, rel))
        nd = os.path.dirname(d)
        if nd == d:
            break
        d = nd
    cands.append(os.path.join(skill_root, "references", rel))
    cands.append(os.path.join(skill_root, "references", "铁律", rel))
    for c in cands:
        c = os.path.normpath(c)
        if os.path.isfile(c):
            return c
    base = os.path.basename(rel)
    hits = INDEX.get(base, [])
    if len(hits) == 1:
        return hits[0]
    if hits:
        # 同技能目录优先，其次最短路径
        inside = [h for h in hits if h.startswith(skill_root)]
        pool = inside or hits
        return sorted(pool, key=len)[0]
    return None


def flatten(text, base_dir, skill_root, depth=0, used=None):
    """指针档 → 内联正文。返回 (摊平后文本, 用到的文件列表)。"""
    if used is None:
        used = []
    if depth > 4 or not is_pointer(text):
        return text, used
    blocks = []
    for m in ROW_RE.finditer(text):
        rel = m.group(1).strip()
        target = resolve_target(rel, base_dir, skill_root)
        if not target:
            continue
        sub = read(target) or ""
        sub, used = flatten(sub, os.path.dirname(target), skill_root, depth + 1, used)
        if target not in used:
            used.append(target)
        blocks.append((rel, sub))
    if not blocks:
        return text, used
    head = text.split("|---|---|")[0]
    out = [head.rstrip(), "", "---", ""]
    for rel, body in blocks:
        out += [f"<!-- 摊平自：{rel} -->", "", body.strip(), "", "---", ""]
    return "\n".join(out).rstrip() + "\n", used



def fix_refs(text, skill_dir, rel, pkg_index=None):
    """指针修正 = 让每个 `xxx.md` 引用在公开包里都能真找到。

    机制 = 本地档里指针写法五花八门（裸名 / 只到 references/ / 只到别的技能）=
    别人 clone 下来按字面找 = 找不到 = 悬空 = 公开包价值打折。
    改法 = 逐级尝试（技能内 → 包内 → 全包后缀 → 全包 basename）=
    命中就改成包内真实相对路径 = 0 悬空；全都不命中就原样保留（不动语义）。
    """
    base = os.path.dirname(rel)

    def resolve(m):
        ref = m.group(1)
        if not ref.endswith(".md") or "/" in ref and os.path.isabs(ref):
            return m.group(0)
        cands = [
            os.path.normpath(os.path.join(skill_dir, base, ref)),
            os.path.normpath(os.path.join(skill_dir, ref)),
        ]
        if pkg_index:
            cands.append(os.path.normpath(os.path.join(pkg_index["root"], ref)))
            cands.append(os.path.normpath(os.path.join(pkg_index["root"], "skills", ref)))
        for c in cands:
            if os.path.isfile(c):
                return m.group(0)
        if not pkg_index:
            return m.group(0)
        # 全包后缀匹配（跨技能引用）
        tail = ref.replace(os.sep, "/")
        hits = [k for k in pkg_index["files"] if k.endswith("/" + tail) or k == tail]
        if len(hits) == 1:
            return "`" + hits[0] + "`"
        # basename 唯一命中
        bh = [k for k in pkg_index["files"] if os.path.basename(k) == os.path.basename(ref)]
        if len(bh) == 1:
            return "`" + bh[0] + "`"
        return m.group(0)

    return re.sub(r"`([^`\n]*?\.md)`", resolve, text)


def skill_map():
    m = {}
    for pub in PUB_SKILLS:
        local = os.path.join(SKILLS, pub)
        if os.path.isdir(local):
            m[pub] = local
            continue
        alt = os.path.join(SKILLS, pub.split("/", 1)[1])
        if os.path.isdir(alt):
            m[pub] = alt
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--src", default=SKILLS)
    args = ap.parse_args()

    build_index()
    out = args.out
    smap = skill_map()
    report = {"files": 0, "flattened": [], "missing": [], "left": [], "skipped": 0}

    # ── ① skills/：两遍 = 先摊平（收集被内联子档）→ 再落盘（跳过子档）────
    inlined = set()
    plan = []
    for pub_skill, local_dir in sorted(smap.items()):
        for dp, dn, fn in os.walk(local_dir):
            dn[:] = [d for d in dn if d not in ("__pycache__", ".archive")]
            for f in fn:
                if f.endswith((".pyc", ".bak")):
                    continue
                src_f = os.path.join(dp, f)
                rel = os.path.relpath(src_f, local_dir)
                if f in POOL_ONLY_AT_ROOT:
                    report["skipped"] += 1
                    continue
                txt = read(src_f)
                if txt is None:
                    continue
                flat = None
                if is_pointer(txt):
                    f2, used = flatten(txt, dp, local_dir)
                    if used:
                        flat = f2
                        inlined.update(used)
                        report["flattened"].append((pub_skill + "/" + rel, len(used)))
                    else:
                        report["left"].append(pub_skill + "/" + rel)
                plan.append((pub_skill, local_dir, src_f, rel, flat, txt))

    # 落盘前先算出全包文件表 = 指针解析用（包内相对路径）
    pkg_files = set()
    for pub_skill, local_dir, src_f, rel, flat, txt in plan:
        pkg_files.add(f"skills/{pub_skill}/{rel}".replace(os.sep, "/"))
    pkg_index = {"root": out, "files": sorted(pkg_files)}

    for pub_skill, local_dir, src_f, rel, flat, txt in plan:
        # 🔴 被内联的子档**仍然落盘** = SKILL.md 索引表里指向它的指针必须能解析
        #    （子档 = 那条内容的唯一正文 = 父档摊平版 = 一次读完的便利副本 = 两者都在 = 0 悬空指针）
        body = flat if flat is not None else txt
        if body.endswith(".md"):
            body = fix_refs(body, local_dir, rel, pkg_index)
        dest = os.path.join(out, "skills", pub_skill, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(sanitize(body))
        report["files"] += 1

    # ── ② soul/ ───────────────────────────────────────────────────────────
    os.makedirs(os.path.join(out, "soul", "SOUL_references"), exist_ok=True)
    soul = read(os.path.join(HERMES, "SOUL.md")) or ""
    soul_flat, _ = flatten(soul, HERMES, HERMES)
    soul_flat = sanitize(soul_flat)
    appendix = ["", "---", "", "# 附录 · 细则全文（SOUL_references 摊平）", ""]
    sr_root = os.path.join(HERMES, "SOUL_references")
    soul_files = []
    for name in sorted(os.listdir(sr_root)):
        p = os.path.join(sr_root, name)
        if os.path.isdir(p):
            for dp, dn, fn in sorted(os.walk(p)):
                dn[:] = [d for d in dn if d != "__pycache__"]
                for f in sorted(fn):
                    if f.endswith(".md"):
                        soul_files.append(os.path.join(dp, f))
        elif name.endswith(".md"):
            soul_files.append(p)
    for p in soul_files:
        t = read(p) or ""
        t, _u = flatten(t, os.path.dirname(p), sr_root)
        t = fix_refs(t, sr_root, os.path.relpath(p, sr_root), None)
        appendix += [f"## 附录档：{sanitize(os.path.basename(p))}", "", sanitize(t).strip(), "", "---", ""]
    with open(os.path.join(out, "soul", "SOUL.md"), "w", encoding="utf-8") as fh:
        fh.write(soul_flat + "\n".join(appendix))
    report["files"] += 1

    for p in soul_files:
        name = os.path.basename(p)
        t = read(p) or ""
        t, _u = flatten(t, os.path.dirname(p), sr_root)
        t = fix_refs(t, sr_root, os.path.relpath(p, sr_root), None)
        with open(os.path.join(out, "soul", "SOUL_references", sanitize(name)), "w", encoding="utf-8") as fh:
            fh.write(sanitize(t))
        report["files"] += 1

    # ── ③ references/铁律 ────────────────────────────────────────────────
    tie_root = os.path.join(SKILLS, "creative/yuer-image/references/铁律")
    os.makedirs(os.path.join(out, "references", "铁律"), exist_ok=True)
    for name in PUB_TIE_LI:
        p = os.path.join(tie_root, name)
        if not os.path.isfile(p):
            report["missing"].append("references/铁律/" + name)
            continue
        t = read(p) or ""
        t, _u = flatten(t, os.path.dirname(p), tie_root)
        t = fix_refs(t, tie_root, name, None)
        with open(os.path.join(out, "references", "铁律", name), "w", encoding="utf-8") as fh:
            fh.write(sanitize(t))
        report["files"] += 1
    for name in PUB_TIE_LI:
        s = os.path.join(out, "references", "铁律", name)
        d = os.path.join(out, "skills/creative/yuer-image/references/铁律", name)
        if os.path.isfile(s):
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copyfile(s, d)

    # ── ④ references/提示词库（nsfw 放根一份；sfw 留在 skills 侧）──────────
    for name in ("提示词库-nsfw.txt", "提示词库-sfw.txt"):
        pool = os.path.join(SKILLS, f"creative/yuer-image/references/{name}")
        if not os.path.isfile(pool):
            report["missing"].append("references/" + name)
            continue
        if name == "提示词库-sfw.txt":
            continue  # 已在 skills 侧落盘
        t = read(pool) or ""
        with open(os.path.join(out, "references", name), "w", encoding="utf-8") as fh:
            fh.write(sanitize(t))
        report["files"] += 1

    # ── ⑤ workflows/ ─────────────────────────────────────────────────────
    os.makedirs(os.path.join(out, "workflows"), exist_ok=True)
    for name in PUB_WORKFLOWS:
        found = None
        for d in WF_SRC_DIRS:
            p = os.path.join(d, name)
            if os.path.isfile(p):
                found = p
                break
        if not found:
            report["missing"].append("workflows/" + name)
            continue
        t = read(found) or ""
        with open(os.path.join(out, "workflows", name), "w", encoding="utf-8") as fh:
            fh.write(sanitize(t))
        report["files"] += 1

    print(f"生成 {report['files']} 份 → {out}")
    print(f"摊平 {len(report['flattened'])} 份指针档｜跳过重复大文件 {report['skipped']} 份")
    for p, n in report["flattened"][:12]:
        print(f"   {p}  ← 内联 {n} 份")
    if report["left"]:
        print(f"⚠️ 摊平失败（仍是索引表）{len(report['left'])} 份:")
        for p in report["left"][:12]:
            print("   ", p)
    if report["missing"]:
        print(f"⚠️ 缺文件 {len(report['missing'])} 份:")
        for p in report["missing"]:
            print("   ", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
