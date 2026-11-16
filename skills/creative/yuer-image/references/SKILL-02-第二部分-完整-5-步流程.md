# 第二部分 · 完整 5 步流程

| 步 | 做什么 | 规矩 |
|---|---|---|
| 0 | 脑子里先有一幅画面 | 过 `yuer-prompt-writer` §1 落笔前五问。**brief 第一行必写「档位：」+「链路：」** |
| 1 | 组合描述成 prompt | 6 句一组、句句接着说、0 分段 0 Markdown 0 元注释 |
| 2 | 调 ComfyUI 出图 | `bash scripts/yuer_ka_fast.sh <prompt_file> <leave_name> "<caption>" "<brief>"` = **0 门禁** + 出图 + 发图 + 双归档一次完成 |
| 3 | 发图 | wrapper 内部已真发飞书。reply 文本 0 MEDIA / 0 路径 · **形状 = 纯文本**（0 斜体 0 `---` 0 加粗 = 真源 `creative/yuer-image-delivery`）|
| 4 | 双存档 | `<leave>.brief.txt` + `<leave>.prompt.txt` → `/path/to/media/` |

**🔴 落盘顺序 = 构思顺序**：brief 先写 → prompt 落盘 → **立刻 cp 进留底目录** → 才跑出图。顺序反了 = 构思环节其实没跑。
**🔴 轮次中断 = 补那一步 = 0 重跑**（出图道）：断在 prompt 落盘后 = `/tmp/prompt_<主题>.txt` 还在 = 补跑 `yuer_ka_fast.sh` 同一条 = **.sent 守卫会自动拦住已发的那张** = 换 leave_name 才能重发。断在出图前 = 落盘目录里没 png = 才补跑。
**🔴 落盘名 = 脚本自动加时间戳**（`yuer_<日期>_<时分>_<短名>.png`）= 天然唯一 = 0 靠自觉起名 = 同秒重名自动追加 `_2`。
**🔴 prompt 文件名禁带引号 / 禁带图像扩展名** = 只能 `[A-Za-z0-9_.-]` + `.txt`。
**🔴 别心算字数** = 门禁只在真超 4000 时拦 = 被字数打回 = 在凑字数砍构图 = 画面不好看的真根因。

## 2.1 出图链路标准命令链

**🔴 出图道 = 快车道一条命令（3 轮内 = 目标墙钟 < 60s）**

```bash
# 1) 读速查卡（1 次 skill_view('yuer-image', 'references/出图速查卡.md')）= 拿到全部规则

# 2) 写 prompt（1 次 write_file → /tmp/prompt_<主题>.txt）

# 3) 出图 + 真发飞书 + 双归档 + timing（1 次 terminal）
bash ~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh \
  /tmp/prompt_<主题>.txt <leave_name> "<caption>" "<一行中文 brief>"
```

🔴 **0 手工预跑门禁 / 0 查素材库 / 0 grep 源码 / 0 写两份 brief** = 这四条是上一轮 A 段 7 分 14 秒的来源。

<details>
<summary>老链路（手敲版 = 只有在改脚本/调试时才用）</summary>

```bash
# 1) 先加载技能（主人查流程时这行就是证据）
skill_view('yuer-prompt-writer')

# 1b) 先查提示词资产池（0 查库 = 现成货白白浪费 = 风格漂移）
python3 ~/.hermes/skills/creative/yuer-image/scripts/yuer_prompt_search.py "<主题:权重>,<道具:权重>,<机位:权重>" --top 6

# 2) 落盘 brief（第一行 = 档位 + 链路）
write_file('/path/to/media/<leave>.brief.txt', '...')

# 3) 落盘 prompt
write_file('/tmp/prompt_<主题>.txt', '<英文散文>')

# 4) 出图 + 真发飞书（🔴 0 门禁 = 11-12 主人钦定）
bash ~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh /tmp/prompt_<主题>_<日期>.txt <leave_name> "<caption>" "<brief>"

# 5) prompt 落盘后立刻 cp 进留底目录
cp /tmp/prompt_<主题>.txt "/path/to/media/<leave>.prompt.txt"
```

</details>

**🔴 模型路由（主人点名才切）**：`--model krea2` = `yuer_moody_fast`（Krea2 Mix v7）｜`--model moss` = `yuer_moodyMoss_fast`（写实 + 真负向框 + 锁脸）｜`--model anima` = 2D 动漫｜`--model qwen` = 编辑道。
**🔴 换模型 = 换工作流 + 换提示词语言 + 换门禁放行 = 三样一起换**，只换其中一样 = 出不来或出得不对。
**🔴 `--report-only` = 抽卡道专用 = 本档出图道一律不加** = 加上 = 体检只报数不拦 = 姿势自然度 FAIL 也放行。**🔴 同一份稿子两条道两个结果** = 抽卡照出 / 出图拦住 = 别把出图道的判据套到抽卡道，反之亦然。
**🔴 提示词方法也按模型分家** = Krea2 → `yuer-krea2-prompt`（英文架构师）｜Moss → `yuer-moss-prompt`（中文架构师）= **两个模型不能共用一份** = 底模 / 编码器 / 提示词语言 / 负向接法全不同 = 共用一份 = 至少一条道的产物层直接作废（例：英文散文喂中文道 = 白瞎它的中文能力）。
**🔴 Moss = 有独立负向框（节点 864）= 负向词正常写**；**Krea2 = `ConditioningZeroOut` = 没有真负向框 = 负向词一律改正面词**。判据 = 先看工作流负向节点接的是 `CLIPTextEncode` 还是 `ConditioningZeroOut`。
**🔴 中文稿 = 门禁已改中英双语 = 0 需翻译**；**中文 brief 走 `--model moss`**（Krea2 读不懂中文）。

