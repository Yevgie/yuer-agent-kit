## **🔴 F 类青春学生/Coser 明亮主题 = 光线自动纠正已焊进脚本（配套 7av 低角度道）**

主人钦定常驻配方：**主题 = 青春学生 / coser + 光线必须明亮**（`bright` / `daylight` / `golden` / `even` = 禁 `night` / `neon` / `dim` / `dusk` / `emergency` / `dark`）。**🔴 触发信号（脚本自动判定）= prompt 含** `student` / `cosplayer` / `cosplay` / `university` / `college` / `high school` / `campus` / `convention` / `idol costume` / `coser` **任一**。**机制 = `yuer_ka_pai_zhi_chu.py` 自动三层**：① **整句级**替换暗光句（`Harsh, clinical fluorescent overhead lighting...` → `Bright clear daylight streaming through tall windows...`）② **整词级**替换暗光词（用 `\b` 词边界正则 = 0 半词误伤）③ **完全没光线词时**追加一句明亮光。**只对 F 类主题触发 = E 类夜场图 0 污染**（判据 = E 类提示词跑一遍 stdout 不出现「☀️ F 类明亮主题」）。**判据 = 落笔不必手工改光 = 脚本会改；出图 stdout 出现「☀️ F 类明亮主题」= 生效。**身份道具表（教材/书包/讲义/托特包/假发/发饰/挂绳证）+ 光线写法表 + 完整配图公式 = `yuer-seduction-pose-library` F 类段

## **🔴 低角度仰拍类 prompt = 必须锚定站姿 + 负向补畸形词 = 否则膝盖反曲**

**真根因（验证 agnes 反推 = 非猜测）**：Moss 遇到 `Extreme low-angle POV` + `looking up from ... steps` 会**脑补跪姿** = 大腿水平展开 + 大腿小腿成直角折叠 = **膝关节反曲 = 人体做不出来 = 畸形**；同提示词换 seed 偶发正常 = 坐实是「姿态脑补」不是画质差。**🔴 修法 = 两层，已在 `yuer_ka_pai_zhi_chu.py` 自动注入 = 0 靠手写**：① **站姿锚定句**追加到 prompt 尾部（`She stands upright on the step, both legs straight and slightly apart, knees only slightly bent, both feet planted flat on the step, her full body visible from head to feet, head fully in frame.`）② **负向补畸形词**（`kneeling, crouching, squatting, bent knees, hyper-extended knees, broken joints, twisted joints, extra legs, extra limbs, fused fingers, mutated hands, broken feet, deformed feet, no head, cropped head, out of frame`）。**触发条件 = prompt 含低角 POV 信号（`low-angle pov` / `extreme low-angle` / `looking up from` / `from below`）** = 只对这类道注入 = 别的道 0 碰。**判据 = 锚定句 + 畸形负向 = 可复用 = 落进参考库的 Full Prompt 也要带 = 不然下次抽卡抽到旧口径 = 又畸形**。**验这类图 = 0 用云端 vision（NSFW 必撞敏感词）= 走 `scripts/yuer_verify_image.py`（agnes 主 + 本地 Qwen 兜底）= brief 直接问「几条腿几只脚几只手？膝盖是站立还是跪姿反曲？」= agnes 会明确答**

## **🔴 门禁已改中英双语 = 门禁不再卡语种**（旧「为过门禁把中文稿翻成英文」的做法旧口径） · 🔴 门禁已改中英双语 = 门禁不再卡语种（旧「为过门禁把中文稿翻成英文」的做法旧口径）

门禁的「5 大结构段」正则**原本全是英文词表** = 中文稿必然 0/5 命中 = 加上「中文残留 = 自毁排版 FAIL」= 两条一起把中文稿拦死 = 我被迫先把中文翻成英文才敢落盘（= 门禁在管语种 = 越权）。**整改 = ① 删掉「中文残留」自毁检查 ② `count_prompt_chars.py` / `check_outfit_lock.py` / `check_prompt_subject.py` 三脚本全部正则扩成「中文 OR 英文」（主体锚 / 外观锁 8 项 / 场景 / 人群 / 道具 / 私密场所 / 发型 / 语儿身份词全双语）= **纯中文稿、中英混写 = 正常跑硬门禁 = 零绕行**。**🔴 剩下的开关 `--allow-chinese` 保留给 Danbooru 标签串那道（`--allow-tags` 同源）= 普通中文稿不再需要**。**🔴 判据 = 门禁拦的是语种 = 门禁错了（不是稿子错了）= 改门禁，0 把稿子改成另一种语言去迎合它**

## **🔴 模型路由 = 主人点名哪个模型就切哪条工作流 = 语儿的人脸 LoRA 绑 Krea2 + Moss（11-10 起）**

## **🔴 挑衣服 = 查服装库（COSTUME-DB-01）= 0 自己编一套**

