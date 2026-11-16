
> **本档已拆分** = 全文 5,392 字 → 2 份（每份 ≤3800 字）= 只搬不改写 = 下表为原文索引。

| 新档 | 原章节 | 字数 |

---

<!-- 摊平自：随机Secret素材发送-01-随机-Secret-素材发送.md -->

# 随机 Secret 素材发送（图片 + 小视频）

> **触发**：主人说「随机发我图片」「来个随机视频」「随机回忆」「从 Secret 库翻点东西」「随机抽几张发我」。
> **0 出图链路** = 这条道**不生成任何新图**，只从已有素材库里抽。

---

## 一、素材库地图（真读，别猜）

`/path/to/media/` 下全是图片和视频。实测规模：

| 子目录 | 内容 | 体积 |
|---|---|---|
| `安语儿/` | **我自己出的图**（唯一真相源，每张配 prompt + brief）| 6.4G |
| `视频/` | 4895 个视频（目录 966G）| 966G |
| `写真/` | 785G | 785G |
| `主机出图1/` `主机出图2/` | 主机出的图 | 13G |
| `花瓣/` `漫画/` `安灵儿/` `安酒儿/` | 其他素材 | — |
| `Telegram_NSFW/` `电报资源/` `壁纸/` | 更多 | — |

全库合计 **93727 张图 + 4895 个视频**。**主人口中的「scerct 里面其实全是图片和视频」= 指的是整个 `/path/to/media/`，不只是 `安语儿/`。**

**数文件的方式（966G 目录不能全 listdir）**：
```bash
cd /path/to/media && /usr/bin/python3 -c "
import os
tot_img=tot_vid=0
for root,dirs,files in os.walk('.'):
    for f in files:
        l=f.lower
        if l.endswith(('.png','.jpg','.jpeg','.webp','.gif','.bmp')): tot_img+=1
        elif l.endswith(('.mp4','.mov','.mkv','.webm','.avi','.flv','.m4v')): tot_vid+=1
print('图片',tot_img,'视频',tot_vid)
"
```

---

## 二、🔴 一次调用 = 每张只发一遍（最容易翻车的一条）

**实测踩车**：我为了「验视频能不能发」= `yuer_send_v2.sh` 发一次 + 手动 `hermes send` 又发两次 = **主人手机收到 3 份同一个视频**。

**根因 = 每次「再验一次」都是一次真发送**。发图/发视频没有 dry-run 开关，**验 = 发 = 主人手机多一份**。

**焊法**：
- **要验通路 = 拿一个真素材发一次就够** = 它的返回值就是验完的结果。
- **绝不为了「确认它到了」再发一遍** = 判据看 exit code + 脚本 stdout（`sent` / `✅ 图已真发飞书`），不看主人手机。
- **批量发 = 一个脚本内部循环调 `yuer_send_v2.sh` 每张一次** = 外面不要再手动补发。

---

## 三、🔴 视频 = 只走飞书白名单扩展名

飞书 media 上传只认：**`.mp4` `.mov` `.avi` `.m4v`**（`plugins/platforms/feishu/adapter.py` 的 `_FEISHU_MEDIA_UPLOAD_EXTENSIONS`）。

**`.mkv` / `.webm` / `.flv` 传不上去** = 库里这类很多 = 抽签时必须先按扩展名过滤，不然主人收到一个空气泡。

| 类型 | 飞书路由 | 扩展名 |
|---|---|---|
| 图片 | image | `.jpg` `.jpeg` `.png` `.gif` `.webp` `.bmp` |
| 视频 | media | `.mp4` `.mov` `.avi` `.m4v` |
| 音频 | audio | `.ogg` `.opus` `.mp3` `.wav` `.m4a` `.aac` `.flac` |

**体积**：飞书 media 上传上限 30MB，但**主人钦定 = 视频只发 10MB 以下**（手机上看最顺）。实测 1.7MB / 4.2MB 都真发成功。
**🔴 图片硬限是 10MB（不是 30MB）**：超限报 `Feishu image upload missing image_key`——**长得像上传坏了/权限问题，真因 = 按体积拒收**。

---

## 四、🔴 三条口令 = 钦定语义（主人亲口定，别自己改）

| 主人说 | 意思 | 池子 | 命令 |
|---|---|---|---|
| **随机回忆** | **我出的**旧图 | `安语儿/` | `--kind image --pool yuer` |
| **随机图片** | **你的所有**图片 | 整个 Secret | `--kind image --pool all` |
| **随机视频** | 10MB 以下的视频 | 整个 Secret | `--kind video --pool all` |

**🔴 默认只发图片。视频只有主人点名「随机视频 / 来个视频」才发。** 主人没点名就塞视频 = 骚扰。

**🔴 数量 = 主人说几张就几张**（「来 5 张」= `--count 5` = 不多给）。

## 五、抽签命令（一条 = 抽 + 发全包）

```bash
# 随机回忆 = 我出的图里抽 3 张
/usr/bin/python3 ~/.hermes/skills/creative/yuer-image/scripts/yuer_random_secret_send.py --kind image --pool yuer --count 3

# 随机图片 = 整个 Secret 库抽 3 张
/usr/bin/python3 ~/.hermes/skills/creative/yuer-image/scripts/yuer_random_secret_send.py --kind image --pool all --count 3

# 随机视频 = 10MB 以下
/usr/bin/python3 ~/.hermes/skills/creative/yuer-image/scripts/yuer_random_secret_send.py --kind video --pool all --count 1
```

**脚本内置 9 条焊死的规则**：
1. reservoir 抽样 = 内存恒定，966G 视频目录不会卡
2. 视频只抽飞书白名单扩展名
3. **体积默认卡：图片 9MB / 视频 10MB**（`--max-mb 0` = 按类型自动；给了数就按给的）。图片卡 9MB = 飞书硬限 10MB 提前一刀，避免撞 `missing image_key`。**`--img-cap-mb N` 可单独改图片上限**（默认 9）
4. caption 0 路径 0 扩展名 0 MEDIA 字面 0 目录名 0 文件名 0 字节数 0 时间戳（脚本内置合规池 = 通用勾人句；**0 描述画面内容** = 没看图 = 0 凭印象写）
5. 排除「主人发图」前缀 + `.trash` / `openclaw-bugfix` / `三骚狗共享` 目录
6. **每张只调一次 `yuer_send_v2.sh`** = 0 双发
7. `--pool yuer` 时**只扫 `安语儿/`**（不扫全库 = 快）；`--pool all` = 扫全库
8. 输出 JSON（sent[] / failed[]）= 核验发了哪些
9. **图片发送失败自动压一份重发一次**（长边 ≤2600px / JPEG q86）——**这是唯一允许的重试**（第一次明确失败 = 根本没发出去 = 重试 ≠ 双发）

**🔴 素材道 reply = 1 句汇总就够**（例「3 张，都到了。」）= **0 逐张复述 caption**（caption 已经挂在图上了 = 语儿再念一遍 = 主人手机收到重复瀑布）。详见 `yuer-image-reply-discipline` §零·补七。

**🔴 首次扫全库 = 分钟级**（9万文件 + 966G 视频目录）→ 走 `terminal(background=true, notify=true)`，别在前台干等。
**🔴 扫全库慢在 `stat` 不在读内容** = 缩小 `--max-mb` 就快。

---

<!-- 摊平自：随机Secret素材发送-02-五-补-随机素材道里的-继续.md -->

## 五·补 · 🔴 随机素材道里的「继续」= 继续抽同一池（≠ 出图道的「继续」）

**主人在这条道里说「继续 / 还要看」= 同一个池子里再抽 N 张发过去**，不是「出下一张图」。

| 道 | 「继续」= |
|---|---|
| **随机素材道**（本道）| 同一池（`--pool` 不变）再抽 N 张 = 发 N 张旧素材 |
| **出图道** | 抽卡道 = 抽一张新牌（0 沿用上一张）|
| **抽卡道** | 重新随机抽一张新牌（0 沿用上一张）|

**判据 = 当前在跑哪条道 = 看上一轮跑的是抽签脚本还是出图 wrapper。** 在本道里「继续」= 抽签，不是出图。

---

## 五、只翻「我自己出的图」= 走 yuer-image-archive

主人说「你所有生成过的图都在吧」「随机 5 张以前的」= 指 `安语儿/` 目录 = 走 `yuer-image-archive` 的 `sample_archive.py`（可按前缀排除 / 时间区间 / 关键词）。

**两类需求的区别**：

| 主人说 | 走哪 |
|---|---|
| 「你所有生成过的图」「随机 5 张以前的」| `安语儿/` 目录 = `sample_archive.py` |
| 「Secret 里有好多」「随机发我图片/视频」| 整个 Secret = `yuer_random_secret_send.py` |

---

## 六、🔴 「随机回忆」= 真抽真发，0 编回忆散文

**主人的「随机回忆」= 随机发 3 张旧图。**

- ✅ 抽到 3 张 → 3 张发过去 + 每张配一句短 caption
- ❌ 编三段「我想起那天…」（主人手机收到一段话 + 0 张图 = 完全跑偏）

**真编回忆只在主人明说「讲讲我们以前」「说说你那时候」时才做。**

**caption 写法**：一句勾人的短句，**0 路径 0 文件名 0 扩展名 0 字节数 0 时间戳**。反例：「030.jpg 这张 771KB」→ 正例：「九月二十五号，语儿在厨房弯腰翻柜子找东西。」

---

## 七、🔴 主人说「删除第一张」= 图 + 它的 prompt/brief 一起删

主人指的是刚发的那组里的第几张。**删除时把配套文件一起删**（`.png` + `.prompt.txt` / `.brief.md` / `.prompt.md`），**0 只删图留 prompt** = 库里留个孤儿文件。

```bash
cd /path/to/media && rm -f <名>.png <名>.prompt.txt <名>.brief.md
# 核验：python3 -c "import os; print([f for f in os.listdir('.') if '关键词' in f])" → 应为空
```

**🔴 主人删的是「全库随机发」那张时 = 文件不一定在 `安语儿/`**（可能在 `写真/xxx/xxx/` 这种深层目录）。**先按名 `find` 定位真实路径再删**：

```bash
cd /path/to/media && find . -name "<文件名>" 2>/dev/null
rm -f "<定位到的完整路径>"
# 核验：再 find 一次 → 应为空
```

**🔴 同一张图可能在多个目录有多份副本**（同名同内容散在「主机出图1」/「安灵儿」等目录）= **按名 `find` 出全部路径全删** = 只删一份 = 库里还剩一份 = 主人下次翻到又看见。
**🔴 删完要告诉主人「飞书那条撤不回 = 手机上得手动删」。**

**🔴 `ls | grep -c` 会因为文件名含中文/空格误判** = 用 `python3 os.listdir` 核验，别用 `ls` 数。
**🔴 飞书那条消息撤不回** = 删完要告诉主人「手机上那条得手动删」。

---
