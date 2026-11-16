## 6.1 露屁股构图 = 不露脸 + 不强扭身形


| # | 铁律 | 落地 |
|---|---|---|
| ① **背影构图 + 零写脸** | 零脸部/表情/眼神词。头发垂下遮住后脑，背影自然成立。**妆容锚照写**（`light makeup applied with black eyeliner and soft pink lipstick`）= 脸看不见 ≠ 外观锚可以省 |
| ② **身体自然放松，不强扭** | 承重腿 + 自然重心。**禁止为露屁股把腰扭到极限、四肢拧在一起 = 一多肢体就畸形** |
| ③ **露出靠服装错位，不靠扭曲** | 系带松开、衣摆滑开、弯腰提裙这类自然动作让布料错位 = 露出真实且形体会合 |
| ④ **🔴 身材词以身材档 v1.5 为准，不以旧背影模板为准** | `yuer-back-view-style` 里的 `small breasts` / `petite` / `骨感纤细` = v1.3 小胸路线 = **已废止**，照抄 = 出小胸平臀 = 比例塌。v1.5 = **大胸紧翘 + 极细腰 + 蜜桃翘臀 + 大长腿**，锚 = `sitting high and firm` / `peach-like swell` / `slender firm thighs` / `waist-to-hip ratio` / `head-lengths`。禁 `resting low and heavy` / `sagging` / `huge ass` / `bubble butt` / `thick thighs` / 锁骨词。**该技能只给文风（视角/发型/剪裁/场景/光线/质感），主体锚和身材锚自己补** |
| ⑤ **🔴 下装必点名** | 门禁 `check_outfit_lock.py` 报「缺下装」= FAIL 级 = 漏了 = 画成光腿 = 主角看不到。`jeans / shorts / leggings / skirt / dress / briefs` 写清楚颜色材质腰头位置 |
> **6.2 cos 系列 = 查参考库最近案例 + 换角色换场景换姿势** = 细则全文 = `references/yuer-pose-diversity-细则全集.md`（撞到具体场景再查）

# 第七部分 · 执行环境坑

- `yuer_run_one_brief.py` 内部 `import comfyui` = 出图必走 `terminal` 调 `/usr/bin/python3 脚本`，不走 `execute_code`（sandbox kernel 没这个包）。
- **🔴 长度 0 阻断**：stdout 报偏长/FAIL = 只报数 = 不拦 = 图照出 = 0 回头改稿；真嫌长 = 删「同一个点写了两遍」那句，0 删维度。
- **🔴 别拿 wrapper 当字符调试器**：一次调用 = 一次完整出图开销。落笔后先 `count_prompt_chars.py` 数一次，目标 = 当轮上限的 70~80%，不贴顶。
- **🔴 同一 prompt 文件重写 ≤2 次 = 熔断**：第 2 次还超 = 读当轮上限（stdout 或 `count_prompt_chars.py`，默认 3200）按 **×0.75 整篇重写**，砍的顺序固定 = 环境第二层 → 材质清单 → 尾参形容词 → 相机硬件尾段，一次砍到位；微调只在超量 <200 字符时值得一次。「硬件收尾段」（`Shot on a Canon EOS R5…`）先 `grep -c 'Shot on' 起点` = 0 就不许自己加（白送 200-300 字符 0 增益）。判据 = 数工具调用数：写超 2 次 = 纯烧。
- **🔴 落盘长 prompt / build 脚本**：长 prompt 直接 `write_file` 一把过；代码里拼串用 `"\n".join([...])` 先建列表再 join（相邻字面量 = SyntaxError 白跑）；写出的 .py 先 `python3 -c "import ast; ast.parse(open(p).read)"` 验语法再跑（`ast.parse` / 每批一个独立 build 脚本 / 批量门禁 = `yuer-image` 批量段，0 重复正文）。
- **🔴 出图落盘 = 立刻真发飞书**（`yuer_ka_fast.sh` 已调 `yuer_send_v2.sh`）= reply 文本 0 MEDIA 字面（主人在场 3 步 = `yuer-image`）；判定顺序 = exit 0 + `✅ 图已真发飞书` + 落盘存在 = 已发出，0 补发 0 重跑，`grep` 日志查重复不查缺失；exit 4 / 发图失败 = 才手动补发。
- **🔴 机械门 = 连续两张 stdout 都带 FAIL = 立刻停批**：按 §3.1「min(上限×0.8, 起点×1.15)」重写这张、数过了再跑；同一张反复被拦 = 逐句抠字了 = 按超量一次砍整段（材质/环境第二层/尾参），别一行行抠。

