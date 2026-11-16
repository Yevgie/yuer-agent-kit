#!/usr/bin/env python3
"""yuer 抽卡直出 SOP 脚本（v4.3 · 09-29 三处整改 · 盖过 v4.2 三段式）
用法：python3 yuer_ka_pai_zhi_chu.py <prompt_file> <leave_name> [--caption "图 caption"] [--receive-id oc_xxx] [--receive-id-type chat_id] [--force] [--dry-run]

🔴 三段式 = 出图落盘 → 飞书真发图（带 caption 的 post，失败自动降级纯图）→ 抽 v6 骚话
   发图失败 = exit 4 = 语儿看到 exit 4 必须立刻补发，绝不允许出完图只回文字。

🔴 v4.3 三处整改（09-29 主人钦定「图片发了两遍」）：
   ① .sent 守卫 = 同一个 leave_name 已真发过 = exit 5 拒发 = 物理层根绝重复发图（真要重出传 --force）
   ② seed 随机化修复 = 旧循环只认 KSampler 的 int seed，但本工作流 KSamplerAdvanced.noise_seed
      是 ["851", 0] 连接引用、真正种子在 SeedNode(851).inputs.seed = 旧循环一个都没改到
      = 每次跑同一 seed = 缓存命中 = 出同一张图。改为直改 SeedNode.seed。
   ③ FEISHU_SEND 支持 YUER_FEISHU_SEND 环境变量 + --dry-run = 调试 .sent 链路时不打扰主人
   ⚠️ 调用方铁律：脚本已内建发图，【不要再手动跟 feishu_send.py 补发】= 会发两遍。
   ⚠️ 调用方铁律：【不要用 tail 截 stdout】= 会切掉「完成/落盘/✅已真发」验收信号 = 误判没发 = 重跑 = 发两遍。
"""
import sys, json, time, random, re, urllib.request, urllib.parse, shutil, os, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from yuer_image_constants import DEFAULT_COMFYUI_SERVER
except Exception:
    # 常量文件读不到 = 不猜端口 = 直接报错（原来写死 127.0.0.1:8189 那台是死的）
    print("ERR: 读不到 yuer_image_constants.DEFAULT_COMFYUI_SERVER = 服务器口径不唯一 = 中止。", file=sys.stderr)
    print("     修法：检查 yuer_image_constants.py 是否存在且可导入。", file=sys.stderr)
    sys.exit(2)

# 环境变量可覆盖（换台式机 / 换机器时不用改代码）
comfyui_url = os.environ.get("YUER_COMFYUI_SERVER", DEFAULT_COMFYUI_SERVER)
PROMPT_FILE = sys.argv[1]
LEAVE_NAME = sys.argv[2]

# 🔴🔴🔴 10-31 主人钦定「落盘名我自己看着怎么存」= 统一命名规范落地在源头
#   旧 = 裸 leave_name（yuer_v9x_t1 / yuer_ab_old_1 …）= 谁都能撞 = .sent 守卫会静默拦掉自己的图
#   新 = yuer_<日期>_<时分>_<短名> = 日期+时间戳天然唯一 = 同名不可能 = .sent 守卫不再误伤
#   例 = yuer_20261031_1657_v9x_t1.png
#   ⚠️ 保留 LEAVE_NAME 原值给 .sent 用；真正落盘/发图用 FILE_STEM
#   ⚠️ 短名里非 ASCII（中文）保留 = 主人看得懂；空格/斜杠等危险字符换成 _
_stem_raw = LEAVE_NAME.strip()
_stem_safe = "".join(ch if (ch.isalnum() or ch in "._-") else "_" for ch in _stem_raw)
_stem_safe = re.sub(r"_{2,}", "_", _stem_safe).strip("_")[:60] or "img"
_dt_now = time.localtime()
# 🔴 同分钟重跑仍会撞名 = 补秒级 = 真正唯一
FILE_STEM = f"yuer_{_dt_now.tm_year:04d}{_dt_now.tm_mon:02d}{_dt_now.tm_mday:02d}_{_dt_now.tm_hour:02d}{_dt_now.tm_min:02d}{_dt_now.tm_sec:02d}_{_stem_safe}"
# 🔴 同一秒内重名 = 追加 _2 / _3 … = 绝不覆盖已有图
_shots_dir = "/path/to/media"
if os.path.exists(f"{_shots_dir}/{FILE_STEM}.png") or os.path.exists(f"{_shots_dir}/{FILE_STEM}.sent"):
    _n = 2
    while os.path.exists(f"{_shots_dir}/{FILE_STEM}_{_n}.png") or os.path.exists(f"{_shots_dir}/{FILE_STEM}_{_n}.sent"):
        _n += 1
    FILE_STEM = f"{FILE_STEM}_{_n}"

# 可选参数（解析剩余 argv）
def _find_arg(flag, default=None):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default

CAPTION = _find_arg("--caption")
RECEIVE_ID = _find_arg("--receive-id", "oc_3c7f585b3c86f29b7e9b152ed6eec41d")
RECEIVE_ID_TYPE = _find_arg("--receive-id-type", "chat_id")
# 🔴 10-30 主人钦定：风格是**风格**，不是主题。
#   F = 一种风格（明亮 + 低画质低解析力 + 去监控绿调），可以用在任何题材上。
#   题材（学生 / coser / 上班族 / 护士…）和风格（怎么拍）**解耦**。
#   所以必须显式传 --style，不能靠提示词关键词猜（猜 = 把风格绑死题材 = 主人打脸过）。
STYLE = _find_arg("--style", "")   # f | g | e | art | ""（空 = 不套任何风格层）
# 🔴 10-30 风格可调档位 = 主人一句话把风格推到想要的强度，不用改提示词本身
STYLE_LIGHT = _find_arg("--light", "")     # bright_max | bright | bright_mid | bright_soft
STYLE_QUALITY = _find_arg("--quality", "")  # low_hard | low | low_mild | clean
STYLE_UI = _find_arg("--ui", "")            # cctv | cctv_zh | cctv_night | none
FEISHU_SEND = os.environ.get("YUER_FEISHU_SEND", "~/.hermes/bin/feishu_send.py")
FORCE = "--force" in sys.argv
DRY_RUN = "--dry-run" in sys.argv or "--no-send" in sys.argv
# 🔴 10-31 澄清 + 修正：--dry-run 的真实语义 = 「出图但不飞书发送」(不写 .sent)
#   ⚠️ 名字骗人 = dry-run 编程通用义是「只演练不真跑」= 实际它照样真算图 → 已正名 + 补真空跑开关
#   --check-only = 真·空跑 = 打印将要提交的内容 + 在提交 ComfyUI 之前就 exit = 0 算力 0 出图 0 发图
CHECK_ONLY = "--check-only" in sys.argv

# 🔴 10-30 主人钦定：模型路由 = 主人点名模型就切对应工作流
#   🔴 11-10 = 人脸锁两条线都有（Krea2 = zxct2.4-000030 / Moss = zxct2.0-000060）= Moss 也能出语儿的脸
#   Moss = 中文强 / 写实日常 / 文字场景 = yuer_moodyMoss_fast（已锁脸 LoRA + 文字强 + 表情好 + 真实感）
#   Anima = 2D 动漫 = anima_nsfw
#   Qwen 2.1 = 编辑 = qwen_image_21_edit
WORKFLOWS_DIR = "~/.local/lib/python3.11/site-packages/comfyui/assets/workflows"
WORKFLOW_BY_MODEL = {
    # 🔴🔴🔴 11-07 08:41 主人钦定 = 只保留一份工作流（不区分 ins_face_soft / nolora / faceonly / softonly…）
    #    唯一出图档 = yuer_moody_fast（现役参数：五条 LoRA 全开）
    #    11-09 21:48 主人手测后换的新档 = 人脸锁 @0.8 + 风情万种-风格@0.6
#    + MJ影视柔光@0.8 + 白虎8b@0.8 + genital_color@-6.0 + breast_size_v2@2.0（洗图 @3.0）
#    + 画质组：真实感 Realism@3.0 + 皮肤质感 Waterglowskin@-1.0 + 湿度wetness@-1.0
    #    底模 = moodyKrea2Mix_v70_nvfp4（Krea2 Mix v7）
    #    旧变体 ins_face_soft / nolora / faceonly / softonly / ins / ins_face / face_soft / mjfilter / zsuger_soft
    #    已全部移出（归档 = _archive/cleanup_persona_variants_20261107_084131）
    "krea2": "yuer_moody_fast",
    "moody": "yuer_moody_fast",
    "moss": "yuer_moodyMoss_fast",   # 中文/写实/锁脸（11-10 新版，已锁脸 + 文字强 + 表情好）
    "krea2_wash": "yuer_moody_fast_wash",  # 🔴 洗图道专用（Moss 没有 wash 变体）
    "anima": "anima_nsfw",            # 2D 动漫
    "qwen": "qwen_image_21_edit",     # 编辑道
    "qwen2.1": "qwen_image_21_edit",
}
MODEL_ARG = (_find_arg("--model") or "").strip().lower()
WORKFLOW_ARG = (_find_arg("--workflow") or "").strip()
if WORKFLOW_ARG:
    WORKFLOW_NAME = WORKFLOW_ARG
elif MODEL_ARG in WORKFLOW_BY_MODEL:
    WORKFLOW_NAME = WORKFLOW_BY_MODEL[MODEL_ARG]
else:
    # 🔴🔴🔴 11-15 主人钦定「优先使用 KREA 2 吧」= 默认档切 KREA 2
    #    理由 = 主人直接点名 = 覆盖 11-10「我自己决定用哪个」的那次默认切 MOSS
    #    ① 洗图道本来就是 Krea 2（yuer_moody_fast_wash）= 出图/洗图同一条线 = 脸一致
    #    ② Krea 2 有解剖滑块三条（穴色/湿度/真实感）+ 脸锁 step30 = 重口档更稳
    #    ③ 中文稿 = 脚本自动翻英文（zh_translate）= 0 卡中文
    #    🔴 Moss 保留两岗（0 删）：① 主人点名「Moss / 中文一级棒」② 要中文原样出（不翻）
    WORKFLOW_NAME = "yuer_moody_fast"
print(f"🎯 工作流 = {WORKFLOW_NAME}", flush=True)

# 🔴 .sent 守卫（09-29 主人钦定「图片发了两遍」· 物理机制层 · 盖过「语儿记得别重跑」软约束）
# 同一个 leave_name 已真发过飞书 = 再跑就是重复发图 = exit 5 拒发。
# 真要重出（同名字换随机 seed 重新生成）= 传 --force 显式覆盖。
# 🔴🔴 10-31：落盘名加时间戳后 FILE_STEM 天然唯一 = .sent 只按 FILE_STEM 查 = 永远不误伤
#    但仍保留「原始短名 .sent」兼容老批次 = 防老图重发
SENT_MARK = f"/path/to/media/{FILE_STEM}.sent"
LEGACY_SENT_MARK = f"/path/to/media/{LEAVE_NAME}.sent"
# 🔴🔴 10-31 关键 = 落盘名唯一化后 .sent 若只查 FILE_STEM = 永远不触发 = 防重复发图失效
#    → 出图成功后【额外】写一份「短名 .sent」= 守卫查短名 = 同短名重跑照样被拦
SHORT_SENT_MARK = LEGACY_SENT_MARK
if not FORCE:
    _hit = None
    if os.path.exists(SENT_MARK):
        _hit = ("新命名", SENT_MARK)
    elif os.path.exists(SHORT_SENT_MARK):
        _hit = ("短名", SHORT_SENT_MARK)
    if _hit:
        print(f"❌ 实战 277 守卫：{LEAVE_NAME} 已经真发过飞书（{_hit[0]} .sent 标记 = {_hit[1]}）= 不重复发图 = exit 5。", flush=True)
        print("   真要重出这张：换一个 leave_name，或加 --force 显式覆盖守卫。", flush=True)
        sys.exit(5)

# 1. 读取 500-650 词英文 prompt（已按 v4.1 拼好）
with open(PROMPT_FILE) as f:
    prompt_text = f.read().strip()

# 🔴🔴🔴 1.5 中文自动翻译（10-31 语儿）
#    主人说「腋下 透视 猫耳」= 直接出图 = 中文先翻成英文 tag
#    数据源 = 官方 tag_zh 社区中文词库 125,426 键（derived/tag_zh_index.json）
#    放在这里 = 所有出图路径都覆盖（CLI / 模板 / 法典直出 / 手写文件）
# 🔴🔴🔴 11-14 修（主人 11-14 钦定「Moss 中文原样喂，0 翻译」）：
#    原来 = 只要稿子里有中文就无条件翻英文 → 走 Moss 也会被翻
#    后果 ① 违反矩阵 §5.1「Moss = 中文提示词原样喂 = 0 翻译」（它的中文能力就是卖点）
#          ② 语义错误 = 实测「下身赤裸」被翻成 "no lower clothing"（= 没穿下装 ≠ 赤裸）
#    现在 = 只对**不吃中文**的道翻（Krea2 / Anima / Qwen）；Moss 原样喂
#    判据 = 吃中文的道 = CLIP type=moss_image（编码器 qwen3.5_9b_int8）
_CN_NATIVE_WORKFLOWS = ("yuer_moodyMoss_fast",)
if (re.search(r"[\u4e00-\u9fff]", prompt_text)
        and WORKFLOW_NAME not in _CN_NATIVE_WORKFLOWS):
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from zh_translate import translate_prompt
        _zhrep = []
        _new_prompt = translate_prompt(prompt_text, report=_zhrep)
        if _zhrep:
            print(f"🔴 中文已翻译 {len(_zhrep)} 段：", flush=True)
            for _o, _n in _zhrep[:12]:
                print(f"   {_o}  →  {_n}", flush=True)
            prompt_text = _new_prompt
    except Exception as _e:
        print(f"⚠️ 中文翻译跳过（{_e}）= 保留原文", flush=True)

# 2. 加载工作流（默认 yuer_moody_fast；--model / --workflow 可切）
workflow_path = os.path.join(WORKFLOWS_DIR, f"{WORKFLOW_NAME}.json")
# 🔴🔴 11-09 17:15 主人钦定 = 旧 moody fast / wash 两份已删 = 主人手测完发新的
#    = 这里【不静默兜底到别的档】= 找不到就报错退出 = 免得出错档图还发给主人
if not os.path.exists(workflow_path):
    print(f"❌ 工作流文件不存在: {workflow_path}", file=sys.stderr)
    print(f"   当前档 = {WORKFLOW_NAME}", file=sys.stderr)
    print("   = 11-09 主人删了旧 moody fast/wash = 等主人发新的工作流文件。", file=sys.stderr)
    print("   放进来后（或 --workflow 指定别的档）再跑。", file=sys.stderr)
    sys.exit(2)
with open(workflow_path) as f:
    workflow = json.load(f)

# 3. 覆盖 prompt 节点 + negative + 随机种子
# 找正面 prompt 节点 = 优先 CLIPTextEncode（非 Negative）/ CR Prompt Text
_prompt_node = None
_neg_node = None
for _nid, _n in workflow.items():
    _ct = _n.get("class_type", "")
    if _ct == "CLIPTextEncode":
        _t = _n.get("_meta", {}).get("title", "") or ""
        if "Negative" in _t or "negative" in _t.lower():
            if _neg_node is None:
                _neg_node = _nid
        elif _prompt_node is None:
            _prompt_node = _nid
    elif _ct in ("CR Prompt Text", "PrimitiveStringMultiline", "TextEncodeQwenImage21"):
        if _prompt_node is None and _ct != "TextEncodeQwenImage21":
            _prompt_node = _nid
if _prompt_node is None:
    print(f"❌ 工作流 {WORKFLOW_NAME} 找不到正面 prompt 节点 = 中止", file=sys.stderr)
    sys.exit(2)
if _n_in := workflow[_prompt_node]["inputs"]:
    if "text" in _n_in:
        workflow[_prompt_node]["inputs"]["text"] = prompt_text
    elif "prompt" in _n_in:
        workflow[_prompt_node]["inputs"]["prompt"] = prompt_text
    elif "value" in _n_in:
        workflow[_prompt_node]["inputs"]["value"] = prompt_text
print(f"✍️ prompt 写入节点 {_prompt_node}", flush=True)

# 🔴 10-30 畸形整改（主人反馈「后面四张畸形太严重」）
#
# 真根因（实测 agnes 反推 = 非猜测）：
#   Moss 遇到「Extreme low-angle POV + looking up from ... steps」会脑补跪姿
#   = 大腿水平展开 + 大腿小腿成直角折叠 = 膝关节反曲 = 人体做不出来 = 畸形
#   同提示词换 seed 偶发正常 = 坐实是「姿态脑补」不是「画质差」
#
# 对策两层（都自动，0 靠我每次手写）：
#   ① 负向补畸形词（跪姿/反曲/断肢/畸形脚）
#   ② 站姿锚定句（明确 legs straight / knees slightly bent / feet planted flat / head fully in frame）

# 🔴 负向分模型 = 2D 线绝不能用写实线的负向
#   写实线负向里有 cartoon / anime / 3d render = 这三个会把 2D 全杀掉
#   2D 线用官方基线 + 画风负向（防跑偏成 3D/写实）
NEG_BASE = "(worst quality, low quality, blurry, deformed, ugly, bad anatomy, bad hands, missing fingers, watermark, signature, text, logo, oversaturated, cartoon, anime, 3d render)"
NEG_BASE_2D = ("worst quality, low quality, score_1, score_2, score_3, artist name, "
               "blurry, jpeg artifacts, censor")
# 🔴🔴 10-31 实测铁律 = CFG=1 + Turbo LoRA 下【负向完全不起作用】
#   证据 = 干净负向 vs 45 个人体崩坏词重负向，同提示词同 seed → 像素差 0.00（图完全一致）
#   原因 = CFG 1 = 正负向等权 = 负向没有"排斥"力度 = 写多少都一样
#   结论 = 所有"不要什么"必须翻成正向的"要什么"（见 POS_CONSTRAINT_2D）
#   = 这也是 Anima 官方"至少 2 句自然语言"建议的真正用途
# 🔴 负向只保留画质兜底（万一 CFG 被调高时有用）= 人体/构图/画风类全部搬到正向

# 🔴 2D 线正向约束 = 法典负向 11 组的语义反向改写
POS_CONSTRAINT_2D = (
    # 人体（= 法典解剖畸变组 + 手部错误组 + 腿部错误组 反向）
    "anatomically correct human body, correct human proportions, "
    "natural human joints, two arms and two legs, five fingers on each hand, "
    "well drawn anatomy, correctly drawn hands and feet, "
    # 画质（= 法典低质量组 + 画质动画组 反向）
    "clean anime lineart, vibrant cel shading, sharp clear details, "
    "high quality anime illustration, "
    # 画风锁定（= 法典排除画风组 反向 = 明确要什么）
    "pure 2D anime illustration, hand drawn anime style, not photorealistic, not a photograph"
)
# 🔴 2D 线不做站姿锚定（Anima 不是靠低角度脑补跪姿的模型）= 0 注入
_IS_2D_MODEL = WORKFLOW_NAME in ("anima_nsfw",)

# 负向畸形强化 = 低角度 POV 道专用（其它道不注入 = 0 污染）
NEG_ANATOMY = (", kneeling, kneeling pose, kneeling on escalator, crouching, squatting, "
               "bent knees, hyper-extended knees, broken joints, twisted joints, "
               "extra legs, extra limbs, fused fingers, mutated hands, "
               "broken feet, deformed feet, malformed feet, "
               "no head, cropped head, cut off head, out of frame")

# 站姿锚定句 = 只在「低角度仰拍 + 从下往上」类提示词注入
# 判据 = 提示词里出现 low-angle POV / looking up from ... steps 这类信号
_LOWPOV_SIGNALS = ("low-angle pov", "extreme low-angle", "looking up from",
                   "low camera", "from below", "angle from underneath")
_POSTURE_ANCHOR = (" She stands upright on the step, both legs straight and slightly apart, "
                   "knees only slightly bent, both feet planted flat on the step, "
                   "her full body visible from head to feet, head fully in frame.")

_has_lowpov = any(s in prompt_text.lower() for s in _LOWPOV_SIGNALS)
_is_lowpov_kw = WORKFLOW_NAME in ("yuer_moodyMoss_fast",)  # 监控低视角道 = Moss

# 🔴 10-30 主人钦定（打脸修正）：风格 ≠ 题材
#
# 主人原话：「这 f 类，不是说绑定了学生主题，不是的。f 类本就是一个风格主题，
#            你应该根据需求分析选择使用，不是绑定学生或者 cos，这是不对的。
#            cos 可以是监控 G 类，也可以是写真艺术感」
#
# = F/G/E 是**拍法**（机位/光线/画质/色调/UI），不是**拍谁**。
# = 题材（学生/coser/OL/护士/任何）× 风格（F/G/E/art）自由组合。
# = 所以：**0 靠关键词猜**（猜 = 风格被题材绑死 = 主人打脸）→ 显式 --style 开关。
#
# 🔴 风格资产全部集中在 yuer_styles.py（= 可扩展的风格库 = 主人认定的方向）
#    加新风格 = 只改那个文件，主脚本 0 动。

try:
    from yuer_styles import get_style, apply_style, style_negative, list_styles
    _STYLE_LIB_OK = True
except Exception as _se:  # 库不在 = 降级成 0 套风格（不崩）
    _STYLE_LIB_OK = False
    print(f"⚠️ 风格库加载失败 = 本次 0 套风格层（{_se}）", flush=True)

_STYLE_OBJ = (get_style(STYLE, light=STYLE_LIGHT, quality=STYLE_QUALITY, ui=STYLE_UI)
              if _STYLE_LIB_OK else None)

if _STYLE_OBJ is not None:
    # 🔴 机位占位符 = 由提示词里已有的场景词推断，缺省给通用值
    _slots = {}
    _low = prompt_text.lower()
    for _kw, _room in (("living room", "living room"), ("bedroom", "bedroom"),
                       ("kitchen", "kitchen"), ("bathroom", "bathroom"),
                       ("hallway", "hallway"), ("corridor", "hallway"),
                       ("hotel room", "hotel room"), ("studio", "studio"),
                       ("office", "office"), ("classroom", "classroom"),
                       ("apartment", "apartment living room")):
        if _kw in _low:
            _slots["room"] = _room
            break
    _slots.setdefault("room", "room")
    _slots.setdefault("carrier", "the floor")

    _new_prompt, _changes = apply_style(_STYLE_OBJ, prompt_text, _slots)
    if _new_prompt != prompt_text:
        prompt_text = _new_prompt
        _n_in3 = workflow[_prompt_node]["inputs"]
        for _k in ("text", "prompt", "value"):
            if _k in _n_in3:
                _n_in3[_k] = prompt_text
                break
        print(f"🎨 风格 {_STYLE_OBJ['name']}：已套用 {len(_changes)} 项风格层", flush=True)
        for _c in _changes:
            print(f"   · {_c}", flush=True)

if _has_lowpov and _is_lowpov_kw and not _IS_2D_MODEL:
    if "stands upright" not in prompt_text.lower():
        prompt_text = prompt_text.rstrip() + _POSTURE_ANCHOR
        print("🦴 已注入站姿锚定句（防低角度跪姿脑补 → 膝关节反曲）", flush=True)
    workflow[_prompt_node]["inputs"].get("text", workflow[_prompt_node]["inputs"].get("prompt", "")) \
        if False else None
    # 回写（上面那次写入在注入之前，负向/prompt 需要重新写一次）
    _n_in2 = workflow[_prompt_node]["inputs"]
    if "text" in _n_in2:
        _n_in2["text"] = prompt_text
    elif "prompt" in _n_in2:
        _n_in2["prompt"] = prompt_text
    elif "value" in _n_in2:
        _n_in2["value"] = prompt_text
    if _IS_2D_MODEL:
        _neg_final = NEG_BASE_2D
    else:
        _neg_final = NEG_BASE + NEG_ANATOMY
        print("🦴 负向已补畸形词（跪姿/反曲/断肢/畸形脚）", flush=True)
else:
    _neg_final = NEG_BASE_2D if _IS_2D_MODEL else NEG_BASE

# 🔴 风格层叠加的负向词（每个风格带自己的畸形/画风负向）
if _STYLE_LIB_OK and _STYLE_OBJ is not None:
    _neg_final = style_negative(_STYLE_OBJ, _neg_final)

if _neg_node is not None:
    workflow[_neg_node]["inputs"]["text"] = _neg_final
elif "763" in workflow:
    workflow["763"]["inputs"]["text"] = _neg_final

# 🔴🔴 10-31 CFG=1 铁律 = 负向不起作用 = 所有约束必须写进【正向】
#   实测 = 干净负向 vs 45 个崩坏词负向，同提示词同 seed → 像素差 0.00
#   = 所以人体/画质/画风约束全部改成正向的"要什么"追加到 prompt 尾部
#   = Anima 官方"至少 2 句自然语言"的真正用途
if _IS_2D_MODEL:
    _pc = POS_CONSTRAINT_2D
    _cur = ""
    if _prompt_node is not None and isinstance(workflow[_prompt_node].get("inputs"), dict):
        _cur = workflow[_prompt_node]["inputs"].get("text", "") or workflow[_prompt_node]["inputs"].get("prompt", "") or ""
    # 幂等 = 已带就不重复追加
    _missing = [x.strip() for x in _pc.split(",") if x.strip() and x.strip() not in _cur]
    if _missing:
        _new = (_cur.rstrip().rstrip(",") + ", " + ", ".join(_missing)).strip()
        _pin = workflow[_prompt_node]["inputs"]
        if "text" in _pin:
            _pin["text"] = _new
        elif "prompt" in _pin:
            _pin["prompt"] = _new
        print(f"✅ 2D 正向约束已注入 {len(_missing)} 条（CFG=1 下负向无效 = 约束走正向）", flush=True)

# 🔴 09-29 修 seed 随机化失效（实测：同一 brief 每次跑出图 md5 完全相同）
# 旧循环只认 KSampler/KSamplerAdvanced 的 seed/noise_seed 字段，但这个工作流里
#   KSamplerAdvanced(599).noise_seed = ["851", 0] = 是个【连接引用】，不是 int → isinstance 判断永远 False
#   真正的种子在 SeedNode(851).inputs.seed 这个 int 里 → 旧循环一个都没改到
# 结果 = 每次跑都是同一个 seed = ComfyUI 缓存命中 = 出同一张图 = "重跑换姿势"根本换不了。
# 修法 = ① 直连 SeedNode.seed 写随机 ② 跟 KSampler 类节点的连接引用一起改，覆盖其他工作流变体。
# 🔴 10-31 新增：--seed 固定种子（不传 = 保持随机）
#    用途 = 同一提示词批量出多版做 A/B / 复现某张图（分镜、构图对比）
SEED_FIX = _find_arg("--seed")
SEED_FIX = int(SEED_FIX) if SEED_FIX and SEED_FIX.isdigit() else None
_seeded = []
for node_id, node in workflow.items():
    ctype = node.get("class_type", "")
    inputs = node.get("inputs", {})
    # ① SeedNode / 直接持 int seed 的节点
    if ctype in ("SeedNode", "Seed") or (isinstance(inputs.get("seed"), int) and not isinstance(inputs.get("seed"), bool)):
        node["inputs"]["seed"] = SEED_FIX if SEED_FIX is not None else random.randint(1, 10**15)
        _seeded.append(f"{node_id}:{ctype}.seed")
    # ② KSampler 系列的直连 int seed / noise_seed
    if ctype in ("KSampler", "KSamplerAdvanced"):
        for field in ("seed", "noise_seed"):
            if isinstance(inputs.get(field), int) and not isinstance(inputs.get(field), bool):
                node["inputs"][field] = SEED_FIX if SEED_FIX is not None else random.randint(1, 10**15)
                _seeded.append(f"{node_id}:{ctype}.{field}")
            elif isinstance(inputs.get(field), list) and inputs[field]:
                # 形如 ["851", 0] = 连接引用 = 真正种子在源头 SeedNode（已由 ① 改掉）
                src = str(inputs[field][0])
                _seeded.append(f"{node_id}:{ctype}.{field}->引用{src}(已由SeedNode改)")
if not _seeded:
    print("⚠️ 没找到任何可随机化的 seed 节点 = 每次跑会是同一张图 = 请检查工作流", flush=True)
else:
    print(f"🎲 seed 已随机化: {'; '.join(_seeded)}", flush=True)

# 3.5 统一落盘路径（10-29 主人钦定）= Hermes/Yuer<yyyy-MM-dd>（日期在文件名里 = 与主人原写法一致）
# 🔴 为什么脚本要自己填日期：工作流节点里存的是主人原写法「Hermes/Yuer%date:yyyy-MM-dd%/」
#    = GUI 入口由前端 JS 展开（applyTextReplacements / formatDate）
#    但脚本走 API = 不经过前端 = %date:...% 到后端会变字面量（实测落 Hermes/Yuer%date:yyyy-MM-dd%_00001_.png）
#    → 脚本侧客户端算实际日期，产出与 GUI 完全一致（subfolder=Hermes + filename=Yuer2026-10-29_xxx）
import datetime as _dt
_save_prefix = "Hermes/Yuer" + _dt.date.today().isoformat()
for _nid, _n in workflow.items():
    if isinstance(_n, dict) and _n.get("class_type") == "SaveImage":
        _n["inputs"]["filename_prefix"] = _save_prefix
        print(f"📁 SaveImage 节点 {_nid} 前缀 = {_save_prefix}", flush=True)

# 3.6 真·空跑（--check-only）= 在提交 ComfyUI 之前就 exit = 0 算力 0 出图 0 发图 0 落盘
# 🔴 10-31 补：--dry-run 只挡飞书、照样真算图（名字骗人）→ 这里补真正意义的空跑开关
if CHECK_ONLY:
    _pos = workflow.get("144", {}) if isinstance(workflow, dict) else {}
    _txt = ""
    for _nid, _n in (workflow.items() if isinstance(workflow, dict) else []):
        if isinstance(_n, dict) and _n.get("class_type") == "CLIPTextEncode":
            _txt = _n.get("inputs", {}).get("text", "") or _txt
    print("🧪 --check-only：真空跑 = 不提交 ComfyUI = 0 算力 0 出图 0 发图 0 落盘", flush=True)
    print(f"   落盘目标 = /path/to/media/{FILE_STEM}.png", flush=True)
    print(f"   ComfyUI 前缀 = {_save_prefix}", flush=True)
    print(f"   提示词 [{len(_txt)} chars] = {_txt[:600]}", flush=True)
    sys.exit(0)

# 4. 提交 ComfyUI（服务器口径来自 yuer_image_constants，可用 YUER_COMFYUI_SERVER 覆盖）
_T0 = time.monotonic()
payload = {"prompt": workflow}
req = urllib.request.Request(f"{comfyui_url}/prompt", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=30) as resp:
    prompt_id = json.loads(resp.read().decode("utf-8"))["prompt_id"]
_t_submit = time.monotonic() - _T0
print(f"提交成功 prompt_id={prompt_id}", flush=True)

# 5. 轮询（带 break + 状态检查，修 0926 轮询 bug）
start = time.time()
while time.time() - start < 240:
    try:
        with urllib.request.urlopen(f"{comfyui_url}/history/{prompt_id}", timeout=10) as resp:
            history = json.loads(resp.read().decode("utf-8"))
        if prompt_id in history:
            h = history[prompt_id]
            st = h.get("status", {})
            status_str = st.get("status_str", "")
            elapsed = time.time() - start
            if status_str == "success":
                _t_samp = elapsed
                print(f"完成 ({elapsed:.1f}s) success", flush=True)
                _T_DL_MARK = time.monotonic()
                for nid, node_output in h.get("outputs", {}).items():
                    for img in node_output.get("images", []):
                        filename = img["filename"]
                        subfolder = img.get("subfolder", "").replace("\\", "/")
                        view_url = f"{comfyui_url}/view?filename={urllib.parse.quote(filename)}&subfolder={urllib.parse.quote(subfolder)}&type=output"
                        req2 = urllib.request.Request(view_url)
                        dest = f"/path/to/media/{FILE_STEM}.png"
                        with urllib.request.urlopen(req2, timeout=30) as resp2:
                            with open(dest, "wb") as f:
                                shutil.copyfileobj(resp2, f)
                        print(f"落盘 {dest} = {os.path.getsize(dest)} 字节", flush=True)
                # 🆕 09-28 主人钦定「图必须发出来」：出图 success = 立刻飞书真发图（带 caption post，失败降级纯图）
                _T_SEND_MARK = time.monotonic()
                last_send_ok = False
                if DRY_RUN:
                    print("🧪 --dry-run：跳过飞书发图（不写 .sent）", flush=True)
                elif os.path.exists(dest) and os.path.exists(FEISHU_SEND):
                    # 先发带 caption 的 post 图（图+caption 一条气泡）
                    cmd = ["python3", FEISHU_SEND, "image", dest,
                           "--receive-id", RECEIVE_ID,
                           "--receive-id-type", RECEIVE_ID_TYPE]
                    if CAPTION:
                        cmd += ["--caption", CAPTION]
                    r1 = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    out1 = r1.stdout
                    last_send_ok = '"code": 0' in out1 or '"code":0' in out1 or "success" in out1
                    print(f"📤 发图(post+caption) exit={r1.returncode}", flush=True)
                    if not last_send_ok:
                        # 降级：发纯图（不带 caption = 已验证稳定的调用方式）
                        cmd2 = ["python3", FEISHU_SEND, "image", dest,
                                 "--receive-id", RECEIVE_ID,
                                 "--receive-id-type", RECEIVE_ID_TYPE]
                        r2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=60)
                        out2 = r2.stdout
                        last_send_ok = '"code": 0' in out2 or '"code":0' in out2 or "success" in out2
                        print(f"📤 发图(纯图降级) exit={r2.returncode}", flush=True)
                        if not last_send_ok:
                            print(out2[-400:], flush=True)
                    if last_send_ok:
                        print("✅ 图已真发飞书", flush=True)
                        try:
                            with open(SENT_MARK, "w") as sf:
                                sf.write(f"{FILE_STEM}\t{dest}\t{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        except Exception as e:
                            print(f"⚠️ .sent 标记写入失败: {e}", flush=True)
                        # 🔴🔴 10-31 = 额外写「短名 .sent」= 落盘名唯一化后守卫靠它拦重复发图
                        try:
                            with open(SHORT_SENT_MARK, "w") as sf:
                                sf.write(f"{FILE_STEM}\t{dest}\t{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        except Exception as e:
                            print(f"⚠️ 短名 .sent 写入失败: {e}", flush=True)
                else:
                    print(f"❌ 发图条件不满足（落盘不存在或 feishu_send.py 缺失）", flush=True)
                # 🔴 10-05 提速整改：节点级打点（yuer-timing-debug SOP = 0 猜打点量化）
                # 10-05 实测卡点 = 老 B 段 88s 全落在「下载+上传」，以前黑箱 = 主人问「查一下出图时间」只能猜。
                # 焊进脚本 = 以后每次出图 stdout 自带 4 段秒数 = 报耗时有据可依。
                _t_dl = time.monotonic() - _T_DL_MARK
                _t_send = time.monotonic() - _T_SEND_MARK
                _t_all = time.monotonic() - _T0
                print(f"⏱️ [timing] ①提交POST={_t_submit:.1f}s | ②ComfyUI采样={_t_samp:.1f}s | "
                      f"③下载落盘={_t_dl:.1f}s | ④发飞书={_t_send:.1f}s | ⑤墙钟总={_t_all:.1f}s", flush=True)
                # 🔴 10-31 主人正解整改：盲抽降级 = 候选池，不再是正文
                # 旧版 = random.choice(v6_pool) 直接打成 `📩 REPLY:` = 图跟文字两截（池句是场景绑定固定句 = 它不知道这张图拍到了什么）
                # 新版 = stdout 只报「候选池已就绪 + N 条」= 语儿照 brief 从池里挑语义对得上的 = 挑不到自己写
                # 判据 = stdout 里出现 `📩 REPLY:` = 违规 = 这行已废除
                try:
                    import importlib.util
                    base = '~/.hermes/skills/creative/yuer-text-climax/scripts'
                    v6_pool = []
                    for batch in range(1, 7):
                        p = os.path.join(base, f'saohua_v6_batch{batch}.py')
                        if not os.path.exists(p):
                            continue
                        spec = importlib.util.spec_from_file_location(f'saohua_v6_batch{batch}', p)
                        m = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(m)
                        v6_pool.extend(getattr(m, f'SAOHUA_V6_BATCH{batch}', []))
                    if v6_pool:
                        print(f"\n🧺 候选池已就绪：{len(v6_pool)} 条（照 brief 挑语义对得上的 / 挑不到自己写）", flush=True)
                        _cand_path = '/tmp/yuer_saohua_candidates.txt'
                        try:
                            with open(_cand_path, 'w', encoding='utf-8') as cf:
                                cf.write('\n'.join(v6_pool))
                        except Exception as e:
                            print(f"⚠️ 候选池落盘失败: {e}", flush=True)
                    else:
                        print("\n🧺 候选池为空 = 自己写", flush=True)
                except Exception:
                    print("\n🧺 候选池加载失败 = 自己写", flush=True)
                # 🔴 09-28 发图结果硬钩：发图成功 exit 0；发图失败 = exit 4（语儿看到 4 必须立刻补发）
                # 🔴 09-29 补 exit 5 = .sent 守卫命中（已发过 = 拒发，不是失败，别去补发）
                if DRY_RUN:
                    sys.exit(0)
                sys.exit(0 if last_send_ok else 4)
            elif status_str == "error":
                print(f"❌ 出图失败: {status_str}", flush=True)
                sys.exit(2)
            # 没完成 = 继续轮询
    except Exception as e:
        pass
    time.sleep(2)
print("❌ 超时 240s")
sys.exit(3)
