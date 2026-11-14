#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔴🔴🔴 LTX-2.5 图生视频（I2V）API 工作流构建器
主人 10-31 钦定：只保留图生视频 = 文生视频砍掉

架构来源：
  = Lightricks 官方 LTX-2.5_T2V_I2V_Two_Stage_Distilled.json（jsdelivr 通道拿到）
  = 本机旧 ltx-23-i2v.json（API 格式 = 图结构同构 = 改造骨架）
  两阶段采样 = Stage1 8步 euler_ancestral → 空间放大 2× → Stage2 3步 euler_ancestral
"""
import json, os, argparse, copy

# ── 模型文件名（主人传文件后核对服务端实际名）──
# 🔴 服务端实际文件名（10-31 从 object_info 拉的真值 = 不能猜）
MODELS = {
    "unet":      "LTX\\ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors",
    "clip_main": "LTX-2\\gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors",
    "clip_enh":  "LTX-2\\gemma4_e2b_it_bf16.safetensors",          # 可选 = 提示词增强
    "vae_video": "LTX-2\\ltx-2.5-video-vae-conv-bf16.safetensors",
    "vae_audio": "LTX-2\\ltx-2.5-audio-vae-bf16.safetensors",
    "upscaler":  "ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors",
}

# ── 官方 2.5 固定 sigma ──
SIGMAS_S1 = "1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0"
SIGMAS_S2 = "0.909375, 0.725, 0.421875, 0.0"

NEG = ("pc game, console game, video game, cartoon, childish, ugly, "
       "blurry, low quality, still frame, watermark, overlay, titles, "
       "has blurbox, has subtitles, distorted face, extra limbs, deformed hands")


def build(width=704, height=1280, frames=121, fps=24, seed=42,
          img_strength=0.7, s2_strength=1.0, img_compression=18,
          use_prompt_enhancer=False, prefix="ltx-2.5/i2v",
          src_image="example.png", prompt="", tile=512, overlap=64,
          temporal_size=64, temporal_overlap=8, crf=19):
    """构建 LTX-2.5 I2V API 工作流"""
    api = {}

    def N(nid, ct, inputs, title=""):
        api[str(nid)] = {"class_type": ct, "inputs": inputs,
                         "_meta": {"title": title or ct}}

    # ═══ 模型 ═══
    N(5569, "UNETLoader", {"unet_name": MODELS["unet"], "weight_dtype": "default"}, "UNET (LTX-2.5 distilled)")
    N(5571, "VAELoader", {"vae_name": MODELS["vae_video"]}, "VAE (video)")
    N(5570, "VAELoader", {"vae_name": MODELS["vae_audio"]}, "VAE (audio)")
    N(5577, "LatentUpscaleModelLoader", {"model_name": MODELS["upscaler"]}, "Latent Upscaler x2")
    N(5574, "CLIPLoader", {"clip_name": MODELS["clip_main"], "type": "ltxv", "device": "default"}, "CLIP (Gemma4 12B)")
    # 🔴 提示词增强器 = 服务端未装 gemma4_e2b = 默认走原提示词
    #    主人装了之后把 use_prompt_enhancer 打开 + 这里补上 CLIPLoader 即可

    # ═══ 尺寸 / 帧数 / 种子 ═══
    N(5512, "PrimitiveInt", {"value": frames}, "Length (frames)")
    N(5511, "PrimitiveFloat", {"value": fps}, "FPS")
    N(5516, "PrimitiveInt", {"value": seed}, "Seed")
    N(105, "PrimitiveInt", {"value": width}, "Width")
    N(5514, "PrimitiveInt", {"value": height}, "Height")

    # ═══ 提示词 ═══
    N(5509, "PrimitiveStringMultiline", {"value": prompt}, "Positive Prompt")
    N(5508, "PrimitiveStringMultiline", {"value": NEG}, "Negative Prompt")
    N(2483, "CLIPTextEncode", {"text": ["5508", 0], "clip": ["5574", 0]}, "CLIP negative")

    # ═══ 提示词增强（可选）═══
    # TextGenerateLTX2Prompt: 输入 prompt + clip(enhancer) → 输出扩写后的 prompt
    N(5555, "CLIPTextEncode",
      {"text": ["5509", 0], "clip": ["5574", 0]}, "CLIP positive (effective)")

    # ═══ 图像预处理 ═══
    N(2004, "LoadImage", {"image": src_image}, "Source Image")
    # 🔴 用核心节点 ImageScale（ResizeImageMaskNode 是 dynamic combo = API 格式字段结构特殊 = 踩坑）
    N(4990, "ImageScale",
      {"image": ["2004", 0], "upscale_method": "lanczos",
       "width": width, "height": height, "crop": "center"}, "Resize Image")
    N(3336, "LTXVPreprocess", {"img_compression": img_compression, "image": ["4990", 0]}, "LTXV Preprocess")

    # ═══ 空潜空间 ═══
    N(3059, "EmptyLTXVLatentVideo",
      {"width": ["105", 0], "height": ["5514", 0], "length": ["5512", 0], "batch_size": 1},
      "Empty LTXV Latent Video")
    N(3980, "LTXVEmptyLatentAudio",
      {"frames_number": ["5512", 0], "frame_rate": ["5511", 0], "batch_size": 1,
       "audio_vae": ["5570", 0]}, "Empty LTXV Audio")

    # ═══ 条件 ═══
    N(1241, "LTXVConditioning",
      {"frame_rate": ["5511", 0], "positive": ["5555", 0], "negative": ["2483", 0]},
      "LTXV Conditioning")

    # ═══ Stage 1：8 步 ═══
    N(4828, "CFGGuider",
      {"cfg": 1.0, "model": ["5569", 0], "positive": ["1241", 0], "negative": ["2483", 0]},
      "CFG Guider S1")
    N(4831, "KSamplerSelect", {"sampler_name": "euler_ancestral"}, "Sampler S1")
    N(4984, "ManualSigmas", {"sigmas": SIGMAS_S1}, "Sigmas S1 (8 steps)")
    N(4832, "RandomNoise", {"noise_seed": ["5516", 0]}, "Noise S1")
    N(3159, "LTXVImgToVideoInplace",
      {"strength": img_strength, "bypass": False, "vae": ["5571", 0],
       "image": ["3336", 0], "latent": ["3059", 0]}, "ImgToVideo S1")
    N(4528, "LTXVConcatAVLatent",
      {"video_latent": ["3159", 0], "audio_latent": ["3980", 0]}, "Concat AV (S1)")
    N(4829, "SamplerCustomAdvanced",
      {"noise": ["4832", 0], "guider": ["4828", 0], "sampler": ["4831", 0],
       "sigmas": ["4984", 0], "latent_image": ["4528", 0]}, "Sampler S1")
    N(4845, "LTXVSeparateAVLatent", {"av_latent": ["4829", 0]}, "Separate AV (S1)")

    # ═══ 空间放大 2× ═══
    N(4975, "LTXVLatentUpsampler",
      {"samples": ["4845", 0], "upscale_model": ["5577", 0], "vae": ["5571", 0]},
      "Latent Upsampler x2")

    # ═══ Stage 2：3 步 ═══
    N(4970, "LTXVImgToVideoInplace",
      {"strength": s2_strength, "bypass": False, "vae": ["5571", 0],
       "image": ["3336", 0], "latent": ["4975", 0]}, "ImgToVideo S2")
    N(4969, "LTXVConcatAVLatent",
      {"video_latent": ["4970", 0], "audio_latent": ["4845", 1]}, "Concat AV (S2)")
    N(4964, "CFGGuider",
      {"cfg": 1.0, "model": ["5569", 0], "positive": ["1241", 0], "negative": ["2483", 0]},
      "CFG Guider S2")
    N(4976, "KSamplerSelect", {"sampler_name": "euler_ancestral"}, "Sampler S2")
    N(4985, "ManualSigmas", {"sigmas": SIGMAS_S2}, "Sigmas S2 (3 steps)")
    N(4967, "RandomNoise", {"noise_seed": ["5516", 0]}, "Noise S2")
    N(4971, "SamplerCustomAdvanced",
      {"noise": ["4967", 0], "guider": ["4964", 0], "sampler": ["4976", 0],
       "sigmas": ["4985", 0], "latent_image": ["4969", 0]}, "Sampler S2")
    N(4973, "LTXVSeparateAVLatent", {"av_latent": ["4971", 0]}, "Separate AV (S2)")

    # ═══ 解码 ═══
    N(5538, "VAEDecodeTiled",
      {"samples": ["4973", 0], "vae": ["5571", 0], "tile_size": tile,
       "overlap": overlap, "temporal_size": temporal_size,
       "temporal_overlap": temporal_overlap}, "VAE Decode Tiled")
    N(4848, "LTXVAudioVAEDecode",
      {"samples": ["4973", 1], "audio_vae": ["5570", 0]}, "Audio VAE Decode")

    # ═══ 输出 ═══
    N(4849, "CreateVideo",
      {"images": ["5538", 0], "audio": ["4848", 0], "fps": ["5511", 0], "bit_depth": 8},
      "Create Video")
    N(4852, "SaveVideo",
      {"video": ["4849", 0], "filename_prefix": prefix, "format": "auto", "codec": "auto"},
      "Save Video")

    return api


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--width", type=int, default=704)
    ap.add_argument("--height", type=int, default=1280)
    ap.add_argument("--frames", type=int, default=121)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--enhancer", action="store_true")
    ap.add_argument("--prefix", default="ltx-2.5/i2v")
    ap.add_argument("--src", default="example.png")
    ap.add_argument("--prompt", default="")
    a = ap.parse_args()

    wf = build(width=a.width, height=a.height, frames=a.frames, fps=a.fps,
               seed=a.seed, use_prompt_enhancer=a.enhancer, prefix=a.prefix,
               src_image=a.src, prompt=a.prompt)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(wf, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✅ LTX-2.5 I2V 工作流 = {len(wf)} 节点 -> {a.out}")
