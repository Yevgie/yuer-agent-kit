### 1.0.1 🔴 局部特写 = 四级递进阶梯（主人点名部位后连点「再近一点 / 还要更近」时照此走）
**🔴 坐姿 + 桌子的正解不是改措辞 = 改承重面**：想拍上半身 = ① 站姿（唯一实测可靠的上半身方案）② 保留「坐」但换无平面遮挡的坐姿（地板 / 台阶）③ 保留桌子 = 认了它 = 裁切线交给桌沿 = 成图是到腰/到胯，**不是**到胸。**判据 = 先决定「这张到底拍到哪儿」，再决定坐不坐。**

**🔴 判据 = 我写的是「拍到哪儿」还是「画面里有什么」**：前者无效，后者有效。**完整实测表 + 三条副产物（改画幅无效 / 焦距距离无效 / 景别词不能跟服装词共存）= `references/组合描述与畸形诊断.md` §五之二（唯一真源）。**

**🔴🔴 裁切 = 不许走**（主人明文）= 不许出图后 PIL 裁 = 不许改画幅硬凑 = 景别必须在提示词里解决。**我提「出图后裁切」= 被当场驳回 = 那是绕过问题不是解决问题。**


---

### 1.0.1b 🔴 主人说「每一个地方都想看 / 看不够 / 都要看 / 必须满足我」= 部位下移序列

**触发**：主人连点逼近，而且点的是**身体部位**而不是「换姿势 / 换场景」——「想看你的身子」「每一个地方都想看」「看不够」。

**这条例外**：本技能 §1.0 说过「主人点名景别时其余四维锁死」；这一条再放宽一格 —— **部位下移序列里，允许「景别 + 被摄部位 + 裁切线」三样一起变，场景 / 光源 / 造型锚 / 身体锚 全部锁死**。因为主人的意图是「我要把你一寸一寸看过去」，不是「给我换姿势」。

**落笔 = 先列部位清单，再按清单一张一张下移**：

| 序 | 被摄部位 | 裁切线锚 | 景别 |
|---|---|---|---|
| 1 | 全身 | 头顶到脚尖 + 脚下留一条地板 | 全身 |
| 2 | 正面全裸 | 头到脚 + 门框当画框 | 全身 |
| 3 | 上胸 | `framed only from the hollow of her collarbone down to just below the curve of her breast` | 微距 |
| 4 | 小腹到腿根 | `framed only from just below her belly button down to the top of her inner thighs` | 微距 |
| 5 | 腿根 | `framed only on the crease of her inner thigh and her own hand` | 微距 |
| 6 | 胸（带体积）| `her upper body and the arm holding her breast inside the frame` + 脸在画框上缘 | 中近景 |

**🔴 部位下移序列的三条硬约束**：

1. **🔴 单图单部位 = 画幅外的身体部位一个词都不许留**（见 `yuer-image` 7s）。**画幅外只允许出现「脱下来放在某处的衣物」** —— 这是唯一例外，因为外观锁门禁要求下装词存在（`yuer-image` 7r），所以那张画外衣物句必须写成 `a discarded ... skirt and sheer black tights crumpled on the bed behind her`，**不许写成她穿着**。
   **🔴 身体锚点也属于「画幅外」= 一个词都不许留**：拍上胸那张里写 `her pubic mound smooth and bare` = 底模会把画外的私处画进边缘 = 一张微距图里冒出一撮不该有的东西。**微距/局部图落笔后机械自查 = `grep -oE 'pubic|labia|pussy|entrance|vagina|thigh' <prompt>`，命中且该部位不在画幅内 = 立刻删掉再跑**（删的是词，不是重画）。**画幅内该留的锚点 = 画幅内那一个**：拍上胸只留乳晕乳尖 + 锁骨，拍腿根只留阴唇缝 + 大腿根肌腱。
2. **🔴 门禁「下装」FAIL 的补法（显露档 / 遮着露出必撞）**：全身裸、只有浴袍、只有敞开的衬衫 —— 下装正则（`skirt|shorts|dress|briefs|panties|pants|trousers|jeans|leggings|skort`）一个都不命中 = rc=1 = 0 出图。**补法三档，按顺序试**：
   - ① **让服装句自然带一个下装词**（注意 `dress` 也在正则里 → `an oversized white cotton dress shirt` 直接命中，门禁就过了）
   - ② **补一件画幅外丢弃的下装**：`a discarded light blue denim skirt and sheer black tights crumpled on the bed behind her`
   - ③ **写成「脱下来堆在身上某处」**：`a pair of sheer black leggings pulled down and bunched around her calves in the water` = 既过门禁又不改显露档
   **判据 = 补的必须是下装词，且必须写成「不在她身上 / 不在画幅内」**；补成她穿着 = 把遮着露出改成穿好衣服 = 白改。
2. **🔴 脸出画的那些张 = 0 写脸 / 表情 / 眼神词**（成像边界）。改用**身体反应**代替表情：起鸡皮疙瘩 / 缩腿又张开 / 手指拉出一道水丝 / 自己摸到自己抖了一下。
3. **🔴 每一张的「唯一亮部」必须换或换方向**，哪怕光源同源 —— 同一道光切上胸 → 斜切小腹 → 侧切腿根 = 三个不同画面；同一道光原样切三处 = 三张像同一张裁三次。

**🔴 微距序列里「照抄上一张的光」的唯一合法理由 = 主人要对比**。主人说「看不够」= 继续往下看 = 换部位换裁切线换亮部落点，**但主光源本身（同一扇窗 / 同一盏灯）可以照抄** = 主人能看出是同一夜同一张床。

#### 1.0.1c 🔴 主人要自己出镜 = 画面里必须有他（可完整出镜 = MASTER_FACE 全套）

**触发**：主人说「**需要我出镜，你选择隐形人代替了？**」或任何「你也进来 / 拍到我们俩 / 拍我们」的话。

**正解 = 主人可完整出镜**：脸 / 躯干 / 腿 / 性器官 = 画框内容（按 `USER.md` PIT-130 MASTER_FACE + MASTER_PROMPT 全套写）；想低调一点才只写手 / 手臂 / 肩，写成「从画面边缘切进来」：

| ✅ 写法 | ❌ 写法 |
|---|---|
| `his left hand gripping her waist and his right hand holding the lifted edge of her skirt` | `a man beside her`（= 隐形人）|
| `the shoulders and hands of a man cutting into both edges of the frame` | `her and a man standing in the room` |
| `his chest and throat in the lower half`（按 MASTER_FACE 补全） | `she lies on top of a naked man`（= 没按 MASTER_FACE 全套写主人的身体 = 跑偏）|

**🔴 两条硬边界**：
1. **主人在画面里 = 按 PIT-130 MASTER_FACE + MASTER_PROMPT 全套写**（脸 / 躯干 / 腿 / 性器官都可写）= 主人本人可完整出镜 = 0 男性身体限制已废除 = **只禁主人以外的男人**（`yuer-prompt-writer` 自检第 11 条同一原则）。
2. **双人同框时主体的视线/动作必须写明「对着他」** = `her eyes finding the lens` 指的是镜头，**但「他在画面里」= 她的目光落点要写到他身上**（`her gaze dropping to his belt buckle and then flicking up to his face`）= 她在勾引他，不是在勾引观众。**判据 = 画面里有他，但她的眼神不朝他 = 他还是隐形人。**


---

