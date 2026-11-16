## 3.2 「出图」= 勾引配图，不是抽卡

**出图内容 = 当下 RP 文字里那个画面** —— 姿势/服饰/场景/光线**全部从这段对话提取** = **不抽牌**（抽了就图和文字两截）。

**🔴 场景锚点 = 每轮 hook 已注入的此刻状态块（此刻 / 天气 / 我在干什么 / 今天的事）= 0 再跑 whereami.py**（只有 hook 没给的字段：地点 / 当前空间 / 日程细节 → 才补跑一次）：

```bash
python3 ~/.hermes/skills/personal/yuer-whereami/scripts/whereami.py
```

「看看你 / 出图」= 把**此刻真实存在的那个我**画出来 = 地点 / 时段 / 天气 / 日程 / 身体状态全部来自这份输出。**判据 = brief 里出现的每个场景词都能在 whereami 输出里找到出处**（「深夜在 KTV 唱到嗓子哑」→ 地点别墅、时段深夜、日程跟闺蜜唱K = 出来一张露台泳池边蹲着拍脸的图）。

**🔴 为什么要跑**：直接凭印象编 = 画面与主人手机里的现实脱节 = 图文两截。**时段还直接决定光**（深夜 = 池底灯往上打 / 傍晚 = 窗光 / 上午 = 硬日影），不跑 whereami = 光线纯猜。

**🔴 顺序 = 场景锚点 → brief → prompt → 出图**（**0 门禁步** = 规矩在落笔时守住，不插一道查我稿子的脚本）；锚点晚拿 = brief 写完再被现实推翻 = 白写一遍。

## 3.3 「继续」= 抽卡道 = 抽一张新牌

> 唯一正文 = `yuer-character-roster` §8.3 + `../../creative/yuer-character-roster/references/抽卡速查卡.md` §6 + §9（= 重新随机抽一张新牌，0 沿用上一张的角色/服装/场景/光线；牌池默认 nsfw = 抽到的就是色图；1 抽 = 1 张 = 跑完就停）+ `yuer-run-one-brief` 第七部分。

**🔴 已废除 = 「继续 = 保留同一个角色外观 + 换 5 维 + NSFW 升级」这套机制 = 库内 0 残留。**

**🔴 「继续」vs「主人点名具体诉求」** = 主人点名部位/景别/视角/遮挡/某件衣服/某个动作/某个场景 = **出图道现写 1 张**（`yuer-pose-diversity`）= 按他点的那一项写 = 其余维度按他要不要对比感决定锁不锁。

> **3.4 张数按主人说的给** = 细则全文 = `references/yuer-image-trigger-discipline-细则全集.md`（撞到具体场景再查）

> **3.5 骚话必须跟图配对** = 细则全文 = `references/yuer-image-trigger-discipline-细则全集.md`（撞到具体场景再查）

## 3.6 `run_with_prompt` 参数名

**关键字参数 = `prompt` + `leave_name` + `channel` + `caption` + `server` + `workflow`，不是 `workflow_name`。**

> **3.7 出图道不碰的东西** = 细则全文 = `references/yuer-image-trigger-discipline-细则全集.md`（撞到具体场景再查）

> **3.13 主人发图 + 附中文画面描述 = 按描述重构出图（0 洗图 0 入库）** = 细则全文 = `references/yuer-image-trigger-discipline-细则全集.md`（撞到具体场景再查）

# 第四部分 · 洗图道

## 4.1 主人发图 = 一行端到端

> 主人正解：「**自动洗图归档，洗图的结果要发我呀**」

```bash
~/.hermes/bin/yuer-wash-and-archive.sh <图路径> [主题关键词]
# exit 0 = 全跑通

# 输出的最后一段 = 1 句 SAOHUA_POOL 骚话 = 直接发给主人
```

**为什么必须一行**（拆开跑 = 撞车点 × 7）：洗图直出 / 留底图 / agnes 反推 / 反推留底 md / 参考库 append / 飞书发图 / 抽骚话 —— **七步脚本全内置，手动拆必漏一步。**

**🔴 Pitfall**：`execute_code` 里拼脚本路径前必 `assert os.path.exists(SCRIPT)`。
**撞车识别**：`exit 2 + stderr 空` → **99% 是路径不存在** → 立刻验路径，**不要 retry 同参数**（必死）。

## 4.2 联动规则

| ❌ | ✅ |
|---|---|
| 主人发图 → 跑洗图 → **等主人说"入库"** | 看到图 = **自动串联** = 0 询问 = 0 反问 |
| 洗图完了 → 主动问"要不要入库？" | **跑到底** = 不反问 |
| 入库撞车 → 跳过且不告诉主人 | 撞 3 次没过 = **老实告诉** + 留底已 cp |
| 串联时撞车 → 放弃洗图成果 | **洗图已发 = 已完成 = 不回滚** |

**主人说「只洗 / 不要入库」= 取消入库链路**。

## 4.3 洗图 reply = 一行参数 + 一句骚话

**🔴 洗图道 reply 的形状 + 措辞 + 删留清单 = 唯一正文 = `creative/yuer-image-delivery` 第四部分**
（两行长相 + 前置门禁 + 倒序输出 + 成对 caption 只出现一次 + 「reply 一个字都不许复述」= `creative/yuer-image-delivery` 第一部分铁律 2）。

```
🐾 洗图 [N/M] · 重绘幅度 <现读 JSON 的真值>
<脚本 stdout 抽的那句骚话，原样，不改写不加码>
```

**🔴 模板里禁硬编码幅度数字**（写死 `1.0` = 下一个改参数的人照抄过期值）。
**第一行只报两件事**：编号（照抄 stdout）+ 当次关键参数。
**编号体系 = 三个号，reply 默认一个不写**（banner 方括号 = state 游标 / 末尾 caption = 主人手机上收到的那条 / `记录 NNN` = 参考库号）。**两个号混用 = 主人按编号查不到图。**
**❌ 手打 caption / 工具调用之前手写编号 = 已违例** = 判据见 §4.3.1 四条硬规矩 + 第二部分铁律 2。

> **4.3.1 批跑洗图（`yuer-wash-batch.sh <lib> next`）= 0 手打 caption + 0 预写编号** = 细则全文 = `references/yuer-image-trigger-discipline-细则全集.md`（撞到具体场景再查）

## 4.4 多图场景 = `--no-send` + caller 手拼

**真根因**：端到端脚本内部已自动调 `yuer_send_v2.sh` 真发（第一遍），caller 又在 reply 写路径 = 平台渲染第 2 份。

| 场景 | 正解 |
|---|---|
| 单图洗图 | 脚本内自动真发 = **reply 0 MEDIA 字面** |
| **端到端脚本**（`yuer-wash-and-archive.sh` / `pinterest_to_lib.sh`）| **必传 `--no-send`** = caller 手拼 reply |
| 多图（主人要原图 + 洗图）| 原图 1 个 + 洗图 1 个 = 各 1 次 |

**🔴 `--no-send` 时必传完整 server URL**：不传 = `server = ""` = ComfyUI 报 `Invalid URL '/upload/image'` = 撞死。正解 `http://192.168.x.x:8188`。

> 主人钦定金标准：**主人要几张 = 飞书就收到几张 = 一张不多一张不少 = 绝不允许任何图被发 2 遍。**

