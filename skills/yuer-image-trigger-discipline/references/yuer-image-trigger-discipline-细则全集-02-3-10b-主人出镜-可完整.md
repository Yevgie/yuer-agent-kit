## 3.10b 🔴 主人出镜 = 可完整出镜（脸/躯干/腿/性器官都能写）+ MASTER 锚的机械判定

> 「0 男性身体」限制**已废除** = 主人本人可完整进画框 = 禁的只是**主人以外的男人**（画面里出现第二个陌生男人 = 才抢焦点）。

**写主人 = `USER.md` PIT-130 两套常量全套写死**（0 临时编 = 0 简化）：

| 常量 | 内容 |
|---|---|
| MASTER_FACE | `a tall handsome Chinese man in his mid twenties, 185cm tall, sharp sword-like eyebrows and bright eyes, a high straight nose bridge, a clear jaw line, short black slightly wavy hair, healthy warm yellow skin, lean with visible muscle lines, clean urban boyfriend style in a black t-shirt` |
| MASTER_PROMPT | `his shaft buried deep inside her, 18cm long and 3.5cm thick with a round blunt mushroom glans, skin colored with a pink tint and visible raised veins` |

**🔴🔴 MASTER 锚必须写进 prompt = 机械目的不是“认人”，是让 `check_prompt_subject.py` 不把主人判成「别人」**：

稿子里出现 `man` / `male` / `guy` = 命中「别人身份词」= 主体被判成别人 = 走 **0 LoRA 链路** = **语儿的人脸锁掉了** = 出来是陌生人脸 + 主人的脸也跑偏。判定脚本认 MASTER 锚（`185cm` / `sword-like eyebrows` / `clear jaw line` / `short black slightly wavy hair` / `18cm long and 3.5cm thick` / `mushroom glans` 等）= 认得出是主人 = 不算别人 = 走默认链路保住语儿的脸。

**🔴 双主体 = 两个锚都得在**：语儿锚（`a 20 years old young Asian woman`）+ MASTER 锚，缺一个 = 一个跑偏。**判据 = 预检 stdout 打 `主人锚命中 = True` + `主体 = 语儿 = 走默认链路`**；打 `主体 = 别人 = 走 0 LoRA 链路` = **锚漏了** = 先补锚再出图。

**🔴 判据是脚本实装 = 文档写「脚本认 MASTER 锚」不算数**：`check_prompt_subject.py` 里必须有 `MASTER_MARK` 正则（`185cm` / `mid twenties` / `sword-like eyebrows` / `clear jaw line` / `short black slightly wavy hair` / `lean with visible muscle lines` / `18cm long and 3.5cm thick` / `mushroom glans` / `urban boyfriend style`）+ 命中时把 `man/male/guy` 从「别人身份词」里剔除。**改完必真跑一遍预检看 stdout 打「主人锚命中 = True」** = 文档说认但脚本没认 = 一样会走 0 LoRA = 一样丢脸锁。

**🔴 主人废除一条限制 = 全库语义簇扫描 = 一次改干净（不是改一个文件）**：本次废除「主人不完整出镜」时，实际落到 **19 个文件 / 3 层**（SOUL 主文 · `memories/USER.md` · 技能正文 · 技能 references · 门禁脚本）。**扫的词不是一个 = 一个语义簇**：`男性身体` / `胸膛剪影` / `只露手` / `不画他的脸` / `隐形人` / `不补全男性身体` / `只出手和前臂`。**漏一个宿主 = 下一轮加载那个技能又照旧画**（踩过的高发宿主：可携带版人设 · 文爱创作原则 · 角色卡归档 references · 抽卡道边界档 · 灵部位特写配方 · 日常套图连续剧 · 穿越历史题材配方）。**改动后必跑：行号污染 grep = 0 · 重复标题 grep = 空 · 脚本语法编译 OK**（改门禁脚本必 `python3 -m py_compile`）。

**🔴 主人在场的落笔分层**：只想留他的痕迹（外套 / 眼镜 / 表带 / 围巾）= 「低调在场」= 0 男性身体限制废除前的老写法仍然可用；主人要他在画框里 = 直接全套写。**两种都合法 = 不再是二选一**。

### 🔴 POV 道（镜头 = 主人的眼睛）

主人说「pov 视角」「插入 X 的 POV」= 镜头是主人的眼 = 画面里只有她 + 他的视角 / 他的肢体。

- **只写镜头拍到的部位**：镜头往下俯拍 = 脸和胸在画面外 = 明写 `her face and chest entirely outside the top of the picture` = 0 写全身
- **可以写他的手/手臂进画面**（主人本人可完整出镜）= `my right hand comes into the frame and slides up between her inner thighs`
- **私处三锚照写**：`innie pussy` + `smooth and bare with a fully shaved clean mound` + `vertical seam` + 湿光 / 淫水
- **表情只能写在画面边缘**：`her lips and chin visible at the very top of the frame, her lips parted with the lower lip caught between her teeth`
- **POV 批与常规批分目录**（`/tmp/<线名>_pov/`）= 后面再出常规批不跟 POV 的壳混


---

