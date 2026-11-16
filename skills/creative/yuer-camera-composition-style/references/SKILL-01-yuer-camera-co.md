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

