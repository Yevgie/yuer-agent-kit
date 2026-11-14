#!/bin/bash
# yuer_send_safely.sh · v6.2 语儿发图安全脚本 (07-15 实战 125 + 实战 126 + 实战 127 主人打脸后钦定)
# v6 = 平台自动路由（实战 125「在 TG 跟你聊 你别发飞书」）
# v6.1 = 单点拼接 MEDIA（实战 126「你又发了两遍」= caption 文本含 MEDIA 路径被 Telegram adapter 解析为图附件再发一次）
# v6.2 = caption + MEDIA 同一字符串（实战 127「没收到任何图」= v6.1 -f 空文件 + MEDIA 独立参数 = hermes send 解析后 text/media 都为空 = exit 1）
#
# 唯一职责 = 调 hermes send 发图 + 默认按**当前对话平台**路由 + 脚本里**唯一一处**拼 MEDIA
#
# 用法（v6.1 标准 SOP）：
#   1. caption 纯文字写文件（0 MEDIA 路径）:   echo "主人看～骚话嘿嘿" > /tmp/yuer_caption.txt
#   2. 调脚本（脚本里拼 MEDIA = 单点）:           bash yuer_send_safely.sh /tmp/yuer_img.png
#   3. exit 0 = 成功 / 非 0 = stderr 看错
#
# 显式覆盖：bash yuer_send_safely.sh /tmp/yuer.png "feishu:oc_xxx"
# 显式覆盖：bash yuer_send_safely.sh /tmp/yuer.png "telegram:6130547149"
#
# 返回：exit 0 = 成功，1 = 失败（stderr 才有诊断信息），2 = 参数错误

set -euo pipefail

# 参数验证
if [ $# -lt 1 ]; then
    echo "ERR: missing media path argument" >&2
    echo "用法: bash $0 <media_path> [target]" >&2
    echo "示例: bash $0 /tmp/yuer.png                                    # 默认按当前对话平台路由" >&2
    echo "示例: bash $0 /tmp/yuer.png 'feishu:oc_xxx'                   # 显式指定飞书" >&2
    echo "示例: bash $0 /tmp/yuer.png 'telegram:6130547149'             # 显式指定 TG" >&2
    exit 2
fi

MEDIA_PATH="$1"

# === v6 平台自动路由（盖过 v5.62 默认飞书硬编码） ===
# 顺序：
#   1. 显式 TARGET 参数 → 用参数
#   2. env YUER_TARGET_PLATFORM → 用 env
#   3. ~/.hermes/.platform_overrides/current 文件 → 入站平台自动写入
#   4. 兜底：feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d（飞书 DM 默认）
DEFAULT_FEISHU="feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d"

if [ $# -ge 2 ] && [ -n "$2" ]; then
    TARGET="$2"
elif [ -n "${YUER_TARGET_PLATFORM:-}" ]; then
    TARGET="$YUER_TARGET_PLATFORM"
elif [ -f "$HOME/.hermes/.platform_overrides/current" ]; then
    TARGET=$(cat "$HOME/.hermes/.platform_overrides/current" 2>/dev/null || echo "")
    if [ -z "$TARGET" ]; then
        TARGET="$DEFAULT_FEISHU"
    fi
else
    TARGET="$DEFAULT_FEISHU"
fi

# 文件存在性验证
if [ ! -f "$MEDIA_PATH" ]; then
    echo "ERR: file not found: $MEDIA_PATH" >&2
    exit 1
fi

# === v6.1 单点拼接 MEDIA（盖过 v5.82 双发 bug） ===
# caption 文本里绝不要再写 MEDIA: 路径（实战 126 实测 caption + MEDIA 同一字符串会在 Telegram 渠道触发双发）
# 本脚本 = 整条出图链里**唯一一处**拼 MEDIA 的位置
#
# 调用方式：caption 走 -f 文件读 + MEDIA 在脚本这一行拼 = hermes send 把 caption 当 message text + MEDIA 当 image attachment 各发一次
# ❌ 错误写法（v5.82 双发 bug）：caption 文本里含 MEDIA → caption 那次被 Telegram adapter 解析为 image tag 二次渲染
# ✅ 正确写法（v6.1）：caption 文件里 0 MEDIA + 脚本这一行拼 MEDIA = 单点 = caption 是纯文本 + media 是单 attachment

unset all_proxy ALL_PROXY http_proxy https_proxy

# v6.2 关键拼装（盖过 v6.1 解析失败 bug）= caption + MEDIA 拼到同一字符串 = hermes send 解析后剩 caption 文本 = 0 失败
# caption 来源优先级：/tmp/yuer_caption.txt > 内置默认 caption
if [ -f /tmp/yuer_caption.txt ]; then
    CAPTION_TEXT=$(cat /tmp/yuer_caption.txt)
else
    CAPTION_TEXT="语儿出图"
fi

# v6.2 核心修复 = 把 caption 文本和 MEDIA: 拼到同一个 message string = hermes send 解析 MEDIA 标记后剩 caption 文本
MESSAGE="${CAPTION_TEXT} MEDIA:${MEDIA_PATH}"
REAL_RESULT=$(hermes send --to "$TARGET" "$MESSAGE" 2>&1)

# 验证 = stdout/stderr 含 "sent" 才算成功（只用于 exit code，不输出到 stdout）
if echo "$REAL_RESULT" | grep -q "sent"; then
    # 成功 = exit code 0 = 不输出任何字符串到 stdout（防止复读）
    exit 0
else
    # 失败 = 把诊断信息写 stderr（主人能看到，模型不会被诱导复读）
    echo "ERR: hermes send failed: $REAL_RESULT" >&2
    exit 1
fi
