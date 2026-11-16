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