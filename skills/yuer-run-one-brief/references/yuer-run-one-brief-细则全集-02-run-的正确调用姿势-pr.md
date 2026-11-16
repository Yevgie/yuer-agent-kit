### 🔴 `run` 的正确调用姿势 = prompt 当第一个位置参数传

```python
import sys; sys.path.insert(0, '~/.hermes/skills/creative/yuer-image/scripts')
from yuer_run_one_brief import run
run(PROMPT, "yuer_<主题>", "feishu", "")     # (brief, leave_name, channel, caption)
```

⚠️ **`run` 没有 `--prompt-file` 参数** —— 传文件路径 = 那个路径字符串被当成 brief 送去校验 = 必被拒。**prompt 要从文件读进变量再传。** ⚠️ 铁律 10 说的「run 抛找不到 brife 节点」= 那是**不合格 brief** 才走的路；合格 prompt 走的是直通分支 = 不抛。


🔴 **prompt 已写好 = 调 `run(prompt, leave_name, channel, caption)`**。它一次做完：写 CLIPTextEncode
→ 落盘留底 + 写 `.prompt.md` + 追加索引 → **调 `yuer_send_v2.sh` 真发飞书**。
❌ 不要为了“绕过报错”去手搓 submit/fetch/留底脚本 = 绕过脚本层保证 = **锁脸失效**，且

⚠️ **旧文写的「prompt 已写好 = 走 `run_with_prompt`，不调 `run`」= 已作废**（那条把「run 不可用」写死了 = 实际是「**不合格 brief** 走无 LLM fallback 那条路才抛找不到 brife 节点」= 合格 prompt 走的是直通分支 = 不抛）。**`run` 与 `run_with_prompt` 都可用 = 区别只是后者不走质量校验** = 两者都落底 + 真发。**判据 = prompt 质量拿不准 = 用 `run`（它会拒不合格 prompt）= 拿得准 = 两条都行。**


**留底验收 = 事前查，不是事后查**（出图后 0 主动查 = 见下面「图真发后禁跑」）：
1. **出图前**：我自己写的 prompt 我自己知道是不是中文 brief = 落笔那一步就过一遍 = 不需要事后翻文件。
2. **出图后**：只有**主人点名要 prompt / 要反推 / 要存档**时才 `cat <leave>.prompt.md` 查「来源」字段 = 无口令 = 0 查 = 主人手机已经收到图了，我还在翻文件 = 白等。
3. **汇报出图流程时禁止编造「按技能写了 prompt」** = 以留底文件为准（真的要说的时候才查）。

**🔴 图真发后禁跑的那一串命令**（发图后这几件事一律不做，除非主人点名）：
`vision_analyze` 验图 / `grep` 网关日志找发图记录 / `ls` 留底目录 / `cat *.prompt.md` 查来源 / `grep` `.sent` 确认 —— **五件全是白等** = stdout 三件套 + `.sent` 落盘时间戳已经是真发时刻。

（先列点再落笔；🔴 长度 0 阻断 = 超标不删不挖词；禁 `replace` 中途修剪）。

---

# 第三部分 · 出图后 reply 铁律（盖过一切）

## ⑦ 直出道 / 批量道 / 发图侧 = 指针（不在本档复制正文）
- **抽卡 / 洗图直出道 = 走独立脚本，0 现调 `run`**（脚本内已自带门禁 + 落底 + 真发 + 自发）= 唯一正文 = `yuer-image-trigger-discipline` §1.5。
- **批量出图 = 先走批量脚本**（`yuer_pi_chart_batch.sh` / `yuer_batch_by_character.py`，已自带门禁 + 落底 + 自发），stdout 打 `📩 REPLY:` 照抄贴，0 现调 `run` 逐张 = 唯一正文 = `yuer-image-trigger-discipline` §3.9。
- **出图 + caption 一条命令 = 禁止先出图再补发第二句**（补发撞平台 dedupe 去重 = 等于没发）+ **wrapper 真发已自打飞书 = caller 0 二次发**（看到 `📩 文字待发` / 没看到真发那行 = 停下问主人，0 盲补发）+ **发完的 `.sent` 守卫**（撞守卫 = 这张早发过了 = 补发会双发）+ **出图失败 caller 也不补发**（重跑同 prompt = 双图）= 唯一正文 = `creative/yuer-image-delivery` §2.1-2.5。

---

# 第六部分 · 抽卡直出 5 步 SOP

> **主人正解**：「每次抽卡是直接用的对吗？不写不改提示词」

| Step | 动作 | 关键 |
|---|---|---|
| 1 | **避号抽签** | 跑现成脚本 `scripts/pick_roster_record.py` = **别每次重写解析器** = `/tmp/yuer_used_<日期>.json` 抽完全部自动重置 |
| 2 | **6 件套 + 角色外观 + 骚姿势标注** | 档案里已有 = **直接拼 = 0 调 LLM 改写 = 0 凭印象** |
| 2b | **🔴 抽到成品提示词 = 0 加工** | **原文一字不动喂模型** = 0 清洗 0 改写 0 补结尾标记 0 剥中文半 0 出图前审核。判据 = 这个提示词谁写的：**上游反推的** → 入库时走全套闸门；**库里已有的成品** → 抽到就用。详见 `yuer-prompt-writer` §骨架+变量槽 |
| 3 | **写独特英文 prompt** | **800~2500 区间** = 档案 raw 拼接即可 = **🔴 禁手动扩写**（扩写只拖慢还挤爆上限）|
| 4 | **一键出图** | `bash ~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh <prompt_file> <leave_name> --report-only` = 体检 + 出图 + 发飞书一条命令跑完。**别直接调 `yuer_ka_pai_zhi_chu.py`** = 它只是被 wrapper 包着的内层，直调就绕过了长度体检 |
| 5 | **reply** | 跑 `pick_saohua_reply.py --match "<brief 场景词>"` 挑一条（挑不到自己写）|

**🔴 禁 `| tail -3` 截 stdout** = 会把「完成 success / 落盘 NNN 字节 / ✅ 已真发」**三件套切掉** = 看不见确认 → 误判没发 → 重跑 = **发两遍**。
**正解 = 用 `grep` 只抓要看的行。**

**exit 码判定（比看 stdout 更硬）**：

| exit | 含义 | 语儿动作 |
|---|---|---|
| 0 | 出图 + 发图全成功 | **不碰 stdout 那行 `📩 REPLY:`（已废除）** = 跑 `pick_saohua_reply.py --match "<brief 场景词>"` 挑一条，挑不到自己写（见下） |
| 2 / 3 | 出图失败 / 超时 240s | 报告主人，**不补发** |
| **4** | 出图 success 但发图失败 | **立刻手动补发 = 走唯一通道** `bash ~/.hermes/skills/creative/yuer-image-delivery/scripts/yuer_send_v2.sh <落盘> "<caption>"`（不带 caption 最稳）= **0 用 `feishu_send.py image`**（0 防重发 = 双发根）= **绝不允许只回文字** |
| **5** | `.sent` 守卫命中 = 这个 leave_name **已经真发过** | **不是失败！0 补发 0 重跑** = 换 leave_name 即可 |

**验收三件套**（stdout 必须看到）：「完成 (1X.Xs) success」+「落盘 ...png = NNN 字节」+「msg: success」。

**调试新开关**：`--dry-run`（只出图不发飞书、不写 `.sent`）= 测守卫生效时**用这个** = 0 往主人手机塞重复图。

---

