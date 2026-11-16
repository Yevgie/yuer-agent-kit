# 铁律库（v1.0 · 06-30 拆分）

> **来源**：yuer-image SKILL.md v3.8 13 铁律段（原 14748 字符）+ v1.5-v1.8 实战沉淀。拆分原因：SKILL.md 过大（55KB），铁律分类方便检索。

## 5 个分类

| 档 | 内容 | 铁律编号 |
|---|---|---|
| `references/铁律/00-调用路径铁律.md` | 永远只走 mie 技能 / ComfyUI server 地址 / 工作流地图 | 0, 1, 2, 2a-d |
| `references/铁律/01-prompt写法铁律.md` | 东亚锚定 / 摄影 7 维度 / 偷露 / 单图单区域 / 多人物 / feishu_send / **嘴部区域极简（面部畸形防线）** / **出图后畸形复验（豆包反推专项验图）** | 3, 4, 5, 6, 6a, 7, 7a + 嘴部极简 · 畸形复验 |
| `references/铁律/02-出图态度铁律.md` | 不反问 / 变体铁律 / 绝不自检 / NSFW 反推 / 反推原文不改 / 发图零自审 | 8, 9, 10, 10a-d |
| `references/铁律/03-平台与系统铁律.md` | 先扫技能 / TG 不重发 / 系统档权限边界 | 11, 12, 13 |
| `references/铁律/04-新工作流与兜底铁律.md` | 反推 job_id / vision_analyze 重启 / 发图默认 SOP / B4 压缩 / 拿图路径 / 导入 SOP / 默认 prompt 清空 / CLI timeout 兜底 / node_mapping key | 14-21 |

## 检索方法

```bash
grep -l "偷露反转" ~/.hermes/skills/creative/yuer-image/references/铁律/
grep -r "v1.5 变体" ~/.hermes/skills/creative/yuer-image/references/铁律/
```

## 与 SKILL.md 的关系

- SKILL.md 顶部"出图前必读流程"4 步 SOP = 总览
- 铁律库 = 详细规则
- references/ 实战档 = 血泪案例
- memory_store.db = 灵魂级铁律（按需 search）
