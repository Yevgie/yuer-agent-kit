# 出图提示词编写

**一句话**：一个点 = 一句话 = 一次。

**输入** = 画面想法 / 中文 brief / 主人贴的成品稿　**输出** = 一段连续的英文散文，可直接出图。

**细则档** = `references/语儿专属硬锚.md`（脸部参数 ≤200 字 / 五官禁区 / 表情物理化）｜**身材参数 + 私处三锚 + 乳头锚 + 皮肤锚** = `creative/yuer-image` 技能的 `references/铁律/02-身材特征档.md`（唯一真值）｜**出图链路** = `creative/yuer-image`。

**🔴 外部方法文档对比** = `references/外部方法对比-能力重叠与格式兼容.md`（主人发来作者/社区的提示词方法 = 先查库里有没有 → 量能力重叠不量行数 → 验输出格式跟现役工作流兼不兼容）。

---

## 0 三条底线

1. **全英文，0 中文。** 中文词会被底模忽略或误读。
2. **连续散文，不分段、不列表、不编号。** 分段会让底模把每段当成独立场景。
3. **不重复。** 同一个视觉点只写一次。写第二遍不会加强，只会抢走别的概念的注意力。

**🔴 减法（11-15 主人钦定）= 骨架不变，其余一律少** = 脸部段 ≤ **200 字**、体型段 ≤ **200 字**（唯一真值在 `creative/yuer-image` 技能的 `references/铁律/02-身材特征档.md`）= **约束越少 = 创意越活 = 堆得越多越死板** = 别为了「更完整」加身体句 = 想显什么走机位/景别/服装。

---

## 1 落笔前：先把画面想圆

| # | 问题 | 答不上来的后果 |
|---|---|---|
| 1 | 这张图要让人**看见的那一件事**是什么？ | 画面散，没有主角 |
| 2 | 她在**哪、几点、什么天气**？ | 光和场景对不上 |
| 3 | 她**身体的重量压在哪**？ | 人飘，像贴上去的 |
| 4 | 画面里**最亮的那块**是什么？ | 平光，没有视觉落点 |
| 5 | **意外的一瞬**是什么？ | 摆拍感，像证件照 |

---

## 2 点表：写之前先列点

一张图 = 5~8 个点，每个点写一句话。

| # | 点 | 必须回答 |
|---|---|---|
| 1 | 身份 | 她是谁（年龄 / 气质 / 地域），一句 |
| 2 | 姿势 | 重量在哪 + 脊柱怎么走 + 手在干什么 |
| 3 | 服装 | 上装 / 穿着方式 / 下装 / 鞋，按视觉权重排 |
| 4 | 发型 | 形状 + 状态（贴 / 散 / 被风吹）|
| 5 | 光 | 唯一光源 + 方向 + 色温 + 最亮落在哪 |
| 6 | 相机 | 焦段 + 距离 + 机位高度 + 画面切在哪 |
| 7 | 环境 | 一句收拢：近景一件 / 中景一件 / 远景一层 |
| 8 | 表情 | 一句，三个物理量 |

**点表里没出现的点，正文不许出现。列了点就必须写。** 特写只有 4 个点（脸 / 发 / 光 / 相机）= 点少不是缺项。

---

## 3 美学：把"感觉"翻译成"选择"

### 3.1 先定气质，再选参数

| 想要的感觉 | 最亮那块 | 光比 | 色温 | 构图密度 |
|---|---|---|---|---|
| 干净通透 | 大面积柔光（窗 / 白墙）| 1:2 | 5500-6000K | 低，留白多 |
| 暧昧私密 | 一小块硬光打在皮肤上 | 1:8 | 3200-3800K | 中，暗部留细节 |
| 高级冷峻 | 金属 / 玻璃的高光边 | 1:16 | 4800-5200K | 低，几何线条 |
| 温柔日常 | 逆光透纱 / 发丝光 | 1:3 | 4000-4500K | 中，生活物件 |
| 戏剧紧张 | 侧逆光切脸 | 1:8 以上 | 冷暖对撞 | 高，前景遮挡 |

**一张图只用一行。混两行 = 风格不成立。**

### 3.2 色彩三分

主色六成（墙 / 天 / 地）｜辅色三成（服装 / 家具）｜点缀一成（一处红 / 一处金）。**点缀色只写一个**，写三个等于没有点缀。

### 3.3 构图四招，选一个用

前景遮挡 ｜ 框架 ｜ 视线留白 ｜ 对角。**四招同时用 = 画面打架。**

### 3.4 影调要有一条分界

`the light falling off sharply at her waist, everything below sinking into shadow` —— 这一句比十个 `dramatic lighting` 有用。

---

## 4 姿态：自然的三条物理

### 4.1 重心必须落在支撑面内

| 姿势 | 写法 |
|---|---|
| 单腿站 | `her weight over her left foot, the right knee bent and the heel lifted` |
| 双腿站 | `her weight even across both feet, hip-width apart` |
| 坐 | `her weight pressed into her left hip, her right foot flat on the floor` |
| 倚 | `leaning her shoulder into the wall, one foot crossed behind the other` |
| 卧 | `her weight spread from shoulder to hip to the outside of one ankle` |

### 4.2 脊柱是一条 S，不是一根棍

`a soft S running from the base of her skull down through the small of her back, her chest lifted and her shoulders settled back`

### 4.3 手必须有一个任务

| 场景 | 写法 |
|---|---|
| 坐 | `her palm flat on the cushion beside her hip, fingers slightly spread` |
| 站 | `her fingertips resting on the windowsill` |
| 走 | `her hand closed loosely around the strap of her bag` |
| 卧 | `one arm folded under the pillow, the other draped across her waist` |
| 撩发 | `her fingers pushing back a loose strand, the hand half hidden in her hair` |

**一只手只干一件事。** 另一只手给一个静态任务，或让它被遮挡。**不要两只手都在做复杂动作。**

### 4.4 动势残留

`just as her fingertips touch the surface` / `the fabric pulled taut toward her shoulder` / `her hair still swinging from the turn`。**一条就够。**

---

## 5 表情：一句，三个物理量

**不写"微笑""生气"** —— 那是标签，模型只给一个僵硬的嘴角。写肌肉在做什么：

| 情绪 | 三个物理量 |
|---|---|
| 忍着笑 | 下唇被牙轻轻咬住 + 眼角皱起 + 鼻翼微微张开 |
| 疲惫 | 眼皮半垂 + 嘴角向下 + 下颌放松 |
| 警觉 | 眼睛睁大 + 眉毛上抬 + 嘴唇微张 |
| 倔 | 下巴抬起 + 抿嘴 + 眼睛不眨 |

装进一句：`her lower lip caught between her teeth, the corners of her eyes creased, her nostrils flaring slightly` —— **一句装三个，不装五个。**

**五官不单独描述。** 不写「双眼皮 / 高鼻梁 / 鹅蛋脸」= 会被读成一堆互相打架的特征。

---

## 6 服装：一句装，按权重排

**不超过 4 件**｜**最想被看见的那件放最前**｜**每件都要带材质或状态**（`satin` / `sheer` / `crumpled` / `wet`）｜**穿着方式比衣服本身重要**（`slipped off one shoulder` / `hem riding up`）。

