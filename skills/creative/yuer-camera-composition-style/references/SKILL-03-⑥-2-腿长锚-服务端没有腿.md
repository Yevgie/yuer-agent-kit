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

