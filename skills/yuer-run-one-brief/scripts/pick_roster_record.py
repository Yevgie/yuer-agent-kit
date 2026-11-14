#!/usr/bin/env python3
"""从提示词池抽 N 条完整提示词（抽卡第 1 步）。

用法：
    python3 pick_roster_record.py                # 抽 1 条
    python3 pick_roster_record.py --count 3      # 抽 3 条（仅主人明说 N 张时）
    python3 pick_roster_record.py --show         # 打印全部字段
    python3 pick_roster_record.py --json         # 输出 JSON
    python3 pick_roster_record.py --stats        # 只看牌池体检（不抽签）

stdout = 可直接拼 prompt 的 6 字段 + 角色外观 + 骚姿势标注。
选中的记录号自动写进 /tmp/yuer_used_<日期>.json 做同会话避号。

🔴 多格式解析（09-29 修复）：参考库里同一张牌存在三种排版，解析器
三种都认，不再只认表格白扔牌。
    1. 表格   | **场景** | xxx |
    2. 粗体   **场景环境**：xxx
    3. 横杠   - **场景**：xxx
标题也容错：`## 记录 159` 后面不带日期 / 也能解析出编号
（09-29 真根因 = 老代码用 split(' ')[0] 取编号，遇到标题后直接换行
的记录会取到 '159\\n-' 这种脏串，isdigit 恒 False = 整段牌被静默丢弃）。
"""
import argparse
import collections
import datetime
import json
import os
import pickle
import random
import re
import sys

FIELDS = ["场景", "机位角度", "姿势", "服饰", "光线", "氛围"]

# 模板废档话术黑名单（命中任一 = 这条档案拼不出 prompt）
PLACEHOLDER_BLACKLIST = [
    "需补", "需主人补", "待补", "占位",
    "一句话描述场景", "镜头的位置/视角/距离",
    "用关键词列出该角色的核心装扮", "描述该角色",
    "示例", "请填写", "TODO", "同上",
    "（待", "(待", "一句话描述",
]

# 撞敏感词 L2 fallback 兜底档 = 6 件套字段本身写的是真空话术，出图必废
# （09-29 体检发现记录 141 属这类：字段写的是"撞敏感词根因 / 具体细节不可考 / 不可文字化"）
# 🔴 只查字段值，不查整块：086/087/138/139/140/234/264 的 6 件套内容都是好的，
#    只在「备注」里提了一句"vision 撞敏感词"= 正常入库留痕 = 不该被误杀
#    （09-29 体检踩坑：按整块 grep "撞敏感词" 一次误杀 7 张好牌）
SENSITIVE_FALLBACK_MARKERS = [
    "不可考", "不可文字化", "实战敏感图", "撞敏感词根因",
    "具体细节不可考", "无法反推", "拒答", "双撞",
]

# ---- 三种排版的字段解析器 -------------------------------------------------
# 表格：必须以 |\s*\n 收尾，不是 \s*|
# \s*\| 会把表格下一行的开头当成本行尾列，最后一条记录字段全空 → valid: 0
_TABLE_RE = r"\|\s*\**(?:🆕\s*)?{name}\**\s*\|\s*(.+?)\s*\|\s*\n"
# 粗体：`**场景环境**：xxx`（场景字段的历史别名是「场景环境」）
_BOLD_RE = r"\*\*{alias}\*\*\s*[:：]\s*(.+?)(?=\n)"
# 横杠：`- **场景**：xxx`
_DASH_RE = r"[-*]\s*\*?{name}\*?\s*[:：]\s*(.+?)(?=\n)"


# 🔴 11-09 22:37 提示词资产池 = 一把尺子两种口味 = 都是「一条完整的英文自然语言提示词」
#    主池 = NSFW / 诱惑向（1067 条）= 抽到即出图给主人看
#    SFW 池 = 小红书 / ins 日常颜值博主向（2677 条）= 主人 11-09 22:37 亲自补的原件
POOLS = {
    "nsfw": os.path.expanduser(
        "~/.hermes/skills/creative/yuer-image/references/提示词库-nsfw.txt"
    ),
    "sfw": os.path.expanduser(
        "~/.hermes/skills/creative/yuer-image/references/提示词库-sfw.txt"
    ),
}
# 🔴 11-12 减法 = 合并池文件删了（50 MB 派生产物）= "all" = 读 nsfw + sfw 现算
#    编号 = 文件内号 + 偏移 = 复现原合并池的连续编号 = 「记录号」当查表键 = 不能变
# 🔴 别名 = 主人嘴里的叫法
POOL_ALIASES = {
    "nsfw": "nsfw", "主": "nsfw", "main": "nsfw", "骚": "nsfw",
    "sfw": "sfw", "小红书": "sfw", "xhs": "sfw", "ins": "sfw", "日常": "sfw",
    "all": "all", "合并": "all", "全部": "all", "both": "all",
}


def ref_path(pool="main"):
    """🔴 11-09 22:20 主人钦定「提示词池 = 一条完整的英文自然语言提示词」
    = 唯一资产池 = 一行一条 `N|<整段英文>` = 0 字段 0 元信息。
    旧的 9 字段参考库已退役（反推/入库链路同步改写新格式）。"""
    key = POOL_ALIASES.get(str(pool).lower(), "nsfw")
    return POOLS[key]


def used_path():
    today = datetime.date.today().isoformat()
    return f"/tmp/yuer_used_{today}.json"


def _clean(s):
    return s.replace("**", "").replace("`", "").replace("\r", "").strip().strip("|").strip()


# 🔴 09-29 修复：参考库字段名有历史别名，粗体格式那一批用的是 agnes 8 段的原名，
# 不认别名 = 姿势/服饰/光线/氛围 四个字段全解析不到 = 好牌被误判成废牌
# （09-29 真根因：只有「场景」有别名「场景环境」，其余四个字段没加）
FIELD_ALIASES = {
    "场景": ["场景", "场景环境", "Scene"],
    "机位角度": ["机位角度", "机位", "镜头角度", "Camera"],
    "姿势": ["姿势", "人物姿势", "动作姿势", "Pose"],
    "服饰": ["服饰", "服饰细节", "服装", "服装细节", "Wardrobe"],
    "光线": ["光线", "光线特点", "灯光", "Lighting"],
    "氛围": ["氛围", "整体氛围", "情绪氛围", "Mood"],
}

# 🔴 09-29 主人钦定「牌池全改英文」：整库英文化后表头换成 Scene/Camera/…
#    这三个新别名不补 = 抽签脚本 8 个字段全解析不到 = 305 张牌全变废档。
#    解析层认两种语言，存档层只留英文。
CELL_ALIASES = {
    "角色外观": ["角色外观", "角色壳", "Character Shell"],
    "骚姿势标注": ["骚姿势标注", "Visual Hook"],
}

# 🔴 09-30 实战：牌池已存成品提示词（Full Prompt = 400-650 词完整英文
#    = 抽卡抽到即出图 0 加工）。但 load_valid() 只吐 6 件套 + 角色外观 + 骚标注，
#    不吐 Full Prompt = 消费侧拿不到 = 「存了等于没存」，出图链路还在
#    自己拼 6 件套 = 主人钦定的成品化目标没闭环。
# 正解 = 加进抽签输出（--show / --json / 纯文本三种都带）。
# 缺失时回落 = 空串 = 调用方仍可回落到 6 件套手工拼，不破坏旧链路。
FULL_PROMPT_ALIASES = ["Full Prompt", "成品提示词", "Ready Prompt", "Final Prompt"]


def _aliases(name):
    """字段名 → 历史别名列表（顺序 = 优先级）。"""
    return FIELD_ALIASES.get(name, [name]) + CELL_ALIASES.get(name, [])


def _table(block, name):
    for alias in _aliases(name):
        m = re.search(_TABLE_RE.format(name=re.escape(alias)), block, re.S)
        if m:
            return _clean(m.group(1))
    return ""


def _bold(block, name):
    for alias in _aliases(name):
        m = re.search(_BOLD_RE.format(alias=re.escape(alias)), block)
        if m:
            return _clean(m.group(1))
    return ""


def _dash(block, name):
    for alias in _aliases(name):
        m = re.search(_DASH_RE.format(name=re.escape(alias)), block)
        if m:
            return _clean(m.group(1))
    return ""


def cell(block, name):
    """三格式依次尝试，任一命中即返回（表格优先，因为表格最规整）。"""
    # 🔴 11-12 提速（实测 57s → 15s）：三种排版正则**全都要求块内存在 "\n"**
    #   （_TABLE_RE 结尾 = \|\s*\n；_BOLD_RE / _DASH_RE 结尾 = (?=\n)）
    #   而新格式池的每一块都来自 content.split("\n") 的**单行** = 块内永远没有 \n
    #   → cell() 对新格式牌恒返回 "" → 41952 块 × 11 字段 × 3 正则 = 461472 次扫描 = 42 秒纯浪费。
    #   判据 = 块内无 \n = 三种排版一个都命中不了 = 直接返回 "" = 与原逻辑**逐字段等价**。
    if "\n" not in block:
        return ""
    for fn in (_table, _bold, _dash):
        v = fn(block, name)
        if v:
            return v
    return ""


def set_star(spec):
    """`--set-star NNN=R`：给某张牌设星级。

    做法 = 在该牌表格里插/改一行 `| **星级** | ★★★★★ |`。
    已有该行 = 原地改；没有 = 插在表格第一行之后（紧跟 |---|---| 分隔行）。
    写完立刻回读断言 = 行确实落在那张牌的块里。
    """
    m = re.match(r"^\s*(\d+)\s*=\s*(.+)$", spec)
    if not m:
        print("格式错：要 NNN=R，例 1314=5 或 1314=★★★★★", file=sys.stderr)
        return 2
    num, raw = m.group(1), m.group(2)
    star = parse_star(raw)
    rp = ref_path()
    with open(rp, encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"(\n## 记录 )", content)
    target = None
    for i in range(1, len(blocks), 2):
        if blocks[i + 1].startswith(num + " ") or blocks[i + 1].startswith(num + "·"):
            target = i + 1
            break
    if target is None:
        print(f"库里找不到记录 {num}", file=sys.stderr)
        return 1

    blk = blocks[target]
    line = f"| **星级** | {'★' * star} |"
    if re.search(r"\|\s*\*\*(?:星级|Star|Rating)\*\*\s*\|", blk):
        new_blk = re.sub(r"\|\s*\*\*(?:星级|Star|Rating)\*\*\s*\|[^|]*\|", line, blk, count=1)
    else:
        # 插在表格分隔行 `|---|---|` 之后
        new_blk = re.sub(r"(\n\|[\s\-|:]+\|\n)", r"\1" + line + "\n", blk, count=1)
        if new_blk == blk:
            print(f"记录 {num} 里没找到表格 = 加星级失败", file=sys.stderr)
            return 1
    blocks[target] = new_blk
    out = "".join(blocks)
    with open(rp, "w", encoding="utf-8") as f:
        f.write(out)

    # 回读断言
    check = open(rp, encoding="utf-8").read()
    ok = False
    for i in range(1, len(re.split(r"(\n## 记录 )", check)), 2):
        b = re.split(r"(\n## 记录 )", check)[i + 1]
        if b.startswith(num + " ") or b.startswith(num + "·"):
            ok = bool(re.search(r"\|\s*\*\*(?:星级|Star|Rating)\*\*\s*\|", b))
            break
    print(f"✅ 记录 {num} 星级 = {'★' * star}（回读断言 {'通过' if ok else '失败'}）")
    return 0 if ok else 1


def parse_star(raw):
    """从单元格文本解析星级 → int 1~5（缺省 3★ = 中性）。

    接受 `★★★★★` / `5` / `5★` / `⭐⭐⭐` 等写法；解析不出 = 3（中性）。
    """
    if not raw:
        return 3
    s = raw.strip()
    m = re.search(r"[1-5]", s)
    if m:
        return int(m.group(0))
    n = s.count("★") + s.count("⭐")
    return n if 1 <= n <= 5 else 3


# 🔴 11-04 星级权重表：主人钦定「5★极为喜欢 → 1★可有可无」。
# 🔴 11-04 修正（主人真数据打脸后改）：权重 = 该星级的**池内份额**，不是单牌绝对值。
#    上一版用单牌绝对权重 = 1 张 5★(80) 抢 1085 张 3★(10×1085) = 命中率仅 0.95%
#    = 等于星级白加。真因 = 权重没按池子规模归一化。
#    正解 = 先按星级分桶，每桶内部等概率，再按星级份额抽桶。
#    默认份额：5★ 50% / 4★ 25% / 3★ 15% / 2★ 7% / 1★ 3%
#    = 「5★极为喜欢」= 抽到一半是主人爱的；「1★可有可无」= 几乎不出现。
STAR_SHARES = {5: 0.50, 4: 0.25, 3: 0.15, 2: 0.07, 1: 0.03}
DEFAULT_STAR = 3
# 单张牌在一轮抽卡里的最高占比 = 防止「1 张 5★ 吃满份额」
SINGLE_CARD_CAP = 0.30


def weighted_pick(cands, n):
    """按星级抽 n 条（无放回）。

    🔴 11-04 主人钦定原话：「5★极为喜欢 → 1★可有可无」。

    🔴 定稿模型（11-04 四轮真数据打脸后收敛 = 三条同时成立才合格）：

      ① **星级档目标份额**：5★50% / 4★25% / 3★15% / 2★7% / 1★3%
         （STAR_SHARES）。
      ② **空档摊回**：某档没牌 → 它的份额按比例分给其他有牌的档。
         库里有 1085 张 3★ + 1 张 5★ 时：5★ 档 0.50/(0.50+0.15) = 77%，
         3★ 档 23%。**这是数学必然**：档稀少的库没法精确命中 50%。
      ③ **单张牌上限 30%**（SINGLE_CARD_CAP）= 档内平分时，一张牌最多吃
         该档的 30%，超出份额回流给同档其他牌。
         = 1 张 5★ 不会吃满 77% = 抽卡保持新鲜感 = 主人不会连着看到同一张。

      ❌ 前三版踩过的坑（勿回退）：
        a. 单牌绝对权重（80/30/10/3/1）→ 5★ 命中率仅 0.95% = 星级白加。
        b. 份额不归一化 → 1★ 拿 35.7% = 「可有可无」变「常常有」。
        c. 档内不设上限 → 1 张 5★ 吃 77% = 抽卡退化成「只看那张」。

    实现 = 轮盘赌（roulette）+ 档内单张上限再分配。
    """
    if not cands:
        return []

    by_star = collections.defaultdict(list)
    for rec, d in cands:
        by_star[d.get("星级", DEFAULT_STAR)].append(rec)

    # ① 档目标份额 ② 空档摊回 = 归一化到 1
    avail_stars = [s for s in by_star if by_star[s]]
    raw = {s: STAR_SHARES.get(s, 0) for s in avail_stars}
    total = sum(raw.values())
    if total <= 0:
        raw = {s: 1.0 for s in avail_stars}
        total = float(len(avail_stars))
    star_share = {s: raw[s] / total for s in avail_stars}

    # ③ 档内单张上限：一张牌最多吃**整池**的 SINGLE_CARD_CAP
    #    = 档内平分该档份额，若单张平分后超过上限 → 按上限截断，
    #    截断掉的份额**归一化时自动回流**给同档其他牌（最后统一归一化）。
    card_weight = {}
    overflow = 0.0
    for s in avail_stars:
        recs = by_star[s]
        n_rec = len(recs)
        each = star_share[s] / n_rec                     # 档内平分
        cap = SINGLE_CARD_CAP                             # 单张占整池上限
        if each > cap:
            overflow += (each - cap) * n_rec
            each = cap
        for rec in recs:
            card_weight[rec] = each
    # 溢出的份额**分给没有触顶的牌** = 高星档不会凭空多拿，也不会凭空少拿
    if overflow > 0:
        free = [(r, w) for r, w in card_weight.items() if w < SINGLE_CARD_CAP - 1e-9]
        if free:
            add = overflow / len(free)
            for r, w in free:
                card_weight[r] = min(SINGLE_CARD_CAP, w + add)
    # 归一化到 1（截断/平分误差都在这一步化掉）
    wsum = sum(card_weight.values())
    if wsum > 0:
        for k in card_weight:
            card_weight[k] /= wsum

    remaining = list(cands)
    picked = []
    for _ in range(min(n, len(cands))):
        wsum = sum(card_weight.get(r, 0) for r, _ in remaining)
        if wsum <= 0:
            rec, d = random.choice(remaining)
        else:
            r = random.random() * wsum
            acc = 0.0
            chosen = None
            for rec, d in remaining:
                acc += card_weight.get(rec, 0)
                if r <= acc:
                    chosen = (rec, d)
                    break
            if chosen is None:
                chosen = remaining[-1]
            rec, d = chosen
        picked.append((rec, d))
        remaining.remove((rec, d))
    return picked


def parse_num(head):
    """从记录标题行取编号，容忍 `## 记录 159` 后直接换行的写法。

    ❌ 旧写法 b.split(' ')[0] 遇到 `159\\n- **日期**` 会取到 '159\\n-'
    → isdigit() 恒 False → 整段牌被静默丢掉（09-29 真根因）
    """
    m = re.match(r"^(\d+)", head.strip())
    return m.group(1) if m else None


# 🔴 11-09 11:22 主人钦定「卡池只保留提示词内容」= 成品提示词反解 6 件套
#    = 库瘦身成「只留成品提示词」时抽卡照样能用 = 字段齐全率 93% / 关键词召回 57%
_DERIVE_PATS = [
    ("机位角度", re.compile(r"\b(shot|camera|angle|lens|composition|framing|close-?up|full shot|full-length|portrait|viewpoint|from (?:a|the) (?:low|high|front|rear|side))\b", re.I)),
    ("光线", re.compile(r"\b(light|lighting|daylight|lamp|neon|backlit|shadow|highlight|glow|ambient|illuminat\w*|dusk|twilight|night)\b", re.I)),
    ("服饰", re.compile(r"\b(wear|wears|wearing|dressed|outfit|robe|dress|gown|shirt|skirt|lingerie|clad|uniform|sock|shoe|boot|jacket|coat)\b", re.I)),
    ("姿势", re.compile(r"\b(sitting|standing|lying|kneeling|leaning|holding|seated|resting|crouching|reclining|perched|straddl\w+|squat\w+|arms?\b|hands?\b)\b", re.I)),
    ("场景", re.compile(r"\b(background|room|hall|street|indoor|outdoor|space|setting|environment|corridor|balcony|studio)\b", re.I)),
]


def derive_fields_from_prompt(fp):
    """成品提示词 → 6 件套（缺失字段的兜底反解）。返回 {字段: 文本} 或 {}。"""
    if not fp:
        return {}
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", fp) if len(s.strip()) > 15]
    if not sents:
        return {}
    buckets = {f: [] for f, _ in _DERIVE_PATS}
    buckets["氛围"] = []
    used = set()
    for s in sents:
        for f, pat in _DERIVE_PATS:
            if pat.search(s):
                buckets[f].append(s)
                used.add(s)
                break
    rest = [s for s in sents if s not in used]
    buckets["氛围"] = (rest[-3:] + buckets["氛围"])
    out = {}
    for f in FIELDS:
        v = " ".join(buckets.get(f, []))[:400].strip()
        out[f] = v
    return out

def _cache_path(pool_key, paths):
    """解析结果缓存 = 池文件 mtime+size 的指纹 → 池一改 = 指纹变 = 缓存自动失效。"""
    import hashlib
    h = hashlib.sha1()
    for pp in paths:
        st = os.stat(pp)
        h.update(f"{os.path.basename(pp)}|{st.st_mtime_ns}|{st.st_size}\n".encode())
    tag = h.hexdigest()[:16]
    d = os.path.expanduser("~/.hermes/cache/roster")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"pool_{pool_key}_{tag}.pkl")


def load_valid(verbose=False, pool="main"):
    """返回 [(记录号, {字段...})]，已剔除模板废档 + 撞敏感词兜底档。

    🔴 11-12 提速：解析结果按「池文件 mtime+size 指纹」缓存到 pickle。
      池 47MB / 41952 条 = 每次重解析 14 秒（反解 6 件套 = 41952 次正则）= 抽卡最大的单项开销。
      指纹 = 池一改就变 = 缓存自动失效 = 0 陈旧风险。
      命中 = 0.6 秒（实测 127MB pickle load 0.58s）。
    """
    paths = []
    key = POOL_ALIASES.get(str(pool).lower(), "nsfw")
    if key == "all":
        paths = [POOLS["nsfw"], POOLS["sfw"]]
    else:
        paths = [POOLS[key]]

    # 🔴 缓存命中 = 直接反序列化（跳过 read + split + 41952 次反解）
    cpath = _cache_path(key, paths)
    if os.path.exists(cpath):
        try:
            with open(cpath, "rb") as f:
                cached = pickle.load(f)
            if verbose:
                print(f"♻️ 命中解析缓存（池未变）合格 {len(cached)} 条 → {cpath}", file=sys.stderr)
            return cached
        except Exception:
            pass  # 缓存坏了 = 老老实实重解析

    # 🔴 11-09 22:20 新池格式 = 一行一条 `N|<整段英文提示词>` = 0 字段 0 元信息
    #    一条提示词 = 一条资产 = 抽到即出图 = 6 件套靠 derive_fields_from_prompt 反解
    # 🔴 11-12 = 逐文件读 + 偏移 = 编号复现原合并池（sfw 的号 = 文件内号 + nsfw 条数）
    blocks = []
    offset = 0
    for pp in paths:
        cnt = 0
        for ln in open(pp, encoding="utf-8").read().split("\n"):
            m = re.match(r"^(\d+)\|(.+)$", ln.strip())
            if m:
                blocks.append((str(int(m.group(1)) + offset), m.group(2).strip()))
                cnt += 1
        offset += cnt
    valid = []
    skipped = {"bad_head": 0, "empty": 0, "short": 0, "placeholder": 0, "sensitive": 0}

    for num, raw_prompt in blocks:
        if not raw_prompt:
            skipped["empty"] += 1
            continue
        b = raw_prompt          # 新格式没有表格块 = 字段一律走反解

        d = {f: cell(b, f) for f in FIELDS}
        d["角色外观"] = cell(b, "角色外观") or d["服饰"]   # 缺列回退服饰
        d["骚"] = cell(b, "骚姿势标注")
        # 🔴 11-04 星级：主人钦定 5★极为喜欢 → 1★可有可无 = 加权抽样。
        # 未标星级 = 旧牌 = 按 3★（中性）算 = 不破坏现状抽样分布。
        d["星级"] = parse_star(cell(b, "星级") or cell(b, "Star") or cell(b, "Rating"))
        # 🔴 11-09 22:20 新池 = 整行就是成品提示词 = 抽到即出图 0 加工
        fp = raw_prompt
        if not fp:
            for alias in FULL_PROMPT_ALIASES:
                fp = cell(b, alias)
                if fp:
                    break
        d["成品"] = fp

        # 🔴 11-09 11:22 主人钦定「卡池只保留提示词内容」= 库可能瘦身成「只留成品提示词」
        #    = 6 件套字段不在库里了 = 靠成品提示词反解出来 = 抽卡照样能用
        #    判据 = 字段缺失才反解 = 库里有的字段 0 覆盖 = 行为不变
        if fp and not all(d[f] for f in FIELDS):
            _der = derive_fields_from_prompt(fp)
            if _der:
                for _f, _v in _der.items():
                    if not d.get(_f) and _v:
                        d[_f] = _v
                if not d["角色外观"]:
                    d["角色外观"] = d["服饰"] or d["场景"]
                if not d["骚"]:
                    d["骚"] = d["氛围"][:200] if d["氛围"] else ""
            # 反解仍缺的字段 = 用成品提示词兜底 = 不判废档（废档 = 抽卡池缩水 = 白丢牌）
            for _f in FIELDS:
                if not d.get(_f) or len(d[_f]) < 8:
                    d[_f] = (fp[:300] if _f in ("场景", "氛围") else fp[:200])
            if not d.get("角色外观") or len(d["角色外观"]) < 8:
                d["角色外观"] = d["服饰"] or d["场景"] or fp[:200]
            if not d.get("骚") or len(d["骚"]) < 8:
                d["骚"] = d["氛围"] or fp[:200]
        vals = [d[f] for f in FIELDS] + [d["角色外观"], d["骚"]]

        if not all(vals):                    # 任一字段空 = 废档
            skipped["empty"] += 1
            continue
        if any(any(p in v for p in PLACEHOLDER_BLACKLIST) for v in vals):
            skipped["placeholder"] += 1
            continue
        # 只判字段值，不判整块（备注里写"撞敏感词"是正常入库留痕）
        if any(any(mk in v for mk in SENSITIVE_FALLBACK_MARKERS) for v in vals):
            skipped["sensitive"] += 1
            continue
        if any(len(v) < 8 for v in vals):
            skipped["short"] += 1
            continue

        d["记录号"] = num
        valid.append((num, d))

    if verbose:
        total = len(blocks)
        print(f"库内块数 {total} / 合格 {len(valid)} / 剔除 {sum(skipped.values())}",
              file=sys.stderr)
        for k, v in skipped.items():
            if v:
                print(f"  - {k}: {v}", file=sys.stderr)

    # 🔴 11-12 提速：写解析缓存（下次池未变 = 直接命中 = 跳过 14 秒反解）
    try:
        tmp = cpath + ".tmp"
        with open(tmp, "wb") as f:
            pickle.dump(valid, f, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, cpath)
        # 旧指纹的缓存 = 垃圾 = 清掉（池改过几次就会攒几份 128MB）
        keep = os.path.basename(cpath)
        cdir = os.path.dirname(cpath)
        for fn in os.listdir(cdir):
            if fn.startswith(f"pool_{key}_") and fn != keep:
                try:
                    os.remove(os.path.join(cdir, fn))
                except OSError:
                    pass
    except Exception as e:
        print(f"⚠️ 解析缓存写入失败（不影响抽卡）: {e}", file=sys.stderr)
    return valid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--show", action="store_true", help="打印全部字段")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--stats", action="store_true", help="只看牌池体检，不抽签")
    ap.add_argument("--pool", default="nsfw",
                    help="抽哪个池：nsfw(6090) / sfw(2455) / all(8545)")
    ap.add_argument("--set-star", metavar="NNN=R",
                    help="设置某张牌的星级（1-5），R 可写 1-5 或 ★★★ 形式")
    ap.add_argument("--star-stats", action="store_true", help="看星级分布")
    args = ap.parse_args()

    # 🔴 11-04 星级设置：直接在参考库那张牌的表格里加/改 `| **星级** | ★★★★★ |` 行。
    # 只动这一张牌的那一行 = 其他牌 0 影响 = 库仍是单一真值。
    if args.set_star:
        return set_star(args.set_star)

    valid = load_valid(verbose=True, pool=args.pool)
    if not valid:
        print("参考库里没有合格档案（可能全部被占位符黑名单筛掉）", file=sys.stderr)
        sys.exit(1)

    if args.stats:
        nums = sorted(int(n) for n, _ in valid)
        print(json.dumps({
            "合格牌数": len(valid),
            "号段": f"{nums[0]} ~ {nums[-1]}",
        }, ensure_ascii=False))
        return

    if args.star_stats:
        dist = {s: 0 for s in range(1, 6)}
        for _, d in valid:
            dist[d.get("星级", 3)] = dist.get(d.get("星级", 3), 0) + 1
        print(json.dumps({
            "合格牌数": len(valid),
            "星级分布": {f"{s}★": dist.get(s, 0) for s in range(5, 0, -1)},
        }, ensure_ascii=False))
        return

    up = used_path()
    used = set(map(str, json.load(open(up)))) if os.path.exists(up) else set()
    cands = [v for v in valid if v[0] not in used]

    if not cands:
        # 同会话全部抽过了 = 池子重置，让下一轮有新鲜感
        cands = valid
        used = set()

    n = min(args.count, len(cands))
    picked = weighted_pick(cands, n)
    for p in picked:
        used.add(p[0])
    os.makedirs(os.path.dirname(up), exist_ok=True)
    with open(up, "w") as f:
        json.dump(sorted(used), f, ensure_ascii=False)

    if args.json:
        # 🆕 09-29 修复：老版输出 [[num, {字段}]] 二元组，caller 拿到后
        # r['记录号'] 直接 TypeError。统一成 [{记录号, **字段}] 扁平结构。
        print(json.dumps(
            [{"记录号": num, **d} for num, d in picked],
            ensure_ascii=False, indent=2))
        return

    for num, d in picked:
        print(f"=== 记录 {num} ===")
        print(f"[星级] {'★' * d.get('星级', 3)}")
        for k in FIELDS + ["角色外观", "骚"]:
            print(f"[{k}] {d[k]}")
        # 09-30：成品提示词 = 抽到即出图（没它 = 调用方得自己拼 6 件套）
        if d.get("成品"):
            print(f"[成品提示词] {d['成品']}")
        else:
            print("[成品提示词] （本牌未存 = 需按 6 件套手工拼）")
        print()


if __name__ == "__main__":
    main()
