#!/usr/bin/env python3
"""出图 prompt 门禁 = 长度报数 + 结构段 + 自毁排版 + 姿势自然度。

🔴🔴 11-07 主人钦定「对门禁进行精简，只保留必须的，不检查的不要写」
   = 本脚本 = 精简后剩下的**唯一一道主门禁**（另两道 = 主体身份 + 外观锁，各管一件事）

【精简后只查这 4 类 —— 每一条都用真产物量过】
① 长度       = **只报数 = 不进退出码**（上限 2000 建议值 / 唯一硬顶 4000 防失控）
              = 主人钦定「就算长度 2000，也不要修改，不要靠多轮修改」= 超长照样出图 = 0 返工
② 结构段     = 只拦**关键项缺一**：相机/镜头/景别 · 主体/年龄/身体 · 光影/摄影尾参
              = 服装 / 场景层次 = 提醒项 = 缺了只提醒不拦（散但不致命）
③ 自毁排版   = 负面词（`no rip` / `without a scar` = LoRA 照着画破洞）
④ 姿势自然度 = 广角近距（腿被压短）· 关节角度值写满（身体被掰）· 标本信号（失衡感）

【🔴 已删的（11-07 精简 = 实测量出来 = 不检查的不要写）】
  · 长度硬顶 1300 / 3200 天花板 → 2000 只报数
  · 「同部位两句矛盾」        → 4274 份全库 0 真阳性 + 误报 `both knees bent / visible`
  · 「中文残留 = 自毁排版」   → 门禁不卡语种（中文稿合法）
  · 外观锁 7 项（内层/发型/妆容/发色/背景人物/真实道具/场景锚定）→ 见 check_outfit_lock.py

【判据 = 实测不靠感觉】
  精简时用 200 份近期样本 → 0 命中 ≠ 噪音！要扫全库 4274 份：
  姿势自然度近期 0 命中但全库 17 份真阳性（28mm@1.0m / at 160 degrees / 失衡感）
  = 是「我最近写得规矩了」= 不是检查没用 = 保留

用法：
    python3 count_prompt_chars.py prompt.txt
    echo "your prompt" | python3 count_prompt_chars.py -
退出码：0 全过；1 有问题（可直接用于门禁）
"""
import argparse
import re
import sys

# 5 大结构段：命中最少 4 段才算合格
# 🔴 10-14 三次整改：结构段只查「有没有写到」，绝不查「怎么写」。
# 真根因 = 旧正则查的是**句式模板**（`20 years old` 开场白 / `Foreground:` `Midground:` `Far background:` 三层标签）
#         = 这些句式本身就是「分段填表 = 拼凑」的产物
#         = 组合描述（先有画面 → 6 句接着说）自然不写分层标签 = 被自己的门禁打成 MISS = 逼我退回拼凑。
#         **门禁在逼我拼凑**，这是最荒谬的一层。
# 正解 = 按**语义**匹配，不按句式：只要这段信息在 prompt 里出现过，就算命中。
# 🔴 11-04 主人钦定：「门禁不需要查中英文，中文英文都行」
#    → 每条正则 = 中文 OR 英文 = 中英混写 / 纯中文 / 纯英文 都能命中。
SECTIONS = {
    "主协议(相机/镜头/景别)": (
        r"captured with|shot with|photograph|EOS|A7|canon|fujifilm|iphone|\d{2}\s*mm|"
        r"镜头|相机|焦段|光圈|拍摄|取景|构图"
    ),
    "主体(年龄/身体)": (
        r"\d{2}\s*years?\s*old|young\s+(?:\w+\s+){0,3}woman|"
        r"her (?:back|shoulders|waist|hips|thighs?|legs?|collarbones?|spine|arms?|hands?|face)|"
        r"\d{1,2}\s*岁|女性|女孩|女人|女性|她的?[^，。,\s]{0,4}(背|肩|腰|胯|腿|手|脸|胸)"
    ),
    "服装5项(上装/下装/颜色/长度/穿着方式)": (
        r"\b(robe|shirt|top|blouse|dress|skirt|shorts|trousers?|swimsuit|bikini|silk|satin|cotton|linen|"
        r"terry|lace|sheers?|knit|garment|top|sleeves?|hem|strap)\b|"
        r"连衣裙|短裙|长裙|裤|丝袜|连裤袜|内裤|胸罩|文胸|泳装|比基尼|上衣|衬衫|背心|外套|大衣|"
        r"蕾丝|缎面|丝绒|针织|棉|透视|薄纱|高跟|靴|凉鞋|球鞋|发色|发型|刘海|妆容"
    ),
    "场景层次(前景/中景/远景)": (
        r"\b(background|behind her|behind him|behind them|horizon|behind|"
        r"floor|wall|window|door|ceiling|balcony|pool|room|deck|shower|carpet|"
        r"tiled?|marble|wooden|stone|sand|grass|curtain|railing|horizon|sky)\b|"
        r"背景|前景|中景|远景|墙|地板|地面|窗外|门口|天花板|阳台|泳池|房间|浴室|地毯|窗帘|"
        r"瓷砖|大理石|木地板|石|沙|草地|天空|地平线"
    ),
    "光影/摄影尾参(光效/景深/调色)": (
        r"depth of field|rim light|backlight|bokeh|color palette|cinematic|"
        r"\b(light|lit|sun|sunlight|lamp|glow|glowing|shadow|bounce|f/1|f/2|film grain)\w*|"
        r"景深|虚化|散景|逆光|轮廓光|调色|色调|光影|光线|阳光|日光|灯光|灯泡|阴影|光晕|"
        r"电影感|胶片颗粒|色温|冷调|暖调"
    ),
}

# 三种把自己 prompt 写坏的排版
# 🔴 11-04 主人钦定：「门禁不需要查中英文，中文英文都行」
#    → 「中文残留」这条禁令已删除（下面 SED 中仍有中文 = 合法）。
#    → 结构段正则已扩成中英双语（中英混写也能命中）。
SELFDESTRUCT = {
    "负面词(LoRA 会照着画出破洞/疤)": r"\b(no|not|without)\s+(rip|tear|hole|scar|stain)\w*",
    # 🔴🔴 11-07 精简 = 删「同部位两句矛盾」
    #    真产物 4274 份全库实测 = **0 份真阳性** = 从来没拦过任何一份
    #    而且会误报合法写法：`both knees bent on the floor and both knees visible` = 同一状态重申 = 不是矛盾
    #    = 半扇门 = 唯一效果 = 我看到 FAIL 就去改我本来没错的承重段
}

# 🔴 姿势自然度 10-14 主人打脸「姿势怎么都这么诡异」后的结构性焊死
# 真根因 = 前三类只查排版，5 大结构段只查「有没有写」，**全绿也照样出人偶标本**。
# 写死 6 物理量 + 广角近距 + 角度值写满 = 三件事各自都能造畸形 = 必须机械拦，不能靠自检自觉。
#
# 🔴🔴 11-07 精简时**差点误删** = 200 份近期样本实测 0 命中 → 看着像噪音
#    = 但全库 4274 份实测 = **17 份真阳性**（全是我自己写坏的稿）
#      · 28mm @ 1.0m  → 腿被压短
#      · at 160 degrees → 身体被掰折
#      · 失衡感/趔趄感 → 姿势写成标本
#    = 200 份 0 命中只说明**我最近写得规矩了** = 不是检查没用 = 删了 = 手滑写坏没人拦
#    = 保留（真阳性 = 手滑复发时能抓住）
WORD_NUM = {
    "one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0,
    "six": 6.0, "seven": 7.0, "eight": 8.0, "nine": 9.0, "ten": 10.0,
    "a": 1.0, "an": 1.0, "half": 0.5,
}


def _camera_distance(p: str):
    """抓机位距离（取最近的那处 = 最危险）。

    实测踩坑：距离的写法五花八门 —— `at knee height one meter from her feet` 里
    数字/英文数词前面既不是 from 也不是 at（是 height），只匹配 `(from|at) N meters` 会整个漏掉
    = 广角近距这条永远不报 = 焊了个假闸门。宁可宽松匹配再人工看，也别漏。
    """
    best = None
    patterns = [
        # from|at|about ... N meter(s)   /   N meter(s) ... from|back|away
        r"(?:from|at|about|within)\s+(?:about\s+)?([\d.]+|[a-z]+)\s*(?:meters?\b|m\b|metres?\b)",
        r"\b([\d.]+|[a-z]+)\s*(?:meters?\b|metres?\b)\s+(?:from|away|distant|distance|back)",
        r"\b([\d.]+|[a-z]+)\s*(?:feet|ft)\s+(?:from|away|back)",
    ]
    for pat in patterns:
        for m in re.finditer(pat, p, re.I):
            tok = m.group(1).lower()
            val = float(tok) if tok.replace(".", "", 1).isdigit() else WORD_NUM.get(tok)
            if val is None:
                continue
            if "feet" in m.group(0).lower() or "ft" in m.group(0).lower():
                val *= 0.3048
            best = val if best is None else min(best, val)
    return best


# 🔴 11-01 主人钦定「低机位虫眼视角」+「超广角全景」= 这两者物理上就是近距广角
#    = 门禁一刀切会把这档全毙掉 = 必须给受控豁免（0 一律放行 = 只认这两种明确写法）
WORM_EYE_WIDE_OK = re.compile(
    r"low(er)?\s+worm[' ]?eye|worm[' ]?eye|on the floor looking up|almost on the floor looking up|"
    r"lens a few centimetres off the floor", re.I)


def _wide_angle_near_human(p: str) -> list:
    """人体 + 广角(<35mm) + 近距(<=3 米) = 腿被压短必畸形。24mm 只允许人离得远。

    🔴 11-01 豁免 = 明确写成「低机位虫眼 / 贴地仰拍 / 超广角全景」时放行
       （这正是主人钦定的合法档 = 广角近距是它的定义 = 0 一刀切毙掉）
    """
    if WORM_EYE_WIDE_OK.search(p):
        return []
    dist = _camera_distance(p)
    if dist is None or dist > 3.0:
        return []
    bad = []
    for m in re.finditer(r"\b(\d{2})\s*mm\b", p):
        f = int(m.group(1))
        if f < 35:
            bad.append(f"{f}mm @ {dist:.1f}m")
    return bad


def _angle_overload(p: str) -> list:
    """关节度数类描写 >3 处 = 身体像被掰过。方向词不算，只数 `at N degrees` / `N-degree`。"""
    return [m.group(0) for m in re.finditer(
        r"\b(?:at|by|about)\s+\d{1,3}\s*[- ]?degrees?\b|\b\d{1,3}[- ]degree\b", p, re.I)]


def _rigid_checklist(p: str) -> list:
    """把姿势写成标本 = 失衡感/趔趄感这类词 + 6 物理量逐格填满。真根因见 yuer-pose-diversity「姿势自然度」。"""
    hits = []
    if re.search(r"\b(unstable|teetering|toppling|precarious|off[- ]balance)\b", p, re.I):
        hits.append("失衡感/趔趄感(标本信号)")
    return hits


NATURALNESS = {
    "人体广角近距(腿必被压短)": _wide_angle_near_human,
    "关节角度值写满(身体像被掰)": _angle_overload,
    "姿势标本信号(失衡感)": _rigid_checklist,
}

# 骨架配额（11-04 二次钦定 = 12 句分镜表，每句 ~110 字）
# 真根因 = 库牌 12 句覆盖 12 个维度；短 = 维度缺 = 画面散
BUDGET = [
    ("1 她是谁+一个情绪词", 110, "🔴 必须在第一句 = CLIP 前半段权重最高 = 钩子"),
    ("2 景别+构图", 110, "0 写 = 底模不知道拍多远"),
    ("3 场景三层", 110, "前景/中景/远景"),
    ("4 姿态1", 110, "一个动词 + 进行时"),
    ("5 姿态2(手在干什么)", 110, ""),
    ("6 服装", 110, "上装+下装+状态+颜色"),
    ("7 配件清单2~4件", 100, "库牌 66% 都写 = 0 写 = 人物空"),
    ("8 头发+头饰", 100, ""),
    ("9 光(光位+光质+落点)", 110, ""),
    ("10 材质对比(哑光 vs 反光)", 100, "库牌 ~2 处/条 = 质感"),
    ("11 氛围+景深", 110, "库牌 46% 写 bokeh"),
    ("12 收尾锚(相机+焦段+质量词)", 110, "🔴 缺 = 画面没调子"),
]


# 🔴🔴🔴 长度 = 参考带，0 阻断（11-07 主人钦定「就算长度 2000，也不要修改」）
#
# 🔴 根因（11-07 实测）：硬顶 1300 + 「超顶 = exit 1 = 不出图」= 我逐句砍了 7 轮
#    （1801 → 1739 → 1582 → 1536 → 1511 → 1456 → 1333 → 1281）
#    = 写 prompt 花 316 秒，而服务端出图 + 落盘 + 发图 = 9 秒。
#    **瓶颈 97% 在反复砍字上，不在算力。** 每一轮砍都要重读全文 + 重跑门禁 + 重落盘。
#
# 🔴 判据 = 长度是**参考带**不是**配额**：
#    · 长度检查只报数，**永远不进退出码** = 不会因为长而不出图 = 0 返工
#    · 唯一还拦的 = LEN_HARD（防失控，防的是 20000 字符那种，不防 2000）
#    · 长度不够也**不拦** = 「加水词凑长度」= 堆料 = CLIP 读到 N 个 = 多肢体畸形
#    · 真正要管的是「一个点有没有写两遍」，不是「多少字」
#
# 🔴 长度上限 2000 = 主人原话「就算长度 2000，也不要修改」= 2000 以内 0 任何长度压力
LEN_MAX = 2000        # 建议上限 = 只报数 = 不拦
LEN_SOFT = 1600       # 超过只提示「偏长」= 不拦
LEN_HARD = 4000       # 唯一真硬顶 = 防失控（>4000 才 exit 1）
# 中文稿 = 一字一义，密度比英文高 ≈2 倍 = 参考带按语种各自标尺，但**两条都不拦**
LEN_MAX_CN = 2000
LEN_SOFT_CN = 1600
LEN_HARD_CN = 4000


def _is_cn(p: str) -> bool:
    """中文占比判定 = 中文字符数 / 总字符数 > 25%。

    🔴 用「比例」不用「有没有中文」= 中英混写（主人贴的稿子常见）不能被误判成纯中文，
    也不能被误判成纯英文 = 一律按实际密度算区间。
    """
    cn = sum(1 for ch in p if "\u4e00" <= ch <= "\u9fff")
    return cn > 0 and (cn / max(len(p), 1)) > 0.25


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="prompt 文件路径；- 表示从 stdin 读")
    ap.add_argument("--max", type=int, default=LEN_MAX, help=f"建议上限（默认 {LEN_MAX} = 🔴 只报数不拦）")
    ap.add_argument("--budget", action="store_true", help="打印落笔前的点清单（🔴 11-07：不是压字顺序）")
    ap.add_argument("--allow-chinese", action="store_true",
                    help="🔴 11-04：门禁已改中英双语 = 中文稿不再需要这个开关。"
                         "保留 = 只跳过结构段门槛（给 Danbooru tag 或超短稿用），"
                         "长度上限 + 姿势自然度检查仍在")
    ap.add_argument("--allow-tags", action="store_true",
                    help="🔴 10-30：Anima = Danbooru tag 提示词 = 逗号分隔的标签串，"
                         "不是英文自然句 = 5 大结构段正则对它无意义 = 跳过结构段门槛")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.path == "-" else open(args.path, encoding="utf-8").read()
    p = raw.strip()

    n = len(p)
    cn_mode = _is_cn(p)
    if cn_mode:
        len_max, soft_max, len_hard = LEN_MAX_CN, LEN_SOFT_CN, LEN_HARD_CN
        label = "中文标尺"
    else:
        len_max, soft_max, len_hard = LEN_MAX, LEN_SOFT, LEN_HARD
        label = "英文标尺"
    # 🔴 长度只报数 = 不进退出码 = 超长也照样出图 = 0 返工（11-07 主人钦定）
    ok_len = n <= len_hard
    if n > len_hard:
        print(f"字符数: {n}  FAIL 失控（>{len_hard} = 唯一硬顶·{label}）")
    elif n > soft_max:
        print(f"字符数: {n}  参考带 {soft_max}~{len_max}（偏长，🔴 0 拦 = 0 返工·{label}）")
    else:
        print(f"字符数: {n}  参考带 {soft_max}~{len_max} 内 OK（🔴 长度不拦·{label}）")

    hit = 0
    print("结构段命中:")
    for name, pat in SECTIONS.items():
        # 🔴 10-14 修：必须 re.S。
        # 真根因 = 正则里的 `.` 默认不跨行，而 prompt 本来就是分句换行写的
        #          = 「robe … wearing」分在两行 = 结构段假 MISS = 白重写一轮。
        #          这就是「门禁不可靠」的又一个实例：不是 prompt 写得不好，是门禁自己瞎。
        ok = bool(re.search(pat, p, re.I | re.S))
        hit += ok
        print(f"  {'OK  ' if ok else 'MISS'} {name}")
    # 🔴 10-14 主人钦定放宽：门槛 5/5 → 3/5。
    # 真根因 = 旧门槛逼我去凑结构段字数 = 为了过闸门把光和构图削平 = 画面不好看。
    #     结构段只是「有没有写到」的体检，不是配额；漏 2 段不该阻断出图。
    # 🔴🔴 11-07 修真 bug = 旧版门槛 >=3 = 缺 2 项也放过
    #    实测 = 「缺相机 + 缺场景」两个都缺 = rc=0 = 照样出图 = 底模拿不到机位 = 半扇门
    #    正解 = **关键项缺一就报**（相机/镜头/景别 · 主体 · 光影）= 少写这三样画面一定不对
    #    服装/场景 = 提醒项（缺了会散，但不致命）= 只算 WARN 不拦
    KEY_SECTIONS = {"主协议(相机/镜头/景别)", "主体(年龄/身体)", "光影/摄影尾参(光效/景深/调色)"}
    missing = {name for name, pat in SECTIONS.items() if not re.search(pat, p, re.I | re.S)}
    key_missing = missing & KEY_SECTIONS
    ok_struct = (not key_missing) and len(missing) <= 2
    if args.allow_chinese:
        # 🔴 10-30：中文模型 = 5 大结构段正则全是英文模式 = 对中文必然全 MISS
        #            = 门槛判定对这条道无意义 = 放行（长度 + 自然度仍拦）
        print(f"  -> 命中 {hit}/5（--allow-chinese = 结构段门槛不适用，放行）")
        ok_struct = True
    elif args.allow_tags:
        # 🔴 10-30：Anima = Danbooru tag = 逗号标签串，不是英文自然句
        print(f"  -> 命中 {hit}/5（--allow-tags = tag 提示词，结构段门槛不适用，放行）")
        ok_struct = True
    else:
        if key_missing:
            print(f"  -> 命中 {hit}/5  WARN 关键项缺 = {', '.join(sorted(key_missing))}（11-08 起不拦：一段散文铺够 近/中/远+相机+光 就不会缺；缺了提醒你补一句，照出图）")
        else:
            print(f"  -> 命中 {hit}/5  OK（关键项齐全）")

    bad = 0
    print("自毁排版检查:")
    for name, pat in SELFDESTRUCT.items():
        found = re.findall(pat, p, re.I)
        if found:
            bad += 1
            print(f"  FAIL {name}: {found[:3]}")
    if not bad:
        print("  OK   无")

    # 🔴 11-08 主人「门禁除非必须否则不设」= 姿势自然度门禁删了（0 拦 0 报 3 项）
    #    肢体畸形（广角近距压短腿 / 关节角度写满 / 失衡感词）= 交给我写 prompt 时自己把关
    #    （yuer-pose-diversity「姿势自然度 5 条」是我脑子里的规矩，不靠门禁 block）
    print("姿势自然度：0 门禁（11-08 起交给我写 prompt 时自己把关 = 广角近距 / 关节角度别写满 / 别用失衡感词）")

    if not ok_len:
        print(f"\n超出唯一硬顶 {n - len_hard} 字符 = 失控稿 = 这次真拦。")
        print("  🔴 但正常的「长」= 0 拦：主人钦定「就算长度 2000，也不要修改」")
        print("  🔴 真的嫌长 = 砍【同一个点写了两遍的那句】= 0 砍维度（砍维度 = 画面散）")
        for name, budget, note in BUDGET:
            print(f"  ~{budget:>3}字  {name}  ({note})")

    # 🔴 10-05 提速整改：--budget 任何情况都打表（10-04 铁律）
    # 真根因 = 原来只在「已经在区间内」才打表 = 超天花板的那一轮**拿不到预算**
    #        = 只能盲删整段 = 撞一次天花板就多一轮「重写 + 重读文件 + 重校验」= 实测 A 段 156s
    # 修法 = 预算表属于「写之前要看的东西」= 超限时更该给 = 0 条件打表
    if args.budget:
        print("\n落笔前的点清单（🔴 散文格式 = 写成一段连贯自然语言，不是这 12 行表格）:")
        for name, budget, note in BUDGET:
            print(f"  ~{budget:>3}字  {name}  ({note})")
        print("  🔴 这些是「写之前心里过的点」= 写出来是一段散文 = 一个点只落一次")
        print("  🔴 长度 = 参考带 = 0 阻断 = 写完不回头改 = 0 返工")

    # （11-08 姿势自然度门禁删了 = 这段 if not ok_nat 提示一并删，肢体畸形交给我写 prompt 时自己把关）

    # 🔴 11-08 主人「门禁除非必须，否则不设」= 结构段从「拦」降成「WARN 提示」
    #    （一段散文把近/中/远 + 相机 + 光铺够，它拦不到真漏 = 脚本自己承认的「半扇门」；
    #      主体缺了另有 check_prompt_subject 兜底，相机/光影漏了底模有默认 = 不 block）
    #    留下的拦 = 长度（>4000 失控）+ 破损负向词（no rip/scar/hole = 反向画）= 必须的那两道
    #    （结构段 = WARN 不拦 · 姿势自然度 = 11-08 删了交给我写 prompt 时自己把关）
    return 0 if (ok_len and not bad) else 1


if __name__ == "__main__":
    sys.exit(main())
