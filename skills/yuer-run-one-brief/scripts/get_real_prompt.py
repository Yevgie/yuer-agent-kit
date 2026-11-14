#!/usr/bin/env python3
"""
实战 376 钦定 · 真实 LLM 翻译 prompt 抓取工具
(08-19 · 灵魂级 · 盖过一切 PNG metadata 错误方法)

主人说「给我提示词」= 主人要这张图实际用的 prompt（手测用）=
❌ 错法 1: 读 PNG metadata 节点 849 displaytext (写死的固定文本 ≠ 实际 prompt)
❌ 错法 2: 改 run() 代码 monkey patch log (截断 + 翻车风险高)
✅ 唯一正解: 重新跑同 brief (channel=local 不真发图) + 调 m.fetch_generated_prompt(history_entry)

用法 (实战 376 钦定):
  1. 复制下面这函数到 caller (sandbox / shell / 任何 Python 上下文)
  2. 调 get_real_prompt(brief="...") 拿 string
  3. 直接给主人

API: get_real_prompt(brief: str, workflow: str = "yuer_moody_fast_llm", server: str = "http://192.168.x.x:8188") -> str | None
"""

import sys
import os
import json
import requests

# 实战 319 钦定路径金标准 (实战 373 验证过)
SCRIPTS_DIR = "~/.hermes/skills/creative/yuer-image/scripts"
DEFAULT_SERVER = "http://192.168.x.x:8188"
DEFAULT_WORKFLOW = "yuer_moody_fast_llm"


def get_real_prompt(brief: str,
                    workflow: str = DEFAULT_WORKFLOW,
                    server: str = DEFAULT_SERVER,
                    leave_name: str = "抓取_prompt_测试") -> str | None:
    """实战 376 钦定: 跑 brief + 抓真实 LLM 翻译 prompt

    Returns:
        完整 prompt string (0 截断), 或 None 如果失败
    """
    if not os.path.isdir(SCRIPTS_DIR):
        raise RuntimeError(f"实战 373 路径金标准失效: {SCRIPTS_DIR} 不存在")

    sys.path.insert(0, SCRIPTS_DIR)
    import yuer_run_one_brief as m  # noqa: E402

    captured_pid = None
    orig_log = m.log

    def patched_log(msg):
        nonlocal captured_pid
        if "prompt_id=" in msg:
            idx = msg.find("prompt_id=")
            captured_pid = msg[idx + 10:].strip()
        orig_log(msg)

    m.log = patched_log
    try:
        # channel=local = 不真发图 (实战 376 钦定)
        m.run(brief=brief, leave_name=leave_name, channel="local",
              caption="", workflow=workflow)
    except Exception:
        pass
    finally:
        m.log = orig_log

    if not captured_pid:
        return None

    try:
        h = requests.get(f"{server}/history/{captured_pid}", timeout=10).json()
    except Exception:
        return None

    if captured_pid not in h:
        return None

    # 实战 376 真根因: outputs["849"]["text"] = LLM 翻译结果
    # (节点 849 inputs.displaytext 是写死的固定文本 ≠ 实际 prompt)
    return m.fetch_generated_prompt(h[captured_pid])


if __name__ == "__main__":
    # CLI 用法: /usr/bin/python3 get_real_prompt.py "<brief>"
    import subprocess
    brief = sys.argv[1] if len(sys.argv) > 1 else "1girl, solo, 20 years old, Chinese girl"
    prompt = get_real_prompt(brief=brief)
    if prompt:
        print(f"=== 真实 prompt ({len(prompt)} 字符) ===")
        print(prompt)
        print("=== END ===")
        sys.exit(0)
    else:
        print(f"❌ 抓 prompt 失败 (brief={brief!r})")
        sys.exit(1)