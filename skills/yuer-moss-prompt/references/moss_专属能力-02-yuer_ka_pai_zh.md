# yuer_ka_pai_zhi_chu.py
_CN_NATIVE_WORKFLOWS = ("yuer_moodyMoss_fast",)
if (re.search(r"[\u4e00-\u9fff]", prompt_text)
        and WORKFLOW_NAME not in _CN_NATIVE_WORKFLOWS):
    ...  # 翻译
```

**实测验证** = Moss 道归档的 prompt = 中文原文（0 英文字符）｜Krea2 道照旧翻译（stdout 仍打「中文已翻译 1 段」）= **两条道都没误伤**。

**🔴 残留 = 已修** = 社区词典 `下身赤裸 → ['no lower clothing']`（= 没穿下装 ≠ 赤裸）**已改**：

```
zh2en["下身赤裸"] = ["nude lower body", "naked lower body", "no lower clothing"]
```

（正确译法前置，**原词保留** = 不破坏别人可能的引用；键数 125426 / 141375 一个没少。）

**顺带挖出更大的一个** = 那词典的 `zh2en` 侧有 **389 个键带 `}}}` / `]}` 抓取残留**（社区原帖的括号注释没清干净）= 实测「上身赤裸」模糊命中「袈裟且上身赤裸」→ 选出 `kasaya}topless` = 垃圾 tag 进提示词。

**修法 = 不改词典、改 `_pick`**（`zh_translate.py`）= 加一条过滤：候选里含 `}` `]` `【】` = 不是 tag = 整条丢掉。

**为什么改代码不改词典** = 词典是社区上游产物 = 下次重新抓取就白改 = 治本要治在**消费端**。

**验证** = 全库 125,426 键扫过 = **0 个脏候选还能被 `_pick` 选中**；正常词一个没误伤（「模糊→blur」「放屁→fart」「高马尾→high ponytail」都仍选到干净那条）。

---

## 关联

| 要什么 | 去哪 |
|---|---|
| 完整能力矩阵 + 四工作流路由 | `creative/yuer-image/references/模型路由与四工作流能力矩阵.md` |
| 畸形修法脚本 | `creative/yuer-image/scripts/yuer_ka_pai_zhi_chu.py` |
| 出图后验图 | `creative/yuer-image/scripts/yuer_verify_image.py` |
| LoRA 审计真值 | `creative/yuer-image/scripts/yuer_lora_audit.py` |
| 架构师正文 | `../templates/moody_moss_caption_zh.txt` |

