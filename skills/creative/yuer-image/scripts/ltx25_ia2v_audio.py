#!/usr/bin/env python3
"""
LTX-2.5 IA2V（图 + 音频参考 → 视频）
主人 10-31 提供的 /path/to/workflows/LTX-2.5-IA2V_Distilled+Distilled+.json
= 带 VHS_LoadAudioUpload(200) + SetLatentNoiseMask "Freeze audio (no noise)"(202)
= 音轨被冻住不重生成 = 视频动作跟参考音频对齐 = 语音用自己的音色。

用法：
  python3 ltx25_ia2v_audio.py --image <png> --audio <mp3/opus/wav> \
      --prompt "<动作/运镜>" --duration 6 --fps 24 --seed 42 --out <mp4> [--no-run]
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from yuer_image_constants import DEFAULT_COMFYUI_SERVER as SERVER
except Exception:
    print("ERR: 读不到 yuer_image_constants.DEFAULT_COMFYUI_SERVER = 中止", file=sys.stderr)
    sys.exit(2)

DEFAULT_WF = "/path/to/workflows/LTX-2.5-IA2V_Distilled+Distilled+.json"


def upload(local_path, kind="image"):
    """上传到服务端。kind=image → /upload/image；kind=audio → /upload/image 也行
    (VHS_LoadAudioUpload 走的是 ComfyUI input 目录里的音频文件)。"""
    name = os.path.basename(local_path)
    boundary = "----FormBoundary" + uuid.uuid4().hex
    with open(local_path, "rb") as f:
        data = f.read()
    ctype = "video/mp4" if local_path.endswith(".mp4") else "application/octet-stream"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{name}"\r\n'
        f"Content-Type: {ctype}\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        SERVER + "/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        info = json.loads(r.read())
    return info["name"], info


def patch_workflow(wf, image_name, audio_name, prompt, duration, fps, seed):
    # 图片
    wf["240"]["inputs"]["image"] = image_name
    # 音频参考
    wf["200"]["inputs"]["audio"] = audio_name
    wf["200"]["inputs"]["start_time"] = 0
    if duration:
        wf["200"]["inputs"]["duration"] = duration
    # 帧数 = 1 + floor(fps*duration/8)*8 → 节点197 用 values.b = 200 的 duration
    wf["212"]["inputs"]["value"] = fps
    # 正向提示词（121）
    wf["121"]["inputs"]["text"] = prompt
    # 种子
    wf["114"]["inputs"]["noise_seed"] = seed
    wf["115"]["inputs"]["noise_seed"] = seed + 1
    # 输出前缀
    wf["244"]["inputs"]["filename_prefix"] = "ltx-2.5/ia2v"
    return wf


def submit(wf):
    body = json.dumps({"prompt": wf}).encode()
    req = urllib.request.Request(
        SERVER + "/prompt",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def wait(pid, timeout=3600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(f"{SERVER}/history/{pid}", timeout=40) as r:
                h = json.loads(r.read())
            if pid in h:
                return h[pid]
        except Exception:
            pass
        time.sleep(4)
    raise TimeoutError("wait timeout")


def find_video(h):
    for out in h.get("outputs", {}).values():
        for g in out.get("gifs", []) + out.get("videos", []) + out.get("images", []):
            if g.get("type") == "output" and str(g.get("filename", "")).endswith((".mp4", ".webm", ".mkv")):
                return g
    return None


def download(item, dest):
    url = (
        f"{SERVER}/view?filename={urllib.parse.quote(item['filename'])}"
        f"&subfolder={urllib.parse.quote(item.get('subfolder', ''))}&type=output"
    )
    urllib.request.urlretrieve(url, dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--duration", type=float, default=None)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--wf", default=DEFAULT_WF)
    ap.add_argument("--no-run", action="store_true")
    args = ap.parse_args()

    print(f"🖼️ 上传源图 = {args.image}")
    img_name, _ = upload(args.image, "image")
    print(f"   → 服务端 input/{img_name}")
    print(f"🎙️ 上传参考音频 = {args.audio}")
    aud_name, _ = upload(args.audio, "audio")
    print(f"   → 服务端 input/{aud_name}")

    wf = json.load(open(args.wf, encoding="utf-8"))
    wf = patch_workflow(wf, img_name, aud_name, args.prompt, args.duration, args.fps, args.seed)
    frames = 1 + int((args.fps * (args.duration or 5)) // 8) * 8
    print(f"⏱️ 时长 = {args.duration}s × {args.fps}fps → {frames} 帧 (1+8k ✓)")
    print(f"📝 提示词 = {args.prompt[:120]}")

    out_json = "/tmp/ltx25_ia2v_final.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)

    if args.no_run:
        print(f"💾 已存 {out_json}（未提交）")
        return

    res = submit(wf)
    pid = res["prompt_id"]
    print(f"✅ 提交成功 prompt_id={pid}")
    h = wait(pid)
    item = find_video(h)
    if not item:
        print("ERR: 没找到视频输出", file=sys.stderr)
        sys.exit(3)
    download(item, args.out)
    size = os.path.getsize(args.out)
    print(f"📥 落盘 {args.out} = {size} 字节")


if __name__ == "__main__":
    main()
