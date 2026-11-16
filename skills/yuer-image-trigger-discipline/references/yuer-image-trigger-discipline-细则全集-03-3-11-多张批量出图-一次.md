## 3.11 🔴 多张批量出图 = 一次 terminal 调用里串完（0 一张一调用）

**🔴 现役最快入口 = `bash scripts/run_batch.sh <tag> <YYYY-MM-DD>`**：约定读 `/tmp/prompt_<tag>_n1.txt` … `n5.txt`，一次调用串行跑完五张，每张自带真发 + `.sent` 守卫，末尾打 `===== BATCH <tag> DONE =====`。实测五张 ~60s（12~14s/张）。**汇报判据 = stdout 里 `✅ 图已真发` 的行数 == 5**（少于 5 = 有一张没到，看 `❌` 那行再补跑那一张，不要重跑全批 = 双发）。

主人要「出几张分别展示 X/Y/Z」= 多张 = **每张一次 wrapper**（每张一个 leave_name = 一次真发）。

**🔴 串在一次调用里跑，不要一张一调用**：

```bash
bash ~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh /tmp/prompt_a.txt "部位_甲" 2>&1 | grep -E "完成|落盘|真发"
bash ~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh /tmp/prompt_b.txt "部位_乙" 2>&1 | grep -E "完成|落盘|真发"
```

理由：单张采样 ~10-14s = 两张 ~30s = 一次调用跑得完。**一张一调用 = 每次往返都要重新发一段 prompt 内容 = 上下文膨胀 + 主人等待被拉长**。

**🔴 别一次调用里挂 4+ 张**：单次 foreground 调用上限 600s = 超了会被系统 promote 成后台进程 = 完成通知回流到对话 = 在我回复中间插一段「后台任务完成」= 主人看到图文两截。

**🔴 后台跑的那批 = 汇报时 0 重复发**：完成通知只是内部确认 = 主人手机已经收到图 = 只需回一句「那批都到了」= **0 重新发一遍、0 逐张复述内容**。

**🔴 每张的 prompt 先全部落盘再跑** = 串行「跑一张看结果再写下一张」会不自觉复制上一张的句子 = 骨架重复（见 `yuer-pose-diversity` §1.4）。

**🔴🔴 批量 = 「全部落盘 → 全部过门禁 → 再开跑」三段式**（0 边跑边修）：

```
1. N 段 prompt 全部先落盘（/tmp/prompt_<batch>_<n>.txt）+ 同时 copy 一份进
   /path/to/media/<日期>_<batch>_<n>.prompt.txt
   （= 出图内容与 caption 同一份源头 = 图文两截从这一步堵住）
2. N 段全部先落盘 → **0 门禁，直接开跑**（🔴 常态链路 0 跑门禁 = 批量也 0 跑 = 规矩在写稿时守住；想查再加 `--gate`）
3. N 张串在一次 terminal 调用里跑（每张一个 leave_name = 一次真发）
4. 跑完核对 N 个 .sent 标记 + N 个 png 都落盘
```

**为什么第 2 步不能省**：边跑边修 = 修到第 3 张才发现超长 = 前面 2 张已经白发给主人 = 主人手机收到 2 张 + 一句「还在调」= 图文两截。

**🔴 批量时的真坑**：第一张可能触发一次重做（穿模门禁）= 那张比别的多花 ~10-15s = **不是故障 = 0 重跑全批** = 重跑 = 主人手机双发（`.sent` 守卫会拦 = exit 5 = 那是「已发过」不是失败）。

**🔴 「分别展示 X / Y / Z」= 一部位一张图 = 各自独立构思**

主人说「出几张，分别展示胸/腰/臀/腿」= 每张**只锁一个部位** = 底模会把 prompt 里所有身体词往画面上堆 = 四张都写 = 四个部位全抢戏 = 主人要看单一重点 = 白跑。

| 规则 | 撞车长相 |
|---|---|
| **一部位 = 一张图** | 胸/腰/臀/腿全写进每张 = 四张都抢戏 |
| **每张换 4 个维度**（场景时段 + 动作 + 机位焦段 + 露出部位）| 四张共用一个浴缸 + 同一个弯腰 = 同构图换滤镜 |
| **机位为该部位而选** | 胸 = 上半身近距仰视 · 腰 = 侧身齐胸 · 臀 = 侧后低机位 · 腿 = 齐膝远景全身 |
| **身材参数 = 唯一真值在 `creative/yuer-image/references/铁律/02-身材特征档.md`** | 参数写进 prompt 时只引那一份 = 0 多处抄写打架 |
| **🔴 单图单部位 = 只写画面里拍到的部位** | 拍臀那张 0 重点写胸 = 底模会把所有身体词往画面上堆 = 都写就都抢戏 = 主人要看单一重点 = 白跑。真值同在那份身材档 |
| **🔴 穿衣服/泳衣 = 胸词保留 + 乳头词必删** | 穿模的真凶是 `nipple`/`areola`（= 给底模的「画乳头」指令，穿衣也画）不是 `bust`/`cleavage`（= 体积描述，画不出乳头）。删掉胸 = 大胸参数没了 = 违背钦定。机械门 `grep -oE 'nipple|areola'` 命中且她穿着衣服 = 删掉再跑 |
| **🔴 身材三禁（大小 vs 形态）** | 底模对关键词是字面执行：**禁低垂形态词**（`resting low and heavy`/`sagging`/`drooping` → 换 `sitting high and firm ... no droop at all`）· **禁肥臀粗腿**（`huge ass`/`bubble butt`/`thick thighs` → 臀只写圆润上翘如蜜桃、大腿写细、加腰臀比句 = 臀肥会把体积摊到大腿，腰臀比一没就变臃肿）· **锁骨一律不写**（禁骨感凹陷词 = 整体丰满有肉）。机械门 `grep -oE 'resting low and heavy|sagging|drooping|huge ass|bubble butt|plump rounded buttocks|voluptuous|curvaceous figure|thick thighs|collarbone hollow'` = 命中 = 换现役锚（真值 = `creative/yuer-image/references/铁律/02-身材特征档.md`）|

**🔴 每张的机位理由 = 「我要拍的那个东西恰好落在这个高度和距离上」**（`yuer-prompt-writer` §1.4 第 2 句）= 不是「要拍全身所以平视」。

