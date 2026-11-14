#!/bin/bash
# 出图三道预检 = 长度/结构 + 主体身份 + 外观锁（11-07 精简 = 只查下装/鞋履/画外描述/单人物）
#
# 用法:
#   bash preflight.sh /tmp/prompt_x.txt            # 三道全跑 = 我自己写的稿
#   bash preflight.sh /tmp/prompt_x.txt --raw      # 全跳 = 0 检测 0 拦截 = 主人贴的稿
#
# 退出码: 0 = 三道全过 | 1 = 有 FAIL | 2 = 用法错
#
# 为什么在 wrapper 之外单独跑: wrapper 自带长度体检, 但不跑主体门禁
# = 主体跑偏时图已经出了才发现 = 白烧一次算力。预检在出图前, 失败时零算力消耗。
#
# 🔴🔴🔴 11-07 10:30 主人当场发火「我发你的提示词，你检测啥」= 主人钦定
#   门禁拦的是「我自己写坏的稿」= 那是保护
#   同一道门作用在「主人的成品」上 = 就是干扰 = 我无权检测无权改写
#   = 主人贴的稿 = --raw = 全跳 = 0 报数 0 提示
#   ⚠️ 旁路必须开在**每个入口** = 只给 wrapper 开 = 我自己先跑 preflight 就已经检测过了
#      = 主人照样挨一遍干扰 = 白开。wrapper + preflight 两处都得认 --raw。

set -u
P="${1:-}"
S=~/.hermes/skills/creative/yuer-image/scripts
RAW=0

for a in "$@"; do
  [ "$a" = "--raw" ] && RAW=1
done

if [ -z "$P" ] || [ ! -f "$P" ]; then
  echo "用法: bash preflight.sh <prompt_file> [--raw]" >&2
  exit 2
fi

if [ "$RAW" = "1" ]; then
  echo "🚦 主人原稿模式 = 0 检测 0 拦截 = 三道预检全跳（11-07 主人钦定）"
  echo "   稿子 = ${P}"
  exit 0
fi

rc=0

echo "── 1/3 长度 + 结构 + 姿势自然度 ──"
python3 "$S/count_prompt_chars.py" "$P" || rc=1

echo
echo "── 2/3 主体身份（是不是语儿）──"
python3 "$S/check_prompt_subject.py" "$P" || rc=1

echo
echo "── 3/3 外观锁（下装/鞋履/画外描述/单人物）──"
python3 "$S/check_outfit_lock.py" "$P" || rc=1

echo
if [ "$rc" = "0" ]; then
  echo "✅ 三道预检全过 = 可以进 wrapper 出图"
else
  echo "❌ 有 FAIL = 先修再出图（不要拿 FAIL 的稿子去烧算力）"
fi
exit "$rc"
