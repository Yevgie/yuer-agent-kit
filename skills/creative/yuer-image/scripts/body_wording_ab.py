#!/usr/bin/env python3
"""body_wording_ab.py = 身材/肢体描述句 A/B 实测器 = 「这句到底改不改变画面」

用途 = 写 prompt 前想知道某个身体描述句有没有用 = 0 靠猜 = 跑同 seed 配对实测。
      例：肩宽词到底改不改肩胯比？胳膊粗细词改不改肘距？胯宽句会不会反效果？

跑法（出图 + 量测一条龙）:
    python3 scripts/body_wording_ab.py \
        --control /tmp/p_ctrl.txt \
        --variant S2=/tmp/p_s2.txt --variant W5=/tmp/p_w5.txt \
        --seeds 424242,424243

流程 = 每个 seed 出 1 张 control + N 张 variant（同场景同服装，只换那一句）
     → MediaPipe 量骨架宽 ÷ 体高 → 逐 seed 配对差 → t = Δ/(sd/√n)
     → 骨架指标（肩/肘/胯/肩胯比）+ 剪影指标（剪影胯宽/躯干胯宽/剪影腰胯比/躯干腰胯比）
       两套必须同时看 = 骨架只量到髋【关节】间距 ≠ 视觉胯宽 = 底模改外形时骨架纹丝不动
       （实测：粗臂句顶替后骨架肩/胯比全 ns，剪影胯宽 t=+6.5）= 只看骨架 = 真有效的句被判成白写

判读:
    |t| < 1.5      = 底模不响应这句 = 白写
    t 显著 + 方向一致 = 真改得动
    🔴 批次必带阳性对照（已知有效的句）= 量法没坏才认结论
    🔴 只在同场景同服装下比 = 换场景 = 变量不隔离 = 白跑
    🔴 变体 = 【替换】不【追加】= 追加 = 同部位权重翻倍 = 测出的 t 是污染值 = 结论作废
      = 追加式会把「这句有没有用」和「这个部位权重翻倍」搅在一起 = 两种解释无法分离
      = 烧算力前先跑 --stack-check = 点名哪个部位翻倍 = 有 = 改成替换式再测

环境（一次性自举，缺包缺模型会自动装）:
    python3 scripts/body_wording_ab.py --setup
    装 = venv(mediapipe/numpy/pillow) + MediaPipe pose_landmarker + 分割模型
    缓存位置 = ~/.hermes/cache/body-measure/（可 YUER_BODY_MEASURE_HOME 改）
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys

HOME = os.environ.get("YUER_BODY_MEASURE_HOME",
                       os.path.expanduser("~/.hermes/cache/body-measure"))
VENV = os.path.join(HOME, "venv")
POSE_TASK = os.path.join(HOME, "pose_landmarker_full.task")
SEG_TASK = os.path.join(HOME, "selfie_multiclass_256x256.tflite")
POSE_URL = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
            "pose_landmarker_full/float16/latest/pose_landmarker_full.task")
SEG_URL = ("https://storage.googleapis.com/mediapipe-models/image_segmenter/"
           "selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite")

FAST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yuer_ka_fast.sh")

# 🔴 部位区域词表 = 按区域数「这个部位在稿里被提了几次」
#    = 追加式变体 = 同一区域多一次 = 底模把该部位权重调 N 倍 = 测出的 t 是污染值 = 结论作废
#    只数头部词（her arms）= 不数子部位（her forearms）= 否则正常的一句
#    「her arms thick with muscle, her forearms powerful」会被误报成叠写
BODY_REGION_RES = {
    "hip": re.compile(r"\bher (hips|hip|buttocks|butt|ass)\b", re.I),
    "arm": re.compile(r"\bher (arms|arm)\b", re.I),
    "waist": re.compile(r"\bher waist\b", re.I),
    "chest/breast": re.compile(r"\bher (chest|breasts|breast|bust)\b", re.I),
    "thigh": re.compile(r"\bher (thighs|thigh)\b", re.I),
    "leg": re.compile(r"\bher (legs|leg)\b", re.I),
    "knee": re.compile(r"\bher (knees|knee)\b", re.I),
    "foot": re.compile(r"\bher (feet|foot|toes)\b", re.I),
    "shoulder": re.compile(r"\bher (shoulders|shoulder)\b", re.I),
    "back": re.compile(r"\bher back\b", re.I),
    "belly": re.compile(r"\bher belly\b", re.I),
    "stomach": re.compile(r"\bher stomach\b", re.I),
    "face": re.compile(r"\bher face\b", re.I),
    "eyes": re.compile(r"\bher eyes\b", re.I),
    "hair": re.compile(r"\bher hair\b", re.I),
    "hand": re.compile(r"\bher (hands|hand)\b", re.I),
    "neck": re.compile(r"\bher neck\b", re.I),
}


def stacking_regions(ctrl_text, var_text):
    """返回 [(状态, 区域, 对照次数, 变体次数)]

    状态 = 叠写(污染) = 对照已提过这个部位 = 变体又提一次 = 权重翻倍 = 两种解释无法分离
          = 新增(被测效果) = 对照 0 次 = 变体 1 次 = 这就是要测的那句 = 不算污染
          = 顶替(改了基准) = 变体比对照少提 = 顺带把对照基准也改了 = 读数要打折
    """
    out = []
    for name, rx in BODY_REGION_RES.items():
        a = len(rx.findall(ctrl_text))
        b = len(rx.findall(var_text))
        if b > a:
            state = "叠写(污染)" if a >= 1 else "新增(被测效果)"
            out.append((state, name, a, b))
        elif b < a:
            out.append(("顶替(改了基准)", name, a, b))
    return out


def stack_report(control, variants):
    """体检每个变体是不是追加式 = 点名哪个部位翻倍 = 返回 {变体名: [污染条目]}"""
    if not control:
        print("需要 --control", file=sys.stderr)
        return 2, {}
    try:
        ctrl_text = open(control, encoding="utf-8", errors="ignore").read()
    except OSError as e:
        print(f"读不了 control: {e}", file=sys.stderr)
        return 2, {}
    dirty = {}
    for name, pf in variants:
        try:
            var_text = open(pf, encoding="utf-8", errors="ignore").read()
        except OSError as e:
            print(f"  变体 {name}: 读不了 {pf} ({e})", file=sys.stderr)
            continue
        rows = stacking_regions(ctrl_text, var_text)
        bad = [r for r in rows if r[0].startswith("叠写")]
        other = [r for r in rows if not r[0].startswith("叠写")]
        if bad:
            dirty[name] = bad
            detail = " / ".join(f"{p} {a}→{b}" for _, p, a, b in bad)
            print(f"⚠️ 变体 {name} = 追加式（污染）= {detail} = 该部位权重翻倍 = 这次 t 不作数")
            print("   = 测『这句能不能替掉锚组』= 必须在 control 里删掉对应那句再插这句 = 追加 0 删")
        else:
            print(f"✓ 变体 {name} = 替换式（干净）")
        for state, p, a, b in other:
            print(f"   · {state}：{p} {a}→{b} = "
                  + ("被测效果 = 正常" if state.startswith("新增") else "对照基准被改 = 读数打折"))
    if dirty:
        print(f"\n{len(dirty)} 个变体是追加式 = 结论只认『替换式』那批 = 追加式的 t 写进结论表 = 下次翻车")
    return 0, dirty


# ───────────────────────── setup ─────────────────────────
def _pip_install(venv_python):
    subprocess.check_call([venv_python, "-m", "pip", "install", "--quiet",
                           "mediapipe", "numpy", "pillow"])


def _download(url, dest):
    import urllib.request
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"↓ 模型 {os.path.basename(dest)}")
    urllib.request.urlretrieve(url, dest)


def setup(force=False):
    os.makedirs(HOME, exist_ok=True)
    if force or not os.path.exists(VENV):
        print("· 建 venv")
        subprocess.check_call([sys.executable, "-m", "venv", VENV])
        _pip_install(os.path.join(VENV, "bin", "python"))
    py = os.path.join(VENV, "bin", "python")
    if force or not os.path.exists(POSE_TASK):
        _download(POSE_URL, POSE_TASK)
    if force or not os.path.exists(SEG_TASK):
        _download(SEG_URL, SEG_TASK)
    print(f"✓ setup 完成 → {HOME}")
    print(f"  之后直接跑本脚本（会自动用 venv 里的 python）")
    return 0


def _has_deps():
    try:
        import mediapipe, numpy, PIL  # noqa: F401
        return True
    except Exception:
        return False


def _reexec_in_venv():
    """用 venv 的 python 重跑自己（mediapipe 只装在 venv 里）"""
    py = os.path.join(VENV, "bin", "python")
    if not os.path.exists(py):
        print("缺环境 = 先跑一次: python3 scripts/body_wording_ab.py --setup", file=sys.stderr)
        sys.exit(3)
    os.execv(py, [py, os.path.abspath(__file__)] + sys.argv[1:])


# ───────────────────────── 量测 ─────────────────────────
def measure(path):
    """返回骨架宽/人体高 + 剪影宽/人体高 = 肩跨 / 肘距 / 胯跨 / 肩胯比 / 剪影肩行宽
       + 剪影胯宽 / 剪影腰宽 / 躯干胯宽 / 躯干腰宽 / 剪影腰胯比 / 躯干腰胯比
    🔴 剪影胯宽 = 最大一段（含并入手臂）= 躯干胯宽 = 只取含躯干中心的那一段 = 两个都要看
       = 粗臂句会把垂在体侧的手臂拉宽 = 只看最大一段会把粗臂误读成胯变宽"""
    import numpy as np
    import mediapipe as mp
    from mediapipe.tasks import python as mpp
    from mediapipe.tasks.python import vision
    from PIL import Image

    pose_opts = vision.PoseLandmarkerOptions(
        base_options=mpp.BaseOptions(model_asset_path=POSE_TASK),
        running_mode=vision.RunningMode.IMAGE, num_poses=1,
        min_pose_detection_confidence=0.4, min_pose_presence_confidence=0.4)
    seg_opts = vision.ImageSegmenterOptions(
        base_options=mpp.BaseOptions(model_asset_path=SEG_TASK),
        running_mode=vision.RunningMode.IMAGE, output_category_mask=True)

    im = Image.open(path).convert("RGB")
    W, H = im.size
    arr = np.asarray(im)
    with vision.PoseLandmarker.create_from_options(pose_opts) as pose, \
         vision.ImageSegmenter.create_from_options(seg_opts) as seg:
        pm = mp.Image(image_format=mp.ImageFormat.SRGB,
                      data=np.ascontiguousarray(arr))
        res = pose.detect(pm)
        if not res.pose_landmarks:
            return None
        P = res.pose_landmarks[0]

        def g(i):
            return (P[i].x * W, P[i].y * H)

        ls, rs = g(11), g(12)          # 双肩
        el, er = g(13), g(14)          # 双肘
        lh, rh = g(23), g(24)          # 双胯
        body_h = abs(g(27)[1] - ls[1]) or 1.0
        sh = abs(ls[0] - rs[0])
        elw = abs(el[0] - er[0])
        hip = abs(lh[0] - rh[0])

        # 剪影 = 人像掩膜（hair/skin/clothes 类）
        cm = seg.segment(pm).category_mask.numpy_view()
        mask = (cm == 1) | (cm == 2) | (cm == 3) | (cm == 4)
        sh_y = int((ls[1] + rs[1]) / 2)
        sil = 0
        for y in range(max(0, sh_y - 4), min(H, sh_y + 5)):
            xs = np.where(mask[y])[0]
            if len(xs):
                sil = max(sil, int(xs.max() - xs.min() + 1))

        # 🔴 剪影胯宽 / 躯干腰胯 = 骨架 landmark 量不到的那一维
        #    骨架 23/24 = 髋【关节】间距 ≠ 视觉胯宽 = 底模改的是外形不是骨盆
        #    实测：粗臂句顶替后骨架肩/胯比全 ns（t<2）但剪影胯宽 t=+6.5 = 改动只在剪影上
        #    = 只量骨架 = 真有效果的那句会被判成「白写」= 必须两个都量
        def runs_at(y):
            row = mask[y]
            out, x = [], 0
            while x < W:
                if row[x]:
                    s = x
                    while x < W and row[x]:
                        x += 1
                    out.append((s, x - 1, x - s))
                else:
                    x += 1
            return out

        def max_run(y):
            best = 0
            for y2 in range(max(0, y - 3), min(H, y + 4)):
                for (_s, _e, w) in runs_at(y2):
                    if w > best:
                        best = w
            return best

        def torso_run(y, cx):
            """取含躯干中心 x 的那一段 = 排除垂在体侧的手臂并入"""
            best = 0
            for y2 in range(max(0, y - 3), min(H, y + 4)):
                for (s0, e0, w) in runs_at(y2):
                    if s0 <= cx <= e0 and w > best:
                        best = w
            return best

        hip_y = int((lh[1] + rh[1]) / 2)
        waist_y = int(((g(15)[1] + g(16)[1]) / 2 + (g(23)[1] + g(24)[1]) / 2) / 2)
        hip_cx = (lh[0] + rh[0]) / 2
        waist_cx = (g(15)[0] + g(16)[0]) / 2
        sil_hip = max_run(hip_y)
        sil_waist = max_run(waist_y)
        th_hip = torso_run(hip_y, hip_cx)
        th_waist = torso_run(waist_y, waist_cx)

        return dict(sh=sh / body_h, el=elw / body_h, hip=hip / body_h,
                    ratio=sh / hip if hip else 0.0,
                    sil=sil / body_h, body_h=body_h,
                    sil_hip=sil_hip / body_h, sil_waist=sil_waist / body_h,
                    th_hip=th_hip / body_h, th_waist=th_waist / body_h,
                    waist_hip=(sil_waist / sil_hip) if sil_hip else 0.0,
                    th_waist_hip=(th_waist / th_hip) if th_hip else 0.0)


# ───────────────────────── 出图 + 配对统计 ─────────────────────────
def render(prompt_file, leave, seed):
    """跑快车道（不发飞书）→ 返回落盘 png 路径"""
    before = set(glob.glob("/path/to/media/*.png"))
    r = subprocess.run(["bash", FAST, prompt_file, leave, "--no-send", "--seed", str(seed)],
                       capture_output=True, text=True)
    m = re.search(r"落盘 (\S+\.png)", r.stdout)
    if m and os.path.exists(m.group(1)):
        return m.group(1)
    after = set(glob.glob("/path/to/media/*.png"))
    new = sorted(after - before, key=os.path.getmtime)
    return new[-1] if new else None


def paired(ctrl, var):
    """ctrl/var = {seed: metrics} → 每指标 Δ + t"""
    out = {}
    for k in ("sh", "el", "hip", "ratio", "sil",
              "sil_hip", "sil_waist", "th_hip", "th_waist",
              "waist_hip", "th_waist_hip"):
        ds = [var[s][k] - ctrl[s][k] for s in ctrl if s in var and k in var[s] and k in ctrl[s]]
        if not ds:
            continue
        mean = sum(ds) / len(ds)
        sd = (sum((d - mean) ** 2 for d in ds) / (len(ds) - 1)) ** 0.5 if len(ds) > 1 else 0.0
        t = mean / (sd / len(ds) ** 0.5) if sd > 0 else 0.0
        out[k] = (mean, sd, t, len(ds))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--setup", action="store_true")
    ap.add_argument("--control")
    ap.add_argument("--variant", action="append", default=[], help="NAME=prompt.txt")
    ap.add_argument("--seeds", default="424242,424243")
    ap.add_argument("--no-render", action="store_true", help="只量已有 png（--variant NAME=png）")
    ap.add_argument("--stack-check", action="store_true",
                    help="只体检不跑图 = 查变体是不是追加式（同部位叠写）= 污染 = 结论不作数")
    args = ap.parse_args()

    if args.setup:
        return setup()

    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    variants = []
    for v in args.variant:
        name, _, path = v.partition("=")
        variants.append((name, path))

    if args.stack_check:
        rc, _ = stack_report(args.control, variants)
        return rc

    if not _has_deps():
        _reexec_in_venv()

    ctrl_m, var_m = {}, {}
    if args.no_render:
        for s in seeds:
            pass
    else:
        if not args.control or not variants:
            print("需要 --control 与 --variant NAME=prompt.txt", file=sys.stderr)
            return 2
        for s in seeds:
            if s == seeds[0]:
                _, dirty = stack_report(args.control, variants)
                if dirty:
                    print("🔴 有追加式变体 = 仍会跑 = 但这些变体的 t 只作参考 = "
                          "结论只认替换式那批 = 别把追加式的 t 写进结论表")
            p = render(args.control, f"ab_ctrl_s{s}", s)
            if not p:
                print(f"control seed {s} 出图失败")
                return 2
            ctrl_m[s] = measure(p)
            print(f"  seed {s} control → {os.path.basename(p)}")
            for name, pf in variants:
                p = render(pf, f"ab_{name}_s{s}", s)
                if not p:
                    print(f"  variant {name} seed {s} 出图失败")
                    return 2
                var_m.setdefault(name, {})[s] = measure(p)
                print(f"  seed {s} {name} → {os.path.basename(p)}")

    print("\n=== 配对差 vs 对照组 (t = Δ/(sd/√n), |t|<1.5 = 白写) ===")
    cols = (("sh", "肩/bodyH"), ("el", "肘/bodyH"), ("hip", "胯/bodyH"),
            ("ratio", "肩/胯"), ("sil_hip", "剪影胯宽"),
            ("th_hip", "躯干胯宽"), ("waist_hip", "剪影腰/胯"),
            ("th_waist_hip", "躯干腰/胯"))
    hdr = f"{'变体':<14}" + "".join(f"{n:>20}" for _k, n in cols)
    print(hdr)
    for name, vm in var_m.items():
        st = paired(ctrl_m, vm)
        line = f"{name:<14}"
        for k, _n in cols:
            if k in st:
                mean, sd, t, n = st[k]
                flag = "*" if abs(t) >= 1.5 else " "
                line += f"{mean:+.4f} t{t:+.2f}{flag}".rjust(20)
            else:
                line += " " * 20
        print(line)
    print("\n* = |t|≥1.5 可能真有效；≥2.5 才算稳；n<3 = 别当结论。")
    print("🔴 只认『替换式』变体的 t = 追加式（= 对照已提过的部位又提一次）= 权重翻倍 = "
          "『这句有没有用』与『部位权重翻倍』两种解释分不开 = 该 t 不作数 = 别写进结论表。")
    print("🔴 骨架指标与剪影指标【必须同时看】= 骨架 23/24 只量髋关节间距 = 底模改外形时骨架纹丝不动"
          "（实测粗臂句顶替后骨架肩/胯比全 ns 但剪影胯宽 t=+6.5）= 只看骨架 = 真有效的句被判成白写。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
