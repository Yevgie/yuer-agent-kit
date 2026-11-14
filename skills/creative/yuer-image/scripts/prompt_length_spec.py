#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prompt_length_spec.py · 语儿出图 prompt 长度规范（11-01 主人钦定「关于长度，我觉得你应该系统的设定一下」）

🔴 背景真账（实测 220 份 /tmp/prompt_v*.txt）：
    旧预算表 = 1000 字（180+280+200+180+160）
    实测中位数 = **2269**  max = 3188
    → **预算表跟实际差 2.3 倍 = 它从来没在指导我写作 = 废纸**
    → 真实分布：min 1475 / p25 2194 / median 2269 / p75 2438 / max 3188

🔴 按景别实测（景别越广/越远，要交代的空间信息越多 = 字越多）：
    worm_eye + ultra_wide   median 3159  (min 2518 max 3188)
    high_above + full_50    median 3148  (min 2592 max 3185)
    low_angle + portrait_120 median 3007  (min 2306 max 3069)
    eye_level + macro_close median 2923  (min 2437 max 3073)
    surveillance + wide_full median 2767  (min 2333 max 3024)

🔴 本规范 = **按景别给区间**，不再给一个笼统的 3200
    = 远景写满（空间是主体）· 近景收着（皮肤是主体）= 字花在刀刃上

长度哲学（三条，缺一不可）：
  0. 🔴🔴🔴 **11-07 主人钦定：长度 0 阻断 = 上限 2000 只报数 = 唯一硬顶 4000 = 不进退出码**
     = 超长也照样出图 = **0 回读 0 重写 0 砍字**
     = 本脚本的区间表 / 删除优先级 = **只在真嫌长时当参考**，**不是门禁**
     = 主人口径原话：「**就算长度 2000，也不要修改**」+「**不要靠多轮修改，纯粹的浪费**」
  1. **上限 3200 是硬线** = CLIP 注意力被稀释的物理边界 = 超过 = 底模开始忽略后半段
     = 但它只是天花板 = **不该被当成目标长度** = **🔴 11-07 起更不该被当成阻断**
  2. 🔴🔴 **11-03 钦定：长度 = 写的时候就少写，不是写完再砍**
     = 本脚本的 `lo`（分景别字数下限）**已作废** = 区间不再是「该写多少字」
     = 现役判据 = **① 负向词 0 ② 同部位同义描述 0（每维只落一次）③ 牌面骨架十句写齐**
     = 判据源 = `yuer-prompt-writer` §1.2 / §1.3 / §1.8
  3. **删的顺序固定** = 先删装饰性形容词 → 再删场景次要物件 → 再删光线修饰
     = **永远不删**：主协议 / 主体锚 / 服装五项 / 唯一光源 / 观看关系
     = 因为这五样= 物理成立 + 不畸形 + 有勾引落点

  ⚠️ 11-03 主人口径：「不要砍字数，是写的时候就就少写。是写的时候就做好减法，
     是写的那个逻辑和原则本身就是做好减法的逻辑和原则」
     = 本脚本只做**事后体检**（找重复 / 找负向词）= **不负责教人怎么写长**

用法（出图前自查）：
    /usr/bin/python3 scripts/prompt_length_spec.py --check /tmp/prompt_v134_n1.txt
    /usr/bin/python3 scripts/prompt_length_spec.py --check-all /tmp/prompt_v134_n*.txt
    /usr/bin/python3 scripts/prompt_length_spec.py --table          # 看全套区间表
    /usr/bin/python3 scripts/prompt_length_spec.py --measure /tmp/prompt_v*.txt   # 重新量实际分布
"""
import argparse
import glob
import os
import re
import statistics
import sys

# ══════════════════════════════════════════════════════════════════
# 一 · 按景别的长度区间（11-01 实测反推）
#    lo = 建议下界（低于此 = 某维度没写够）
#    hi = 建议上界（高于此 = 该砍装饰了）
#    hard = 硬天花板（超 = 门禁拦）
# ══════════════════════════════════════════════════════════════════
LEN_HARD_MAX = 3200

SPEC = {
    "ultra_wide_full": dict(
        lo=2500, hi=3200, hard=LEN_HARD_MAX,
        why="超广角全景 = 空间是主体 = 要交代空间层次/透视变形/环境体量 = 字最多",
        must=["空间三层(前中远)", "环境体量对比", "14mm 边缘畸变", "唯一光源", "人物在空间中的位置"],
    ),
    "wide_full": dict(
        lo=2300, hi=3000, hard=LEN_HARD_MAX,
        why="远景 = 人在环境里 = 环境要立住 = 人只占一小块",
        must=["环境层次", "人物在画面中的占比", "唯一光源", "观看关系"],
    ),
    "full_50": dict(
        lo=2400, hi=3100, hard=LEN_HARD_MAX,
        why="50mm 全身 = 标准全身 = 身体和场景都要交代清楚",
        must=["完整身体可见", "承重面/重心", "地面/支撑关系", "唯一光源", "服装五项"],
    ),
    "half_body": dict(
        lo=2300, hi=3000, hard=LEN_HARD_MAX,
        why="半身 = 齐胯 = 上半身勾引主力 = 腰胯和手臂是重点",
        must=["上半身细节", "手部动作", "唯一光源", "腰胯处理"],
    ),
    "portrait_120": dict(
        lo=2200, hi=2900, hard=LEN_HARD_MAX,
        why="120 特写 = 胸部以上 = 脸和颈 = 表情物理化最吃字",
        must=["表情物理化(唇/眼/喉)", "颈肩线", "唯一光源", "焦点位置"],
    ),
    "macro_close": dict(
        lo=2200, hi=2900, hard=LEN_HARD_MAX,
        why="微距 = 只剩一块皮肤 = 皮肤质感要写细 = 毛孔/绒毛/水痕",
        must=["皮肤微观质感", "焦点落在哪", "唯一光源方向", "延伸出画框的暗示"],
    ),
}

# ══════════════════════════════════════════════════════════════════
# 二 · 九维 + D10 的「写齐了没」检查（比字数更能判长短）
#    = 短不是问题 = 漏维度才是问题
# ══════════════════════════════════════════════════════════════════
D9_CHECK = {
    "D9 观看关系": [r"photographer", r"the camera", r"stranger", r"viewer", r"watcher", r"filmed", r"filming", r"took this", r"shooting", r"camera was", r"one looking at her", r"behind the camera", r"on the other side of"],
    "D6 唯一光源": [r"the single source of light", r"the light is", r"the light comes from",
                    r"the light ", r"daylight", r"the sun", r"the ceiling light",
                    # 🔴 11-03 补 = 旧表漏「唯一光源」的常见写法 = 假警报
                    r"is the only light", r"the only light", r"the only real brightness",
                    r"only source of light", r"the only brightness"],
    "D10 未完成": [r"halfway", r"still ", r"not yet", r"has not ", r"stopped", r"caught",
                   r"stuck", r"bunched", r"partly", r"one hand ", r"the other ",
                   r"is not plugged", r"not plugged in", r"has stopped", r"has not reached",
                   r"has not been", r"creeping up", r"riding up", r"slipped", r"fallen open",
                   r"stopped moving", r"and has not", r"still in it",
                   # 🔴 11-03 补 = 「动作做到一半」的常见写法 = 旧表漏 = 假警报
                   r"mid-", r"in the middle of", r"half-", r"drawn up", r"lifted a hand",
                   r"pulled up", r"gathers", r"draws the"],
    # 🔴 11-01 修正：这张表是**关键词检测** = 语义上有、字面没命中 = 误报。
    #   补的是语义等价写法（"没转身也没在意"/"陌生人"/"背对着"/"没有叫住她"…）
    #   ⚠️ 仍不是 100% = 判据 = 命中=大概率写齐 / 未命中=**人工复核**，别直接当 FAIL

    "D7 服装五项": [r"fully covers her breasts", r"clearly covering her hips",
                    r"dress", r"skirt", r"shorts", r"briefs", r"trousers", r"leggings",
                    r"swimsuit", r"top", r"shirt", r"robe", r"coat", r"jacket", r"singlet"],
    "D8 姿态/承重": [r"weight", r"her foot", r"her feet", r"her hand", r"her hands",
                    r"her knee", r"her knees", r"her elbow", r"her hips", r"leaning",
                    r"bent", r"sitting", r"stands", r"kneels", r"lies"],
    "D4 机位/焦段": [r"\d+mm", r"macro lens", r"tele(photo|wide)"],
    "D3 场景层次": [r"behind her", r"in the background", r"behind", r"beyond", r"past ",
                    r"in front of", r"beyond her", r"further"],
}

# ══════════════════════════════════════════════════════════════════
# 三 · 删除优先级（固定顺序 = 每次压字不用重新想）
# ══════════════════════════════════════════════════════════════════
CUT_ORDER = [
    ("① 形容词堆叠", "very / extremely / quite / really / deeply / soft(重复) / beautiful / stunning / gorgeous"),
    ("② 场景次要物件", "道具堆里的第三、第四件"),
    ("③ 光线修饰语", "光效的次级修饰(不是主光本身)"),
    ("④ 重复的身体锚", "身材锚里与前面重复的同义句"),
    ("⑤ 尾参加长", "尾参尾巴"),
]
NEVER_CUT = [
    "主协议(机位/焦段/距离/裁法)",
    "主体锚(年龄/身体/皮肤)",
    "服装五项(上装/下装/颜色/长度/穿着方式)",
    "唯一光源 + 它的方向",
    "观看关系(谁拍/为何/她知不知)",
    "D10 未完成的那个动作",
]


def detect_framing(t):
    for key, pats in [
        ("macro_close", [r"macro lens"]),
        ("ultra_wide_full", [r"ultra wide lens"]),
        ("portrait_120", [r"telephoto at 120mm"]),
        ("half_body", [r"short telephoto at 85mm"]),
        ("full_50", [r"normal lens at 50mm"]),
        ("wide_full", [r"wide lens at 28mm"]),
    ]:
        for p in pats:
            if re.search(p, t, re.I):
                return key
    return None



# ══════════════════════════════════════════════════════════════════
# 🔴 11-01 修正：三条「被看」线 = **三选一** = 不是三个都要满足
#    v135 完全不知道 / v136 半知道 / v137 主动迎上 = 每批只走一条
#    旧版把三个都塞进 D9_CHECK = 每批必报两个缺 = 假警报
AWARENESS_EITHER = [
    ("D10 主动迎上", [r"eyes are on the camera", r"eyes are straight", r"look straight",
                      r"her eyes hold the lens", r"looking at the camera", r"eyes go straight",
                      r"eyes find the camera", r"into the lens", r"at the camera", r"toward the camera"]),
    ("D10 半知道", [r"had seen", r"has seen", r"seen him", r"seen the", r"without hurrying",
                    r"did not stop", r"carried on", r"went on", r"as though", r"gave him nothing",
                    r"not on the lens", r"had looked up at him"]),
    ("D10 她不知道", [r"no idea", r"unaware", r"not on the camera", r"has no idea", r"did not notice",
                      r"had not noticed", r"has not noticed", r"has not turned", r"had not turned",
                      r"not once", r"almost close enough", r"stopped listening", r"not yet decided",
                      r"did not care", r"knew and did not", r"never told her", r"without noticing",
                      r"without looking up"]),
]

def check_d9(t):
    miss = []
    for name, pats in D9_CHECK.items():
        if not any(re.search(p, t, re.I) for p in pats):
            miss.append(name)
    # 🔴 三条「被看」线 = 三选一 = 命中任意一条就算写齐
    if not any(any(re.search(p, t, re.I) for p in pats) for _, pats in AWARENESS_EITHER):
        miss.append("D10 被看状态(三条线选一条)")
    return miss


# 🔴🔴 11-03 钦定：负向词 = 反向提示词 = 正向里一个都不许有
NEGATIVE_WORDS = re.compile(r"\b(no|not|without|never|avoid|absent|lacking)\b", re.I)


def check_negative(t):
    """正向 prompt 里的负向词 = 反向提示词 = CLIP 会照着画那个被否的东西。
    11-03 主人钦定「坚决不允许」= 命中即全删。"""
    hits = NEGATIVE_WORDS.findall(t)
    return hits


def check_one(path, verbose=True):
    t = open(path, encoding="utf-8").read().strip()
    n = len(t)
    fr = detect_framing(t)
    spec = SPEC.get(fr)
    status = []
    if n > LEN_HARD_MAX:
        status.append("FAIL 超硬顶 %d" % LEN_HARD_MAX)
    if spec:
        if n > spec["hi"]:
            status.append("偏长(> %d = 有堆料，去找重复项)" % spec["hi"])
        else:
            status.append("长度 OK")
    else:
        status.append("景别未识别")
    negs = check_negative(t)
    if negs:
        status.append("🔴 负向词 %d 个（no/not/without/never/avoid/lacking）= 反向提示词 = 全删" % len(negs))
    miss = check_d9(t)
    if miss:
        status.append("维度待人工复核: " + ",".join(miss))
    else:
        status.append("九维+D10 写齐")
    if verbose:
        print("%s  %d 字  [%s]  %s" % (os.path.basename(path), n, fr or "?", " | ".join(status)))
    return n, fr, miss, status


def measure(pattern):
    files = sorted(glob.glob(pattern))
    lens = []
    by_fr = {}
    for f in files:
        t = open(f, encoding="utf-8").read().strip()
        n = len(t)
        lens.append(n)
        fr = detect_framing(t)
        by_fr.setdefault(fr or "?", []).append(n)
    if not lens:
        print("没匹配到文件")
        return
    lens.sort()
    print("=== 实测长度分布 (n=%d) ===" % len(lens))
    print("min=%d p25=%d median=%d p75=%d max=%d"
          % (lens[0], lens[len(lens) // 4], statistics.median(lens),
             lens[len(lens) * 3 // 4], lens[-1]))
    print("\n=== 分景别 ===")
    for k, v in sorted(by_fr.items(), key=lambda x: -statistics.median(x[1])):
        v.sort()
        s = SPEC.get(k)
        print("%-18s n=%3d median=%4d min=%4d max=%4d  规范[%s-%s]"
              % (k, len(v), statistics.median(v), v[0], v[-1],
                 s["lo"] if s else "-", s["hi"] if s else "-"))


def table():
    print("=== 长度规范表 (硬顶 %d) ===" % LEN_HARD_MAX)
    for k, s in SPEC.items():
        print("\n%s  [%d-%d]" % (k, s["lo"], s["hi"]))
        print("   why: %s" % s["why"])
        print("   必写: %s" % " / ".join(s["must"]))
    print("\n=== 删除优先级 ===")
    for i, (a, b) in enumerate(CUT_ORDER, 1):
        print("  %s  %s  —— %s" % (a, b, ""))
    print("\n=== 永远不删 ===")
    for x in NEVER_CUT:
        print("  - %s" % x)
    print("\n=== 九维+D10 写齐检查项 ===")
    for k in D9_CHECK:
        print("  - %s" % k)
    print("\n⚠️ 这套是**关键词检测** = 未命中≠没写 = **人工复核**（别当硬门禁）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--check-all", action="store_true")
    ap.add_argument("--table", action="store_true")
    ap.add_argument("--measure", action="store_true")
    a = ap.parse_args()
    if a.table:
        table()
        return
    if a.measure:
        measure(a.path or "/tmp/prompt_v*.txt")
        return
    if a.check_all:
        files = sorted(glob.glob(a.path or "/tmp/prompt_*.txt"))
        bad = 0
        for f in files:
            n, fr, miss, st = check_one(f)
            if n > LEN_HARD_MAX:
                bad += 1
        print("\n合计 %d 个，超硬顶 %d 个（维度项 = 待人工复核，不计入）" % (len(files), bad))
        return
    if a.check and a.path:
        n, fr, miss, st = check_one(a.path)
        sys.exit(1 if (miss or n > LEN_HARD_MAX) else 0)
    print(__doc__)


if __name__ == "__main__":
    main()
