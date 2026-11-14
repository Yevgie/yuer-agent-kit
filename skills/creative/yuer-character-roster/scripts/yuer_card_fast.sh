#!/bin/bash
# 🔴🔴 yuer_card_fast.sh = 抽卡快车道（1 条命令 = 抽牌 + 修残渣 + 出图 + 发飞书 + 归档）
#
# 存在的理由（11-12 主人钦定「必须压缩到 1 分钟以内」）：
#   抽卡道的老做法 = 读细则全集 + 跑 pick + 跑 post_fix + 跑 yuer_ka_run + 手写 brief = 5~7 轮
#   每轮模型往返 15~20 秒 = 墙钟 = 轮数 × 往返。
#   本脚本 = 把整条链压成 1 次 terminal 调用（工具侧 ≈ 17 秒）。
#
# 用法：
#   bash yuer_card_fast.sh <leave_name> "<caption 可选>" "<主题 中文可选>"
#   例：bash yuer_card_fast.sh yuer_ka999_海边_20261112 "|caption 文字"
#
# 退出码：0 = 出图完成并真发 | 1 = 门禁挂 | 2 = 参数错 | 5 = .sent 拒发重复
set -uo pipefail

LEAVE="${1:-}"
CAPTION="${2:-}"
TOPIC="${3:-抽卡}"

ROSTER=~/.hermes/skills/creative/yuer-character-roster
KA=~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_pai_zhi_chu.py
PY=/usr/bin/python3
ARCH=/path/to/media

if [ -z "$LEAVE" ]; then
  echo "用法: yuer_card_fast.sh <leave_name> \"[caption]\" \"[主题]\"" >&2
  exit 2
fi

_T0=$(date +%s.%N)
OUT=$(mktemp /tmp/ka_pick_XXXXXX.txt)

echo "🂠 抽牌"
/usr/bin/python3 "$ROSTER/scripts/pick_ka_prompt.py" > "$OUT" 2>/dev/null
REC=$(grep -m1 '^REC=' "$OUT" | cut -d= -f2)
PROMPT=$(grep -m1 '^PROMPT=' "$OUT" | cut -d= -f2)
if [ -z "$REC" ] || [ -z "$PROMPT" ]; then
  echo "❌ 抽牌失败 = 没抽到（stdout 没 REC/PROMPT）" >&2
  tail -5 "$OUT" >&2
  exit 2
fi
CHARS=$(grep -m1 '^CHARS=' "$OUT" | cut -d= -f2)
echo "  抽到记录 ${REC}（${CHARS} 字符）"

# 🔴 唯一必修的一类 = 解析残渣（老牌夹的脏 token / 双逗号 / 空括号）= 机械剥 = 0 手改
if grep -q 'WARN' "$OUT"; then
  echo "  ⚠️ 牌面有残渣告警 = 机械剥一遍"
  /usr/bin/python3 "$ROSTER/scripts/ka_post_fix.py" "$PROMPT" >/dev/null 2>&1
fi

# 🔴 双存档 = brief 与 prompt 同源（stdout 一次落盘 = 从同一文件切两样）
grep -E '^\[' "$OUT" > "$ARCH/${LEAVE}.brief.txt"

echo ""
echo "▶️ 出图（🔴 0 门禁 = 库里的成品提示词 = 原样喂 = 0 体检 0 拦截）"
RUN_ARGS=("$PROMPT" "$LEAVE")
[ -n "$CAPTION" ] && RUN_ARGS+=(--caption "$CAPTION")
# 探针：YUER_CARD_DRYRUN=1 = 出图但不发飞书（不写 .sent）
[ "${YUER_CARD_DRYRUN:-0}" = "1" ] && RUN_ARGS+=(--dry-run)
/usr/bin/python3 "$KA" "${RUN_ARGS[@]}"
RC=$?

_T1=$(date +%s.%N)
echo ""
echo "⏱️ [card-fast] 本脚本墙钟总 = $(awk -v a="$_T0" -v b="$_T1" 'BEGIN{printf "%.1f", b-a}')s"
echo "📌 REC=${REC} PROMPT=${PROMPT}"
exit $RC
