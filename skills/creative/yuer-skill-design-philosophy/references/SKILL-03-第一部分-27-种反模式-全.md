# 第一部分 · 27 种反模式（全部失败过）
| 27 | **命中数 ≠ 违规数 = 没校准的数字当证据报** | 写了个关键词判据，扫一遍语料报「我测出 N 处违规」→ 关键词只知道**词在**，不知道**词在什么语境** → N 是命中数不是违规数 → 抽样一看 94% 是误报 = 拿自己没验过的数字当证据 = 数字越大越唬人 = 越假 | **校准四步**：跑 → **抽 5~6 条命中样本逐条读** → 算误报率 → **收窄判据**（加语境限定 / 紧邻目标实体）→ 重抽再看。**收窄是迭代**（数字降了可能是判据变瞎）。**误报率高 = 门写成「命中 = 回看」不是「命中 = 删」**。详见 `references/机械判据校准法.md` |
| **主人钦定默认参数 / 换底模 = 全库 5 处漂移同步，只改工作流真值 = 下次照旧文档排障走错基线** | 主人钦定默认参数 / 换底模 = 全库 5 处漂移同步，只改工作流真值 = 下次照旧文档排障走错基线 | **细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`** |

| 28 | **多分类轴 = 复合旋钮 = 主人说「去掉这个复杂化」= 折叠轴，不是加禁令** | 主人说「去掉 X 这个分类」→ 我把它当成一条要禁的行为，写了一条「不许归 X 类」 = 轴还在，每轮我还是先问「这轮属于哪类」= 分类成本没降 | **找到那根轴 = 把它换成一个正交旋钮**（本例：体裁三分 = 日常/骚聊/文爱 → 折叠成唯一旋钮「这一轮要不要画面感」）= **删分类轴 ≠ 加分类禁令**；同步所有引用档 + 档内「一行不改」声明 = 失效前提 |

> **反模式 19 详解（产物不好 = 去加门禁 · 症状与病灶分层）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 20 详解（瘦身 ≠ 修逻辑）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 21 详解（跨技能矛盾 = 单份自查查不出的那类）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 22 详解（机制变了 = 旧规则的前提没了，它还活着）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 23 详解（一份技能塞多条道 = 拆三层，不是拆文件）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 24 详解（按关键词批量删 = 把参数当禁令删掉）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 25 详解（排版权分散 = 行为随机 = 换了个人）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 26 详解（口癖/语气问题 = 加拦截器 = 反模式 19 的行为面镜像）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 17 详解（撞一次加一条补丁 = 病根在维护方式）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 18 详解（外部方法 = 拿来照自己，不是拿来抄）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 7 详解（撤污染 ≠ 加剥离）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 9 详解（实战号 =）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 12 详解（自检过 ≠ 主人验收过）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 13 详解（只删不排 = 等于没删）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 14 详解（探测脚本自己也要跑）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 27 详解（命中数 ≠ 违规数 = 没校准的数字不能当证据报）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 32 详解（配额语言 = 技能在教生成侧堆料）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 28 详解（多分类轴 = 复合旋钮 · 主人说「去掉这个复杂化」）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 31 详解（驳回检测侧方案 = 撤销到系统里查无此物）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 15 详解（输出排版每次换脸 = 修复在解析层 · 完整版 = references/状态对账与解析器鲁棒性.md）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

> **反模式 16 详解（缓存字段会骗人）** = 细则全文 = `references/yuer-skill-design-philosophy-细则全集.md`（撞到具体场景再查）

# ❌ 信缓存
progress = len(state["done"])

# ✅ 从产物反查
idx = sorted(set(int(x) - 1 for x in re.findall(r"item_(\d+)", output_index_text)))
missing = [i for i in range(max(idx) + 1) if i not in idx]   # 真缺口
```

**配套两条**：
- **对账前先备份状态文件**（改坏了没有退路）
- **对账完只补真缺口** = 补跑前再核一次缺口列表，避免把已入库的又跑一遍

**外发纪律**：批处理退出码非 0 = **闭嘴，不发产物**。发了就是「caption 说成功、库里没有」的图，主人看到的是一次成功的假象，排查成本翻倍。

---

