# v4.6 · soul_face 字段防误报

> **场景**：myself-now 出图 prompt 拼接时 soul_face 13 关键词和 body 文本混合，v5_self_check `--check variation` 误报多个"变化维度叠加"警告。

## 🔍 实战现象（07-04 凌晨 myself-now）

final_prompt 拼接后：
```
1girl, solo, sugar_face_z, ..., signature small beauty mole under left eye, refined facial features, ..., long natural lashes, soft brows, slim nose bridge, ..., 1girl, solo, young asian woman, ..., long natural lashes, soft brows, slim nose bridge, ...
```

soul_face 字段里 `long natural lashes, soft brows, slim nose bridge, slightly plump lips, pale porcelain skin` 被 hermes chat 输出重复带了 1 次到 body 段尾。

**v5_self_check variation 警告**：
```
⚠️ 室内锚定弱（但实际加过）
⚠️ 反义缺失（但实际加过）
⚠️ 表情变化叠加
⚠️ 姿势变化叠加
```

4 个 false positive。

## ✅ 正确拼接法（split + concat）

```python
trigger = "1girl, solo, sugar_face_z, anatomy_detail, masterpiece, best quality"
soul_face = "signature small beauty mole under left eye, refined facial features, sharp jawline, deep-set eyes, long natural lashes, soft brows, slim nose bridge, slightly plump lips, pale porcelain skin, cold elegant aura, modern Chinese beauty"
indoor_anchor = "clearly indoor scene, no outdoor elements, no natural daylight, artificial light only, closed space, the window completely dark with black curtains drawn closed, no sky visible, no trees visible, no campus visible"

# hermes chat 返回的 body 整段
body = """A first-person late-night selfie taken covertly from a phone screen captured in a dimly lit female dorm bunk bed, where a young woman in her early twenties lies half-propped against a pillow at the lower bunk near the window, ..., long natural lashes, soft brows, slim nose bridge, slightly plump lips, pale porcelain skin, cold elegant aura, modern Chinese beauty, ..."""

# 关键:body 切前 10 段保留 trigger/soul_face(防 soul_face 重复)
parts = body.split(', ', 10)
rest = ', '.join(parts[10:]) if len(parts) > 10 else body
final_prompt = f"{trigger}, {soul_face}, {indoor_anchor}, {rest}"
```

## 🔴 反模式（不要做）

❌ 把 soul_face 直接 f-string 拼到 body 前后：

```python
# 错:soul_face 字段内部词在 body 里被 self-check 重复统计
final_prompt = f"{trigger}, {soul_face}, {body}"
```

## 📋 自检 debug 流程

1. v5_self_check 报 variation 警告 → 看警告里具体哪几个维度
2. 如果维度是 `lashes / brows / lips / skin / aura` → soul_face 重复问题
3. 用 split 法清掉重复 → 重跑 self-check
4. ✅ 全部通过 → 出图

## 关联

- `yuer-myself-now` SKILL.md Step 4 拼接 prompt
- `image-prompt-writer` v5.1 self-check variation 模式
- 实战档：`2026-07-04-v4.6实战档-myself-now-soul-face误报.md`（该档已不存在 · 历史提及）