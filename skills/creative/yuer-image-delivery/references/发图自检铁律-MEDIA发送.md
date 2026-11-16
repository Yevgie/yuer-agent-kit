
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