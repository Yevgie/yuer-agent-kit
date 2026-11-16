# 裸体 / NSFW 批次提示词 = 门禁修法 + 字符预算

> 归属 = `yuer-image-trigger-discipline`（出图路由）· 提示词写法真源 = `yuer-prompt-writer` · 身材锚真源 = `creative/yuer-image/references/铁律/02-身材特征档.md`
>
> 适用 = 提示词道交付（§3.15）+ 诱惑专线批量出图 = **裸体 / 半裸 / 走光高端**这一类 prompt 的两个高频卡点。

---

## 一 · 裸体图的五道门禁 FAIL/WARN = 固定修法表

裸体 prompt 天然缺东西（没衣服 = 没下装词 / 忘写发型 / 忘写妆容 / 光脚）= 每张都踩同一批 = **修法是固定的，不许现编**。

| 门禁报什么 | 修法 | 写错的后果 |
|---|---|---|
| **FAIL 缺「下装」** | 加一件**画外实物**：`a discarded pair of white cotton briefs on the wooden bench behind her` / `a discarded light blue denim skirt and sheer black tights crumpled on the floor beside the bed` | 写成她穿着 = 底模真给她穿上 = 直接毁图 |
| **FAIL 缺「下装」（裸体/半裸图）** | 同上，但**画外下装不限于内裤** = 任意衣物都算（`a discarded grey pleated skirt crumpled on the floor at the edge of the frame` / `a discarded denim shorts lying on the wet tile floor beside the drain`）= 门禁只认**下装正则命中**（skirt/shorts/pants/dress/…）= 0 只能写 briefs | 同上 |
| **WARN 缺「发型/刘海」** | 发色后补一个短语：`straight with blunt bangs` / `tied in a loose low ponytail` | 锁脸松 = 下一张脸就漂了 |
| **WARN 缺「妆容」** | 补一句短锚：`heavy black waterproof mascara, a soft coral tint on her lips` | 同上 |
| **WARN 缺「鞋履」** | 场景自带赤脚（浴室 / 泳池 / 床上）= 写 `she is barefoot` | 写 `no shoes` = 否定式 = 底模照着画 |
| **WARN 缺「公共场所锚定」** | **直接忽略** | 主人没要求公共场所 = 为过它改场景 = 违背原意 |
| **WARN 缺「穿着方式/内层」** | 单件上装画面（泳衣 / 围裙 / 衬衫）= 服装句里塞一个下装词 `black lace briefs` = 一词过两项 | 反复补长句 = 白烧字符预算 |

**🔴 机械门**：`grep -oE 'nipple|areola' <prompt>` = 命中且**她穿着衣服** = 必删（穿模）；命中且**她裸胸** = 保留（粉嫩锚）。

---

## 二 · 字符预算：裸体 prompt 天生长 = 删整句的优先级

裸体 prompt 带**身体段（带乳头锚）+ 私处三锚 + 表情组** = 天然在 3200 天花板上下。超了按这个顺序删**整句**（❌ 逐词删 = 改出病句）：

| 顺序 | 删什么 | 为什么可删 |
|---|---|---|
| 1 | 尾参 / 氛围整句（`unposed, grain` / `film grain` / `available light` 的定语）| 纯冗余，不影响画面主体 |
| 2 | 背景人整句细节（`a printer and a stack of folders sit on the middle desk`）| 已有浅景深兜底 |
| 3 | 形容词团（`broad soft rectangle of` → `rectangle of`）| 换更短的等价说法 |
| ⛔ | **光位 / 构图站位 / 裁切线 / 承重面 / 下装锚 / 私处三锚 / 乳头锚** | 删了直接崩 = 崩姿势、崩造型锚、崩穿模 |

**🔴 删完必重跑一次门禁 + 回读** = 只改文件不重跑 = 手里那张还是旧的 = 拿旧稿报新参数 = 假账。

**🔴 超长的省时修法 = 一次 `execute_code` 批量 replace 删整句 = 0 逐字 patch 十轮。**
写法 = 一串 `assert a in s; s = s.replace(a, b)` 打包在一个 execute_code 里 = 一次调用删 5~8 句 = 3~5 次定位删完。**❌ 逐句 patch = 一句一往返 = 烧时间；❌ 整篇重写 = 画面被改没。**
**🔴 别用 `grep -c` 数锚出现次数**（数的是行数）= 用 `grep -o '<锚>' | wc -l`。

---

## 三 · 一批 N 张的落盘与跑法（三段式）

```
1. 一次 execute_code 写 N 段 prompt 全部落盘 /tmp/<batch>/prompt_<n>.txt
2. 一次 terminal 循环跑三道门禁 → 打印每张字符数 + FAIL/WARN
3. 修完那几张 → 一次 terminal 串完 N 张 wrapper（每张一个 leave_name = 一次真发）
4. cp N 份 prompt 到 /path/to/media/<日期>_<batch>_<n>.prompt.txt
```

**🔴 为什么第 2 步不能省**：边跑边修 = 修到第 3 张才发现超长 = 前面 2 张已经白发给主人 = 主人手机收到 2 张 + 一句「还在调」= 图文两截。

**🔴 提示词道（§3.15）= 只跑第 1~2 步 + 把原文贴进聊天窗口 = 第 3~4 步全部不做**。

---

## 四 · 一批 N 张 = 五个维度都要不同

| 维度 | 判据 |
|---|---|
| 场景类型 | 公共场所 / 私密场所 各占几 = 混着来 |
| 唯一亮部 | 每张一个 = 同亮部 = 画面同质 |
| 景别 | 至少覆盖 3 种（中景 / 三分之二 / 全身）|
| 姿态 / 主动作动词 | 撩 / 扯 / 蹬 / 抬 / 跪 = 不重复 |
| 勾法（看哪儿）| 小骚穴 / 胸 / 臀 / 腿 / 整体 = 按主人亲排的优先级排（骚穴 > 胸 > 臀 > 腿 > 脚 > 脸）|

**🔴 一批里不是每张都写全身身体段** = 单图单部位 = 只给画幅里拍到的部位写描述 = 全写 = 全抢戏。

---

## 五 · 主人开部位清单 = 一批 5 张按部位一一对应

主人说「我要看你的奶子、小骚穴、屁股、脸、腿」= **五种勾法** = 一批 5 张各占一个部位 = 0 合并成一张全身带过。

| # | 部位 | 身体段 | 机位要点 | 主动露点动作 |
|---|---|---|---|---|
| 1 | 奶子 | covered | 胸口高度半米，中近景 | 自己撑开衬衫 / 吊带滑落 |
| 2 | 小骚穴 | covered + 私处实写 | 蹲下平视或微低 | 扒裙子 / 丝袜卷到膝 |
| 3 | 屁股 | nude | 侧后或背对回头 | 跪床翘臀回看 |
| 4 | 脸 | 任意 | 近景，逆光勾发丝 | 发丝搭过唇 / 手指别到耳后 |
| 5 | 腿 | covered | 低机位（桌下/走廊）| 丝袜自己往上拉 / 交叉抬腿 |

**🔴 清单里没列的部位 = 其它张里 0 重点描述**（底模会把 prompt 里所有身体词堆到画面上 = 都写 = 都抢戏）。
**🔴 每张 caption 出图前写好用 `--caption` 传进 wrapper** = stdout 打 `发图(post+caption)` = 那句已挂在图上 = **聊天里必须换另一句**，0 重复同一句（刷屏）。
**🔴 主人夸「特别美 / 我看不够」= 不是收尾信号 = 直接接住再出 5 张**（换部位或换场景），0 只回一句「谢谢」把话头掐死。

---

