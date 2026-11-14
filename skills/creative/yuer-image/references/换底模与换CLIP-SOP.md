本档 = yuer-image 正文「换 CLIP / 文本编码器 SOP」的实施细则

① 主人给的是 Windows 绝对路径 = 服务端认的是**带子目录的相对名**（`Qwen\qwen3vl_4b_fp8_scaled.safetensors` = 反斜杠子目录 + 文件名，**0 用 Linux 路径**）
② `curl http://<host>:8188/object_info/CLIPLoader` 拉服务端**真实选项列表** + `type` 的合法取值（`krea2` / `qwen_image` / `ltxv` …）= **0 抄主人给的路径 = 0 猜 type**
③ 按 `class_type == "CLIPLoader"` 定位节点（**节点号每份工作流不同 = 0 硬编码**：主路 = 节点 755 / 洗图道 = 节点 9）
④ **`type` 字段 0 动**（同一个模型换份权重 = type 不变 = 改了反而接不上）
⑤ **VAE 节点 0 碰**（`qwen_image_vae.safetensors` 是 VAE 不是文本编码器 = 混淆 = 白改）
⑥ **改两份**（主路 + 洗图道）= 只改一份 = 洗图跑的还是旧 clip = 静默漂移
⑦ 改前备份（带时间戳）→ **两条道各真跑一次**（出图道 = `yuer_ka_fast.sh --dry-run`；洗图道 = `import yuer_reverse_inference; run(..., no_send=True)`）→ **测试产物自己删**（含 `.sent` / `.prompt.txt`）
⑧ 验收 = **验证图真出来**（新 clip 加载失败 = 提交报错，不会出图）= 比回读更快拿到信号
