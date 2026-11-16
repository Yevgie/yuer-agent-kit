# yuer-character-roster 细则展开（11-11 从主档下沉）

> **唯一职责** = 装主档里超长的细则段落。
> **主档 = `../SKILL.md`** = 判据句 + 索引。
> **本档 = 细则全文** = 撞到具体条款再查。

---


## 8.1 抽卡 = 3 条命令（唯一入口）
> **🔴 触发词覆盖 = 主人任何「想看 / 想要 / 再给一张 / 换个 / 来张 / 抽卡 / 继续抽 / 继续抽卡」出图诉求 = 全走本 3 条命令**（10-07 主人钦定·盖过 yuer-image 路由一切）。「看看你」这类才走 yuer-image 5 步画当前场景；「想看 X」= 抽卡随机池出新壳 = 不写新 brief = 不 skill_view yuer-image/prompt-writer。
> **🔴 主人要「一次 N 张」= 不走这 3 条 = 走 §8.1f 的批量脚本**（`scripts/ka_batch_pick.py` = **0 门禁全池抽 + 完全随机** = 11-10 钦定「抽卡不设置门禁」+ 11-15 钦定「防重复机制全删」）。

| # | 命令 | 干什么 |
|---|---|---|
| **1+2** | `/usr/bin/python3 ~/.hermes/skills/creative/yuer-character-roster/scripts/pick_ka_prompt.py` | **一步完成抽档案 + 落盘成品提示词**（抽 1 条 = 370 条合格牌池自动避号，**只调一次** → 原样写 `/tmp/ka_<记录号>_prompt.txt` → 机械去噪脏 token / 双逗号 / 空括号 = **0 手打 0 两趟**）。stdout 打 `REC=` `CHARS=` `PROMPT=` + 牌面字段行 + `WARN` 残渣告警。**库里这格没写全时才走 8.2 速查卡现写** |

**🔴 一次运行 = prompt 文件 + brief 必须同源**：把 stdout **一次落盘**再从同一文件切两样（`REC`/`PROMPT` 行取 prompt 路径，`[...]` 字段行取 brief）= 同源。**分开跑两次 = 第二次重新洗牌 = brief 属于 A 牌、prompt 属于 B 牌 = 图文两截 = 主人拿到一张不是他抽到的那张**。**判据 = prompt 文件的记录号 == brief 里的记录号 == stdout 的 REC = 三个必须一致**。

```bash
OUT=/tmp/ka_pick_$$.txt
/usr/bin/python3 ~/.hermes/skills/creative/yuer-character-roster/scripts/pick_ka_prompt.py > "$OUT" 2>/dev/null
REC=$(grep -m1 '^REC=' "$OUT" | cut -d= -f2)
PROMPT=$(grep -m1 '^PROMPT=' "$OUT" | cut -d= -f2)
grep -E '^\[' "$OUT" > "/path/to/media/yuer_ka${REC}_<主题>_<日期>.brief.txt"
```

**🔴 0 在 prompt 文件生成后再去跑一次 pick 去「看看到底抽到哪张」= 白换牌 = 白烧一轮**（这条与 8.1 坑表「一次抽卡调多次 = 抽到另一张」是同一个坑的两面：那次是看 stdout，这次是重跑）。
| **3** | `bash ~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh /tmp/ka_<记录号>_prompt.txt yuer_ka<记录号>_<主题>_<日期> --report-only` | **体检 + 出图 + 发飞书 + 抽骚话 四合一** = 12~14 秒 |

**🔴🔴 命令 3 的 `--model` = 主人点名哪条道就传哪个（抽卡道也有模型分流）**

| 主人说 | 命令 3 加什么 | 走哪条道 |
|---|---|---|
| 「抽卡」/「抽卡 krea2 流」/「抽卡 krea2」| 不传 `--model` = **默认档 = 以 wrapper stdout 那行 `🎯 工作流 = <id>` 为准**（现役解析到哪条就哪条）= **0 凭本表旧文字假设 = 0 grep 源码去确认** | 两条线**都绑语儿脸锁** = 出图结果不受影响 |
| **「抽卡 moss 流」/「moss 抽卡」/「抽卡走 moss」** | `--model moss` | `yuer_moodyMoss_fast`（文字一级棒·写实·中文友好）|
| 「抽卡 2D / 动漫抽卡」| `--model anima` | `anima_nsfw` |

```bash
# 抽卡 · 默认档（不传 --model = 现役工作流以 wrapper stdout 那行 `🎯 工作流 = <id>` 为准）
bash ~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh /tmp/ka_13985_prompt.txt yuer_ka13985_20261110 --report-only

