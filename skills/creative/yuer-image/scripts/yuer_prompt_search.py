#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""yuer_prompt_search.py · 提示词资产池检索器（出图前先查库）

为什么要有它（主人钦定）：
    「关于提示词，你可以利用你的仓库哦。我们入库了很多提示词，不是吗？
      这个很重要的资产，你要高效的使用。」

现状问题 = 库里有 1241 条带成品提示词的角色档案 + 1000+ 份我自己出过的 prompt 文件，
但出图链路没有检索入口 = 每张图都从零手写 = 库里的现成货白白浪费 = 出图风格漂移。

本脚本 = 出图前的「先查库」一步：
    1. 扫两个资产源：提示词池（提示词库-nsfw.txt）+ 自出 prompt 文件（Secret/安语儿/*.prompt.*）
    2. 关键词加权打分（可多词、可带权重）
    3. 命中 Top N → 打印记录号/来源/摘要 → 供语儿「照抄 / 换造型 / 借光位机位」

用法：
    python3 yuer_prompt_search.py "street lamp,rope"                 # 逗号分隔 = 与关系
    python3 yuer_prompt_search.py "rope:10,barefoot:4,street lamp:8"  # 词:权重（词在前）
    python3 yuer_prompt_search.py "trench coat" --top 8
    python3 yuer_prompt_search.py "夜 街" --lib-only                  # 只查参考库
    python3 yuer_prompt_search.py "rope" --dump 229                   # 看某条完整成品提示词
    python3 yuer_prompt_search.py "rope" --stats                      # 资产池体检
    python3 yuer_prompt_search.py "rope" --save                       # TOP1 落盘 /tmp

退出码：0 = 有命中；1 = 无命中。
"""
import argparse
import glob
import os
import re
import sys

# 🔴 11-09 22:40 提示词资产池 = 一把尺子两种口味 = 都是一行一条完整英文提示词
REF = os.path.expanduser(
    "~/.hermes/skills/creative/yuer-image/references/提示词库-nsfw.txt"
)
REF_SFW = os.path.expanduser(
    "~/.hermes/skills/creative/yuer-image/references/提示词库-sfw.txt"
)
POOL_ALIASES = {
    "主": "main", "main": "nsfw", "nsfw": "nsfw",
    "sfw": "sfw", "小红书": "sfw", "xhs": "sfw", "ins": "sfw", "日常": "sfw",
    "all": "all", "全部": "all", "both": "all",
}
OWN_GLOBS = [
    "/path/to/media/*.prompt.txt",
    "/path/to/media/*.prompt.md",
]
OUT_DIR = "/tmp"

# 参考库字段别名（与 pick_roster_record.py 同一套，防解析漂移）
FIELD_ALIASES = {
    "场景": ["场景", "场景环境", "Scene"],
    "机位角度": ["机位角度", "机位", "镜头角度", "Camera"],
    "姿势": ["姿势", "人物姿势", "动作姿势", "Pose"],
    "服饰": ["服饰", "服饰细节", "服装", "服装细节", "Wardrobe"],
    "光线": ["光线", "光线特点", "灯光", "Lighting"],
    "氛围": ["氛围", "整体氛围", "情绪氛围", "Mood"],
    "角色外观": ["角色外观", "角色壳", "Character Shell"],
    "骚姿势标注": ["骚姿势标注", "Visual Hook"],
}
FULL_PROMPT_ALIASES = ["Full Prompt", "成品提示词", "Ready Prompt", "Final Prompt"]

_TABLE_RE = r"\|\s*\**(?:🆕\s*)?{name}\**\s*\|\s*(.+?)\s*\|\s*\n"
_BOLD_RE = r"\*\*{alias}\*\*\s*[:：]\s*(.+?)(?=\n)"
_DASH_RE = r"[-*]\s*\*?{name}\*?\s*[:：]\s*(.+?)(?=\n)"


def _clean(s):
    return s.replace("**", "").replace("`", "").replace("\r", "").strip().strip("|").strip()


def cell(block, name):
    """表格 / 粗体 / 横杠 三格式依次尝试。"""
    aliases = FIELD_ALIASES.get(name, [name])
    for alias in aliases:
        m = re.search(_TABLE_RE.format(name=re.escape(alias)), block, re.S)
        if m:
            return _clean(m.group(1))
    for alias in aliases:
        m = re.search(_BOLD_RE.format(alias=re.escape(alias)), block)
        if m:
            return _clean(m.group(1))
    for alias in aliases:
        m = re.search(_DASH_RE.format(name=re.escape(alias)), block)
        if m:
            return _clean(m.group(1))
    return ""


def full_prompt_of(block):
    for alias in FULL_PROMPT_ALIASES:
        v = cell(block, alias)
        if v:
            return v
    return ""


# 🔴 11-09 22:20 新池没有分字段 = 从整条提示词反解 6 件套（供加权检索）
_DERIVE_PATS = [
    ("机位角度", re.compile(r"\b(shot|camera|angle|lens|composition|framing|close-?up|full shot|full-length|portrait|viewpoint)\b", re.I)),
    ("光线", re.compile(r"\b(light|lighting|daylight|lamp|neon|backlit|shadow|highlight|glow|ambient|illuminat\w*|dusk|twilight|night)\b", re.I)),
    ("服饰", re.compile(r"\b(wear|wears|wearing|dressed|outfit|robe|dress|gown|shirt|skirt|lingerie|clad|uniform|sock|shoe|boot|jacket|coat)\b", re.I)),
    ("姿势", re.compile(r"\b(sitting|standing|lying|kneeling|leaning|holding|seated|resting|crouching|reclining|perched|straddl\w+|squat\w+)\b", re.I)),
    ("场景", re.compile(r"\b(background|room|hall|street|indoor|outdoor|space|setting|environment|corridor|balcony|studio)\b", re.I)),
]


def derive_fields_from_prompt(fp):
    if not fp:
        return {}
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", fp) if len(s.strip()) > 15]
    if not sents:
        return {}
    buckets = {f: [] for f, _ in _DERIVE_PATS}
    buckets["氛围"] = []
    used = set()
    for st in sents:
        for f, pat in _DERIVE_PATS:
            if pat.search(st):
                buckets[f].append(st)
                used.add(st)
                break
    rest = [s for s in sents if s not in used]
    buckets["氛围"] = rest[-3:] + buckets["氛围"]
    out = {f: " ".join(buckets.get(f, []))[:400].strip() for f in
           ("场景", "机位角度", "姿势", "服饰", "光线", "氛围")}
    out["角色外观"] = out["服饰"][:120] or out["场景"][:120]
    return out

def load_reflib(pool="main"):
    """🔴 11-09 22:40 提示词资产池 = 一行一条 `N|<整段英文提示词>`
    → [{id, src, txt, shell, scene, cam, pose, wd, light}]
    字段无独立存储 = 从整条提示词反解（供加权检索用）
    🔴 pool = main(NSFW) / sfw(小红书日常) / all(两个都进)"""
    key = POOL_ALIASES.get(str(pool).lower(), "nsfw")
    if key == "all":
        pairs = [(REF, "NSFW库"), (REF_SFW, "SFW库")]
    elif key == "nsfw":
        pairs = [(REF, "NSFW库")]
    else:
        pairs = [(REF_SFW, "SFW库")]
    out = []
    for path, src in pairs:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            content = f.read()
        for ln in content.split("\n"):
            m = re.match(r"^(\d+)\|(.+)$", ln.strip())
            if not m:
                continue
            fp = m.group(2).strip()
            if not fp:
                continue
            d = derive_fields_from_prompt(fp) if derive_fields_from_prompt else {}
            out.append({
                "id": m.group(1), "src": src, "txt": fp,
                "shell": d.get("角色外观", ""), "scene": d.get("场景", ""),
                "cam": d.get("机位角度", ""), "pose": d.get("姿势", ""),
                "wd": d.get("服饰", ""), "light": d.get("光线", ""),
            })
    return out


def load_own():
    """我自己出过的 prompt 文件 → 同结构（只有 txt + id）。"""
    out = []
    for pat in OWN_GLOBS:
        for path in glob.glob(pat):
            try:
                with open(path, encoding="utf-8") as f:
                    t = f.read()
            except OSError:
                continue
            if len(t.strip()) < 300:
                continue
            name = os.path.basename(path)
            for suf in (".prompt.txt", ".prompt.md"):
                if name.endswith(suf):
                    name = name[: -len(suf)]
                    break
            out.append({"id": name, "src": "自出", "txt": t,
                        "shell": "", "scene": "", "cam": "", "pose": "",
                        "wd": "", "light": ""})
    return out


def parse_kwarg(spec):
    """'rope:10,barefoot:4' → [('rope',10),('barefoot',4)]；无权重 = 权重 1。
    🔴 词在前权重在后 = rpartition(':') 必须先切词再切权重，
    否则 'rope:10' 会把权重当成词、词当成权重 = 全库 0 命中。"""
    kws = []
    for chunk in re.split(r"[,，;；]", spec):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" in chunk:
            k, _, w = chunk.rpartition(":")
            try:
                kws.append((k.strip().lower(), int(w)))
                continue
            except ValueError:
                pass
        kws.append((chunk.lower(), 1))
    return kws


def score(rec, kws):
    """加权命中分。多次出现小幅加权（不线性爆炸）+ 命中词数占检索词数的比例，
    避免「一个词命中 20 次」压过「五个词各命中一次」。"""
    blob = " ".join([
        rec["txt"], rec.get("shell", ""), rec.get("scene", ""),
        rec.get("cam", ""), rec.get("pose", ""), rec.get("wd", ""), rec.get("light", ""),
    ]).lower()
    total = 0
    raw = 0
    hit = []
    n_hit = 0
    for k, w in kws:
        n = blob.count(k)
        if n:
            n_hit += 1
            raw += n
            total += w * (1 + min(n - 1, 3) * 0.2)
            hit.append(f"{k}×{n}")
    if n_hit:
        total *= 1 + 0.5 * (n_hit / len(kws) - 1)
    return total, raw, hit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--lib-only", action="store_true")
    ap.add_argument("--own-only", action="store_true")
    ap.add_argument("--dump", help="打印某条记录（库=记录号 / 自出=文件名）的完整成品提示词")
    ap.add_argument("--stats", action="store_true", help="只做资产池体检")
    ap.add_argument("--save", action="store_true", help="把 Top1 成品提示词落盘 /tmp")
    ap.add_argument("--pool", default="nsfw",
                    help="搜哪个池：nsfw(1119) / sfw(2418) / all(3537)")
    args = ap.parse_args()

    lib = load_reflib(args.pool)
    own = [] if args.lib_only else load_own()
    pool = lib + own if not args.own_only else own

    if args.stats:
        lens = sorted(len(r["txt"]) for r in pool) or [0]
        print(f"资产池合计 {len(pool)} 条（参考库 {len(lib)} + 自出 {len(own)}）")
        print(f"成品提示词长度 min/median/max = {lens[0]}/{lens[len(lens)//2]}/{lens[-1]}")
        return 0

    if args.dump:
        for r in pool:
            if r["id"] == args.dump:
                print(r["txt"])
                return 0
        print(f"没找到 {args.dump}", file=sys.stderr)
        return 1

    if not args.query:
        print("给关键词。例：rope:10,barefoot:4,street lamp:8", file=sys.stderr)
        return 1

    kws = parse_kwarg(args.query)
    scored = []
    for r in pool:
        s, raw, hit = score(r, kws)
        if s > 0:
            scored.append((s, raw, r, hit))
    scored.sort(key=lambda x: (-x[0], -x[1], x[2]["id"]))

    if not scored:
        print("库里没有命中这些词。换个词组再试。", file=sys.stderr)
        return 1

    print(f"命中 {len(scored)} 条 / 池 {len(pool)} 条 · 关键词 {[k for k,_ in kws]}\n")
    for s, raw, r, hit in scored[: args.top]:
        head = re.sub(r"\s+", " ", r["txt"])[:110]
        print(f"[{s:5.1f}] ({r['src']}) {r['id']}  命中 {'/'.join(hit)}")
        print(f"          {head}")

    if args.save:
        top = scored[0]
        dest = os.path.join(OUT_DIR, f"pool_top_{top[2]['src']}_{top[2]['id']}.txt")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(top[2]["txt"])
        print(f"\nTOP1 已落盘: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
