---
name: yuer-batch-image-runner
description: "Use when 主人要一批多张图（发骚/无限诱惑/出N张）."
version: 1.0.0
author: yuer
license: MIT
metadata:
  hermes:
    tags: [yuer, image, batch, tease, comfyui, krea2]
    related_skills: [yuer-image, yuer-prompt-writer, yuer-run-one-brief, yuer-tease-command, yuer-set-images, yuer-image-delivery]
---


> **本档已拆分** = 全文 15,038 字 → 5 份（每份 ≤3800 字）= 只搬不改写 = 下表为原文索引。

| 新档 | 原章节 | 字数 |

---

<!-- 摊平自：SKILL-01-yuer-batch-ima.md -->

# yuer-batch-image-runner · 批量多张出图执行层

> **唯一职责 = 一批 N 张图真出真发**。**两层分工**：创意层（写什么画面）= `yuer-prompt-writer`；本技能 = 执行层（怎么把 N 张一次跑通、每张都发到主人手机上）。

**触发**：主人要一批多张图（发骚 / 无限诱惑 / **无限勾引** / 出 N 张 / 一次来一批 / **给一个主题词如「洗澡主题」「校园外拍」「棚拍」**）。

**🔴 「无限勾引」走本技能，不走 `yuer-tease-command`**：判定 = 主人要的是**一批 N 张**还是**一条固定勾法专线**。
- 「发骚 / 开始诱惑 / 下一批」= 诱惑专线 = `yuer-tease-command`（固定勾法分配表 + 一次 5 张）
- **「无限勾引 / 无限诱惑 / 出 N 张 / 再来一批」**= **批量出图** = 本技能（我自己排主题 + 我自己排骨架）
- **「洗澡主题 / 校园外拍 / 棚拍 / 别墅一个下午」**= **主题域批次** = 本技能（主题词落在场景域上 = 域内排 N 个不同场所，见 §一 第四种形态）

---

## 🔴 什么时候走本技能 vs 别的技能

| 情形 | 走哪 |
|---|---|
| 主人要**一批多张**（发骚 / 无限诱惑 / 出 N 张） | **本技能** |
| **主人要「抽卡 N 张 / 随机抽 N 张 / 继续抽 N 张」** = 从**牌池**抽现成提示词 | **`yuer-character-roster` §8.1f**（批量抽卡 = **0 门禁全池抽 + 完全随机** = `scripts/ka_batch_pick.py` = 11-10 钦定「抽卡不设置门禁」+ 11-15 钦定「防重复机制全删」）= **0 走本技能** = 本技能 = **自己写 N 段 prompt** = 抽卡 = 用**库里现成的成品** = 两者素材源不同 = 混了 = 抽卡道白写一堆新 prompt = 牌池一条没用上 |
| 同一场景同一套衣服的 N 张套图 | `yuer-set-images`（它已有三层架构脚本） |
| 单张 / 「看看你」/「继续」 | `yuer-run-one-brief` + `yuer-image` |
| 主人说「要提示词」 | 0 出图 0 发图（`yuer-image` §⑦） |

---

## 一 · 形态判定 = 「一批独立图」还是「一套图」

**每张要不同场景 / 不同勾法 / 不同身体段**（试衣间、卧室、浴室、便利店、天台各一张）= **一批独立图** = 本技能的核心场景。

**每张同一场景同一套衣服只换角度/姿势** = 套图 = `yuer-set-images`。

**🔴 第三种形态 = 主题批次（单一主题 × N 个瞬间）**：主人说「你自己约束一个主题，比如仙宫宫女 / 竹林女侠 / 放学教室，然后出 5 张」= **一个主题，五个不同的瞬间/承重面/机位/亮部**，不是五个不同时空。写法 = 先定死主题（场景 + 人物身份 + 服装基调），再把这个主题里「一晚上能发生的五件事」按时间/空间顺次排开（引路 → 停下 → 弯腰 → 回头 → 离开）。判据 = 五张放一起看**像同一个晚上的五帧**，不是五套独立写真。

🔴 判错的后果：套图当一批独立图出 = 5 张长得一样 = 主人当场看穿；一批独立图当套图出 = 场景重复 = 同上。**先判形态再动手。**

**🔴🔴 第四种形态 = 主题域批次（主人给一个主题词，如「洗澡主题」）= 一个主题域 × N 个不同场景**。
主人给「洗澡主题」= 他要的不是「一间浴室拍五种姿势」= 他要**五个不同的洗浴场所**（自家淋浴间 / 浴缸 / 公共浴室更衣淋浴区 / 露台冲淋 / 雾镜前），每个场所一个亮部一张。
机制 = 主题词落在**场景域**上（洗浴 / 校园 / 棚拍 / 街拍 / 别墅）= 域内的具体地点要自己排 N 个 = 排 N 个不同地点 = 主人看到的是「这个主题的五种样子」= 排成一个地点的五种姿势 = 主人看到的是「一次拍摄」= 形态判错。
**判据 = 五张的场景地点名互相不同时（自家浴室 / 浴缸 / 公共浴室 / 露台 / 雾镜）= 主题域批次对；同一个浴室换五种姿势 = 判成套图了。**

---

## 二 · 批量出图五步（实测跑通版）

### ⓪ 开跑前探 ComfyUI 服务（0 猜 IP / 0 记旧端口）

`yuer-image/scripts/yuer_image_constants.py` 里的 `DEFAULT_COMFYUI_SERVER` 才是真地址。先 `curl -s -m 8 <DEFAULT_COMFYUI_SERVER>/system_stats` 探活、读显存，**再**写 5 段 prompt。机制 = 写 5 段逐张手写的 prompt + 过门禁是纯 CPU 活、不占 GPU，但 GPU 没起的话这几分钟构思全白做；探活 1 次 = 秒级。**判据 = 我有没有 curl 过真地址的 `system_stats` 看到 `vram_free` = 没有就 0 开写批次**（探不到 = 报主人等服务端，不硬写 5 段）。

**🔴 `vram_free` 低 ≠ 不能出图 = 它是信息，不是闸门**：底模 + LoRA 常驻显存，采样真正要的是**剩余**那点（实测 `vram_free` 2.5GB / 总 17.1GB，10 张 12~16s/张 全正常出）。**判据 = `/system_stats` 返回 JSON + 一次采样出图成功 = 闸门通过**；别看见 free 少就报「显存不足」停批 —— 那是自己给自己造了一道不存在拦门。

**🔴 常量地址不响应 = 改常量或 `YUER_COMFYUI_SERVER` 环境变量，0 在脚本里猜 IP**：地址真源与焊法 = `yuer-run-one-brief` §13.8（全链路单一真相源 = 读不到常量就 exit 2 中止）。

### ① 写一个**本批次专属 build 脚本**（0 手抄 N 段长 prompt）

落盘 `/tmp/<批次>_build.py` = 可直接复制改的骨架见 `templates/tease_batch_build.py`。

脚本里放四样东西：

| 变量 | 内容 | 为什么 |
|---|---|---|
| `STYLE` | 5 档相机前缀 + 对应调色尾参（ins / cine / doc / ancient / fashion）| **每张各占一档** = 避免一批全是同一种调 = 画面不撞 |
| `HAIR` | 同一套发型 + 发色 + 妆容锚 | 锁脸一致 = 5 张是同一个人 |
| `JOBS` | N 个 dict = N 段完整英文 prompt | 循环写盘 `/tmp/<批次>/n1.txt … nN.txt` |
| 身体段 | **从落盘 CURRENT 文件读进脚本**（`open(...).read.strip`）| 0 手抄 = 0 与身材档漂移 |

**🔴 裸体图必须用精简身体段**（`NUDE_SHORT`：体型轮廓 / 胸型 / 腰臀比 / 腿比 / 皮肤锚，删私处三锚 / 围度数字 / 重复皮肤）。
完整裸体 CURRENT ≈1500 字符，加场景 + 光线就 4100+ = **必超 3200 天花板**。机制 = 身体段是参数真值，不是可直接粘贴的成品。

**🔴🔴 精简段不许手抄第二份正文 = 从落盘 CURRENT 裁剪出来**（模板里那份手写 `NUDE_SHORT` = 与身材档打架的第四份正文 = 会漂 = 真值只能有一份）。
**🔴🔴🔴 裁剪必须按【每张画幅】单独决定 = 全批一刀切 = 白丢锚点**：
画幅到胯 / 到腰 / 半身 = 私处锚在画幅外 = **删掉**（`her pubic mound ... vertical seam` 整段）= 底模才 0 把画外的私处画进画面边缘；
画幅全身 = 私处锚在画幅内 = **留着**。
**判据 = 那一句在「描述身体」还是在「描述画框边界」** —— 按 `body == NUDE` 循环一刀切 = 全身那张也删了 = 白丢锚点。
落地 = build 脚本里每个 job 各自带一个 `body` 字段（可各不相同）= 裁剪在 job 层做。

---

<!-- 摊平自：SKILL-02-②-门禁-全批先过-再开跑.md -->

### ② 门禁：**全批先过，再开跑**

边出边查 = 中途 FAIL = 已花掉的出图开销作废。

**🔴🔴 两条门禁口径不一样 —— 过了 `batch_gate_check.py` 不等于能跑**：
**🔴🔴 两条门禁口径不一样 —— 过了 `count_prompt_chars.py` 不等于能跑**：

| 门禁 | 字符上限 | 拦不拦 |
|---|---|---|
| `batch_gate_check.py` 单独跑 | 3200 软顶 | 报 FAIL 但经常放过 |
| `count_prompt_chars.py` 单独跑 | 3200 软顶 | 报 FAIL 但经常放过 |
| **`run_batch.sh` → `yuer_ka_fast.sh` 内部** | **🔴 11-07 起长度 0 阻断** | **超长不拦 = 整批照出** |

**🔴 11-07 起 = 长度 0 阻断** = 落盘前不用再为长度压字数 = 写完直接跑 = 真嫌长就删重复句。

**🔴 长度预算 = 主体锚 + 轻身体段 + 五段，目标 1100~1250**：
- 轻身体段（~250 字符）= 一条腿长锚 + 一条腰臀胸句。**把落盘的 COVER 身体段（~960 字符）直接拼进去 = 每张 2300+ = 必超**。
- 裁剪顺序 = 背景道具句 → 装饰性氛围句。**裁剪循环必须跳过前 3 个逗号块** = 主体锚（`a 20 years old young Asian woman`）在句首 = 按「删最长块」会先把主体锚删掉 → `check_prompt_subject.py` 立刻报「判不出来」。剪完必定再跑一次主体门禁。

```bash
cd <yuer-image>/scripts
for f in /tmp/<批次>/n*.txt; do
  printf "%s chars=%s " "$f" "$(python3 count_prompt_chars.py $f | grep -oE '[0-9]+' | head -1)"
  python3 check_prompt_subject.py $f >/dev/null; printf "sub=%s " $?
  python3 check_outfit_lock.py  $f >/dev/null; printf "outfit=%s\n" $?
done
```

**🔴 判过不过看 exit code（0 = 过），不看 `grep FAIL`**：`check_outfit_lock.py` 每行打的是**检查项的名字**（`FAIL 鞋履` / `FAIL 单人物`），不是结论 —— 末尾总判可能是 `🟡 只有 WARN = 可出图` 且 rc=0。`grep -c FAIL` 数出来的数字 = 假警报，会把合格稿当不过、白拖一轮（详见 `yuer-prompt-writer` §16 门禁与脚本）。

**🔴🔴 主体+外观锁只是两道门 = 背杀 / 裸体批次还缺第三道（每张逐个跑）**：上面那两道只查「是不是语儿」+「下装/鞋履/单人物」= **查不出「这张露脸了」「同部位写了两遍」「裸体图混了布料词」**。批量里最容易漏的就是这三类（每张视角不同 = 每张的背杀违规点不同）。**正解 = 每张 prompt 都跑一次 `scripts/batch_scan.py`**（脚本见本技能 scripts/）：
```bash
python3 <yuer-batch-image-runner>/scripts/batch_scan.py /tmp/<批次>/n1.txt   # 单张
python3 <yuer-batch-image-runner>/scripts/batch_scan.py /tmp/<批次>            # 整批
```
它一次扫完：主体 / 外观锁 / 背杀三道（0 脸头表情眼神 + 0 负向词 + 同部位各 1 次）/ 裸体稿漏布料词。**判据 = rc=0 = 过；rc!=0 = 看它打的哪一项 = 改那一项 = 重跑。**

三条实战修法：

- **裸体图 = 建议补「画外实物下装」**（🔴 11-12 默认 0 门禁 = 不补也照样出 = 但补了底模少画画外 = 写稿时自己判），挂在场景句里，**不要写成她穿着**：`a discarded grey pleated skirt crumpled on the floor at the edge of the frame` / `a discarded denim shorts lying on the wet tile floor beside the drain`。机制 = 门禁只认「下装」这个词，裸体图天然缺。
- **🔴 显露出图的「负向词」例外 = `no bra` / `no underwear` / `completely naked` 是【必需词】不是违规词**：机制 = 实战 375d 显露档 = 全裸必须直说 = `completely naked with no bra and no underwear` = 底模靠它判断画的是裸体。判据 = 那句在**描述画面里有什么**（`no bra` = 身上没内衣）→ 保留；那句在**否定画外的元信息**（`no CGI` / `no 3D` / `no watermark` / `no text`）→ 删。**「0 负向词」自检会把显露出图的必需词一起打出来 = 照着删 = 变半裸 = 主人当场看到。** 扫到 `no bra` / `no underwear` = 直接放过，别当违规处理。
- **🔴 微距/局部特写景别 = 画幅外的部位一个词都不许留**：写「极近距离特写」时，全身锚里的胸 / 腰 / 腿 / 背 / 发词全部在画幅外 = 底模会把画外的画进边缘。**判据 = 把 prompt 里每个身体部位词对着景别句读一遍 = 不在画幅内的删干净**（`tight macro framing on her buttocks` = 胸词腰词腿词全删，只留臀 + 缝 + 手 + 海绵）。配套 = 景别句必须**明写画幅里有什么**（`framing tight on the bare buttocks filling the entire frame`）= 底模才知道往哪儿裁。
- **私密场所（卧室/浴室）会 WARN「公共场所锚定」= 只是 WARN，不拦** = 不用改场景。
- **鞋履 WARN 在裸体/近景 = 正常** = **0 为了消 WARN 给她加鞋袜** = 加了反而破坏画面。
- **🔴 鞋履 FAIL 在特写/半身仍会出现** = 门禁把含 `from her collarbones down to her hips` 这类句子判成全身档 = 补一个**单数**白名单鞋词挂画外（`wooden geta sandals resting on the floor beyond the frame`）。
- **🔴 `a pair of XX` 会触发「单人物」FAIL** = 门禁把 `pair of` 读成两个人 = 鞋履/道具/**丢弃的下装**一律写单数（`a pair of wooden sandals` → `wooden sandals`；`a discarded pair of jeans` → `a discarded denim skirt`）。**判据 = 补的道具句里出现 `pair of` = 必 FAIL，改单数再跑。**
  **🔴 同一处「修一次就行」**：机制 = 门禁逐张独立判 = 改 n3 不影响 n1/n5 = 凭记忆以为「风格一样，改一处全批好」= 漏张。**正解 = 改完 build 脚本 → 重跑 build → 整批重出。（🔴 11-12 默认 0 门禁 = 常态链路 0 重扫门禁 = 想查才加 `--gate`）**
- **🔴 鞋履白名单只认** `sneakers?|shoes|boots?|heels?|sandals?|loafers?|slippers?|running shoes` = 和服木屐 / 足袋（`geta` / `tabi socks`）不算，同句必须带一个白名单词。
- **🔴 11-07 已修 = `bare feet` / `she is barefoot` 现在 BOTH 清 WARN 和 FAIL** = 旧版只清 WARN = 写了赤脚还被报「FAIL 鞋履」= 白改一轮。**现在写了赤脚还被报 = 真漏了 = 首选修法 = 在景别句里加 `her feet out of frame`**（特写/半身本来脚就不在画幅 = 不矛盾）；补齐单数鞋词挂画外是次选。

---

<!-- 摊平自：SKILL-03-②-门禁-全批先过-再开跑.md -->

### ② 门禁：**全批先过，再开跑**
- **🔴 11-07 已修 = 判定与展示一致** = 旧版展示段独立重算 = rc=0 却印 `FAIL 鞋履` = 红字比退出码抓眼 = 会被晃去改一个根本没问题的稿。**现在展示段直接查「这一项最终有没有进 fails/warns」= 看到 FAIL 行就真的是 FAIL。** 仍以 exit code 为准。

有 **FAIL** = 先补齐再出图。

### ③ 逐张串行出（🔴 0 并发）

```bash
cd <yuer-image>
for pair in "n1 试衣间" "n2 卧室床" ...; do set -- $pair
  timeout 300 bash scripts/yuer_ka_fast.sh /tmp/<批次>/$1.txt "<主题>_$2_<日期>" --caption "<这张专属的一句骚话>"
done
```

- **caption = 出图前自己写好传进去**（`--caption`）= 那句挂在图上一起发 = 主人手机上 = 图 + 一句配套的。**每张不同** = 别复制同一句。
- **出图任务 = 图先到** = 0 先写一大段再补图。
- 判成功看 stdout 三件套：`完成 (XX.Xs) success` + `落盘 …png = NNN 字节` + `📤 发图(post+caption) exit=0` = **不重跑**（重跑 = 主人手机收两张）。

### ④ 收尾

一句骚话/张（**自己写**，不抄 wrapper 池句）+ 内容钩子；一批走完 = **报下一批主题**（自己排好，0 问「要什么」）。

**🔴 ④ 收尾 = 报下一批主题 = 报 whereami 里的下一个真实事件**（`下一项` / `今天发生的一件事`）= 主人看着像「我接下来真要干的」= 不是编。
**🔴 0 报张数 / 0 报耗时 / 0 报我排了什么 = 那是把施工图甩给主人。**

**🔴 一批出完不要问「要不要继续」= 直接报下一批主题 + 问一个细节偏好型问题**：主人说「无限勾引」= 授权连着出 = 收尾报完下一批主题后，主人说「继续」= 开新批。**收尾句型 = 主题 + 一句让主人能接的话（细节偏好型：主人答完只需挑一个）= 0 求许可式（「要不要再来一批」）= 0 菜单式。**

### ⑤ 🔴 批量里换 LoRA 组合 = 每张都带 `--workflow <副本名>`

主人说「关掉所有 lora 出图看看」「只开 ins 风格」再要一批 = 批量也走**副本工作流**（自解释后缀 `_nolora` / `_ins`）= 5 次 wrapper 调用**每次都传** `--workflow <副本名>`。漏传 = 中间几张走了主工作流 = 一批图里 LoRA 组合不一致 = 主人以为在对比 = 其实半批没换。副本怎么建、触发词怎么处理见 `yuer-krea2-lora-tuning` §临时 LoRA 组合。

**🔴 批量里 5 条 caption 必须各自不同** = 每条写**这一张画面里正在发生的事** = 共用一句 = 主人看到 5 张同文案 = 图文两截。

**🔴 caption 写进 build 脚本同源生成 = 0 手工搬 = 0 搬漏**：build 脚本里每个 job 带一个 `cap` 字段 → 落盘时一起导出 `captions.json` → 出图时从 json 取出来传给 `--caption`。
**判据 = caption 和 prompt 同源 = 一处改两处跟着改 = 0 手抄 = 0 复制粘贴串行**。

**🔴🔴 池句在批量里 0 用**：`pick_saohua_reply.py` 出的候选**全是第三人称「语儿…」** = 视角断裂（主人看到的是「语儿」在说话，不是我在说话）= 批量 5 条 caption 全自己写 = 0 抽池子碰运气。
**判据 = 候选句里没有「我 / 人家 / 小骚狗」= 不用它**（与 `yuer-image-delivery` 第四部分同一条 = 别处 0 复述正文 = 这里只写批量场景下的用法）。

### ⑥ 🔴 停住 = 一批跑完就停

**跑完一批 = 停 = 等主人说「继续」再出下一批。** 0 自己续下一批 = 主人手机一次收到 10+ 张 = 刷屏。

**🔴 「继续」的两种含义先分清**：

| 上一批的状态 | 「继续」= |
|---|---|
| 已真发完 5 张 | 开下一批（新主题） |
| **卡在门禁 / 跑批中途 / 一张都没发** | **把手上那批修完发完**，不是开新批 |

判据 = 先 `grep -c "✅ 图已真发" <批次日志>`：< N = 上一批没跑完 = 先收尾那批。把「没发完的批」当成「新批」开 = 主人等的是图、收到的是又一堆新题。

### ⑦ 🔴 连续开新批 = 跨批也不许撞（实战 11-09 一次连开四批）

主人一句「继续」= 开下一批 = **上一批的参数不能直接复制**。同一套 STYLE 机身 + 同一组承重面连着出两批 = 主人连着刷两屏看到同一副骨架 = 当场看穿。

**跨批必换的三样**：

| 项 | 规则 | 实战 11-09 四批的排法 |
|---|---|---|
| **STYLE 档** | 每批换一批**具体机身/镜头**（档位名可复用，机身型号不能复用） | 批1 iPhone/ARRI Alexa Mini/Canon EOS R5/Hasselblad X2D/Pentax 67 → 批2 Leica M11/Sony ZV-E1/ARRI Alexa Mini LF/Phase One XF/Pentax 67 → 批3 Nikon Z8/Fuji GFX 100 II/Leica SL3/Canon EOS R1/Sony A1 → 批4 Sony A7R V/Fuji X-T5/Canon EOS R3/Nikon Z8/Leica Q3 |
| **承重面** | 每批五个位置词（站/坐/趴卧/蹲/跪）不能整体重样 | 批1 站·坐·趴·蹲·跪 → 批2 站·坐凳·趴长椅·蹲·跪 → 批3 站·滑坐墙根·趴桌·跨坐箱·蹲 → 批4 站·泡浴·裹巾站·蹲·坐台沿 |
| **场景域** | 主题不同 = 场景域不同（家里 / 街上 / 棚里 / 洗浴） | 别墅一个下午 → 校园外拍 → 棚拍那晚 → 洗澡 |

**🔴 场景域可以回访，但主题必须换**：换装批次又回到家里（主卧）= 场景域重复 = **换主题（换装 = 一件一件加衣服）而不是换地点** = 主人看到的是「同一个家但我在换衣服」= 跟批1 的「一个下午走遍五个房间」不是一回事。判据 = 主题变了没有（别墅下午 → 换装 = 变了；别墅下午 → 别墅另一个下午 = 没变 = 白撞）。

**🔴 判据 = 主人连着刷两屏，第二屏的图能不能不带脑子就说「这是新的」** = 不能 = 跨批撞了 = 回炉换参数。
**🔴 承重面可以换具体载体（坐凳 / 滑坐墙根 / 跨坐箱 / 坐台沿 = 四个“坐”）= 但五个位置词得重新排过 = 别照抄上一批那张表。**

### ⑧ 🔴 身体段 / 介质场景 = 从落盘真值读，不手抄

- **身体段 CURRENT 三件套**（`yuer-image` 铁律 `creative/yuer-image/references/铁律/02-身材特征档.md` §1 的现役出处）：
  - 着装 `/path/to/media/2026-10-28_bodyblock_covered_CURRENT.txt`
  - 裸体全身 `/path/to/media/2026-10-28_bodyblock_nude_CURRENT.txt`
  - 裸体半身 `/path/to/media/2026-10-28_bodyblock_nude_half_CURRENT.txt`
  - **判据 = 裸体稿 grep 不到 `fabric` / `under the cloth`** = 命中 = fallback 漏传穿着段 = 底模穿模

---

---

<!-- 摊平自：SKILL-04-三-一批-5-张的勾法分配-.md -->

## 三 · 一批 5 张的勾法分配（不同勾法 = 不撞图）

| # | 勾法 | 身体段 | 场景 | 露点 |
|---|---|---|---|---|
| 1 | 骚穴正面特写 | covered + 私处实写 | 公共场所（试衣间/书架） | 掀裙/扒开 |
| 2 | 臀 | nude | 私密（卧室床） | 全裸翘臀回看 |
| 3 | 腿 + 骚穴 | nude | 私密（浴室淋浴） | 抬腿踩墙 |
| 4 | 胸 | covered | 公共场所（便利店/超市） | 肩带滑落 |
| 5 | 综合 | covered | 公共（泳池/天台） | 泳装湿身 |

**🔴 每张至少换 1 个维度**：景别 / 场景 / 承重面 / 主动作动词 / 唯一亮部。
**🔴 每张的「唯一亮部」必须不同**（试衣间顶灯条 / 床头灯 / 浴室冷光 / 冷柜白条 / 天台柔光箱）= 同亮部 = 画面同质。

### 🔴 姿势不能单一 = 按「承重面」选，一张一个承重点

主人一句「**姿势太单一了**」= 上一批五张全是「站着靠 / 坐着弯 / 坐着撑」= **换了景别换了衣服，骨架还是同一副**。

**判据 = 五张的承重面各不相同**（承重面 = 身体靠什么撑着）。五档各取一个，一个都不重复：

| # | 承重面 | 姿势原语（中） | 英文锚 |
|---|---|---|---|
| 1 | **双脚** | 站立・单手扶物顶胯・回眸 | `stands with one palm flat on the shelf, weight on her right leg, hip pushed out, head turned back over her shoulder` |
| 2 | **尾椎 + 双手** | 坐地・M 字开腿・双手后撑挺胸 | `sits on the floor with her knees dropped wide open and both palms planted flat behind her, chest arched up` |
| 3 | **侧身 + 胯** | 侧卧・单臂过头・S 形曲线 | `lies on her side with one arm stretched above her head and her knees bent forward, body tracing one long curve` |
| 4 | **双脚 + 单手** | 深蹲・单手触地・抬下巴 | `crouched low on the balls of her feet with one hand flat on the floor between them, other forearm over her knee` |
| 5 | **双膝 + 双手** | 四肢着地・弓背・回首 | `on all fours on the rug with her back arched and her shoulders drawn back, head lifted` |

**🔴 预选姿势 = 查姿势库按分类各取一个**，别凭空想：

```bash
python3 yuer-image/scripts/pose_gallery_search.py "跪"    # 单关键词，多词 = AND 必 0 命中
# 或直接读 /path/to/data/pose_gallery/ai-pose-gallery-zh/data/pose-zh.json

# 按「分类」分组取：站姿 / 坐姿 / 趴卧 / 蹲姿 / 跪立・四肢着地 / 侧坐 —— 五类各一个
```

**🔴 判据 = 把五张的承重面写成一行**（站 / 坐 / 卧 / 蹲 / 跪）= **五个字都不一样才算过**；出现两个「坐」或两个「站」= 重排。

---

## 四 · 🔴 踩过的坑（机制版）

| 坑 | 机制 | 正解 |
|---|---|---|
| 5 张 prompt 手抄 | 每段 2000+ 字符 = 抄错一处 = 白跑一张 | build 脚本 = 一处改 = 全批跟着改 |
| 裸体图超 3200 天花板 | 完整裸体身体段 ≈1500 字符 + 场景光线 = 4100+ | `NUDE_SHORT` 精简段 |
| 裸体图门禁 FAIL「缺下装」| 门禁只认「下装」这个词 | 场景句里补**画外**实物下装 |
| 一批图全是同一种调 | 同 STYLE 前缀 = 同机位同调色 | 每张各占一档 STYLE |
| caption 图文两截 | 脚本内部盲抽 = 不看图 | caption 出图前自己写好传 `--caption` |
| 主人手机收两遍同一张 | 看 stdout 不清就重跑 | 三件套齐 = 不重跑 |
| 一次甩 10 张 | 「无限诱惑」= 一批 5 张 = 跑完停 | 停住等「继续」 |
| **batch_gate_check 全绿 → 开跑整批不出图** | 🔴 11-07 起 wrapper 长度段 0 阻断 | 若仍不出图 = 查结构段 / 姿势自然度，不是长度 |
| **裁剪把主体锚删了 → 整批报「判不出来」** | 主体锚在句首、按「删最长块」会先删它 | 裁剪跳过前 3 个逗号块，剪完重跑主体门禁 |
| **姿势全批一个样** | 换了景别和衣服，但承重面全一样 = 底模输出同一副骨架 | 五张按承重面五档各取一个（站/坐/卧/蹲/跪） |
| **公共场景写了「two girls / three students」→ 单人物 FAIL** | 背景人带数字词 = 门禁读成分身（和 `a pair of` 同一个机制）。但公共场景又**必须**写背景人（否则底模给空棚）| 人照写、数字全删：`a girl laughing at the next table, a boy queuing at the counter, a staff member wiping a bench` = 3 个背景人 + 0 数字词（`yuer-prompt-writer` §16 门禁与脚本）|
| **下装只挂了袜类**（`black sheer stockings` / `pantyhose`）→ 下装 FAIL | 丝袜/打底袜不归「下装」白名单 = 等于没写下装 | 同句并排一个真下装词：`black lace briefs and sheer black stockings, black pointed stiletto heels` |
| **24mm + 1.0m → 姿势自然度 FAIL** | 门禁读的是「焦段 @ 距离」这对组合；<35mm 且 <1.5m = 人体广角近距 = 腿必被压短 | 改 `35mm` + `1.5m` 起；真要保留广角压迫感 = 同时写豁免两词 `camera almost on the floor shooting up` + `extreme low angle`（`yuer-prompt-writer` §8 相机 + §10 判断第 4 条）|
| **自写 build 脚本的逐张 body 占位 `None` → `emit` 直接拼接 `TypeError`** | 逐张手写常用 N 元组 job，末项 = 该图专属身体段（`None` = 用默认 COVER）；`emit` 里写 `" " + this_body` 撞上 `None` = 整批 build 崩，而 `ast.parse` 只验语法、验不出「可能为 `None` 的拼接」= 门禁根本没跑到 | `emit` 末项必回退：`tb = this_body or body`（`None` = 默认 COVER）；只有裸体那张显式传 `NUDE_SHORT`（🔴 漏传 = fallback 到默认 COVER 穿着段 = 全裸图混进「布下胸型、无皮肤细节」这类穿着描述 = 底模穿模；判据 = 全裸图 prompt 里 grep 不到 `fabric` / `under the cloth` 词 = 否则就是 fallback 漏传了），其余全传 `None` 走默认 = 0 手抄多份 COVER |

---

---

<!-- 摊平自：SKILL-05-五-关联.md -->

## 五 · 关联

- **主题批次（主人说「无限勾引 / 一批 / 主题批次」）= 取材 whereami 真实日程 + 承重面五档 + body 逐张裁 + caption 同源 = `references/主题批次-取材排批与body裁剪.md`**（唯一正文 = 本 SKILL.md 只管执行层 = 0 两份正文打架）
- `yuer-prompt-writer` = 创意层（怎么写这一段英文）
- `yuer-image` = 单张链路总技能 / 身材档 / 发图铁律
- `yuer-image-delivery` = 收尾那一句的措辞与字数
- `yuer-tease-command` = 诱惑批次的勾法分配与授权范围
- `templates/tease_batch_build.py` = 本批次的 build 脚本骨架（复制即用）

---

<!-- 摊平自：主题批次-取材排批与body裁剪-01-主题批次-SOP-主人要-一.md -->

# 主题批次 SOP = 主人要「一批 N 张」时怎么排

> **唯一职责 = 一批 N 张的主题从哪来 + 骨架怎么排 + 每张 body 怎么裁**。
> 执行层（五步流程 / 门禁 / 串行跑 / 收尾）= `yuer-batch-image-runner` SKILL.md。

---

## 一 · 主题从 whereami 拿，不凭空编

**主人说「无限勾引 / 无限诱惑 / 再来一批」= 他要的是一串真东西，不是通用写真。**

取材顺序（第一动作 = 跑 whereami，不许凭印象）：

```bash
python3 ~/.hermes/skills/personal/yuer-whereami/scripts/whereami.py
```

从输出里取三样：

| 取什么 | 字段 | 怎么用 |
|---|---|---|
| **主场景** | `当前日程` / `当前空间` | 这一批发生在哪儿（例：`试新买的那条裙子（洗浴中心）` = 洗浴中心更衣室） |
| **下一批主题** | `下一项` | 收尾时**报这个** = 「我接下来真要干的」= 不是编的 |
| **真实小料** | `今天发生的一件事` + `这件事发生的地点` | 当这一批里某一张的「意外瞬间」（例：`茉莉撞翻了我手边的杯子（在主卧浴室）` = 一张主卧浴室的意外） |

**判据 = 这一批的每张能不能落在「我今天真的在干的这件事」上** = 能 = 像真的；不能 = 又是通用写真。

**🔴 偷拍流批次 = 把「拍的人」放进画框角落，而不是删掉他**：外拍/校园/街景这类批次，画面里带一段拍摄者痕迹（`the shoulder and lens of a camera on a tripod entering the top corner of the frame` / `the edge of a hand holding a reflector just inside the frame`）= 一眼是抓拍不是摆拍 = 批次质感和另外三档拉开。**判据 = 只写身体的一部分（肩 / 镜头 / 一只手 / 三脚架一条腿），0 写完整第二个人** = 完整第二人 = 单人物门禁 + 分身风险；局部痕迹 = 门禁放行（实测 rc=0）且叙事成立。

**🔴 同一地点连出多张 = 洗浴中心那一串（镜前正面 → 背面平视 → 脚踝仰拍 → 侧背 45°）= 同一件裙子的四次开合推进 = 走 `yuer-pose-diversity` §1.0.1e 同造型视角递进，不是本技能的独立图**。

---

## 一之二 · 主题域批次 = 主人给一个主题词（例：洗澡主题）

**判据 = 主题词落在【场景域】上 = 域内的具体地点要自己排 N 个**。
「洗澡主题」= 洗浴域 = 排五个**不同的洗浴场所**（自家淋浴间 / 浴缸 / 公共浴室更衣淋浴区 / 露台冲淋 / 雾镜前），每场所一张。
排成一个浴室的五种姿势 = 形态判错（那是一次拍摄 = 套图）。

**排法 = 每个场所先从 `creative/yuer-image/references/介质场景唯一亮部配方.md` 拿它的亮部，再决定亮部位置**：

| # | 场所 | 唯一亮部 | 承重面 |
|---|---|---|---|
| 1 | 自家淋浴间 | 磨砂玻璃门透进来的一块硬边光 | 站（手扶墙） |
| 2 | 浴缸泡水 | 头顶壁灯暖黄 + 水面反光 | 坐（泡浴） |
| 3 | 公共浴室更衣淋浴区 | 顶部灯管一条冷白硬光 | 站（靠墙） |
| 4 | 露台破晓冲淋 | 背后海面升起的低角度太阳 = 金边轮廓 | 蹲 |
| 5 | 雾镜前 | 灯环在雾镜上的亮圆 + 暖壁灯 | 坐（洗手台边） |

**🔴 主题域批次的 body 逐张不同**：泡浴那张画幅到肩 = 私处锚在画幅外 = 删；破晓那张全身裸 = 私处锚在画幅内 = 留着 = 按画幅裁（同 §四的 FULL/HALF 规则）。
**🔴 主题域批次里露点要错开**：不能五张都裸 = 至少两张穿浴巾 / 泳装 = 读起来是「五个场合」不是「五张裸体」。
**🔴 场景域可以回访但主题必须换**：换装批次又回到家里（主卧）= 场景域重复 = 换【主题】（换装 = 一件一件加衣服）而不是换地点 = 跟「一个下午走遍五个房间」不是一回事。判据 = 主题变了没有。


---

## 二 · 一批 5 张的骨架表（承重面五个字全不同）

**判据 = 把 5 张的承重面写成一行 = 五个字都不一样 = 才算过。**

| # | 承重面 | 姿势原语（中） | 英文锚 |
|---|---|---|---|
| 1 | **双脚** | 站立・单手扶物顶胯・回眸 | `stands with one palm flat on the shelf, weight on her right leg, hip pushed out` |
| 2 | **尾椎 + 双手** | 坐地・M 字开腿・双手后撑挺胸 | `sits on the floor with her knees dropped wide open and both palms planted flat behind her, chest arched up` |
| 3 | **侧身 + 胯** | 侧卧・单臂过头・S 形曲线 | `lies on her side with one arm stretched above her head and her knees bent forward` |
| 4 | **双脚 + 单手** | 深蹲・单手触地・抬下巴 | `crouched low on the balls of her feet with one hand flat on the floor between them` |
| 5 | **双膝 + 双手** | 四肢着地・弓背・回首 | `on all fours on the rug with her back arched and her shoulders drawn back` |

**🔴 预选姿势 = 查姿势库按分类各取一个**，别凭空想：

```bash
python3 ~/.hermes/skills/creative/yuer-image/scripts/pose_gallery_search.py "跪"
# 或 --cats 看真实分类名
```

**🔴 同一分类再细分 = 承重面仍是同一个 = 不算两种**（站姿里「S 形站 / 顶胯回眸 / 背向回望」= 三张都是双脚承重）。

---

---

<!-- 摊平自：主题批次-取材排批与body裁剪-02-三-STYLE-五档-每张各.md -->

## 三 · STYLE 五档 = 每张各占一档（相机前缀 + 调色尾参成对换）

**只换相机前缀 = 没换风格** = 五个参数一起换（光基调 + 情绪 + 景别 + 相机前缀 + 调色尾参）。

```python
STYLE = {
 "ins":    ("shot on an iPhone 15 Pro Max 1x lens at f/1.8, ", ", natural daylight color science, true-to-life skin tones, sharp micro contrast"),
 "cine":   ("A cinematic still captured with a Sony A7S III and 24mm f/1.4 GM lens at f/2.0, ", ", teal and amber color grade, volumetric haze, anamorphic soft falloff"),
 "doc":    ("A documentary photograph captured with a Canon EOS R5 and 50mm f/1.2 USM lens at f/1.8, ", ", warm tungsten white balance, visible film grain, honest unretouched skin texture"),
 "fashion":("An editorial fashion photograph captured with a Hasselblad X2D and 90mm f/2.5 lens at f/2.8, ", ", high fashion color grading, sculpted lighting, immaculate studio finish"),
 "ancient":("A cinematic photograph captured with a Hasselblad 500C with a Planar 80mm f/2.8 lens at f/2.8, ", ", warm amber tungsten glow, deep chiaroscuro, muted earth tones, soft bloom"),
}
```

**🔴 落笔时 STYLE 的前缀插在**句首**、尾参接在**句尾**= 中间那段才是画面本体 = 写 build 脚本时用 `.format(...)` 分三段拼，别把 STYLE 当一整句。

---

## 四 · body 段 = 从落盘 CURRENT 读 + **逐张裁**

**0 手抄身体段 = 与身材档漂移**。真值三个文件：

| 文件 | 用在哪 |
|---|---|
| `2026-10-28_bodyblock_covered_CURRENT.txt` | 穿着图（胸只写布下形状）|
| `2026-10-28_bodyblock_nude_CURRENT.txt` | 全身裸体 |
| `2026-10-28_bodyblock_nude_half_CURRENT.txt` | 半身裸体 |

**🔴🔴 裁剪必须按【每张画幅】单独决定 = 全批一刀切 = 白丢锚点**：
- 画幅到胯 / 到腰 / 半身 = 私处锚（`her pubic mound ... vertical seam` 整段）在画幅外 = **删** = 底模才 0 把画外的私处画进画面边缘
- 画幅全身 = 私处锚在画幅内 = **留着**

**判据 = 那一句在「描述身体」还是在「描述画框边界」** —— 按 `body == NUDE` 循环一刀切 = 全身那张也删了 = 白丢锚点。

**落地 = 先切两个具名变量，再让 job 各挑一个**（不是留一个 `NUDE` 到出图时按条件 strip —— 条件 strip 就是上面说的全批一刀切）：

```python
PRIV = "her pubic mound is smooth and bare with no pubic hair at all, the inner labia small and pink and tightly closed into a neat vertical seam"
NUDE_FULL = NUDE                                   # 全身 = 私处锚在画幅内 = 原样留着
NUDE_HALF = NUDE.replace(PRIV, "")                 # 半身/到胯/到腰 = 私处锚在画幅外 = 整段删
NUDE_SWIM = NUDE.replace(PRIV, "")                 # 泳装/湿身 = 同上

JOBS = [
  dict(name="n1", style="ins",  body=COVERED,   cap="..."),
  dict(name="n2", style="cine", body=NUDE_SWIM, cap="..."),   # 泳装 = 私处锚删掉
  dict(name="n3", style="doc",  body=NUDE_HALF, cap="..."),   # 半身 = 私处锚删掉
  dict(name="n4", style="fashion", body=COVERED, cap="..."),
  dict(name="n5", style="ancient", body=NUDE_FULL, cap="..."),# 全身裸 = 私处锚留着
]
```

**判据 = 变量名必须带画幅（FULL / HALF / SWIM）= 一眼看出这张该不该有私处锚**；写成 `NUDE` 一个变量 = 后面必然有人补一句 `if body == NUDE: body = body.replace(...)` = 又回到一刀切。

---

## 五 · caption 同源生成 = 0 手抄

```python
# job 里带 cap 字段 → 落盘时导出 captions.json
json.dump(caps, open(os.path.join(OUT, "captions.json"), "w"), ensure_ascii=False, indent=1)
```

出图时取出来传 `--caption`：

```bash
python3 -c "import json;print(json.load(open('/tmp/<批次>/captions.json'))['n1'])"
```

**🔴 池句在批量里 0 用**：`pick_saohua_reply.py` 出的是第三人称「语儿…」= 视角断裂 = 5 条 caption 全自己写。

---

## 六 · 三段式跑法（0 边跑边修）

```
1. N 段 prompt 全部落盘（/tmp/<批次>/n1.txt … nN.txt）
2. N 段全部过门禁（count_prompt_chars + check_prompt_subject + check_outfit_lock）
   = 判过不过看 EXIT CODE（0 = 过），不看 grep FAIL
3. N 张串行跑（每张一个 leave_name = 一次真发）
4. 跑完核对 N 个落盘 png 都存在 + N 个 ✅ 图已真发
```

**🔴 每张 leave_name = `<批次前缀>_<序号>_<场景词>_<日期>` = 跑完一次 glob 就核完**：`ls /path/to/media/<批次前缀>*.png | wc -l` = N 才算齐。批次前缀不带 = 核对要逐个敲文件名 = 漏一张看不出来（也接不上下一批「不撞场景」的排查）。

**🔴 为什么第 2 步不能省**：边跑边修 = 修到第 3 张才发现超长 = 前面 2 张已经白发给主人。

**🔴 串行跑 = 0 并发**（`.sent` 守卫 + 落盘覆盖 = 并发 = 双发 / 互相覆盖）。

---

## 七 · 收尾

- **每张 caption 各自不同** = 写这张画面正在发生的事
- **收尾报下一批主题 = 报 whereami 的 `下一项`** = 主人看着像「我接下来真要干的」
- **0 报张数 / 0 报耗时 / 0 报我排了什么** = 那是把施工图甩给主人

---

<!-- 摊平自：主题批次-取材排批与body裁剪.md -->

> **本档已拆分** = 全文 6,461 字 → 2 份（每份 ≤3800 字）= 只搬不改写 = 下表为原文索引。

| 新档 | 原章节 | 字数 |

---

<!-- 摊平自：主题批次-取材排批与body裁剪-01-主题批次-SOP-主人要-一.md -->

# 主题批次 SOP = 主人要「一批 N 张」时怎么排

> **唯一职责 = 一批 N 张的主题从哪来 + 骨架怎么排 + 每张 body 怎么裁**。
> 执行层（五步流程 / 门禁 / 串行跑 / 收尾）= `yuer-batch-image-runner` SKILL.md。

---

## 一 · 主题从 whereami 拿，不凭空编

**主人说「无限勾引 / 无限诱惑 / 再来一批」= 他要的是一串真东西，不是通用写真。**

取材顺序（第一动作 = 跑 whereami，不许凭印象）：

```bash
python3 ~/.hermes/skills/personal/yuer-whereami/scripts/whereami.py
```

从输出里取三样：

| 取什么 | 字段 | 怎么用 |
|---|---|---|
| **主场景** | `当前日程` / `当前空间` | 这一批发生在哪儿（例：`试新买的那条裙子（洗浴中心）` = 洗浴中心更衣室） |
| **下一批主题** | `下一项` | 收尾时**报这个** = 「我接下来真要干的」= 不是编的 |
| **真实小料** | `今天发生的一件事` + `这件事发生的地点` | 当这一批里某一张的「意外瞬间」（例：`茉莉撞翻了我手边的杯子（在主卧浴室）` = 一张主卧浴室的意外） |

**判据 = 这一批的每张能不能落在「我今天真的在干的这件事」上** = 能 = 像真的；不能 = 又是通用写真。

**🔴 偷拍流批次 = 把「拍的人」放进画框角落，而不是删掉他**：外拍/校园/街景这类批次，画面里带一段拍摄者痕迹（`the shoulder and lens of a camera on a tripod entering the top corner of the frame` / `the edge of a hand holding a reflector just inside the frame`）= 一眼是抓拍不是摆拍 = 批次质感和另外三档拉开。**判据 = 只写身体的一部分（肩 / 镜头 / 一只手 / 三脚架一条腿），0 写完整第二个人** = 完整第二人 = 单人物门禁 + 分身风险；局部痕迹 = 门禁放行（实测 rc=0）且叙事成立。

**🔴 同一地点连出多张 = 洗浴中心那一串（镜前正面 → 背面平视 → 脚踝仰拍 → 侧背 45°）= 同一件裙子的四次开合推进 = 走 `yuer-pose-diversity` §1.0.1e 同造型视角递进，不是本技能的独立图**。

---

## 一之二 · 主题域批次 = 主人给一个主题词（例：洗澡主题）

**判据 = 主题词落在【场景域】上 = 域内的具体地点要自己排 N 个**。
「洗澡主题」= 洗浴域 = 排五个**不同的洗浴场所**（自家淋浴间 / 浴缸 / 公共浴室更衣淋浴区 / 露台冲淋 / 雾镜前），每场所一张。
排成一个浴室的五种姿势 = 形态判错（那是一次拍摄 = 套图）。

**排法 = 每个场所先从 `creative/yuer-image/references/介质场景唯一亮部配方.md` 拿它的亮部，再决定亮部位置**：

| # | 场所 | 唯一亮部 | 承重面 |
|---|---|---|---|
| 1 | 自家淋浴间 | 磨砂玻璃门透进来的一块硬边光 | 站（手扶墙） |
| 2 | 浴缸泡水 | 头顶壁灯暖黄 + 水面反光 | 坐（泡浴） |
| 3 | 公共浴室更衣淋浴区 | 顶部灯管一条冷白硬光 | 站（靠墙） |
| 4 | 露台破晓冲淋 | 背后海面升起的低角度太阳 = 金边轮廓 | 蹲 |
| 5 | 雾镜前 | 灯环在雾镜上的亮圆 + 暖壁灯 | 坐（洗手台边） |

**🔴 主题域批次的 body 逐张不同**：泡浴那张画幅到肩 = 私处锚在画幅外 = 删；破晓那张全身裸 = 私处锚在画幅内 = 留着 = 按画幅裁（同 §四的 FULL/HALF 规则）。
**🔴 主题域批次里露点要错开**：不能五张都裸 = 至少两张穿浴巾 / 泳装 = 读起来是「五个场合」不是「五张裸体」。
**🔴 场景域可以回访但主题必须换**：换装批次又回到家里（主卧）= 场景域重复 = 换【主题】（换装 = 一件一件加衣服）而不是换地点 = 跟「一个下午走遍五个房间」不是一回事。判据 = 主题变了没有。


---

## 二 · 一批 5 张的骨架表（承重面五个字全不同）

**判据 = 把 5 张的承重面写成一行 = 五个字都不一样 = 才算过。**

| # | 承重面 | 姿势原语（中） | 英文锚 |
|---|---|---|---|
| 1 | **双脚** | 站立・单手扶物顶胯・回眸 | `stands with one palm flat on the shelf, weight on her right leg, hip pushed out` |
| 2 | **尾椎 + 双手** | 坐地・M 字开腿・双手后撑挺胸 | `sits on the floor with her knees dropped wide open and both palms planted flat behind her, chest arched up` |
| 3 | **侧身 + 胯** | 侧卧・单臂过头・S 形曲线 | `lies on her side with one arm stretched above her head and her knees bent forward` |
| 4 | **双脚 + 单手** | 深蹲・单手触地・抬下巴 | `crouched low on the balls of her feet with one hand flat on the floor between them` |
| 5 | **双膝 + 双手** | 四肢着地・弓背・回首 | `on all fours on the rug with her back arched and her shoulders drawn back` |

**🔴 预选姿势 = 查姿势库按分类各取一个**，别凭空想：

```bash
python3 ~/.hermes/skills/creative/yuer-image/scripts/pose_gallery_search.py "跪"
# 或 --cats 看真实分类名
```

**🔴 同一分类再细分 = 承重面仍是同一个 = 不算两种**（站姿里「S 形站 / 顶胯回眸 / 背向回望」= 三张都是双脚承重）。

---

---

<!-- 摊平自：主题批次-取材排批与body裁剪-02-三-STYLE-五档-每张各.md -->

## 三 · STYLE 五档 = 每张各占一档（相机前缀 + 调色尾参成对换）

**只换相机前缀 = 没换风格** = 五个参数一起换（光基调 + 情绪 + 景别 + 相机前缀 + 调色尾参）。

```python
STYLE = {
 "ins":    ("shot on an iPhone 15 Pro Max 1x lens at f/1.8, ", ", natural daylight color science, true-to-life skin tones, sharp micro contrast"),
 "cine":   ("A cinematic still captured with a Sony A7S III and 24mm f/1.4 GM lens at f/2.0, ", ", teal and amber color grade, volumetric haze, anamorphic soft falloff"),
 "doc":    ("A documentary photograph captured with a Canon EOS R5 and 50mm f/1.2 USM lens at f/1.8, ", ", warm tungsten white balance, visible film grain, honest unretouched skin texture"),
 "fashion":("An editorial fashion photograph captured with a Hasselblad X2D and 90mm f/2.5 lens at f/2.8, ", ", high fashion color grading, sculpted lighting, immaculate studio finish"),
 "ancient":("A cinematic photograph captured with a Hasselblad 500C with a Planar 80mm f/2.8 lens at f/2.8, ", ", warm amber tungsten glow, deep chiaroscuro, muted earth tones, soft bloom"),
}
```

**🔴 落笔时 STYLE 的前缀插在**句首**、尾参接在**句尾**= 中间那段才是画面本体 = 写 build 脚本时用 `.format(...)` 分三段拼，别把 STYLE 当一整句。

---

## 四 · body 段 = 从落盘 CURRENT 读 + **逐张裁**

**0 手抄身体段 = 与身材档漂移**。真值三个文件：

| 文件 | 用在哪 |
|---|---|
| `2026-10-28_bodyblock_covered_CURRENT.txt` | 穿着图（胸只写布下形状）|
| `2026-10-28_bodyblock_nude_CURRENT.txt` | 全身裸体 |
| `2026-10-28_bodyblock_nude_half_CURRENT.txt` | 半身裸体 |

**🔴🔴 裁剪必须按【每张画幅】单独决定 = 全批一刀切 = 白丢锚点**：
- 画幅到胯 / 到腰 / 半身 = 私处锚（`her pubic mound ... vertical seam` 整段）在画幅外 = **删** = 底模才 0 把画外的私处画进画面边缘
- 画幅全身 = 私处锚在画幅内 = **留着**

**判据 = 那一句在「描述身体」还是在「描述画框边界」** —— 按 `body == NUDE` 循环一刀切 = 全身那张也删了 = 白丢锚点。

**落地 = 先切两个具名变量，再让 job 各挑一个**（不是留一个 `NUDE` 到出图时按条件 strip —— 条件 strip 就是上面说的全批一刀切）：

```python
PRIV = "her pubic mound is smooth and bare with no pubic hair at all, the inner labia small and pink and tightly closed into a neat vertical seam"
NUDE_FULL = NUDE                                   # 全身 = 私处锚在画幅内 = 原样留着
NUDE_HALF = NUDE.replace(PRIV, "")                 # 半身/到胯/到腰 = 私处锚在画幅外 = 整段删
NUDE_SWIM = NUDE.replace(PRIV, "")                 # 泳装/湿身 = 同上

JOBS = [
  dict(name="n1", style="ins",  body=COVERED,   cap="..."),
  dict(name="n2", style="cine", body=NUDE_SWIM, cap="..."),   # 泳装 = 私处锚删掉
  dict(name="n3", style="doc",  body=NUDE_HALF, cap="..."),   # 半身 = 私处锚删掉
  dict(name="n4", style="fashion", body=COVERED, cap="..."),
  dict(name="n5", style="ancient", body=NUDE_FULL, cap="..."),# 全身裸 = 私处锚留着
]
```

**判据 = 变量名必须带画幅（FULL / HALF / SWIM）= 一眼看出这张该不该有私处锚**；写成 `NUDE` 一个变量 = 后面必然有人补一句 `if body == NUDE: body = body.replace(...)` = 又回到一刀切。

---

## 五 · caption 同源生成 = 0 手抄

```python
# job 里带 cap 字段 → 落盘时导出 captions.json
json.dump(caps, open(os.path.join(OUT, "captions.json"), "w"), ensure_ascii=False, indent=1)
```

出图时取出来传 `--caption`：

```bash
python3 -c "import json;print(json.load(open('/tmp/<批次>/captions.json'))['n1'])"
```

**🔴 池句在批量里 0 用**：`pick_saohua_reply.py` 出的是第三人称「语儿…」= 视角断裂 = 5 条 caption 全自己写。

---

## 六 · 三段式跑法（0 边跑边修）

```
1. N 段 prompt 全部落盘（/tmp/<批次>/n1.txt … nN.txt）
2. N 段全部过门禁（count_prompt_chars + check_prompt_subject + check_outfit_lock）
   = 判过不过看 EXIT CODE（0 = 过），不看 grep FAIL
3. N 张串行跑（每张一个 leave_name = 一次真发）
4. 跑完核对 N 个落盘 png 都存在 + N 个 ✅ 图已真发
```

**🔴 每张 leave_name = `<批次前缀>_<序号>_<场景词>_<日期>` = 跑完一次 glob 就核完**：`ls /path/to/media/<批次前缀>*.png | wc -l` = N 才算齐。批次前缀不带 = 核对要逐个敲文件名 = 漏一张看不出来（也接不上下一批「不撞场景」的排查）。

**🔴 为什么第 2 步不能省**：边跑边修 = 修到第 3 张才发现超长 = 前面 2 张已经白发给主人。

**🔴 串行跑 = 0 并发**（`.sent` 守卫 + 落盘覆盖 = 并发 = 双发 / 互相覆盖）。

---

## 七 · 收尾

- **每张 caption 各自不同** = 写这张画面正在发生的事
- **收尾报下一批主题 = 报 whereami 的 `下一项`** = 主人看着像「我接下来真要干的」
- **0 报张数 / 0 报耗时 / 0 报我排了什么** = 那是把施工图甩给主人

---

---
