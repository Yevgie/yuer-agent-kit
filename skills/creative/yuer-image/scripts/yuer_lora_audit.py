#!/usr/bin/env python3
"""yuer Lora 审计工具（09-26 沉淀 · 10-03 隔离整改）
用法：python3 yuer_lora_audit.py [工作流json路径...]
不传参数 = 默认审计语儿 4 个活工作流。
输出每个工作流里所有 Power Lora Loader 节点的 LoRA 清单（名字 + 强度 + on/off）。
主人问「Lora 开了哪几个 / 强度多少 / 核实一遍强度」= 跑这个脚本，0 手写 grep。
"""
import json, os, sys

# 🔴 10-03 隔离铁律：只审计系统 python 那份（= load_workflow 真正读的那份）
#    之前这里列了 4 条 = 系统那份 2 条 + pipx venv 那 2 条。
#    错因 = ~/.local/bin/comfyui-agent-skill-mie 的 shebang 是 #!/usr/bin/python3
#    → PATH 上那个 CLI 走系统 python = 只读得到系统那份，pipx 那份根本没人读。
#    分工见 assets/workflows/README-归属-语儿专属勿动.md
#    ⚠️ 软链（yuer/ 与 ayao/ 文件夹里）指向同一批实体文件，审计结果一致，不重复列。
WF_DIR = "~/.local/lib/python3.11/site-packages/comfyui/assets/workflows"
DEFAULT_FILES = [
    # 🔴🔴 11-07 08:41 = 只保留一份工作流
    f"{WF_DIR}/yuer_moody_fast.json",
    f"{WF_DIR}/yuer_moody_fast_wash.json",
    # 🔴🔴 11-10 = Moss 线现役档 = 也要进审计（人脸锁 = zxct2.0_figziz_moss-000060 @1.0）
    f"{WF_DIR}/yuer_moodyMoss_fast.json",
    f"{WF_DIR}/api_qwen3.5_9b_反推_默认.json",
]

# 🔴 人脸 LoRA 特征 = 现役两套（Krea2 线 / Moss 线各一）
#    Krea2 线 = zxct2.4_fizgig_krea2-000030 @1.0（11-10 主人更新 lora2.4 五版，照他主机实测档 @1.0）
#    Moss 线 = zxct2.0_figziz_moss-000060 @1.0（11-10 七档实拍对比后钦定 step60）
#    🔴 换版本就要连这里一起换 = 不然人脸槽静默失去 ⭐ 标记 = 排障从错的地方开始查
FACE_LORA = ("zxct2.4_fizgig_krea2", "zxct2.0_figziz_moss")

def audit(fp):
    try:
        w = json.load(open(fp))
    except Exception as e:
        print(f"  ⚠️ {fp}: 读取失败 {e}")
        return
    rows = []
    for nid, node in w.items():
        for k, v in node.get("inputs", {}).items():
            if isinstance(v, dict) and "lora" in v:
                name = str(v.get("lora", "")).replace("\\", "/").split("/")[-1]
                mark = "⭐人脸" if any(f in str(v.get("lora", "")) for f in FACE_LORA) else ""
                rows.append((nid, k, name, v.get("strength"), v.get("on"), mark))
    print(f"\n=== {os.path.basename(fp)} ===")
    for nid, k, name, s, on, mark in rows:
        print(f"  节点{nid} {k}: {name}  强度={s}  on={on}  {mark}")

if __name__ == "__main__":
    files = sys.argv[1:] or [f for f in DEFAULT_FILES if os.path.exists(f)]
    # 🔴 11-09 17:15 主人删了旧 moody fast/wash = 审计不能静默跳过 = 要明说"缺席"
    if not sys.argv[1:]:
        _miss = [f for f in DEFAULT_FILES if not os.path.exists(f)]
        if _miss:
            print("⚠️ 默认档缺席（文件不存在）= 审计结果不完整：")
            for f in _miss:
                print("   ❌", f)
            print("   = 11-09 17:15 主人删了旧 moody fast/wash = 等主人发新的工作流文件。")
    if not files:
        print("❌ 没有任何可审计的工作流文件 = 现役档缺席。")
        sys.exit(1)
    for fp in files:
        audit(fp)
