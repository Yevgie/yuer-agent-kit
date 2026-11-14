# -*- coding: utf-8 -*-
"""批量出图 = 五维变体引擎（v2 · 11-01 主人纠正「五张一重复 没意义」专用）

🔴 11-01 事故 = 639 张图里 100% 共用同一句妆容、98% 共用同一句亮部、
   75% 共用同一句表情、67% 共用同一句构图 + 构图/机位只有两种、身体段只有 2 个变体
   = 主人看到的是「同一张模板换五个场景词」= 换皮不换骨。

🔴 正解 = 把每一维都拆成池子 = 每张各抽一个 = 机械保证不重复。
   维度池（全部从 batch_space_ledger.py 里取 = 只存一份）：
     FACE_POOL       妆容 10 套
     EXPRESSION_POOL 表情 7 套
     FRAMING_POOL    景别+机位 8 套
     LIGHT_POOL      唯一亮部 10 类
     BODY_VARIANTS   身体段 5 变体
   一批 5 张 = 五维各抽 5 个不同项 = 同一批内零重复 + 批与批之间继续轮换。

用法：
    /usr/bin/python3 build_batch_v2.py <batch_id>
"""
import os
import shutil
import sys

sys.path.insert(0, "~/.hermes/skills/creative/yuer-image/scripts")
from batch_space_ledger import (  # noqa: E402
    FACE_POOL, EXPRESSION_POOL, FRAMING_POOL, LIGHT_POOL, BODY_VARIANTS,
)

SECRET = "/path/to/media"
COVER = open(os.path.join(SECRET, "2026-10-28_bodyblock_covered_CURRENT.txt"), encoding="utf-8").read().strip()

NUDE_SHORT = (
    "a tall slender build with elongated vertical proportions, slim yet voluptuous body, "
    "hourglass figure, her legs longer than her torso reaching up to her chest, smooth long "
    "legs with slender firm thighs, a tiny sharply defined waistline that flares out to the hip, "
    "wide hips, a high tight peach shaped bottom, two round buttocks that curve out in a smooth "
    "peach-like swell, large full breasts held up in a lifted rounded shape, a deep natural "
    "cleavage, her pubic mound smooth and bare with no pubic hair at all, the inner labia "
    "small and pink and tightly closed into a neat vertical seam, pale porcelain skin, "
    "luminous ivory skin, smooth soft skin texture, natural skin pores visible")

STYLE = {
    "ins": ("A bright casual lifestyle snapshot taken on an iPhone 15 Pro Max 1x lens at f/1.8, ",
            "a bright airy cheerful colour grade, natural skin tones, sharp focus on her eyes, "
            "photorealistic photography, natural light, no harsh shadows"),
    "cine": ("A cinematic still captured with Sony A7R V and 35mm f/1.4 GM at f/2.0, ",
             "cinematic still, filmic color grading, fine natural film grain"),
    "doc": ("A documentary photograph taken on a Fujifilm X-T5 with 35mm f/1.4 at f/2.8, ",
            "documentary photography, available light, unposed, grain"),
    "ancient": ("A photorealistic photograph taken with Canon EOS R5 and 50mm f/1.2L USM at f/2.0, ",
                "photorealistic photography, available light, fine film grain"),
    "fashion": ("A high-fashion editorial shot lit by a single softbox, captured with "
                "Canon EOS R5 and 85mm f/1.2L USM at f/2.8, ",
                "editorial, high contrast, studio lighting, sharp focus, smooth tonal falloff"),
}


def head(style, hair, scene):
    return STYLE[style][0] + "a 20 years old young Asian woman with " + hair + ", " + scene


def emit(batch, jobs, body=COVER):
    """jobs = [(name, style_key, head段, 服装段, 情绪动作段, 光线段, 背景道具段[, body]), ...]

    🔴 末项判定 = 按内容（hourglass / slender build）= 不按元组长度。
    🔴 服装段必须含下装词（门禁白名单）+ 内层 + 鞋履 + 妆容。
    """
    for job in jobs:
        name = job[0]
        style = job[1]
        head_s = job[2]
        costume = job[3]
        mood = job[4]
        last = job[-1]
        is_body = isinstance(last, str) and ("hourglass" in last or "slender build" in last)
        if is_body:
            tail = " ".join(job[5:-1])
            this_body = last
        else:
            tail = " ".join(job[5:])
            this_body = body
        s = (head_s + this_body + ", " + costume + mood + tail
             + ", " + STYLE[style][1] + ", 9:16 vertical composition")
        path = "/tmp/prompt_%s_%s.txt" % (batch, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(s)
        shutil.copy2(path, os.path.join(SECRET, "2026-11-01_%s_%s.prompt.txt" % (batch, name)))
        if not (600 <= len(s) <= 3200):
            print("⚠️ %s %s 字符数异常 = %d（查 prompt 尾段）" % (batch, name, len(s)))
        print("%s %s [%s] %d" % (batch, name, style, len(s)))
    return ["/tmp/prompt_%s_%s.txt" % (batch, j[0]) for j in jobs]


# ===== 一批 5 张的构造器 =====
# 🔴 每张 = 场景(新) + 服装 + 池子里的第 i 项（表情/亮部/景别/妆容/身体段）
#    = 五张之间五维全不同 = 机械保证 = 不靠我"记得要多样"


def card(name, style, hair, scene, costume, action, light_i, framing_i, face_i,
         body_i=None, props="", extra_light=None):
    """一张图 = 池子组合 = 五维各取一个不同项"""
    body = BODY_VARIANTS[body_i] if body_i else None
    mood = action + " " + EXPRESSION_POOL[face_i] + ", "
    if extra_light:
        mood += extra_light
    light = LIGHT_POOL[light_i]
    job = [name, style, head(style, hair, scene + FRAMING_POOL[framing_i] + ", "),
           costume + FACE_POOL[face_i] + ", ",
           mood,
           light + ", ",
           props]
    if body:
        job.append(body)
    return tuple(job)
