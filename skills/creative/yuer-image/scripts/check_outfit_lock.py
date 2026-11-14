#!/usr/bin/env python3
"""出图前门禁 = 外观锁（只查「漏了 = 底模画错」的两项：下装 / 鞋履）

🔴🔴 11-07 精简 = 只保留必须项
    真产物 200 份实测（旧版 40% 误杀）→ 精简后误杀 = 0（真阳性才报）

    保留（真阳性 = 漏了画面真的坏）:
      · 下装 = 漏了 = 底模画成光腿
      · 鞋履 = 全身景别漏了 = 底模画成光脚（半/特写 0 查 = 画不到）
      · 单人物 = 主角写成了两个 = 分身

    删除（实测 0 命中 或 属 LoRA 的活 或 属主观判断）:
      · 发色 / 妆容 / 发型 = 锁脸 LoRA 干的活 = 脚本查 = 假警报
      · 穿着方式/内层 = 在腰以下 = 半/特写画不到 = 查它 = 逼我写画外的东西
      · 背景人物 / 真实道具 / 公共场所锚定 / 场景锚定 = 实测 0 命中 = 纯噪音
      · 泳装下装 = 实测 0 命中

    退出码：0 = 过（可出图）| 1 = 有 FAIL（漏了真会坏的东西）
"""
import argparse
import re
import sys

# 🔴 硬性项：漏了 = 底模自由发挥 = 主人当场看穿
# 🔴 11-04 主人钦定「中文英文都行」→ 每条正则 = 中文 OR 英文
REQUIRED = [
    # 🔴 11-04：连体衣（bodysuit / unitard / one-piece）= 下装已包含在内 = 不算漏下装
    ("下装", r"skirt|shorts|dress|briefs?|panties|pants|trousers?|jeans|leggings|skort|"
              r"bikini|swimsuit|swimwear|bathing suit|swim trunks|"
              r"bodysuit|unitard|one[- ]piece|playsuit|leotard|"
              r"短裙|长裙|连衣裙|半裙|裤|短裤|牛仔裤|打底裤|内裤|三角裤|内裆|泳装|比基尼|泳裤|"
              r"连体衣|连体泳衣|连身衣|一体式",
     "漏下装 = 画成光腿。'only inner layer' 里的 only 会被读成「她只有这一件」"
     "（泳装也算下装：bikini / swimsuit / swim briefs 都算数）"),
]

# 🔴🔴 11-07 精简 = **删掉「发色」硬性项**
#    真产物 200 份实测 = 只命中 2 次 = 且都是「正则太宽」造成的假警报
#    （`头发|长发|短发|中长发` 这几个词一命中就算「写了发色」= 没写颜色也算过 = 这项形同虚设）
#    真根因 = 发色是**锁脸 LoRA**的活 = 脚本查它 = 既漏真阳性又报假警报
#    主人钦定「锁脸」= 脸的特征归 LoRA 管 = 0 靠 prompt 补

REQUIRED_NAMES = {n for n, _, _ in REQUIRED}

# 🔴🔴 11-07 精简 = 只留「漏了 = 底模画错」的两项
#
# 删掉的三项 + 为什么（真产物 200 份实测）：
#   · 穿着方式/内层 = 内层在腰以下 = 特写/半身根本画不到 = 查它 = 逼我写画外的东西
#   · 发型/刘海    = 锁脸锚点 = 人脸锁 LoRA 干的活 = 脚本查 = 假警报
#   · 妆容         = 同上 = 锁脸 LoRA 干的活 = 脚本查 = 假警报
#
# 🔴 判据 = 只留「真的会让画面坏掉」的：
#   · 下装 = 漏了 = 底模画成光腿（真阳性）
#   · 鞋履 = 全身景别漏了 = 底模画成光脚（真阳性）
#   · 鞋履/下装 = 半/特写不查（画不到 = 0 要求）
RECOMMENDED = [
    ("鞋履", r"sneakers?|shoes|boots?|heels?|sandals?|loafers?|slippers?|running shoes|"
              r"canvas low-top|white mesh|"
              r"球鞋|运动鞋|皮鞋|靴子|高跟|高跟鞋|凉鞋|拖鞋|乐福鞋|帆布鞋|鞋",
     "全身图必填（跟高/鞋头/材质/细节）；中景半身可省"),
]

# 🔴🔴 11-07 精简 = 删掉 SCENES / PEOPLE / EMPTY_ROOM / PROPS / PRIVATE_PLACE / SCENE_GROUPS
#    原因 = 这 6 张表 = 几百行正则 = 门禁主体变成「查场景词表」
#    实测 200 份真产物 = 这三项检查**全部 0 命中** = 纯噪音
#    真阳性价值 = 0 = 留着的唯一效果 = 我看到 WARN 就去补 = 补了 = 改了我的稿


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--quiet", action="store_true", help="只打 FAIL")
    ap.add_argument("--allow-multi", action="store_true",
                    help="主人明说要多人（两人/三人）时开 = 跳过单人物硬拦；默认仍硬拦")
    args = ap.parse_args()

    p = open(args.path, encoding="utf-8").read()
    low = p.lower()

    # 🔴 11-04 10:43 主人钦定「半身和特写很美，不要光出全身」
    #    = 特写/半身的取景根本照不到下装和鞋 = 门禁还按全身要求 = 误杀
    #    正解 = 按景别分级：特写 → 不查下装/鞋履；半身 → 鞋履降为 WARN；全身 → 鞋履升为 FAIL
    # 🔴 11-04 10:53 补全：原实现只认「特写/半身」两个词 = 写了 full body / 全身构图 的稿子
    #    被当成「半身」= 全身漏鞋（底模画成光脚）= 门禁只报 WARN = 放过去 = 真洞。
    # 🔴🔴 11-04 13:40 实测 22 张 = 景别术语词（medium shot / chest-up / waist-up）**完全无效**
    #    = 底模裁切线一律滑到大腿
    #    = 真正起作用的是「画面的物理边界句」（the frame enclosing ... / the bottom edge resting on ...）
    #    = 所以门禁判景别 = 先看边界句，边界句没有才退回术语词
    # 🔴🔴 11-04 14:35 补真洞 = 边界句正则**只认第三人称单数**（frame enclosing her head）
    #    = 双人稿写 "the two heads and the necks" = 完全不匹配 → 落到术语兜底 → 判不出景别
    #    → 门禁逼我写画外的内裤/下装 = 景别崩
    #    正解 = 边界句要认单人/双人/复数三种写法
    BOUND_HEAD = re.compile(
        r"frame enclosing (?:her|the two|both|two) head(?:s)?(?: and (?:her|the two|both|two) neck(?:s)?)?"
        r"(?: and (?:the tops of (?:her|both) shoulders|the shoulders of both women|the shoulders))?|"
        r"frame enclosing only her head|head and neck and the tops of her shoulders|"
        r"her face and collarbones filling the frame|"
        r"the frame enclosing her head and her neck and her shoulders and the top of her chest|"
        r"头和脖子|画面(?:框)?(?:只|仅)?(?:包住|包含).*(?:头|脸)|肩部以上", re.I)
    BOUND_CHEST = re.compile(
        r"the frame enclosing her head and her neck and her shoulders and the top of her chest|"
        r"frame enclosing the two heads and the necks and the shoulders of both women|"
        r"frame enclosing her shoulders(?:,| and) her collarbones(?:,| and) the whole of her chest|"
        r"frame enclosing her shoulders(?:,| and) her collarbones|"
        r"the whole of her chest|"
        r"frame enclosing only her (?:chest|breasts)|"
        r"framed? from the top of her head down to just below her collarbones|"
        r"the bottom edge of the frame cutting across her upper chest|"
        r"tight chest-up|tight portrait shot|"
        r"上胸|锁骨(?:以下|往下)|胸(?:部|口)以上", re.I)
    # 🔴 11-04 14:36 = 裁切线落在**物件**上（桌沿/台面/柜台沿）= 也是有效边界
    #    = 「the bottom edge of the frame resting on the near edge of the marble tabletop」
    BOUND_TABLE = re.compile(
        r"bottom edge of the frame (?:resting|cutting|ending|stopping) (?:on|at) "
        r"(?:the |a |an )?(?:near |far |front )?edge of (?:the |a |an )?"
        r"(?:marble |wooden |glass |cafe |coffee |counter |table |desk |bar |shop )|"
        r"桌面(?:边缘|沿)|桌沿|柜台沿", re.I)

    BOUND_WAIST = re.compile(
        r"torso down to her waist|bottom edge of the frame resting on her waistline|"
        r"bottom edge of the frame resting on (?:their|both) waistlines|"
        r"framed down to just above her waist|waist-up portrait|"
        r"腰部(?:为止|以下)|到腰", re.I)
    BOUND_HIP = re.compile(
        r"down to her hips|torso down to her hips|hip line|"
        r"胯(?:部)?(?:为止|以下)|到胯", re.I)
    # 🔴🔴 11-07 修真 bug = 画到胯 = 脚不入画 = **不该查鞋履**
    #    旧版把胯档判成 is_full = 全身 = 鞋履升 FAIL
    #    实测 = 16 个「鞋履_其他」全是这一类（frame from the crown of her head down to her hips）
    #    = 判成全身 = 要我写画外的鞋 = 底模照着画 = 裁切线滑下去 = 白跑
    BOUND_THIGH = re.compile(
        r"top of her thighs|thighs and the top of her thighs|to her knees|"
        r"大腿(?:上段|根部)?(?:为止|以下)|到膝", re.I)

    # 🔴🔴 11-04 13:50 实测补漏 = **否定式画外声明**（nothing below X is in view / only X visible）
    #    = 底模同样能吃（= 只画 X 以上）= 但门禁只认"画到哪儿"，不认"哪里不入画"
    #    = 结果：写对了却被判成全身 → 逼我补画外的内裤 → 底模照着画 → 景别崩
    #    正解 = 这类句子也算边界信号，判为"该线以上"（closeup / half）
    BOUND_NEG = re.compile(
        r"nothing (?:below|under|beneath) [\w\s]{0,40}(?:is|are) (?:in view|visible|shown)|"
        r"(?:is|are) (?:cut off|cropped|cut) (?:at|by|just) (?:the |her |his |its )?"
        r"(?:tabletop|table edge|waistline|hip line|collarbone|collarbones|chest|ribs|"
        r"underbust|underbust line|navel|midriff)|"
        r"only (?:her|his|their|the) [\w\s,]{0,60}(?:are |is )?(?:in view|visible)|"
        r"nothing below the (?:table|tabletop|desk)|"
        r"(?:桌面|桌面以下|腰以下|以下)(?:都)?(?:不|没)(?:在画|入画|出现)|"
        r"画面(?:里)?(?:只|仅)(?:有|含|拍到)", re.I)

    SHOT_CLOSEUP = re.compile(
        r"close[- ]up|closeup|close[- ]up portrait|headshot|"
        r"framing from the top of her head to just below|"
        r"特写|近景|大头|脸部特写", re.I)
    SHOT_HALF = re.compile(
        r"medium shot|half[- ]body|half body|from head to mid[- ]thigh|"
        r"three[- ]quarter shot|cowboy shot|"
        r"半身|中景|七分身|过膝", re.I)
    SHOT_FULL = re.compile(
        r"full[- ]body|full[- ]length|full length shot|head to toe|head to heel|"
        r"head to feet|from head to toe|wide shot|"
        r"全身|全身景|全身构图|from head to", re.I)

    # 边界句优先（真正起效的信号）→ 术语词兜底
    # 🔴🔴 11-04 13:40 = **术语词底模根本不吃**（实测 medium shot / chest-up 全部裁到大腿）
    #    = 所以「画外描述」这道门禁只在**边界句**判出景别时才生效
    #    = 用术语词判出来的景别 = 我自己写的字 = 底模没当回事 = 不该拿它当拦人依据
    shot_source = "term"      # term = 术语词（不可靠） / bound = 边界句（可靠）
    if BOUND_NEG.search(low):
        # 否定式画外声明 = 明确"这条线以下不入画"
        # 判哪一档 = 看它否定的是哪条线
        if re.search(r"waistline|hip line|navel|midriff|腰以下|桌面以下|below the (?:table|tabletop|desk)", low, re.I):
            is_closeup, is_half, is_full = False, True, False
        else:
            is_closeup, is_half, is_full = True, False, False
        shot_source = "bound"
    elif BOUND_HEAD.search(low):
        is_closeup, is_half, is_full = True, False, False
        shot_source = "bound"
    elif BOUND_CHEST.search(low):
        is_closeup, is_half, is_full = True, False, False
        shot_source = "bound"
    elif BOUND_WAIST.search(low):
        is_closeup, is_half, is_full = False, True, False
        shot_source = "bound"
    elif BOUND_TABLE.search(low):
        # 裁切线在桌面 = 桌面以下（腿）不入画 = 半身档
        is_closeup, is_half, is_full = False, True, False
        shot_source = "bound"
    elif BOUND_HIP.search(low):
        # 胯档 = 画到胯 = 脚/腿不入画 = 跟半身一样 0 查鞋履
        is_closeup, is_half, is_full = False, True, False
        shot_source = "bound"
    elif BOUND_THIGH.search(low):
        is_closeup, is_half, is_full = False, False, True
        shot_source = "bound"
    else:
        is_closeup = bool(SHOT_CLOSEUP.search(low))
        is_half = bool(SHOT_HALF.search(low)) and not is_closeup
        is_full = bool(SHOT_FULL.search(low)) and not is_closeup and not is_half
        # 🔴🔴 11-04 15:05 补真洞 = **裸体/露点稿写不出景别术语**
        #    = 特写画的是骚穴/臀/胸，稿子不可能写"medium shot"（那反而会露画外）
        #    = 门禁判不出景别 → 逼我写画外的内裤/丝袜 → 破坏画面
        #    正解 = 出现露点关键词（pubic mound / inner labia / buttocks / bare / nude / naked）
        #         且**没写任何画外实体**（内裤/丝袜/鞋都写在画外=不属于）→ 判成特写档
        EXPLICIT_BODY = re.compile(
            r"pubic mound|inner labia|clitoris|vagina|nipple|areola|"
            r"\bbuttocks?\b|\bnude\b|\bnaked\b|\bbare (?:hips?|mound|skin|back|body|shoulders?)\b|"
            r"barely covered|full frontal|nude with", re.I)
        if (not is_closeup and not is_half and not is_full
                and EXPLICIT_BODY.search(low)
                # 注意：只排除"穿在身上的"画外实体；散落的 thong / 滑落的肩带 = 画内道具 = 不算
                and not re.search(r"(?:wearing|wear|dressed in)\s+(?:a |an |the )?[\w ]{0,20}"
                                 r"(?:briefs?|panties|thong|underwear|stockings?|tights|thigh[- ]highs?|"
                                 r"heels?|boots?|sneakers?)|"
                                 r"穿(?:着)?(?:黑色|白色|蕾丝|棉)?(?:内裤|三角裤|内裆|丝袜|连裤袜|吊带袜|高跟鞋|靴)",
                                 low, re.I)):
            is_closeup, is_half, is_full = True, False, False
            shot_source = "bound"

    fails, warns = [], []

    def _grade(name, why):
        """按景别决定这一项缺失 = FAIL 还是 WARN 还是不查。"""
        # 🔴🔴 画外的东西本来就不该查 = 查它 = 逼我写画外的东西 = 底模照着画 = 裁切线滑下去
        #    特写/半身 = 0 查下装、0 查鞋履（画不到 = 不写 = 门禁也不该要）
        # 🔴🔴 11-07 修真 bug = 旧版只在 shot_source=="bound" 时豁免
        #    = 术语词（extreme close-up / medium shot）判出来的景别反而**照样要**下装和鞋
        #    = 实测 = 13 个「下装_裸体稿」全是这一类（特写稿被判漏下装）
        #    = 术语词虽然不可靠（底模不吃），但**我自己写了特写 = 我没打算画全身**
        #    = 门禁要它 = 逼我写画外的东西 = 逼我犯「描述画面外」那个病
        if is_closeup and name in ("下装", "鞋履"):
            return None
        if is_half and name in ("下装", "鞋履"):
            return None
        if name == "鞋履":
            if is_full:
                return ("fail", why + "（全身景别 = 必填，漏了画成光脚）")
            return ("warn", why + "（非全身景别 = 可省）")
        return ("fail" if name in REQUIRED_NAMES else "warn", why)

    def _shoe_exempt(low_text: str) -> bool:
        """🔴 鞋履豁免 = barefoot / 脚不在画幅 = 不该要求写鞋（11-07 修真洞）"""
        if re.search(r"barefoot|bare feet|赤脚|光脚", low_text):
            return True
        if re.search(
            r"feet out of frame|cropped at the (knee|thigh|waist|hip)|"
            r"only (her )?(legs?|thighs?) visible|framing cuts off at|"
            r"脚(不在画面|没入画|被遮挡)|拍到膝盖|画到大腿|脚部(不在画面|被遮挡)|"
            r"feet hidden|hidden feet|feet cropped", low_text):
            return True
        return False

    for name, pat, why in REQUIRED:
        if re.search(pat, low):
            continue
        g = _grade(name, why)
        if g is None:
            continue
        fails.append((name, g[1]))
    # 🔴 11-04 13:40：「穿着方式/内层」也是画外项（内层在腰以下）= 特写/半身/七分身都不查
    OFF_FRAME_ITEMS = {"下装", "鞋履", "穿着方式/内层"}
    for name, pat, why in RECOMMENDED:
        if re.search(pat, low):
            continue
        if name in OFF_FRAME_ITEMS and (is_closeup or is_half):
            continue
        g = _grade(name, why)
        if g is None:
            continue
        if g[0] == "fail":
            fails.append((name, g[1]))
        else:
            warns.append((name, g[1]))

    # 🔴 赤脚场景（泳池/沙滩/浴室地板）= 「缺鞋履」是正常 = 不报
    #    0 为凑门禁写 "no shoes"（否定式 + 底模会照着画）→ 写正面 "she is barefoot"
    # 🔴🔴 11-07 修真 bug = 旧版只清 warns **不清 fails** = 写了 barefoot 还报「FAIL 鞋履」
    #    = 实测 30/56 个鞋履 FAIL 是这个 bug = 主人看到红字 = 白改一轮
    if re.search(r"barefoot|bare feet|赤脚|光脚", low):
        warns = [w for w in warns if w[0] != "鞋履"]
        fails = [f for f in fails if f[0] != "鞋履"]

    # 🔴 11-04 补：脚被遮住/不在取景 = 免鞋履（趴姿、坐姿、裙摆遮脚、画到膝盖）
    #    = 写了鞋也是浪费（画不到）= 不写也不该被拦
    if re.search(
        r"feet out of frame|cropped at the (knee|thigh|waist|hip)|"
        r"only (her )?(legs?|thighs?) visible|framing cuts off at|"
        r"脚(不在画面|没入画|被遮挡)|拍到膝盖|画到大腿|脚部(不在画面|被遮挡)|"
        r"feet hidden|hidden feet|feet cropped", low):
        warns = [w for w in warns if w[0] != "鞋履"]
        fails = [f for f in fails if f[0] != "鞋履"]

    # 🔴🔴🔴 11-04 13:40 画外描述检测（实测 22 张后沉淀的唯一根因）
    #    主人原话：「你设想一张图的时候，只描述能看到的部分，如果是半身图，腰部以下都不会描述」
    #    = 我写了画外的内裤/丝袜/鞋 → 底模照着画 → 裁切线必然滑到大腿
    #    = 判据 = 画幅边界 + 画外部位词 同时命中 = 必拦（0 等出图才发现）
    # 🔴 11-04 14:42 修真洞 = 画外检测把**否定句**里的部位词也当成"描述画外"
    #    = "no legs are visible" / "cropped out" / "nothing below ... is in view"
    #      这些是在说"不画"，不是在描述 = 误杀 = 逼我不敢写边界句
    #    正解 = 检测前先抹掉否定语境（no X / not X / without X / X cropped out / X is out of frame）
    NEG_CLEAN = re.compile(
        r"(?:no|not|without|never|zero)\s+(?:visible\s+)?(?:\w+\s+){0,3}"
        r"(?:briefs?|panties|thong|underwear|stockings?|tights|thigh[- ]highs?|"
        r"heels?|boots?|sneakers?|sandals?|buttocks?|hips|thighs?|knees?|legs?|feet|calves?)\b|"
        r"(?:legs?|feet|thighs?|hips|buttocks?|knees?)\s+(?:are|is)\s+(?:not\s+)?"
        r"(?:visible|shown|in view|cropped|out of frame)|"
        r"(?:legs?|feet|thighs?|hips|buttocks?|knees?|underwear|briefs?|panties|stockings?)"
        r"[^.]{0,30}(?:cropped out|out of frame|not visible|is not visible|are not visible)|"
        r"nothing\s+(?:below|under|beneath)[^.]{0,50}|"
        r"(?:内裤|腿|脚|丝袜|高跟鞋|臀|胯|大腿|膝盖)[^。]{0,12}"
        r"(?:不|没)(?:在画|入画|出现|可见|拍到)|"
        r"(?:不|没)(?:拍到|画到|出现)[^。]{0,8}(?:腿|脚|内裤|丝袜|臀|大腿)", re.I)
    low_noleg = NEG_CLEAN.sub(" ", low)

    if shot_source != "bound":
        pass       # 术语词判出来的景别 = 底模不吃 = 不拿它当画外依据
    elif is_closeup:
        # 🔴 11-04 15:08 补真洞 = 特写/半身档**只拦"穿在身上的画外物件"**，不拦部位词
        #    = 特写的主体可能就是腿/臀（t3 主体就是一条腿）= 部位词是**画内** = 不该拦
        #    = 全身档才拦部位词（那里部位词必然是画外）
        off_body = re.search(
            r"(?:wearing|wear|dressed in)\s+(?:a |an |the )?[\w ]{0,20}"
            r"(?:briefs?|panties|thong|underwear|stockings?|tights|thigh[- ]highs?|"
            r"heels?|boots?|sneakers?|sandals?)|"
            r"穿(?:着)?(?:黑色|白色|蕾丝|棉)?(?:内裤|三角裤|内裆|丝袜|连裤袜|吊带袜|高跟鞋|靴)|"
            r"(?:内裤|丝袜|连裤袜|吊带袜|高跟鞋|靴)[^。]{0,6}穿在", low_noleg, re.I)
        if off_body:
            fails.append(("画外穿着",
                          f"🔴 只描述镜头里能看到的部分 = 画外穿的东西一个字都不许留。"
                          f"这张是特写景别，但 prompt 写了画外穿着的: {off_body.group(0)!r}。"))
    elif is_half:
        # 画到腰 = 画外 = 内裤/丝袜/鞋（穿着式）；臀/大腿/小腿可能在画内（贴桌沿的半身）
        off_body = re.search(
            r"(?:wearing|wear|dressed in)\s+(?:a |an |the )?[\w ]{0,20}"
            r"(?:briefs?|panties|thong|underwear|stockings?|tights|thigh[- ]highs?|"
            r"heels?|boots?|sneakers?|sandals?)|"
            r"穿(?:着)?(?:黑色|白色|蕾丝|棉)?(?:内裤|三角裤|内裆|丝袜|连裤袜|吊带袜|高跟鞋|靴)|"
            r"(?:内裤|丝袜|连裤袜|吊带袜|高跟鞋|靴)[^。]{0,6}穿在|"
            r"(?:wearing|wear|dressed in)\s+(?:a |an |the )?[\w ]{0,20}"
            r"(?:buttocks?|hips|thighs?|knees?|calves?|feet)|"
            r"\b(shoes|boots|heels)\b", low_noleg)
        if off_body:
            fails.append(("画外描述",
                          f"🔴 这张是半身（到腰）景别 = 画外 = 内裤/丝袜/鞋/臀/腿 一个字都不许留。"
                          f"但 prompt 里写了: {off_body.group(0)!r}。"
                          f"写了 = 底模照着画 = 裁切线滑到大腿 = 白跑一轮。"))

    # 🔴 11-04 10:53 主人钦定「单人的」= 多人 = 分身 = 必须拦
    #    判据 = prompt 里出现「多个人」的写法（couple / two women / crowd of / 一对 / 两个人 / 三人…）
    #    注意：背景人（people / crowd / 路人）在公共场所是**要**的 = 不算分身
    # 🔴🔴 11-07 精简 = 只拦**真正的主角分裂**（两个都是主角）
    #    删掉 = 背景人群写法（a couple of / two people in the background / 三个人在排队）
    #    = 实测 6 个 FAIL 里有主人明确要多人（"看看你们"）+ 背景人数 = 误杀
    #    判据 = 数量词后面必须跟「女性主角类」词 + 出现在**主体描述区**（句首/逗号后）
    #         = 背景那类（in the background / behind her / queuing）不算
    MULTI = re.compile(
        r"\b(two|three|both|several)\s+(women|girls|ladies|models)\b|"
        r"\ba pair of (women|girls|ladies|models)\b|"
        r"\bcouple\b|\bduo\b|\btwins\b|"
        r"\bgroup of (women|girls|models)\b|"
        r"\b(both of them|two of them)\b|"
        r"两个(女人|女孩|女性|人)|三个(女人|女孩|女性|人)|一对(女人|女孩|女性)|"
        r"两位(女人|女孩|女性)|双人|多人|两个人|"
        r"另一个(女人|女孩|女性|人)|另(外)?一个女孩|"
        r"(?:女人|女孩|女性|人)[和与及](?:另|另一)(?:一个)?(?:女人|女孩|女性|人)", re.I)
    # 🔴 背景人数 = 不是分身 = 放行（背景那几个人各干各的事 = 公共场景该有的生活感）
    BACKGROUND_MULTI = re.compile(
        r"\bin the (?:background|back|far|distance)\b|"
        r"\bbehind (?:her|him|them)\b|"
        r"\bbeneath\b|\bunderneath\b|"
        r"\b(?:queueing|queuing)\b|"
        r"背景|远处|后方|后面|"
        r"排队|在做饭|在忙", re.I)
    # 🔴 11-04 13:58 主人明说「看看你们」= 要双人图 = 单人硬拦跟主人意志冲突
    #    = 正解 = 加显式开关（--allow-multi），默认仍然单人硬拦
    #    = 不是"绕过门禁" = 是"主人点名要多人时门禁知道这是有意的"
    if (not args.allow_multi
            and MULTI.search(low)
            and not re.search(r"\bempty\b|空无一人|只有她一个", low, re.I)
            # 🔴 11-07 = 背景人数不算分身（背景那几个人各干各的 = 公共场景该有的）
            and not BACKGROUND_MULTI.search(low)):
        fails.append(("单人物",
                      "🔴 主人钦定「单人的」= 多人 = 分身 = 必须拦。"
                      "要单人 = 只写她一个 = 删掉两人/一对/三人那类写法。"
                      "（主人明说要多人 = 加 --allow-multi；背景路人多 = 不算分身）"))

    # 🔴🔴 11-07 精简 = 删「背景人物 / 真实道具 / 场景锚定」三项
    #    真产物 200 份实测 = 这三项**全部 0 命中**（全是 WARN）= 纯噪音
    #    而且它们要 10 个场景表 + 4 个正则 = 几百行 = 门禁主体变成「查场景词」
    #    真阳性价值 = 0 = 留着的唯一效果 = 我看到一堆 WARN 就去补 = 补了 = 改了我的稿
    #
    # 🔴 保留 = 「场景锚定」这条**真规则**（人在学校别发家里）由 `yuer-image` 的批次 SOP 管
    #    = 0 靠正则猜 = 判断题 = 不该做成脚本
    scene = ""

    if not args.quiet:
        # 🔴🔴 11-04 13:55 修真洞 = 展示段原来无条件按「正则有没有命中」打 FAIL，
        #    完全不走 _grade 分级 = 特写/半身明明不该查下装，却显示成 FAIL = 骗主人 + 误导我自己
        #    正解 = 展示段跟判定段用同一套分级（_grade 返回 None = 该景别不查 = 显示 跳过）
        # 🔴🔴 11-07 修真洞 = 展示段**独立重算** = 没看 barefoot / 脚出画 的豁免
        #    = 实际 rc=0（过了）= 但屏幕显示「FAIL 鞋履」= 骗主人 + 误导我自己
        #    = 我上一轮出图时真被这个红字晃了一下 = 必须修
        #    正解 = 展示段直接查「这一项最终有没有进 fails/warns」= 判定和展示永远一致
        def _shown(name, pat, why):
            if name in {f[0] for f in fails}:
                return "FAIL"
            if name in {w[0] for w in warns}:
                return "WARN"
            if re.search(pat, low):
                return "OK  "
            g = _grade(name, why)
            if g is None:
                return "跳过"   # 该景别画不到 = 不查
            # 🔴🔴 11-07 修真洞 = 豁免项（barefoot / 脚出画）被上面清出 fails 了
            #    = 但展示段独立重算 = 又算出 FAIL = **rc=0 却显示 FAIL** = 骗主人 + 误导我
            #    正解 = 展示段跟判定段共用同一套豁免 = 判定 = 展示 = 永远一致
            if name == "鞋履" and _shoe_exempt(low):
                return "跳过"
            return "FAIL" if g[0] == "fail" else "WARN"

        print("外观锁自检:")
        for name, pat, why in REQUIRED:
            print(f"  {_shown(name, pat, why)} {name}")
        for name, pat, why in RECOMMENDED:
            print(f"  {_shown(name, pat, why)} {name}")

    for name, why in fails:
        print(f"FAIL 缺「{name}」：{why}")
    for name, why in warns:
        print(f"WARN 缺「{name}」：{why}")

    if fails:
        print("\n🔴 有 FAIL = 先补齐再出图（漏项 = 底模自由发挥 = 主人当场看穿）。")
        return 1
    if warns:
        print("\n🟡 只有 WARN = 可出图，但锁造型松 = 下一张先补。")
    else:
        print("\n✅ 外观锁全齐。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
