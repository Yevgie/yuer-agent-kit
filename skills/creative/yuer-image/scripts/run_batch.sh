#!/usr/bin/env bash
# 无限勾引批次跑法 = 一条命令收一整批。
#
# 用法：bash scripts/run_batch.sh <batch_tag> [leave_prefix]
#   例：bash scripts/run_batch.sh v2 2026-11-01
#
# 🔴 三条硬规则（都是实战踩出来的）：
# 1. 文件名必须与 build 脚本产出一致 = 本脚本用 glob 收 /tmp/prompt_<tag>_n*.txt
#    = 0 手工列文件名（手写列表 = 生成名与跑名对不上 = 全批 FileNotFound = 白跑一轮）。
# 2. 跑前必须校验文件数 == 5 = build 脚本改过 job key（如 n5x→n4）会留孤儿文件
#    = glob 一起跑 = 多出一张重复图真发到主人手机。
# 3. 先全部过门禁再开跑 = 中途 FAIL = 已花掉的出图开销作废。
#
# 🔴 批内串行 = 0 并行（GPU 抢显存 = 采样变慢/爆显存）；一批 = 一个后台进程 = 用
#    process(action='wait') 收口 = 0 跑到前台超时被系统抬成后台。
set -u
TAG="${1:?用法: run_batch.sh <batch_tag> [leave_prefix]}"
PREFIX="${2:-$(date +%Y-%m-%d)}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="${SKILL_DIR}/scripts"

FILES=$(ls -1 /tmp/prompt_"${TAG}"_n*.txt 2>/dev/null | sort)
COUNT=$(printf '%s\n' "$FILES" | grep -c . )
if [ "$COUNT" -ne 5 ]; then
  echo "❌ 文件数 = $COUNT ≠ 5 = 孤儿文件或漏张 = 0 开跑"
  printf '%s\n' "$FILES"
  exit 1
fi
echo "== 批次 ${TAG} · 文件 ${COUNT} 份 =="

for f in $FILES; do
  name=$(basename "$f" | sed "s/^prompt_${TAG}_//; s/\.txt$//")
  echo "----- GATE ${TAG} ${name} -----"
  /usr/bin/python3 "${SCRIPTS}/check_prompt_subject.py" "$f" || { echo "❌ 主体门禁挂 = ${name}"; exit 1; }
  /usr/bin/python3 "${SCRIPTS}/check_outfit_lock.py" "$f" || { echo "❌ 外观锁门禁挂 = ${name}"; exit 1; }
done

for f in $FILES; do
  name=$(basename "$f" | sed "s/^prompt_${TAG}_//; s/\.txt$//")
  echo "===== RUN ${PREFIX}_${TAG}_${name} ====="
  bash "${SCRIPTS}/yuer_ka_fast.sh" "$f" "${PREFIX}_${TAG}_${name}" || echo "❌ ${name} 失败"
done
echo "===== BATCH ${TAG} DONE ====="
