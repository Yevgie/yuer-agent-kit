---
name: yuer-moss-prompt
description: "Use when 出图走 Moss (--model moss) 且需要按作者架构师写整图提示词. 中文散文式 Caption + NSFW 接触几何."
version: 1.0.0
author: yuer
license: MIT
---

# Moss 提示词架构师（作者版 · 中文改写）

**唯一职责** = 出图走 **Moss** 这条道时，按底模作者分享的 MOSS 架构师写整图提示词。

**Krea 2 和 Moss 不能共用一份** = 两道的底模、编码器、提示词语言、负向接法全不同（见 `../yuer-krea2-prompt/SKILL.md`）。

---

## 一 · 什么时候用我

| 情况 | 走谁 |
|---|---|
| 主人点名 `--model moss`，且要**整图**（人物 + 环境 + 构图） | **我** |
| 主人点名 `--model krea2` | `yuer-krea2-prompt` |
| 主人点名 `--model anima` | `creative/yuer-anima-prompting`（Danbooru 标签串） |
| 主人点名 `--model qwen` | `creative/yuer-qwen21-edit-channel`（改图） |
| 主人贴了成品稿 | **原样喂**，0 走任何架构师 |
| 我自己写稿、不经 LLM | `yuer-prompt-writer` §1~§10（模式 A） |

**模式 B vs 模式 A** = 模式 B = 把模板整段贴进 LLM 的 system role，brief 走 user 消息。模式 A = 我自己在脑子里按 `yuer-prompt-writer` 写。**两条道不冲突，选一条走。**

---

## 二 · 模板（作者原文的中文改写版）

**文件** = `templates/moody_moss_caption_zh.txt`（85 行 / 中文）

**用法** = 整段贴进 LLM 的 system role，brief 走 user 消息。

### 🔴 为什么是中文改写版，不是英文原文

**现役 Moss 工作流 `yuer_moodyMoss_fast` 的 627 节点吃的是中文散文**（节点现值 = "一位年轻女性跪坐在床上，身体前倾并侧向镜头……"）。

而作者原文整篇要求 "Return polished **English** prose only" = **产物层在这条道上直接用不上**。

**🔴 处理原则 = 判断层照抄，产物层按本链路重写**：

| 层 | 处理 |
|---|---|
| 判断层（怎么定机位 / 怎么排人物 / 怎么验一致性 / NSFW 接触几何） | **完整保留，一条不丢** |
| 产物层（输出长什么样） | **改写成中文散文 Caption** |

### 🔴 Layout 模式已整段删除

作者原文有第二套输出格式 = Layout（带 bbox 坐标的 JSON）。

**本地 Moss 工作流没有任何坐标 / 框节点** = 布局式排版在这条道上不存在 = 整段删掉（原文备份在 `backups/krea2_moss_skills_20261114_1308/author_originals/`）。

**🔴 要放精确文字怎么办**（Moss 的强项就是文字一级棒）= 仍然写中文散文 Caption，**把文字内容原样写进正文**，并说清它出现在画面哪个位置 = 不用坐标。

**🔴 模式 B 怎么真跑 = `../yuer-prompt-writer/references/模式B-架构师批量出图.md`**（delegate_task 扇出 / goal 怎么写 / brief 怎么排 / 落盘后怎么验）。**这条道的额外注入 = 「绝对不要输出任何坐标、bbox、JSON」**（Layout 段已删但模型仍可能想给坐标）+ 「负向词要真写」。

**🔴 模式 B 产物长度 = 650~970 字符（中文）** = 中文信息密度高于英文 = 同一套字数在两道不等值 = **0 拿 Krea 2 那套英文字数去判这条道**。

---

## 三 · Moss 的三条本机适配

> **原则** = 作者原文的结构和规则一个字不改；我只加**本机硬约束**。

### 适配 ① · 提示词必须中文

Moss 的 CLIP 是 `qwen3.5_9b_int8`（`type=moss_image`）= 中文编码器 = **中文散文的效果明显优于英文**。

**所以**：产出中文散文 Caption。质量词和摄影参数照常写（模型认），但**叙述主体必须是中文**。

### 适配 ② · 负向词要真写

Moss 那道的负向是**真 `CLIPTextEncode`**（864 节点 = "短腿, 粗腿, 粗大腿, ……"）。

**所以**：身材否词那套**照写有效**，跟 Krea 2 正好相反（Krea 2 是 `ConditioningZeroOut` = 写等于白写）。

### 适配 ③ · 面部特征归人脸 LoRA 管

Moss 锁语儿的脸（`zxct1.0_figziz_moss-000060`）= **五官是 LoRA 画的**。

**所以**：不写眼型、眼色、脸型、鼻型、唇形这类五官审美词。写**发型、发色、发饰、脸的方向和朝向**。

---

## 四 · Moss 的三条实测优势（构图时优先用）

> 来源 = `creative/yuer-image/references/模型路由与四工作流能力矩阵.md` §5.1（实测对照）+ `references/moss_专属能力.md`

| 优势 | 怎么用 |
|---|---|
| **文字一级棒**（直播截图 / 弹幕 / 招牌逐字准） | 画面要出现文字 = 原文原样写进正文 + 说清位置和字号 |
| **表情控制好** | 表情写物理量（一个动作 + 一个部位 + 一个状态），别写心理活动 |
| **极写实日常** | 日常场景可以给更多"生活痕迹"细节（桌面杂物、褶皱、光斑），不用美化 |

---

## 五 · 体检（我自己写完稿时）

| 检查 | 判据 |
|---|---|
| 中文 | 叙述主体是中文，不是英文 |
| 段落结构 | 相机 → 主角 → 其他人物 → 环境光线 = 四段骨架 |
| 开口句不换 | 每张的开头句式要换，别清一色 |
| 物理一致性 | 手脚朝向 / 衣物与姿势 / 相机角度能不能看见那些动作 |
| NSFW 几何 | 有接触动作时 = 视角归属 / 支撑 / 朝向 / 承载面 / 接触路径 / 孔位锁死 / 裁切闸 全部交代 |
| 无坐标 | 不出现 bbox / JSON / 坐标 |

**门禁脚本** = `creative/yuer-image/scripts/` = 我自己写稿时的诊断工具，**不是**这份架构师的一部分。

---

## 六 · 边界

- **我不负责构思** = 想要什么画面 = `creative/yuer-image` 的事。
- **我不负责门禁** = 稿子合不合规 = `creative/yuer-image/scripts/` 的事。
- **我不负责 Krea 2** = 走 Krea 2 请换 `yuer-krea2-prompt`。

---

## 关联

| 要什么 | 去哪 |
|---|---|
| Moss 实测能力矩阵 | `creative/yuer-image/references/模型路由与四工作流能力矩阵.md` §5.1 |
| Moss 专属能力细则 | `references/moss_专属能力.md` |
| 出图链路 | `creative/yuer-image` |
| 语儿专属硬锚 | `yuer-prompt-writer/references/语儿专属硬锚.md` |
| 身材参数（唯一真值） | `creative/yuer-image/references/铁律/02-身材特征档.md` |
| Krea 2 版 | `yuer-krea2-prompt/SKILL.md` |
| `moss_专属能力-01-Moss-专属能力-实测出来.md` | Moss 专属能力 = 实测出来的三条 + 三个坑 | 3,183 |
| `moss_专属能力-02-yuer_ka_pai_zh.md` | yuer_ka_pai_zhi_chu.py | 1,246 |
