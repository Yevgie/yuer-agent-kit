#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""yuer_verify_image.py · 语儿出图自动验图（双通道）

唯一职责 = 给一张图，判断「我要的东西在不在」。

主通道 = agnes-3.0-flash（云端，语义细，能读姿势/光线/氛围）
兜底   = 本地 Qwen3.8-VL-27B（ComfyUI 工作流，无网、免费、慢但稳）

🔴 云端 vision_analyze 对 NSFW 图必撞 new_sensitive = 0 用它做验图 = 0 重复调。

用法:
  /usr/bin/python3 yuer_verify_image.py <图路径> [--brief "重点看什么"] [--fallback]

  --fallback  = agnes 失败后自动转本地 Qwen3.8
  --only-local= 跳过 agnes 直接走本地
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request

SECRET = "/path/to/media"
AGNES_SCRIPT = "~/.hermes/skills/yuer-agnes-reverse/scripts/yuer_agnes_reverse.py"
QWEN_SCRIPT = "~/.hermes/skills/creative/yuer-reverse-inference/scripts/yuer_qwen_reverse_only.py"
SMALL_DIR = "/tmp/verify_small"
MAX_SIDE = 900          # agnes 对大图 504 = 压到 900px 内
AGNES_TIMEOUT = 200
LOCAL_TIMEOUT = 400


def shrink(src: str) -> str:
    """压图 = agnes 对 >1MB 的 PNG 必 504（实测 1.65MB 挂 126s）。"""
    from PIL import Image
    os.makedirs(SMALL_DIR, exist_ok=True)
    im = Image.open(src).convert("RGB")
    w, h = im.size
    sc = min(1.0, MAX_SIDE / max(w, h))
    if sc < 1.0:
        im = im.resize((int(w * sc), int(h * sc)), Image.LANCZOS)
    out = os.path.join(SMALL_DIR, os.path.splitext(os.path.basename(src))[0] + ".jpg")
    im.save(out, "JPEG", quality=82, optimize=True)
    return out


def load_env():
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        for line in open(env_path, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    for k in ("YUER_AGNES_API_KEY", "AGNES_AGENT_API_KEY", "AGNES_API_KEY"):
        if os.environ.get(k):
            os.environ["YUER_AGNES_API_KEY"] = os.environ[k]
            break


def run_agnes(src: str, brief: str) -> str:
    small = shrink(src)
    cmd = ["/usr/bin/python3", AGNES_SCRIPT, small,
           "--brief", brief or "完整描述图中可见的一切，重点看人物姿势、服装、裸露部位、场景、光线",
           "--model", "agnes-3.0-flash"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=AGNES_TIMEOUT,
                       env=dict(os.environ))
    out = (p.stdout or "") + (p.stderr or "")
    if "反推成功" not in out:
        raise RuntimeError(out.strip()[-400:] or f"agnes exit={p.returncode}")
    return out.split("【反推结果】", 1)[-1].strip()


def run_local(src: str) -> str:
    p = subprocess.run(["/usr/bin/python3", QWEN_SCRIPT, src],
                       capture_output=True, text=True, timeout=LOCAL_TIMEOUT,
                       env=dict(os.environ))
    out = (p.stdout or "") + (p.stderr or "")
    if "=== 反推提示词 ===" not in out:
        raise RuntimeError(out.strip()[-400:] or f"qwen exit={p.returncode}")
    return out.split("=== 反推提示词 ===", 1)[-1].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--brief", default="")
    ap.add_argument("--fallback", action="store_true", help="agnes 失败自动转本地")
    ap.add_argument("--only-local", action="store_true", help="跳过 agnes 直接本地")
    a = ap.parse_args()

    if not os.path.exists(a.image):
        print(f"FAIL 图片不存在: {a.image}", file=sys.stderr)
        return 1

    load_env()
    report = {"image": a.image, "channel": None, "text": "", "error": None}

    if not a.only_local:
        t0 = time.time()
        try:
            report["text"] = run_agnes(a.image, a.brief)
            report["channel"] = "agnes-3.0-flash"
            report["elapsed"] = round(time.time() - t0, 1)
            print(f"=== 验图通道: agnes-3.0-flash ({report['elapsed']}s) ===")
            print(report["text"])
            return 0
        except Exception as e:
            report["error"] = f"agnes失败: {e}"
            print(f"[warn] agnes 验图失败: {e}", file=sys.stderr)
            if not a.fallback:
                return 2

    t0 = time.time()
    try:
        report["text"] = run_local(a.image)
        report["channel"] = "local-qwen3.8"
        report["elapsed"] = round(time.time() - t0, 1)
        print(f"=== 验图通道: local-qwen3.8 ({report['elapsed']}s) ===")
        print(report["text"])
        return 0
    except Exception as e:
        print(f"FAIL 本地兜底也失败: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
