---
name: yuer-camera-composition-style
description: Use when brief含 POV极低/广角/透视/构图/王座/全身比例/腿长. Camera composition rules. v1.1 加第⑥节 = 全身/背影景禁广角近距（透视失真 = 上身过长腿被压短）+ 构图防裁句 + 头身比算式段。
author: 语儿
version: v1.1 (2026-10-05 新增第 ⑥ 节 = 全身景焦段禁广角 + 构图防裁 + 头身比算式)
tags: [prompt, style-synthesis, composition, perspective, camera-position, focal-length, 实战486]
metadata:
  hermes:
    tags: [prompt, style-synthesis, composition, perspective, camera-position, focal-length, 实战486]
    related_skills:
      - prompt-style-synthesis
      - yuer-back-view-style
      - yuer-run-one-brief
      - yuer-image
      - creative/yuer-image
---

# yuer-camera-composition-style · 画面构图控制文风金标准

> **🔴 实战 486 主人正解打脸原话**：
> 「**这段提示词控制画面很强 llm 节点的系统提示词应该向这方面学**」
>
> = 主人正解钦定：从主人手写的高控制力 prompt 中**提炼画面构图技法** = 沉淀为独立子伞 = 联动 5 大出图技能

> **⚠️ 当前基于 1 个示例**（POV 极低广角 cos 沙发王座）= 技法清单 1.0 = 后续 N 个示例可补全（v1.0 5 件套必全）

---

## 来源

基于主人 08-26 提供的 1 段 POV 极低广角 cos 沙发王座高控制力中文 prompt 提炼 = 5 条画面构图技法金标准。

完整原文（实战档留底）：
> 采用超广角镜头以 POV 低角度仰视，镜头几乎贴着地板从下往上对准她，广角透视让最靠近镜头的那只靴子在画面前方被极度放大，双腿随透视向远处急速收束，形成强烈纵深感；浅景深将背景柔化为暖色光斑。温暖午后阳光透过白色纱帘漫射进来，在她肩头与脸颊勾出柔和的暖色轮廓光，红色披风在光下泛着浓郁暖调，皱起的沙发坐垫在身下投下柔软阴影；整体暖调低明度，色彩浓郁，氛围慵懒而带着居高临下的俏皮。…她端坐在客厅沙发的坐垫边缘，像坐在王座上一样…构图采用对角线，仰视的广角透视线条自画面下方的大靴子一路向上汇聚到她的脸庞，人物位于画面中上方，前景的大靴子与耸起的交叠膝盖构成强烈的透视纵深感与王座般的压迫感。

---

## 正面约束唯一正确路径

凡是 brief 含以下触发词 = **必调用本技能**：

- **机位**：`POV 极低` / `极低广角` / `extreme low angle` / `worm's-eye view` / `low-angle POV` / `广角` / `ultra wide` / `fisheye`
- **透视**：`透视收束` / `perspective convergence` / `vanishing point` / `leading line` / `透视纵深` / `perspective depth`
- **构图**：`对角线构图` / `diagonal composition` / `前景放大` / `foreground element` / `王座` / `throne` / `压迫感` / `oppressive presence`
- **光 / 美**：`不够美丽` / `不够美` / `太普通` / `没感觉` / `逆光` / `backlit` / `轮廓光` / `rim light` / `光影` / `氛围感` / `一整块光` / `大片暗`
- **焦段**：`ultra wide 16mm` / `24mm wide` / `35mm` / `85mm portrait` / `135mm telephoto` / `telephoto compression`

---

## 5 条画面构图技法金标准（一切）

### ① 机位强制（Camera Position Forcing）· 三轴坐标法

**不要写「low angle」「high angle」这种角度词 = 要写相机相对场景的空间坐标**。

**三轴坐标钦定**：
- **HEIGHT 高度轴**：floor-level（贴着地面）/ waist-level（腰平）/ eye-level（眼平）/ overhead（俯视）/ bird's-eye（鸟瞰）/ worm's-eye（虫视）
- **DISTANCE 距离轴**：extreme close-up（特写）/ close-up（近景）/ medium（中景）/ full（全景）/ wide（远景）
- **ORIENTATION 方向轴**：front（正面）/ side（侧面）/ back（背面）/ low-angle（仰视）/ high-angle（俯视）

**原 prompt 例子**：
> 「镜头几乎贴着地板从下往上对准她」= `the camera positioned almost touching the floor looking up` = **HEIGHT=floor-level + ORIENTATION=low-angle**

**❌ 反例（vague 角度词）**：❌ `low angle` / ❌ `from below` / ❌ `looking up`

**✅ 正解（空间坐标）**：✅ `extreme low angle shot, the camera almost touching the floor looking up` / ✅ `worm's-eye view from floor level`

### ② 透视收束（Perspective Convergence Forcing）· 三段式前景/中景/远景

**不要写「strong perspective」这种空话 = 要写三段式前景/中景/远景强制透视感**。

**三段式钦定**：
- **前景（foreground）**：放一个大主体（靴子/手/道具）+ 用广角畸变让它「被极度放大」
- **中景（midground）**：主体人物的身体部分 + 透视收束的过渡段
- **远景（background）**：汇聚点（vanishing point）+ 远端虚化

**原 prompt 例子**：
> 「最靠近镜头的那只靴子在画面前方被极度放大」= **foreground element + wide-angle distortion**
> 「双腿随透视向远处急速收束」= **midground legs receding into distance**
> 「仰视的广角透视线条自画面下方的大靴子一路向上汇聚到她的脸庞」= **vanishing point at her face**

**❌ 反例（空话）**：❌ `strong perspective` / ❌ `dramatic perspective` / ❌ `deep perspective`

**✅ 正解（三段式）**：✅ `wide-angle distortion makes the foreground boot oversized, the perspective lines converging from the foreground up to her face as the vanishing point, legs receding sharply into the distance`

### ③ 构图骨架（Composition Skeleton Forcing）· 线型 + 主体位置 + 情绪耦合

**不要写「dynamic composition」= 要写具体构图原理 + 主体物理位置 + 情绪目的**。

**线型钦定**：
- `diagonal`（对角线）= 王座压迫 / 动感
- `S-curve`（S 曲线）= 优雅 / 婀娜
- `rule-of-thirds`（三分法）= 平衡 / 自然
- `leading-lines`（引导线）= 视线聚焦
- `frame-within-frame`（框中框）= 聚焦 / 私密
- `symmetric`（对称）= 庄严 / 神圣
- `asymmetric`（不对称）= 张力 / 紧张

**主体位置钦定**：
- `upper-center` / `lower-center` / `left-third` / `right-third` / `edge`

**情绪耦合钦定**（独创 = 构图-情绪绑定）：
> 「前景的大靴子与耸起的交叠膝盖构成强烈的透视纵深感与王座般的压迫感」= **构图的目的 = 情绪**

**原 prompt 例子**：
> 「构图采用对角线」= `diagonal composition lines`
> 「人物位于画面中上方」= `subject positioned upper-center of frame`
> 「王座般的压迫感」= `throne-like oppressive presence`

**❌ 反例（无情绪绑定）**：❌ `diagonal composition`（只写线型）

**✅ 正解（线型 + 位置 + 情绪三件套）**：✅ `diagonal composition with the subject positioned upper-center, the foreground enlarged boot and stacked knees creating throne-like oppressive presence through perspective convergence`

### ④ 焦段与畸变（Focal Length & Distortion Forcing）· 焦段 → 构图效果绑定

**不要写「portrait lens」这种模糊词 = 要写具体焦段 + 焦段对应的构图效果**。

**焦段钦定**（焦段 → 构图效果映射表）：

| 焦段 | 类型 | 畸变 | 景深 | 构图效果 | 情绪适配 |
|---|---|---|---|---|---|
| `16mm` | ultra-wide | 极强 | 大 | 前景夸张放大 + 强透视 | 戏剧 / 王座 / 压迫 |
| `24mm` | wide | 强 | 大 | 透视夸张 + 广角视野 | 街拍 / 环境人像 |
| `35mm` | natural wide | 弱 | 中 | 自然视角 | 日常 / 纪实 |
| `50mm` | standard | 无 | 中 | 标准人像 | 平衡 / 自然 |
| `85mm` | portrait | 弱 | 浅 | 面部压缩 + 焦外虚化 | 肖像 / 情绪 |
| `135mm` | telephoto | 弱 | 浅 | 空间压缩 + 远距离感 | 偷拍 / 私密 |
| `200mm` | super-telephoto | 极弱 | 极浅 | 强压缩 + 奶油虚化 | 远景偷拍 |

**❌ 反例（无焦段）**：❌ `wide-angle shot`（无畸变强度）

**✅ 正解（焦段 + 效果绑定）**：✅ `16mm ultra-wide lens exaggerates the foreground boot with extreme distortion, the perspective lines converging sharply to her face`

#### 🔴 ⑥ 全身/背影景 = 焦段不能取广角（构图失真反噬）

**真根因**：上表把 16/24mm 标为「透视夸张 + 前景放大」= 只讲优点。但**全身景一旦用广角 + 近距**，透视把下半身放大、上半身压缩 = 出图必然「上半身过长 + 腿被压短」。**同一张焦段表对半身/特写是优点，对全身景是毒。**

**🔴 全身/背影/大全身 = 焦段换长焦 + 拉远 + 机位压低**：

| 项 | 值 | 理由 |
|---|---|---|
| 焦段 | `135mm f/3.5 at f/4.0` | 长焦压缩 = 头身比不失真 |
| 距离 | `four to five meters directly behind her` | 近距 = 透视变形 |
| 机位高 | `camera at knee height` | 与胯线齐 = 视觉上腿不被顶高 |
| 禁 | 16/24/35mm + 近距全身 | 全身比例镜头头号杀手 |

**✅ 全身景正解句**：`a 135mm f/3.5 lens at f/4.0 from five meters directly behind her, camera at knee height, vertical orientation`

**🔴 全身景必配「构图防裁」** = 不给头顶和脚下留边 = 视觉自动压缩 = 腿又变短：

```
her entire body from the crown of her head to the soles of both feet contained inside the frame
with a clear band of ceiling above her head and a wide band of carpet below her heels,
no cropping at top or bottom, vertical orientation.
```

**🔴 比例仍不达标 = 补「头身比算式段」**（焦段只是必要条件，不是充分条件）：

```
Her proportions are exact and eight-head-tall,
her legs measuring four full head-lengths from the crotch crease to the floor so they occupy
exactly half her height, her torso three head-lengths from the crotch crease to the top of her head,
her hip line sitting exactly at the vertical midpoint of the frame with equal height above and below it.
```

长腿版（**v1.4 现役**，实测出图比例正确）：`ten head-lengths from crown to floor` + 腿 `five and a half full head-lengths so they occupy more than half her total height` + 胯线 `slightly below the vertical midpoint with visibly more height below it than above it`，**外加** `the knee crease sitting at mid-thigh and clearly separated from where a normal knee would fall`（衣服不给长度参照 = 模型算不出腿长）。真值见 `yuer-image/references/铁律/02-身材特征档.md`。

**🔴 修正顺序**：短 → 换长焦 + 拉远 + 构图防裁（不动镜头焦段以外的东西）→ 还短 → 头身比算式推长腿版。**每轮只改这两处 = 不重写整篇。**

#### 🔴 ⑥-1 景别三级 = 主人钦定「半身和特写很美，不要光出全身」

> **主人原话**：「全身记得腿长一点，短腿不好看。…半身和提特写很美，不要光出全身。」

**这不只是审美偏好 = 它同时改了「腿长锚的写法」和「批次结构」两件事。**

| 景别 | 写法（中/英） | 腿长要不要写 | 焦点落在 |
|---|---|---|---|
| **全身** | `全身构图，从头顶到鞋跟完整入画` / `full body shot, head to heel` | **必写**（头身比算式段 + 构图防裁句）| 比例 + 服装全身 |
| **半身** | `半身景别，取景从头顶到大腿中段` / `medium shot, from head to mid-thigh` | **写**（但不需要头身比算式）| 腰胯线 + 上半身 |
| **特写** | `特写景别，取景从头顶到锁骨下方` / `close-up portrait, from the top of her head to just below her collarbones` | **0 写**（拍不到）| 脸 / 肩颈 / 手 |

**🔴 批次要混景别，不能一色全身**：一批 5 张 = **至少 2 张非全身**（半身 + 特写各来一张）= 主人看 5 张不会觉得「都是站桩全身照」。判据 = 出 5 张前先看这 5 张的景别列 = 全是全身 = 自己先改。

**🔴 景别词 = 底模不认 = 门禁认 = 出图不一定认**：写了「半身景别」出来仍是全身 = **底模对景别词的服从度低** = 景别靠**取景描述**（`framing from the top of her head to just below her collarbones` = 具体到哪个解剖位置）比靠景别名（`close-up`）更靠得住。**正解 = 景别名 + 取景范围两句一起写**。

#### 🔴 ⑥-2 腿长锚 = 服务端没有腿长滑块 = 只能写进 prompt

**服务端全部 LoRA 里没有「腿长 / 比例」滑块**（只有胸 / 湿度 / 精液转换 / Realism / Waterglowskin 几个）= **腿长改不了 = 只能靠 prompt 写** = 别去找滑块，浪费时间。

**🔴 半身 / 特写景也能写腿长（不是只有全身才需要）**：半身取到大腿 = 腿根线条 = 大腿长度已经是画面内容 = 写一句就够。

**中文版（实测出图有效，视觉验收确认「腿明显长于躯干」）**：

```
她的腿明显比躯干长一大截，大腿修长笔直，小腿线条紧实，膝盖位置偏高，
整条腿从胯到脚形成一道很长的直线。
```

**英文版**：

```
her legs are noticeably longer than her torso, long straight thighs, firm calves,
a high knee line, one unbroken line running from hip to heel
```

**🔴 全身景的腿长 = 这句 + 头身比算式段 + 构图防裁句 = 三件齐**；半身景 = 只用这句；特写 = 一句都不写。**判据 = 取景照不到腿 = 写腿长 = 纯浪费字符 = 拉低其余维度的权重。**

**🔴 腿长不够时的排查顺序**（别一上来就改姿势）：① 焦段够不够长（<35mm 近距 = 腿必被压短）→ ② 距离够不够远（≤3m = 透视变形）→ ③ 构图防裁句在不在 → ④ 头身比算式段在不在 → ⑤ 全身还短才推长腿版。**每轮只改一处 = 不重写整篇。**

#### 🔴 ⑥-3 「美」不等于「信息全」= 批次要混景别

**主人说「半身和特写很美」= 他在挑好看的 = 不是在挑信息全的 =** 一批 5 张全是全身构图 = 每张都把全身信息摆满 = 每张都平 = 反而没一张好看的。

**正解 = 同一套服装/发型/光方案，换景别出 3 张 = 光和造型不变，只换取景范围** = 变化成本最低 = 好看程度差异最大。**判据 = 主人说「很好看」的那张 = 往往不是信息最多的那张。**

### ⑤ 情绪-构图耦合（Mood-Composition Coupling）· 情绪 → 构图三件套映射

**不要写「intimate atmosphere」= 要写情绪 → 构图三件套（机位+线型+焦段）的强制映射**。

**情绪钦定映射表**（独创）：

| 情绪 | 机位 | 构图线型 | 焦段 | 整体氛围 |
|---|---|---|---|---|
| **throne / oppressive（王座压迫）** | extreme low angle + foreground enlarged | diagonal + perspective convergence | 16mm ultra-wide | warm low-key tones, lazy and superior |
| **intimate / quiet（私密安静）** | close-up + eye-level | rule-of-thirds + shallow DOF | 85mm portrait | soft bokeh, warm rim light |
| **dynamic / energetic（动感活力）** | low angle + mid-distance | leading-lines + diagonal | 24mm wide | bright daylight, motion blur |
| **dreamy / ethereal（梦幻空灵）** | mid-distance + backlight | S-curve + silhouette | 135mm telephoto | soft bokeh foreground, glowing rim |
| **candid / voyeuristic（偷拍窥视）** | hidden angle + distance | asymmetric + foreground blur | 200mm super-telephoto | dim ambient, grain, sharp focus on subject |

**原 prompt 例子**：
> 「慵懒而带着居高临下的俏皮」= `lazy and superior, throne-like oppressive presence`
> 「整体暖调低明度，色彩浓郁」= `warm low-key tones, rich saturated colors`
> 「像坐在王座上一样」= `sitting on the throne, oppressive presence through foreground enlargement`

**❌ 反例（情绪没绑定构图）**：❌ `throne atmosphere`（情绪孤立）

**✅ 正解（情绪 → 构图三件套映射）**：✅ `throne-like oppressive presence through extreme low angle + foreground boot enlarged by 16mm distortion + diagonal composition lines converging upward`

---

## 完整画面构图控制模板（沉淀金标准）

```python
camera_composition_template = """
[Camera Position · 三轴坐标]
{HEIGHT} level shot, the camera {DISTANCE} from subject,
{ORIENTATION}, e.g., "floor-level shot, the camera almost touching the floor looking up",

[Lens & Distortion · 焦段钦定]
captured with a {焦段 mm} {ultra-wide / wide / portrait / telephoto} lens,
{焦段对应的畸变效果},
e.g., "16mm ultra-wide lens exaggerates the foreground with extreme distortion",

[Perspective Convergence · 三段式]
foreground: {前景主体 + 放大比例}, e.g., "the boot closest to the camera dramatically enlarged in the foreground",
midground: {中景 + 透视收束过渡}, e.g., "legs receding sharply into the distance with strong perspective convergence",
background: {远景汇聚点}, e.g., "the perspective lines converging from the foreground up to her face as the vanishing point",

[Composition Skeleton · 线型 + 主体位置 + 情绪耦合]
{构图线型} composition with the subject positioned {主体位置},
{构图目的 = 情绪耦合}, e.g., "the foreground boot and stacked knees creating throne-like oppressive presence",

[Depth of Field & Background]
{景深描述} + {背景虚化效果}, e.g., "shallow depth of field with the background melted into warm bokeh",

[Mood-Composition Coupling]
{整体情绪} through {构图三件套}, e.g., "lazy superior throne-like presence through extreme low angle + foreground enlargement + diagonal composition",
{色调}, e.g., "warm low-key tones, rich saturated colors",
{光线}, e.g., "warm afternoon sunlight filtering through sheer curtains casting soft rim light"
"""
```

---

## 完整词库（按 5 维度分类）

### 机位词库（三轴坐标）

```
HEIGHT:
  - floor-level / almost touching the floor
  - waist-level
  - eye-level
  - overhead / bird's-eye
  - worm's-eye view

DISTANCE:
  - extreme close-up
  - close-up
  - medium shot
  - full body
  - wide shot

ORIENTATION:
  - front view
  - side view
  - back view
  - low-angle POV
  - high-angle
  - three-quarter
```

### 透视词库

```
- perspective convergence
- vanishing point at [主体]
- leading lines from [起点] to [终点]
- foreground [主体] dramatically enlarged by wide-angle distortion
- midground [身体部分] receding into distance
- background [远景元素] out of focus
- perspective lines converging upward/downward
- strong perspective depth
- wide-angle distortion exaggerates the foreground
```

### 构图词库（线型 + 位置 + 情绪）

```
线型:
  - diagonal composition
  - S-curve composition
  - rule-of-thirds composition
  - leading-lines composition
  - frame-within-frame composition
  - symmetric composition
  - asymmetric composition

位置:
  - upper-center
  - lower-center
  - left-third
  - right-third
  - subject positioned at edge

情绪耦合:
  - throne-like oppressive presence through [构图]
  - intimate quiet atmosphere through [构图]
  - dynamic energetic atmosphere through [构图]
  - dreamy ethereal atmosphere through [构图]
  - candid voyeuristic atmosphere through [构图]
```

### 焦段词库

```
- 16mm ultra-wide lens (extreme distortion, strong perspective)
- 24mm wide lens (strong perspective, wide FOV)
- 35mm natural lens (mild distortion, natural perspective)
- 50mm standard lens (no distortion, natural FOV)
- 85mm portrait lens (mild compression, shallow DOF, creamy bokeh)
- 135mm telephoto lens (strong compression, very shallow DOF)
- 200mm super-telephoto lens (extreme compression, dreamy bokeh)
```

### 氛围词库（情绪 → 色调 + 光线 + 焦段）

```
throne / oppressive:
  - warm low-key tones, rich saturated colors
  - lazy and superior expression
  - 16mm ultra-wide + diagonal composition + foreground enlarged

intimate / quiet:
  - soft bokeh, warm rim light
  - heavy-lidded gaze
  - 85mm portrait + rule-of-thirds + close-up

dreamy / ethereal:
  - backlit silhouette
  - glowing rim light
  - 135mm telephoto + S-curve + soft bokeh foreground

candid / voyeuristic:
  - dim ambient, film grain
  - hidden angle
  - 200mm super-telephoto + asymmetric + foreground blur
```

---

## ⑦ 画面「美」= 光与构图的活，不是动作细节的活

> **触发**：主人说「你设想的画面不够美丽 / 不够美 / 太普通 / 没感觉」，而图已经跑完且门禁全过。
> **判据**：这轮 **0 畸形、0 门禁挂、字数控得准**，主人还是说不够美 = **不是描绘能力不够，是那幅画面本身就不美** = **该重新设想，不是重写细节**。

### 7.1 分工卡在「构想」，不是卡在「成图」

| 阶段 | 谁负责 |
|---|---|
| **脑子里那幅画面**（prompt 之前）| **我的活** = 主人说不够美 = 我这层没做好 |
| **把画面描绘成 prompt** | 我的活 = 描绘不准再好的主意也救不回来 |
| **跑完的成图美不美** | **主人的活** = 我不自己看图判定好不好看 |

**🔴 两种「不美」要分清**：① **画面构想不够美**（我该重想光和构图）vs ② **成图没达到我构想的美**（描绘不准，重写描绘）。**先判自己在哪一层，再动手。**

### 7.2 重想的手法：换光方案，不动动作

**🔴 同一副造型（同一场景、同一个人、同一道具）也能出两张，第二张好看 = 换光与构图，不是把动作写得更细。** 反过来也成立：**把动作细节写满 = 标本图 = 信息齐全但一句都不美。**

| 手法 | 英文写法 | 效果 |
|---|---|---|
| **巨大且唯一的软光源** | `the whole pane turned into one big glowing warm apricot rectangle with the lattice reading as a darker grid burned into it` | 画面里最亮的东西 = 那扇窗 = 主体从黑里浮出来 |
| **大暗部** | `most of the picture falling away into deep cool blue-green shadow` | 让唯一的亮处有分量 |
| **一整块硬边光斑落在身上** | `a hard-edged block of warm light falling across her shoulder and the top of her thigh` | 体积感 = 照片「贵」起来的地方 |
| **只给一只眼一个亮点** | `her eye on the lit side catching a bright pinpoint` | 灵魂 = 主人一眼被钉住 |
| **另一侧脸整个沉进阴影** | `the other side of her face falling away into soft deep shadow` | 硬边分割 = 立体 |
| **大面积留白** | 主体只占画面一角 / `framed with breathing room` | 画面有呼吸 |
| **透光材质当光源的果** | `the wet cloth going translucent where the light passes through it` | 光穿过东西 = 活 |

**🔴 顺序**：**先把光和构图那几行写好（7.2 全套），再去填动作和姿态。** 额度不够时先砍材质细节，**不砍光线段**。

**❌ 反模式**：均匀顶光 + 平铺中景 + 动作写满 = 标本图。

### 7.3 光方案词库（按情绪选一个，别每张都一样）

| 情绪 | 光方案 | 关键句 |
|---|---|---|
| **逆光 / 空灵** | 巨大单光源在人物背后 | `the last of the dusk coming through the paper window behind her and to her left turning the whole pane into one big glowing rectangle` |
| **烛火 / 暖密** | 低位暖光从下往上打 | `one warm lamp behind and to her right throwing light up from beneath her so the underside of her jaw and her breasts burn bright` |
| **冷蓝 / 月** | 硬边高光条 + 冷补光 | `cold white moonlight laying a hard rim along the top of her head, cold bounce off the pale stone filling the shadow between her knees` |
| **水下 / 泳池** | 水面反光当第二光源 | `cool teal bounce coming back up off the lit pool floor filling the shadow under her arm so nothing goes black` |
| **偷拍 / 暗** | 单一远处点光 + 高 ISO 噪点 | `dim ambient, film grain, sharp focus on the subject, the far end of the room dissolving completely` |

**🔴 「不让暗部死黑」= 补光要写出来**，但补光只准做 **bounce / spill / glow** 三种弱补，**不准开第二盏灯**（一盏主光 + 一个反射面 = 仍然是单一光源的影调）：

```
{暗部} filled by {墙面/水面/地面} {bounce / spill / glow} so nothing goes black
```

---

## brief → prompt 提炼流程（沉淀）

主人 brief 含「POV 极低 / 广角 / 王座 / 透视收束 / 对角线构图 / 极低广角 / 靴子前景 / 王座般的压迫感」等触发词 = 调本技能：

1. **机位层**：按 brief 三轴坐标 = `extreme low angle POV almost touching the floor looking up`
2. **焦段层**：按情绪选焦段 = `16mm ultra-wide` (王座) / `85mm portrait` (私密) / `200mm telephoto` (偷拍)
3. **透视层**：写三段式 = `foreground [主体] enlarged + midground [身体] receding + background [远景] out of focus`
4. **构图层**：写线型 + 主体位置 + 情绪 = `diagonal composition + subject upper-center + throne-like oppressive presence`
5. **景深层**：加 `shallow depth of field + background melted into warm bokeh`
6. **情绪-构图耦合**：把构图目的绑定情绪 = `lazy superior throne-like atmosphere through extreme low angle + foreground enlargement + diagonal composition`
7. **0 写脸**：brief 不指定 = 不调灵魂面容 PREFIX

---

## 联动技能（5 大出图技能v1.0 联动）

- `yuer-run-one-brief`（出图固定入口）→ brief 含触发词 → 自动调本技能提炼 5 条金标准 → 写入 prompt
- `yuer-image` → 出图主路 → prompt 阶段调本技能
- `creative/yuer-image`（伞技能）→ Brief 模板段增加「Camera Composition」子段
- `yuer-personality-voice` → 聊到构图时引用本技能 5 条金标准
- `prompt-style-synthesis`（父技能）→ 实战 314 v1.0 钦定方法论 → 本子伞是首个「技法清单」（非 6 维度金标准）

---

## 反例硬表（一切）

| ❌ 反模式 | ✅ 正解 |
|---|---|
| ❌ `low angle`（vague 角度词）| ✅ `extreme low angle POV almost touching the floor looking up`（三轴坐标） |
| ❌ `strong perspective`（空话）| ✅ `foreground boot enlarged + midground legs receding + vanishing point at face`（三段式） |
| ❌ `diagonal composition`（只有线型）| ✅ `diagonal composition with subject upper-center creating throne-like oppressive presence`（线型+位置+情绪三件套） |
| ❌ `wide-angle shot`（无焦段）| ✅ `16mm ultra-wide lens exaggerates foreground with extreme distortion`（焦段+效果绑定） |
| ❌ `throne atmosphere`（情绪孤立）| ✅ `throne-like oppressive presence through extreme low angle + foreground enlargement + diagonal composition`（情绪→构图三件套映射） |
| ❌ `intimate mood`（情绪孤立）| ✅ `intimate quiet atmosphere through 85mm portrait + rule-of-thirds + close-up shallow DOF` |
| ❌ `dynamic shot`（无透视）| ✅ `dynamic energetic atmosphere through 24mm wide + leading-lines + diagonal composition + motion blur` |
| ❌ `dreamy feel`（无构图）| ✅ `dreamy ethereal atmosphere through 135mm telephoto + S-curve + soft bokeh foreground + glowing rim light` |
| ❌ `candid moment`（无偷拍感）| ✅ `candid voyeuristic atmosphere through 200mm super-telephoto + asymmetric + foreground blur + film grain` |
| ❌ 全身/背影景用 16/24mm 近距（透视夸张）| ✅ `135mm f/3.5 at f/4.0 from five meters, camera at knee height` + 构图防裁句 + 头身比算式段（见第 ⑥ 节）|
| ❌ 全身景只写 `slender` / `long legs`（无算式）| ✅ 头身比算式 + `hip line sitting slightly below the vertical midpoint with more height below than above` |
| ❌ 均匀顶光 + 平铺中景 + 动作写满（标本图）| ✅ 巨大单光源 + 大暗部 + 一块硬边光斑 + 只给一只眼一个亮点（见第 ⑦ 节）|
| ❌ 主体说「不够美丽」就去加动作细节 | ✅ 重想光方案和构图，动作与场景可原封不动（见第 ⑦ 节）|

---

## 主奴分明原则

- **主人** = 决定情绪 + 大致场景 + 主体姿态的 1 个核心 brief
- **我** = 调本技能按 5 条金标准扩展为完整 Krea 2 prompt（含机位 + 焦段 + 透视 + 构图 + 情绪-构图耦合）
- **0 越界**：不擅自加未要求的服装元素 / 场景细节 / 道具（除非 brief 明确提及）

---

## 当前基于 1 个示例 · 后续 N 个示例可补全

实战 314 v1.0 钦定「0 凭印象瞎编金标准 = 必从原文逐条提炼 + 频率统计 + 同义聚类」= 当前 n=1 = **技法清单 1.0** = 不是 6 维度金标准 = 后续主人提供更多高控制力 prompt（背身/POV/极低广角等）= 触发 prompt-style-synthesis v1.0 = 按频率统计补全金标准。

---

## 实战档指针

- 实战 314 v1.0 = 父技能 prompt-style-synthesis 5 件套方法论
- 实战 313 = 灵魂面容 PREFIX 0 写脸铁律（联动）
- 实战 354 = system_prompt 节点 861 = 唯一最终交付物铁律（联动）

---

## 一句话总结（v1.0）

**yuer-camera-composition-style v1.0 = 实战 486 主人正解打脸「应该向这方面学」钦定沉淀 = 基于 1 个高控制力 prompt 提炼 5 条画面构图技法金标准（机位三轴坐标 + 透视三段式 + 构图线型+位置+情绪三件套 + 焦段+畸变效果绑定 + 情绪-构图耦合映射）= 后续 brief 含 POV 极低/广角/王座/透视/对角线构图等触发词 = 自动调用本技能 = 联动 5 大出图技能 = 跟 yuer-back-view-style 同级别（v1.0 方法论产出）**。
