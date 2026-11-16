### 2.0 🔴 `yuer_asset_search.py` = 姿势/发型/服装**统一入口**（11-04 新建 · 首选用它）
         data/portrait-meta-zh.json data/costume-meta-zh.json; do
  git show origin/main:$f > $f
done
```

（**0 整库 sparse-checkout** = 8690 个文件 = >7 分钟超时；数据 JSON 逐个 `git show` 取 = 秒级。**落盘后必核对条数** = 姿势 1439 / portrait 1499 / costume 1407 / costume-anime 440 = 少一条就是取漏了。）

### 2.1 costume_gallery_search.py（旧入口 · 保留）

```bash
cd ~/.hermes/skills/creative/yuer-image/scripts
./costume_gallery_search.py --cats                      # 列出所有分类 + 每个分类条目数（先跑这个看真实分类名）
./costume_gallery_search.py --cat セクシー --limit 5     # 按分类取，--cat 传日文分类名
./costume_gallery_search.py lace satin corset --limit 5  # 关键词 = 英文单词（lace/satin/corset/choker/stockings/fur/tulle/beret…）
./costume_gallery_search.py 水着 --paths                # 加 --paths = 直接打印图片路径（能拿去当参考图喂 ControlNet）
```

- **🔴 分类名 = 以 `--cats` 当场输出为准，不要凭记忆猜中/日文。** 写实服装库 `/path/to/data/costume_gallery/ai-costume-gallery/data/costume.json` 的分类字段是**日文 `カテゴリ`**（`セクシー`/`水着`/`ランジェリー`/`パーティ`/`春`/`夏`/`秋`/`冬`）；统一检索脚本 `prompt_asset_search.py costume` 读的是 pose 仓库里的 `costume-zh.json`（**中文 `分类`**）= **两库分类名不同源**。**实测：统一入口用中文「性感」命中；传日文 `--cat ランジェリー` / `--cat 水着` / `--cat パーティ` 全部 0 命中；日文名只对旧 `costume_gallery_search.py` 有效。** 判据 = 0 命中先跑 `--cats` 看这个库的真实分类名，**不是库空**。
- **🔴 分类名 = 以 `--cats` 当场输出为准，不要凭记忆猜中/日文。** 写实服装库 `/path/to/data/costume_gallery/ai-costume-gallery/data/costume.json` 的分类字段是**日文 `カテゴリ`**（`セクシー`/`水着`/`ランジェリー`/`パーティ`/`春`/`夏`/`秋`/`冬`）；统一检索脚本 `prompt_asset_search.py costume` 读的是 pose 仓库里的 `costume-zh.json`（**中文 `分类`**）= **两库分类名不同源**。**实测：统一入口用中文「性感」命中；传日文 `--cat ランジェリー` / `--cat 水着` / `--cat パーティ` 全部 0 命中；日文名只对旧 `costume_gallery_search.py` 有效。** 判据 = 0 命中先跑 `--cats` 看这个库的真实分类名，**不是库空**。
- **关键词 = 英文单词**，用中文词 = 0 命中（词表不匹配，不是库空）。
- 每条含 ID 前缀（`LNG-` / `AUT-` 等）+ 关键词 + 图片路径 = **成套信息**，整条抄进 prompt 才是「现成搭配」。

### 2.2 pose_gallery_search.py（姿势 / 发型 / 二次元服装）

```bash
cd ~/.hermes/skills/creative/yuer-image/scripts
./pose_gallery_search.py --cats                        # 真实分类名（子库名也在里面：portrait / costume-anime / depth）
./pose_gallery_search.py --cat portrait --limit 5      # 发型库
./pose_gallery_search.py <中文姿势词> --limit 5        # 中文命中率低，0 命中时直接用 Python 过滤「姿势名称」字段
```

**🔴 0 命中 ≠ 库空** = 词表不匹配。先 `--cats` 看真实分类名，或用 Python 直接过滤 JSON 字段。

