#!/usr/bin/env python3
"""
yuer_qwen_reverse_only.py · 单纯 qwen 反推提示词（v2.0 · 09-29 升级 qwen 3.8）

唯一职责：主人发图 → 单纯反推提示词（不出图）= 走三档工作流（default=9B/detail/fast=4B），27B 已于 11-04 删除
= 上传图 → QwenTE_ModelLoader 加载 Qwen3.8-VL → QwenTE_ImageInfer 出 8 段反推文本 → easy showAnything 展示

🔴 v2.0 变更（09-29 升级 · 盖过 v1.0 一切）：
  旧：/path/to/workflows/qwen3_vision_single.json（Qwen3.5-9B，09-29 主人升级 3.8 时**已连脚本一并删除**）
      输出取 PreviewAny 节点 16
  新：/path/to/workflows/api_qwen3.5_9b_反推_默认.json（9B 破限 Q8_0）+ api_qwen3.5_4b_反推_快速筛.json（4B 官方 Q6）
      节点 QwenTE_ModelLoader（Qwen3.8-VL-27B）+ QwenTE_ImageInfer
      输出取 easy showAnything 节点 20
  原因：主人钦定换 qwen 3.8 工作流 = 旧 qwen 3.5 工作流删除

🔴 输出格式铁律（09-29 钦定 · 与 agnes 链路统一）：
  工作流内的「提示词」框已写死 8 段编号格式（英文）。
  本地 qwen 走这条路时**同样 8 段**，语儿解析器 `yuer_parse_suite.py` 对两条链路通用。
  ⚠️ 8 段是英文 = 解析器 SRC_KEYS_EN 的中英别名组已覆盖（Scene/Camera Angle/Pose/Wardrobe/
     Lighting/Mood/Character Look/Seductive Pose Note）= 两条链路输出格式统一 = 解析器只维护一份。

调用方唯一入口：run(image_path) → 返回反推文本
"""
import json
import os
import sys
import time

import requests

DEFAULT_COMFYUI_SERVER = "http://192.168.x.x:8188"

# 🔴 三档工作流（11-04 实测选型 · 见 SKILL.md §选型）
#   档位名 → 工作流文件。默认档 = 9B 破限 Q8_0 + 中文长提示词（30s / 8段 / 追平 AGNES）
WORKFLOW_TIERS = {
    "local": "/path/to/workflows/api_qwen3.5_9b_反推_默认.json",
    "fast":  "/path/to/workflows/api_qwen3.5_4b_反推_快速筛.json",
}
DEFAULT_WORKFLOW_PATH = WORKFLOW_TIERS["local"]

# 🔴 反推档位（11-04 主人钦定 · 27B 已删除）
#   agnes = 默认主链路（云端 · 9~21s · NSFW 零删减 · 中文输出）
#   local = 兜底（本地 9B 破限 Q8_0 · 30~36s · 中文）
#   fast  = 兜底（本地 4B 官方 Q6 · 12~15s · 中文 · 粗筛）
#   detail/27B = 已于 11-04 删除，不再支持
REVERSE_TIERS = ("agnes", "local", "fast")
DEFAULT_TIER = "agnes"
AGNES_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "yuer-agnes-reverse", "scripts", "yuer_agnes_reverse.py",
)
OUTPUT_NODE_ID = "20"  # easy showAnything
POLL_INTERVAL = 3
POLL_MAX = 200  # 27B 模型加载慢 = 最多等 10 分钟


def upload_image(image_path: str, server: str) -> str:
    with open(image_path, "rb") as f:
        r = requests.post(
            f"{server}/upload/image",
            files={"image": (os.path.basename(image_path), f, "image/jpeg")},
            timeout=60,
        )
    r.raise_for_status()
    return r.json()["name"]


def _extract_text(outputs: dict) -> str:
    """从 outputs 里取反推文本（兼容多节点/多字段）。"""
    for nid in (OUTPUT_NODE_ID,):
        node_out = outputs.get(nid)
        if not node_out:
            continue
        for field in ("text", "anything", "value", "string"):
            val = node_out.get(field)
            if val is None:
                continue
            if isinstance(val, list):
                val = "\n".join(str(x) for x in val)
            val = str(val)
            if val.strip():
                return val
    # 兜底：扫全部节点找最长的字符串
    best = ""
    for node_out in outputs.values():
        for val in node_out.values():
            if isinstance(val, list):
                val = "\n".join(str(x) for x in val)
            if isinstance(val, str) and len(val) > len(best):
                best = val
    return best


def run(image_path: str, server: str = DEFAULT_COMFYUI_SERVER,
        tier: str = "local") -> str:
    """单纯 qwen 3.8 反推提示词，不出图。

    Args:
        image_path: 参考图路径
        server: ComfyUI server URL

    Returns:
        str: 反推文本（8 段编号格式，英文）

    Raises:
        RuntimeError: 工作流不存在 / ComfyUI 不通 / 反推失败或超时
    """
    if not os.path.exists(image_path):
        raise RuntimeError(f"参考图不存在: {image_path}")

    wf_path = WORKFLOW_TIERS.get(tier)
    if not wf_path:
        raise RuntimeError(f"🔴 未知反推档位 {tier!r}，可选: {list(WORKFLOW_TIERS)}")
    if not os.path.exists(wf_path):
        raise RuntimeError(f"🔴 反推工作流不存在: {wf_path}")

    # Step 1: 上传图
    uploaded_name = upload_image(image_path, server)
    print(f"[yuer_qwen_reverse_only] 📤 上传: {uploaded_name}", flush=True)

    # Step 2: 加载工作流
    with open(wf_path, encoding="utf-8") as f:
        wf = json.load(f)

    # Step 3: 改 LoadImage.image（qwen 3.8 工作流的加载节点 id 动态找）
    patched = False
    for nid, node in wf.items():
        if node.get("class_type") == "LoadImage":
            node["inputs"]["image"] = uploaded_name
            print(f"[yuer_qwen_reverse_only]   节点 {nid} LoadImage → {uploaded_name}", flush=True)
            patched = True
            break
    if not patched:
        raise RuntimeError("🔴 工作流里没找到 LoadImage 节点")

    # Step 4: 提交
    r = requests.post(f"{server}/prompt", json={"prompt": wf}, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"提交失败 HTTP {r.status_code}: {r.text[:400]}")
    prompt_id = r.json()["prompt_id"]
    print(f"[yuer_qwen_reverse_only] 📝 提交: {prompt_id}", flush=True)

    # Step 5: 轮询
    for i in range(POLL_MAX):
        time.sleep(POLL_INTERVAL)
        try:
            r = requests.get(f"{server}/history/{prompt_id}", timeout=15)
        except requests.RequestException:
            print(f"[yuer_qwen_reverse_only]   等待 ({(i + 1) * POLL_INTERVAL}s)...", flush=True)
            continue
        if r.status_code != 200:
            continue
        data = r.json()
        if prompt_id not in data:
            print(f"[yuer_qwen_reverse_only]   等待 ({(i + 1) * POLL_INTERVAL}s)...", flush=True)
            continue
        status = data[prompt_id].get("status", {})
        outputs = data[prompt_id].get("outputs", {})
        if outputs:
            text = _extract_text(outputs)
            if text.strip():
                print(f"[yuer_qwen_reverse_only] ✅ 反推完成 "
                      f"({(i + 1) * POLL_INTERVAL}s) {len(text)} 字符", flush=True)
                return text
        if status.get("completed", False):
            msg = json.dumps(status, ensure_ascii=False)[:400]
            raise RuntimeError(f"工作流执行完成但无文本输出: {msg}")

    raise RuntimeError(f"反推超时 ({POLL_MAX * POLL_INTERVAL}s): {prompt_id}")


# ══════════════════════════════════════════════════════════════
# 🔴 统一反推入口（11-04 主人钦定 · 默认 AGNES，本地两档兜底）
# ══════════════════════════════════════════════════════════════
def _run_agnes(image_path: str) -> str:
    """走 AGNES 云端 API（默认主链路）。"""
    import importlib.util
    if not os.path.exists(AGNES_SCRIPT):
        raise RuntimeError(f"🔴 AGNES 反推脚本不存在: {AGNES_SCRIPT}")
    spec = importlib.util.spec_from_file_location("yuer_agnes_rev", AGNES_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.reverse(image_path)


def reverse(image_path: str, tier: str = DEFAULT_TIER, server: str = DEFAULT_COMFYUI_SERVER) -> str:
    """统一反推入口。

    Args:
        image_path: 参考图路径
        tier: agnes(默认·云端) / local(本地9B兜底) / fast(本地4B兜底·粗筛)
        server: ComfyUI 服务端地址（仅本地档用）

    Returns:
        str: 反推文本
    """
    if tier == "agnes":
        return _run_agnes(image_path)
    if tier in WORKFLOW_TIERS:
        return run(image_path, server=server, tier=tier)
    raise RuntimeError(f"🔴 未知反推档位 {tier!r}，可选: {list(REVERSE_TIERS)}")

if __name__ == "__main__":
    tier = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TIER
    if len(sys.argv) < 2:
        print("用法: python3 yuer_qwen_reverse_only.py <image_path>", file=sys.stderr)
        sys.exit(1)

    try:
        text = reverse(sys.argv[1], tier=tier)
        print("\n=== 反推提示词 ===")
        print(text)
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
