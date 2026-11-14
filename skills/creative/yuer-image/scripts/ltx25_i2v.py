#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔴🔴🔴 LTX-2.5 图生视频（I2V）命令行入口
主人 10-31 钦定 = 只做图生视频 = 文生视频砍掉 = 时长 0-15s

用法：
  python3 ltx25_i2v.py --image <服务端input里的图名> --prompt "<中文/英文提示词>" \
        --duration 8 --fps 24 --seed 42 --out <落盘路径>

说明：
  - 工作流本体 = 主人自己做的 LTX-2.5-I2V_Distilled+Distilled.json
  - 时长参数走 ComfyMathExpression '1 + floor(a*b/8)*8' = fps×秒 自动算帧数（1+8k）
  - 源图必须在服务端 ComfyUI/input/ 下（LoadImage 只认服务端文件名）
"""
import json, os, sys, time, argparse, urllib.request, urllib.parse, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REG = "~/.local/lib/python3.11/site-packages/comfyui/assets/workflows"
WF_ID = "ltx25_i2v"
sys.path.insert(0, HERE)
from yuer_image_constants import DEFAULT_COMFYUI_SERVER as SERVER

NEG = ("blurry, low quality, still frame, frames, watermark, overlay, titles, "
       "has blurbox, has subtitles")


def load_wf():
    with open(f"{REG}/{WF_ID}.json", encoding="utf-8") as f:
        return json.load(f)


def patch(wf, image=None, prompt=None, duration=None, fps=None, seed=None,
          width=None, height=None, prefix=None):
    """参数注入（节点 ID = 主人原工作流里的固定 ID）"""
    if image is not None:
        wf["180"]["inputs"]["image"] = image          # LoadImage
    if prompt is not None:
        wf["121"]["inputs"]["text"] = prompt          # CLIPTextEncode (positive)
    if duration is not None:
        wf["112"]["inputs"]["value"] = int(duration)  # PrimitiveInt = 秒
    if fps is not None:
        wf["220"]["inputs"]["value"] = float(fps)      # PrimitiveFloat = fps
    if seed is not None:
        wf["114"]["inputs"]["noise_seed"] = int(seed)  # Stage2 噪声
        wf["115"]["inputs"]["noise_seed"] = int(seed + 1)  # Stage1 噪声
    if width is not None:
        wf["189"]["inputs"]["width"] = int(width)      # ImageResizeKJv2
    if height is not None:
        wf["189"]["inputs"]["height"] = int(height)
    if prefix is not None:
        wf["209"]["inputs"]["filename_prefix"] = prefix
    return wf


def frames_of(wf):
    """复算帧数 = 1 + floor(fps*sec/8)*8"""
    sec = wf["112"]["inputs"]["value"]
    fps = wf["220"]["inputs"]["value"]
    return 1 + int(fps * sec / 8) * 8


def submit(wf):
    body = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(SERVER + "/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))["prompt_id"]


def wait(pid, timeout=3600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(f"{SERVER}/history/{pid}", timeout=40) as r:
                d = json.loads(r.read().decode("utf-8"))
            h = d.get(pid)
            if h:
                st = h.get("status", {})
                if st.get("completed"):
                    return h
        except Exception:
            pass
        time.sleep(6)
    raise TimeoutError(f"超时 {timeout}s")


def upload(local_path):
    """🔴 把本地图传到服务端 ComfyUI/input/ = LoadImage 只认服务端文件名
    上传端点 = POST /upload/image (multipart)"""
    import requests
    name = os.path.basename(local_path)
    with open(local_path, "rb") as f:
        files = {"image": (name, f, "image/png")}
        data = {"type": "input", "overwrite": "true"}
        r = requests.post(SERVER + "/upload/image", files=files, data=data, timeout=180)
    r.raise_for_status()
    j = r.json()
    return j.get("name") or name


def find_video(h):
    for oid, o in (h.get("outputs") or {}).items():
        for key in ("videos", "gifs", "images"):
            for it in o.get(key) or []:
                if it.get("filename", "").endswith((".mp4", ".webm", ".mkv")):
                    return it
    return None


def download(item, dest):
    url = (f"{SERVER}/view?filename={urllib.parse.quote(item['filename'])}"
           f"&subfolder={urllib.parse.quote(item.get('subfolder',''))}&type=output")
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    urllib.request.urlretrieve(url, dest)
    return dest


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", help="服务端 input 目录里的文件名，或本地图绝对路径（自动上传）")
    ap.add_argument("--prompt", help="正向提示词（写动作/运镜/台词）")
    ap.add_argument("--duration", type=int, help="时长秒数 0-15")
    ap.add_argument("--fps", type=float, help="帧率，默认 24")
    ap.add_argument("--seed", type=int, help="种子")
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("--prefix", help="落盘前缀，默认 ltx-2.5/i2v")
    ap.add_argument("--out", help="下载到本地的路径")
    ap.add_argument("--no-run", action="store_true", help="只打印不提交")
    a = ap.parse_args()

    # 🔴 本地路径 = 自动上传到服务端 input/ = 再传给 LoadImage
    image = a.image
    if image and os.path.isfile(image):
        print(f"📤 上传源图 = {image}")
        image = upload(image)
        print(f"   → 服务端 input/{image}")

    wf = patch(load_wf(), image=image, prompt=a.prompt, duration=a.duration,
               fps=a.fps, seed=a.seed, width=a.width, height=a.height,
               prefix=a.prefix)
    n = frames_of(wf)
    print(f"⏱️ 时长 = {wf['112']['inputs']['value']}s × {wf['220']['inputs']['value']}fps "
          f"→ {n} 帧 (1+8k ✓)")
    print(f"🖼️ 源图 = {wf['180']['inputs']['image']}")
    print(f"📝 提示词 = {wf['121']['inputs']['text'][:120]}")

    if a.no_run:
        json.dump(wf, open("/tmp/ltx25_i2v_final.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print("💾 已存 /tmp/ltx25_i2v_final.json（未提交）")
        sys.exit(0)

    t0 = time.time()
    pid = submit(wf)
    print(f"✅ 提交成功 prompt_id={pid}", flush=True)
    h = wait(pid)
    item = find_video(h)
    if not item:
        print("❌ 没找到视频输出")
        print(json.dumps(h.get("status", {}), ensure_ascii=False)[:800])
        sys.exit(2)
    meta = item.get("metadata", {})
    print(f"🎬 成片 = {meta.get('width')}x{meta.get('height')} · {meta.get('frame_count')} 帧 · "
          f"{meta.get('duration', 0):.2f}s · {meta.get('fps')}fps")
    print(f"⏱️ 生成耗时 = {time.time()-t0:.1f}s")
    if a.out:
        p = download(item, a.out)
        print(f"📥 落盘 {p} = {os.path.getsize(p)} 字节")
