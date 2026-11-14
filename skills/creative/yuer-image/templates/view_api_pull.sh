#!/usr/bin/env bash
# view API 直拉图 - 绕过 comfyui --poll 8-15s 延迟
# 用法: ./view_api_pull.sh <job_id> <output_path>
JOB_ID=$1
OUT=$2

RESULT=$(curl -s -m 10 "http://192.168.x.x:8188/history/${JOB_ID}")
FILENAME=$(echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
job_id = '$JOB_ID'
if job_id in data and 'outputs' in data[job_id]:
    outs = data[job_id]['outputs']
    for nid, out in outs.items():
        if 'images' in out:
            for img in out['images']:
                print(img['filename'])
                sys.exit(0)
")

if [ -z "$FILENAME" ]; then
    echo "❌ 还没好, 等 3 秒"
    sleep 3
    RESULT=$(curl -s -m 10 "http://192.168.x.x:8188/history/${JOB_ID}")
    FILENAME=$(echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
job_id = '$JOB_ID'
if job_id in data and 'outputs' in data[job_id]:
    outs = data[job_id]['outputs']
    for nid, out in outs.items():
        if 'images' in out:
            for img in out['images']:
                print(img['filename'])
                sys.exit(0)
")
fi

curl -s -m 10 "http://192.168.x.x:8188/view?filename=${FILENAME}&type=output" -o "$OUT"
echo "✅ 已拉到: $OUT ($(stat -c%s $OUT) bytes)"
echo "$FILENAME"