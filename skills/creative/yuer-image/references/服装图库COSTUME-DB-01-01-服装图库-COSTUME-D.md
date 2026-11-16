# 服装图库 · COSTUME-DB-01（姿势库的姊妹库）

> **唯一职责** = 出图时当**衣服词典**（挑一套 → 拆成提示词里的服饰段），编辑道时当**换装参考源**（当 image_2 喂给 Qwen21）。
> **它本身 0 出图**（幽灵人台 = 无人物服装图）= 直接喂底模只会得到一张穿衣服的假人。

---

## 一 · 库 facts

| 项 | 值 |
|---|---|
| 原始站 | `https://ai-costume-gallery.pages.dev/` |
| 标题 | 衣装集 COSTUME-DB-01 |
| **与姿势库同作者** | 姿勢库 = `anhao/ai-pose-gallery-zh`（原作者 `giaaibusi`）= **同一作者的姊妹库** = 姿势管「身体怎么摆」+ 服装管「穿什么」= 天然互补 |
| 数量 | **1407 套** |
| 规格 | 1366×2048（2:3）webp（约 93KB/张）· 原尺寸 PNG 约 1.1MB/张 · 缩略图约 7KB |
| 画面 | **幽灵人台**（无头 · 无手臂 · 衣服撑在隐形身上）+ 浅冷灰纯背景 = **纯服装 · 0 人物** |
| 授权 | 免费用于作品创作 / 商用 / 编辑 / 参考 · **禁原图转售与再配布** · 署名不需要 · 图像均为 t2i 生成的虚构服装 |

**本地路径** = `/path/to/data/costume_gallery/ai-costume-gallery/`
- `img/<ID>.webp` = 全量图
- `data/costume.json` = 元数据（id / カテゴリ / キーワード / サムネ / 画像 / 原寸）

## 二 · 8 个分类（日文原文 = 检索时要用日文）

| 分类 | 中文 | 数量 | id 前缀 |
|---|---|---:|---|
| 夏 | 夏 | 254 | `SUM` |
| 冬 | 冬 | 253 | `WIN` |
| 秋 | 秋 | 244 | `AUT` |
| 春 | 春 | 215 | `SPR` |
| ランジェリー | 内衣/睡衣 | 199 | `LNG` |
| セクシー | 性感 | 140 | `SXY` |
| 水着 | 泳装 | 54 | `SWM` |
| パーティ | 派对 | 48 | `PTY` |

## 三 · 检索

```bash
cd ~/.hermes/skills/creative/yuer-image
/usr/bin/python3 scripts/costume_gallery_search.py --cats
/usr/bin/python3 scripts/costume_gallery_search.py lace white --limit 8   # 多词 = AND
/usr/bin/python3 scripts/costume_gallery_search.py --cat ランジェリー --limit 5
/usr/bin/python3 scripts/costume_gallery_search.py --cat セクシー --paths   # 只出路径
/usr/bin/python3 scripts/costume_gallery_search.py --random 5              # 系列出图抽签
```

**坑**：
1. **关键词是英文**（原库就用英文）= 中文搜不到 = 只能搜英文单词（`lace` / `denim` / `stockings` / `blazer`）。
2. **分类是日文** = 检索时用日文分类名（脚本已内置中文对照输出）。
3. 库根写死 = 可用环境变量 `COSTUME_GALLERY_ROOT` 覆盖。

## 四 · 关键词结构（= 提示词服饰段的原料）

每套的 `キーワード` = **颜色 + 单品 + 材质 + 鞋包配饰** 的空格串，直接可翻成提示词：

```
SPR-0001 | 春 | ivory frill knit denim mini skirt coat socks white sneakers
LNG-0107 | ランジェリー | ivory bra briefs lace black velvet ribbon stockings heels choker
SXY-0159 | セクシー | mint velvet mini dress stockings heels gloves
```

**用法** = 挑一套 → 把关键词逐项抄进 brief 的「服饰」段 → 再按本场景补穿着方式 / 材质质感 / 内层 / 鞋履锚。
**🔴 0 直接把关键词整串喂底模**（它不是提示词 = 没有主体/场景/光线）= 必须拆解改写成自然语言服饰句。

## 五 · 下载（代理下 curl 会随机失败）

**坑**：走本地代理 7890 时 `curl` 拉大图会随机返回 `code=000`（CONNECT 建连后无响应）= 单线程 curl 基本跑不动。
**正解** = `urllib` + 线程池 + 指数退避：

```python
# 16 线程 / 每线程独立 UA / 失败退避重试 / 已存在跳过 / 最后再跑一遍补残
from concurrent.futures import ThreadPoolExecutor, as_completed
# 见 scripts/costume_fetch_mt.py（同款逻辑）
```

**收尾判据 = 文件数 + 每张字节数**：0 信任「脚本说 ok」= 逐个 `os.path.getsize > 2000` 核。
**残留零星失败 = 补拉一轮**（长退避 + 更多重试）= 不要重跑全量。

**✅ 已装完= 1407/1407 = 0 缺图 = 117MB**
- `img/` 1407 张 webp，逐张 `getsize > 2000` 全过，抽样 6 张 `Image.open` 全部正常解码 = 1366×2048。
- 16 线程首轮 `ok=1240 fail=48` → 补拉脚本（单线程长退避 8 次重试）`recovered 48` → 零缺。
- **教训 = 线程池跑完必须跑一次「缺图核对 + 补拉」**（首轮 fail 数不为 0 = 一定有洞）= 只看 FINAL 行会漏。

## 六 · 用法 A：出图道 = 衣服词典（默认）

1. 跑检索挑一套（按季节 + 场合 + 露出需求）
2. 把 `キーワード` 拆开 → 逐项写进 brief 服饰段（颜色 + 单品 + 材质）
3. 仍走本技能完整 5 步 + 两道门禁 = **服装库不替代门禁**
4. **🔴 库图的幽灵人台造型 0 抄**（它没有腰臀比例、没有真人动态）= 只借「穿什么」，不借「怎么穿在身上」

## 七 · 用法 B：编辑道 = 换装参考源（image_2）

服装库图当 Qwen21 的 `image_2` = 整套换装（比只写文字服装段准得多）。

**🔴 两条必写的排他句**（不写 = 它把人台的怪体型和背景一起搬过来）：

```
只参考 <image2> 的服装本身，不要参考它的白色背景，不要参考它的无头人台体型，也不要参考它没有手臂的身体。
```

**🔴 `image_1` 必须是**单幅底图**（被改的那张）= **0 用四宫格**：四宫格当 image_1 = 它直接输出四宫格（prompt 写「不要分格」也救不回来）= 锁脸改用「保留她原有脸型五官发型发色」的 preserve 句，而不是靠 image_1 锁。

**换装提示词骨架**：

```
把画面里这位女生身上原来的衣服，整套换成 <image2> 里的那一整套服装：<逐件点名：颜色+单品+材质>。
服装的款式、颜色、层次、材质和配件全部严格照 <image2>。
只参考 <image2> 的服装本身，不要参考它的白色背景，不要参考它的无头人台体型，也不要参考它没有手臂的身体。
她的脸型、五官、发型发色、身材比例、<姿势>、<背景>、<光线>和构图全部保持不变。
只生成一张单人单幅竖版照片，不要四宫格，不要并排双图，不要拼图，不要多格排版，不要文字，不要水印。
```

**🔴 换整套 = 属于「一处一改」的合法例外**（改的属性 = 服装 = 一个属性）= 之前「一次改三件衣服 = 重画」那次失败是因为同时改了**上衣+裙子+外套**三个独立属性；这里换的是**一整套**（一套 = 一个属性）= 实测通过。

