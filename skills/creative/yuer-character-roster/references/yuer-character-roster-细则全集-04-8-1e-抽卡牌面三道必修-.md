### 8.1e 🔴 抽卡牌面三道必修 = 老牌三个固定病（11-10 = 只剩第 3 类必跑）

`pick_ka_prompt.py` 落盘的成品里，**老牌（早期入库那批）稳定带三个病**。**🔴 11-10 主人钦定抽卡 0 门禁 = 三道里只有「解析残渣」那类还必跑**（第 1 类老前缀 + 第 2 类陌生男人 = 0 必跑 = 抽到就出）。要跑就一条命令：`scripts/ka_post_fix.py`（0 手改）。

| # | 病 | 长什么样 | 不修的后果 | 修法 |
|---|---|---|---|---|
| 1 | **年龄/国籍 PREFIX 走老模板** | `one breathtakingly beautiful 18-year-old Chinese young girl with pure, innocent refined features, clear bright eyes…` | 🔴 **11-10 = 已免**：老前缀不改照样出图 = 脸锁 LoRA 压得住 | **0 必跑**（真要改 = 正则整段换成灵魂脸 PREFIX：`a 20 years old young Asian woman with a <表情词>, `）|
| 3 | **解析残渣** | `lngcon` / `connectors,,` / `` 空壳 / `., ` | 底模把脏 token 当语义吃 = 画面漂 | **✅ 唯一仍必跑的一类** = 机械剥掉（`pick_ka_prompt.py` 内建一部分，**没盖全的用本脚本补刀**）|

```bash
# 一条命令剥解析残渣（自行 0 手改，打印新长度 + 前 150 字符供核对）
/usr/bin/python3 ~/.hermes/skills/creative/yuer-character-roster/scripts/ka_post_fix.py /tmp/ka_<记录号>_prompt.txt

# 🔴 11-10 = 主体门禁已免 = 0 跑 check_prompt_subject.py = 抽到啥出啥
```

**🔴🔴 11-10 主人钦定 = 抽卡道一道门禁都不设（盖过上面 11-05 口径）**

> **主人口令原话：「不需要卡门禁，抽卡直接出就行！抽卡不设置门禁」**


**🔴 为什么主体门禁在抽卡道免掉也 0 掉脸锁（11-10 实测坐实）**：出图链路里 `grep` 不到任何 `check_prompt_subject` / `nolora` 自动判定 = **脸锁永远 on** = 主体门禁从来就不在链路上 = 它只是「我手工把牌踢掉重抽」= 取消它 = 抽到的牌照样是语儿的脸。

**🔴 上面三道「必修」里，第 1 类（老前缀）现在 = 0 必跑**：老牌的前缀不改照样出图（脸锁 LoRA 压得住）= 门禁免了 = 前缀也不用改了。**第 3 类（解析残渣）仍要剥** = 底模把脏 token 当语义吃。**第 2 类（陌生男人）= 0 必跑**（抽到就出）。

**🔴 判据 = 怎么证明「免门禁 0 掉脸锁」= 0 拍脑袋 = 去 grep 出图链路**：`grep -nE 'check_prompt_subject\|nolora' yuer_ka_pai_zhi_chu.py yuer_ka_fast.sh` = **0 命中** = 链路里根本没有自动主体判定 = 脸锁永远 on = 门禁从来就不在链路上 = 它只是「我手工踢牌」。**这条 grep 以后每次改抽卡链路都要重跑一遍**（出图脚本一旦加了自动切链路的逻辑 = 免门禁就真的会掉脸锁 = 那时必须恢复门禁）。

| 坑 | 正解 |
|---|---|
| 一次抽卡调多次 `pick_roster_record.py` 想「看清楚」| **只调一次** = 每次调用都重新洗牌 = 第二次抽到的是**另一张牌** = 白抽 + 烧掉好牌。取 stdout 全文即可 |
| 跑 `--json` 想解析干净 | `--json` 前后带体检行 = `json.loads` 炸 `Extra data` = **走纯 stdout 字段行，别包 JSON** |
| 在本技能 `scripts/` 里找抽卡脚本 | 本技能 `scripts/` 无抽卡脚本 = **抽卡脚本在 `~/.hermes/skills/yuer-run-one-brief/scripts/pick_roster_record.py`** |
| 库里的【成品提示词】原样喂出图 | **🔴 就是要原样喂**= 0 改写 0 清洗 0 补收尾标记 0 剥中文半。实测 3007 字符的成品提示词原样喂 = 12.1s 出图正常 = 「老格式出不了图」不成立 |
| **命令 2 亲手手打提示词**（把 stdout 里的成品提示词敲进 `write_file`）| **🔴 手打 = 加工 = 违「0 加工」**。哪怕自我感觉一字不差，2352 字符里敲错一个 `and` 底模照吃不误，而主人拿到的是被改过的牌。**正解 = 管道保真（一条命令，不经人手）**：**首选 `scripts/pick_ka_prompt.py`**（抽档案 + 落盘 + 去噪一步做完）；下面这段是它的等价手敲版，不方便跑脚本时才用。

```bash
OUT=/tmp/ka_pick_$$.txt
/usr/bin/python3 ~/.hermes/skills/yuer-run-one-brief/scripts/pick_roster_record.py > "$OUT" 2>/dev/null
python3 - "$OUT" <<'PY'
import re,sys
t=open(sys.argv[1],encoding='utf-8').read
rec=re.search(r'记录\s*(\d+)',t).group(1)
m=re.search(r'\[成品提示词\]\s*(.+)',t)
p=m.group(1).strip
