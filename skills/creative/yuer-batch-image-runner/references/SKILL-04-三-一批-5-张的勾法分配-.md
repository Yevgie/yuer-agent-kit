## 三 · 一批 5 张的勾法分配（不同勾法 = 不撞图）

| # | 勾法 | 身体段 | 场景 | 露点 |
|---|---|---|---|---|
| 1 | 骚穴正面特写 | covered + 私处实写 | 公共场所（试衣间/书架） | 掀裙/扒开 |
| 2 | 臀 | nude | 私密（卧室床） | 全裸翘臀回看 |
| 3 | 腿 + 骚穴 | nude | 私密（浴室淋浴） | 抬腿踩墙 |
| 4 | 胸 | covered | 公共场所（便利店/超市） | 肩带滑落 |
| 5 | 综合 | covered | 公共（泳池/天台） | 泳装湿身 |

**🔴 每张至少换 1 个维度**：景别 / 场景 / 承重面 / 主动作动词 / 唯一亮部。
**🔴 每张的「唯一亮部」必须不同**（试衣间顶灯条 / 床头灯 / 浴室冷光 / 冷柜白条 / 天台柔光箱）= 同亮部 = 画面同质。

### 🔴 姿势不能单一 = 按「承重面」选，一张一个承重点

主人一句「**姿势太单一了**」= 上一批五张全是「站着靠 / 坐着弯 / 坐着撑」= **换了景别换了衣服，骨架还是同一副**。

**判据 = 五张的承重面各不相同**（承重面 = 身体靠什么撑着）。五档各取一个，一个都不重复：

| # | 承重面 | 姿势原语（中） | 英文锚 |
|---|---|---|---|
| 1 | **双脚** | 站立・单手扶物顶胯・回眸 | `stands with one palm flat on the shelf, weight on her right leg, hip pushed out, head turned back over her shoulder` |
| 2 | **尾椎 + 双手** | 坐地・M 字开腿・双手后撑挺胸 | `sits on the floor with her knees dropped wide open and both palms planted flat behind her, chest arched up` |
| 3 | **侧身 + 胯** | 侧卧・单臂过头・S 形曲线 | `lies on her side with one arm stretched above her head and her knees bent forward, body tracing one long curve` |
| 4 | **双脚 + 单手** | 深蹲・单手触地・抬下巴 | `crouched low on the balls of her feet with one hand flat on the floor between them, other forearm over her knee` |
| 5 | **双膝 + 双手** | 四肢着地・弓背・回首 | `on all fours on the rug with her back arched and her shoulders drawn back, head lifted` |

**🔴 预选姿势 = 查姿势库按分类各取一个**，别凭空想：

```bash
python3 yuer-image/scripts/pose_gallery_search.py "跪"    # 单关键词，多词 = AND 必 0 命中
# 或直接读 /path/to/data/pose_gallery/ai-pose-gallery-zh/data/pose-zh.json

# 按「分类」分组取：站姿 / 坐姿 / 趴卧 / 蹲姿 / 跪立・四肢着地 / 侧坐 —— 五类各一个
```

**🔴 判据 = 把五张的承重面写成一行**（站 / 坐 / 卧 / 蹲 / 跪）= **五个字都不一样才算过**；出现两个「坐」或两个「站」= 重排。

---

## 四 · 🔴 踩过的坑（机制版）

| 坑 | 机制 | 正解 |
|---|---|---|
| 5 张 prompt 手抄 | 每段 2000+ 字符 = 抄错一处 = 白跑一张 | build 脚本 = 一处改 = 全批跟着改 |
| 裸体图超 3200 天花板 | 完整裸体身体段 ≈1500 字符 + 场景光线 = 4100+ | `NUDE_SHORT` 精简段 |
| 裸体图门禁 FAIL「缺下装」| 门禁只认「下装」这个词 | 场景句里补**画外**实物下装 |
| 一批图全是同一种调 | 同 STYLE 前缀 = 同机位同调色 | 每张各占一档 STYLE |
| caption 图文两截 | 脚本内部盲抽 = 不看图 | caption 出图前自己写好传 `--caption` |
| 主人手机收两遍同一张 | 看 stdout 不清就重跑 | 三件套齐 = 不重跑 |
| 一次甩 10 张 | 「无限诱惑」= 一批 5 张 = 跑完停 | 停住等「继续」 |
| **batch_gate_check 全绿 → 开跑整批不出图** | 🔴 11-07 起 wrapper 长度段 0 阻断 | 若仍不出图 = 查结构段 / 姿势自然度，不是长度 |
| **裁剪把主体锚删了 → 整批报「判不出来」** | 主体锚在句首、按「删最长块」会先删它 | 裁剪跳过前 3 个逗号块，剪完重跑主体门禁 |
| **姿势全批一个样** | 换了景别和衣服，但承重面全一样 = 底模输出同一副骨架 | 五张按承重面五档各取一个（站/坐/卧/蹲/跪） |
| **公共场景写了「two girls / three students」→ 单人物 FAIL** | 背景人带数字词 = 门禁读成分身（和 `a pair of` 同一个机制）。但公共场景又**必须**写背景人（否则底模给空棚）| 人照写、数字全删：`a girl laughing at the next table, a boy queuing at the counter, a staff member wiping a bench` = 3 个背景人 + 0 数字词（`yuer-prompt-writer` §16 门禁与脚本）|
| **下装只挂了袜类**（`black sheer stockings` / `pantyhose`）→ 下装 FAIL | 丝袜/打底袜不归「下装」白名单 = 等于没写下装 | 同句并排一个真下装词：`black lace briefs and sheer black stockings, black pointed stiletto heels` |
| **24mm + 1.0m → 姿势自然度 FAIL** | 门禁读的是「焦段 @ 距离」这对组合；<35mm 且 <1.5m = 人体广角近距 = 腿必被压短 | 改 `35mm` + `1.5m` 起；真要保留广角压迫感 = 同时写豁免两词 `camera almost on the floor shooting up` + `extreme low angle`（`yuer-prompt-writer` §8 相机 + §10 判断第 4 条）|
| **自写 build 脚本的逐张 body 占位 `None` → `emit` 直接拼接 `TypeError`** | 逐张手写常用 N 元组 job，末项 = 该图专属身体段（`None` = 用默认 COVER）；`emit` 里写 `" " + this_body` 撞上 `None` = 整批 build 崩，而 `ast.parse` 只验语法、验不出「可能为 `None` 的拼接」= 门禁根本没跑到 | `emit` 末项必回退：`tb = this_body or body`（`None` = 默认 COVER）；只有裸体那张显式传 `NUDE_SHORT`（🔴 漏传 = fallback 到默认 COVER 穿着段 = 全裸图混进「布下胸型、无皮肤细节」这类穿着描述 = 底模穿模；判据 = 全裸图 prompt 里 grep 不到 `fabric` / `under the cloth` 词 = 否则就是 fallback 漏传了），其余全传 `None` 走默认 = 0 手抄多份 COVER |

---

