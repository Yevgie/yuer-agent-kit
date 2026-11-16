#!/usr/bin/env bash
# ka_batch_run.sh = 批量抽卡出图 = manifest + caption 表 → 串行出图 + 真发飞书
#
# 用法
#   bash ka_batch_run.sh <manifest.tsv> <captions.tsv> [输出后缀]
#
#   manifest.tsv : REC<TAB>prompt文件路径          ← ka_batch_pick.py / ka_pick_clean.py 出
#   captions.tsv : REC<TAB>caption<TAB>主题中文    ← 逐张盲写（从该张 prompt 文件读牌面写）
#   输出后缀      : 默认 yuer_ka<REC>_<主题>_<日期>
#
# 规则
#   ① 0 门禁 = 牌面原文直接喂 = 0 查档 0 改写 0 补参数
#   ② caption 必逐张（烧在图上 = 共用一个 = N 张里 N−1 张图文两截）
#   ③ 串行 = 0 并发（ComfyUI 抢显存 + 落盘名撞）
#   ④ caption 缺行 = 拿主题顶 + 打出警告（不静默丢卡）
#   ⑤ 🔴 首次用 = 先拿 1 张试跑确认 = 别一次上 5 张（这层是包装，底层出图链路另算）
#
# 退出码：0 = 全部出图完成 | 1 = 参数错
set -uo pipefail

MANIFEST="${1:-}"
CAPTIONS="${2:-}"
SUFFIX="${3:-}"
FAST=~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh

if [ -z "$MANIFEST" ] || [ -z "$CAPTIONS" ] || [ ! -f "$MANIFEST" ] || [ ! -f "$CAPTIONS" ]; then
  echo "用法：ka_batch_run.sh <manifest.tsv> <captions.tsv> [后缀]" >&2
  echo "  manifest: REC<TAB>prompt路径   captions: REC<TAB>caption<TAB>主题" >&2
  exit 1
fi

D=$(date +%Y%m%d)
OK=0; FAIL=0

while IFS=$'\t' read -r REC PF; do
  REC="${REC:-}"; PF="${PF:-}"
  [ -z "$REC" ] && continue
  # manifest 只给 REC 时 = 按惯例路径找牌面文件
  [ -z "$PF" ] && PF="/tmp/ka_${REC}_prompt.txt"
  if [ ! -f "$PF" ]; then
    echo "❌ REC=$REC prompt 文件不存在：$PF" >&2
    FAIL=$((FAIL+1)); continue
  fi
  # 找这张卡的 caption / 主题
  CAP=""; TOPIC=""
  while IFS=$'\t' read -r c_rec c_cap c_topic; do
    c_rec="${c_rec:-}"; c_cap="${c_cap:-}"; c_topic="${c_topic:-}"
    [ "$c_rec" = "$REC" ] || continue
    CAP="$c_cap"; TOPIC="$c_topic"; break
  done < "$CAPTIONS"
  if [ -z "$CAP" ]; then
    echo "⚠️ REC=$REC 没写 caption = 拿主题顶上（图文可能两截）" >&2
    CAP="${TOPIC:-抽卡}"
  fi
  [ -z "$TOPIC" ] && TOPIC="抽卡"

  LEAVE="yuer_ka${REC}_${TOPIC}${SUFFIX:+_${SUFFIX}}_${D}"
  echo "── REC=${REC} ${TOPIC}"
  OUT=$(bash "$FAST" "$PF" "$LEAVE" --caption "$CAP" --brief "$TOPIC" 2>&1)
  if echo "$OUT" | grep -q "已真发飞书"; then
    echo "$OUT" | grep -E "落盘|timing"
    OK=$((OK+1))
  else
    echo "$OUT" | tail -5
    FAIL=$((FAIL+1))
  fi
done < "$MANIFEST"

echo ""
echo "✅ 完成：成功 $OK / 失败 $FAIL"
[ "$FAIL" -eq 0 ]
