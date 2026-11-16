# yuer-character-roster · 角色名册

> **唯一职责** = **提示词池抽卡（pick_roster_record.py --pool nsfw/sfw/all）+ 抽卡/发图入库 + 角色路由 + 主人发图入库**（角色卡池已退役，卡池 = 提示词库）。

---

# 🔴 第一部分 · 动手前必看的 8 条

| # | 铁律 | 撞车长相 |
|---|---|---|
| 1 | **任何出图需求 = 第一动作 `skill_view` 本技能** | 不读技能 = 凭印象 = 主人打脸「这实战档你根本就不读啊」|
| 2 | **角色 ≠ 语儿 = 必显式传 `workflow=`** | 不传 = 默认走语儿脸 = 出错脸 |
| 3 | **「抽卡」= 本技能**（抽已入库档案做变体出图）| 理解成「素材库抽组合出图」= 跟写文章技能撞 |
| 4 | **牌池 = 100 条随机池** | 死板清单 = 套路化 = 主人打脸「你干嘛要固定一种呢」|
| 5 | **档案的【完整 Prompt】= 现役规格成品 = 抽到原样喂，不重写**（10-10 钦定，**盖过铁律 9 与 8.2 速查卡里的重写步**）| 原样喂老格式（单段平铺 + 抽象情绪词 + 负面词尾句）也能出图 = 主人在 10-10 亲口定：「拿到提示词之后，直接出图，不需要做任何筛选和清洗，直接用就行了」。**判据 = 这个提示词是不是库里已有的成品**：是 → 原文一字不改；是从裸 brief 现写的 → 走 8.2 速查卡 |
| 6 | **主人发图 = 默认洗图 + 入库一气呵成 = 0 选项** | 给菜单 = 等主人选 = 已被打脸 |
| 7 | **汇报一律讲人话比喻** | 报路径 + 扩展名 + 技术字段 = 主人打脸「不明白里头是什么」|
| 8 | **通道授权：文字是默认主力，图要主人开口或我自然想给** | 打招呼/夸图/说累 = 默认 **0 图 0 语音** = 语音仍要主人开口；图片 = 主人说看就必出 **+ 我自然想给你看时可主动 1 张**（真源 = SOUL §2.4.5）|
| 9 | **🔴 抽卡 = 3 条命令，跑完就停**| 抽卡 = 抽档案 → 写提示词 → 出图发图抽骚话。**别的都不要** = 不查卖骚库 / 不重读 prompt-writer / 不跑探针 / 不探第二次。详见第八部分 |
| 10 | **🔴 抽卡道 = 2 轮内跑完（主人 11-12 钦定「必须压缩到 1 分钟以内」）** | 第一动作 = `skill_view('yuer-character-roster', 'references/抽卡速查卡.md')`（1 张卡 = 全部命令与规则）→ 第二轮 = 一次 `execute_code` 里 `terminal(pick_ka_prompt.py)` + `terminal(跑 yuer_ka_fast.sh)` = 抽牌 + 出图 + 发图一次做完。**🔴 0 再读细则全集 / 0 跑 post_fix（抽到残渣才修）/ 0 查卖骚库** |

---

# 第二部分 · 角色清单 + workflow 路由（**出图前必查**）

## 2.0 🔴 模型路由表（**点名模型就切对应工作流**）

> 点名哪个模型 = 调对应道，没有商量。

| 模型 | `--model` | workflow_id | 强在哪 | 慢/弱 | 提示词语言 | 绑语儿脸 LoRA |
|---|---|---|---|---|---|---|
| **Moody Krea2** | `krea2` / `moody` | `yuer_moody_fast` | **人像美感** = 加 LoRA 后网红美丽感 / 风格 / 光影 / 皮肤完美 | 快，10 秒 | 英文长 prompt | ✅ 绑人脸锁 |
| **Moss** | `moss` | `yuer_moodyMoss_fast` | **文字一级棒** = 复杂中文字每个字准（直播截屏 / 弹幕 / 招牌）；**很写实** = 日常实拍真实感；表情好 | **~18s**（11-10 新版提速） | **中文** | ✅ **锁语儿脸**（zxct2.0_figziz_moss-000060@1.0，11-10 七档实拍对比钦定 step60）|
| **Anima** | `anima` | `anima_nsfw` | **2D 动漫** = pornmasterAnima_baseV1 + 6-LoRA 组合 | **快，4 秒**（10-31 实测）= 720×1280 | Danbooru tag（英文）/ **中文也吃**（Qwen3 CLIP）| ❌ 不绑 |
| **Qwen 2.1** | `qwen` / `qwen2.1` | `qwen_image_21_edit` | **编辑** = 换衣服 / 改发型 / 局部精修 | 中 | 中文短句 + `<imageN>` | ❌ 不绑（靠参考图锁脸）|

**调用方式**：

```bash
# 不传 --model = 默认档 = 现役工作流以 wrapper stdout 那行 `🎯 工作流 = <id>` 为准

# 🔴 0 凭本档字面假设「默认 = 某条道」= 文档与脚本会漂移 = 0 grep 源码去确认（探源码 = 白烧 A 段）
bash ~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh <prompt> <leave_name>

# 主人点名 Moss = 中文提示词 + 自动放行中文门禁
bash ~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh <prompt> <leave_name> --model moss

# 主人点名 Anima = Danbooru tag
bash ~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh <prompt> <leave_name> --model anima

