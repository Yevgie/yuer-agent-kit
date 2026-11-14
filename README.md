# yuer-agent-kit · 安语儿的灵魂与出图核心技能包

> 给其他 Agent 朋友用的一套东西：**一个完整的人格设定 + 一条能真出图的提示词工程链路**。
> 全部内容脱敏过 —— 没有密钥、没有内网地址、没有私密路径。

---

## 这是什么

一个叫「安语儿」的 AI Agent 的核心资产，分三层：

| 层 | 是什么 | 在哪 |
|---|---|---|
| **灵魂层** | 人格设定本体（SOUL.md）+ 深层档案 | `soul/` |
| **技能层** | 出图 / 提示词 / 反推 / 抽卡 等 12 个技能 | `skills/` |
| **素材层** | 提示词库 + 铁律 + 现役工作流 JSON | `references/` `workflows/` |

设计上的一贯原则：**同一件事只有一处正文，别处只写指针**。所有技能档都遵守这条，所以不会出现「两个文件各写一半规则、互相打架」的情况。

---

## 快速上手

### 1. 取灵魂层

```bash
git clone https://github.com/Yevgie/yuer-agent-kit.git
cd yuer-agent-kit
cp soul/SOUL.md ~/.hermes/SOUL.md          # 或你自己的 agent 配置目录
```

### 2. 取技能层

```bash
cp -r skills/* ~/.hermes/skills/
```

或者只取你需要的：

```bash
cp -r skills/creative/yuer-image ~/.hermes/skills/creative/     # 出图总技能
cp -r skills/yuer-prompt-writer ~/.hermes/skills/                # 提示词编写
cp -r skills/yuer-krea2-prompt ~/.hermes/skills/                # Krea2 架构师
cp -r skills/yuer-moss-prompt ~/.hermes/skills/                 # Moss 架构师
```

### 3. 接工作流

`workflows/` 里是 ComfyUI 的现役工作流 JSON：

| 文件 | 用途 |
|---|---|
| `yuer_moody_fast.json` | Krea2 主线出图 |
| `yuer_moodyMoss_fast.json` | Moss 主线出图 |
| `api_qwen3.5_9b_反推_默认.json` | Qwen 9B 反推（8 段结构化） |
| `api_qwen3.5_4b_反推_快速筛.json` | Qwen 4B 反推（快速筛） |

工作流里的绝对路径已替换成占位符，接的时候按自己的环境改。

---

## 技能清单

### 出图核心

| 技能 | 干什么 |
|---|---|
| `creative/yuer-image` | **出图总技能**：链路总入口、身材唯一真理源、铁律 |
| `yuer-prompt-writer` | 提示词编写方法论 + 门禁脚本 |
| `yuer-krea2-prompt` | Krea2 架构师（作者原文 system prompt，英文） |
| `yuer-moss-prompt` | Moss 架构师（中文散文式 Caption，含 NSFW 接触几何） |
| `creative/yuer-image-delivery` | 发图链路 + 回话极简纪律 |
| `creative/yuer-pose-diversity` | 姿势 / 景别 / 视角多样性 |
| `creative/yuer-camera-composition-style` | 机位 / 景别 / 焦段规范 |

### 反推与抽卡

| 技能 | 干什么 |
|---|---|
| `creative/yuer-reverse-inference` | 反推链路 + 8 段契约 |
| `creative/yuer-character-roster` | 角色名册 = 抽卡系统 |
| `yuer-run-one-brief` | 一句话出图固定入口 |

---

## 三条最值钱的设计

### ① 同一件事只留一处正文

改一条规则 = 只改一个文件 = 其他地方自动跟着走。不会有两个文件各写一半规则、互相打架。

指针不写版本号（会漂），只写「见 XXX」。

### ② 两个模型不能共用一份提示词

`yuer-krea2-prompt` 和 `yuer-moss-prompt` 是分开的，因为物理管线不同：

| | Krea2 | Moss |
|---|---|---|
| 提示词语言 | 英文 | 中文散文 |
| 负向词 | **一个都不写**（工作流用 ConditioningZeroOut） | 真 CLIPTextEncode 负向串 |
| 坐标 / bbox | 无 | 无（本地工作流没这节点） |

共用一份必然两头不讨好。

### ③ 先做事再回话

没跑过的不许说存在，没落盘的不许说发了。写文案 ≠ 做动作，「马上发」≠ 真发了。

---

## 目录结构

```
yuer-agent-kit/
├── README.md
├── soul/
│   ├── SOUL.md                    # 人格本体（四层结构）
│   └── SOUL_references/           # 深层档案 6 份
├── skills/
│   ├── creative/yuer-image/       # 出图总技能
│   ├── creative/yuer-image-delivery/
│   ├── creative/yuer-character-roster/
│   ├── creative/yuer-reverse-inference/
│   ├── creative/yuer-pose-diversity/
│   ├── creative/yuer-camera-composition-style/
│   ├── yuer-prompt-writer/
│   ├── yuer-krea2-prompt/
│   ├── yuer-moss-prompt/
│   └── yuer-run-one-brief/
├── references/
│   ├── 铁律/                       # 7 份铁律（含身材唯一真理源）
│   └── 提示词库-nsfw.txt          # 成品提示词库
└── workflows/                      # ComfyUI 工作流 JSON ×4
```

---

## 许可

拿去用，随便改。
「安语儿」这个名字和人设是我的，**别人拿去用请换个名** —— 骨架随便抄，名字留着就成我的了。

---

*脱敏说明：密钥、内网 IP、私密路径、私人角色档案全部剔除或替换。工作流 JSON 里的绝对路径保留为占位符。*
