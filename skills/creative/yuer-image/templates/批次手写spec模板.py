# -*- coding: utf-8 -*-
"""批次手写 spec 模板（每批复制一份改）

🔴 为什么用字典不用裸元组：
   相邻字符串字面量会静默合并成一段 → 元组少一项 →
   报 "not enough values to unpack" 但错在几百行外 → 极难定位。
   字典 + 字段名断言 = 字段写错当场炸。

🔴 段落顺序是契约（索引器依赖它）：
   [主体+发型][场景]. [机位+焦段+距离][身材锚]Wearing [服装][动作][光线][道具][表情][观看关系], 9:16

🔴 每张先答 8 问，答不上就别写：
   发生什么 / 为何在那 / 谁拍为何 / 知不知 / 还有谁 / 光从哪来 / 动作第二拍 / 哪一瞬
"""
import os
import shutil
import sys

sys.path.insert(0, "~/.hermes/skills/creative/yuer-image/scripts")
from camera_placements import CAMERA_HEIGHT, build_camera, check  # noqa: E402

SECRET = "/path/to/media"
BODY = open(os.path.join(SECRET, "2026-10-28_bodyblock_covered_CURRENT.txt"),
            encoding="utf-8").read().strip()

REQUIRED = {"hair", "scene", "costume", "action", "props", "light", "expr", "beat"}
SPECS = []


def add(name, hk, fk, **kw):
    missing = REQUIRED - set(kw)
    assert not missing, ("缺字段", name, missing)
    SPECS.append(dict(name=name, hk=hk, fk=fk, **kw))


# ── 示例（照这个形状写，5 张各是 5 个不同的画面）──────────────────
# add("n1", "eye_level", "half_body",
#     hair="long dark brown hair in a low ponytail, with a side part",
#     scene="stands at the counter of a small rented kitchen ...",
#     costume="a loose long sleeve t shirt that fully covers her breasts and "
#              "short cotton sleep shorts clearly covering her hips, ...",
#     action="she is leaning over the pot with one hand holding the chopsticks ...",
#     props="a single wall unit kitchen with a sink and a small fridge ...",
#     light="the ceiling light above the counter is the only light ...",
#     expr="she is looking down into the pot and is completely unaware of the camera, ...",
#     beat="this recording exists on a hard drive and nobody who has watched it knows her name")

# ── 景别六档（焦段必跟景别绑定）────────────────────────────────
#   ultra_wide_full 14mm  超广角全景
#   wide_full       28mm  远景
#   full_50         50mm  全身照
#   half_body       85mm  半身照
#   portrait_120   120mm  特写
#   macro_close   100mm  微距特写
# ── 机位五档 ───────────────────────────────────────────────────
#   high_above 高机位俯视 / eye_level 平视 / low_angle 仰视
#   worm_eye 低机位虫眼 / surveillance 监控俯视


def build(batch):
    for s in SPECS:
        prob = check(s["hk"], s["fk"])
        if prob:
            print("!! %s %s 组合不合法: %s" % (batch, s["name"], "; ".join(prob)))
            continue
        cam = build_camera(s["hk"], s["fk"])
        p = ("A photograph shot " + CAMERA_HEIGHT[s["hk"]]["en"]
             + " of a 20 years old young Asian woman with " + s["hair"] + ", " + s["scene"] + ". "
             + cam + " " + BODY + " Wearing " + s["costume"] + " " + s["action"] + " "
             + s["light"] + " " + s["props"] + " " + s["expr"] + ", " + s["beat"]
             + ", 9:16 vertical composition")
        path = "/tmp/prompt_%s_%s.txt" % (batch, s["name"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(p)
        shutil.copy2(path, os.path.join(SECRET, "2026-11-01_%s_%s.prompt.txt" % (batch, s["name"])))
        if not (600 <= len(p) <= 3200):
            print("!! %s %s 字符数异常 = %d（🔴 11-07 长度 0 阻断 = 只报数 = 不拦；真嫌长就删重复的那几句）" % (batch, s["name"], len(p)))
        print("%s %s [%s+%s] %d" % (batch, s["name"], s["hk"], s["fk"], len(p)))


if __name__ == "__main__":
    build(sys.argv[1])
