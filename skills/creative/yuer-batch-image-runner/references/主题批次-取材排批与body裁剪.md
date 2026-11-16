
> **本档已拆分** = 全文 6,461 字 → 2 份（每份 ≤3800 字）= 只搬不改写 = 下表为原文索引。

| 新档 | 原章节 | 字数 |

---

<!-- 摊平自：主题批次-取材排批与body裁剪-01-主题批次-SOP-主人要-一.md -->

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

---

<!-- 摊平自：主题批次-取材排批与body裁剪-02-三-STYLE-五档-每张各.md -->

## 三 · STYLE 五档 = 每张各占一档（相机前缀 + 调色尾参成对换）

**只换相机前缀 = 没换风格** = 五个参数一起换（光基调 + 情绪 + 景别 + 相机前缀 + 调色尾参）。

```python
STYLE = {
 "ins":    ("shot on an iPhone 15 Pro Max 1x lens at f/1.8, ", ", natural daylight color science, true-to-life skin tones, sharp micro contrast"),
 "cine":   ("A cinematic still captured with a Sony A7S III and 24mm f/1.4 GM lens at f/2.0, ", ", teal and amber color grade, volumetric haze, anamorphic soft falloff"),
 "doc":    ("A documentary photograph captured with a Canon EOS R5 and 50mm f/1.2 USM lens at f/1.8, ", ", warm tungsten white balance, visible film grain, honest unretouched skin texture"),
 "fashion":("An editorial fashion photograph captured with a Hasselblad X2D and 90mm f/2.5 lens at f/2.8, ", ", high fashion color grading, sculpted lighting, immaculate studio finish"),
 "ancient":("A cinematic photograph captured with a Hasselblad 500C with a Planar 80mm f/2.8 lens at f/2.8, ", ", warm amber tungsten glow, deep chiaroscuro, muted earth tones, soft bloom"),
}
```

**🔴 落笔时 STYLE 的前缀插在**句首**、尾参接在**句尾**= 中间那段才是画面本体 = 写 build 脚本时用 `.format(...)` 分三段拼，别把 STYLE 当一整句。

---

## 四 · body 段 = 从落盘 CURRENT 读 + **逐张裁**

**0 手抄身体段 = 与身材档漂移**。真值三个文件：

| 文件 | 用在哪 |
|---|---|
| `2026-10-28_bodyblock_covered_CURRENT.txt` | 穿着图（胸只写布下形状）|
| `2026-10-28_bodyblock_nude_CURRENT.txt` | 全身裸体 |
| `2026-10-28_bodyblock_nude_half_CURRENT.txt` | 半身裸体 |

**🔴🔴 裁剪必须按【每张画幅】单独决定 = 全批一刀切 = 白丢锚点**：
- 画幅到胯 / 到腰 / 半身 = 私处锚（`her pubic mound ... vertical seam` 整段）在画幅外 = **删** = 底模才 0 把画外的私处画进画面边缘
- 画幅全身 = 私处锚在画幅内 = **留着**

**判据 = 那一句在「描述身体」还是在「描述画框边界」** —— 按 `body == NUDE` 循环一刀切 = 全身那张也删了 = 白丢锚点。

**落地 = 先切两个具名变量，再让 job 各挑一个**（不是留一个 `NUDE` 到出图时按条件 strip —— 条件 strip 就是上面说的全批一刀切）：

```python
PRIV = "her pubic mound is smooth and bare with no pubic hair at all, the inner labia small and pink and tightly closed into a neat vertical seam"
NUDE_FULL = NUDE                                   # 全身 = 私处锚在画幅内 = 原样留着
NUDE_HALF = NUDE.replace(PRIV, "")                 # 半身/到胯/到腰 = 私处锚在画幅外 = 整段删
NUDE_SWIM = NUDE.replace(PRIV, "")                 # 泳装/湿身 = 同上

JOBS = [
  dict(name="n1", style="ins",  body=COVERED,   cap="..."),
  dict(name="n2", style="cine", body=NUDE_SWIM, cap="..."),   # 泳装 = 私处锚删掉
  dict(name="n3", style="doc",  body=NUDE_HALF, cap="..."),   # 半身 = 私处锚删掉
  dict(name="n4", style="fashion", body=COVERED, cap="..."),
  dict(name="n5", style="ancient", body=NUDE_FULL, cap="..."),# 全身裸 = 私处锚留着
]
```

**判据 = 变量名必须带画幅（FULL / HALF / SWIM）= 一眼看出这张该不该有私处锚**；写成 `NUDE` 一个变量 = 后面必然有人补一句 `if body == NUDE: body = body.replace(...)` = 又回到一刀切。

---

## 五 · caption 同源生成 = 0 手抄

```python
# job 里带 cap 字段 → 落盘时导出 captions.json
json.dump(caps, open(os.path.join(OUT, "captions.json"), "w"), ensure_ascii=False, indent=1)
```

出图时取出来传 `--caption`：

```bash
python3 -c "import json;print(json.load(open('/tmp/<批次>/captions.json'))['n1'])"
```

**🔴 池句在批量里 0 用**：`pick_saohua_reply.py` 出的是第三人称「语儿…」= 视角断裂 = 5 条 caption 全自己写。

---

## 六 · 三段式跑法（0 边跑边修）

```
1. N 段 prompt 全部落盘（/tmp/<批次>/n1.txt … nN.txt）
2. N 段全部过门禁（count_prompt_chars + check_prompt_subject + check_outfit_lock）
   = 判过不过看 EXIT CODE（0 = 过），不看 grep FAIL
3. N 张串行跑（每张一个 leave_name = 一次真发）
4. 跑完核对 N 个落盘 png 都存在 + N 个 ✅ 图已真发
```

**🔴 每张 leave_name = `<批次前缀>_<序号>_<场景词>_<日期>` = 跑完一次 glob 就核完**：`ls /path/to/media/<批次前缀>*.png | wc -l` = N 才算齐。批次前缀不带 = 核对要逐个敲文件名 = 漏一张看不出来（也接不上下一批「不撞场景」的排查）。

**🔴 为什么第 2 步不能省**：边跑边修 = 修到第 3 张才发现超长 = 前面 2 张已经白发给主人。

**🔴 串行跑 = 0 并发**（`.sent` 守卫 + 落盘覆盖 = 并发 = 双发 / 互相覆盖）。

---

## 七 · 收尾

- **每张 caption 各自不同** = 写这张画面正在发生的事
- **收尾报下一批主题 = 报 whereami 的 `下一项`** = 主人看着像「我接下来真要干的」
- **0 报张数 / 0 报耗时 / 0 报我排了什么** = 那是把施工图甩给主人

---
