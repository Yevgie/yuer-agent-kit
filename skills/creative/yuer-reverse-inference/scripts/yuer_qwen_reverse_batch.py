#!/usr/bin/env python3
"""
yuer_qwen_reverse_batch.py · 本地 qwen 3.8 批量反推（v1.0 · 09-29 实战 264/265/266 钦定）

唯一职责：批量跑三档反推工作流（--tier default/fast），一次加载模型跑 N 张反推。

🔴 灵魂级铁律（主人原话，09-29 钦定）：
    「批量反推跑完之后、输出完之后把自动卸载模型给关掉」
    「如果你反推完之后没有卸载模型，直接去跑图，跑图会变得异常慢」

  = 批量模式全程 `生成后自动卸载模型 = False` = 模型常驻显存 = 每张只付推理时间
  = 单张首跑 ~21s（含 27B 加载），常驻后每张 ~7-8s
  = **批量跑完必须显式卸载**（`/free` 释放模型），否则后续出图链路抢显存 = 异常慢

🔴 与单张的关系：
  - 单张反推（主人主动要单独反推）= `yuer_qwen_reverse_only.run()` = 保持 True（跑完就卸，不占显存）
  - 批量反推（连续多张入库/洗图前预热）= 本脚本 = 保持 False（跑完统一卸）
  = 两脚本互不干扰，各按场景定卸载策略

用法：
    # 1. 批量反推目录里所有图 → JSONL 结果
    python3 yuer_qwen_reverse_batch.py <图片目录|图片文件...> [-o 输出.jsonl] [--keep-model]

    # 2. 只反推不卸载（主人自己后面还要跑图时慎用，必须先手动跑 /free）
    python3 yuer_qwen_reverse_batch.py <路径> --keep-model
"""
import argparse
import glob
import json
import os
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yuer_qwen_reverse_only import (  # noqa: E402
    DEFAULT_COMFYUI_SERVER,
    DEFAULT_WORKFLOW_PATH,
    WORKFLOW_TIERS,
    _extract_text,
    upload_image,
)

FREE_MODELS = "/free"
POLL_INTERVAL = 3
POLL_MAX = 200  # 单张最长 600s（27B 首跑加载）


def free_models(server: str, unload: bool = True) -> None:
    """通知 ComfyUI 释放模型显存。

    ❗ 批量反推跑完不调这个 = 模型常驻 = 后续出图异常慢（主人亲历过的坑）。
    """
    if not unload:
        return
    try:
        r = requests.post(f"{server}/free", json={"unload_models": True,
                                                  "free_memory": True}, timeout=30)
        print(f"[batch] 🧹 已卸载模型释放显存 (HTTP {r.status_code})", flush=True)
    except requests.RequestException as e:
        print(f"[batch] ⚠️ 卸载失败（不影响已得结果）: {str(e)[:120]}", flush=True)


def collect_images(paths):
    """目录 → 递归收集图片；文件 → 直接用。"""
    exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in sorted(files):
                    if os.path.splitext(f)[1].lower() in exts:
                        out.append(os.path.join(root, f))
        elif any(p.lower().endswith(e) for e in (".jpg", ".jpeg", ".png", ".webp", ".bmp")):
            out.append(p)
        else:
            hits = sorted(glob.glob(p))
            out.extend(h for h in hits if os.path.splitext(h)[1].lower() in exts)
    return out


def reverse_one(image_path: str, server: str, keep_model: bool, tier: str = "local") -> str:
    """反推单张。keep_model=True 时不改自动卸载（走批量常驻）。"""
    uploaded = upload_image(image_path, server)
    wf_path = WORKFLOW_TIERS.get(tier)
    if not wf_path:
        raise RuntimeError(f"🔴 未知反推档位 {tier!r}，可选: {list(WORKFLOW_TIERS)}")
    with open(wf_path, encoding="utf-8") as f:
        wf = json.load(f)

    for nid, node in wf.items():
        if node.get("class_type") == "LoadImage":
            node["inputs"]["image"] = uploaded
            break
    else:
        raise RuntimeError("🔴 工作流里没找到 LoadImage 节点")

    # 批量模式 = 关掉自动卸载 = 模型常驻 = 每张只付推理时间
    for nid, node in wf.items():
        if node.get("class_type") == "QwenTE_ImageInfer":
            node["inputs"]["生成后自动卸载模型"] = bool(keep_model)

    r = requests.post(f"{server}/prompt", json={"prompt": wf}, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"提交失败 HTTP {r.status_code}: {r.text[:400]}")
    prompt_id = r.json()["prompt_id"]

    for i in range(POLL_MAX):
        time.sleep(POLL_INTERVAL)
        try:
            r = requests.get(f"{server}/history/{prompt_id}", timeout=15)
        except requests.RequestException:
            continue
        if r.status_code != 200:
            continue
        data = r.json()
        if prompt_id not in data:
            continue
        outputs = data[prompt_id].get("outputs", {})
        if outputs:
            text = _extract_text(outputs)
            if text.strip():
                return text
        if data[prompt_id].get("status", {}).get("completed", False):
            raise RuntimeError(f"执行完成但无输出: {json.dumps(data[prompt_id].get('status'), ensure_ascii=False)[:300]}")
    raise RuntimeError(f"反推超时 ({POLL_MAX * POLL_INTERVAL}s)")


def main():
    ap = argparse.ArgumentParser(description="本地 qwen 3.8 批量反推（模型常驻 + 跑完统一卸载）")
    ap.add_argument("paths", nargs="+", help="图片目录 / 图片文件 / glob")
    ap.add_argument("-o", "--out", default="/tmp/qwen38_batch_results.jsonl", help="输出 JSONL")
    ap.add_argument("--server", default=DEFAULT_COMFYUI_SERVER)
    ap.add_argument("--tier", default="local", choices=list(WORKFLOW_TIERS),
                    help="反推档位：local=本地9B破限Q8中文长版(30s) / fast=本地4B官方Q6短版(15s)。默认走 AGNES 云端请用 yuer_qwen_reverse_only.reverse()")
    ap.add_argument("--keep-model", action="store_true",
                    help="跑完不卸载模型（默认跑完就卸，避免拖慢后续出图）")
    args = ap.parse_args()

    images = collect_images(args.paths)
    if not images:
        print("❌ 没找到图片", file=sys.stderr)
        sys.exit(1)
    print(f"[batch] 📚 待反推 {len(images)} 张 · 模型常驻模式 · 跑完"
          f"{'不卸载 ⚠️' if args.keep_model else '自动卸载'}", flush=True)

    ok = fail = 0
    try:
        with open(args.out, "w", encoding="utf-8") as fh:
            for idx, img in enumerate(images, 1):
                t0 = time.time()
                try:
                    text = reverse_one(img, args.server, keep_model=True, tier=args.tier)
                    fh.write(json.dumps({"image": img, "ok": True, "text": text},
                                        ensure_ascii=False) + "\n")
                    fh.flush()
                    ok += 1
                    print(f"[batch] {idx}/{len(images)} ✅ {os.path.basename(img)[:50]} "
                          f"{len(text)}字 {time.time() - t0:.0f}s", flush=True)
                except Exception as e:
                    fh.write(json.dumps({"image": img, "ok": False,
                                         "error": str(e)[:300]}, ensure_ascii=False) + "\n")
                    fh.flush()
                    fail += 1
                    print(f"[batch] {idx}/{len(images)} ❌ {os.path.basename(img)[:50]} "
                          f"{str(e)[:100]}", flush=True)
    finally:
        # 🔴 灵魂级：无论成败都要卸载，否则后续出图异常慢
        free_models(args.server, unload=not args.keep_model)

    print(f"\n[batch] === 完成：成功 {ok} / 失败 {fail} · 结果 {args.out} ===", flush=True)
    sys.exit(0 if fail == 0 else 2)


if __name__ == "__main__":
    main()
