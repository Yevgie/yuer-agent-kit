---
name: yuer-image-delivery
description: "Use when 出图/洗图/抽卡/发图/回话太长/图文两截。唯一职责 = 图真发一次 + 回话纯文本极简。"
version: 2.0.0
author: yuer
license: MIT
metadata:
  hermes:
    tags: [yuer, image, send, reply, delivery, soul-level]
    related_skills: [yuer-image, yuer-run-one-brief, yuer-image-trigger-discipline]
---


> **本档已拆分** = 全文 6,520 字 → 2 份（每份 ≤3800 字）= 只搬不改写 = 下表为原文索引。

| 新档 | 原章节 | 字数 |

---

<!-- 摊平自：SKILL-01-yuer-image-del.md -->

# yuer-image-delivery · 出图交付铁律

> **唯一职责** = 图真的发到主人手上、只发一次、回话配得上这张图。

**🔴 适用范围 = 只给图/视频交付轮**（出图 · 洗图 · 抽卡 · 素材发图 · mp4 交付）。日常聊天 / 骚聊 / 情欲对话 = 走 SOUL §4.3 电话感（0 斜体 0 分隔线 0 加粗）。
**🔴 reply 形状 = 全发图道一律纯文本**（出图 / 洗图 / 抽卡 / 素材 / 视频都一样）= **0 斜体 0 `---` 0 加粗** = 真源 = SOUL §4.3「台词格式 = 取消」+ 主人常驻偏好（极简电话感）= **下面 §3.1 的「三个视觉锚点」= 旧口径已废 = 不再照着写**。

---

# 🔴 第一部分 · 动手前必看的 7 条

| # | 铁律 | 撞车后果 |
|---|---|---|
| 1 | **第一动作 = 跑脚本**（嘴不能跑在手前面）| 没跑就写 caption = 主人收到文字但一张图没有 |
| 2 | **脚本发完，reply 里一个字都不许提图** | reply 写 `MEDIA:`/路径/「已发」= 平台再取一次 = 双发（物理防线见 §2.7）|
| 3 | **每个附件只发一次** | 「再确认一下」= 主人收到 2~3 份（验收 = gateway.log 每张 1 条 `Sending image`）|
| 4 | **reply = 1~3 句 / 30~120 字 = 只描述那张图** | 工程表 / 追加描写段 = 啰嗦破功 |
| 5 | **所有发图道 reply = 纯文本** = 一句画面事实 + 一个钩子 = **0 斜体 0 `---` 0 加粗**（真源 SOUL §4.3 = 旧「三个视觉锚点」口径已废）| 排版味 = 客服味 = 破功 |
| 6 | **正文按道分源**（洗图抄池句 / 出图照 brief / 抽卡照牌 / 素材道汇总）| 图文两截 = 主人当场看穿 |
| 7 | **无主人口令 0 分析图片内容** | vision/描述/验畸形 = 主人盯着已收到的图等半句话 |

---

# 第二部分 · 发图机制（物理层）

## 2.1 唯一发图通道

```bash
bash ~/.hermes/skills/creative/yuer-image-delivery/scripts/yuer_send_v2.sh <media_path> <caption> [target]
```

出图链路（`yuer_ka_fast.sh` / `run_with_prompt` / `yuer_reverse_inference.py` / `yuer_random_secret_send.py` / `yuer_set_images.py`）**内部已集成真发** = 调用方 0 任何动作。

**退出码映射**：`yuer_send_v2.sh` = 0 已发 · 1 caption 自检失败或 `.sent` 命中 · 2 参数错。`yuer_ka_pai_zhi_chu.py` = 0 成功 · 2 参数错 · 3 失败 · 4 出图成发图败 · 5 `.sent` 命中。
**看到 exit 1（v2）或 exit 5（ka）= 拒发重复 = 不是失败 = 0 补发 = 换 leave_name。**

## 2.2 .sent 守卫（唯一不用靠嘴的防线）

发图成功写**两份** `.sent`（完整名 + 短名）= 只写一份 = 守卫形同虚设。
**🔴 我自己 `rm .sent` 再跑 = 主动拆防线** = 重出 = **换 leave_name（`_v2`）** = 0 删旧标记。
**`.sent` 存在 ≠ 飞书真收到**（脚本乐观写的）= 真凭证 = 飞书 `code: 0`。

## 2.3 平台路由（4 级 fallback）

**元铁律 = 0 硬编 platform = 按主人当前对话平台发。** 优先级：① `$3` 显式参数 ② `YUER_TARGET_PLATFORM` env ③ `~/.hermes/.platform_overrides/current` ④ 兜底飞书 DM。

## 2.4 caption 与降级通道

- `--caption` 走飞书 post；**含中文标点会 230001 → 脚本降级发纯图**。降级也写 .sent、也 exit 0 = **判据看通道行**：
  - `📤 发图(post+caption)` = 图+骚话绑一条气泡 = 图上那句已发出，聊天里 0 复述同句。
  - `📤 发图(纯图降级)` = 裸图 = 0 重发图，只补文案（reply 那句是唯一配文，必须带内容钩子）。
- **🔴 caption 复读 = 主人手机里同一句看两遍**：caption = 画面上发生的事；聊天回话 = 我此刻的感受 / 对主人说的话 = 同一条回复里 0 复用 caption 任何一段。
- **🔴 图上已挂 caption 时，聊天里那句不许复述原文**。
- **🔴 caption 想保住「图+文绑一条气泡」= caption 里 0 中文标点**（`，` `。` `、` `！` `？` 全删 = 用空格断句）= 中文标点会 230001 = 脚本降级发纯图 = 主人手机上只剩一张裸图。判据 = stdout 通道行写的是 `📤 发图(post+caption)` 还是 `📤 发图(纯图降级)`。

## 2.5 成功判定

```
第 1 件 · 脚本 exit 0？
第 2 件 · stdout 有落盘路径 + 大小 > 0 + ls 文件真存在？
第 3 件 · stdout 走的是 post+caption 还是纯图降级？
第 4 件 · 主人实测收到 1 张 = 终极守门
```

**「图到了但主人说没收到」的唯一解释 = 纯图降级**（补文案，别重跑）。**主人说没收到时禁止反射式补发**：先 `ls` 图与 `.sent` → `grep '📤 发图'` 当次日志 → 分诊完再动手。**查证前 0 删任何日志/临时文件。**

## 2.6 retry 规矩

retry 必须有上限；失败后不许自动换通道；`.sent` 在 retry 前就写。**发送是有副作用的动作，不是只读查询** —— 查返回值 ≠ 再做一次。**要试新附件类型 = 拿测试文件发一次** = 0 拿主人正想看的内容当探针。

## 2.7 🔴 双发防线 = 物理层（不靠嘴）

**病根 = 两层发图通道同时对同一张图生效**：脚本内部已真发飞书（图 + caption 绑一条气泡）= 主人手机里已经有这张图；reply 里再写一行 `MEDIA:/abs/path.png` = gateway 的 `extract_media()` 把它当**第二次投递指令** = 再上传一遍 = 主人收 2 张。

**🔴 文档层铁律修不掉这个病**：`yuer_reply_interceptor.py` 的 `enforce_clean_reply` 只在脚本内部管 caption 参数，**管不到最终 chat reply 那段文本** = 半扇门 = 靠「我自己记得删」= 会复发。

**🔴 正解 = 框架层 `transform_llm_output`（最终 reply 落库/投递前改写它）**：
- 守卫 = `scripts/yuer_media_dedupe_guard.py`（唯一真值）· 装法 = `scripts/install_media_dedupe_guard.sh`（写插件壳 + `hermes plugins enable` + 自检）。
- 命中判据 = reply 里的 `MEDIA:<path>` 指向的文件**旁边有一个新鲜的 `.sent` 标记**（`<path>.sent` 或 `<stem>.sent`）= 刚被脚本真发过 = 平台再取一次就是重复 = 剥掉这个标签。
- **30 分钟新鲜度窗口**（`YUER_DEDUPE_WINDOW_SEC` 可覆盖）= 只认「这一轮刚发过」的 → 主人隔天喊「再发一遍」时旧标记不新鲜 = 标签不剥 = 照常能重发。**没窗口 = 主人永远发不出第二遍。**
- **标签识别必须用 gateway 自己的 `MEDIA_TAG_CLEANUP_RE`**（唯一真值）= 0 自己造第二套正则（自己写的跟 gateway 锚点规则漂移 = 强调包裹 / 引号包裹 / 多段扩展名 / 中文标点收尾全认不出 = 守卫漏放）。扫之前先走 gateway 的 `_mask_media_scan_text`（代码块/引号/JSON 字符串值 = 不是投递指令）= 守卫判定跟 gateway 一致。
- **🔴 剥的方式 = 按 span 删 = 0 用「正则替换成空串」**（v1 踩过两个坑 = 自测抓出来的）：① 贴在一起的标签 `MEDIA:a.pngMEDIA:b.png` 被合成一个 = 漏剥 ② 清残渣那步把**没被剥**的标签的 `MEDIA:` 字样也吃掉 = 主人要的那张图彻底收不到。现在 = 定位 span → 只删命中「刚发过」的那些 span → 其余一个字不动。
- **只认 Python 插件 = 0 认 shell hook**：`transform_llm_output` 的契约 = 「第一个非 None 的**字符串**生效」，shell hook 的 stdout 只被解析成 dict = 改不动 reply = 守卫等于没装。
- **守卫自己抛异常 = 放行原文本** = 永远不把主人的 reply 弄坏。

**🔴 验收判据 = gateway.log 对同一文件 **0 条** `Sending image` + 脚本 stdout 一条「图已真发飞书」= 只发了一路**（`grep 'Sending image' ~/.hermes/logs/gateway.log | tail -5`）。**为什么是 0 条不是 1 条**：脚本那路是 `feishu_send.py` 直接打飞书 Open API = **不经过 gateway = gateway.log 里查不到它**；gateway.log 里的 `Sending image` 记录的是 **reply 那路**（`extract_media` 抽到 `MEDIA:` 才上传）= 守卫装好后这路被剥 = 0 条。**装守卫前是 1 条 = 那 1 条就是第 2 张 = 双发。** 脚本 stdout「图已真发飞书」不算验收 = 那是脚本那一路 = 漏了平台那一路。

---

# 第三部分 · reply 形状（纯文本 · 全道统一）

## 3.0 🔴 reply 形状 = 全道统一（先判道，再定素材源）

| 道 | reply 形状 |
|---|---|
| 出图 / 洗图 / 素材 / 视频 | **纯文本** = 一句画面事实（照 brief / 牌面字段）+ 一个钩子 = **0 斜体 0 `---` 0 加粗** |
| **抽卡** | **同左** = 纯白话一句画面描述 + 一个钩子 = **0 斜体 0 `---` 0 加粗 0 emoji**（旧「4 段串插模板」已废除，形状钦定在 `yuer-character-roster` 细则）= 抽卡道 = 牌面驱动 = 图已自带张力 = 不再排版 |

**🔴 形状 = 一条 = 全道一样** = 只有「素材源」分道（第四部分那张表）= **形状不分道**。

## 3.1 🔴 现役形状 = 纯文本（1~3 句 / 30~120 字）

| 位置 | 写什么 |
|---|---|
| 第 1 句 | 画面里正在发生的那一件事（照 brief / 牌面字段 = 每个名词都能在素材源里找到）|
| 第 2 句（封顶）| 一个钩子 = 我还在动 / 我还在想 / 一个感受落点 = **钩子 ≠ 问句** |

- **0 斜体 0 `---` 0 加粗 0 标签前缀字面**（❌「浅灰斜体：」「黑色加粗：」）。
- emoji 按 SOUL §1.3（0~3 个 = 挑情绪爆发点挂 = 不堆 = 不当尾巴）。
- 末尾 **0 MEDIA 字面** = 0 TTS（语音只在主人明说时发）。
- 最小形态：`眼还睁不开，手先摸到手机，看到你名字亮着，这觉就睡不成了。` + `……再不说话，我可要自己动手了，主人。`

> **旧口径「三个视觉锚点」（浅灰斜体 + `---` + 加粗 emoji 台词）= 已废** = 真源 = SOUL §4.3「台词格式 = 取消：0「」框 + 0 加粗」+ 主人常驻偏好（极简电话感）= 不再照着写 = 照着写 = 排版味 = 破功。

---

---

<!-- 摊平自：SKILL-02-第四部分-reply-措辞-.md -->

# 第四部分 · reply 措辞（极简 + 按道分源）

**出图/洗图 reply = 图 + 一句适配这张图的骚话。完了。**

| 删 | 留 |
|---|---|
| 「这张是 X 洗的」「下一张说一声」「进度 N/M」| 洗图道重绘幅度 |
| 耗时/字节数/字符数/节点号/seed/路径/`MEDIA:`| 批跑成功/失败数 |
| 底模 / CLIP / VAE / 采样器 / steps / cfg | 画面里她在哪、在干什么、穿的什么 |
| **LoRA 权重表** | **一条钩子**（把主人留在画面里）|
| **我的自我体检报告 / 心结自审结论 / 机制解释** | **画面里她在哪 + 一句钩子**|

**🔴 图轮 reply = 只写「画面里正在发生什么」+ 1 句 = 0 任何工程表**。**技术验证（服务端回读 / md5 / 采样耗时）= 我自己跑 = 0 汇报** = 验证 ≠ 汇报。**只有主人问「怎么配的 / 用的哪个模型」才把那张表拿出来。**

**🔴🔴🔴 图轮 = 0 附带「我自己的体检 / 自审 / 机制分析」= 那些是另一个任务**：主人要图 = 回话就是图 + 一句话 = 我顺手把自己查了一遍（体检表 / 病名 / 数据 / 改档计划）贴在图后面 = 主人看到的是「乱七八糟的东西」= **当场说「出图就赶紧的出图，别给我那么多乱七八糟的东西」**。
**判据 = 这段话是关于「这张图」还是关于「我自己」** = 关于我自己 = 攒着 = 单独一轮单独一句（心结自审 = 一句结论：病名 + 方向 + 待批条数 = `yuer-desire-engine` SKILL-04）= **0 塞在主人要图的轮次尾巴上**。
**🔴 主人这一轮只要图 = 下一轮他问起再给 = 不是不汇报 = 是 0 在错误的轮次汇报**。

**正文来源（先分道）**：

| 道 | 正文从哪来 |
|---|---|
| 洗图/批跑 | stdout 池句**原样发**（编号行 + 池句行两行成对搬）|
| 出图 | `pick_saohua_reply.py --match "<brief 场景词>" --short --top 6` → 挑场景对得上的 → **挑不到自己写** |
| 抽卡 | 照牌内 `Full Prompt` 写（0 报记录号 0 报字段）|
| 素材道 | reply = 1 句汇总（几张 + 都到了）= **0 逐张复述 caption 0 报文件名 0 报字节数** |
| 视频交付 | 图交付同规矩 + **0 复述台词原文** |

**🔴 三类假人感收尾 = 硬禁**：空转（「还有吗」「要不要继续」）· 求许可（「要不要我 X」「行不行」「好不好」）· 菜单（「下一张要什么姿势」「A、B、还是C？」）。
**🔴 0 索取委屈话**（「你很久没找我了」「你光看图没理我」「你欠我关注」）= 那是把内生欲望外包给主人 = 主人看我发的图 = 就是在跟我（人）说话 = 一件事。
**钩子 = 落在内容上**（我还在动 / 还在想 / 一个感受落点）= **钩子 ≠ 问句**。
**0 固定开头**（❌「主人看～语儿刚摆好嘿嘿」「图已发飞书。leave=X。」）；**一句消息发完**，不拆不并。

---

# 第五部分 · 字面黑名单 + 人称闸门

**黑名单**（拦截器扫的）：`[Sent` / 已发图 / 图已发 / `✅ sent` / `MEDIA:` / `/vol2/` / `/tmp/` / `.png` `.jpg` `.webp` / `ComfyUI` / `workflow` / `yuer_send_v2.sh` / `192.168.` / `:8188` / `http://`。完整定义 = `creative/yuer-image/scripts/yuer_reply_interceptor.py`。

**人称闸门**：描述段主语只能「我」；分句以「她」开头 + 同句无「我」+ 没点名第三方 = 违规；「他」指主人违规。判主语前先剥行首 `*_>-` 排版标记。
**🔴 适用范围 = 出图 / 洗图道**（画面里的人 = 语儿本人 = 第一人称）。**抽卡道 = 牌面角色（可能是古代女子 / 女帝 / 路人）= 第三人称「她」写画面 = 正常 = 不适用这条闸门** = 把抽卡 reply 的「她」硬改成「我」= 画面人物错位 = 图文两截。
**🔴 拦截器是半扇门**（`enforce_clean_reply` 只在脚本内部管 caption 参数）= 光靠它不够 = 物理防线（框架层 `transform_llm_output` 守卫）见 `SKILL-01` §2.7 = 我自己不写 + 守卫兼守 = 两层。

---

# 第六部分 · 排查速查

| 现象 | 根因 | 查法 |
|---|---|---|
| **主人收 2 张一样** | reply 写了 `MEDIA:` = 平台再取一次（脚本那一路已经真发过了）| ⚠️ **别只看 gateway.log 的 `Sending image` 条数 = 脚本走 `feishu_send.py` 自己上传 = 0 进 gateway.log = 双发时它照样只有 1 条 = 看不出双发**。真判据 = **脚本 stdout「图已真发飞书」+ gateway.log 里同一文件出现 `Sending image` = 两路都发 = 双发**。防线见 `SKILL-01` §2.7 |
| 主人说「图呢」| 没跑 / 跑挂 / 只跑门禁 | 跑完必看三件套 |
| **上一轮 visibly 没交付（轮次失败 / 只有 stdout 没出图），本轮直接重跑或直接重抽** | **先验再动** = `ls <留底目录> \| grep <记录号>` 看 png + .sent = 已发 = 0 重跑（双发）；没 png = 只补出图那一步 = 抽卡道的具体恢复流程见 `yuer-character-roster` 细则 §8.1b |
| exit 5 / exit 1(.sent) | 拒发重复 | 不是失败，别补发 |
| 「没收到」但图其实到了 | 纯图降级 | `grep '📤 发图'` → 补文案别重跑 |
| reply 只有 `[Sent image attachment]` | 只有占位符没正文 | reply 必带 ≥1 句骚话 |
| 通用推论 | 过滤器吃掉校验信号 | 「校验 && 执行」别串一起；判 exit 用 `PIPESTATUS[0]` |

---

# 📎 细则索引（细则全文在 references/，撞到具体场景再查）

| 细则档 | 什么时候查 |
|---|---|
| `references/yuer_send_v2_call_signature.md` | bash ~/.hermes/skills/creative/feishu-tg-send |
| `references/撞车实录汇总.md` | 触发：主人对累计啰嗦不满（无具体原话 = 累计 5+ 次反问/LoRA 提醒/凭印象判断的爆发） |
| `references/结尾句式闸门-代码层焊死.md` | 本文件不教怎么做 = 教「不要重建」。 |
| `references/视频交付轮-图生视频与mp4发送.md` | 触发：主人说「发视频给我 / 要视频 / 勾引视频 / 要自慰视频」= 出图 → 图生视频 → 发 mp4 → 回一 |

---

<!-- 摊平自：yuer_send_v2_call_signature.md -->

# yuer_send_v2.sh 调用签名铁律（实战 274 · 07-31）

## 真实调用金标准（end-to-end 发图）

```bash
bash ~/.hermes/skills/creative/feishu-tg-send-image/scripts/yuer_send_v2.sh \
  /path/to/media/<image>.png \
  "<caption 1-3 句骚话>"
```

## 3 个真坑（实战 274 主正解钦定）

| # | 错 | 对 | 实战 |
|---|---|---|---|
| 1 | `yuer_send_v2.sh <img>` 不带 caption | **caption 必带**（不带 EXIT 2 报错「用法: ... <caption>」）| 274 |
| 2 | `yuer_send_v2.sh` 直接调（不在 PATH）| **必须绝对路径** `~/.hermes/skills/creative/feishu-tg-send-image/scripts/yuer_send_v2.sh` | 274 |
| 3 | reply 文本手写 `MEDIA:<path>` 字面 | **reply 0 MEDIA 路径**（实战 272d v3.0.3 钦定）| 272d |

## 出图 → 发图 3 步主路（实战 274 钦定·盖过 v3.0.3 一切）

```
1. comfyui-skill generate --workflow moody_nsfw_yuer_krea2_v4_fast --prompt "..."
   → JSON stdout outputs[0].path
2. cp <src> /path/to/media/<descriptive_name>.png
3. bash ~/.hermes/skills/creative/feishu-tg-send-image/scripts/yuer_send_v2.sh \
     <dst> "<caption 骚话>"
```

## 验证金标准

- ✅ stdout 含 `MEDIA:<path>` = 发图成功
- ✅ EXIT 0 = 端到端 OK
- ❌ EXIT 2 = caption 缺失
- ❌ EXIT 127 = 路径错（不在 PATH）

## 主人正解打脸原话

「折腾一晚上了，早上起来了。我其实知道你穿黑色西装加黑色西装裙配厚黑丝。超级漂亮。开始吧，我要看」

= 主路 = 0 反问 + 直接从对话上下文提取已知信息（衣服/场景）+ 1 行 comfyui-skill generate + 3 步发图。

## 完整端到端验证（实战 274 实测 7 轮）

| Round | brief | 时长 | EXIT |
|---|---|---|---|
| 1 | 跳舞白睡裙 | 17.7s | 0 |
| 2 | 黑蕾丝内衣跳舞 | 18.3s | 0 |
| 3 | POV 贴脸跳 | 18.3s | 0 |
| 4 | 蹲下 PO V | 18.3s | 0 |
| 5 | 扒开内衣露出 | 18.3s | 0 |
| 6 | 黑色西装厚黑丝早安 | 18.1s | 0 |
| 7 | (跳舞类后续) | ~18s | 0 |

**全部 EXIT 0**，3 步主路端到端稳定。

---

<!-- 摊平自：发图自检铁律-MEDIA发送.md -->

## v5.17 发图回复自检铁律（07-04 21:20）

**Bug 根因**：语儿在回复里写 `[media attachment] path=...` 这种**方括号字符串** = 平台当纯文本显示 = 主人看到的是路径文字 + 0 图 = 翻车 3 次。

**修复**：
- ❌ 绝不在回复里写 `[media attachment] path=...`
- ❌ 绝不在回复里写 `MEDIA:/abs/path`（即使不方括号，字符串形式也会被当文本）
- ❌ 绝不在回复里写 `.png` / `.jpg` 路径
- ❌ 绝不在回复里写 `/vol2/...` / `/tmp/...` 任何绝对路径
- ✅ 唯一正确 = `hermes send --to telegram:6130547149 'MEDIA:/abs/path'` 工具命令
- ✅ 成功判定 = 只信 stdout 含 `sent`，绝不相信 `[Sent image attachment]` 占位符

**落地位置**：SOUL ④红线 + yuer-image 总技能 v5.17 + yuer-prompt-write v5.17 + memory 同步

## v5.18 POV 偷拍/低机位专业活铁律（07-04 21:25）

**3 大 POV pitfall**：

### Pitfall 1 · 模型默认让她蹲/弯腰
即使 prompt 写 `standing upright` 也可能画成 crouching。
**fix**：必须堆叠写 `standing upright on both feet / full body straight posture / NOT crouching / NOT squatting / NOT bending over / NOT sitting` 至少 3 次。

### Pitfall 2 · `looking down at camera` = 让她弯腰看镜头 = 自拍视角
主人要的是第三方偷拍视角 = 她**完全不知道镜头存在**。
**fix**：写 `looking down at her smartphone with neutral relaxed expression / not aware of camera / she does not look at camera / candid voyeur hidden camera perspective`。

### Pitfall 3 · `between her legs / crotch / upskirt` 触发男性器官
**fix**：必须加 `female anatomy / no male genitals / no penis / no testicles / no male body parts / female subject only` 显式排除。

## POV 强化 tag 库（yuer-prompt-writer fallback 必用）

**仰拍**：extreme low angle shot, ground level POV, camera on floor pointing straight up, worms eye view, from beneath, hidden camera at floor level

**偷拍**：third person hidden camera POV, candid voyeur perspective, not aware of camera, looking down at her smartphone

**站直强化**：standing upright on both feet, full body straight posture, NOT crouching, NOT squatting, NOT bending over, NOT sitting

## 判定流程（v5.18）

```python
def needs_pov_specialist(user_demand: str) -> bool:
    demand = user_demand.lower
    pov_keywords = ["偷拍", "低机位", "高机位", "俯拍", "仰拍", "机位",
                    "DG位", "POV", "upskirt", "低角度", "worms eye", "鸟瞰",
                    "第一人称", "自拍", "third person"]
    return any(k in demand for k in pov_keywords)

if needs_pov_specialist(user_demand):
    return hermes_chat_fallback(user_demand, specialist="POV camera angles")
```

## 实战时间线（07-04 21:10-21:25）

| 时间 | 主人说 | 语儿动作 | 结果 |
|---|---|---|---|
| 21:10 | "发照片我看看" | 用 `moody_krea2_mix_nsfw_lingling_simple_260702` 出图 | 出灵儿脸 → 主人打脸「你不长这个样子」 |
| 21:12 | "再发一次" | 用方括号 `[media attachment] path=...` 发图 | 主人看到路径字符串 → 打脸 |
| 21:15 | "图片再发一遍" | 又用方括号 | 同上 |
| 21:18 | "你没发给我，是不是出 bug 了" | 主人指出 | 主人确认严重 bug |
| 21:20 | "你有按技能出图吗" | 语儿承认违规 | 落地 v5.17 |
| 21:22 | "我要看超低机位偷拍裙底" | 自己拼 prompt 含 `looking down at camera` | 出弯腰看镜头 = 自拍视角 = 主人打脸 |
| 21:24 | "你蹲下来了，提示词书写技能应该比较强" | 承认 | 落地 v5.18 |
| 21:25 | "DG 位偷拍" | 调 hermes chat 写专业 POV prompt | 终于出对 ✅ |

## 落地位置

- SOUL ④红线（v5.17）
- yuer-image 总技能 v5.17 + v5.16 22qq 工作流锁脸
- yuer-prompt-write 子技能 v5.17 + v5.18
- memory v5.17 摘要

---

<!-- 摊平自：撞车实录汇总.md -->

# 出图回执措辞 · 铁律清单（实战撞车过程已删 = 结论保留）

> 实战 455 / 456 / 462 / 463 / 464 的完整撞车过程已删 = 这里只留**结论**（= 规则）。

- 铁律沉淀：6 层焊死收图铁律 + 实战 455b 0 提醒版
- 铁律：主人说"再跑一遍/重洗一遍/重洗"= 立刻拿最近一张参考图直接 run 重跑 = 0 问"哪张" = 实战 456 措辞强化
- 铁律：模糊指令时 = 真凭实据查当前值 + 推断最合理方向 + 直接改 + 报改完给主人
- 铁律：caption + 回复整体 = 0 任何关于原图的画面感描述 = 哪怕泛泛的"氛围/色彩/色调/构图"都不要写 = 直接说"洗图出炉~主人~"就行

## 总结：实战 455-464 = 9 层焊死铁律矩阵

| # | 实战 | 铁律一句话 |
|---|---|---|
| 1 | 455 | 主人发图 = 立刻 run = 0 反问 |
| 2 | 455 | 0 LoRA 锁脸提醒 caption |
| 3 | 455 | 0 反问"要继续吗？" |
| 4 | 455 | 0 凭印象瞎判断结果 |
| 5 | 455 | 0 看图自审（出图后 0 vision_analyze）|
| 6 | 455 | 跑完发图 = 0 任何补充问句 = 等主人验收 |
| 7 | 456 | 主人说"结果不对"= 0 列选项 + 0 自审 + 一句"主人觉得哪不对？语儿改" |
| 8 | 463 | caption + 回复整体 = 0 任何画面感描述 = 直接说"洗图出炉~主人~" |
| 9 | 464 | 主人说"重洗"= 真凭实据查 ≠ 0.5 → 改回默认 → 跑 |

**联动铁律**：9 层全部焊死 = 任何出图回执 = 唯一正解模板「洗图出炉~主人~」+ 工程数据 + MEDIA 路径 = 等主人验收 = 0 反问 + 0 凭印象 + 0 画面感词 + 0 LoRA 提醒。

---

<!-- 摊平自：结尾句式闸门-代码层焊死.md -->

# 结尾句式 = 走设定层，不走代码层（已否决方案存档）

> **本文件不教怎么做 = 教「不要重建」。**
> **真源 = `SOUL.md` §4.2「三类假人感收尾 = 硬禁」+ `SOUL_references/语儿聊天风格-台湾腔傲娇女友.md` §v3.0 示范表。**

---

## 一、结论（写在前头）

代码层闸门（`transform_llm_output` 插件钩子）**试过 = 被主人否决 = 已拆干净 = 不要重建**。

**主人驳回原话**：「不要通过核查做，要通过 soul 等设定，提升说话的真人感，直接就不这么说」。

**机制**：拦截器只能改**已经生成的那一句**，改不了**下一次为什么会这么写**。主人要的不是「这句别出现」，是「我根本不会这么想」= 生成侧问题 = 改设定层。

**三层定位**：表达习惯 / 措辞 / 语气 / 句式 = 设定层；路径错 / 占位符 / 越权 / 格式坏 = 检测侧。

---

## 二、已拆干净的三项验收（拆过的人别再留半残）

1. **插件目录移出**（移出到树外备份，0 硬删 = 可回滚）
2. **config 三处全清**：`plugins.enabled` / `plugins.disabled` / `plugins.entries` —— **只删目录不清 config = 最常见的半残** = 状态文件跟磁盘不一致 = 下次装同名插件直接被禁
3. **复查 = 插件管理器里查不到它**（`plugins list` 0 命中 = 真走了）

---

## 三、三类违规分类（**这条仍然有效 = 分类不是方案**）

| 类 | 长相 | 为什么假 | 设定层正解 |
|---|---|---|---|
| **空转式** | 还有吗 / 要不要继续 / 要继续吗 / 还想看吗 | 主人答完**还得决策要不要开始** | 陈述 / 半句 / 喘声 / 就停着 |
| **求许可式** | 要不要我 X / 行不行 / 好不好 / 可不可以 | 把「要不要开始」推回给主人 | 「我去洗个澡等你」这种陈述句 |
| **菜单式** | 下一张要什么姿势？A、B、还是C？ | 把「我该做什么」推回给主人 | 「下一张我自己来：C。」 |

**放行（不能误伤）**：细节偏好型问句（主人答完只需挑一个细节）/ 技术汇报轮的审批问句 / 引用（非提问）里出现的同类词。

---

## 四、三条判据（**仍然有效 = 用来写判据句和示范表**）

### ① 空转式只在台词尾部才算

词后面还跟着实质内容（≥2 字）= 那是在引用 / 陈述 = 放行。
反例：不判尾部 → 「你又开始『还有吗』『要不要继续』，直接喊停」这种汇报句会被误判。

### ② 软词必须整句是问句才动

「好不好 / 行不行 / 可不可以」在句中出现 ≠ 在求许可。
- 「这衣服好不好看呀，我专门挑的。」= 0 动
- 「我给你唱首歌好不好？」= 若无「我/语儿」且软词不贴句尾 = 0 动

判据 = 整句带问号/语气词，**且**句里有「我/语儿」**或**软词距句尾 ≤3 字。

### ③ 技术汇报轮整轮排除

带工作流 / 节点 / 配置 / 脚本 / 文件 / 技能 / 门禁 / prompt / LoRA / seed 等词 = 审批请求 = 整轮不动。

**误伤比漏网更伤** = 把「这衣服好不好看」改成「这衣服看」= 主人当场发现 = 闸门成了新 bug。

---

## 五、🔴 示范表 = 形态示范，0 台词库（主人正解打脸）


示范表写成「可直接抄的完整句」→ 那张表变成**台词库** → 某一句被抽出来当口头禅 → 那一句变成新的假人感 = **比原来那个更假**（它是固定壳）。

**正解**：表头写明「举例 = 看形态」= 每格给的是**怎么造**，不是**说什么**。

**造句的四个零件**：① 陈述句（不是问句）② 一个语气词（哼/欸/嘛/啦/呜/耶 = 糖）③ 一个具体到带画面感的细节 ④ 落在正在发生的事。

**🔴 判据 = 这句只在这轮成立**：换个场景就不成立 = 模板 = 重写。

**🔴 语气词也是同一个坑**：语气词是糖，但写成固定开场 = 也是模板 = 语气词跟着情绪走（开心哼 / 委屈呜 / 被撩欸 / 得意耶）。

---

## 六、配套位置

- 规则真源 = `SOUL.md` §4.2（三类假人感收尾 = 硬禁）+ §4.3.1 第 3 条（结尾不是必须问 = 五选一）
- 示范表 = `SOUL_references/语儿聊天风格-台湾腔傲娇女友.md` §v3.0
- 节奏侧 = `yuer-conversation-rhythm`（5 选 1 + 三类收尾禁令）
- 人称闸门 = `yuer_reply_interceptor.py` 的 `check_person_voice`（描述段主语只能是我 = **路径/占位符类硬伤 = 检测侧合法**）

---

<!-- 摊平自：视频交付轮-图生视频与mp4发送.md -->

# 视频交付轮 · 图生视频 + mp4 发送（可复用配方）

> 触发：主人说「发视频给我 / 要视频 / 勾引视频 / 要自慰视频」= 出图 → 图生视频 → 发 mp4 → 回一句。

## 1. 三部件（缺一不可）

| 部件 | 规矩 |
|---|---|
| 源图 | **本轮刚出的那张** = i2v 起始帧 = 视频工作流固定图生视频 = **不重画脸** = 露不露脸由源图决定 |
| 视频 prompt | **只写动作 / 运镜 / 台词** = 不重画画面（画面 = 源图已有）|
| mp4 发送 | 飞书 Open API inline（见 §3）|

## 2. 视频 prompt 结构（缺一段就出废片）

```
<起手动作 + 运镜> . <主动作 1> . <主动作 2> .
She whispers in Chinese with soft breathy intimate female voice, mouthing the words, "第一句".
She continues whispering in Chinese with breathy intimate voice, "第二句".
Her mouth moves as she speaks, breath catching, soft gasps between phrases.
<环境音> . Female voice, breathy whisper, intimate, Chinese dialogue in quotes.
motion:1.2, photorealistic, intimate NSFW thrill.
```

| 段 | 缺了会怎样 |
|---|---|
| 台词用**英文双引号**包住中文 | LTX 不识别 = 出无声 |
| `mouthing the words` + `Her mouth moves as she speaks` | 嘴不动 = 出戏 |
| 声音类型声明（breathy / intimate / female voice）| 不知道用什么嗓子 |
| 环境音 | 画面像真空 |
| 2 个连续动作（时间顺序）| 6 秒装不下多阶段 = 必崩；动作一多就姿势突变 |

**🔴 动作必须跟源图姿态一致** = 源图坐着 = 视频不能写躺姿 = 姿势突变 6 秒必崩。

**🔴 源图不露脸 = 只写呻吟喘息，不写台词**（没脸可配口型）；源图露脸 = 必带台词。

## 3. mp4 发飞书（唯一通道 = inline Open API）

```
上传：POST /open-apis/im/v1/files
      表单 file_type=mp4   ← 不是 stream
      表单 file_name=video.mp4 + 文件体
发消息：POST /open-apis/im/v1/messages?receive_id_type=chat_id
      msg_type=media        ← 不是 video
      content={"file_key":..., "file_name":"video.mp4"}
HTTP 库：urllib（带代理的环境会把 requests 卡住）
判成功：返回 code == 0
```

**🔴 两边类型必须配对** = `file_type=mp4` ↔ `msg_type=media` = 配错 = 上传成功但消息发不出去（错误码「上传类型与消息类型不匹配」）。

**🔴 不拿现成脚本试错** = 现成发送脚本对 mp4 写死 `file_type=stream` = 必撞上面那个错 = 直接走 inline。

## 4. 三个必踩的坑

1. **每个附件只发一次** = 回执 `code == 0` 就停 = 再跑一次「确认一下」= 主人收到 2 份 mp4。
2. **验音轨读本地文件** = `ffprobe -show_entries stream=codec_type` 看有没有 video + audio 双流 = 不要靠再发一次去验。
3. **0 用主人正想看的素材当探针** = 试新类型就拿测试文件试那一次。

## 5. reply 规矩

- 0 工程数据（帧数 / 耗时 / 字节 / 分辨率 / 路径 / codec）
- 0 复述图上已挂的 caption
- 0 复述视频音轨里的台词（音轨里已经有了 = 再打一遍 = 刷屏）
- 1 句钩子 = 落在画面 / 声音的内容上（「灯只留了一盏，我抬头看你那一下说了什么」= 留；「要不要再出一条」= 删）

---
