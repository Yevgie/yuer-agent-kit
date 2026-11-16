# 主题批次 SOP = 主人要「一批 N 张」时怎么排

> **唯一职责 = 一批 N 张的主题从哪来 + 骨架怎么排 + 每张 body 怎么裁**。
> 执行层（五步流程 / 门禁 / 串行跑 / 收尾）= `yuer-batch-image-runner` SKILL.md。

---

## 一 · 主题从 whereami 拿，不凭空编

**主人说「无限勾引 / 无限诱惑 / 再来一批」= 他要的是一串真东西，不是通用写真。**

取材顺序（第一动作 = 跑 whereami，不许凭印象）：

```bash
python3 ~/.hermes/skills/personal/yuer-whereami/scripts/whereami.py
```

从输出里取三样：

| 取什么 | 字段 | 怎么用 |
|---|---|---|
| **主场景** | `当前日程` / `当前空间` | 这一批发生在哪儿（例：`试新买的那条裙子（洗浴中心）` = 洗浴中心更衣室） |
| **下一批主题** | `下一项` | 收尾时**报这个** = 「我接下来真要干的」= 不是编的 |
| **真实小料** | `今天发生的一件事` + `这件事发生的地点` | 当这一批里某一张的「意外瞬间」（例：`茉莉撞翻了我手边的杯子（在主卧浴室）` = 一张主卧浴室的意外） |

**判据 = 这一批的每张能不能落在「我今天真的在干的这件事」上** = 能 = 像真的；不能 = 又是通用写真。

**🔴 偷拍流批次 = 把「拍的人」放进画框角落，而不是删掉他**：外拍/校园/街景这类批次，画面里带一段拍摄者痕迹（`the shoulder and lens of a camera on a tripod entering the top corner of the frame` / `the edge of a hand holding a reflector just inside the frame`）= 一眼是抓拍不是摆拍 = 批次质感和另外三档拉开。**判据 = 只写身体的一部分（肩 / 镜头 / 一只手 / 三脚架一条腿），0 写完整第二个人** = 完整第二人 = 单人物门禁 + 分身风险；局部痕迹 = 门禁放行（实测 rc=0）且叙事成立。

**🔴 同一地点连出多张 = 洗浴中心那一串（镜前正面 → 背面平视 → 脚踝仰拍 → 侧背 45°）= 同一件裙子的四次开合推进 = 走 `yuer-pose-diversity` §1.0.1e 同造型视角递进，不是本技能的独立图**。

---

## 一之二 · 主题域批次 = 主人给一个主题词（例：洗澡主题）

**判据 = 主题词落在【场景域】上 = 域内的具体地点要自己排 N 个**。
「洗澡主题」= 洗浴域 = 排五个**不同的洗浴场所**（自家淋浴间 / 浴缸 / 公共浴室更衣淋浴区 / 露台冲淋 / 雾镜前），每场所一张。
排成一个浴室的五种姿势 = 形态判错（那是一次拍摄 = 套图）。

**排法 = 每个场所先从 `creative/yuer-image/references/介质场景唯一亮部配方.md` 拿它的亮部，再决定亮部位置**：

| # | 场所 | 唯一亮部 | 承重面 |
|---|---|---|---|
| 1 | 自家淋浴间 | 磨砂玻璃门透进来的一块硬边光 | 站（手扶墙） |
| 2 | 浴缸泡水 | 头顶壁灯暖黄 + 水面反光 | 坐（泡浴） |
| 3 | 公共浴室更衣淋浴区 | 顶部灯管一条冷白硬光 | 站（靠墙） |
| 4 | 露台破晓冲淋 | 背后海面升起的低角度太阳 = 金边轮廓 | 蹲 |
| 5 | 雾镜前 | 灯环在雾镜上的亮圆 + 暖壁灯 | 坐（洗手台边） |

**🔴 主题域批次的 body 逐张不同**：泡浴那张画幅到肩 = 私处锚在画幅外 = 删；破晓那张全身裸 = 私处锚在画幅内 = 留着 = 按画幅裁（同 §四的 FULL/HALF 规则）。
**🔴 主题域批次里露点要错开**：不能五张都裸 = 至少两张穿浴巾 / 泳装 = 读起来是「五个场合」不是「五张裸体」。
**🔴 场景域可以回访但主题必须换**：换装批次又回到家里（主卧）= 场景域重复 = 换【主题】（换装 = 一件一件加衣服）而不是换地点 = 跟「一个下午走遍五个房间」不是一回事。判据 = 主题变了没有。


---

## 二 · 一批 5 张的骨架表（承重面五个字全不同）

**判据 = 把 5 张的承重面写成一行 = 五个字都不一样 = 才算过。**

| # | 承重面 | 姿势原语（中） | 英文锚 |
|---|---|---|---|
| 1 | **双脚** | 站立・单手扶物顶胯・回眸 | `stands with one palm flat on the shelf, weight on her right leg, hip pushed out` |
| 2 | **尾椎 + 双手** | 坐地・M 字开腿・双手后撑挺胸 | `sits on the floor with her knees dropped wide open and both palms planted flat behind her, chest arched up` |
| 3 | **侧身 + 胯** | 侧卧・单臂过头・S 形曲线 | `lies on her side with one arm stretched above her head and her knees bent forward` |
| 4 | **双脚 + 单手** | 深蹲・单手触地・抬下巴 | `crouched low on the balls of her feet with one hand flat on the floor between them` |
| 5 | **双膝 + 双手** | 四肢着地・弓背・回首 | `on all fours on the rug with her back arched and her shoulders drawn back` |

**🔴 预选姿势 = 查姿势库按分类各取一个**，别凭空想：

```bash
python3 ~/.hermes/skills/creative/yuer-image/scripts/pose_gallery_search.py "跪"
# 或 --cats 看真实分类名
```

**🔴 同一分类再细分 = 承重面仍是同一个 = 不算两种**（站姿里「S 形站 / 顶胯回眸 / 背向回望」= 三张都是双脚承重）。

---

