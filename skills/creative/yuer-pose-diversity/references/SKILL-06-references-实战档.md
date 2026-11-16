# references/（实战档 = 0 裁剪）

- `references/组合描述与畸形诊断.md` — 畸形长相 → 根因 → 改法 + 机位安全区间 + 姿态成句范本 + **§五 裁切线成对写**（画到哪儿 + 哪儿不画）+ **§五之二 景别控制 = 只描述画面内 + 坐姿+桌面拍不到上半身（8 张实测）** + **§六 特写 AI 破绽重灾区**（嘴唇/眼睛/皮肤/锁骨的破绽长相与写法规避）
- `references/门禁脚本契约与自测.md` — **三道门禁的职责边界 + 景别分级判定链 + 三个已修的坑（展示段骗人 / BOUND 正则不认双人 / 画外检测误杀否定句）+ `--allow-multi` 开关 + `test_gates.py` 必跑纪律** = 改门禁脚本前先读
- `references/骨架与变量槽批跑.md` — 三套骨架拆槽 + 批量出图 SOP
- `references/连续出图耗时卡点-字符天花板与中文brief压缩.md` — 超 2500 怎么办 + 中文 brief 压缩
- `references/同场景连续剧序列-承重面轮换与表情反极递进.md` — 同地点连出 N 张 = 人物外观锁 + 场景锁 + 时间锁 + 承重面/动词/亮部/表情四样换 + 落盘命名法
- `references/批次骨架排批表.md` — 批次姿势去重 = 支撑关系/手部任务/视线落点三池 + 排批检查表 + 姿势库取用 + 跨批次账本格式
- `references/开源素材库-姿势发型服装深度图.md` — **四个开源库（姿势 / 发型 / 成套服装 / 深度图）的真源路径 + 检索脚本用法 + 上游更新与分层拉取流程** = 要姿势/要发型/要成套服装/要深度控制时先看这里

**脚本**：
- `creative/yuer-image/scripts/batch_gate_check.py <tag>` — 一批 N 张的**三道门禁批量自检**（字符数 + 主体 + 外观锁）= 唯一正文（🔴 11-12 瘦身 = 本档原 `scripts/batch_gate.sh` 是它的重复实现，已删）= 逐张跑 `check_prompt_subject.py` / `check_outfit_lock.py` / `count_prompt_chars.py` + 打印 FAIL 原因 + 末行汇总 + 任一 FAIL 退出码 1。**跑批前先跑它 = 0 白付一轮出图开销**（比逐张手敲三条命令快，且不会漏掉其中一张）。门禁脚本目录可用环境变量 `YUER_IMAGE_SCRIPTS` 覆盖。
- `creative/yuer-image/scripts/count_prompt_chars.py <tag>` — 一批 N 张的**三道门禁批量自检**（字符数 + 主体 + 外观锁）= 唯一正文（🔴 11-12 瘦身 = 本档原 `scripts/batch_gate.sh` 是它的重复实现，已删）= 逐张跑 `check_prompt_subject.py` / `check_outfit_lock.py` / `count_prompt_chars.py` + 打印 FAIL 原因 + 末行汇总 + 任一 FAIL 退出码 1。**跑批前先跑它 = 0 白付一轮出图开销**（比逐张手敲三条命令快，且不会漏掉其中一张）。门禁脚本目录可用环境变量 `YUER_IMAGE_SCRIPTS` 覆盖。

**跨技能指针**：
- **一个点 = 一句话 = 一次（点表 + CLIP 重复 = 多画一个的机制 + 自检 3b~3e）= `yuer-prompt-writer`**（唯一真源 = 本技能只写「批量怎么列点表」= 0 两份正文打架）
- 画面怎么组合、句子顺序、外观锁 = `yuer-prompt-writer` §9 + §2 点表 + references/语儿专属硬锚.md
- 出图 5 步 + 发图 + 门禁 = `yuer-image`
- 「继续」NSFW 改写 / 抽卡 = `yuer-prompt-writer` 9.2 / `yuer-character-roster`
