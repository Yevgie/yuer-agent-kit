## 🔴 本地档（local / fast）= 单纯反推提示词 = **活链路 = 不是历史**

> **🔴 v2.2 三档选型 = 云端 agnes 是默认主线 = 但 local / fast 两档还在跑 = 本块的节点链（LoadImage 17 → QwenTE_ImageInfer 21 → easy showAnything 20）= 只有这里有 = 删了 = 本地档直接哑。**

**触发场景**：主人说「反推 / qwen 反推 / 反推提示词 / 单纯反推 / 只要提示词 / 反推给我提示词 / 反推工作流 / 不要洗图」

**调用路径**：`yuer_qwen_reverse_only.reverse(image_path, tier)` → 返回反推提示词文本（**不出图**）

**工作流**：`api_qwen3.5_9b_反推_默认.json`（⚠️ v2.0 时代的 `api_qwen3.8_图片提示词反推.json` = **27B，已于 11-04 删除**）

**节点链路**（4 节点，API 格式 = 顶层 key 就是节点 id，无 `nodes` 数组）：
```
LoadImage (节点 17) ──────────┐
                              ├→ QwenTE_ImageInfer (节点 21) → easy showAnything (节点 20)
QwenTE_ModelLoader (节点 19) ─┘   [9B 破限 Q8_0 + mmproj 视觉投影]
```

**v2.0 变更（改脚本的 4 处，缺一即静默失败）**：

| 项 | v1.0（qwen 3.5） | v2.0（qwen 3.8） |
|---|---|---|
| 工作流路径 | `qwen3_vision_single.json` | ~~`api_qwen3.8_图片提示词反推.json`~~ → 现役 `api_qwen3.5_9b_反推_默认.json` |
| 推理节点 | `llama_cpp_instruct_adv` | `QwenTE_ImageInfer` |
| **输出取文本节点** | `16` PreviewAny | `20` easy showAnything |
| 轮询上限 | 180s | 600s（本地模型加载慢） |

**🔴 输出节点 id 必须跟着工作流走**：写死 `16` 换到新工作流后永远取不到文本，报「反推超时」而不是报「节点不存在」——因为 `outputs` 里有节点但字段名不同。脚本用 `_extract_text` 按 `text/anything/value/string` 逐个试 + 全节点取最长字符串兜底，**不要只认一个字段名**。

**实测性能**（本地 9B）：上传 ~0.5s，加载 + 反推 ~30s，输出 8 段编号格式 1100-1800 字符。

**🔴 中英混写的正解（主人拍板方案①）**：qwen 3.8 会把中文标题自己翻成英文（「机位角度」→「机位 angle」「骚姿势标注」→「骚 pose 标注」）。两条解法，**主人钦定走①**：

1. **工作流「提示词」框的 8 段标题锁死成纯英文**（已落地，备份 `.bak_zh8seg_20260929`）：

```
1. Scene  2. Camera Angle  3. Pose  4. Wardrobe
5. Lighting  6. Mood  7. Character Shell  8. Seductive Pose Note
```

加了一句 `Do NOT translate the section titles; keep them exactly as written below.` = 实测 qwen 就不翻了。

2. **解析器加中英别名组**（`yuer_parse_suite.py` 的 `SRC_KEYS_EN`）= 每维一个 `(?:中文|English)` 正则组，兜住历史混写数据 + agnes 中文格式 = 两条链路共用一份解析器。

**⚠️ 参数坑**：`最多帧数` 的 min = 2，设 1 会被 ComfyUI 拒（`value_smaller_than_min`）= 单图反推设 2。

**⚠️ 标题残渣**：英文 `8. Seductive Pose Note: xxx` 切出来正文前面会带一个孤零零的 `Note:` = 解析器 `main` 里加了 `re.sub(r"^(?:Note|Scene|Angle|Pose|Wardrobe|Lighting|Mood|Shell)\s*[:：]\s*", "", v)` 剥掉。

**🔴 反推输出格式契约**（8 段编号式 + 两条链路统一 + 解析器容错 5 变体 + 中英混写陷阱 + 静默失败三层检查）→ 见 `references/8section-reverse-inference-contract.md`

**🔴 排查反推链路不稳定时，先分清「模型这轮写了什么」和「我的哪层逻辑失效了」——后者才是能修的东西。** 主人会直接问「是不稳定是反推的结果不稳定吗」，答错等于把责任推给模型。**判别方法**：拿同一条留底**反复跑解析器** —— 输出稳定但结果错 = 我的逻辑层坏了（跟模型这轮怎么排版无关）；输出本身就在飘 = 才轮到查上游 prompt。实战里两者同时存在，但**决定性的是我的逻辑层**：身份句分身那次两层剥除同时瞎（头句判定不认前导空格 + 兜底靠「前面有没有 a」判断，而那两句前面都恰好有 a）。**反推链路反复出同一类脏牌 = 先查自己的正则，别先怪模型。**

**🔴 改格式 = 改上游 system prompt / 工作流「系统提示词」框，不是改下游正则。** 下游只治标；上游写「三段式散文」时，解析器无论多少个变体都会在某张图上退化（实测 = 六件套全填同一段）。

**vs 实战 318 钦定的 yuer_reverse_inference.run 关键区别**：

| 维度 | `yuer_qwen_reverse_only.reverse` 🆕 v2.2 | `yuer_reverse_inference.run` 实战 318 |
|------|------------------------------------------|------------------------------------------|
| **工作流** | 云端 agnes API（默认）/ `api_qwen3.5_9b_反推_默认.json`（local）/ `api_qwen3.5_4b_反推_快速筛.json`（fast）| `语儿无需反推的快速洗图工作流` |
| **是否出图** | ❌ 不出图 | ✅ 出图（洗图直出） |
| **反推文本输出** | PreviewAny 节点 = 文本 | 节点 32 llama_cpp_instruct_adv = 仅显示，不持久化 |
| **调用场景** | 主人要「单纯反推提示词」| 主人发参考图，要「反推参考出图」|
| **结果交付** | str 反推文本 | MEDIA: 图片路径 + 留底 |

---

