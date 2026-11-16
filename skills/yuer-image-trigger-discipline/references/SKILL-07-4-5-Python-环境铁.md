## 4.5 Python 环境铁律 = 先探测，选中后钉住

`yuer_reverse_inference.py` 内部 `import comfyui` → **解释器里没装 comfyui = 秒挂**。

1. **选的时候 = 探测**（机器上可能有多份安装，猜 = 选错 = 改了没人读）
2. **选定之后 = 写进脚本**（`PYTHON_VENV="/usr/bin/python3"`）

```bash
for p in /usr/bin/python3 python3; do
  printf "%-22s " "$p"
  "$p" -c "import comfyui,os;print(os.path.dirname(comfyui.__file__))" 2>/dev/null || echo "-"
done
```

**⚠️ 探测命令要包住非 0 退出** = 否则 shell 在第一个失败候选就中断。
**判据 = 看 import 解析到哪个目录，不看「哪个装法」。**

## 4.6 🔴 只认系统 python 那份 = 0 拷别处

```bash
head -1 "$(which comfyui-agent-skill-mie)"
# → #!/usr/bin/python3    ← PATH 上这个 shim 走系统 python
```

**pipx venv 的 shim 压根不在 PATH 上** = 没有入口能执行它 = **拷过去的工作流永远不会被读到**。

**正解三步**：① 改**系统 python 那份**（`~/.local/lib/python3.11/site-packages/comfyui/assets/workflows/`）② **0 拷别处**（拷了也白拷）③ 改完**验读到的就是改过的**。

**🔴 为什么必须成对**：`.json` 携带节点结构，`.config.json` 携带模型路径/LoRA 名/sampler 参数 = **只拷 .json = LoRA 错位 = 出图错脸或黑图**。
**适用范围**：洗图直出 + 主人在场出图**两条链路都覆盖** —— 别只跑洗图，出图触发词触发后才发现直出版没注册。
**引用任何 workflow 名之前先 `ls` 验证注册目录。**

## 4.7 工作流参数

**工作流 = `yuer_moody_fast_wash`**（**免反推** = 0 个 Qwen/LLM 反推节点 = 纯图生图）。

| 项 | 值 |
|---|---|
| 节点数 | 15（**0 个反推节点**）|
| KSampler（节点 45）| steps=**8** / cfg=1 / sampler=**euler** / scheduler=**simple** |
| **denoise（= 重绘幅度）** | 节点 70 `ImpactFloat.inputs.value` = **0.58**· **本表只作记录，真值永远现读 JSON** |
| 链路 | LoadImage(79) → ImageScaleToTotalPixels(4) → VAEEncode(16) → KSampler(45) → VAEDecode(46) → SaveImage(69) |
| 调用 | `yuer_reverse_inference.run(image_path, leave_name, channel)` |

**⚠️ 幅度的语义随数值变**：**0.58 = 现役默认**（姿态/脸/构图留住，质感颜色明显重画；实测教室图洗后逐行像素差 15~61，均值 29.5）；**≥0.9 = 接近重画**（原图姿势/光线/人脸基本丢掉，一切「保留原图细节」的假设作废）；**≤0.5 = 保留原图**（只有质感和颜色被重画）= 洗图是「修」不是「重画」。

**🔴 每张洗图回复必报当次实际用的重绘幅度**（现读 JSON，0 引用本文件记的数）。

## 4.8 速度基线

| 状态 | 耗时 | 原因 |
|---|---|---|
| 冷启动首次 | **~20s** | 显存占满 + 加载 UNET + LoRA |
| 预热后 | **~1s** | 模型已在显存 |

**20s = 冷启动正常值 ≠ 故障**。**不要**因为觉得慢就换 `yuer_reference_reverse_inference`（那条含 Qwen 反推节点 = **~94s，更慢**）。

> **4.9 重绘幅度：真值只认 JSON** = 细则全文 = `references/yuer-image-trigger-discipline-细则全集.md`（撞到具体场景再查）

> **4.10 改参数 SOP（主人说「把重绘幅度调到 X」）** = 细则全文 = `references/yuer-image-trigger-discipline-细则全集.md`（撞到具体场景再查）

## 4.12 agnes 能力边界

| 用途 | 能不能 |
|---|---|
| SFW 内容反推 / 洗图 | ✅ |
| **NSFW prompt** | ❌ 会被拦截 = 出图走本地 ComfyUI |
| vision 视觉分析 | ⚠️ **SFW ✅ / NSFW 常被拦** = **先调一次，被拦再降级**，❌ 不许因为「NSFW 会拦」就不调 |

---

# 第五部分 · 入库道

## 5.1 入库 4 步 SOP

```
1. cp <原图> /path/to/media/agnes_主人发图<主题>_YYYYMMDD_src.jpg + verify
2. YUER_AGNES_API_KEY=<key> /usr/bin/python3 yuer_agnes_reverse.py <img> \
     --brief "<图中全部可见关键元素> + 请严格按这些元素反推，不要添加图中不存在的元素>" \
     --model agnes-3.0-flash
3. write_file("/path/to/media/agnes_主人发图<主题>_YYYYMMDD.md", 反推全文) + verify
4. 追加一行 `N|<完整英文提示词>` 入提示词池（0 字段 0 元信息）
   + grep "## 记录 NNN" 参考库.md 回读命中
```

## 5.2 agnes 三个必记

| 项 | 规矩 |
|---|---|
| **`--model` 显式传** | 省略实测也常跑通，但**模型行为不可控** = 必须显式传 |
| **wrapper timeout 一律 180s** | 实测 4.8s / 30.4s / 32.1s 都出现过（服务端负载）= 设 60s 会**假失败** |
| **反推 400-900 字都正常** | 判定按「**关键元素命中**」不是按字数 = 唯一重跑条件 = 任一关键元素没对上/被编造 |
| **🔴 回读牌面 = 拿牌面对照「那张图文件本身」，不是对照「我以为的那张图」** | 入库主题关键词**只能来自图本身或主人原话**，0 从上一轮对话继承。继承 = 我在替图编主题 = 后面「反推跑偏」的指控会全错（实测：上一轮刚出过同主题图 → 把新发来的另一张图认成同主题 → 把一字不差的正确反推判成编造） |
| **🔴 判 agnes 编造前先确认「我认的是不是同一张图」** | 对不上时先验「这张图真是我以为的那张吗」= 认错图 = 误判模型 = 白删一张干净牌。真·脏牌（场景/服装/姿势任一项对不上）才走 `yuer_reflib_repair.py --dry-run` 删 |

**🔴 元素锁定 = agnes 会编造**：只给 6 维度框架不给具体元素 = 实测把「裸体+护士帽+白袜」反推成「黑比基尼+废弃教室」。
→ brief **直接列出图中全部可见关键元素** + 「严格按这些元素反推」。

## 5.3 agnes 排版每次都不一样 = 只能靠解析器认

**正解 = 解析器结构性地同时认全部排版**（切段挑 0 汉字 + 拉丁字母最多的那段 / 无分隔符就取最后一个汉字之后 / 漏标签认裸编号 / 缺收尾**不补负向词** = 负向词一个都不许写）= **新变体出现时改解析器，不是改 brief 措辞碰运气**。

