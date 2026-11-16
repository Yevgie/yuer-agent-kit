## 六 · POV 批次（镜头 = 主人的眼睛）= 只写画框拍到的部位

主人说「pov 视角」「插入骚穴 pov」= 镜头是主人的眼 = 画面里只有她 + 他的视角 / 他的肢体。

| 要素 | 写法 | 写错的后果 |
|---|---|---|
| **画框裁切** | 明写脸和胸在画面外：`her face and chest entirely outside the top of the picture` | 不写 = 底模给全身 = POV 感全失 = 变普通第三视角 |
| **他的肢体入画** | `my right hand comes into the frame and slides up between her inner thighs, my thumb pressing along the seam` | 禁写主人完整身体进 POV 画面 = 视角就破了 |
| **私处三锚** | `Her pubic mound is innie pussy, smooth and bare with a fully shaved clean mound, the inner labia small and pink and tightly closed into a neat vertical seam, clear fluid running down the inside of her thigh` | 漏 = 底模自由发挥 = 画成有毛 / 画成老阴 = 直接毁图 |
| **表情写画面边缘** | `her lips and chin visible at the very top of the frame, her lips parted with the lower lip caught between her teeth, her jaw set lightly` | 写完整表情 = 她脸不在画面里 = 矛盾 |
| **下装门禁** | 裸体 POV = 必 FAIL「下装」= 写**画外实物**：`a pair of white cotton briefs crumpled on the sheet beside her hip` | 写成她穿着 = 毁图 |

**🔴 POV 批次目录必须跟常规批次分开**（`/tmp/<线名>_pov/`）= 后面出常规批不跟 POV 的壳混 = 五张一锅端 = 场景串味。

**🔴 POV 批的机位 = 焦段固定短**（手机 1x 广角感 = `iPhone 15 Pro Max 1x lens at f/1.8`）= 视角贴得近 = 越向下俯 = 越像“他的眼睛”= 越骚。**别用 85mm 特写** = 那是第三人称摄影感。

---

## 七 · 主人出镜批次 = MASTER 全套 + 双锚判定

**「0 男性身体」限制已废除** = 主人本人可完整出镜（脸 / 躯干 / 腿 / 性器官）= 禁的是**主人以外的男人**。

**写主人 = `USER.md` PIT-130 两套常量全套写死**（0 临时编）：

| 常量 | 写进 prompt 的版本 |
|---|---|
| MASTER_FACE | `a tall handsome Chinese man in his mid twenties, 185cm tall, sharp sword-like eyebrows and bright eyes, a high straight nose bridge, a clear jaw line, short black slightly wavy hair, healthy warm yellow skin, lean with visible muscle lines, clean urban boyfriend style in a black t-shirt` |
| MASTER_PROMPT | `his shaft buried deep inside her, 18cm long and 3.5cm thick with a round blunt mushroom glans, skin colored with a pink tint and visible raised veins` |

**🔴🔴 MASTER 锚必须写进 prompt = 机械目的不是“认人”，是让 `check_prompt_subject.py` 不把主人判成「别人」**：
稿子里出现 `man` / `male` / `guy` = 命中「别人身份词」= 主体被判成别人 = 走 **0 LoRA 链路** = **语儿的人脸锁掉了** = 出来是陌生人脸。判定脚本认 MASTER 锚（`185cm` / `sword-like eyebrows` / `clear jaw line` / `short black slightly wavy hair` / `18cm long and 3.5cm thick` / `mushroom glans`）= 认得出是主人 = 不算别人 = 走默认链路保住语儿的脸。

**🔴 双主体 = 两个锚都得在**：语儿锚（`a 20 years old young Asian woman`）+ MASTER 锚，缺一个 = 一个跑偏。

**🔴 验收判据 = 预检 stdout**：打 `主人锚命中 = True` + `主体 = 语儿 = 走默认链路` = 对；打 `主体 = 别人 = 走 0 LoRA 链路` = **锚漏了** = 先补锚再出图。

**🔴 双主体图的构图铁律**：她的视线落点要写到他身上（`her gaze dropping to his belt buckle and then flicking up to his face`）= 她在勾引他不是在勾引观众；机位写「从她侧后 / 从下往上」= 保住「他的视角」= 不变成双人戏。**两个身体在同一画框 = 焦点只给一个 = 他的脸和她的脸不要在同一焦平面。**

**🔴 主人废除一条限制 = 全库语义簇扫描（不是改一个文件）**：本次废除「主人不完整出镜」实际落到 **19 个文件 / 3 层**（SOUL 主文 · `memories/USER.md` · 技能正文 · 技能 references · 门禁脚本）。**扫的不是一个词 = 一个语义簇**：`男性身体` / `胸膛剪影` / `只露手` / `不画他的脸` / `隐形人` / `不补全男性身体` / `只出手和前臂`。**漏一个宿主 = 下一轮加载那个技能又照旧画。**

**高发漏宿主清单**（本类全库扫描必扫）：可携带版人设 · 文爱创作原则十五条 · 角色卡归档 references · 抽卡道与出图道两套规矩边界档 · 灵感复刻档 · 局部特写与微距配方 · 日常套图生活连续剧 · 明快日常档 ins 配方 · 穿越与历史题材配方 · 灵魂脸前缀档案。

**改动后必跑三项体检**：行号污染 `grep -cE '^[0-9]+\|' <file>` = 0 · 重复标题 `grep -n '^## ' <file> | sort -k2 | uniq -d` = 空 · 改到门禁脚本必 `python3 -m py_compile` OK。


---

