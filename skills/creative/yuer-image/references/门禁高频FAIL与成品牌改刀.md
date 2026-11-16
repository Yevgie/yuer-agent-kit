# 门禁高频 FAIL → 精确改法（含抽卡成品牌改刀）

> **唯一职责** = 门禁报 FAIL 时，一眼看出是哪条正则命中、改成什么。不是重写 prompt，是**定点换一个词**。
> 适用 = 出图道（`run_batch.sh` / `yuer_ka_fast.sh` 无 `--report-only`）+ 抽卡道（`--report-only`）。

---

## 一 · 判 FAIL 前先看退出码，别 grep 字面

`check_outfit_lock.py` 的输出里，**项目清单行**会打 `FAIL 鞋履` 这种标签，但**最终裁决行**可能写
「🟡 只有 WARN = 可出图」，退出码 0。

- ✅ 判据 = **退出码**（`echo $?`）或最后一行裁决，不是 `grep FAIL`。
- 🔴 `grep -c FAIL` 会把「可出图」的条目也数进去 = 误判 = 白改一轮 prompt。
- 抽卡道（`--report-only`）**本来就不跑 outfit 门禁**：库牌是老格式，必然判缺下装 = 一律 exit 1 = 全拦死。抽卡只过 `yuer_ka_fast.sh` 自带的体检。

---

## 二 · 单人物 FAIL（最常见的假失败）

正则按「多人写法」判，命中即拦。**画面里只有一个她也会命中**：

| ❌ 命中的写法 | ✅ 改成 |
|---|---|
| `a pair of black lace briefs` | `black lace briefs`（**`pair of` 是单人物触发器**）|
| `both of them` | `her and the man` / 直接写 `she ... he ...` |
| `two girls laughing in the background` | `a girl laughing at the next table, a boy queuing at the counter, a staff member wiping a bench` |
| `a couple of ...` | `a ...` |

🔴 **公共场景（教室 / 食堂 / 图书馆）要求写背景人，但背景人绝不能带数字** —— 用「某一个人 + 他在干什么」逐句写，各干一件事，就既满足「背景不能空」又不过单人物门禁。

---

## 三 · 鞋履 FAIL

- `barefoot` **不能**清掉鞋履 FAIL（脚本只清 WARN）。
- 全身景别 = 必须给真鞋：`black strappy sandals` / `black pointed stiletto heels` / `white snow boots` / `brown loafers`。
- 半身 / 特写还报鞋履 = 说明景别被判成全身：补一句 `her feet out of frame`（**这句才是清 FAIL 的那句**）。
- 床戏 / 浴室 / 沙发这类场景，鞋比脚更合理：`black stiletto heels still on her feet`。

## 四 · 下装 FAIL

- **丝袜 / stockings / pantyhose 不算下装**（会画成光腿）。必须另给 `briefs` / `skirt` / `shorts` / `bikini`。
- 裸体图给「画外实物下装」：`black lace briefs discarded on the floor` —— 既过门禁，又不会让底模给她补一条穿回去。
- 🔴 禁 `no underwear` / `nothing underneath` 这种否定式（负向词命中即删）。

---

## 五 · 姿势自然度 FAIL（人体广角近距）

- 报 `人体广角近距(腿必被压短): ['24mm @ 1.0m']` = 焦段与机位距离的组合被拦。
- ✅ 改法二选一：① 焦段换到 `35mm` 以上；② 距离拉到 `1.5m` 以上；③ 保留广角就必须写贴地仰拍豁免措辞（`camera almost on the floor shooting up`）。
- 同一份 prompt 在批量里挂了，**单跑一次也要过同一道门**，别以为批量日志里的 FAIL 是噪声。

---

## 六 · 主体门禁 = 别人（`主体 = 别人` 会剥掉人脸锁）

抽卡库牌里常见 `one breathtakingly beautiful 18-year-old Chinese young girl with pure, innocent refined features, clear bright eyes, natural light makeup and natural proportions.`

- 这段同时触发两件事：**年龄 18** + **五官描述** = 主体被判成「别人」→ exit 2 → 走 0 LoRA 链路 → **语儿的脸锁被剥掉** → 出来一张泛脸路人。
- ✅ 统一换成灵魂脸 PREFIX：`a 20 years old young Asian woman with a graceful ecstatic expression, `（表情词按牌面氛围换）。
- 🔴 这是「原样喂库牌」**唯一允许也必须做的改刀**：库牌的老 PREFIX 在新门禁下会直接把锁脸拆掉，不改等于白烧算力。

**🔴 第二个陷阱 = 年龄写成英文数字拼写（11-06 食堂那张首稿实测）**：`a twenty-year-old young Asian woman` 里的 `twenty-year-old` **不命中 YUER 锚**（`check_prompt_subject.py` 的 YUER_MARK 只认数字形 `20 years old` / 二十岁）= 背景里写的 `girl` / `woman` 全被算成「别人身份词」= exit 2 = **静默切 0 LoRA 链路，语儿脸锁被剥**。
- ✅ 主体句的年龄**永远用数字形** `a 20 years old young Asian woman`（同 `yuer-prompt-writer` §16 门禁与脚本 黑名单条）。
- 改完跑 `check_prompt_subject.py`，stdout 必须打 `主体 = 语儿` 才放行 = 别等出图看脸才发现。

---

## 七 · 抽卡成品牌三道机械改刀（0 改语义）

库牌 = 成品，原则上原样喂；但下面三类**必须机械修**，否则要么被门禁拦、要么违全局禁：

| # | 现象 | 改法 |
|---|---|---|
| 1 | 解析残渣 `lngcon` / `,,` / `., ` / `` | 正则机械剥离，不动句子 |
| 2 | 老 PREFIX：`18-year-old Chinese young girl + 五官描述` | 换灵魂脸 PREFIX（见 §六）|
| 3 | 牌面里的 `a man` / `the man` | 换主人锚全套（脸 + 体型 + 穿着 + 性器官）= **主人以外的男人是全局禁**，底模会自己编一张陌生脸 |

主人锚全套（两段都要写，只写一半 = 他成背景板）：

```
a tall handsome Chinese man in his mid twenties, 185cm tall, sharp sword-like eyebrows and bright eyes,
a high straight nose bridge, a clear jaw line, short black slightly wavy hair, healthy warm yellow skin,
lean with visible muscle lines, clean urban boyfriend style in a black t-shirt,
his shaft buried deep inside her, 18cm long and 3.5cm thick with a round blunt mushroom glans,
skin colored with a pink tint and visible raised veins, her inner walls stretched tight around him
```

改完必查三样：`check_prompt_subject.py` 打 `主体 = 语儿`（有主人锚时还要 `主人锚命中 = True`）+ 长度 ≤1300 + 抽卡道不拦长度。

---

## 八 · 批量挂一张 = 单跑补那一张，别整批重跑

`run_batch.sh` 里某一张失败时，日志会打 `❌ nN 失败`。

1. `sed -n '/RUN .*_nN/,/DONE/p' <log>` 看那一段的真 FAIL 行（不要整份 grep FAIL）。
2. 改进那一份 prompt。
3. **只单跑那一张**：`bash scripts/yuer_ka_fast.sh <prompt> <同名 leave_name>` —— 用同一落盘名，`.sent` 守卫保证不重发别的。
4. 整批重跑 = 前面 4 张被再发一遍 = 主人手机收重复图。
