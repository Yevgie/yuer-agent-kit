#!/usr/bin/env python3
"""Anima 直接提交 ComfyUI 的测试器（10-31 语儿）

🔴 用途 = 绕开主脚本做受控实验（同 seed / 换 LoRA / 换负向 / 分镜验证）
🔴 🔴 关键 = **每次都从当前注册工作流实时读取** = 不会再用到过期副本
   （10-31 踩坑：一直用 /tmp/negvar/old.json = 修复前的带 daod2t 副本 = 白测一堆带水印的图）

用法：
  python3 anima_test.py --prompt-file /tmp/p.txt --out yuer_test --seed 3333
  python3 anima_test.py --prompt-file /tmp/p.txt --out yuer_test --seed 3333 --no-lora 3
  python3 anima_test.py --prompt-file /tmp/p.txt --out yuer_test --seed 3333 --loras "4=0.0,5=0.0"
  python3 anima_test.py --prompt-file /tmp/p.txt --out yuer_test --seed 3333 --negative "xxx,yyy"
"""
import json, os, sys, time, re, urllib.request, urllib.parse

URL = "http://192.168.x.x:8188"
REG = os.path.expanduser("~/.local/lib/python3.11/site-packages/comfyui/assets/workflows")
SHOTS = "/path/to/media"
WORKFLOW = f"{REG}/anima_nsfw.json"


def _find_lora_node(wf):
    for nid, n in wf.items():
        if isinstance(n, dict) and "Lora" in n.get("class_type", ""):
            return nid, n
    return None, None


def build(prompt, seed, no_lora=None, loras=None, negative=None):
    with open(WORKFLOW, encoding="utf-8") as f:
        wf = json.load(f)

    # 正向
    for nid, n in wf.items():
        if not isinstance(n, dict):
            continue
        if n.get("class_type") == "CLIPTextEncode":
            title = n.get("_meta", {}).get("title", "")
            if "Positive" in title or "正向" in title:
                n["inputs"]["text"] = prompt
            elif "Negative" in title or "负向" in title:
                if negative is not None:
                    n["inputs"]["text"] = negative

    # seed
    for nid, n in wf.items():
        if not isinstance(n, dict):
            continue
        ctype = n.get("class_type", "")
        inputs = n.get("inputs", {})
        if ctype in ("SeedNode", "Seed") or (isinstance(inputs.get("seed"), int)
                                            and not isinstance(inputs.get("seed"), bool)):
            inputs["seed"] = seed
        if ctype in ("KSampler", "KSamplerAdvanced"):
            for f in ("seed", "noise_seed"):
                if isinstance(inputs.get(f), int) and not isinstance(inputs.get(f), bool):
                    inputs[f] = seed

    # LoRA 开关 / 权重
    nid, lnode = _find_lora_node(wf)
    if lnode is not None:
        for k, v in lnode["inputs"].items():
            if not (k.startswith("lora_") and isinstance(v, dict)):
                continue
            idx = int(k.split("_")[-1])
            if no_lora and idx in no_lora:
                v["on"] = False
            if loras and idx in loras:
                v["on"] = True
                v["strength"] = loras[idx]
    return wf


def run(prompt, out, seed, no_lora=None, loras=None, negative=None, save=True):
    wf = build(prompt, seed, no_lora, loras, negative)
    body = json.dumps({"prompt": wf, "client_id": "anima_test"}).encode()
    r = urllib.request.urlopen(
        urllib.request.Request(URL + "/prompt", body,
                               headers={"Content-Type": "application/json"}), timeout=60)
    pid = json.loads(r.read())["prompt_id"]
    for _ in range(180):
        time.sleep(1)
        h = json.loads(urllib.request.urlopen(URL + "/history/" + pid, timeout=30).read())
        if pid in h:
            for o in h[pid].get("outputs", {}).values():
                for im in o.get("images", []):
                    q = urllib.parse.quote(im["filename"])
                    sub = urllib.parse.quote(im.get("subfolder", ""))
                    data = urllib.request.urlopen(
                        f"{URL}/view?filename={q}&subfolder={sub}&type=output").read()
                    if save:
                        p = f"{SHOTS}/{out}.png"
                        with open(p, "wb") as f:
                            f.write(data)
                        return p
                    return data
            return None
    return None


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=3333)
    ap.add_argument("--no-lora", default="")     # "3,4"
    ap.add_argument("--loras", default="")       # "4=0.0,5=0.0"
    ap.add_argument("--negative")
    a = ap.parse_args()
    prompt = open(a.prompt_file, encoding="utf-8").read().strip()
    # 🔴🔴🔴 中文自动翻译（10-31）= 受控测试器也必须走翻译，否则中文直喂 Anima 理解差
    if re.search(r"[\u4e00-\u9fff]", prompt):
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from zh_translate import translate_prompt
            _rep = []
            _p = translate_prompt(prompt, report=_rep)
            if _rep:
                print(f"🔴 中文已翻译 {len(_rep)} 段：")
                for _o, _n in _rep[:12]:
                    print(f"   {_o}  →  {_n}")
            prompt = _p
        except Exception as _e:
            print(f"⚠️ 中文翻译跳过（{_e}）")
    nl = [int(x) for x in a.no_lora.split(",") if x.strip()]
    lo = {}
    for pair in a.loras.split(","):
        if "=" in pair:
            k, v = pair.split("=")
            lo[int(k)] = float(v)
    p = run(prompt, a.out, a.seed, nl, lo, a.negative)
    print(f"✅ {p}")
