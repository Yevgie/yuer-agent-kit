# 第八部分 · 脚本 + 已知坑

| 脚本 | 干什么 |
|---|---|
| `scripts/yuer_ka_fast.sh` | **出图道唯一入口** = 0 门禁 + 出图 + 发飞书 + 双归档 + timing（`--gate` = 想手查才开）|
| `scripts/yuer_ka_fast.sh` | 底层统一入口（`--raw` / `--report-only` / `--dry-run` / `--check-only` / `--force` / `--model` / `--workflow` / `--style` / `--caption` / `--seed`）|
| `scripts/yuer_ka_pai_zhi_chu.py` | 真正的出图执行体（wrapper 调它）|
| `scripts/yuer_run_nolora.py` | 0 LoRA 底模直出 = 画面里的人不是语儿时走这条 |
| `scripts/count_prompt_chars.py` | 长度报数 + 5 结构段 + 自毁排版 |
| `scripts/check_prompt_subject.py` | 主体身份预检 = 决定走哪条链路 |
| `scripts/check_outfit_lock.py` | 外观锁 = 下装 / 鞋履 / 画外描述 / 单人物 |
| `scripts/check_body_anchors.py` | **身材锚自检 = 主人报身材不对时的分诊工具**（社区词/腿长锚/围度/腰臀胸句齐不齐 + 同部位叠写 + 负向词 + 十头身比 + 禁词）| `--selfcheck` = 内置正/负样例自测 |
| `scripts/yuer_prompt_search.py` | 提示词资产池检索 = 出图前先查库 |
| `scripts/yuer_asset_search.py` | 四池统一检索（prompt / pose / costume / dim）|

| `scripts/yuer_breast_expose_prefix.py` | 实战 224 露出前缀配方（写露出 prompt 时对表） |
| `scripts/ltx25_i2v.py` | LTX-2.5 图生视频工作流构建（出视频要动节点时） |
| `scripts/yuer_lora_audit.py` | 读现役工作流真实 LoRA 配置（要查当前挂了哪些 LoRA） |
**🔴 已知坑（改任何工作流字段前必看）**：
- 节点 863 的字段在 `wf['863']['inputs']['input_string']`，**不是** `wf['863']['input_string']`（撞 KeyError）。
- 真正的 seed 在 `SeedNode(851).inputs.seed` = **不是** `KSamplerAdvanced.noise_seed`（那是连接引用不是 int）= 改错 = 每次出同一张图。
- `patch` 工具改不了 `config.yaml` = 用 terminal `sed -i`。
- `| grep` / `| tail` 会吃掉脚本自己的退出码 = **判 exit 用 `PIPESTATUS[0]`**；判成功看 stdout 三件套（`完成 (XX.Xs) success` + `落盘 …png = NNN 字节` + `✅ 图已真发飞书`），**不看 `$?`**。
- 长任务日志必落文件 = `| head/tail` 会 SIGPIPE 掐死脚本。
- ComfyUI 地址 = 全链路读 `yuer_image_constants.DEFAULT_COMFYUI_SERVER` = 读不到 exit 2 绝不猜端口。
- **改动带脚本的技能 = 改完真跑一次最小链路** = 文档对但脚本没跑 = 链路断在暗处。
- 🔴 **prompt 里的非年龄数量一律写阿拉伯数字**（`30-degree` ✅ / `thirty degree` ❌）= **年龄正则会把 `thirty`/`fifty` 这类英文数字词读成年龄 = 主体判定被污染 = 静默切错链路（脸锁跟着走错）= 门禁从安全网变成误伤源**。年龄本身照写 `a 20 years old young Asian woman`。
- 🔴🔴 **prompt 文件名 = 必须带唯一后缀**（`/tmp/prompt_<主题>_<日期时分>.txt`）= **write_file 撞到同名旧文件会「拒绝覆盖」= 它返回错误但不抛异常 = 批处理里的下一步照样跑 = 拿几天前的旧稿出图 = 主人收到一张跟自己要求无关的图**。**机制 = 同名文件已存在 = 写入被拒 = 但渲染读的还是那个旧文件**。**判据 = 批处理 execute_code 里 write_file 的返回值必看（带 refused/error 就地停）= 渲染前核对 prompt 首行是不是本轮写的**。

## 8.0 references / scripts 指针

**细则全文 = `references/yuer-image-细则全集.md`**（含：门禁高频 FAIL 与成品牌改刀 / 穿模部位排查表 / 身体颜色写死三锚 / 局部特写与微距配方 / 介质场景唯一亮部配方 / 玻璃反光板写法 / 六维场景设计 / 抓拍感与诱惑优先级 / 公共场景人群与下装必写 / 单人场景主人在场写法 / 日常套图生活连续剧 / 借壳骚内核示例 / 提示词资产池检索 / 提示词池批量入库 / 服装图库 / 存档SOP / 落盘名唯一化机制 / 模型路由与四工作流能力矩阵 / 实战档索引）。

**参数唯一真值**：`references/铁律/02-身材特征档.md`（身材两条锚 + 私处三锚 + 乳头锚 + 皮肤锚 + 禁词表 + 三条机械门 + 景别裁切）。
**出图道速查卡**：`references/出图速查卡.md`（= 出图前唯一该读的一张 = 上面这些的浓缩操作版）。

---

