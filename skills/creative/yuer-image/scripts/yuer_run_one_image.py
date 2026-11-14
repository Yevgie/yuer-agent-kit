#!/usr/bin/env python3
"""
yuer_run_one_image.py - DEPRECATED - 08-05 实战 319 钦定(盖过一切)

**本脚本已废弃. 08-05 实战 319 钦定: SOP-B 一句话出图原路径(yuer-prompt-writer + yuer_image_constants + yuer_run_one_image.run() = 调 LLM 翻译子进程 + 拼灵魂脸 PREFIX + yuer_stable_sop)全部删除.**

唯一一句话出图入口 = yuer_run_one_brief.run() = 走 yuer_moody_fast_llm 工作流
= 上传 brief -> 工作流内嵌 MiniMax M2.7 LLM + 内置实战 318 破甲 XML + 实战 313 灵魂面容 + 实战 313 Krea 2 摄影风 -> 自动翻译成高质量英文 prompt -> Krea 2 LoRA 出图 + 发图.

调用 run() 会立刻 raise, 不再静默运行.

原功能如需恢复:
  - 一句话出图 = yuer_run_one_brief.run(brief, leave_name, channel, caption) = 走 yuer_moody_fast_llm 工作流
  - 端到端 32s(实测) = 比旧 48s 更快 = 更稳
"""


def run(*args, **kwargs):
    """DEPRECATED - 08-05 实战 319 钦定 - 已废弃"""
    raise RuntimeError(
        "yuer_run_one_image.run() 已废弃 (08-05 实战 319 钦定 盖过一切). "
        "唯一一句话出图入口 = yuer_run_one_brief.run() = 走 yuer_moody_fast_llm 工作流."
    )


def _assert_no_duplicate_prompts(*args, **kwargs):
    """DEPRECATED"""
    raise RuntimeError("yuer_run_one_image._assert_no_duplicate_prompts() 已废弃")


def _assert_media_paths(*args, **kwargs):
    """DEPRECATED"""
    raise RuntimeError("yuer_run_one_image._assert_media_paths() 已废弃")


def _generate_one_and_send(*args, **kwargs):
    """DEPRECATED"""
    raise RuntimeError("yuer_run_one_image._generate_one_and_send() 已废弃")


def _make_leave_name(*args, **kwargs):
    """DEPRECATED"""
    raise RuntimeError("yuer_run_one_image._make_leave_name() 已废弃")


def _count_nsfw_tags(*args, **kwargs):
    """DEPRECATED"""
    raise RuntimeError("yuer_run_one_image._count_nsfw_tags() 已废弃")


def _make_caption_from_prompt(*args, **kwargs):
    """DEPRECATED"""
    raise RuntimeError("yuer_run_one_image._make_caption_from_prompt() 已废弃")