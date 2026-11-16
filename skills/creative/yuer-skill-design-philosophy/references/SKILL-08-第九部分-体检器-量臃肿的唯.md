# 第九部分 · 体检器（量臃肿的唯一量化入口）

```bash
S=~/.hermes/skills/creative/yuer-skill-design-philosophy/scripts/skill_audit.py
python3 $S --top 20              # 全库臃肿榜
python3 $S <skill_dir>           # 单份体检 + 逐段明细
python3 $S <skill_dir> --json    # 机读
```

**跨技能矛盾探针（反模式 21 / 22 = 体检器查不出的那一类）**：

```bash
C=~/.hermes/skills/creative/yuer-skill-design-philosophy/scripts/cross_skill_conflict_probe.py
python3 $C                                    # 动作 × 技能命中矩阵 + 重叠区硬约束行并排
python3 $C --skills a b c                     # 只比指定技能
python3 $C --matrix-only                      # 只看哪里重叠
python3 $C --topic 发图,洗图 --matrix-only    # 自定义动作词
```

命中矩阵告诉你**哪里重叠**（某一行 ≥3 份技能命中 = 重叠区），**对打点靠人读并排的硬约束行**——脚本不猜结论。

**🔴 增重闸（防继续无用增重 · 11-11 = 减负的另一半）**：

```bash
G=~/.hermes/skills/creative/yuer-skill-design-philosophy/scripts/skill_weight_gate.py
python3 $G --all                          # 全库扫（臃肿榜 + 红灯清单，退出码 1 = 有红灯）
python3 $G --all --baseline base.json    # 与基线比 = 净账（只能持平或下降）
```

**🔴 🔴 密度必须按「拆档族」算（拆档后不看这一条 = 满屏假红灯）**：

一个逻辑档被拆成 N 份 chunk = 每份的字数分母都变小 = **密度凭空翻 N 倍** = 内容一个字没加 = 闸子却报「你重点稀释了」。

**判据 = 拆档后密度红灯暴增 = 先看是不是拆出来的 = 对比拆前同档的密度（拆前 5.7 → 拆后 10.0 = 纯拆档副作用 = 不是内容坏了）**。
**正解 = 密度按族算**（`<stem>` + 同族所有 `-NN-slug` chunk 的字数与 🔴 合起来算）= 闸子已内置 `red_per_1k_family` = 单份报 `red_per_1k` = 族报 `red_per_1k_family` = **判定用后者**。
**同类陷阱 = 索引表把 chunk 标题里的 🔴 抄回父档 = 父档密度与考古占比同时翻倍 = 解法 = 索引表引用标题时剥掉标记词**（`yuer-skill-tidy` 的 `split_docs_lossless.py` 已内置 `sanitize_heading()`）。

**🔴 体积类红灯的处置顺序 = 先分「谁造的」再动手**：红灯来自**拆档副作用**（索引表回抄 / 标题自我重复）= 修索引表 = **0 动正文**；红灯来自**正文真密** = 才是要改写内容。**分不清就先去删正文 = 把唯一真源删了 = 不可逆**。

**🔴 闸子自己也要体检 = 「量的到底是什么」比阈值更重要（11-14 实测）**：闸子报的红灯里有一批是**假阳性** = 真病灶修完后红灯还挂着 = 主人看到红灯就麻 = 数字失去意义。

**🔴 三类假阳性 + 各自正解**：
- **考古行 = 履历叙事**：表格里的文件清单行 / 代码块里的命令 / frontmatter 的 description **都不是叙事** = 算进去 = 考古行虚高 = 红灯全靠误判撑着。**正解 = 考古行只扫正文**（跳过 frontmatter + 表格行 + 代码块）。
- **第三方档算我的账**：`github/` `research/` `mlops/` 等 = 作者不是我 = 我不维护 = 不该拿我的红线判它。**正解 = 第三方目录豁免**（跟「抄来的第三方技能不硬拆」同一条钦定）。
- **库外真值当库内**：`SOUL_references/xxx.md` = 真文件在 `~/.hermes/SOUL_references/` = 不是断链。

**🔴 判据 = 红灯从 26 → 0 是不是因为真病灶被修了**：真病灶修完红灯还高 = 去查**口径**（量的东西对不对），**0 改阈值**（阈值 = 规矩 = 动了就等于放水）。

**七条红线 + 豁免规则 + 减法三步 = 见第八部分之二。**

**🔴 红灯分两类 = 处置不同：体积类（行数/字数/🔴密度/版本号/考古行）= 慢慢砍；**功能类（description 无触发词 / 句尾截断 / Use when 重复）= 技能在列表里但永远不会被选中 = 静默失效 = 立刻修**。诊断 + 修法（触发词从该档正文搬 = 0 编）+ 批量改 30 份的五个坑（正则偏移切 frontmatter / 静默吃字段 / 只验改过的那份 / 忘了同步测试断言 / 顺手改 bundled 技能）= `references/description路由面修复-体检分诊与批量改程序.md`。

**整改终检探针（反模式 20 / 22 / 23 配套 = 一致性那一类）**：

```bash
D=~/.hermes/skills/creative/yuer-skill-design-philosophy/scripts/dead_rule_sweep.py
python3 $D <skill_dir> [...]           # 墓碑 / 悬空引用 / 编号断层 / 死规矩 / 可复制实体值
python3 $D --layered <skill_dir>       # 反模式 23：路由表深度 + 共核是否被各道复制
python3 $D --all                       # 全库扫一遍
```

体检器量**冗余**，这个脚本量**一致性** —— 两者都过才算整改完成，缺一都会漏。退出码非 0 = 有问题。

**改完设定 / 新建技能后「要不要重启」的判定法** = `references/改完设定要不要重启-生效路径判定法.md`
（🔴 **新 session 现读磁盘 SOUL.md = 不用重启**；旧 session 会从 `system_prompts` 表恢复旧字节 = **要开新 session 测**；新建技能 = `skill_manage` 已清索引缓存 = 不用重启。**「进程启动早于文件改动 ⇒ 必须重启」是过度结论。**）

**5 个指标**：字数/行数/标题数 · 重复标题组（去掉版本号后同名 = 只增不减的证据）· 重复段占比 · 履历段占比（「真根因/已落地/vs vX/关键差异」）· 不同版本号个数。

**健康线**：重复 0% + 履历 < 15% + 版本 < 5。超过 = 该瘦。
**只增不减的信号**：重复段 > 15% 或版本号 > 10。

⚠️ **体检器只出清单不出判决**——「删哪一段」仍要人（语儿）通读判断，它给的是量不是判。
