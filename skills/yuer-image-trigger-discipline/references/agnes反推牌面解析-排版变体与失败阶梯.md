# agnes 反推牌面解析 · 排版变体与失败阶梯

> **唯一职责** = 洗图/入库链路里，参考库 9 个牌面字段为什么会被闸门拦下来、怎么修。
> 解析器 = `~/.hermes/bin/yuer_parse_suite.py`，闸门 + 调用 = `~/.hermes/bin/yuer-wash-and-archive.sh`。

---

## 一、核心原则：格式不能靠指令求，只能靠解析器结构性地认

agnes 是中文人格。brief 里写 `all body content in English` / `必须写成「中文 || English」`，
**跑几次能生效几次都不一定**。每次输出排版都不一样。

**正解 = 解析器一侧同时认全部已知排版；新变体出现时，往下加一条判定，不要改 brief 措辞碰运气。**

| 变体 | 长相 | 解析器认法 |
|---|---|---|
| A | `中文 \|\| English` | 分隔符切段 |
| B | `中文 \|\| 中文 \|\| English` | 切出**全部**段，挑 0 汉字里拉丁字母最多的那段 |
| C | `中文整句。 English`（无分隔符）| 找**最后一个汉字**，它之后就是英文半 |
| D | `中文, 书店, 阅读。 Sultry, bookstore, ...`（句末接英文）| 同 C |
| E | 第 9 段漏掉「成品提示词:」标签，直接写 `9. a 20 years old ...` | 成品提示词额外认「裸编号 + 英文长段」 |
| F | 第 9 段写到相机参数中间就断（`…85mm f/1.2, 1/1000s ISO`）| 收尾幂等补齐，见下 |

**判据优先级**（全部纯结构性判定，不看措辞）：
`0 汉字 > 拉丁字母数最多 > 最后一个汉字之后 > 原样`

**踩坑记录**：判据写成「有 || 就取第二段」→ 遇到变体 B（三段）直接取到中文段；
写成「找第一个 ASCII 标签:」→ 遇到变体 C/D 完全失配。**每一次都要靠实测数据修，不能靠推理。**

---

## 二、成品提示词的两个幂等自愈

| 函数 | 何时补 | 补什么 |
|---|---|---|
| `ensure_opening` | 开头不是 `a 20 years old young Asian woman with a` | 补人物锚点句（缺锚点 = 抽卡出图人脸漂移）|
| `ensure_closing` | 尾巴 260 字符内没有 `no text` / `no watermark` / `no logo` | 先砍残缺尾巴（`ISO 500`、`1/1000s` 这种半个参数），再补标准收束语 |

⚠️ **收尾补齐不是掩盖截断**——先砍残缺尾巴再补，补的是固定收束语，不是猜出来的内容。
⚠️ 补出来的成品提示词词数可能远低于 400（实测 130-388）= 底线能过闸门 = 出图质量另说 = **别拿词数当质量信号**。

---

## 三、失败阶梯（撞到哪一格做哪一格，不跳级）

```
牌面污染自检未过
  ├─ 某字段含中文 ────────► 查该字段原始排版是不是 B/C/D 变体
  │                        ► 是 → 解析器加一条结构判定（不是改 brief）
  │                        ► 否 → 查正则边界是不是被下一维标签抢走
  ├─ 某字段仍含「||」─────► en_half 走了「只取第二段」老路 → 改成切全部段挑最英文
  ├─ Full Prompt 整维空 ──► 第 9 段漏标签（变体 E）→ 加裸编号兜底
  ├─ Full Prompt 缺收尾 ──► 变体 F 截断 → ensure_closing
  └─ 6 件套占位符 ─────────► agnes 返回拒答模板 / 空 / 错格式
                            ► 换 SFW 措辞重写 brief 重试 ≤1 次，仍撞走 L2 fallback
```

**闸门全部失败都会回滚参考库 + 退出码 2** = 不留脏牌 = 可以放心反复重跑。

---

## 四、单张重跑（批跑中途失败后怎么补）

`failed{}` 里的索引不会被 `next` 自动重试（`current_index` 已越过它）。补跑单张：

```bash
python3 - <<'EOF'
import json
p = '/tmp/telegram_state.json'   # 花瓣库换 /tmp/huaban_state.json
s = json.load(open(p))
s['current_index'] = <失败索引>
s['failed'].pop('<失败索引>', None)
json.dump(s, open(p, 'w'), ensure_ascii=False, indent=2)
EOF
bash ~/.hermes/bin/telegram-batch.sh next
```

⚠️ 重置 `current_index` 前先确认失败索引**没被 done 记过**——记过 = 已入库 = 重跑产生重复记录。
⚠️ `reset` 更危险：清空整个 done = 已入库的图全部重复入库 = 参考库污染。**只在状态文件真丢了才用。**

---

## 五、入库成功后的自验（不信任脚本的一行成功）

脚本打「记录 NNN 入库成功」之后，**回读那条记录块**确认 9 个字段真的 0 中文：

```bash
python3 - <<'EOF'
import re
lib = "~/.hermes/skills/creative/yuer-image/references/提示词库-nsfw.txt"
c = open(lib, encoding="utf-8").read
m = re.search(r"^## 记录 NNN\b(.*?)(?=^## 记录 |\Z)", c, re.S | re.M)
blk = m.group(0)
for f in ["Scene","Camera","Pose","Wardrobe","Lighting","Mood",
          "Character Shell","Visual Hook","Full Prompt"]:
    mm = re.search(r"\| \*\*"+f+r"\*\* \|(.*?)\|", blk, re.S)
    v = mm.group(1) if mm else ""
    print(f, len(re.findall(r"[\u4e00-\u9fff]", v)))
fp = re.search(r"\| \*\*Full Prompt\*\* \|(.*?)\|", blk, re.S).group(1)
print("开头", fp.strip.startswith("a 20 years old young Asian woman with a"),
      "收尾", any(x in fp[-260:].lower for x in ("no text","no watermark","no logo")),
      "词数", len(fp.split))
EOF
```

**记录块标题有两种形态**（`## 记录 002` 无日期后缀 / `## 记录 312 · 2026-10-01` 有后缀），
grep 回读**别用 `startswith("## 记录 NNN ")` 带尾空格**——那样 2-051 号全部找不到 = 自检对老记录永久放行。
用 `re.match(rf"^## 记录 {num}\b", b)` 的编号边界正则。

**meta 行是中文正常**（`留底图` / `反推全文` / `来源` / `入库时间` = 溯源路径和日期，不是牌面）= **别拿整块的中文数当污染判据** = 只看 9 个牌面字段。
