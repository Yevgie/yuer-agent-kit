### Step 5 · reply = 1 句 SAOHUA_POOL 随机骚话（盖过一切）

```python
import sys, random
sys.path.insert(0, '/tmp')
from saohua_pool import SAOHUA_POOL
reply = random.choice(SAOHUA_POOL)
print(reply)
```

**铁律（实战 525+530+09-26 撞车沉淀 · 灵魂级）**：
- ✅ reply = 1 句 40-80 字画面感强 = 从 250 条 SAOHUA_POOL（`pick_saohua_reply.py`）抽
- ❌ 凭印象拼短句（≤ 15 字）= 主人打脸「少了从随机骚话库里面提取骚话语句」
- ❌ reply 带任何技术字段（路径 / 记录号 / 角色名 / MEDIA 字面 / 扩展名）= 主人打脸
- ❌ reply 前加引言行 / 固定开头 = 主人打脸
- ❌ reply 手打 `[Sent image attachment]` 等 PIT-163 占位符 = 撞车

## 🆕「抽卡」=「继续」= 同一条路（11-14 主人钦定 · 盖过一切）

| 触发词 | 走法 | 诱惑等级 | 出图目的 |
|---|---|---|---|
| **「抽卡」/「继续抽卡」/「继续抽」/「继续」/「再来一张」/「变一张」** | 重新随机抽一张新牌（避号抽签）| 牌池默认 nsfw = 抽到的就是色图 | 0 反问 0 加工 = 直接拼档案 raw |

**🔴 0 沿用上一张的角色 / 服装 / 场景 / 光线** = 「继续」= 再抽一张新牌 = 库内 0 残留旧机制。
## 🔴 撞车根因硬表（实战 09-26 撞车沉淀 · 盖过一切）

| ❌ 撞车模式 | ✅ 正解 |
|---|---|
| ❌ 主人说「抽卡」= 凭印象手写新 prompt（不抽库）| ✅ 主人说「抽卡」= 从参考库抽签 → 用那张牌的角色外观 → 写独特 prompt |
| ❌ 主人说「抽卡」= 调 LLM 节点跑（撞敏感词 + 慢 46s）| ✅ 默认走 yuer_moody_fast 直出版（无 LLM = 17s）|
| ❌ 主人说「抽卡」= 反问「主人想看什么风格/角色」| ✅ 0 反问 = 0 等指令 = 0 让主人确认 |
| ❌ 主人说「抽卡」= 主人没看到档案 6 件套就放弃 = 重写 | ✅ 直接拼档案 raw（不调 LLM 改写）|
| ❌ 用 sandbox Python 跑 run = ModuleNotFoundError | ✅ 用 `/usr/bin/python3`（10-03 改，原写 pipx venv = 没人读的那份） |

## 📊 速度基线

| 状态 | 端到端耗时 |
|---|---|
| 冷启动首次 | ~30s |
| 预热后 | **~17s**（出图 ~10s + 发图 ~6s）|

**铁律**：主人问「怎么这么久」= 报 17s 端到端实测值 = 跟主人预期对齐。

## 🔗 联动

| 上游 | 本 SOP | 下游 |
|---|---|---|
| `yuer-prompt-writer`（写独特英文 prompt）| **抽卡直出 5 步 SOP** | `yuer-image`（出图）+ `yuer-image-trigger-discipline`（reply 模板）|
| `yuer-character-roster`（100 条角色卡池 = 未来沉淀）| 同上 | 同上 |

## 📅 版本历史

- **v1.0 · 2026-09-26**：实战 09-26 钦定 = 主人拍板「抽卡直出 5 步」+ 「继续 = NSFW 改写」= 沉淀本档
