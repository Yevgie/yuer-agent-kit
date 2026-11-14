#!/usr/bin/env python3
"""反推后端 A/B 基准台 = 同一张图跑不同模型/量化/上游提示词，量耗时 + 输出长度。

用途 = 主人问「哪个反推模型更好」「要不要自己调一下」时 = 先跑这个拿数据，别拍脑袋。

🔴 为什么必须自己跑（而不是查文档）：
  反推耗时 = 端到端墙钟 = 取决于 ComfyUI 端有没有别的任务排队、Flash Attention 开没开、
  模型大小 vs 显存余量。**任何写在文档/注释里的秒数都是某次调度环境下的快照**，
  机器一忙就整倍劣化。选型前必须用本轮真实数字说话。

🔴 「本地 qwen」跑在哪 = 必须先确认：
  本地那台机器（无 GPU 的那台）**跑不动 VL 大模型** = 反推实际跑在 ComfyUI 服务端。
  所以「按我这台电脑的配置选模型」= 先查**服务端**的 GPU/显存，不是本机。
  ```bash
  curl -s --noproxy '*' http://<comfy_host>:8188/system_stats | python3 -c "
  import json,sys; d=json.load(sys.stdin)
  print(d.get('devices')); s=d.get('system',{})
  print('RAM GB', round(s.get('ram_total',0)/1e9,1))"
  ```

🔴 上游提示词是第一个变量，不是最后一个：
  「这个本地模型很烂」这个结论，八成是上游提示词松，不是模型笨。
  **改提示词后必须重跑本台再下结论** —— 同一张图、同一模型，换提示词后输出长度能差一倍以上。
  仓库自带紧约束版模板 = `templates/8段反推提示词-紧约束版.txt`（每段带字数下限 + 第 2 段点名裁切边界
  + 第 5 段禁开尔文 + 第 7 段豁免字数 + 第 8 段点名解剖词）。

用法：
  python3 bench_reverse_backend.py <image> <tag> [主模型] [mmproj] [推理强度] [FlashAttention] [提示词文件]

  不传主模型 = 用工作流默认（当前默认档）
  推理强度 = xhigh / medium / low
  FlashAttention = 开启 / 不开启
  提示词文件 = 覆盖工作流里的「提示词」框（上游 8 段指令）= 换提示词做 A/B

例：
  python3 bench_reverse_backend.py /path/a.png q38_iq3 \\
      'Q38-27B-U-HauhauCS-MTP\\Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-IQ3_XS.gguf' \\
      'Q38-27B-U-HauhauCS-MTP\\mmproj-Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-BF16.gguf' \\
      xhigh 开启

输出 = stdout 打印耗时/字符数，文本落在 /tmp/rev_bench/<tag>.txt（对照用）。

🔴 判读要点（实测得来的，不是推演）：
  · 只看耗时 = 看不出差异 = 质量要看**抓到的细节数**（左手在哪 / 色温 / 指甲 / 道具），
    不是看字符数（长的可能是废话）。
  · **同族模型 + 不同量化** = 唯一变量 = 对照才成立。跨族比（27B vs 4B）= 混淆了
    模型能力差和量化差 = 结论会错。
  · **Flash Attention 开/关 = 独立变量** = 要单独比，否则会把提速误记成量化的功劳。
  · **Q8 不一定比 Q4 好**（小模型上实测反而更差 = 段落标题都掉 = 退化）=
    量化的甜点因模型而异 = 必须实测。
  · **主模型和 mmproj 必须同源同代** = 混搭 = 输出退化（段落标题丢失）。
  · **每段字数下限必须逐段给** = 只给末段（末段给 30-80 词，前 7 段一个字数下限都没有）
    = 9B 一句话交差（实测 1117 字符）、27B 反而自由发挥（2395 字符）
    = **结论会错判成「9B 差、27B 好」**。补齐后 9B 涨到 1801 字符直追 agnes。
  · **给字数下限时，第 7 段（角色外观关键词串）必须豁免** = 加了字数要求它会无限重复关键词，
    实测单段涨到 13464 字符把末段挤掉 = 段落数只有 7 + 耗时 156s。修法 = 第 7 段单独豁免
    + 明写「never repeat a keyword」，修完 57s 8 段齐。
  · **同模型同提示词两次跑可能差 40% 字符数** = 采样随机性 = 单次结果不足以下结论，
    关键对比要跑两次。
"""
import json
import os
import sys
import time

import requests

SERVER = os.environ.get("YUER_COMFYUI_SERVER", "http://192.168.x.x:8188")
WF = "/path/to/workflows/api_qwen3.5_9b_反推_默认.json"
OUT_NODE = "20"
OUT_DIR = "/tmp/rev_bench"

DEFAULT_MODEL = ("Q38-27B-U-HauhauCS-MTP\\"
                 "Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-IQ2_M.gguf")
DEFAULT_MMPROJ = ("Q38-27B-U-HauhauCS-MTP\\"
                  "mmproj-Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-BF16.gguf")

# 工作流里承载上游 8 段指令的输入框名（不同时代版本叫法不同，依次试）
PROMPT_INPUT_KEYS = ("提示词", "prompt", "text", "user_prompt")


def upload(image_path):
    with open(image_path, "rb") as f:
        r = requests.post(
            f"{SERVER}/upload/image",
            files={"image": (os.path.basename(image_path), f, "image/jpeg")},
            timeout=120,
        )
    r.raise_for_status()
    return r.json()["name"]


def extract(outputs):
    for field in ("text", "anything", "value"):
        v = outputs.get(OUT_NODE, {}).get(field)
        if v:
            return "\n".join(v) if isinstance(v, list) else str(v)
    best = ""
    for no in outputs.values():
        for v in no.values():
            if isinstance(v, list):
                v = "\n".join(str(x) for x in v)
            if isinstance(v, str) and len(v) > len(best):
                best = v
    return best


def inject_prompt(wf, prompt_text):
    """把上游 8 段指令写进工作流。返回写入的节点 id；没找到 = 抛错（静默失败最坑）。"""
    for nid, node in wf.items():
        if node.get("class_type") != "QwenTE_ImageInfer":
            continue
        for key in PROMPT_INPUT_KEYS:
            if key in node.get("inputs", {}):
                node["inputs"][key] = prompt_text
                return f"{nid}.{key}"
    raise RuntimeError(
        "工作流里找不到承载上游提示词的输入框 = 节点 "
        f"{PROMPT_INPUT_KEYS} 都不存在 = 别猜，查工作流 JSON 里的真实键名")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    img, tag = sys.argv[1], sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else DEFAULT_MODEL
    mmproj = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] else DEFAULT_MMPROJ
    effort = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] else "xhigh"
    flash = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] else "不开启"
    prompt_file = sys.argv[7] if len(sys.argv) > 7 and sys.argv[7] else ""

    os.makedirs(OUT_DIR, exist_ok=True)
    up = upload(img)

    with open(WF, encoding="utf-8") as f:
        wf = json.load(f)

    prompt_note = "默认提示词"
    if prompt_file:
        with open(prompt_file, encoding="utf-8") as f:
            ptext = f.read().strip()
        where = inject_prompt(wf, ptext)
        prompt_note = f"提示词={os.path.basename(prompt_file)}@{where}"

    for node in wf.values():
        ct = node.get("class_type", "")
        if ct == "LoadImage":
            node["inputs"]["image"] = up
        elif ct == "QwenTE_ModelLoader":
            node["inputs"]["主模型"] = model
            node["inputs"]["视觉投影mmproj"] = mmproj
            node["inputs"]["Qwen3.8推理强度"] = effort
            node["inputs"]["Flash Attention"] = flash
        elif ct == "QwenTE_ImageInfer":
            node["inputs"]["seed"] = 1234567

    t0 = time.time()
    r = requests.post(f"{SERVER}/prompt", json={"prompt": wf}, timeout=120)
    if r.status_code != 200:
        print(f"[{tag}] 提交失败 {r.status_code}: {r.text[:300]}")
        return
    pid = r.json()["prompt_id"]
    print(f"[{tag}] 提交 {pid} model={model.split(chr(92))[-1]} "
          f"effort={effort} flash={flash} {prompt_note}", flush=True)

    for _ in range(400):
        time.sleep(3)
        try:
            d = requests.get(f"{SERVER}/history/{pid}", timeout=20).json()
        except Exception:
            continue
        if pid not in d:
            continue
        text = extract(d[pid].get("outputs", {}))
        if text.strip():
            el = time.time() - t0
            out = os.path.join(OUT_DIR, f"{tag}.txt")
            with open(out, "w", encoding="utf-8") as f:
                f.write(text)
            segs = sum(1 for l in text.splitlines() if l.strip())
            longest = max((len(l) for l in text.splitlines()), default=0)
            print(f"[{tag}] ✅ {el:.1f}s  {len(text)}字符  段落数 {segs}  "
                  f"最长段 {longest}字符 → {out}")
            return
    print(f"[{tag}] ❌ 超时 {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()