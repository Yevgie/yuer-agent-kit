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

## brief → prompt 提炼流程

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

