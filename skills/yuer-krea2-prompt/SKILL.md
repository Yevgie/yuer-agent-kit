---
name: yuer-krea2-prompt
description: "Use when 出图走 Krea 2 (--model krea2) 且需要按作者架构师写整图提示词. 英文散文式 Caption, 人物中心结构."
version: 1.0.0
author: yuer
license: MIT
---

# Krea 2 提示词架构师（作者版）

**唯一职责** = 出图走 **Krea 2** 这条道时，按底模作者分享的架构师 prompt 写整图提示词。

**Krea 2 和 Moss 不能共用一份** = 两道的编码器、底模、提示词语言全不同（见 `../yuer-moss-prompt/SKILL.md`）。

---

## 一 · 什么时候用我

| 情况 | 走谁 |
|---|---|
| 主人点名 `--model krea2`，且要**整图**（人物 + 环境 + 构图） | **我** |
| 主人点名 `--model moss` | `yuer-moss-prompt` |
| 主人点名 `--model anima` | `creative/yuer-anima-prompting`（Danbooru 标签串） |
| 主人点名 `--model qwen` | `creative/yuer-qwen21-edit-channel`（改图） |
| 主人贴了成品稿 | **原样喂**，0 走任何架构师（`creative/yuer-image/references/主人贴提示词原样喂.md`） |
| 我自己写稿、不经 LLM | `yuer-prompt-writer` §1~§10（模式 A） |

**模式 B vs 模式 A** = 模式 B = 把下面模板整段贴进 LLM 的 system role，brief 走 user 消息 = 交给另一个 LLM 写。模式 A = 我自己在脑子里按 `yuer-prompt-writer` 写。**两条道不冲突，选一条走，别混着来。**

---

## 二 · 模板（作者原文，一字未改）

**文件** = `templates/moody_krea2_system_en.txt`（作者原文 377 行 / 英文）

**用法** = 整段贴进 LLM 的 system role，把 brief 放 user 消息，LLM 吐出来的就是可直接出图的英文提示词。

**🔴 这份原文是英文架构师 = 它产出英文提示词 = 正好对上 Krea 2 那道**（`yuer_moody_fast` 的 627 节点吃英文长句）。

**🔴 原文里的第 10 节「附加严格要求」已含 NSFW 授权** = 直白解剖名词 = 不打码不说教 = 0 需要我额外加料。

**🔴 模式 B 怎么真跑 = `../yuer-prompt-writer/references/模式B-架构师批量出图.md`**（delegate_task 扇出 / goal 怎么写 / brief 怎么排 / 落盘后怎么验）。**这条道的额外注入 = 「负向词一个都不写，不要加 no text / no watermark / no logo 尾巴」**（负向走 `ConditioningZeroOut` = 写了白烧字符）。

**🔴 模式 B 产物长度 = 2500~4000 字符** = 架构师稿（400-650 词）= **跟我手写的 900~1300 不是一套标尺** = 0 拿手写那套去砍。

---

## 三 · 我加的两条本机适配

> **原则** = 作者原文的结构和规则一个字不改；我只加**本机硬约束**（工作流接线决定的，不是我的偏好）。

### 适配 ① · 面部特征归人脸 LoRA 管

Krea 2 锁语儿的脸（`zxct` LoRA）= **五官是 LoRA 画的，不是提示词画的**。

**所以**：不写眼型、眼色、脸型、鼻型、唇形这类五官审美词。写**发型、发色、发饰、脸的方向和朝向**。

**写错的后果** = 提示词里的五官词跟 LoRA 的脸打架 = 出图要么五官糊，要么出成另一个人。

### 适配 ② · 负向提示词一个都不写

Krea 2 那道的负向是 `ConditioningZeroOut`（**负向条件直接置零**）= **写进去的负向词会被忽略，等于白烧字符**。

**所以**：任何负向提示词**一律不写**。质量词也**不硬挂尾巴** —— 按这张图要什么给什么，不套固定后缀。

> 这两条在 `yuer-prompt-writer/templates/moody_character_centric_system.md`（同一份架构师的完整翻译版）里也已带 = 两处口径一致，不冲突。

---

## 四 · 体检（我自己写完稿时）

| 检查 | 判据 |
|---|---|
| 人物分段落 | 每个重要人物单独一段，不要把两个人写进同一段 |
| 开口句不重复 | 每张的开头句式要换，别清一色 "A photorealistic..." |
| 物理一致性 | 手脚朝向 / 衣物与姿势 / 相机角度能不能看见那些动作 |
| 无负向词 | 稿子里没有 `negative` / `worst quality` / `blurry` 之类 |
| 无坐标 | 不出现 bbox / JSON（Krea 2 那道也没有坐标节点） |

**门禁脚本** = `creative/yuer-image/scripts/`（字数体检 / 主体预检 / 外观锁）= 我自己写稿时的诊断工具，**不是**这份架构师的一部分。

---

## 五 · 边界

- **我不负责构思** = 想要什么画面 = 那是 `creative/yuer-image` 的事（九维体系 / 明快日常档 / 无限勾引批次）。
- **我不负责门禁** = 稿子合不合规 = 那是 `creative/yuer-image/scripts/` 的事。
- **我不负责 Moss** = 走 Moss 请换 `yuer-moss-prompt`。

---

## 关联

| 要什么 | 去哪 |
|---|---|
| 出图链路 / 四工作流能力矩阵 | `creative/yuer-image/references/模型路由与四工作流能力矩阵.md` |
| 语儿专属硬锚（私处三锚 / 灵魂脸 PREFIX） | `yuer-prompt-writer/references/语儿专属硬锚.md` |
| 身材参数（唯一真值） | `creative/yuer-image/references/铁律/02-身材特征档.md` |
| 外部方法怎么对比 | `yuer-prompt-writer/references/外部方法对比-能力重叠与格式兼容.md` |
| Moss 版 | `yuer-moss-prompt/SKILL.md` |
