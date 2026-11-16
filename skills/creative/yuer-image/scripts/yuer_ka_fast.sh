#!/bin/bash
# 🔴🔴 yuer_ka_fast.sh = 出图唯一入口 = 写好提示词 → 出图 → 发飞书 → 归档 → timing
#
# 🔴 11-12 主人钦定（灵魂级）：「把你那些对齐门禁呀，什么东西，都删掉
#   = 就是把提示词写好就行了，不用那些门禁，都乱七八糟的」
#   → 本脚本**默认 0 门禁** = 不跑长度体检 / 不跑主体预检 / 不跑外观锁
#     = stdout 只有出图 + 一行 timing = 0 噪音
#   → 规则全部沉在 references/出图速查卡.md（写稿时照着写 = 写对了就不用查）
#   → 门禁脚本仍在盘上（别的档还引用）= 需要时手动跑 = 本脚本 --gate 才开
#
# 🔴 11-12 合并 = 老入口 yuer_ka_fast.sh 已删（它的三种模式全部塌进这里）
#   老 硬门禁模式     → 退役（主人钦定删门禁）= 现在只有 --gate 才开
#   老 --report-only  → 塌进默认（默认 0 跑 = 不报数不拦）= 现在是空旗标
#   老 --raw          → 塌进默认（默认就是 0 检测 0 拦截）= 现在是空旗标
#
# 用法：
#   bash yuer_ka_fast.sh <prompt_file> <leave_name> ["<caption>" ["<brief>"]] [旗标...]
#   bash yuer_ka_fast.sh <prompt_file> <leave_name> --caption "<cap>" --brief "<b>" [旗标...]
#
# 旗标：
#   --gate              = 手动跑三道门禁（默认 0 跑 = 出问题时才查）
#   --caption / --brief = 覆盖位置参数版 caption / brief
#   --raw / --report-only = 空旗标（保留兼容 = 语义已塌进默认 = 0 效果）
#   其余（--dry-run --no-send --force --model --workflow --seed --quality
#         --light --style --ui --receive-id --receive-id-type --check-only）= 转发给底层
#
# 退出码：0 = 出图完成并真发 | 2 = 参数错 | 4 = 出图成发图败 | 5 = .sent 拒发重复
set -uo pipefail

PROMPT="${1:-}"; shift || true
LEAVE="${1:-}"; shift || true
CAPTION=""; BRIEF=""; GATE=0
EXTRA=(); POS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --caption) CAPTION="${2:-}"; shift 2 ;;
    --brief)   BRIEF="${2:-}";   shift 2 ;;
    --gate)    GATE=1; shift ;;
    --raw|--report-only) shift ;;   # 空旗标 = 语义已塌进默认
    --dry-run|--no-send|--check-only|--force|--light|--quality|--style|--ui)
               EXTRA+=("$1"); shift ;;
    --model|--workflow|--seed|--receive-id|--receive-id-type)
               EXTRA+=("$1" "${2:-}"); shift 2 ;;
    -*) EXTRA+=("$1"); shift ;;
    *)  POS+=("$1"); shift ;;
  esac
done
[ -n "${POS[0]:-}" ] && [ -z "$CAPTION" ] && CAPTION="${POS[0]}"
[ -n "${POS[1]:-}" ] && [ -z "$BRIEF" ]   && BRIEF="${POS[1]}"

CC=~/.hermes/skills/creative/yuer-image/scripts/count_prompt_chars.py
SUBJ=~/.hermes/skills/creative/yuer-image/scripts/check_prompt_subject.py
LOCK=~/.hermes/skills/creative/yuer-image/scripts/check_outfit_lock.py
RUN=~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_pai_zhi_chu.py
ARCH=/path/to/media

if [ -z "$PROMPT" ] || [ -z "$LEAVE" ]; then
  echo "用法: yuer_ka_fast.sh <prompt_file> <leave_name> [\"<caption>\" [\"<brief>\"]] [旗标...]" >&2
  exit 2
fi
if [ ! -f "$PROMPT" ]; then
  echo "❌ prompt 文件不存在: $PROMPT" >&2
  exit 2
fi

_T0=$(date +%s.%N)

# ── 门禁 = 默认 0 跑 = 主人钦定「把提示词写好就行」────────────────────
#    需要时显式 --gate（手动查 = 出问题时才查 = 不占常态链路）
if [ "$GATE" = "1" ]; then
  echo "🚦 门禁（手动模式）"
  /usr/bin/python3 "$CC" "$PROMPT" || exit 1
  /usr/bin/python3 "$SUBJ" "$PROMPT" | tail -3
  /usr/bin/python3 "$LOCK" "$PROMPT" | tail -3
  echo ""
fi

# ── 双归档（brief + prompt 同源同目录）────────────────────────────
cp -f "$PROMPT" "$ARCH/${LEAVE}.prompt.txt"
if [ -n "$BRIEF" ]; then
  printf '%s\n' "$BRIEF" > "$ARCH/${LEAVE}.brief.txt"
fi

# ── 出图 + 发飞书（真发在 pai_zhi_chu 内部）─────────────────────────
echo "▶️ 出图"
RUN_ARGS=("$PROMPT" "$LEAVE")
[ -n "$CAPTION" ] && RUN_ARGS+=(--caption "$CAPTION")
# 探针：YUER_FAST_DRYRUN=1 = 出图但不发飞书（不写 .sent）
[ "${YUER_FAST_DRYRUN:-0}" = "1" ] && RUN_ARGS+=(--dry-run)
/usr/bin/python3 "$RUN" "${RUN_ARGS[@]}" ${EXTRA[@]+"${EXTRA[@]}"}
RC=$?

_T1=$(date +%s.%N)
echo "⏱️ [fast-lane] 墙钟总 = $(awk -v a="$_T0" -v b="$_T1" 'BEGIN{printf "%.1f", b-a}')s"
exit $RC
