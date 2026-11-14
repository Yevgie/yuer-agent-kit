#!/usr/bin/env python3
"""yuer_image_constants.py · 出图链路共享常量

11-07 死代码清理：旧 PREFIX 拼装（build_yuer_prefix / YUER_GIRL_FULL_PREFIX）、
Krea2 no-text 锚点、DEPRECATED 反推常量、9 大穿搭池、旧 workflow 名
`moody_nsfw_yuer_krea2_v4_fast`、旧采样参数全部删除。
外部只有 DEFAULT_COMFYUI_SERVER 被 import（yuer_ka_pai_zhi_chu / ltx25_i2v /
ltx25_ia2v_audio）= 其余 0 调用（yuer_run_one_brief 明文 ❌ 不走本文件拼装）。

底模 / LoRA / 采样器真值 = 现读工作流 JSON（0 在本文件写死 = 写了就漂）。
"""

DEFAULT_COMFYUI_SERVER = "http://192.168.x.x:8188"
