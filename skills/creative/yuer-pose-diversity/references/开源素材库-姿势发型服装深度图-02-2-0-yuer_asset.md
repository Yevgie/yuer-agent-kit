### 2.0 🔴 `yuer_asset_search.py` = 姿势/发型/服装**统一入口**（11-04 新建 · 首选用它）

**🔴 这个脚本是出图链路的公共入口 = `yuer-image` 技能里也有一行指针指到这里** = 四库都在 pose_gallery 仓库（数据 JSON 已落盘本地 = 秒级）：

```bash
cd ~/.hermes/skills/creative/yuer-image/scripts
./prompt_asset_search.py --libs                       # 四个子库 + 条数
./prompt_asset_search.py pose --cats                  # 姿势分类名
./prompt_asset_search.py pose 跪立 --limit 5          # 姿势（中文名/分类/机位）
./prompt_asset_search.py hair --cats                  # 发长名
./prompt_asset_search.py hair 长发 --limit 8           # 发型
./prompt_asset_search.py hair 空气刘海 --prompt       # 查具体发型名
./prompt_asset_search.py costume --cats               # 服装分类名
./prompt_asset_search.py costume 泳装 --prompt --limit 5   # 写实成套服装
./prompt_asset_search.py costume-anime 水手服 --prompt --limit 3   # 二次元成套服装
./yuer_asset_search.py --libs                       # 四个子库 + 条数
./prompt_asset_search.py pose --cats                  # 姿势分类名
./prompt_asset_search.py pose 跪立 --limit 5          # 姿势（中文名/分类/机位）
./prompt_asset_search.py hair --cats                  # 发长名
./prompt_asset_search.py hair 长发 --limit 8           # 发型
./prompt_asset_search.py hair 空气刘海 --prompt       # 查具体发型名
./prompt_asset_search.py costume --cats               # 服装分类名
./prompt_asset_search.py costume 泳装 --prompt --limit 5   # 写实成套服装
./prompt_asset_search.py costume-anime 水手服 --prompt --limit 3   # 二次元成套服装
```

**🔴 `--prompt` = 直接打印可进 prompt 的英文串** = 服装库给的是英文逗号串（`pink knit turtleneck mini dress stockings heels`）= **现成的搭配思路 = 整条用 / 取几件 / 照思路重搭 = 三种都合法**（见 §6）。发型库和姿势库**没有英文关键词字段** = 只给中文名（发型名 / 骨架名+分类+机位）= **英文动作短语和发型英文词自己翻**。

**🔴🔴 服装分类名 = 两套命名不同源 = 中文「春/夏」跟日文对调了 = 按条数认，不按名字认**

统一入口 `prompt_asset_search.py costume --cats` 吐**中文分类名**；写实库 `costume.json` 的字段是**日文 `カテゴリ`**。两套名字**不是逐个对应的** —— 按条数对位后发现春/夏两项是**反的**：
统一入口 `prompt_asset_search.py costume --cats` 吐**中文分类名**；写实库 `costume.json` 的字段是**日文 `カテゴリ`**。两套名字**不是逐个对应的** —— 按条数对位后发现春/夏两项是**反的**：

| 中文（统一入口） | 条数 | 日文（costume.json） | 条数 |
|---|---|---|---|
| 夏季穿搭 | 254 | 春 | 254 |
| 冬季穿搭 | 253 | 冬 | 253 |
| 秋季穿搭 | 244 | 秋 | 244 |
| 春季穿搭 | 215 | 夏 | 215 |
| 内衣・睡衣 | 199 | ランジェリー | 199 |
| 性感穿搭 | 140 | セクシー | 140 |
| 泳装・度假 | 54 | 水着 | 54 |
| 派对・礼服 | 48 | パーティ | 48 |

**🔴 机制 = 分类名是各库自带的元数据 = 翻译时按「顺序」对位而不是按「含义」对位 = 春↔夏 错位 = 按名字挑季节 = 拿到反季节那一套 = 我自己都看不出挑错了 = 主人看到「夏天」图穿的是春款**。

**判据 = 要某一季的成套 = 先 `--cats` 看**条数**，再按条数回查日文那一项 = 名字只用来往检索脚本里传**。**别写「我按中文搜了春装」就当筛对了 = 先核条数。**

**🔴 服装库的检索词 = 服装词 / 英文关键词 = 不是场景词也不是情绪词**：「睡裙 / 浴袍 / 凌乱 / 刚睡醒」这类**场景-状态词库里根本没有 = 0 命中 = 不是库空**。正解 = **先按分类取一批条目，再从取回的那批里挑最接近这个场景的一件**（取回的条目里带 `服装名称` + 关键词串 = 从里面挑 = 场景匹配发生在**我这一层的挑**，不在检索器里）= **检索器只认服装词 = 场景要我自己翻译成服装词**。条目前缀（如 `WIN-` / `AUT-` / `LNG-`）= 成套 ID = 整条抄进 prompt 才是「现成搭配」。

**🔴 检索参数 = `--cats` 列出的分类名本身 = 0 拼接品名**：传 `秋季` 命中，传 `秋季连衣裙` / `秋季 迷你裙` = **0 命中 = 不是库空**（分类字段是单一值 = 整词匹配 = 多一个词就落空）。**正解 = 传分类名单独取一批（`--limit` 给大）= 再在取回的条目里按 `服装名称` + 关键词串自己挑。** 判据 = 0 命中时先 `--cats` 看分类名 = 拿分类名原样传 = 再不行就 `--limit 50` 整批取回自己筛。

**🔴 发型库同理 = 检索参数 = 发长名（`长发` / `中长发`）或完整发型名** = 传 `长发 空气刘海` = 0 命中（名字里的空格分隔 = 多词 = 落空）。**取回的中文发型名 = 设计依据 = 英文发型词自己翻**（见 §6）。

**🔴 发型库的真坑**：「收腰感短发（**长发**尾・空气刘海）」里含「长发」= 子串匹配会命中 435 条短发 = **查发长必须按 `发长` 字段精确匹配**（脚本已做 = 按名字查）。手写过滤时同理。

**🔴 四套 JSON 键名各不一样**（`pose-zh` 全中文 / `portrait-zh` 用 分区·发长·发型名称·标题 / `costume-zh` 用 分类·服装名称·标签·关键词 / `costume-anime-zh` 用 一级分类·分类·服装名称·日文名称·标签·关键词）= **别拿一套键名去读另一套**。

**🔴 库数据已在本地 `data/`（11-04 已全部落盘）** = `pose-zh.json` / `pose.json` / `portrait-zh.json` / `portrait.json` / `costume-zh.json` / `costume.json` / `costume-anime-zh.json` = **检索直接读本地 = 秒级，不需联网**。**🔴 上游更新后要重新覆盖落盘**（否则永远读到旧版）：

```bash
cd /path/to/data/pose_gallery/ai-pose-gallery-zh
git fetch origin
for f in data/pose-zh.json data/pose.json data/portrait-zh.json data/portrait.json \
         data/costume-zh.json data/costume.json data/costume-anime-zh.json \
