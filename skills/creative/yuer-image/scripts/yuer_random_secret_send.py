#!/usr/bin/env python3
"""随机从 /path/to/media 抽素材发给主人（图片 + 小视频）。

用法:
  python3 yuer_random_secret_send.py --kind image --count 3
  python3 yuer_random_secret_send.py --kind video --count 1 --max-mb 8
  python3 yuer_random_secret_send.py --kind both --count 2

设计要点（踩过的坑都焊死在这里）:
1. 🔴 一次调用 = 发一组素材 = 每张只发一次。绝不重复调 hermes send 验第二次
   （10-19 实测：yuer_send_v2.sh 发一次 + hermes send 手动两次 = 主人收到 3 份同一个视频）
2. 🔴 视频扩展名走 .mp4/.mov/.avi/.m4v（飞书 media 上传白名单），.mkv/.webm/.flv 不在白名单
3. 🔴 飞书 media 上传大小上限 30MB —— 默认按 max-mb 卡住
4. 🔴 caption 0 路径 0 扩展名 0 MEDIA 字面（否则双发）
5. 🔴 随机池要排除「主人发图」类（那是主人发来让我洗的，不是我的素材库）
6. 🔴 素材库巨大（9万+图），用 os.scandir + reservoir 抽样，不全量 listdir（966G 视频目录会卡）
"""
import argparse
import json
import os
import random
import subprocess
import sys
from pathlib import Path

SECRET_ROOT = Path("/path/to/media")
YUER_ROOT = Path("/path/to/media")   # 语儿自己出的图（=「随机回忆」那个池）
SEND_SH = Path.home() / ".hermes/skills/creative/yuer-image-delivery/scripts/yuer_send_v2.sh"
DEFAULT_TARGET = "feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d"

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
VID_EXT_SEND = {".mp4", ".mov", ".avi", ".m4v"}   # 飞书 media 上传白名单
SKIP_NAME_PREFIX = ("主人发图",)
SKIP_DIR_PARTS = (".trash", "openclaw-bugfix", "三骚狗共享")

# 🔴 合规 caption 池（素材道 caption 铁律见 yuer-image-delivery §零·补七）
# 禁：目录名（"Secret 库"/"安语儿目录"）· 文件名 · 扩展名 · 字节数 · 时间戳 · 工程数字
# 禁：画面内容描述（随机图我没看过 = 0 凭印象写 = 违「无主人口令 0 分析图片内容」）
CAPTION_POOL = [
    "随手翻到这张，主人看看～",
    "语儿在旧相册里刨出来的这一张～",
    "老存货翻出来了，主人收着～",
    "这张藏在角落里的，主人眼福～",
    "语儿随手一抽就抽到这张，运气好吧～",
    "翻到这张的时候语儿停了一下，主人看～",
]


def caption_iter(n: int, override: str | None = None):
    """给 n 张素材各配一句 caption（不重样优先）。"""
    if override:
        return [override] * n
    pool = CAPTION_POOL[:]
    random.shuffle(pool)
    while len(pool) < n:
        pool += CAPTION_POOL[:]
        random.shuffle(pool)
    return pool[:n]


def collect(kind: str, max_mb: int, limit: int, pool: str = "all"):
    """reservoir 抽样 = 内存恒定，不吃磁盘。

    pool:
      yuer = 语儿自己出的图（/path/to/media）= 主人口中的「随机回忆」
      all  = 整个 Secret 库（9万+图）= 主人口中的「所有图片」
    """
    exts = IMG_EXT if kind == "image" else VID_EXT_SEND
    max_bytes = max_mb * 1024 * 1024
    root_dir = YUER_ROOT if (pool == "yuer" and kind == "image") else SECRET_ROOT
    rng = random.Random()
    reservoir = []
    seen = 0
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR_PARTS and not d.startswith(".")]
        for fn in files:
            ext = Path(fn).suffix.lower()
            if ext not in exts or fn.startswith(SKIP_NAME_PREFIX):
                continue
            p = Path(root) / fn
            try:
                st = p.stat()
            except OSError:
                continue
            if st.st_size < 40 * 1024 or st.st_size > max_bytes:
                continue
            seen += 1
            if len(reservoir) < limit:
                reservoir.append((p, st.st_size))
            else:
                j = rng.randrange(seen)
                if j < limit:
                    reservoir[j] = (p, st.st_size)
    return reservoir, seen


def shrink_copy(path: Path, max_side: int = 2600, quality: int = 86) -> Path | None:
    """图超 10MB 时飞书拒收（image upload missing image_key）。
    兜底 = 压一份小图再发。压不出来就返回 None（老实失败，不发半张）。"""
    try:
        from PIL import Image
    except Exception:
        return None
    try:
        im = Image.open(path)
        im.load()
        w, h = im.size
        if max(w, h) > max_side:
            s = max_side / max(w, h)
            im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        out = Path("/tmp") / f"yuer_shrink_{abs(hash(str(path))) % 10**8}.jpg"
        im.save(out, "JPEG", quality=quality, optimize=True)
        if out.stat().st_size < 40 * 1024:
            out.unlink(missing_ok=True)
            return None
        return out
    except Exception:
        return None


def send_one(path: Path, caption: str, target: str) -> bool:
    """发一次 = 一次。🔴 严禁为了「验通路」再发第二遍（10-19 打脸：同一个视频发了 3 遍）。

    唯一的成功信号 = hermes send 的退出码 0（stdout 故意为空 = 正常）。
    ❗重试只允许发生在「第一次明确失败（rc≠0）」时 = 那一次根本没发出去 = 重试不构成双发。
    """
    r = subprocess.run(
        ["bash", str(SEND_SH), str(path), caption, target],
        capture_output=True, text=True, timeout=300,
    )
    if r.returncode == 0:
        return True

    # 失败 = 大概率是图超 10MB。压一份再试一次（仅此一次）。
    if path.suffix.lower() in IMG_EXT:
        small = shrink_copy(path)
        if small:
            r2 = subprocess.run(
                ["bash", str(SEND_SH), str(small), caption, target],
                capture_output=True, text=True, timeout=300,
            )
            small.unlink(missing_ok=True)
            if r2.returncode == 0:
                return True
            sys.stderr.write(f"FAIL(small) {path.name}: {r2.stderr.strip()[:200]}\n")
            return False

    sys.stderr.write(f"FAIL {path.name}: rc={r.returncode} {r.stderr.strip()[:200]}\n")
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["image", "video", "both"], default="image")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--max-mb", type=int, default=0,
                    help="0=按类型自动（图片 9MB / 视频 10MB）")
    ap.add_argument("--img-cap-mb", type=int, default=9,
                    help="图片实际发送上限（飞书 >10MB 拒收）")
    ap.add_argument("--pool", choices=["yuer", "all"], default="all",
                    help="yuer=语儿自己出的图(随机回忆) / all=整个 Secret 库(随机图片)")
    ap.add_argument("--caption", default=None,
                    help="覆盖 caption（默认从合规池抽，禁目录名/文件名/工程数据）")
    ap.add_argument("--target", default=DEFAULT_TARGET)
    args = ap.parse_args()

    kinds = ["image", "video"] if args.kind == "both" else [args.kind]
    n_each = max(1, args.count // len(kinds)) if len(kinds) > 1 else args.count

    sent, failed = [], []
    for k in kinds:
        # 主人钦定：随机视频 = 10MB 以下；图片卡 9MB（飞书硬限 10MB 提前一刀）
        cap_mb = args.max_mb if args.max_mb > 0 else (10 if k == "video" else args.img_cap_mb)
        pool, seen = collect(k, cap_mb, n_each * 4, pool=args.pool)
        if not pool:
            sys.stderr.write(f"NO_POOL {k}\n")
            continue
        picks = random.sample(pool, min(n_each, len(pool)))
        caps = caption_iter(len(picks), args.caption)
        for (p, sz), cap in zip(picks, caps):
            if send_one(p, cap, args.target):
                sent.append({"kind": k, "name": p.name, "bytes": sz})
                # 🔴 caption 由脚本发（yuer_send_v2.sh 内部 hermes send 带上），
                #    不要再在语儿的 reply 里重复念 caption = 0 刷屏 + 0 重复发
                print(f"SENT {k} {p.name} {sz}", flush=True)
            else:
                failed.append({"kind": k, "name": p.name})
                print(f"FAIL {k} {p.name}", flush=True)

    out = {"sent": sent, "failed": failed}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if sent and not failed else (0 if sent else 1)


if __name__ == "__main__":
    sys.exit(main())
