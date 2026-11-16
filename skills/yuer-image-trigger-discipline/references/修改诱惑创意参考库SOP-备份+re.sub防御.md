
> **本档已拆分** = 全文 4,875 字 → 2 份（每份 ≤3800 字）= 只搬不改写 = 下表为原文索引。

| 新档 | 原章节 | 字数 |

---

<!-- 摊平自：修改诱惑创意参考库SOP-备份+re.sub防御-01-修改提示词库必走-SOP-撞.md -->

# 修改提示词库必走 SOP（撞车沉淀 · 09-27 实战）

> 实战撞车：本会话 `re.sub(r'## 记录 164\n.*?(?=\n## 记录 165|\Z)', ...)` 贪婪匹配 `\Z` → 整个文件被截到 1.9KB（145953 → 986）= 162 条记录丢失。靠 `/path/to/data/hermes-skills-backup/` 24h 同步 + `cp /tmp/<bak>.md` 当场回滚救回 = **绝不能再撞**。

## 🔴 必走 4 步（修改前 → 修改后）

### Step 1: 必先 cp 备份（双保险）

```bash
TS=$(date +%Y%m%d_%H%M%S)
LIB="~/.hermes/skills/creative/yuer-image/references/提示词库-nsfw.txt"
cp "$LIB" "/tmp/yuer_reflib_bak_${TS}.md"
echo "✅ 临时备份: /tmp/yuer_reflib_bak_${TS}.md"
ls -la /tmp/yuer_reflib_bak_${TS}.md
```

**双保险** = 同时存在：
- `/tmp/yuer_reflib_bak_<时间戳>.md` = 当场回滚（30 天内）
- `/path/to/data/hermes-skills-backup/references/提示词库-nsfw.txt` = 24h 同步（每天凌晨）

### Step 2: 改文件 = 必走 `execute_code` 而非 `write_file`

**为何不用 write_file**：
- `write_file` = 必先读完整文件再写回 = 145KB+ 文件容易超时
- `write_file` = replace-all 模式 = 没有边界 = 一次写错 = 整个文件毁

**正解 = `execute_code` 内修改**：
- 内核变量持有 `with open(...) as f: content = f.read` 后的内容
- 任何 `re.sub` / `content.replace` 出错 = 立刻用备份 `cp` 回滚
- 修改后 `with open(..., 'w')` 写回 = `os.path.getsize` 验证大小

```python
import os, shutil, re
LIB = "~/.hermes/skills/creative/yuer-image/references/提示词库-nsfw.txt"
with open(LIB) as f:
    content = f.read
print(f"原始大小: {len(content)} 字符")

# 修改内容...
new_content = content.replace("OLD_STRING", "NEW_STRING")

# 验证大小没塌缩
assert len(new_content) > len(content) * 0.5, f"文件塌缩！原 {len(content)} → 现 {len(new_content)}"

with open(LIB, 'w') as f:
    f.write(new_content)
print(f"✅ 修改完成: {len(new_content)} 字符")
```

### Step 3: re.sub / regex 替换必加防御

**撞车根因**：
- `re.sub(r'X.*?Y', ..., content, flags=re.DOTALL)` 中 `Y` 不存在 = 量词自动贪婪到 `(?=\Z)` = 替换到文件末尾
- `re.sub(..., count=1)` 不显式传 = 默认全文件替换

**防御 3 件套**：

1. **模式必含结束锚点**：
```python
# ❌ 错：`?=\Z` 当 Y 不存在 = 贪婪到文件末尾
re.sub(r'## 记录 164\n.*?(?=\Z)', record, content, flags=re.DOTALL)

# ✅ 对：明确下一条记录号边界
re.sub(r'## 记录 164\n.*?(?=\n## 记录 165\n)', record, content, flags=re.DOTALL, count=1)

# ✅ 更安全：先 match 再 replace
match = re.search(r'## 记录 164\n.*?(?=\n## 记录 165|\Z)', content, re.DOTALL)
if match and match.group.startswith('## 记录 164'):
    new_content = content[:match.start] + record + content[match.end:]
```

2. **count=1 显式传**（即使只换一处）

3. **改完必验证大小**：
```python
assert len(new_content) > len(content) * 0.5, "文件塌缩超过 50% = 回滚"
```

### Step 4: 出错立刻回滚

```bash
# 出错 = 立刻 cp 备份回滚
cp "/tmp/yuer_reflib_bak_<时间戳>.md" "$LIB"
echo "✅ 已回滚"
```

## 🆕 append vs insert 选型

| 场景 | 工具 | 原因 |
|------|------|------|
| 在文件末尾追加新记录 | `with open(LIB, 'a') as f: f.write(record)` | append 模式不会改前面的内容 = 0 风险 |
| 在中间插入新记录（如记录 164 插在 163 后面）| `execute_code` + `re.sub` 或切片 | 必先备份 + 必 match 后 replace |

**正解**：新记录永远 append 在文件末尾（最大编号在最后）= 不需要 re.sub = 0 贪婪匹配风险。

```python
# 找最大编号
import re
with open(LIB) as f:
    content = f.read
matches = re.findall(r'^## 记录 (\d+)', content, re.MULTILINE)
next_n = max(int(m) for m in matches) + 1
print(f"下一条 = 记录 {next_n}")

# 直接 append 到文件末尾
record = f"\n## 记录 {next_n}\n- **日期**：...\n- ...\n\n"
with open(LIB, 'a') as f:
    f.write(record)

# 验证
import subprocess
verify = subprocess.run(["grep", f"## 记录 {next_n}", LIB], capture_output=True, text=True)
assert verify.stdout.strip, "记录未追加成功"
```

## 反查自检门（修改完必跑）

```bash
LIB="~/.hermes/skills/creative/yuer-image/references/提示词库-nsfw.txt"

# 1. 文件大小 > 100KB（参考库正常 145KB+）
SIZE=$(stat -c %s "$LIB")
[ "$SIZE" -gt 100000 ] && echo "✅ 文件大小正常: ${SIZE} bytes" || echo "❌ 文件塌缩！"

# 2. 记录数量 = 文件修改前数量 + 新增数量
COUNT=$(grep -c "^## 记录 " "$LIB")
echo "记录数量: $COUNT"

# 3. 末尾记录号 = 期望的新增记录号
LAST=$(grep "^## 记录 " "$LIB" | tail -1 | grep -oE '[0-9]+')
echo "末尾记录: $LAST"

# 4. 文件可读（没有截断/编码错误）
head -5 "$LIB"
echo "---"
tail -5 "$LIB"
```

**任一项失败 = 立刻回滚**。

---

<!-- 摊平自：修改诱惑创意参考库SOP-备份+re.sub防御-02-撞车防御硬表.md -->

## 撞车防御硬表

| ❌ 撞车模式 | ✅ 正解 |
|---|---|
| ❌ 直接 `write_file` 覆盖 145KB 参考库 | ✅ `cp` 备份 + `execute_code` 内 `with open` 读改写 |
| ❌ `re.sub(r'X.*?Y', ...)` 不带 `count=1` | ✅ `count=1` 显式传 + 明确结束锚点 |
| ❌ 模式不严：`?=\Z` 让贪婪到末尾 | ✅ match 验证 + `replace` 而不是 `re.sub` |
| ❌ 修改完不验证大小 = 直接告知主人成功 | ✅ `assert len(new_content) > len(content) * 0.5` |
| ❌ 出错不立刻回滚 = 主人收到半空记录 | ✅ `cp /tmp/<bak> $LIB` 一键回滚 |
| ❌ 撞了 1-2 次不重跑 = 主人打脸「怎么又撞」 | ✅ 撞 1 次 = 改 regex；撞 2 次 = 用 `replace` 替代 `re.sub`；撞 3 次 = 放弃 = 走手工 cp 备份重建 |


**撞车现场**：跑 agnes 反推成功后，语儿脑子自动写记录 164 的 Python 字符串 = 拼好后用 `re.sub(r'## 记录 164\n.*?(?=\n## 记录 165|\Z)', ...)` 拼接 = 撞 `(?=\Z)` 因为 `## 记录 165` 不存在 = 贪婪匹配到文件末尾 = 替换为新记录 = 文件只剩头部 + 记录 164 = 145953 → 986 字符 = 162 条记录丢失。

**修复过程**：
1. 立刻 `ls -la 提示词库-nsfw.txt` = 1910 字节 = 撞车确认
2. 找备份：`/path/to/data/hermes-skills-backup/references/提示词库-nsfw.txt` = 145407 字节 = 162 条 + 文件头
3. 读备份内容 + 追加新记录 164 + 写回主路径 = 146209 字节 = 162 条老记录 + 1 条新记录 + 文件头 = 完整恢复
4. 主人飞书已发洗图 + msg=success = 洗图成果保留 = 仅入库链路回滚修复

**主人正解打脸**（事后脑补）：主人会问「为什么撞了 = 为什么没备份」 = 「为什么 re.sub 没防御」 = 「为什么不用 append 而用 re.sub」。

**整改金标准**：本 support file 落地 = 未来任何 agent 修改大参考库前 = 必读本文件 = 必先 cp 备份 = 必走 execute_code = 必 match 验证 = 0 re.sub 撞车。

---
