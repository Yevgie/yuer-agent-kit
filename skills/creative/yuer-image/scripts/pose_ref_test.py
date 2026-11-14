#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pose_ref_test.py · 姿势参考图驱动的出图脚本（用法 B）。

姿势线稿当 image2img 参考源 = 让底模「看到」人怎么摆，而不是靠英文去说服它。

用法:
    /usr/bin/python3 scripts/pose_ref_test.py "<英文 prompt>" <姿势线稿png> <out_name>

原理:
    复制 wash 工作流 → LoadImage 换成姿势线稿 → denoise 调高洗掉线稿质感 → 出图落盘。
    实测姿势结构保得住，胯部朝向这类细节只「像」不「锁死」。
    前提 = 本机 ComfyUI 只有 Anima-LLLite 一个 ControlNet，没有标准 openpose/dwpose 模型，
    所以走「线稿当参考源 + 高 denoise」而不是姿势硬控。

坑:
    · 必须用 terminal() 调 /usr/bin/python3 跑，不要用 execute_code（sandbox kernel 没有 comfyui 包）。
    · denoise 低于 0.85 会把线稿质感一起洗成照片以外的塑料感；高于 0.9 姿势结构开始飘。
    · 出图前先跑 check_prompt_subject.py / check_outfit_lock.py，跟默认链路一样。
"""
import json
import os
import random
import shutil
import sys
import time
import uuid

import requests

SERVER = os.environ.get("YUER_COMFYUI_SERVER", "http://192.168.x.x:8188")
WORKFLOW = "/path/to/workflows/yuer_moody_fast_wash.json"
OUT_DIR = "/tmp/pose_ref_out"


def upload_image(path):
    with open(path, "rb") as f:
        files = {"image": (os.path.basename(path), f.read())}
        r = requests.post(f"{SERVER}/upload/image", files=files, timeout=120)
        r.raise_for_status()
    data = r.json()
    return {"name": data["name"], "subfolder": data.get("subfolder", ""), "type": data.get("type", "input")}


def build(prompt, ref_png, seed=None, denoise=None):
    wf = json.load(open(WORKFLOW, encoding="utf-8"))
    up = upload_image(ref_png)
    # LoadImage 节点 = 找到它的 class_type
    load_ids = [k for k, v in wf.items() if v.get("class_type") == "LoadImage"]
    if not load_ids:
        raise SystemExit("工作流里没有 LoadImage 节点")
    lid = load_ids[0]
    wf[lid]["inputs"]["image"] = up["name"]
    # 提示词节点 = 取第一个 text 编码节点
    text_ids = [k for k, v in wf.items() if v.get("class_type", "").startswith("TextEncode")]
    if text_ids:
        wf[text_ids[0]]["inputs"][list(wf[text_ids[0]]["inputs"].keys())[0]] = prompt
    # 随机种子
    seed_ids = [k for k, v in wf.items() if v.get("class_type") in ("KSampler", "KSamplerAdvanced")]
    if seed_ids:
        wf[seed_ids[0]]["inputs"]["seed"] = seed if seed is not None else random.randint(0, 2**31 - 1)
    # denoise = 洗掉线稿质感的旋钮
    if denoise is not None:
        den_ids = [k for k, v in wf.items() if "denoise" in v.get("inputs", {})]
        if den_ids:
            wf[den_ids[0]]["inputs"]["denoise"] = denoise
    client_id = str(uuid.uuid4())
    for k, v in wf.items():
        v["_meta"]["title"] = v.get("_meta", {}).get("title", "")
    return wf, client_id


def run(wf, client_id):
    r = requests.post(f"{SERVER}/prompt", json={"prompt": wf, "client_id": client_id}, timeout=300)
    r.raise_for_status()
    pid = r.json()["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < 600:
        time.sleep(2)
        d = requests.get(f"{SERVER}/history/{pid}", timeout=30).json()
        if pid in d:
            outs = []
            for nid, node in d[pid].get("outputs", {}).items():
                for im in node.get("images", []):
                    outs.append(im)
            if outs:
                return outs
    raise SystemExit("超时")


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    prompt, ref_png, name = sys.argv[1], sys.argv[2], sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else None
    denoise = float(sys.argv[5]) if len(sys.argv) > 5 else 0.88
    os.makedirs(OUT_DIR, exist_ok=True)
    wf, cid = build(prompt, ref_png, seed, denoise)
    outs = run(wf, cid)
    saved = []
    for i, im in enumerate(outs):
        q = requests.get(
            f"{SERVER}/view",
            params={"filename": im["filename"], "subfolder": im.get("subfolder", ""), "type": im.get("type", "output")},
            timeout=120,
        )
        out = os.path.join(OUT_DIR, f"{name}.png" if len(outs) == 1 else f"{name}_{i}.png")
        with open(out, "wb") as f:
            f.write(q.content)
        saved.append((out, len(q.content)))
    for p, n in saved:
        print(f"OUT: {p} {n} bytes")


if __name__ == "__main__":
    main()
