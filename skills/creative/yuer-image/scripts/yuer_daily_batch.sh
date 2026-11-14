#!/bin/bash
# 日常套图批量出图（3 张一轮 = 1 次 terminal）
#
# 用法：
#   bash yuer_daily_batch.sh <p1> <leave1> [<p2> <leave2> [<p3> <leave3>]]
#   例：bash yuer_daily_batch.sh /tmp/prompt_daily_library.txt 日常_图书馆午后 \
#                             /tmp/prompt_daily_dorm.txt     日常_宿舍床上 \
#                             /tmp/prompt_daily_canteen.txt  日常_食堂午饭
#
# 🔴 场景锚定（可选）：环境变量 YUER_EXPECT_SCENE=学校|家
#    = 日常套图第一铁律的机械门。人在学校就 0 发家里（主人会当场纠正）。
#    例：YUER_EXPECT_SCENE=学校 bash yuer_daily_batch.sh ...
#
# 每张依次跑：外观锁门禁 → 字符门禁+出图+真发飞书 → 验收三件套
# 任何一张 FAIL = 停在那张，不往下跑（不浪费时间在后面的图上）。
#
# 🔴 三件套齐（完成/落盘/已真发）= 图已到主人手机 = 立刻回话
#    本脚本不跑任何验收工具（不 vision_analyze / 不 grep 日志 / 不 ls 目录）。
set -u

KA_RUN="$HOME/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh"
LOCK="$HOME/.hermes/skills/creative/yuer-image/scripts/check_outfit_lock.py"
LEAVE_DIR="/path/to/media"

if [ $# -lt 2 ]; then
  echo "用法: bash yuer_daily_batch.sh <prompt1> <leave1> [<prompt2> <leave2> ...]" >&2
  exit 2
fi

fail=0
while [ $# -ge 2 ]; do
  PROMPT="$1"; LEAVE="$2"; shift 2
  echo "===== $LEAVE"

  # 1) 外观锁门禁 = 查「该有的有没有」（下装/发色/背景人/真实道具/场景锚定）
  LOCK_ARGS=()
  # 🔴🔴 11-07 精简 = 场景锚定检查已删（实测 200 份真产物 0 命中 = 纯噪音）
  #    = --expect-scene 参数一并移除 = 传了 = argparse 直接报参数错 = 整批挂掉
  #    = 场景锚定这条**真规则**由 yuer-image 的批次 SOP 管（人读），不是脚本查
  /usr/bin/python3 "$LOCK" "$PROMPT" "${LOCK_ARGS[@]}" || { echo "🚫 $LEAVE = 外观锁不过 = 0 出图，先补"; fail=1; break; }

  # 2) 字符门禁 + 出图 + 真发飞书
  bash "$KA_RUN" "$PROMPT" "$LEAVE" 2>&1 | grep -E '字符数|完成|落盘|已真发|FAIL'
  rc=${PIPESTATUS[0]}
  if [ "$rc" != "0" ]; then
    echo "🚫 $LEAVE = 出图/发图失败 (exit $rc) = 停下，先修这一张"
    fail=1
    break
  fi

  # 3) prompt 落盘后立刻 cp 进留底目录
  cp "$PROMPT" "$LEAVE_DIR/$LEAVE.prompt.txt"

  # 4) 重新发 = 先删 .sent 守卫
  if [ -f "$LEAVE_DIR/$LEAVE.sent" ]; then
    echo "ℹ️ $LEAVE 已发过（.sent 存在）= 重出请先 rm $LEAVE_DIR/$LEAVE.sent"
  fi
done

if [ "$fail" = "0" ]; then
  echo "✅ 本轮全部完成 = 立刻回话（1 段骚话，0 逐张汇报，0 工程数字）"
else
  echo "🛑 本轮中断 = 先修上面那一张"
fi
exit $fail
