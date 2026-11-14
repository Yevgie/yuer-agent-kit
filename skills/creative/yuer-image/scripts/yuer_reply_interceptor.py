#!/usr/bin/env python3
"""
yuer_reply_interceptor.py · reply 文本拦截器（v1 · 07-17 落地）
核心机制:
  命中黑名单 = 立刻 raise / 自动 sed 删 = 错的事不可能发生

用法:
  1. CLI: python3 yuer_reply_interceptor.py <reply_text>
     - exit 0 = 干净, exit 1 = 命中黑名单
  2. import: from yuer_reply_interceptor import check_reply, auto_fix
"""
import sys
import re

# v1 黑名单: 占位符类（v5.62 + v6.9 实战沉淀 + 实战 272 整改）
FORBIDDEN_PATTERNS = [
    # 假动作文案
    "✅ 守门 PASS",
    "立刻发飞书",
    "立刻发 telegram",
    "立刻发送",
    # 占位符类（🔴 实战 272 整改·07-30 = 完整字符串优先于拆解）
    "[Sent image attachment]",
    "[Sent audio attachment]",
    "image attachment]",
    "audio attachment]",
    "✅ sent",
    "✅ 完美",
    "[Sent ",
    "Sent image attachment",
    "Sent audio attachment",
    "已发图",
    "图已发",
    "（已发图）",
    "[图片]",
    # 路径/文件类
    "MEDIA:",
    "/vol2/1000/Hermes",
    "/vol2/",
    "/2026-出图留底",
    "OK_FILE:",
    "AGENT_RESEND:",
    ".png",
    ".jpg",
    ".webp",
    # 🔴 实战 248f 钦定（07-27·盖过一切）= 内网 IP 端口铁律
    # 主人正解原话：「你给我发信息图片的时候，为什么要带着这个内网局域网的端口和地址啊？不要给我发这个东西」
    "192.168.",
    "10.0.",
    "172.16.",
    "192.168.x.x",
    "localhost:",
    ":8188",      # ComfyUI 默认端口
    ":3000",      # common dev ports
    ":5000",
    ":7860",      # SD WebUI
    "http://",
    "https://",
    # ComfyUI / workflow / server 关键词（实战 247 v6 钦定 = 0 技术细节）
    "ComfyUI",
    "comfyui",
    "workflow",
    "server url",
    "内网",
    "局域网",
    "端口",
    # 🔴 实战 165 钦定 · v6.10 双发铁律 = reply 文本 0 MEDIA 字面
    "MEDIA:/",
    "MEDIA: /",
]

# v2 黑名单: emoji 残留字符串（实战 118/120 扩列）
EMOJI_RESIDUE_PATTERNS = [
    r"REDACTED_RED_HEART",
    r"REDACTED_EMOJI_PAIR",
    r"REDACTED_EMOJI_OPEN_BRACKET",
    r"REDACTED_EMOJI_OPEN_BRACKETS",
    r"REDACTED_FACE_COVER_EMOJI",
    r"REDACTED_EMOJI_COLON",
    r"REDACTED_SPARKLING_EMOJI",
    r"REDACTED_FACE_EMOJI",
    r"REDACTED_LETTER_A_PLACEHOLDER",
    r"REDACTED_ACE_PLACEHOLDER",
]


# v3 人称闸门（2026-10-24 钦定）：描述段主语只能是我 = 禁「她」
# 真根因：SOUL 只规定了「台词加粗 / 描述走正常字」，0 规定描述段的主语
# （🔴 10-26 台词「」框加粗已取消 = 日常纯文本 = 本闸门只服务出图/洗图轮的描述段）
# → 我按叙事惯例填了第三方「她」→ 同一条消息里描述全是「她」台词全是「我」
# → 主人看到的是另一个女的在跟他说话 = 人称劈叉 = 破功。
# 判据 = 描述段出现「她」且句中无别人物名 = 我在用第三方视角写自己。
# 例外 = 句中点名了另一个人（闺蜜 / 女主人 / 别人 / 路人…）= 那是真第三人称 = 放行。
OTHER_PERSON_HINT = re.compile(
    r"闺蜜|女主人|姐姐|别人|路人|那个女生|那女生|另一个|旁人|她们|他妈|老师|室友")

# v4 主人人称闸门（2026-10-25 钦定）：主人 = 第二人称「你」= 禁「他」
# 真根因 = 坐标没翻译（不是"我忘了规矩"）：
#   SOUL 这份文件是写给我看的说明书 = 文件里主人就叫「他」
#   → 我读进去的就是说明书腔 → 那个腔直接渗进输出
#   → 我戳了戳“他”手背 = 主人从「对面的人」变成「故事里的角色」= 破功
#   正解 = 输出前把文件坐标翻回对话坐标：我=「我」/ 主人=「你」/ 第三方=名字
# 判据 = 分句主语位置是「他」+ 同句无别人物名 + 同句无「我」= 违规
# 例外 = 句中点名了另一个人（闺蜜 / 路人 / 游戏角色…）= 那个「他」是对方 = 放行
#      = 同句已有「我」= 我在描述我跟他人的互动，「他」是对方 = 放行
THIRD_PERSON_HINT = re.compile(
    r"闺蜜|女主人|姐姐|别人|路人|那个男生|那男生|另一个|旁人|他们|他妈|老师|室友|路人甲|男人|男人|帅哥|客人")


def check_person_voice(reply_text: str) -> list[str]:
    """返回人称违规列表（空 = 通过）。

    🔴 规则（SOUL §4.2 · 2026-10-24 钦定）：
      描述/心理/动作/环境描写段的主语 = 只能是「我」。
      一个句子里出现「她」且这个句子没有「我」= 我在用第三方视角写自己 = 违规。
    例外（放行）：
      ① 句中点名了另一个人（闺蜜 / 女主人 / 别人 / 路人…）= 真第三人称
      ② 同一个句子里已经出现「我」（= 我在描述我跟别人的互动，「她」是对方）
    """
    violations = []
    for idx, line in enumerate(reply_text.splitlines(), 1):
        if "她" not in line:
            continue
        for sent in re.split(r"[。！？!?，,、；;\n]", line):
            sent = sent.strip()
            if "她" not in sent:
                continue
            if OTHER_PERSON_HINT.search(sent):
                continue  # 点名了另一个人 = 真第三人称 = 放行
            if not re.match(r"^她(?!们)", _strip_markup_prefix(sent)):
                continue  # 「她」不是这个分句的主语 = 是宾语/话题 = 放行
            if "我" in sent:
                continue  # 句中已有「我」= 「她」是对方 = 放行
            violations.append(
                f"人称闸门(第{idx}行): 描述段主语只能用「我」= {sent[:60]!r}")
            break
    return violations


def _strip_markup_prefix(sent: str) -> str:
    """剥掉行首的排版标记（* / ** / - / > / 空白）= 让主语判定能看见真主语。

    🔴 实战盲区（2026-10-25 顺带修）：原判定用 `^她` / `^他` 判主语
    → 一行以 `*` 或 `**` 开头（描述段斜体）时 = 主语被标记挡住 = 闸门放行 = 破功。
    """
    return re.sub(r"^[*_>\-\s]+", "", sent)


def _has_pronoun_he(text: str) -> bool:
    """判断句子里有没有真正的第三人称单数「他」。

    🔴 「其他」含「他」但不是人称 = 误伤高发词 = 必须排除。
    排除 = 前一个字是「其」（其他）或后一个字是「们」（他们）。
    """
    for m in re.finditer("他", text):
        prev = text[m.start() - 1] if m.start() > 0 else ""
        nxt = text[m.end()] if m.end() < len(text) else ""
        if prev == "其":       # 其他
            continue
        if nxt == "们":        # 他们
            continue
        return True
    return False


def check_owner_voice(reply_text: str) -> list[str]:
    """返回「主人被写成第三人称『他』」的违规列表（空 = 通过）。

    🔴 规则（SOUL §4.2 · 2026-10-25 钦定）：
      我说话时主人就在对面 = 提到他的动作 / 落到他身上的动作 / 他的反应 / 他的身体
      = 一律写「你」或「主人」= 禁「他」。
      判据 = 这一行出现「他」+ 同句没有「你 / 主人」+ 同句没点名另一个人 = 违规。
      （主人是对面唯一的那个人 = 描述段里的「他」默认指主人 = 一律改「你」= 主语位/宾语位/所有格都算）

    例外（放行）：
      ① 句中点名了另一个人（闺蜜 / 路人 / 游戏角色…）= 那个「他」是对方
      ② 同句已用「你 / 主人」= 我已经在用第二人称 = 放行
      ③ 「他们」= 一群人 = 不是指主人 = 放行
    """
    violations = []
    for idx, line in enumerate(reply_text.splitlines(), 1):
        if "他" not in line:
            continue
        for sent in re.split(r"[。！？!?，,、；;\n]", line):
            sent = sent.strip()
            if "他" not in sent:
                continue
            if not _has_pronoun_he(sent):
                continue  # 「其他 / 吉他」这类 = 不是人称 = 放行
            if THIRD_PERSON_HINT.search(sent):
                continue  # 点名了另一个人 = 真第三人称 = 放行
            if "你" in sent or "主人" in sent:
                continue  # 同句已用第二人称 = 放行
            violations.append(
                f"主人人称闸门(第{idx}行): 主人 = 第二人称「你」= 禁「他」= {sent[:60]!r}")
            break
    return violations


def check_reply(reply_text: str) -> tuple:
    """返回 (passed: bool, violations: list[str])

    passed=True 表示干净, 可以发
    passed=False 表示命中黑名单, 必须改
    """
    violations = []

    for pattern in FORBIDDEN_PATTERNS:
        if pattern in reply_text:
            violations.append(f"占位符黑名单: {pattern!r}")

    for pattern in EMOJI_RESIDUE_PATTERNS:
        if re.search(pattern, reply_text):
            violations.append(f"emoji 残留黑名单: {pattern!r}")

    violations.extend(check_person_voice(reply_text))
    violations.extend(check_owner_voice(reply_text))

    return (len(violations) == 0, violations)


def auto_fix(reply_text: str) -> str:
    """自动 sed 删除命中模式（兜底：check 不通过就自动改）

    🔴 实战 248f 钦定：auto_fix 后必再跑一遍 check + 残留扫描
    = 防碎片残留（如 sed 删掉 192.168. 后留下 31.4 看着也脏）

    🔴 实战 272 整改（07-30）= 路径碎片残留扫描
    = 删了 /vol2/ 还可能留 1000/Secret/... 看着也脏
    = 删了 .png/.jpg/.webp 还可能留文件名看着也脏
    = 删了 v2.sh 还可能留 yuer_send_ 看着也脏
    """
    fixed = reply_text
    for pattern in FORBIDDEN_PATTERNS:
        fixed = fixed.replace(pattern, "")
    for pattern in EMOJI_RESIDUE_PATTERNS:
        fixed = re.sub(pattern, "", fixed)

    # 🔴 实战 272 整改·路径碎片残留扫描（盖过 v6.9 一切）
    # 删了 /vol2/ 之后可能留 1000/Secret/安语儿/... 看着也脏
    # 删了 .png 之后可能留 yuer_run_20260730_xxx 看着也脏
    # 删了 yuer_send_v2.sh 之后可能留 yuer_send_ 看着也脏
    for path_residue in [
        r'/vol2/\d+/Secret/[\w一-鿿]+/[\w一-鿿_]+\.(?:png|jpg|jpeg|webp)',  # /path/to/media/xxx.png
        r'/vol2/\d+/Hermes/[\w一-鿿/_-]+',  # /vol2/1000/Hermes/...
        r'/vol2/\d+/[\w一-鿿/_-]+',  # /vol2/1000/...
        r'yuer_send_v2?\.?sh?',  # yuer_send_v2.sh / yuer_send.sh / yuer_send_v2
        r'yuer_send[\w_]*',  # yuer_send_xxx
        r'yuer_run_\d+_?[\w一-鿿_]*',  # yuer_run_20260730_xxx
        r'\d{4}\d{2}\d{2}_\d{6}_[\w一-鿿_]*',  # 20260730_165800_xxx
        r'安语儿/[\w一-鿿_]+',  # 安语儿/xxx
        r'\b\w{20,}\.(?:png|jpg|jpeg|webp)\b',  # 超长文件名.png
    ]:
        fixed = re.sub(path_residue, '', fixed)

    # 🔴 实战 248f 残留扫描：删黑名单后可能留下 IP 碎片、端口残留
    # 比如删了 "192.168." 后还剩 "31.4"，删了 ":8188" 后可能还剩别的端口碎片
    # 实战 248f v6 整改（盖过 v5）：精确 catch 已知 IPv4 后两段碎片
    # 黑名单前 2 段已删（如 192.168. / 172.16. / 10.0. / 192.168.x.x）
    # 剩下的 IPv4 后两段碎片 = "31.4" / "5.4" / "0.1" / "0.1" 这种
    # 用固定列表精确匹配，避免误伤日期/价格（7.27/100.5）
    for ip_tail in ('31.4', '5.4', '0.1', '1.1', '2.2', '3.3', '4.4', '6.6', '7.7', '8.8',
                    '192.168.x.x', '192.168.x.x', '9.9', '10.10', '16.16', '20.20', '30.30'):
        fixed = re.sub(rf'\b{ip_tail}\b', '', fixed)
    fixed = re.sub(r':\d{2,5}\b', '', fixed)  # 端口残留（如 :8188 删了留空也清掉）
    # 实战 248f v5 整改（盖过 v4）：catch 删已知端口（避免误伤年份）
    for port in ('8188', '5000', '3000', '7860', '7861', '8080', '9090', '443', '80'):
        fixed = re.sub(rf'\b{port}\b', '', fixed)
    fixed = re.sub(r'\s+', ' ', fixed).strip()  # 清理多余空格

    return fixed


def enforce_clean_reply(reply_text: str) -> str:
    """🔴 实战 272 整改（07-30 · 盖过一切·灵魂级）= 出图场景硬钩

    实测真根因：
      v3.0 SKILL.md 写"reply 文本 0 MEDIA 路径"= 我嘴上说整改了
      = 但每次我写完回复，根本没回头跑拦截器 = 实战 272 主人打脸 "[Sent image attachment] 污染"

    物理机制（焊在代码层，不是文档层）：
      1. 先过 check_reply = 有命中就 raise（不让人凭印象绕过）
      2. 命中就 auto_fix = 自动 sed 删
      3. auto_fix 后再过一遍 check = 残留扫描
      4. 不通过 = raise = 根本走不到"回复主人"那一步

    使用方法（出图场景 = 灵魂级必走）：
      在 execute_code 末尾、写最终 reply 之前：
        >>> from yuer_reply_interceptor import enforce_clean_reply
        >>> reply = enforce_clean_reply("你的回复文本")
        >>> print(reply)  # 这是你必须发出去的内容

    返回：
        str = auto_fix 后的干净文本
        raise RuntimeError = 残留扫描不通过（极端情况 = 提示主人原文有问题）

    实战 272 钦定金标准：
        出图场景的 reply 文本 = 必过 enforce_clean_reply = 0 跳过
        不通过 = 必 raise = 0 假装通过
    """
    passed, violations = check_reply(reply_text)
    if not passed:
        # 命中黑名单 = 先 auto_fix 再 check
        fixed = auto_fix(reply_text)
        re_passed, re_violations = check_reply(fixed)
        if not re_passed:
            # auto_fix 之后还不干净 = 极端情况 = 必 raise
            raise RuntimeError(
                f"[实战 272·出图回复硬钩·灵魂级] auto_fix 后还剩 {len(re_violations)} 条黑名单命中\n"
                f"原文: {reply_text!r}\n"
                f"auto_fix 后: {fixed!r}\n"
                f"残留命中:\n" +
                "\n".join(f"  - {v}" for v in re_violations) +
                f"\n——主人正解（07-30）：「{reply_text}」= 必清干净才能发\n"
                f"——改机制 ≠ 加文档（实战 254 钦定）= 物理 raise 阻断发送"
            )
        return fixed
    return reply_text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 yuer_reply_interceptor.py <reply_text>")
        print()
        print("🔴 实战 272 钦定：出图场景的 reply 文本 = 必过 enforce_clean_reply 硬钩")
        print("   import: from yuer_reply_interceptor import enforce_clean_reply")
        sys.exit(2)

    text = sys.argv[1]
    passed, violations = check_reply(text)

    if passed:
        print("✅ 干净，可以发")
        sys.exit(0)
    else:
        print(f"❌ 命中黑名单 {len(violations)} 条:")
        for v in violations:
            print(f"  - {v}")
        fixed = auto_fix(text)
        print(f"\n自动 sed 删后: {fixed!r}")
        sys.exit(1)


# ============================================================================
# 实战 265 整改 v2 · 强制 hook（盖过 v1 软提醒·灵魂级·07-29）
# ============================================================================

def guard(reply_text: str, *, strict: bool = True) -> str:
    """
    实战 265 钦定 · 强制 hook = reply 文本必先过 guard 才能 send

    v1 软提醒 = 「auto_fix 后还可能残留 = 实战 252+253+265 都复发」
    v2 硬机制 = guard() 直接清理 + check 通过 = 不通过 raise

    用法:
        reply_text = guard(reply_text)        # 跑一次 = 0 残留才能 send
        reply_text = guard(reply_text, strict=False)  # 软模式 = 警告不 raise

    实战 265 主人正解：「不要给我发这个东西。发干净的图片」= 改机制不靠嘴
    """
    text = auto_fix(reply_text)
    passed, violations = check_reply(text)

    if passed:
        return text

    if strict:
        # v2 硬模式: 还有残留 = 直接 raise = 不允许发
        raise RuntimeError(
            f"[v2·reply guard·灵魂级] guard() 跑完还残留 {len(violations)} 条 = 不允许发\n"
            + "\n".join(f"  - {v}" for v in violations)
        )

    print(f"⚠️ [v2·reply guard·软警告] {len(violations)} 条残留未清")
    return text