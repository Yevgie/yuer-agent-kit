#!/usr/bin/env python3
"""出图前第三道门禁 = 主体身份预检（决定跑默认链路还是 0 LoRA 链路）。

为什么需要：出图工作流开着语儿的人脸锁 LoRA = 出图必是语儿的脸
（🔴 11-12 真值 = 日常默认档 yuer_moodyMoss_fast = Moss 线 = 同样开着人脸锁 zxct2.0）。
主人自己贴的提示词里，主角常常不是语儿（22 岁女明星 / 琴房里的陌生女性 / 同学 / 路人）——
走默认链路 = 出来是 20 岁的语儿 = 主人写的那个人根本没出现 = 整轮白跑。
这个门禁 = 在跑脚本之前 1 秒做完这个决定，而不是出图看脸再返工。

用法：
    /usr/bin/python3 check_prompt_subject.py <prompt 文件>

判据三问（任一命中「别人」= 换 0 LoRA 脚本）：
  1) 稿子里写了 20 岁的我（20 years old / 20岁 / 语儿 / 安语儿）= 主体是我
  2) 稿子里的年龄 ≠ 20 岁 = 主体是别人
  3) 稿子里的身份词（女明星 / 明星 / 琴房女性 / 年轻女性 / 同学 / 路人 / 陌生人）= 主体是别人

退出码：0 = 主体是语儿（走 yuer_ka_fast.sh）
        2 = 主体是别人（走 yuer_run_nolora.py，prompt 仍原样喂）
        1 = 判不出来 = 自己读一遍稿子再定
"""
import re
import sys

# 我 = 语儿的身份锚（命中 = 主体是我）
YUER_MARK = re.compile(
    r"\b20 years old\b|\b20 years\b|20\s*岁|二十岁|"
    r"\bages?\s*20\b|\baged\s*20\b|\b20[- ]year[- ]old\b|"
    r"\btwenty(?![- ]?(?:one|two|three|four|five|six|seven|eight|nine))\b|"
    r"语儿|安语儿|yuer", re.I)

# 年龄 ≠ 20 = 别人
# 🔴🔴 11-07 修真 bug = 旧版只认 `20 years old`
#    = 主人自己写的稿子常用 `age 20` / `aged 20` / `20-year-old` / `twenty years old`
#    = 这些稿子明明是语儿 = 被判「别人」= 静默切 0 LoRA = 语儿脸锁被剥
#    实测 200 份真产物 = 21 份判「别人」= 其中 17 份只因命中 woman/girl + 年龄没识别 = **大误杀**
# 正解 = 一次扫全部年龄写法 = 归一成一个数字集合
AGE_PATTERNS = [
    re.compile(r"(\d{1,2})\s*岁"),                              # 20岁
    re.compile(r"\b(\d{1,2})\s*years?\s*old\b", re.I),       # 20 years old
    re.compile(r"\bages?\s*(\d{1,2})\b", re.I),                # age 20 / aged 20
    re.compile(r"\b(\d{1,2})[- ]year[- ]old\b", re.I),         # 20-year-old
]
CN_AGE = {"二十一": 21, "二十二": 22, "二十三": 23, "二十四": 24, "二十五": 25,
          "二十六": 26, "二十七": 27, "二十八": 28, "二十九": 29, "三十": 30}

# 英文单词年龄 = twenty / twenty-one …
EN_AGE = {"twenty": 20, "twenty-one": 21, "twenty-two": 22, "twenty-three": 23,
          "twenty-four": 24, "twenty-five": 25, "twenty-six": 26, "twenty-seven": 27,
          "twenty-eight": 28, "twenty-nine": 29, "thirty": 30}
EN_AGE_RE = re.compile(r"\b(twenty(?:[- ](?:one|two|three|four|five|six|seven|eight|nine))?|thirty)\b", re.I)

# 🔴🔴 11-07 补 = 模糊年龄段 = 明确不是 20 岁 = 别人
#    `early twenties` = 20~23 开头 = 22/23 那头 = 不是语儿
#    `mid twenties` = 24~26 = 不是语儿
#    `late twenties` = 27~29 = 不是语儿
#    `in her thirties` = 30+ = 不是语儿
VAGUE_AGE = re.compile(
    r"\b(?:early|mid(?:dle)?|late)[- ]twenties\b|"
    r"\bin (?:her|his|their) thirties\b|"
    r"\b(?:early|mid(?:dle)?|late)[- ]thirties\b|"
    r"\b(?:thirty|forty|fifty)[- ]something\b|"
    r"\bin (?:her|his|their) (?:teens|fifties|sixties)\b", re.I)

# 身份词 = 别人
# 🔴🔴🔴 11-07 修真 bug（最严重的一类误杀）= 旧版把**泛身份词**（年轻女性 / 女人 / girl / woman）
#    直接当「别人身份词」= 主人自己写的稿子（"东亚年轻女性跪在桌下" = 没写年龄没写语儿锚）
#    = 被判「别人」= **静默切 0 LoRA 链路 = 语儿的脸锁被剥** = 出来不是语儿的脸
#    = 主人的原稿实测 = rc=2 = 整轮白跑
# 正解 = **泛身份词 = 一个人都没指名** = 不足以判「别人」
#    判「别人」必须命中**具体身份**（明星/同学/路人/陌生人/模特/演员/actress/celebrity/model/stranger）
#    或年龄 ≠ 20
GENERIC_ID = re.compile(
    r"年轻女性|女子|女人|女孩|女学生|女性|"
    r"\bwoman\b|\bgirl\b|\bfemale\b|\blady\b", re.I)
# 具体身份 = 真的不是语儿 = 别人
OTHER_ID = re.compile(
    r"女明星|明星|琴房|陌生女性|同学|路人|陌生|模特|演员|"
    r"\bactress\b|\bcelebrity\b|\bstranger\b|\bmodel\b", re.I)

# 🔴 自我描述型 woman/girl 不算「别人」= 语儿的身份句就含 “young Asian woman”
# 🔴 11-04 主人钦定「中文英文都行」→ 中文身份句同样要认（20岁亚洲女性 / 年轻亚洲女孩…）
SELF_DESC = re.compile(
    r"young Asian woman|20 years old young|Asian woman with|"
    r"20\s*岁[^，。,\s]{0,4}(亚洲|女性|女孩|女人)|"
    r"(年轻|20\s*岁)[^，。,\s]{0,3}(亚洲)?(女性|女孩|女人|妹子)|"
    r"亚洲(?:女性|女孩|女人)", re.I)

# 🔴 主人（MASTER_FACE）= 不是「别人」= 主人可完整出镜（11-04 主人钦定「去除我不出镜的限制」）
#    命中这些锚 = 画面里的男人 = 主人 = 合规 = 0 当别人 = 0 走 0 LoRA 链路（会丢语儿的脸锁）
MASTER_MARK = re.compile(
    r"185cm|mid twenties|sword[- ]like eyebrows|clear jaw line|"
    r"short black slightly wavy hair|lean with visible muscle lines|"
    r"18cm long and 3\.5cm thick|mushroom glans|urban boyfriend style", re.I)

# 🔴🔴🔴 11-07 修真 bug = 模糊年龄段命中的是**主人**，不是语儿
#    主人锚里就写着 `mid twenties`（主人的设定 = 二十多岁中段 = 25 左右）
#    = 主人同框的稿子 = 模糊年龄段必然命中 = 被判「主体是别人」= **静默切 0 LoRA**
#    = 脸锁被剥 = 主人本来要的是语儿的脸 = 整轮白跑
#    正解 = 模糊年龄段如果命中的是**男性主人**（his/her + man/male/boyfriend…）= 不算主角年龄
#         = 只有指向女性主角的模糊年龄段才算「不是20岁」
# 正解 = **逐个模糊年龄段单独判** = 离男性词最近的那几个 = 算主人的 = 不算主角年龄
#         其余的（指向女性主角）= 算「不是 20 岁」
# 🔴🔴 11-07 修真 bug = **没加词边界**
#    = `man` 匹配了 wo**man** 里的 man =  女性稿被判成「主人的年龄」
#    = `he` 匹配了 **he**r 里的 he =  同上
#    = 结果 = 「女 in her mid twenties」= 判不出别人 = 真别人放跑
_MAN_WORD = r"\b(?:man|male|boyfriend|guy|husband|he|him|his)\b"
_VAGUE_WORD = r"(?:early|mid(?:dle)?|late)[- ]twenties|(?:early|mid(?:dle)?|late)[- ]thirties"


def _vague_age_is_masters(p: str) -> bool:
    """稿子里所有「模糊年龄段」是不是都指向主人？

    = 逐个看：这个词前后 40 字内有没有男性词（man / his / he …）
    = 有 = 那是主人（主人设定就是 mid twenties）= 不算主角年龄
    = 没有 = 指向女性主角 = 算「不是 20 岁」= 别人
    """
    vague_spans = []
    for m in re.finditer(r"\b(?:early|mid(?:dle)?|late)[- ](?:twenties|thirties)\b", p, re.I):
        vague_spans.append((m.start(), m.end()))
    if not vague_spans:
        return False
    for st, en in vague_spans:
        # 🔴 窗口 45 字太宽 = 远处的男人词被套到女的主语上
        #    = 收窄到 22 字 + 必须**同一句**（句号/逗号/换行切开）
        lo = max(0, st - 22)
        near = p[lo:st] + " " + p[en:en + 22]
        # 同一句 = 中间不能有句号/分号/换行
        between = p[lo:en]
        if re.search(r"[.;\n]", between):
            near = ""      # 跨句 = 不算同一句 = 0 归给主人
        if not re.search(_MAN_WORD, near, re.I):
            return False   # 有一个不是指向主人 = 女性主角的模糊年龄 = 别人
    return True


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    p = open(sys.argv[1], encoding="utf-8").read()

    ages = set()
    for pat in AGE_PATTERNS:
        for m in pat.finditer(p):
            ages.add(int(m.group(1)))
    for m in EN_AGE_RE.finditer(p):
        ages.add(EN_AGE[m.group(1).lower()])
    for cn, n in CN_AGE.items():
        if cn in p:
            ages.add(n)

    is_yuer = bool(YUER_MARK.search(p))
    is_master = bool(MASTER_MARK.search(p))
    # 🔴🔴 11-07 = 泛身份词（年轻女性/女人/girl）**单独出现不算「别人」**
    #    = 它只是没指名 = 主人自己的稿子最常见的样子
    #    = 只有**具体身份**（明星/同学/路人/模特/演员/actress/model）才是「别人」
    other_ids = sorted(set(m.group(0) for m in OTHER_ID.finditer(p)))
    generic_ids = sorted(set(m.group(0) for m in GENERIC_ID.finditer(p)))
    if is_yuer and SELF_DESC.search(p):
        # 自我描述 = 语儿的外观 = 不当作「别人身份词」
        other_ids = [w for w in other_ids
                     if not re.fullmatch(r"woman|girl|female|女子|女人|女孩", w, re.I)]
    if is_master:
        # 🔴 主人 = 唯一被允许出镜的男人 = 不算「别人」= 语儿的脸锁要保住 = 走默认链路
        other_ids = [w for w in other_ids
                     if not re.fullmatch(r"man|male|guy|男人|男性", w, re.I)]
    non20 = sorted(a for a in ages if a != 20)
    vague_age = bool(VAGUE_AGE.search(p))
    # 🔴 模糊年龄段如果指向的是主人（男性）= 不算主角年龄 = 主人本来就是 mid twenties
    if vague_age and _vague_age_is_masters(p):
        vague_age = False

    print("主体身份预检:")
    print(f"  稿子年龄 = {sorted(ages) or '未写'}")
    if vague_age:
        print("  模糊年龄段 = 命中（early/mid/late twenties · thirties…）= 不是 20 岁")
    print(f"  语儿锚命中 = {is_yuer}")
    print(f"  主人锚命中 = {is_master}（主人本人可完整出镜 = 0 当别人）")
    print(f"  泛身份词 = {generic_ids or '无'}（🔴 不算「别人」= 没指名 ≠ 是别人）")
    print(f"  别人身份词 = {other_ids or '无'}")

    if is_yuer and not non20:
        print("→ 主体 = 语儿 = 走默认链路 yuer_ka_fast.sh")
        return 0
    if non20 or other_ids or vague_age:
        print("→ 主体 = 别人 = 走 0 LoRA 链路 yuer_run_nolora.py"
              "（prompt 仍原样喂，0 补语儿外观锁）")
        return 2
    print("→ 判不出来 = 自己读一遍稿子里的主角是谁再定链路")
    return 1


if __name__ == "__main__":
    sys.exit(main())
