
> **本档已拆分** = 全文 4,437 字 → 2 份（每份 ≤3800 字）= 只搬不改写 = 下表为原文索引。

| 新档 | 原章节 | 字数 |

---

<!-- 摊平自：moss_专属能力-01-Moss-专属能力-实测出来.md -->

# Moss 专属能力 = 实测出来的三条 + 三个坑

> **唯一职责** = 记 Moss 这条道**实测**跟别的道不一样的地方 = 写 Moss 提示词时优先用这些、避开这些坑。
>
> **来源** = `creative/yuer-image/references/模型路由与四工作流能力矩阵.md` §5.1（实测对照）+ 现役工作流 `yuer_moodyMoss_fast.json` 逐节点核。

---

## 一 · 三条优势（构图时优先用）

### ① 文字一级棒

Moss 的杀手锏 = **逐字准确**。直播截图 / 带弹幕的界面 / 带中文 UI 的写实日常场景 = 别的道做不了的精度。

**怎么写** = 文字内容**原样写进正文**，并说清它出现在画面哪个位置、什么字号、什么颜色、什么底。

```
画面右下角有一块半透明的手机通知栏，白底黑字写着「今晚七点，别忘了」，字号很小，边缘被手指遮住一角。
```

**🔴 不用坐标** = 这条道没有框节点（见 `../SKILL.md` §二）。

### ② 表情控制好

Moss 的脸（LoRA 画的）表情比 Krea 2 更可控 = 值得多给表情细节。

**怎么写** = 表情写**物理量**，不写心理活动。

| ❌ | ✅ |
|---|---|
| 她看起来很犹豫 | 她的下唇被牙齿轻轻咬住，右眼眼皮比左眼高一点点 |
| 带着挑衅的笑 | 嘴角向一侧歪着，露出左边一颗犬齿，眼睛没有跟着笑 |

### ③ 极写实日常

Moss 的日常场景真实度是它最强的一档 = **别把它拍干净**。

**怎么写** = 该给的"生活痕迹"给足 —— 桌面杂物、衣物褶皱、皮肤上的油光、窗外漏进来的杂光。Krea 2 那道是网红精修感，Moss 这道才是"随手拍的"。

---

## 二 · 三个坑（写完自查）

### 坑 ① · 低角度 POV 不锚站姿 = 膝盖反曲

**真根因（实测 agnes 反推，非猜测）** = Moss 遇到 `Extreme low-angle POV` + `looking up from ... steps` 会**脑补跪姿** = 大腿水平展开 + 膝盖反折。

**两层修法** = 已在 `yuer_ka_pai_zhi_chu.py` 自动注入 = 0 靠手写：

| 层 | 做法 | 触发条件 |
|---|---|---|
| ① 站姿锚定句 | 尾部追加 `She stands upright on the step, both legs straight and slightly apart, knees only slightly bent, both feet planted flat on the ground.` | 低角度 + 台阶类场景 |
| ② 畸形负向 | 负向补 `kneeling, crouching, squatting, bent knees, hyper-extended knees, broken joints, twisted joints, extra legs, extra limbs, fused fingers` | 同上 |

**🔴 修完必验** = `scripts/yuer_verify_image.py`（agnes 主 + 本地 Qwen 兜底）= 直接问「几条腿几只脚几只手？膝盖是站立还是跪姿？」

### 坑 ② · 监控绿调 / 颗粒 / 桶形畸变 = 只有 Moss 给

**实测对照**（同提示词双模型）：

| 要素 | Moss | Krea2 |
|---|---|---|
| 低角度仰拍 | ✅ | ✅ |
| 背后视角 | ✅ | ✅ |
| **监控绿调** | ✅ | ❌ 丢失 |
| **颗粒 / 隔行扫描线** | ✅ | ❌ 丢失 |
| **桶形畸变** | ✅ | ❌ 丢失 |

**机制** = Krea 2 优化的是「网红精修感」（反推原话 `minimal grain`）= 监控味天生被它抹平。

**判据** = 提示词里出现监控 / 偷拍 / POV / 绿调 / 低画质这类词 = **只能走 Moss** = 走 Krea2 = 白跑。

### 坑 ③ · 不能走批量 = 50s/张 × N 张 = 前台超时 + 同名双发

**实测** = 单张 50~55s（11-10 换 8 步写实底模后提速到 ~18s，但批量仍需分批）。

**🔴🔴 铁律 = 同一批 leave_name 0 并发 / 0 重跑** = 后台批次与前台批次**同名 = 落盘互相覆盖 + 主人手机双发**（`.sent` 守卫只在发图那一刻拦，落盘早就撞了）。

---

## 三 · 本机接线事实（跟别的道的差别）

| 项 | Moss | Krea2 |
|---|---|---|
| 底模 | `PornMaster_Moss_MIX_V2_int8_convrot` | `moodyKrea2Mix_v70_nvfp4` |
| CLIP | `qwen3.5_9b_int8`（`type=moss_image`） | `qwen3vl-4b-abliterated`（`type=krea2`） |
| **提示词语言** | **中文** | **英文长句** |
| 负向接法 | **真 CLIPTextEncode**（864 节点 = 身材否词那套） | `ConditioningZeroOut`（**写负向 = 白烧字符**） |
| 人脸锁 | ✅ `zxct2.0_figziz_moss-000060` | ✅ `zxct2.4_fizgig_krea2` |
| 坐标 / 框节点 | ❌ 无 | ❌ 无 |

**✅ 口径已统一（11-14 修）** = `creative/yuer-image/references/模型路由与四工作流能力矩阵.md` §5.1 原有一句「Moss = 不锁脸」= **已过期**（11-10 起 Moss 也锁语儿脸）= **本轮已改掉**（现写法 = 「**锁脸** = 语儿的脸（`zxct2.0_figziz_moss-000060`）= 出图直接就是语儿，不用改走 Krea2」）= 与 §3.1 一致 = 全库 0 矛盾。

> **注** = 矩阵第 40 行那句「不锁脸 = 出路人/别人的脸」**不是矛盾** = 那是另一套机制（要出别人的脸 = 走 `yuer_run_nolora.py` 把 LoRA 全关）= 别混。

---

## 四 · 🔴 中文稿 0 翻译（11-14 修的真 bug）

**原状** = `yuer_ka_pai_zhi_chu.py` 里的中文自动翻译是**无条件触发**（稿子里有中文就翻英文）= **走 Moss 也被翻**。

**两个后果**：

1. **违反矩阵 §5.1**「Moss = 中文提示词原样喂 = 0 翻译成英文（它的中文能力就是卖点）」= 文档说的和代码做的对不上。
2. **语义翻错** = 实测「下身赤裸」被翻成 `no lower clothing`（= 没穿下装 ≠ 赤裸）= 根因在社区词典 `tag_zh_index.json` 的 `zh2en`（125,426 键）= `下身赤裸 → ['no lower clothing']`。

**修法（11-14 已落）** = 翻译只对**不吃中文**的道生效；中文原生道走白名单跳过。

```python

---

<!-- 摊平自：moss_专属能力-02-yuer_ka_pai_zh.md -->

# yuer_ka_pai_zhi_chu.py
_CN_NATIVE_WORKFLOWS = ("yuer_moodyMoss_fast",)
if (re.search(r"[\u4e00-\u9fff]", prompt_text)
        and WORKFLOW_NAME not in _CN_NATIVE_WORKFLOWS):
    ...  # 翻译
```

**实测验证** = Moss 道归档的 prompt = 中文原文（0 英文字符）｜Krea2 道照旧翻译（stdout 仍打「中文已翻译 1 段」）= **两条道都没误伤**。

**🔴 残留 = 已修** = 社区词典 `下身赤裸 → ['no lower clothing']`（= 没穿下装 ≠ 赤裸）**已改**：

```
zh2en["下身赤裸"] = ["nude lower body", "naked lower body", "no lower clothing"]
```

（正确译法前置，**原词保留** = 不破坏别人可能的引用；键数 125426 / 141375 一个没少。）

**顺带挖出更大的一个** = 那词典的 `zh2en` 侧有 **389 个键带 `}}}` / `]}` 抓取残留**（社区原帖的括号注释没清干净）= 实测「上身赤裸」模糊命中「袈裟且上身赤裸」→ 选出 `kasaya}topless` = 垃圾 tag 进提示词。

**修法 = 不改词典、改 `_pick`**（`zh_translate.py`）= 加一条过滤：候选里含 `}` `]` `【】` = 不是 tag = 整条丢掉。

**为什么改代码不改词典** = 词典是社区上游产物 = 下次重新抓取就白改 = 治本要治在**消费端**。

**验证** = 全库 125,426 键扫过 = **0 个脏候选还能被 `_pick` 选中**；正常词一个没误伤（「模糊→blur」「放屁→fart」「高马尾→high ponytail」都仍选到干净那条）。

---

## 关联

| 要什么 | 去哪 |
|---|---|
| 完整能力矩阵 + 四工作流路由 | `creative/yuer-image/references/模型路由与四工作流能力矩阵.md` |
| 畸形修法脚本 | `creative/yuer-image/scripts/yuer_ka_pai_zhi_chu.py` |
| 出图后验图 | `creative/yuer-image/scripts/yuer_verify_image.py` |
| LoRA 审计真值 | `creative/yuer-image/scripts/yuer_lora_audit.py` |
| 架构师正文 | `../templates/moody_moss_caption_zh.txt` |

---
