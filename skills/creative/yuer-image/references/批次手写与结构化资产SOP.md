# 批次手写 + 结构化资产 SOP

> 出图批次怎么写、怎么自检、产出怎么回流成可检索资产。
> 配套：`scripts/design_dimensions.py` / `camera_placements.py` / `yuer_asset_search.py` / `yuer_prompt_index.py`

---

## 一、批次构建器的写法（先看这条，能省掉一整轮返工）

### 1.1 🔴 相邻字符串字面量会静默合并 → 段数对不上

Python 里两个相邻的 `"..." "..."` 会被编译成**一个**字符串。于是 spec 元组少一项，
报 `ValueError: not enough values to unpack (expected 11, got 9)` —— 而且**报错位置指向解包行，
真正的原因在几百行上面的字面量处**，极难定位。

**正解 = spec 用显式字段，不用裸元组。**

```python
# ❌ 错：靠元组位置，合并了就错位
SPECS.append(("n1", "eye_level", "half_body", """hair""", """scene""", """costume"""))

# ✅ 对：字典 + 字段名断言
def add(name, hk, fk, **kw):
    missing = {"hair", "scene", "costume", "action", "props",
               "light", "expr", "beat"} - set(kw)
    assert not missing, (name, missing)
    SPECS.append(dict(name=name, hk=hk, fk=fk, **kw))

add("n1", "eye_level", "half_body",
    hair="...", scene="...", costume="...", action="...",
    props="...", light="...", expr="...", beat="...")
```

**判据 = 构建器里任何一个字段名写错，脚本必须在构建时就炸，而不是在解包时炸。**

### 1.2 段落顺序是契约，不是格式

builder 输出的段落顺序**被索引器依赖**。顺序变了，索引全废。

```
[主体+发型] [场景] . [机位+焦段+距离+裁法] [身材锚] Wearing [服装]
[动作] [光线] [道具] [表情] [观看关系] , 9:16 vertical composition
```

- `The camera is` → 机位段起
- `a tall slender build` → 身材锚起（**首句恒定**，别改）
- `Wearing ` → 服装段起
- 光源词 / 表情词 / 观看关系词 → 三段起
- `, 9:16 vertical composition` → 尾参

**🔴 段与段之间只有逗号，没有句号。** 按句号切会碎成渣 —— 按锚点切。

### 1.3 门禁预算（超了怎么改）

| 项 | 区间 |
|---|---|
| 成品 prompt 字符数 | **600 ~ 3200** |

超上限 → **删整句，不挖词**。按优先级删：道具 → 场景次要细节 → 光线补充 → 表情补充。
**不删**：主体锚 / 服装五项 / 身材锚 / 观看关系 / 尾参。

### 1.4 机位×景别先跑 `check()`，撞了换机位而不是改措辞

```python
from camera_placements import check, build_camera, CAMERA_HEIGHT
prob = check(hk, fk)          # 非法组合直接返回原因
if prob: print(prob)          # 先改机位/景别，不是先改 prompt 措辞
```

**🔴 高机位俯视 + 超广角全景 = 物理上是"贴脸俯拍"，姿势门禁必拦。**
这不是措辞问题，是我把两个互斥的东西叠上了。**正解 = 换一个物理上成立的组合**
（那张悬崖题材本来就该从崖底虫眼往上拍）。

### 1.5 服装门禁：连体装（旗袍/汉服/长袍）也要写下装

服装门禁要求显式下装词。连体装写「qipao skirt falling past her knees」才过。
`black underwear` 这类泛词不命中下装白名单 —— 写具体的 `black briefs`。

---

## 二、批次自检（每批 5 张，跑完必须过）

| 项 | 门槛 |
|---|---|
| D9 观看关系 | 5 张 5 种（谁拍 / 为何 / 她知不知 / 画外有谁） |
| D4 机位 | 5 档各占一档 |
| D5 景别 | 5 种各占一档 |
| D6 光源 | 5 种不同（每张唯一光源，说得出从哪来） |
| **共同句数（排除身材锚+妆容后）** | **≤ 1 句/对** |
| 勾引维度 | 可勾引皮肤 ≥1 块 / "她不知道" ≥3 张 / "未完成" ≥3 张 / 光顺着皮肤滑 5/5 |
| 定性自查 | **这五张是五个不同的画面，还是一张画面的五次换皮？** |

### 🔴 共同句数的度量必须排除身材锚和妆容

那些是**必须一致**的锚（"她还是语儿"的保证），不是骨架。把它们算进共同句数，
原始值会飙到 14，看着像很糟，实际那 14 句全是身材段和妆容句。
**排除后 0.0 = 五张除身材外没有一句相同 = 真不重复。**

### 🔴 排除后仍然 > 1 = 模板在漏

> 拍摄意图档案版的残余就是 3.0 —— 同一套句式在几张之间漏了出来。
> 出现这种值就去读那几张的共同句是什么，改**句式源头**，不是改某一张。

---

## 三、产出回流：积累闭环

```
出图 → 落盘 .prompt.txt + .png + .sent
     → 批跑脚本末尾自动跑 yuer_prompt_index.py --check
     → 新 prompt 增量入索引 + 抽 tag + 标 verified
     → 下一批检索时立刻能用
```

**🔴 积累 = 攒进索引 = 攒成能检索、能过滤、能验证的结构。攒文件不算积累。**

### 3.1 索引器（`scripts/yuer_prompt_index.py`）

```bash
--build            # 全量重建
--build --limit N
--stats            # 维度分布 + 段落非空率 + 批次分布
--check            # 增量补新文件（每批跑完自动调）
--show <i>         # 看一条解析结果
```

索引落盘 = `/path/to/media/.prompt_index.json`（跟图同目录 = 不散落）。

### 3.2 🔴 五种历史格式 = 全部接住，0 丢数据

| 格式 | 特征 | 处理 |
|---|---|---|
| A | `The camera is` + 固定段序 | 九段全切 |
| B | 相机参数开头 + 小写 `wearing` | 九段全切 |
| C | `.prompt.md` markdown 头 + 代码块散文 | 半结构化（抽 tag + 全文） |
| D | 相机参数开头 + 散段落 | 半结构化 |
| E | 兜底 | 半结构化（只抽 tag） |

**原则 = 能切就切，切不了就抽标签，一条都不扔。**

### 3.3 🔴 解析器的三个必踩坑

1. **坐标系混用** = 光线锚点、表情锚点在不同坐标系里算 → 位置全错 → **解析 0 成功**。
   **判据 = 所有锚点位置必须在同一坐标系里算。**
2. **`.*?` 后接歧义回溯** = `^(a 20 years old .*? young Asian woman with .*?), (.*)$` 永不匹配
   （`.*?` 后面又要求同一串）。改成 `^(a 20 years old .*?with .*?), (.*)$`。
3. **大小写** = 格式 A 是 `Wearing `，格式 B 是 `wearing `。大小写敏感的 `find` 只中一半。

### 3.4 🔴 主题池是中文、prompt 是英文 → 必须有英文别名

`design_dimensions.THEME_EN` = 13 类主题各配一套英文信号词。
**没有它 = 主题检索永远 0 命中 = 题材维度形同虚设。**

### 3.5 🔴 检索关键词宁窄勿宽

泛词（`crystal` / `surreal` / `beach`）会让单个标签命中几百条 = 过滤失效。
**判据 = 单标签命中超过全库 15% = 太宽 = 收窄。**

---

## 四、检索纪律

```bash
python3 scripts/yuer_asset_search.py --pool prompt "qipao" --top 5
python3 scripts/yuer_asset_search.py --pool prompt --dim theme --tag "theme:民国近代" "silk"
python3 scripts/yuer_asset_search.py --pool prompt --dim cam "low angle street"
python3 scripts/yuer_asset_search.py --pool prompt --batch v130 "bookshop"
python3 scripts/yuer_asset_search.py --pool pose "跪"
python3 scripts/yuer_asset_search.py --pool costume "lace white"
```

可过滤维度 = `cam` / `framing` / `lens` / `light` / `viewer` / `aware` / `expose` / `theme`
评分 = 关键词命中 + 标签命中×3 + **verified×5**（真出过图的稿更可信 = 优先选）

**🔴 底层库多词 = AND = 复合词整句搜必 0 命中**
（中文姿势名是"跪立・四肢着地"这种复合词）→ 检索器自动拆词逐个搜 + 多词 OR。

### 4.1 🔴 命中 ≠ 使用

库给的是**骨架素材**，不是成品 prompt。

- 库给「猫式（胸贴地翘臀・側面）」→ 我要写「她跪在瓷砖上，手撑在前面，腰塌下去，脸转过来看镜头」
- 库给「blue lace camisole cardigan beige denim pants pumps」→ 我要写「深蓝蕾丝吊带外面套着开衫，牛仔裤，脚下高跟鞋」

**抄库字段进 prompt = 库变模具 = 回到"每两张共享 13.6 句"的老路。**
**判据 = 我用了库之后，这张图还是不是我自己想的？**

### 4.2 检索顺序

1. **先想画面**（不许先检索）
2. 想完，九维里**只查不确定的那一维**（全查一遍 = 变填表）
3. 查到 → **自己判断能不能用 + 怎么改** → 命中即用是错的
4. 写完 → 跑门禁 → 出图

---

## 五、四池分工

| 池 | 规模 | 给我什么 |
|---|---|---|
| 提示词资产池 | 3098 条（参考 1313 + 自出 1785） | 成品 prompt 的**句法组织**（不抄内容） |
| 姿势库 | 1439 条 / 287 个不同姿势 | **身体怎么摆**（承重面 + 关节 + 重心） |
| 服装库 | 1407 套 | **穿什么**（层次 + 材质 + 配饰） |
| 九维维度库 | 760 条 | **九维素材**（主题/角色身份/机位/景别/光源/姿态/观看关系） |
