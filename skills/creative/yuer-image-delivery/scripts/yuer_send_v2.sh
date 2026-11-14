#!/bin/bash
# yuer_send_v2.sh · v2.1 SOP 终极版 (07-11 实战打脸后钦定·盖过 yuer_send_safely.sh)
# 唯一职责 = 调 hermes send 发图 + 4 件套自检 + caption 嵌消息 + env -u 清代理
# 用法：bash yuer_send_v2.sh <media_path> <caption> [target]
# 示例：bash yuer_send_v2.sh /tmp/yuer.png "主人看～嘿嘿 ✨"
# 默认 target = feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d
# 返回 exit code 0 = 成功，1 = 4 件套自检失败，2 = 参数错误
set -euo pipefail

# ========== 参数验证 ==========
if [ $# -lt 2 ]; then
    echo "ERR: 用法: bash $0 <media_path> <caption> [target]" >&2
    echo "示例: bash $0 /tmp/yuer.png '主人看～嘿嘿'" >&2
    exit 2
fi

MEDIA_PATH="$1"
CAPTION="$2"
TARGET="${3:-feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d}"

if [ ! -f "$MEDIA_PATH" ]; then
    echo "ERR: file not found: $MEDIA_PATH" >&2
    exit 1
fi

# ========== 实战 277 物理机制层守卫（07-31）：.sent 标记检测 = 防重复发图 ==========
# 真根因（盖过实战 272d/274 一切）：之前 run() 内部已发图，调用方又手动调 = 重复发
# 整改 = 改机制不靠嘴：run() 发过的图写 <img>.sent → 本脚本检测到立刻拒发
# ⚠️ 只有 yuer_run_one_image.run() 端到端出来的图才有 .sent（手动放进去的图没有，正常发）
SENT_MARKER="${MEDIA_PATH}.sent"
if [ -f "$SENT_MARKER" ]; then
    echo "ERR: [实战 277 守卫] 这张图已经发过了！.sent 标记存在: $SENT_MARKER" >&2
    echo "  → run() 端到端内部已经发图，调用方不要再手动调 yuer_send_v2.sh" >&2
    echo "  → 如果想再发一次，请先删掉 .sent 标记（手动覆盖模式）" >&2
    exit 1
fi

# ========== 4 件套自检（违规=立刻退出 1，不让发图）==========
ERRORS=()

# 件套 1: caption 不能含路径字符串
if echo "$CAPTION" | grep -qE "/vol2/|/comfyui-output/|/tmp/|~/"; then
    ERRORS+=("caption 含路径字符串")
fi

# 件套 2: caption 不能含文件扩展名
if echo "$CAPTION" | grep -qE "\.png|\.jpg|\.jpeg|\.webp"; then
    ERRORS+=("caption 含 .png/.jpg 文件扩展名")
fi

# 件套 3: caption 不能含 MEDIA: 字面字符串（会触发飞书 SDK 双图 bug）
if echo "$CAPTION" | grep -q "MEDIA:"; then
    ERRORS+=("caption 含 MEDIA: 字面字符串（触发双图 bug）")
fi

# 件套 4: caption 不能含占位符/已发暗示词
if echo "$CAPTION" | grep -qE "Sent|已发|sent verified|sent successfully|sent message|\[图片\]|\[Result\]"; then
    ERRORS+=("caption 含占位符/已发暗示词")
fi

if [ ${#ERRORS[@]} -gt 0 ]; then
    echo "ERR: 4 件套自检失败：" >&2
    for e in "${ERRORS[@]}"; do
        echo "  - $e" >&2
    done
    echo "" >&2
    echo "caption 必须是：主人视角 + 骚话 + 三件套 + 0 路径/0 文件名/0 MEDIA:/0 占位符" >&2
    exit 1
fi

# ========== 4 件套自检通过，正式发图 ==========
unset all_proxy ALL_PROXY http_proxy https_proxy

# v6.12 整改（07-21 实战 164）= caption 写文件 + MEDIA 走 -f 第一行 + stdin 不再用
# 真根因：旧版 MSG="caption MEDIA:path" → hermes SDK 看到 message 含 MEDIA 字面双渲染
# 整改：caption 单独写文件，MEDIA 拼到 -f 第一行，用 stdin stage 文件传给 hermes
CAPTION_FILE="/tmp/yuer_caption_$$.txt"
echo "$CAPTION" > "$CAPTION_FILE"

STAGE_FILE="/tmp/yuer_stage_$$.txt"
printf 'MEDIA:%s\n' "$MEDIA_PATH" > "$STAGE_FILE"
cat "$CAPTION_FILE" >> "$STAGE_FILE"

# v6.12 stdout 守门：必须含 MEDIA 真信号（实测 07-21：旧版 stdout 空 = 幂等跳过的复发温床）
RESULT=$(unset all_proxy; hermes send --to "$TARGET" -f "$STAGE_FILE" -q 2>&1)
RC=$?
rm -f "$CAPTION_FILE" "$STAGE_FILE"

# v6.11 stdin stage 文件守门：第一行必是合法 MEDIA: 路径
# 实战 525b 整改：不再 echo MEDIA 到 stdout —— 真发由 hermes send 完成，
# stdout 里的 MEDIA: 字面会让 Hermes 平台再发一遍 = 重复发图
if [ "$RC" = "0" ]; then
    exit 0
else
    echo "ERR: hermes send RC=$RC: $RESULT" >&2
    exit 1
fi
