### 1.0.1 🔴 局部特写 = 四级递进阶梯（主人点名部位后连点「再近一点 / 还要更近」时照此走）

**触发链** = 主人一句接一句逼近：`看脸` → `再近一点` → `局部特写（嘴唇/锁骨/乳尖…）` → `还要更近` → `颜色不对`。
每一级 = **同场景同光线同一套造型**（照 §1.0 锁死），只动 **镜头距离 + 焦段 + 被摄部位 + 颜色锚点**。

| 级 | 焦段 / 距离 | 画面里有什么 | 出图后**唯一**要报的一句 |
|---|---|---|---|
| 1 半身 | 85mm f/1.8 / 2m | 头 + 肩 + 上半身 | 「近到 XX 厘米」|
| 2 大头 | 85mm f/1.6 / **20cm** | 脸占画面 2/3 | 「近到 XX 厘米」|
| 3 极微距 | **100mm macro f/2.8 / 15~6cm** | 只剩嘴唇 / 锁骨 / 乳晕那一小块 | 「XX 厘米，就这一小块」|
| 4 极致微距 | **200mm macro + 1.4x 增距 / 6cm** | 那一小块占满画面 | 「XX 厘米，XXX 占掉一半多画面」|

**🔴 递进时 0 重画场景** = 场景 / 时段 / 主光源 / 造型锚全部照抄上一张 = 主人能对比 = 才叫「更近」而不是「换一张」。

**🔴 换被摄部位 = 只改 crop 那一段** = 例：脸 → 嘴唇 = 把 `framed from the crown of her head down past her collarbones` 换成
`framed to just the lower half of her face, her lips and chin and the hollow of her throat, nothing else in the picture`。
**只换裁切线 = 主体自然换部位。**

**🔴 4 段铁律**（每级都要写）：① 焦段 ② **距离（厘米）** = 主人最爱听的就是这个数 ③ **裁切线**（漏了 = 还是上一张的构图）④ **颜色锚点**（见 §1.0.2 = 局部特写的成败点）。

**🔴🔴 裁切线只写「cutting across her hips」不够 = 底模会自己往下延伸**（写半身到胯，出图裁到小腿；写齐胸，出图给到腰）。**正解 = 裁切线 + 排除项成对写**：`the frame ends at her hip line, her knees and feet outside the frame` / `framed to just above her waist so that only her upper body stays in the frame` / `her face and collarbones filling the frame, her chin at the upper edge`。**判据 = 裁切线必须同时说清「画到哪儿」和「哪儿不画」；只说前者 = 画幅往下溜。**

**🔴 画幅越窄越要写排除项**：全身图底模默认给全身 = 越靠近特写越容易被拉回去（写嘴唇出成半张脸+环境，写腰胯出到大腿）。**排除项 = 一句抵一个负向词**（正面写法 = 不违反 0 负向词）。

**🔴🔴 但光有裁切线句还是不够 = 真根因 = 我在描述画面外的东西（实测 22 张）**


**22 张实测结论（同一张脸 / 同一场景 / 只改景别句）**：
- `medium shot` / `waist-up` / `upper body only` / `portrait crop` / `tight chest-up` = **全裁到大腿**（术语词 0 效果）
- 写 `the bottom edge of the frame cutting across her upper chest` = **还是大腿**
- 改画幅（3:4 / 4:3 / 3:4@2MP）= **还是大腿**
- 改焦距 + 距离（0.8m~3.2m 五档）= **还是大腿**
- 提示词里**彻底删掉**内裤/丝袜/鞋 + 只写脸/发/上胸蕾丝 + 写画面边界句 = **✅ 胸像**
- 同上 + 画面下缘落在腰线上 = **✅ 半身（到腰）**

**🔴 两条铁律**：
1. **只描述镜头里能看到的部分 = 画外一个字都不提**（画到腰 = 0 写内裤/丝袜/鞋/臀/腿/腿长锚）。**这是唯一根因** —— 我前 13 张每张都写了 `black lace briefs and sheer black thigh-high stockings and black high heels` = 我在描述画外的东西 = 底模照着画 = 下半身必然出现。
2. **写「画面的物理边界」不是写「景别术语」** = `the frame enclosing her head and her neck and her shoulders and the top of her chest` + `the bottom edge of the frame resting on her waistline` = 有效；`chest-up shot` = 无效。

**🔴🔴 批量出图时这条最容易复发**（单张记得，5 张写到手滑 = 顺手又补上「水从她腿上流下来」这类画外句 = 腿又跑出来）。**症状 = 框句明明写了，出图还是全身/大腿 = 不要再调框句写法 = 去 prompt 里找那句画外的 = 删整句。** 机械门（画外词扫描命令）+ 画内画外区分 + 裸体/露点稿的门禁倒逼正解 = `references/组合描述与畸形诊断.md` §五之二。

**🔴 强弱阶梯 = 肯定物理边界句 > 否定式画外声明 > 景别术语（无效）**：否定句（`nothing below X is in view`）单人勉强、**双人物直接失效**（裁切线滑到桌下）= 双人必须写肯定框句 + 框里点名「两个」（`the frame enclosing the two heads and the necks and the shoulders of both women` + `the bottom edge of the frame resting on the near edge of the marble tabletop`）。完整强弱表 + 双人物实测 = `references/组合描述与畸形诊断.md` §五之二。

**🔴🔴 但坐姿 + 桌面 = 物理上拍不到上半身（实测 8 张双人物批次）**：坐着的人面前有张平面桌 = 底模必须交代桌面下方是什么（桌腿 / 椅子 / 腿）= 肯定框句拦不住、否定式拦不住、补「桌面以下全部裁掉」也拦不住 = **三张全是腿跑出来**。**这不是措辞问题 = 几何约束。**

**🔴 落笔前机械问 = 这张要拍到腰以上吗？要的话 = 画面里有没有一张平面家具（桌 / 台 / 柜台 / 沙发座面）？** 有 = 改站姿，别在提示词里跟桌沿较劲。完整实测表 = `references/组合描述与畸形诊断.md` §五之二。

**🔴🔴 这两条机械问 = 门禁脚本一条都不拦 = 只能自己问**（实测吃过一次：`count_prompt_chars.py` 报「结构段命中 5/5 OK」+ 三类自毁排版全 OK + 负向词 0 = **全绿**，而 prompt 里写着 `seated at the edge of a dark wooden dining table` + `near half-body composition` = 坐着的人前面有张平面桌 = 底模必须交代桌面下方是什么 = 腿必然跑出来 = 主人要的上半身拿不到）。**判据 = 门禁绿 ≠ 几何成立** = 门禁只查字符/结构/排版/负向词，**查不出「这个坐姿在这张图里物理上拍不拍得到」**。

**🔴 落笔前固定跑一遍的两问（写在 prompt 文件旁边，不是心里过一遍）**：

```
□ 这张要拍到腰以上吗？→ 要  ⇒  画面里有平面家具吗？
   有（桌/台/柜台/沙发座面）⇒ 改站姿（吧台前/靠墙/窗边）
   0 平面家具 ⇒ 坐姿也行（地板/台阶/相机贴地平视）
□ 手出现了几次？⇒ 两次 = 多手风险 = 只在一句里写手
```

