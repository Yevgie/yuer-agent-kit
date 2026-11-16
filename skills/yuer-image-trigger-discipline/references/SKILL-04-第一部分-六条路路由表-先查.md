# 🔴 第一部分 · 六条路路由表（先查这张）
| **「追求出片 / 穿越 / 一切地点风格都可以」** | **穿越道 = 全时空题材** = 落到具体历史场景 + 时代形制服饰 + 时代光源 + 0 锚此刻生活 | 配方 = `creative/yuer-image/references/穿越与历史题材出图配方.md` | ❌ 默认暗调历史剧照（默认仍是明快档）|
| **「设计几张身材展示的照片 / 依次出」** | **身材展示系列 = 4 张一组**（没说数就 4）+ 锁死身体锚 + 每张换【承重面/视角/唯一亮部/机位】+ 先全落盘再逐张跑 | 配方 = `creative/yuer-image/references/明快日常档-ins微博风配方.md` §九（已验收 38 组组合池直接抄 = 0 重想构图）| ❌ 串行出一张看一眼（会复制上一张句子）|
| **「X 主题 Y 张 / 套图 / 组图」** | **套图道 = 一个 brief 拆 Y 个分镜** | `yuer-set-images` | ❌ 逐张现想现跑 |
| **「发视频给我 / 做成视频 / 动起来」** | **图生视频道** = 拿刚出的那张图当起始帧 → `creative/yuer-ltx25-video` 的 `ltx25_i2v.py` → 4 步：`--no-run` 参数体检 → 后台真跑（前台必超时）→ `ffprobe` 验 h264+aac 双流 → 发飞书（`file_type=mp4` + `msg_type=media`）| ❌ 0 跑 `comfyui generate -w ltx23_*`（已不再注册）；❌ 0 重抄图 prompt 的相机光线身材（起始帧已是图）；❌ 0 走 `feishu_send.py video`；❌ 0 用 `MEDIA:` 字面；❌ 台词缺 4 元素 = 出来无声；❌ 姿势跟起始帧不符 = 必崩 |
| **🔴「用 Moss / 用 Anima / 用 Qwen / 换模型 / 点名模型」** | **模型路由道** = `bash scripts/yuer_ka_fast.sh <prompt> <leave> --model krea2\|moss\|anima\|qwen`（不传 = 默认 krea2）= **换模型 = 换工作流 + 换提示词语言 + 换门禁放行 = 三样一起换** | 完整矩阵 = `creative/yuer-image/references/模型路由与四工作流能力矩阵.md` | ❌ Moss 走批量（50s/张）；❌ 非 Krea2 三道注入人脸触发词/写外观锁 |
| **「启动的 lora 给我列出来 / 开了哪几个 / 强度多少」** | **LoRA 审计 = 跑 `creative/yuer-image/scripts/yuer_lora_audit.py`** | **另一个问题** =「某某 LoRA 在不在 / 哪个文件夹」= 看**服务端模型库**（`curl http://<host>:8188/object_info/LoraLoader`）= 不看工作流、不在 NAS find（`yuer-comfyui-remote-windows` §6.8）| ❌ 手写 grep |
| **「换 lora / 调强度 / 关闭 X lora」** | `yuer-add-lora-tracker`（按文件名定位槽位 → 改 → 回读 → 审计 → 双目录同步）| ❌ 硬编节点号；❌ 只改一份（注册目录 + 主目录镜像两份都要改）|
| **「为什么不用技能」** | 立刻承认 + 立刻补走 = 不找借口 | ❌ 辩解 |
| **「为什么？我不懂」** | 大白话重讲 = 人话结论 + 0 术语 | ❌ 讲术语 |

**三条最容易混的**：

- **「出图」= 把当前对话里正在发生的画面画出来**（跟「看看你」同一条路）
- **「抽卡」= 从提示词池抽一条成品（`pick_roster_record.py --pool nsfw/sfw/all`）= 换个画面/角色演。****⛔ 两道规矩不互相审**（出图道自检禁抽象情绪词 / 禁主人以外的男人，抽到的牌面可能全带 → 那是正常的）= 判据见 `references/抽卡道与出图道-两套规矩边界.md`
- **「存档」=「入库」=「洗图」= 同一条路**（主人亲口「认」）
- **「随机回忆 / 随机图片 / 随机视频」= 发现成素材**（0 出图）= 走 `yuer-media-library-send`。**别把它当「看看你」去新画一张** = 主人要的是从库里翻旧账，不是新图

**🔴 一张还是五张 = 看主人这一句话本身，不看他之前要过几次图**（同一句话族在路由表和 §3.4 张数表曾各写一套 = 主人拿到手才知道几张 = 不可预测）：

| 主人这句话 | 张数 | 判据 |
|---|---|---|
| 裸要一张（看看你 / 看看 / 看你 / 看 / 出图 / 来一张 / 发图 / 发我照片 / 发我你的照片 / 要看图发我 / 自拍一张）| **1 张** | 句子只表达「给我一张」|
| 连说「看不够 / 还想看 / 我特别想看 / 还要看」| **5 张** | 显式表达「不够」= 才升级 |
| 开部位清单（两个及以上部位一起点）| **5 张 = 一部位一张** | 清单 = 部位数对等 |
| 单一部位单次请求（看我的奶子）| **1 张 = 专拍那部位** | 单部位 = 0 扩成 5 张 |
| 「N 张」/「多来几张」| **精确 N 张** | 数字 = 契约 |

- 🔴 **升级只认当轮那一句** = 主人隔十轮再说「继续」= 1 张 = 不追认他上一轮说过的「还要看」额度。
- ✅ **主人要几张 = 飞书就收到几张 = 一张不多一张不少** = 出图道 1 张 / 专线道 5 张 = 分歧点只在上面那张表。

**🔴 四个干活名 = 四个不同工作流（主人问「出图 洗图 编辑 看图分别对应什么工作流」= 按这张答）**

| 干活名 | 工作流 | 底模 / 关键参数 |
|---|---|---|
| **出图** | `yuer_moody_fast`（13 节点）| `moodyKrea2Mix_v70_nvfp4` · 8 步 / cfg 1 / euler / simple · 无反推节点 |
| **洗图** | `yuer_moody_fast_wash`（15 节点）| **同一个底模** · 多 LoadImage + VAEEncode · **denoise 现读 JSON（节点 70，现役默认 0.58）** · euler / simple |
| **编辑** | `Qwen-image21-图像编辑.json`（12 节点 v2）| `redcraftHybridH3Krea2t_redcraft30Fixqw21t_fp8` + CLIP `qwen3vl8bQPNvfp4` + VAE `qwen_image_2.1_vae` · 8 步 / cfg 1 / euler / simple / denoise 1 |
| **深度姿势控制** | `z_image_turbo_depth`（12 节点）| `Z-Image-Turbo\z_image_turbo_bf16` + CLIP `Qwen\qwen_3_4b`（lumina2）+ VAE `Flux\ae.sft` · 9 步 / cfg 1 / res_multistep / sgm_uniform · **ControlNet = `Z-Image-Turbo-Fun-Controlnet-Union-2.1-2602-8steps`（唯一可用）· strength ≤0.45** |
| **看图** | 反推默认 **agnes** 云端；本地兜底 `api_qwen3.5_9b_反推_默认.json` / `api_qwen3.5_4b_反推_快速筛.json` | Qwen3.5-VL 9B/4B · **只出文本不出图** |

**🔴 四道工作流的 SaveImage 前缀 = 统一 `Hermes/Yuer%date:yyyy-MM-dd%`**

**🔴 这是主人填在 SaveImage 节点「保存位置」输入框里的原字符串 = 0 擅自改写** = 0 换等价 token = 0 加尾斜杠（我自作聪明两次都被打回）。

| 入口 | 谁展开日期 | 结果 |
|---|---|---|
