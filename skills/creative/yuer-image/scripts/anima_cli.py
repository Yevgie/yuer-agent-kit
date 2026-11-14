#!/usr/bin/env python3
"""Anima 出图 CLI（10-31 语儿）

🔴 一个命令出图 = 选预设 → 存提示词 → 走主脚本 → 落盘 + 发飞书

用法：
  # 列出全部预设
  python3 anima_cli.py --list

  # 只生成提示词（不跑图）
  python3 anima_cli.py --preset youth_vitality --seed 42

  # 生成 + 直接出图（推荐）
  python3 anima_cli.py --preset youth_vitality --out yuer_youth_test --seed 42

  # 手动指定内容（不走预设）
  python3 anima_cli.py --tags "1girl, solo, nude, running" \
      --scene "a sunny beach" --action "running along the shore" \
      --camera "low angle" --out yuer_manual

  # 从法典检索并出图
  python3 anima_cli.py --codex --kw 泳装 --out yuer_codex

  # 只转法典权重语法
  python3 anima_cli.py --codex --kw 泳装 --toanima --out /tmp/p.txt
"""

import argparse, json, os, random, subprocess, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anima_templates as AT

KA_RUN = os.path.expanduser("~/.hermes/skills/creative/yuer-image/scripts/yuer_ka_fast.sh")
SHOTS = "/path/to/media"
DATE = None


def _today():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d")


def cmd_list(args):
    print(f"🔴 {len(AT.TEMPLATE_PRESETS)} 个预设\n")
    groups = {
        "青春活力": ["youth_vitality", "summer_pool", "sakura_spring", "festival_night"],
        "强调/诱惑": ["foot_focus_soles", "teasing_sensual", "public_exposure"],
        "多人": ["yuri_trio"],
        "分镜/漫画": ["comic_3koma_vertical", "comic_4koma_grid", "manga_bw_screentone"],
        "SM/成人向": ["bondage_shibari", "outfit_rework", "missionary_topdown"],
    }
    for g, names in groups.items():
        print(f"  【{g}】")
        for n in names:
            if n in AT.TEMPLATE_PRESETS:
                P = AT.TEMPLATE_PRESETS[n]
                print(f"    {n:26s} {P.get('tags','')[:72]}")
    print(f"\n  用法：python3 {os.path.basename(__file__)} --preset <名字> --out <落盘名>")


def cmd_codex(args):
    """🔴 法典检索 → 提示词 → 出图"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "nai_codex",
        os.path.expanduser("~/.hermes/skills/creative/yuer-style-library/nai_codex.py"))
    nc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nc)

    # 🔴 直接用模块函数（nai_to_anima(prompt) = 权重语法转换器）
    idx = json.load(open("/path/to/nai_codex/derived/suozhang_nai5_r18.index.json",
                         encoding="utf-8"))
    hits = [e for e in idx["entries"]
            if args.kw in (e.get("prompt") or "") or args.kw in (e.get("title") or "")
            or args.kw in "/".join(e.get("path") or [])]
    if not hits:
        print(f"❌ 法典里没找到「{args.kw}」")
        return
    hit = random.choice(hits)
    raw = hit.get("prompt") or ""
    prompt = nc.nai_to_anima(raw) if raw else ""
    if not prompt:
        print("❌ 该条没有 prompt")
        return
    print(f"🔴 法典命中 [{hit['title']}]  ({len(raw)} → {len(prompt)} chars)")
    # 🔴 --out 在 codex 模式下 = 落盘名（不是提示词路径）；--toanima 才是提示词路径
    path = args.out if (args.toanima and args.out) else f"/tmp/anima_codex_{args.kw}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"✅ 提示词已存 {path}")
    print(prompt[:500])
    if args.gen:
        args.prompt_file = path
        run_gen(args)


def build_prompt(args):
    if args.prompt_file:
        with open(args.prompt_file, encoding="utf-8") as f:
            return f.read().strip()
    if args.preset:
        if args.preset not in AT.TEMPLATE_PRESETS:
            print(f"❌ 未知预设 {args.preset}")
            sys.exit(1)
        p = AT.build_prompt(
            preset=args.preset,
            tags=args.tags or "",
            scene=args.scene or "", action=args.action or "",
            expression=args.expression or "", camera=args.camera or "",
            light=args.light or "", cloth=args.cloth or "",
            motion=args.motion or "", mood=args.mood or "",
            rnd=random.Random(args.seed if args.seed is not None else random.randint(0, 10**9)))
    else:
        p = AT.build_prompt(
            tags=args.tags or "", scene=args.scene or "", action=args.action or "",
            expression=args.expression or "", camera=args.camera or "",
            light=args.light or "", cloth=args.cloth or "",
            motion=args.motion or "", mood=args.mood or "",
            rnd=random.Random(args.seed if args.seed is not None else random.randint(0, 10**9)))
    return p


def run_gen(args):
    prompt = build_prompt(args)
    tmp = f"/tmp/anima_cli_{args.out or 'tmp'}.txt"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"📝 提示词 [{len(prompt)} chars] → {tmp}")

    name = args.out or f"anima_cli_{random.randint(1000,9999)}"
    sent = os.path.join(SHOTS, f"{name}.sent")
    if os.path.exists(sent):
        os.remove(sent)   # 🔴 .sent 守卫会拦重跑
    model = getattr(args, "model", None) or "anima"
    cmd = ["bash", KA_RUN, tmp, name, "--model", model]
    if args.seed is not None:
        cmd += ["--seed", str(args.seed)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    out = r.stdout + r.stderr
    for line in out.splitlines():
        if any(k in line for k in ("落盘", "完成", "真发", "❌", "正向约束", "timing")):
            print("  " + line.strip())
    final = os.path.join(SHOTS, f"{name}.png")
    if os.path.exists(final):
        print(f"✅ 完成 = {final}")
    else:
        cand = sorted([x for x in os.listdir(SHOTS)
                       if x.startswith(name) and x.endswith(".png")])
        print(f"✅ 完成 = {os.path.join(SHOTS, cand[-1]) if cand else '未找到落盘'}")



def cmd_cx(args):
    """🔴 法典直出 = 角色档案 + 画师比例 + 尺寸"""
    import anima_templates as AT
    prompt = AT.build_from_codex(
        kw=args.kw, n_roles=args.cx_roles, path=args.cx_path,
        artist_group=args.artist_group, with_artists=not args.no_artists)
    if not prompt:
        print("❌ 法典没命中")
        return
    print(f"🔴 法典直出 [{len(prompt)} chars]")
    print(prompt[:600])
    if args.out:
        path = args.out if args.out.endswith(".txt") else args.out + ".txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"✅ 已存 {path}")
    if args.gen:
        args.prompt_file = path if args.out else "/tmp/anima_cx.txt"
        if not args.out:
            with open(args.prompt_file, "w", encoding="utf-8") as f:
                f.write(prompt)
        run_gen(args)



def cmd_raven(args):
    """🔴🔴 渡鸦词库直出 = 二级分类抽词 + 画风层 + 中文字幕检索"""
    import anima_templates as AT
    import raven_vocab as RV
    groups = args.groups or "hair,eye,expression,pose,scene,view,light"
    seed = args.seed if args.seed is not None else 7

    # 🔴 --kw 命中时 = 把命中的 tag 强制加进提示词
    forced = []
    if args.kw:
        hits = RV.search(args.kw, limit=args.kw_limit or 6,
                         loose_limit=0 if args.kw_exact else args.loose_limit)
        if not hits:
            print(f"❌ 渡鸦没命中 [{args.kw}]")
            return
        print(f"🔴 渡鸦命中 [{args.kw}] {len(hits)} 条：")
        for grp, it in hits:
            t = RV.clean_tag(it.get("tag"))
            print(f"   [{grp}] {t}  |  {it.get('title')}  |  {str(it.get('note'))[:70]}")
            if t and t not in forced:
                forced.append(t)

    head = args.head
    if forced:
        head = (head + ", " if head else "") + ", ".join(forced)

    if args.style:
        prompt = AT.build_raven_style(style_id=args.style, groups=groups, n=args.n,
                                      seed=seed, sub=args.sub, head=head)
    else:
        prompt = AT.build_raven(groups=groups, n=args.n, seed=seed, sub=args.sub,
                                head=head)
    print(f"\n🔴 渡鸦组装 [{len(prompt)} chars]")
    print(prompt[:700])
    if args.out:
        path = args.out if args.out.endswith(".txt") else args.out + ".txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"✅ 已存 {path}")
    if args.gen:
        args.prompt_file = path if args.out else "/tmp/anima_raven.txt"
        if not args.out:
            with open(args.prompt_file, "w", encoding="utf-8") as f:
                f.write(prompt)
        run_gen(args)



def cmd_jiegao(args):
    """🔴🔴🔴 解构原典直出 = 一整套作品级配方（画风 + 角色 + 构图 + 道具）

    🔴 --jiegao <关键词>       = 搜解构原典（标题 + tags + 路径）
    🔴 --jiegao-title <精确标题> = 精确取一套配方
    🔴 --jiegao-chapter <专章>   = 风格专章 / 人物专章 / 构图专章 / 魔法教程
    🔴 --jiegao-list              = 列专章统计
    🔴 配方里默认剥 NAI 默认尾 + 修括号不平衡
    """
    sys.path.insert(0, os.path.expanduser("~/.hermes/skills/creative/yuer-style-library"))
    import nai_codex3 as NC

    if args.jiegao_list:
        import collections
        c = collections.Counter()
        for e in NC.jiegao_chapters():
            for pp in (e.get("path") or []):
                c[pp] += 1
        for k, v in c.most_common():
            print(f"  {v:>4}  {k}")
        return

    prompt = NC.jiegao_build(kw=args.jiegao, chapter=args.jiegao_chapter,
                             title=args.jiegao_title)
    if not prompt:
        print(f"❌ 解构原典没命中 [{args.jiegao or args.jiegao_title or args.jiegao_chapter}]")
        return
    print(f"\n🔴 解构原典配方 [{len(prompt)} chars]")
    print(prompt[:800])

    head = args.head
    if head:
        prompt = head + ", " + prompt

    path = None
    if args.out:
        path = args.out if args.out.endswith(".txt") else args.out + ".txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"\n✅ 已存 {path}")
    if args.gen:
        if not path:
            path = "/tmp/anima_jiegao.txt"
            with open(path, "w", encoding="utf-8") as f:
                f.write(prompt)
        args.prompt_file = path
        run_gen(args)



def cmd_mix(args):
    """🔴🔴🔴 三源合流 = 角色档案（--cx）+ 渡鸦细节（--raven）+ 解构配方（--jiegao）

    🔴 一次出图拿三层：
       ① --cx      = 法典角色档案 + 画师组 = 人物骨架
       ② --raven   = 渡鸦词库抽词 = 表情/姿势/场景/光细节
       ③ --jiegao  = 解构原典 = 作品级整套配方（画风 + 角色 + 构图 + 道具）
       ④ --style   = 我的画风层（如 film_painterly）
    """
    sys.path.insert(0, os.path.expanduser("~/.hermes/skills/creative/yuer-style-library"))
    import anima_templates as AT
    import raven_vocab as RV
    import nai_codex3 as NC

    seed = args.seed if args.seed is not None else 7
    # 🔴 合流时渡鸦默认只抽**细节组** = 场景/光线/道具由解构配方负责
    #    （否则会出现 body_soaping + canyon 混进「红黑魔女」这种不搭）
    groups = args.groups or ("hair,eye,expression,pose,scene,view,light" if args.full_raven
                             else "hair,eye,expression,pose")
    layers = []

    # 🔴 ① 解构原典 = 底座
    jg = NC.jiegao_build(kw=args.jiegao, chapter=args.jiegao_chapter, title=args.jiegao_title)
    if jg:
        print(f"🔴 [1/4] 解构原典配方 {len(jg)} chars")
        layers.append(jg)

    # 🔴 ② 角色档案 + 画师组
    cx = ""
    if args.cx:
        cx = AT.build_from_codex(kw=args.cx_kw or args.kw, n_roles=args.cx_roles,
                                  path=args.cx_path, artist_group=args.artist_group,
                                  with_artists=not args.no_artists)
        if cx:
            print(f"🔴 [2/4] 角色档案 {len(cx)} chars")
            layers.append(cx)

    # 🔴 ③ 渡鸦细节
    rv = ""
    if args.raven:
        forced = []
        if args.kw:
            hits = RV.search(args.kw, limit=args.kw_limit or 6,
                             loose_limit=0 if args.kw_exact else args.loose_limit)
            for grp, it in hits:
                t = RV.clean_tag(it.get("tag"))
                if t and t not in forced:
                    forced.append(t)
                    print(f"   [{grp}] {t}  |  {it.get('title')}")
        head = args.head
        if forced:
            head = (head + ", " if head else "") + ", ".join(forced)
        rv = AT.build_raven_style(style_id=args.style, groups=groups, n=args.n,
                                  seed=seed, sub=args.sub, head=head) if args.style \
             else AT.build_raven(groups=groups, n=args.n, seed=seed, sub=args.sub, head=head)
        if rv:
            print(f"🔴 [3/4] 渡鸦细节 {len(rv)} chars")
            layers.append(rv)

    # 🔴 ④ 画风层（如果没走 raven 就单独加）
    if args.style and not args.raven:
        st = AT.build_raven_style(style_id=args.style, groups="", n=0, seed=seed, head=args.head)
        if st:
            print(f"🔴 [4/4] 画风层 {len(st)} chars")
            layers.append(st)

    if not layers:
        print("❌ 至少要 --cx / --raven / --jiegao 其中一个")
        return
    prompt = ", ".join(x for x in layers if x)
    # 🔴 去重（tag 级）
    seen = set(); keep = []
    for t in [x.strip() for x in prompt.split(",") if x.strip()]:
        k = t.lower()
        if k not in seen:
            seen.add(k); keep.append(t)
    prompt = ", ".join(keep)
    print(f"\n🔴 合流 [{len(prompt)} chars]")
    print(prompt[:800])

    path = None
    if args.out:
        path = args.out if args.out.endswith(".txt") else args.out + ".txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"\n✅ 已存 {path}")
    if args.gen:
        if not path:
            path = "/tmp/anima_mix.txt"
            with open(path, "w", encoding="utf-8") as f:
                f.write(prompt)
        args.prompt_file = path
        run_gen(args)



def cmd_desc(args):
    """🔴🔴🔴 中文混合描述直出 = 一句话 → 三层提示词 → 出图

    🔴 例：
       --desc "红黑魔女风格的猫耳腋下少女，夜晚室内，跪姿"
       → ① 解构配方（红黑魔女）② 渡鸦细节（cat_ears/armpits/night/kneeling）
         ③ 普通翻译（indoors）④ 画风层
    """
    import cn_desc as CD
    prompt, d = CD.build(args.desc, style=args.style, seed=args.seed or 7,
                          head=args.head)
    print(f"🔴 配方: {(d['recipe'][:70] or '(无)')}")
    print(f"🔴 渡鸦: {d['raven']}")
    print(f"🔴 翻译: {d['plain']}")
    print(f"\n🔴 组装 [{len(prompt)} chars]")
    print(prompt[:700])

    path = None
    if args.out:
        path = args.out if args.out.endswith(".txt") else args.out + ".txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"\n✅ 已存 {path}")
    if args.gen:
        if not path:
            path = "/tmp/anima_desc.txt"
            with open(path, "w", encoding="utf-8") as f:
                f.write(prompt)
        args.prompt_file = path
        run_gen(args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="列出全部预设")
    ap.add_argument("--preset", help="预设名")
    ap.add_argument("--tags"); ap.add_argument("--scene"); ap.add_argument("--action")
    ap.add_argument("--expression"); ap.add_argument("--camera"); ap.add_argument("--light")
    ap.add_argument("--cloth"); ap.add_argument("--motion"); ap.add_argument("--mood")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--out", help="落盘名（不含日期）")
    ap.add_argument("--gen", action="store_true", help="生成后直接出图")
    ap.add_argument("--codex", action="store_true", help="走 NovelAI 法典")
    ap.add_argument("--kw", help="法典检索关键词")
    ap.add_argument("--toanima", action="store_true", help="只转法典权重语法")
    ap.add_argument("--prompt-file", dest="prompt_file")
    # 🔴 法典直出（角色档案 + 画师比例 + 尺寸）
    ap.add_argument("--cx", action="store_true", help="法典直出：角色档案 + 画师组")
    ap.add_argument("--cx-path", help="法典分类路径，如 视角/强调")
    ap.add_argument("--cx-roles", type=int, help="角色数 1-5")
    ap.add_argument("--artist-group", help="画师组名，如 NAI5时期：3")
    ap.add_argument("--no-artists", action="store_true", help="不套画师组")
    # 🔴 渡鸦词库直出
    ap.add_argument("--raven", action="store_true", help="渡鸦词库直出（二级分类抽词）")
    ap.add_argument("--groups", help="语义组，如 hair,eye,expression,pose,scene,view,light")
    ap.add_argument("--sub", help="二级分类，如 室内空间")
    ap.add_argument("--style", help="画风层 ID，如 film_painterly")
    ap.add_argument("--n", type=int, default=2, help="每组抽几个词")
    ap.add_argument("--head", help="固定开头，如 '1girl, solo, outdoors'")
    ap.add_argument("--kw-limit", type=int, default=6)
    ap.add_argument("--kw-exact", action="store_true", help="只取精确命中（不要 note 弱命中）")
    ap.add_argument("--loose-limit", type=int, default=3, help="弱命中最多几条")
    ap.add_argument("--jiegao", help="解构原典关键词（蒸汽 / 印象风格 / 魔女 …）")
    ap.add_argument("--jiegao-title", help="解构原典精确标题")
    ap.add_argument("--jiegao-chapter", help="专章：风格专章/人物专章/构图专章/魔法教程")
    ap.add_argument("--jiegao-list", action="store_true", help="列专章统计")
    ap.add_argument("--mix", action="store_true", help="🔴 三源合流出图（--cx + --raven + --jiegao）")
    ap.add_argument("--cx-kw", help="角色档案检索词")
    ap.add_argument("--full-raven", action="store_true", help="渡鸦抽全部组（含 scene/light/prop）")
    ap.add_argument("--desc", help="🔴 中文混合描述（自动拆解构配方+渡鸦+翻译）")
    ap.add_argument("--model", default="anima", help="anima(2D) / moss(写实) / krea2(默认写实) / qwen(编辑)")
    args = ap.parse_args()

    if args.list:
        return cmd_list(args)
    if args.desc:
        cmd_desc(args)
        return
    if args.mix:
        cmd_mix(args)
        return
    if args.jiegao or args.jiegao_title or args.jiegao_chapter or args.jiegao_list:
        cmd_jiegao(args)
        return
    if args.raven:
        return cmd_raven(args)
    if args.cx:
        return cmd_cx(args)
    if args.codex:
        if not args.kw:
            print("❌ --codex 需要 --kw")
            sys.exit(1)
        return cmd_codex(args)
    if args.prompt_file:
        return run_gen(args)
    if not (args.preset or args.tags):
        ap.print_help()
        return
    if args.gen:
        return run_gen(args)
    # 只出提示词
    p = build_prompt(args)
    if args.out:
        path = args.out if args.out.endswith(".txt") else args.out + ".txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(p)
        print(f"✅ 已存 {path}  [{len(p)} chars]")
    print(p)


if __name__ == "__main__":
    main()
