#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新提示词文件 · 审核入库（11-10 00:40 语儿）

🔴 唯一职责 = 把 `/path/to/promptlib/` 里新增的 12 个文件
   审核 → 清洗 → 分类 → 写入 nsfw / sfw 两池

🔴 审核口径（11-09 23:10 主人钦定 + 11-10 00:40 语儿执行细则）
  ① 一条 = 一条完整英文自然语言提示词 = 一行 `N|<整段英文>`
  ② 0 儿童、0 男性主体（男女同框保留）
  ③ 中文正文必须翻成英文（Krea2 底模看不懂中文长句）
     = 中文只是画面招牌/包装文字 → 保留（那是画面元素）
  ④ 结构噪声（目录 / 分隔线 / 标题 / 说明行 / tag 串残留）不入库
  ⑤ 内部重复 + 跨文件重复 + 与现有池重复 → 去重
  ⑥ 太短（<200 字符）= 不完整 → 剔

用法：
    python3 ingest_new_pools.py --dry-run     # 只体检不出库
    python3 ingest_new_pools.py                # 真入库
"""

import argparse
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from zh_prompt_map import translate, residual_cjk           # noqa: E402
from audit_pool_subject import classify, is_child          # noqa: E402

NAS_DIR = "/path/to/promptlib"
REF_DIR = os.path.abspath(os.path.join(_HERE, "..", "references"))
POOL_NSFW = os.path.join(REF_DIR, "提示词库-nsfw.txt")
POOL_SFW = os.path.join(REF_DIR, "提示词库-sfw.txt")
BACKUP_DIR = os.path.expanduser(
    "~/.hermes/backups/prompt_pool_ingest_20261110_0040")

# ═══ 文件 → 池 归类（人工定性 = 内容定位，不是关键词猜）══════════════════
#   nsfw = 诱惑/裸体/情色向   sfw = 日常/穿搭/风景向
# 🔴 条目级分池判据 = 硬裸体词 = nsfw，其余 = sfw（杂图 = 逐条判，不是整文件）
HARD_NUDE = re.compile(
    r"\b(nude|naked|topless|bottomless|shaved pussy|pussy|vagina|pubic|"
    r"her genitals|fully exposed|erect nipples|spread wide showing)\b", re.I)

# 🔴 文件级分池 = None = 走条目级判据
FILE_POOL = {
    "001.txt":                    "nsfw",   # 诱惑向 = 大量露点/开胸
    "NSFW_明确裸露.txt":          "nsfw",   # 明确裸露
    "Grok_dancer.txt":           "nsfw",   # 舞者 = 露胸露阴
    "仙侠.txt":                   "nsfw",   # 仙侠 = 衣衫半解露胸露阴
    "制服sex2.txt":               "nsfw",   # 制服 = 插入描写
    "彩绘_v3.txt":                "nsfw",   # 彩绘 = 完全裸体
    "彩绘_v4.txt":                "nsfw",   # 彩绘 = 完全裸体
    "汉服脱衣舞_v5.txt":          "nsfw",   # 汉服脱衣舞
    "prompt2.txt":                "nsfw",   # 夜间人妻露出
    "百合多p群飞百合多p群飞150分组4_150.txt": "nsfw",  # 百合 = 女性向情色
    "杂图.txt":                   None,    # 杂图 = 逐条判（有硬裸体词 → nsfw / 其余 → sfw）
    "海边姿势提示词合集.txt":      "sfw",    # 海边比基尼 = 日常擦边
}

# ═══ 结构噪声 ═══════════════════════════════════════════════════════════
SEP_LINE = re.compile(r"^=+\s*$")
TAG_NUM = re.compile(r"\b(?:a|an|the)\s+\d+(?:girl|woman|boy|man)\b", re.I)
ON_MIDDLE = re.compile(r"\bon the middle of the image\b", re.I)
STRUCT_KEYS = [
    "【目录】", "词源提醒", "借自", "命中", "语料", "底模", "建议本条",
    "另一个人物：", "这两个词可能不被识别", "本条「", "在抖音语料",
]

MIN_LEN = 200          # 太短 = 不完整
# 🔴 11-10 01:05 = 中文判据改「最长连续片段」= 不是占比
#   占比是错的（仙侠 74 字正文塞在 2200 字提示词里 = 占比 0.002 = 被当招牌放过）
#   最长连续中文片段 ≥10 字 = 正文叙述 = 必须翻
#   最长连续中文片段 <10 字 = 画面招牌/包装/店铺文字 = 合法保留 = 原样不动
CJK_RUN = re.compile(r"[\u4e00-\u9fff][\u4e00-\u9fff\s，。、；：！？「」（）·—]*[\u4e00-\u9fff]")
CJK_BODY_MIN = 10


def max_cjk_run(text):
    runs = [len(m.group(0).strip()) for m in CJK_RUN.finditer(text)]
    return max(runs) if runs else 0


# 🔴 11-10 01:15 = 招牌 vs 正文 = 光看长度判不准
#   「烟火起 照人间 喜悦无边 举杯敬少年」18 字 = 春节横幅 = 画面招牌 = 该留
#   「兼具时尚感与亲和力，呈现出…」30 字 = 正文 = 该翻
#   = 招牌有语义标记 = 引号 / 横幅 / 招牌 / 印着 / 写着 / 上写 / 对联
# 🔴 引号必须【包住中文】才算招牌 = 英文引号对不能误判
# 🔴 引号内【含中文】即可 = 不管中英混排（"OK PANO 我们是…" = 黑板粉笔字 = 招牌）
SIGN_QUOTED_CJK = re.compile(r"[\"''][^\"''\n]{0,120}[\u4e00-\u9fff][^\"''\n]{0,120}[\"'']")
SIGN_CONTEXT = re.compile(
    r"(?:"
    r"banner|slogan|signboard|shop sign|printed on|"
    r"reads |displayed |hung |hanging |"
    r"横幅|招牌|对联|牌匾|匾额|写着|印着|上写|字样|文字)", re.I)


def is_signage_cjk(text):
    """中文是画面里的招牌/文字 = 合法保留"""
    runs = [m.group(0).strip() for m in CJK_RUN.finditer(text)]
    if not runs:
        return False
    longest = max(runs, key=len)
    # 短片段（<10 字）本来就是招牌
    if len(longest) < 10:
        return True
    # 长片段 = 看它周围有没有招牌语义标记
    m = CJK_RUN.search(text)
    if not m:
        return False
    # 🔴 11-10 01:30 = 招牌词必须【紧邻中文片段】（±40 字符）
    #   90 字符窗口会误判 = "arms hanging softly" 里的 hanging = 身体动作不是招牌
    ctx = text[max(0, m.start() - 40): m.end() + 40]
    if SIGN_QUOTED_CJK.search(text):
        return True
    return bool(SIGN_CONTEXT.search(ctx))


def read_lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return [l.strip() for l in f.read().split("\n")]


def is_struct(line):
    if not line:
        return True
    if SEP_LINE.match(line):
        return True
    if any(k in line for k in STRUCT_KEYS):
        return True
    # 目录条目 = "  1  站姿·xxx" 这类短行
    if len(line) < 40 and re.match(r"^\s*(\d+|附|N\d)\s+\S", line):
        return True
    if line.startswith("〔") or line.startswith("【"):
        return True
    return False


# 🔴 11-10 02:40 = 中文标点清理（引号内的画面文字 = 保留）
CJK_PUNCT = "。，、；：！？「」『』（）《》【】～·"
_QUOTED = re.compile(r"[\"''][^\"''\n]{0,200}[\"'']")


def strip_cjk_punct(text):
    """清正文里的中文标点 = 但引号内的画面招牌文字不动"""
    quoted_spans = [m.span() for m in _QUOTED.finditer(text)]
    out = list(text)
    for i, ch in enumerate(text):
        if ch not in CJK_PUNCT:
            continue
        if any(a <= i < b for a, b in quoted_spans):
            continue          # 引号内 = 画面文字 = 保留
        if ch in "（）：；":
            out[i] = " " if ch in "（）：；" else ","
        elif ch == "，":
            out[i] = ","
        elif ch == "。":
            out[i] = "."
        elif ch == "、":
            out[i] = ","
        elif ch == "；":
            out[i] = ";"
        elif ch == "：":
            out[i] = ":"
        elif ch in "！？「」『』（）《》【】～·":
            out[i] = " "
    res = "".join(out)
    res = re.sub(r"\s{2,}", " ", res)
    res = re.sub(r"\s+([,.])", r"\1", res)
    return res.strip()


def clean_body(line):
    """正文清洗 = 剔 tag 串残留 + 收拾标点"""
    out = line
    # "a 1woman" → "a woman"（Danbooru 编号残留）
    out = TAG_NUM.sub(lambda m: "%s %s" % (m.group(0).split()[0], m.group(0).split()[1][1:]), out)
    # "on the middle of the image, " 冗余 = 保留（是正常散文用法）
    out = re.sub(r"[，、；]\s*$", "", out)
    out = strip_cjk_punct(out)
    out = re.sub(r"\s{2,}", " ", out).strip()
    # 首字母大写（翻译片段拼接后可能小写开头）
    if out and out[0].islower():
        out = out[0].upper() + out[1:]
    return out


def extract_blocks(path):
    """海边那种 = 分隔线包起来的块；普通文件 = 一行一条"""
    lines = read_lines(path)
    name = os.path.basename(path)
    blocks = []
    if any(SEP_LINE.match(l) for l in lines):
        i = 0
        while i < len(lines):
            if SEP_LINE.match(lines[i]):
                j = i + 1
                blk = []
                while j < len(lines) and not SEP_LINE.match(lines[j]):
                    if lines[j].strip() and not is_struct(lines[j]):
                        blk.append(lines[j])
                    j += 1
                if blk:
                    body = " ".join(blk).strip()
                    if len(body) > MIN_LEN:
                        blocks.append(body)
                i = j
            else:
                i += 1
    else:
        for l in lines:
            if not is_struct(l) and len(l) > MIN_LEN:
                blocks.append(l)
    return blocks


def load_pool(path):
    out = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for l in f:
                m = re.match(r"^(\d+)\|(.+)$", l.strip())
                if m:
                    out.append(m.group(2).strip())
    return out


def norm(s):
    return re.sub(r"\s+", " ", s.lower()).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    existing_nsfw = load_pool(POOL_NSFW)
    existing_sfw = load_pool(POOL_SFW)
    seen = {norm(x) for x in existing_nsfw + existing_sfw}
    print("现有池：nsfw %d + sfw %d = %d\n" % (
        len(existing_nsfw), len(existing_sfw), len(seen)))

    new = {"nsfw": [], "sfw": []}
    stats = {}
    for fname, pool in FILE_POOL.items():
        path = os.path.join(NAS_DIR, fname)
        if not os.path.exists(path):
            print("❌ 缺文件 %s" % fname)
            continue
        blocks = extract_blocks(path)
        st = Counter()
        kept = []
        for b in blocks:
            st["抽到"] += 1
            # 结构噪声复查
            if any(k in b for k in STRUCT_KEYS):
                st["剔:结构"] += 1
                continue
            # 🔴 中文分两类（11-10 01:05 定稿 = 按最长连续片段判，不按占比）
            #   最长连续中文片段 < 10 字 = 画面招牌/包装/店铺文字 = 合法保留 = 原样不动
            #   最长连续中文片段 ≥ 10 字 = 中文正文叙述 = 必须翻 = Krea2 看不懂中文长句
            if max_cjk_run(b) >= CJK_BODY_MIN and not is_signage_cjk(b):
                b = translate(b)
                st["翻中文"] += 1
                resid = residual_cjk(b)
                if resid:
                    st["剔:中文残留"] += 1
                    continue
            else:
                st["留:招牌中文"] += 1
            b = clean_body(b)
            if len(b) < MIN_LEN:
                st["剔:太短"] += 1
                continue
            # 主体判据
            cat, why = classify(b)
            if cat == "child_lead":
                st["剔:儿童"] += 1
                continue
            if cat == "male_lead":
                st["剔:男主体"] += 1
                continue
            # 去重
            n = norm(b)
            if n in seen:
                st["剔:重复"] += 1
                continue
            seen.add(n)
            st["入库"] += 1
            kept.append(b)
        if pool is None:
            # 条目级分池
            for b in kept:
                tgt = "nsfw" if HARD_NUDE.search(b) else "sfw"
                new[tgt].append(b)
                st["→" + tgt] += 1
        else:
            new[pool].extend(kept)
        stats[fname] = dict(st)
        print("### %-46s → %s" % (fname, pool or "条目级"))
        print("    %s" % dict(st))

    print("\n═══ 入库结果 ═══")
    for p in ("nsfw", "sfw"):
        print("  %s 新增 %d 条" % (p, len(new[p])))
    print("  合计新增 %d 条" % (len(new["nsfw"]) + len(new["sfw"])))
    print("  → nsfw %d / sfw %d / 合并 %d" % (
        len(existing_nsfw) + len(new["nsfw"]),
        len(existing_sfw) + len(new["sfw"]),
        len(existing_nsfw) + len(new["nsfw"]) + len(existing_sfw) + len(new["sfw"])))

    if args.dry_run:
        print("\n(dry-run = 未写入)")
        json.dump({"stats": {k: dict(v) for k, v in stats.items()}},
                  open("/tmp/ingest_dry.json", "w"), ensure_ascii=False, indent=1)
        return

    # 备份
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for p in (POOL_NSFW, POOL_SFW):
        if os.path.exists(p):
            shutil.copy(p, os.path.join(BACKUP_DIR, os.path.basename(p) + ".pre_ingest"))
    print("\n备份 → %s" % BACKUP_DIR)

    def write_pool(path, items):
        with open(path, "w", encoding="utf-8") as f:
            for i, t in enumerate(items, 1):
                f.write("%d|%s\n" % (i, t))
        return len(items)

    n_nsfw = write_pool(POOL_NSFW, existing_nsfw + new["nsfw"])
    n_sfw = write_pool(POOL_SFW, existing_sfw + new["sfw"])
    print("✅ 落盘：nsfw %d / sfw %d" % (n_nsfw, n_sfw))

    json.dump({"new_nsfw": len(new["nsfw"]), "new_sfw": len(new["sfw"]),
               "stats": {k: dict(v) for k, v in stats.items()}},
              open("/tmp/ingest_result.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
