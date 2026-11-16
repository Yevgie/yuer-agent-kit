---
name: yuer-image
description: "Use when 出图/看看你/写提示词/继续/洗图/存档/套图/图片链路。🔴 出图前先读 references/出图速查卡.md → 写 prompt → 跑 scripts/yuer_ka_fast.sh = 2 轮 <60s。身材参数 = 铁律/02-身材特征档.md。"
version: 8.0.0
author: yuer
license: MIT
metadata:
  hermes:
    tags: [creative, image-generation, comfyui, krea2, yuer, soul-face-stable, breakthrough-time-space]
    related_skills: [yuer-prompt-writer, yuer-krea2-prompt, yuer-moss-prompt, yuer-pose-diversity, yuer-image-trigger-discipline, yuer-image-delivery, yuer-run-one-brief]
---


> ## 🔴 永远生效（每次出图都算 = 不读 references 也得先认这四条）
>
> **1 · 减法铁律（11-15 主人钦定）** = 体型段 ≤ **200 字**｜脸部段 ≤ **200 字**｜**骨架不变**（落笔前 5 锚 + prompt 句子顺序 + 九维框架 = 参照出来的那个框架，一个字都不动）｜**其余设定一律少** = **约束越少 = 创意越活 = 堆得越多越死板** = 别再给身体加句子「修」体型。
> **2 · 参数唯一真值（照抄 = 全库 0 第二份）** = 机身 = 本技能 `references/铁律/02-身材特征档.md`｜脸部 = `yuer-prompt-writer` 技能档 `语儿专属硬锚.md`。
> 🔴 **「改那里 = 全库自动跟上」只对文档成立 = 脚本里内联的参数字面量必须一起改**：脚本（批量姿势变体 / 体型池 / 门禁自测样例 / 落盘真值 txt）里会内联同一串参数 = 改 md 档不会改它们 = 两边一旦不一致 = 门禁自测样例跑的是旧串 = 主人改完档以为生效了其实没生效。
> **改参数段后必跑对账** = `grep -rn "<参数串里的一句>" scripts/ /path/to/media/*CURRENT*` = 命中处逐个确认是同串 = 有旧串 = 改掉。**判据 = 参数串有第二份 = 就是漂移源。**
> 🔴 **对账完 = 再把新参数段跟一段真场景句拼起来跑一次门禁** = `check_body_anchors.py <拼好的prompt>` = 参数段自己过关 **≠** 跟场景句拼起来过关 = 场景句里的 `her waist` / `her leg` 会跟参数段里的同部位撞 = 叠写 = 门禁 FAIL = **场景句改成不含该部位词**（例：场景写 `the sheet pushed down to her midsection` 而不是 `to her waist`）= **改场景句 = 0 改参数段** = 参数段是唯一真值 = 场景句让路。**判据 = 新参数段 + 一段真场景句 = 门禁 rc=0 = 才算参数段能用。**
> **3 · 默认工作流 = Krea 2**（`yuer_moody_fast`）= 不传 `--model`；Moss 保留两岗 = 主人点名 / 要中文原样出不翻。
> **4 · 改参数段 = 顶替 0 追加** = 追加 = 同部位叠写 = 门禁必 FAIL（体积放大）= 素材句顶掉被替那句 = 顶完 0 再加第二句。
> **5 · 人物成分 = 只许女生 + 主人** = 禁主人以外的男人（路人 / 同学 / NPC）= **主人可完整出镜**（按 MASTER_FACE + MASTER_PROMPT 写 = 写法 `references/主人在场-主人完整出镜写法与门禁-01-主人在场-主人完整出镜的写法.md`）= 禁陌生男人 ≠ 禁主人 = 写成「绝不画任何男角色」= 与钦定打架 = 改这句话。

---

> **本档已拆分** = 全文 16,782 字 → 5 份（每份 ≤3800 字）= 只搬不改写 = 下表为原文索引。

| 新档 | 原章节 | 字数 |
| `references/yuer-image-索引表-01.md` | 索引表 1/4（129 条细则索引 · 第 1 份） | — |
| `references/yuer-image-索引表-02.md` | 索引表 2/4（第 2 份） | — |
| `references/yuer-image-索引表-03.md` | 索引表 3/4（第 3 份） | — |
| `references/yuer-image-索引表-04.md` | 索引表 4/4（第 4 份） | — |
| `references/铁律/README.md` | 铁律库 6 分类（调用路径 / prompt 写法 / 出图态度 / 身材参数 / 平台系统 / 新工作流兜底） | — |
| `templates/README.md` | 批量提速工具集（main_template / view_api_pull / 批量出图 SOP） | — |

> **首读** = `references/yuer-image-索引表-01.md` → 其第 1 行 `references/SKILL-01-yuer-image-出图总.md` = 正文入口（其余按表查）
