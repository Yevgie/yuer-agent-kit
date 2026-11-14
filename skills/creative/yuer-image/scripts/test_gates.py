#!/usr/bin/env python3
"""门禁自测：把已知真洞钉成断言，改门禁后必跑。

用法：
    /usr/bin/python3 ~/.hermes/skills/creative/yuer-image/scripts/test_gates.py

退出码 0 = 全绿；1 = 有回归。
"""
import os
import subprocess
import sys
import tempfile

S = os.path.dirname(os.path.abspath(__file__))
OUTFIT = os.path.join(S, "check_outfit_lock.py")
CHARS = os.path.join(S, "count_prompt_chars.py")
SUBJECT = os.path.join(S, "check_prompt_subject.py")

FAILS = []
PASSES = []


def run(script, txt, extra=None):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                     encoding="utf-8") as f:
        f.write(txt)
        path = f.name
    try:
        r = subprocess.run(
            ["/usr/bin/python3", script, path] + (extra or []),
            capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout
    finally:
        os.unlink(path)


def check(name, cond, detail=""):
    if cond:
        PASSES.append(name)
    else:
        FAILS.append(f"{name}  ← {detail}")


def expect_fail(name, txt, script=OUTFIT, needle=None):
    rc, out = run(script, txt)
    ok = rc != 0 and (needle is None or needle in out)
    check(name, ok, f"rc={rc} out={out[:200]!r}")


def expect_pass(name, txt, script=OUTFIT, needle=None):
    rc, out = run(script, txt)
    ok = rc == 0 and (needle is None or needle in out)
    check(name, ok, f"rc={rc} out={out[:200]!r}")


def expect_warn(name, txt, needle):
    rc, out = run(OUTFIT, txt)
    check(name, rc == 0 and needle in out, f"rc={rc} out={out[:200]!r}")


FULL_OK = ("a full body shot of a young Asian woman wearing a black pleated skirt, "
           "black lace briefs, black high heels, long black hair, black eyeliner, "
           "in a convenience store with a classmate and a notebook on the counter")
HALF_OK = ("a medium shot of a young Asian woman wearing a black pleated skirt, "
           "black lace briefs, long black hair, black eyeliner, "
           "in a convenience store with a classmate and a notebook on the counter")
CLOSE_OK = ("a close-up portrait of a young Asian woman wearing a black spaghetti strap top, "
            "black lace briefs, long black hair, black eyeliner, "
            "warm lamp light, dark blurred background")


def main() -> int:
    # ══ 1. 景别分级 ══
    expect_fail("全身漏鞋 → FAIL",
                "a full body shot of a young Asian woman wearing a black pleated skirt, "
                "black lace briefs, long black hair, black eyeliner")
    expect_fail("中文全身漏鞋 → FAIL",
                "全身构图：一位亚洲女孩穿着黑色短裙，黑色蕾丝内裤，黑色长发，眼线清晰")
    # 🔴🔴 11-07 修真洞 = 判定(退出码) = 展示(屏幕那几行) 必须永远一致
    #    = 旧版展示段独立重算 = 写了 barefoot 时 rc=0 但屏幕显示「FAIL 鞋履」
    #    = 骗主人 + 误导我自己（差点去改一个根本没问题的稿）
    rc, out = run(OUTFIT, "a full body shot of a young Asian woman wearing a black pleated skirt, "
                             "black lace briefs, she is barefoot with her toes curled against the tile, "
                             "long black hair, black eyeliner")
    check("裸脚全身 = rc 0 且不显示 FAIL 鞋履",
          rc == 0 and "FAIL 鞋履" not in out, f"rc={rc} out={out[:220]!r}")
    rc, out = run(OUTFIT, "a full body shot of a young Asian woman wearing a black pleated skirt, "
                             "black lace briefs, long black hair, black eyeliner, standing in a library")
    check("真缺鞋 = rc 1 且显示 FAIL 鞋履",
          rc == 1 and "FAIL 鞋履" in out, f"rc={rc} out={out[:220]!r}")

    # 🔴 11-07 精简 = 半身/特写 = 下半身在画外 = 不该要求写鞋履 = 直接跳过（不是 WARN）
    #    = 旧版报 WARN = 我看到 WARN 就去补鞋履 = 补了 = 逼我写画外的东西 = 裁切线滑下去
    expect_pass("半身漏鞋 → 跳过不查", HALF_OK)
    expect_warn("半身漏鞋 → 明写跳过", HALF_OK, "跳过 鞋履")
    expect_pass("特写 → 不查下装鞋履", CLOSE_OK)

    # ══ 2. 脚部遮挡免检 ══
    expect_pass("脚出画 → 免鞋履",
                "a young Asian woman lying down on a bed with her feet out of frame, "
                "wearing a black dress, black lace briefs, long black hair, black eyeliner")

    # ══ 3. 单人物硬拦 ══
    expect_fail("两人 → FAIL", FULL_OK + ", two women standing together")
    expect_fail("一对 → FAIL", FULL_OK + ", a couple posing")
    expect_fail("中文两人 → FAIL",
                "全身构图：一位亚洲女孩和另一个女孩穿着黑色短裙，黑色蕾丝内裤，"
                "黑色长发，眼线清晰，黑色高跟鞋，便利店里有同学和笔记本")
    expect_pass("背景人群 ≠ 分身",
                "a full body shot of a young Asian woman wearing a black pleated skirt, "
                "black lace briefs, black high heels, long black hair, black eyeliner, "
                "in a busy convenience store with a crowd of people and shelves of products")

    # ══ 4. 双语 ══
    expect_pass("纯中文稿 → 外观锁过",
                "全身构图：一位二十岁的亚洲年轻女性穿着黑色百褶短裙，黑色蕾丝内裤，"
                "黑色长发扎成马尾，眼线清晰，唇色浅粉，脚上是黑色漆皮高跟鞋，"
                "落地窗前，背景是虚化的城市灯光")
    expect_pass("纯英文稿 → 外观锁过", FULL_OK)

    # ══ 5. 连体衣 = 下装已含 ══
    expect_pass("bodysuit = 不算漏下装",
                "a full body shot of a young Asian woman wearing a black lace bodysuit, "
                "black high heels, long black hair, black eyeliner")

    # ══ 6. 长度区间自适应 ══
    rc, out = run(CHARS, FULL_OK)
    check("英文稿走英文标尺", "英文标尺" in out, out[:200])
    # 用真跑过出图的中文稿 = 断言反映真实现场，不是人造样本
    cn = ""
    for cand in ("/tmp/ins5/p1.txt", "/tmp/single5/p1.txt", "/tmp/ins5/p2.txt"):
        if os.path.exists(cand):
            cn = open(cand, encoding="utf-8").read().strip()
            break
    if not cn:
        cn = ("全身构图：一位二十岁的亚洲年轻女性侧身站在便利店门口，"
              "上眼睑半垂，嘴唇微启，下巴微微抬起，目光直直看向镜头，"
              "右手拎着一个帆布袋，左手插在短裙口袋里。"
              "她穿着黑色百褶短裙，短裙底下是黑色蕾丝内裤，"
              "脚上是黑色漆皮细高跟鞋，黑色长发扎成马尾，眼线清晰，唇色浅粉。"
              "店里有同学和收银台上的笔记本，货架上摆着饮料，"
              "落地窗外是虚化的城市灯光，午后三点的大太阳斜照进来，"
              "一块硬边光斑落在她的膝盖上，其余部分沉在阴影里，"
              "85毫米镜头光圈f/2.0，距离四米，浅景深，冷调，"
              "高分辨率且锐利，解剖结构正确的人体")
    rc, out = run(CHARS, cn)
    check("中文稿走中文标尺", "中文标尺" in out, out[:200])
    check("中文真稿不再报偏短", "偏短" not in out, out[:200])
    # 🔴 11-07 主人钦定：长度 0 阻断 = 偏短不报（报偏短 = 诱导我加水词凑数 = 堆料）
    # 注：这稿只有 11 字 = 结构段本来就该 MISS（门槛 3/5）= rc 必然 1 = 只断言长度段不判偏短
    rc, out = run(CHARS, "一位亚洲女孩站在便利店")
    check("中文过短 = 只报数，不判偏短（0 加水词）",
          "偏短" not in out and "字符数: 11" in out, out[:200])
    # 🔴 11-07：长度 0 阻断 = 2000 以内超长也照出 = 0 返工
    rc, out = run(CHARS, cn * 8)
    check("中文超长（<4000）不拦 = 0 返工", rc == 0, f"rc={rc} {out[:160]}")
    # 唯一真硬顶 = 4000 失控稿
    rc, out = run(CHARS, cn * 30)
    check("失控稿（>4000）才拦", rc != 0, f"rc={rc}")

    # ══ 7. 主体门禁 ══
    rc, out = run(SUBJECT, "一位二十岁的亚洲年轻女性，穿着黑色短裙")
    check("中文主体 = 语儿", rc == 0, out[:200])
    rc, out = run(SUBJECT, "a young East Asian woman in her early twenties wearing a dress")
    check("英文「early twenties」= 别人", rc != 0, out[:200])

    # 🔴🔴🔴 11-07 修真 bug（最严重的一类误杀）= 泛身份词被当「别人」
    #    主人自己的原稿（"东亚年轻女性跪在桌下" = 没年龄没语儿锚）= 旧版判「别人」
    #    = 静默切 0 LoRA = 语儿脸锁被剥 = 出来不是语儿的脸 = 整轮白跑
    rc, out = run(SUBJECT, "现实抓拍摄影照片，东亚年轻女性跪在桌下，嘴巴含住椅子上东亚年轻男性的阴茎")
    check("泛身份词（年轻女性）+ 无年龄 = 0 判别人",
          rc != 2, f"rc={rc} out={out[:220]!r}")
    rc, out = run(SUBJECT, "A young woman with long hair standing in a library")
    check("英文泛身份词（young woman）= 0 判别人",
          rc != 2, f"rc={rc} out={out[:220]!r}")
    # 反向 = 真别人一个都不能放跑
    for who in ["A 25 years old celebrity woman in a red dress",
                "A classmate of mine, a 22 years old young woman",
                "A beautiful young Asian woman, age 28, in a library",
                "An actress in her thirties posing for a camera",
                "A stranger passing by on the street",
                "A woman in her mid twenties at a party",
                "A lady in her thirties in a cafe"]:
        rc, out = run(SUBJECT, who)
        check(f"真别人必须拦下 = {who[:38]}", rc == 2, f"rc={rc} out={out[:200]!r}")
    # 语儿的各种写法一个都不能误判
    for ok in ["A 20 years old young Asian woman in a red dress",
               "A beautiful young Asian woman, age 20, in a library",
               "A beautiful young Asian woman, aged 20, in a library",
               "A beautiful young Asian woman, 20-year-old, in a library",
               "A beautiful young Asian woman, twenty years old, in a library",
               "一位二十岁的亚洲年轻女性穿着红色短裙"]:
        rc, out = run(SUBJECT, ok)
        check(f"语儿各种写法必须放行 = {ok[:38]}", rc == 0, f"rc={rc} out={out[:200]!r}")

    # ══ 7b. 画外描述检测（11-04 13:40 实测 22 张沉淀的唯一根因）══
    CHEST_OK = ("a chest-up portrait of a striking young Asian woman, 20 years old, "
                "the frame enclosing her head and her neck and her shoulders and the top of her chest\n"
                "her upper eyelids half-lowered with her gaze fixed on the lens and her lips slightly parted, "
                "a small mole beside her nose, light makeup with black eyeliner and soft pink lipstick\n"
                "her black hair worn in a loose low bun with wispy strands at her temples\n"
                "the sheer black lace of her top across her collarbones and the upper part of her chest, "
                "a fine gold chain with a small pendant\n"
                "the blurred blue city skyline through the window behind her, "
                "85mm lens at f/2.0, shallow depth of field, high resolution and sharp focus, "
                "anatomically correct human body")
    WAIST_OK = ("a waist-up portrait of a striking young Asian woman, 20 years old, "
                "the frame enclosing her head and her shoulders and her chest, "
                "the bottom edge of the frame resting on her waistline\n"
                "her upper eyelids half-lowered with her gaze fixed on the lens and her lips slightly parted, "
                "a small mole beside her nose, light makeup with black eyeliner and soft pink lipstick\n"
                "her black hair worn in a loose low bun with wispy strands at her temples\n"
                "the black lace bodice of her top filling the frame below her collarbones, "
                "a fine gold chain with a small pendant lying on her collarbone\n"
                "the blurred blue city skyline through the window behind her, "
                "85mm lens at f/2.0, shallow depth of field, high resolution and sharp focus, "
                "anatomically correct human body")
    expect_pass("胸像（只写画面内）→ 门禁过", CHEST_OK)
    expect_pass("半身（只写画面内）→ 门禁过", WAIST_OK)
    expect_fail("胸像写了内裤 → 画外描述 FAIL",
                CHEST_OK + "\nwearing black lace briefs and sheer black thigh-high stockings and black high heels")
    expect_fail("半身写了丝袜 → 画外描述 FAIL",
                WAIST_OK + "\nwearing sheer black thigh-high stockings and black high heels")
    expect_fail("胸像写了高跟鞋 → 画外描述 FAIL",
                CHEST_OK + "\nwearing black high heels")

    # 边界句优先于术语词（实测术语词无效 = 门禁不能只认术语词）
    expect_fail("胸像边界句 + 画外裤 → FAIL（边界句优先）",
                "a close-up shot of a young woman, the frame enclosing her head and her neck and her shoulders "
                "and the top of her chest, wearing black lace briefs and black high heels, "
                "light makeup with black eyeliner, long black hair, the blurred blue city skyline behind her, "
                "85mm lens at f/2.0, shallow depth of field, high resolution and sharp focus, "
                "anatomically correct human body")

    # ══ 8. 回归：历史真稿仍过 ══
    for path in ["/tmp/v4b2/p1.txt", "/tmp/v4b2/p5.txt", "/tmp/v4batch/p3.txt",
                 "/tmp/single5/p4.txt", "/tmp/ins5/p1.txt", "/tmp/ins5/p4.txt",
                 "/tmp/ins5/p5.txt"]:
        if not os.path.exists(path):
            continue
        rc, out = run(OUTFIT, open(path, encoding="utf-8").read())
        check(f"回归 {os.path.basename(path)}", rc == 0, out[:160])
        rc2, out2 = run(CHARS, open(path, encoding="utf-8").read())
        check(f"回归字符数 {os.path.basename(path)}", rc2 == 0, out2[:160])

    print(f"\n{'='*56}")
    print(f"通过 {len(PASSES)} / {len(PASSES)+len(FAILS)}")
    for f in FAILS:
        print(f"  ❌ {f}")
    if not FAILS:
        print("  ✅ 全绿")
    print("=" * 56)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
