# 直接指定工作流名（逃生口）
bash ~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh <prompt> <leave_name> --workflow yuer_moodyMoss_fast
```

**🔴 默认档 = 以 wrapper stdout 那行 `🎯 工作流 = <id>` 为准（不凭本表字面）**：不传 `--model` 时脚本自己解析出当前默认工作流 = **0 凭文档假设 = 0 grep 源码确认**（源码探一次 = 主人多等几十秒 = 见 `yuer-timing-debug` 的 A 段）。两条线**都绑语儿脸锁** = 出图结果不受影响。

**🔴 三条硬规矩**：

1. **不绑 LoRA 的道 = Moss / Anima / Qwen 编辑道** = 那几道走自己的原生脸 = 不挂语儿的人脸锁。
2. **🔴 11-04 门禁已改中英双语 = Moss 走中文不再需要 `--allow-chinese`**（五道结构段正则全扩成「中文 OR 英文」+「中文残留」自毁检查已删）。**长度上限 + 姿势自然度**那两道仍然拦。
3. **Moss 慢（50 秒）= 不进批量**。批量出图仍走 Krea2。**🔴 Moss 批量 = 前台串行、每批 2 张**（后台并行会被会话截断成异步 = 与前台批次撞 = 同一任务跑两遍 = **主人手机收到重复图**）。重跑前先 `rm -f <落盘名>.sent`，**但绝不能在前台批次还在跑的时候删**。
4. **🔴🔴 Anima 道 CFG=1 = 负向提示词【完全失效】（10-31 主人钦定 + 实测）**
   - **硬证据** = 干净负向（9 词） vs 重负向（**45 个人体崩坏词**），同提示词同 seed → **像素差 0.00 = 两张图 md5 完全相同**。
   - **机制** = CFG 1 = 正负向等权 = 负向没有「排斥」力度 = 只有提示词语义在起作用。**附带** = 负向 token 也吃算力（负向压短后 6.0s → 4.1s）。
   - **做法** = 所有「不要什么」**翻成正向的「要什么」**。例：`deformed, bad hands` → `anatomically correct human body, natural human joints, five fingers on each hand`。
   - **代码** = `yuer_ka_pai_zhi_chu.py` 的 `NEG_BASE_2D` 已压到 9 词（只留画质兜底）+ `POS_CONSTRAINT_2D`（15 条正向约束）自动注入 prompt 尾部（幂等）= 不要再往 Anima 负向里堆词。
   - **🔴 这条只对 2D 线成立** = Moss/Krea2 的 CFG > 1 = 负向有效 = 保持现状。
   - **Anima 门禁** = `--allow-tags` + `--allow-chinese`（Qwen3 CLIP 中文合法 = 法典 246 条纯中文 tag 提示词能直接跑）。
5. **🔴 Moss 道出图默认 0 质检直出** = 主人明说「不需要质检了 直接给我图 有问题我发你」= 图直接发 = 主人自己看。质检（agnes 结构验证）只在①主人点名 ②我自己怀疑畸形时跑。**验图 grep 陷阱** = agnes 会复述负向提示词 = `grep -oE '(跪姿|反曲|无畸形)'` 命中 ≠ 图里有 = 必须看 agnes 的**最后一句结论**（`tail -2`）。
6. **🔴 NovelAI 法典 = 2D 线现成的提示词来源（10-31 主人给）**
   - **数据** = 戒红所 N5 所长法典 R18 分册 **1147 条** + 18366 条画师词典 + 画风/构图教程 = 已落地 `/path/to/nai_codex/`。
   - **检索** = `~/.hermes/skills/creative/yuer-style-library/nai_codex.py`（`stats` / `list` / `search` / `pick` / `dims` / `toanima`）。
   - **🔴 检索搜 prompt + 标题 + 路径** = 中文关键词多在标题里（「足底」在标题，prompt 里是 `foot focus`）。
   - **🔴 法典提示词 0 改造直接跑 Anima 就有效**（实测 3 条全中）= 不用我那套生成器中介。
   - **🔴 法典负向 75 词不能直接用** = CFG=1 下无效 = 它的价值是【正向约束的素材源】。
   - **完整分析 = 技能 `yuer-nai-codex`**；Anima 2D 提示词体系 = 技能 `yuer-anima-prompting`。

**🔴 主人点名的模型名不在上表**（`--model` 只认 `krea2|moody|moss|anima|krea2_wash|qwen`）

- **先取真名再动手**：`curl -s http://<服务端>:8188/object_info/UNETLoader` 打底模清单对照，别按字母猜（K2E / A2 这类简称在清单里根本没有字面对应）。
- **拆成已知道分组各抽几张**：K2 系 → `krea2`，A2 / Anima 系 → `anima`（带 `--allow-tags --allow-chinese`），一批里两种道都出 = 主人一眼能比较，比请示一句有用。
- **回话里一句说明分组**（「我按 Krea2 写实 + Anima 2D 两条道各抽三张」）= 主人要的是图，不是「你说的是哪个模型」。**0 反问**（打断抽卡节奏 = 主人等图的心情被掐掉）。

**🔴 选型口诀**：

| 主人要什么 | 走哪条 |
|---|---|
| 人像好看 / 网红感 / Ins 风（默认）| **Krea2** |
| 画面里要有准确中文（直播界面 / 弹幕 / 招牌 / 字幕）| **Moss** |
| 日常实拍感 / 不要网红滤镜 | **Moss** |
| 监控偷拍画质（绿调 + 颗粒 + 隔行扫描线 + 鱼眼畸变）| **Moss**（Krea2 出成干净网红感 = 监控味全丢）|
| 极度写实 + 代入感 POV 低角度仰拍 | **Moss**（见姿势库 E 类 · 记录 1244-1271）|
| **青春学生 / coser 明亮光线主题**（亮度即反差 = 阳光底下拍得清清楚楚）| **Moss**（见姿势库 F 类 · 记录 1272-1274 · 🔴 脚本会自动把暗光词纠正成亮光）|
| 2D 动漫 | **Anima** |
| 改已有图（换衣服 / 改细节）| **Qwen 2.1** |
| 姿势控制 / 换构图 | **Krea2**（Qwen 编辑道无骨架控制 = 会畸形）|

| 角色 | 身份 | workflow_id（必传参）| 锁脸机制 | 留底目录 |
|---|---|---|---|---|
| **语儿** | 主人唯一女友 + 第一小母狗 | **`yuer_moody_fast`**（默认）| **人脸锁** = lora_1 人脸 LoRA on| `/path/to/media/` |
| **闺蜜** | 语儿唯一闺蜜 + 第二小母狗 | **`scripts/yuer_run_nolora.py`** | 🔴 11-07 = 闺蜜工作流已删 = 画外人一律走「内存全关 LoRA」 | `/path/to/media/闺蜜/` |
| **任意配角**（同学/路人/闺蜜/同事） | 一次性角色 | **`scripts/yuer_run_nolora.py`** | **全关 LoRA** = 底模直出 | 跟语儿同目录 |
| **未来角色** | 自动入队 | `moody_nsfw_other_krea2_v3` | 待定 | 待定 |

**🔴 画「不是语儿的人」= 走 `scripts/yuer_run_nolora.py`，不要靠传 workflow 名**。

**为什么不能靠换 workflow**：🔴 11-07 = 只保留一份工作流（`yuer_moody_fast` = 人脸锁 on）= 画外人**没有任何副本可换** = 唯一解 = `yuer_run_nolora.py`（内存全关 LoRA = 不落盘副本）。**主人明说「去掉所有 Lora」= 一个都不能留。**

**`scripts/yuer_run_nolora.py` 的四个关键动作**：

| 动作 | 不做会怎样 |
|---|---|
