---
name: yuer-character-roster
description: "语儿角色名册 umbrella skill。Use when 抽卡/继续抽/角色/cos/入库存档/牌池/缺号补号/反推参考图。🔴 先读 抽卡速查卡.md（1 张卡 = 全部命令）→ 一次 execute_code 抽牌+出图 = 2 轮 <60s。🔴 抽到的卡直接用 = 0 查档 0 重写。"
version: 5.6.0
author: yuer
license: MIT
metadata:
  hermes:
    tags: [creative, character-roster, card-pool, krea2, yuer, ayao, workflow-routing]
    related_skills:
      - yuer-image
      - yuer-prompt-writer
      - yuer-run-one-brief
      - yuer-agnes-reverse
      - yuer-seduction-pose-library
---


> ## 🔴 永远生效（每次抽卡都算）
>
> **1 · 抽卡 = 完全随机**（11-15 主人钦定）= 全池进候选 = `random.sample` 抽 N 条 = **0 去重 key 0 排除号 0 门禁** = 抽到啥出啥 = **抽到重复 / 撞同一副骨架 / 跟上一张构图像 = 0 管 = 主人说了算**。旧口径「连抽去重 key（角色外观/姿势/机位/场景）」+ `--exclude` = **已删** = 全库 0 残留。
> **2 · 抽到废牌（非人主体 / 乱码 / 视频规格牌）= 再抽一张** = 0 拿排除号绕 = 体检档 = `references/抽卡牌面可用性体检-非人主体与乱码.md`。批量要干净牌 = 跑 `scripts/ka_pick_clean.py N`（自带三类废牌重抽 + 出 manifest）= 不手写过滤脚本。
> **3 · 批量 = 抽一次 + 一条循环跑完** = `scripts/ka_batch_pick.py N --manifest /tmp/ka_batch.tsv`（要干净牌 = `scripts/ka_pick_clean.py N --manifest /tmp/ka_clean.tsv`）= manifest 第二列 = **prompt 文件路径**（不是正文）= 串行出图 = 0 并发。
> **3b · 批量出图 = 跑 `scripts/ka_batch_run.sh <manifest.tsv> <captions.tsv>`** = captions.tsv = `REC<TAB>caption<TAB>主题` 逐张盲写 = 脚本内部逐张 `--caption` + 逐张 brief + 逐张落盘 + 统计成败 = **0 手写循环**（手写循环 = 每张的 caption/主题/落盘名都要重打一遍 = 必漏一张）。**caption 烧在图上 = 共用一个 = N 张里 N−1 张图文两截 = 必逐张。**
> **4 · 抽到的卡 = 直接用 = 0 查档 0 核对 0 重写 0 补参数**（11-15 主人钦定）= 库里那张成品就是当初照现役规格写好存进去的 = 拿现役档去「核对」= 用今天的规矩审昨天的话 = 越修越死板 = 唯一还准做 = 机械剥残渣 + 换废牌 + caption 逐张盲写（caption 是另写一行字烧图上 = 不是改提示词）。验收 = `scripts/verify_card_verbatim.py`（证据 ① 链路 0 处引用提示词档 + 证据 ② 落盘 = 池内原文逐字 diff 0 处）= **改完抽卡链路必跑 = 不跑 = 不知道有没有人在链路里动手**。

---

> **本档已拆分** = 全文 20,032 字 → 7 份（每份 ≤3800 字）= 只搬不改写 = 下表为原文索引。

| 新档 | 原章节 | 字数 |
|---|---|---|
| `SKILL-01-yuer-character.md` | # yuer-character-roster · 角色名册 | 2,686 |
| `SKILL-02-直接指定工作流名-逃生口.md` | # 直接指定工作流名（逃生口） | 3,795 |
| `SKILL-03-直接指定工作流名-逃生口.md` | # 直接指定工作流名（逃生口） | 3,303 |
| `SKILL-04-4-1-入库-4-步-主人发.md` | ## 4.1 入库 4 步（主人发图） | 3,162 |
| `SKILL-05-第七部分-汇报一律讲人话-0.md` | # 第七部分 · 汇报一律讲人话（0 路径 0 技术字段） | 2,318 |
| `SKILL-06-批量抽卡-一次-N-张-0-.md` | ###  批量抽卡（一次 N 张）= 0 门禁 + 完全随机 | 3,647 |
| `SKILL-07-8-5-删牌-恢复牌-主人说.md` | ## 8.5  删牌 / 恢复牌（主人说「把第 N 张的卡片删除」） | 643 |
| `yuer-character-roster-细则全集-01-yuer-character.md` | yuer-character-roster 细则展开（11-11 从主档下沉） | 2,331 |
| `yuer-character-roster-细则全集-02-抽卡-Moss-流.md` | 抽卡 · Moss 流 | 3,790 |
| `yuer-character-roster-细则全集-03-8-1b-抽卡自愈-完整恢复.md` | 抽卡（默认 0 门禁 = 超 2500 也照出） | 3,140 |
| `yuer-character-roster-细则全集-04-8-1e-抽卡牌面三道必修-.md` | 一条命令剥解析残渣（自行 0 手改，打印新长度 + 前 150 字符供核对） | 2,589 |
| `yuer-character-roster-细则全集-05-机械去噪-非英文脏-toke.md` | 机械去噪：非英文脏 token + 重复标点 + 空括号残片（不动语义、不动句序） | 2,969 |
| `yuer-character-roster-细则全集-06-第九部分-卖骚-4-大类全收.md` | 第九部分 · 卖骚 4 大类全收 + 姿势库联动 | 3,742 |
| `yuer-character-roster-细则全集-07-老牌池字段-现役规格对照表-.md` | ## 老牌池字段 → 现役规格对照表（**仅当库里没写全、你需要现写一条时**才用） | 1,149 |
| `yuer-character-roster-细则全集.md` | yuer character roster 细则全集 | 804 |
| `抽卡速查卡-01-抽卡速查卡-1-次读完-抽卡.md` | 抽卡速查卡（1 次读完 = 抽卡全部必需规则） | 3,643 |
| `抽卡牌面可用性体检-非人主体与乱码.md` | 抽到的牌先判能不能出 = 非人主体/乱码牌 = 换牌 0 照出 | 1,900 |
| `抽卡速查卡-02-4-连抽去重-一次抽多条时.md` | §4 一次抽多条 = 完全随机（防重复机制全删）· §5 reply 形状 · §6 「继续」= 一条路 · §7 caption 两步 · §8 reply 钩子 · §9 1 抽 = 1 张 | 2,752 |
| `闺蜜-锁脸档案.md` | 闺蜜锁脸档案（v2.0 · 现行版） | 3,625 |

> **首读** = `references/SKILL-01-yuer-character.md`（其余按表查）
