# 六、姿势参考图库（ai-pose-gallery-zh）

> **与提示词池互补**：提示词池解决「这句话怎么写」，姿势库解决「人怎么摆」。
> 我出图最大的短板一直是姿势 —— 只能写英文去说服底模，底模经常给我歪的。

## 6.1 库里有什么

- **1439 条记录 = 287 个姿势 × 5 个视角**（正面 / 斜侧 / 侧面 / 俯视 / 仰视）= **姿势数按姿势名称去重**（原库 P001~P080 编号有同名复用 = 用编号去重会多算）
  **🔴 「287×5=1439」是错的** = 287×5=1435 ≠ 1439 = 真实姿势数必须现算（`len({(分类, 姿势名称) for ...})`），0 引用旧数字当结论。
- 4 个体系：全身单人・标准系 / 全身单人・性感系 / 上半身单人 / 双人缠绵
- 26 个动作分类（跪立・四肢着地 / 站立・单腿高抬 / 猫式 / 骑乘风 …）
- **姿势名全中文** → 可直接翻成英文姿势锚，比瞎写 `leaning forward with one leg raised` 精确得多

## 6.2 落盘位置

```
/path/to/data/pose_gallery/ai-pose-gallery-zh/
├── data/pose-zh.json      # 1439 条记录（体系 / 分类 / 姿势名 / 视角 / 文件名）= 中文版
├── data/pose.json         # 同一批记录的英文版 = 用法 A 的英文字段来源（键名先 print 再用）
├── data/meta.json  meta-zh.json   # 体系分类字典（4 个体系名）
├── data/translations.csv  # 中英对照表 = 姿势名 / 分类名逐条对照
├── img/                   # 1439 张原图
├── thumbs/                # 1439 张缩略图
├── index.html             # 本地可直接用浏览器翻的姿势画廊（翻姿势名 + 看线稿 = 比调脚本快）
├── og-cover.jpg  robots.txt  sitemap.xml  _headers
└── scripts/  download.py  verify.py  i18n.py  apply_translation.py  build.sh
```

**🔴 挑姿势最快的路径 = 开 `index.html` 用浏览器翻** = 比反复调 `pose_gallery_search.py`（AND 语义 + 只吐 1 条）快一个量级；
`pose-zh.json` / `pose.json` 才是脚本化批取时的数据源。

## 6.3 🔴 获取方式（全量 clone 会断）

`git clone` 全量拉到 ~226M 时会以 `fetch-pack: unexpected disconnect while reading sideband packet` 中断。
正解 = **sparse 检出 + 官方脚本补全**：

```bash
cd /path/to/data/pose_gallery
git clone --depth 1 --filter=blob:none --sparse https://github.com/anhao/ai-pose-gallery-zh.git
cd ai-pose-gallery-zh
git sparse-checkout set data thumbs scripts
python3 scripts/download.py          # 补 img/ 全量原图
python3 scripts/verify.py            # 期望 2878 文件，异常 0 才算装好
```

`sparse-checkout` 若报 `.git/index.lock` 残留 → 删掉锁文件再重跑。
**装完必须跑 verify.py** = 官方校验通过才算装好（实测 img 637.6MB + thumbs 22MB = 885MB 落盘）。

## 6.4 两种用法

**用法 A（默认，成本最低）= 查中文姿势名 → 写英文姿势锚。**
零生图成本，直接治「底模给我歪姿势」。

**用法 B = 线稿当 image2img 参考源真出图。**
流程 = 复制 wash 工作流 → `LoadImage` 换成姿势线稿 → denoise 调到 **0.85~0.9**（洗掉线稿质感）→ 出图。
实测：**姿势结构保得住**（倒 V 前倾单腿高抬 / 跪坐脊柱挺直都对得上），
但**胯部朝向这类细节只「像」不「锁死」**。

**🔴 前提 = 本机 ComfyUI 只有 Anima-LLLite 一个 ControlNet**，没有标准 openpose/dwpose 控制模型
→ 走的是「线稿当参考源 + 高 denoise」，不是姿势硬控。想要硬控必须先装控制模型 + 检测节点，
那是常驻配置变更，**0 擅自改**。

## 6.5 🔴 版权

代码 MIT，**图片著作权归原作者**（原作者日文站 ギア / 中文镜像维护者 anhao）。
当本地参考自用没问题 → **禁再分发 / 禁商用 / 禁把图塞进公开图库**。

## 6.7 🔴 检索姿势库的两个坑（脚本层面）

```bash
/usr/bin/python3 scripts/pose_gallery_search.py --cats          # 列 26 个分类 + 条数
/usr/bin/python3 scripts/pose_gallery_search.py 坐 --limit 30      # 单关键词搜（多词 = AND）
/usr/bin/python3 scripts/pose_gallery_search.py --system 全身单人・性感系 --cat 坐姿 --angle 侧面
/usr/bin/python3 scripts/pose_gallery_search.py 骑乘 --paths      # 打印线稿路径（用法 B 用）
```

1. **多词是 AND，不是 OR** = `"浴缸 坐 靠"` = 三个词都要出现在姿势名里 = 中文姿势名很少这么写 = 报 `0 命中` = **这不是「库里没有」，是筛选太紧** = 先用单关键词（`坐` / `骑乘` / `抱头`）再筛。
2. **脚本按姿势名去重 + 单关键词只吐 1 条** = 想看某分类的**全部**姿势名（写 prompt 时挑姿势）= **直接读 `data/pose-zh.json` 按 `(分类, 姿势名称)` 去重排序**：

```python
import json
d = json.load(open('/path/to/data/pose_gallery/ai-pose-gallery-zh/data/pose-zh.json'))
for c, n in sorted({(r['分类'], r['姿势名称']) for r in d}):
    print(c, '|', n)
```

## 6.8 🔴 英文姿势锚 = 抄库里的英文字段，0 手译中文姿势名

**机制**：中文姿势名（如「M字开腿（坐位・双手后撑）」「单膝立起・双手抱头后」）= 底模不认，
必须翻成英文姿势锚；**手译会丢精度**（同一句中文能对应多种英文写法，底模认哪种是社区词频决定的）。

**正解 = 库里已经有一份同批记录的英文版 = 按同一条 `id` 去取英文字段，逐字抄进 prompt。**

```bash
# ① 先看清 pose.json 的真实键名（0 凭印象猜键名）
python3 -c "import json;d=json.load(open('/path/to/data/pose_gallery/ai-pose-gallery-zh/data/pose.json'));print(d[0])"

