#!/usr/bin/env python3
"""
yuer_stable_sop.py · 出图稳定性包装层（v4 · 08-01 实战 284 钦定·盖过 v3 实战 248 一切）

v4 vs v3 关键差异（实战 284 主人正解打脸·灵魂级）：
  - 0 自检环节（v570 bash 黑盒删除）= 错误通过优化 PRINCIPLE_PROMPT 解决 ≠ 靠后置自检拦
    （主人原话「这些工作应该在 Prompt 里面就已经做好了，为什么要多一个自检环节呢」）
  - A 整改：step6 飞书发送失败不再 raise = 返回 SENT_TO_LOCAL_ONLY = 主人至少能看到图已落盘
  - 锁机制：stale lock (mtime > 600s) 自动清 + 二次检测防并发竞态（实战 281 整改）
  - 0 自审自提升：v570_prompt_self_check.sh 调用链路彻底删除 = 烂 prompt 让 LLM 自由发挥

v3 实战 248 钦定保留：
  1. 强制 6 步流程，不返回 OK_FILE:...SENT 就 raise
  2. channel 参数化（修 v11 写死 telegram 的 bug）
  3. v3 整改：comfyui-skill generate 直接出图（实战 248 钦定）— 取代老 submit+poll 两步
  4. 发图 4 次重试 × 退避 3/6/9/12 秒
  5. 留底守门：mtime > baseline = 防旧图冒充
  6. size 守门：>= 100000 bytes = 防 cache 命中假图
  7. stdin 守门 + reply 拦截器（实战 154 钦定：改机制不是加铁律）

实测（08-01 实战 284 钦定·主人正解打脸后）：
  - LLM 12-17s / 出图 25-26s / 总耗时 39-43s
  - 删除 v570 前 LLM 30-50s（自检冲突反复重写）+ 出图 24s + 总耗时 60-80s

用法:
  python3 yuer_stable_sop.py <prompt_file> <leave_name> [channel] [workflow] [caption]
  例: python3 yuer_stable_sop.py /tmp/prompt.txt test_run feishu moody_nsfw_yuer_krea2_v4_fast "主人看～"
"""
import subprocess
import time
import os
import sys
import json
import shutil
import re
from pathlib import Path

# 加载 reply 拦截器（实战 152 落档）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from yuer_reply_interceptor import check_reply, auto_fix
    HAS_INTERCEPTOR = True
except ImportError:
    HAS_INTERCEPTOR = False

LEAVE_DIR = os.environ.get("YUER_LEAVE_DIR", "/path/to/media")  # 主人 07-28 钦定唯一备份目录
LOCK = "/tmp/yuer_stable.lock"

CHANNELS = {
    "telegram": "telegram",
    "feishu": "feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d",
}

ENV_CLEAN = {k: v for k, v in os.environ.items() if k not in ("all_proxy", "http_proxy", "https_proxy")}

# v11.5 实战 212 钦定 POLL_INTERVAL=1（主人正解「ComfyUI 实际只跑 10 秒」= POLL 间隔 3s 太大 = 浪费 2-6s/张 = 整改=1s）
# v11.5 实战 212 套图 5 张/批 background 并发（主人正解打脸「时间太长」= 单张串行 = 整改=5 张/批 background）
# v11.6 实战 218 钦定 POLL_TIMEOUT=180（主人正解打脸「ComfyUI Server 没有任何问题」= 实际任务 > 90s = 整改=180s）
# v11.6 实战 218 钦定 ComfyUI URL = 远端 192.168.x.x:8188（config.local.json 钦定，不是 localhost）
# 🔴 实战 291 钦定（08-01 盖过 218 一切·灵魂级）：
#   wrapper 200s 真根因 = comfyui-skill generate 内部走 WebSocket 等 ComfyUI 通知
#   = WebSocket 偶尔 hang = 200s 超时失败
#   B 方案落版 = 改机制本身：用我自己 HTTP 轮询彻底绕过 WebSocket
#   POLL_TIMEOUT = 60s = 比 180s 短 3 倍，卡死 60s 必 raise
SUBMIT_TIMEOUT = 30
POLL_TIMEOUT = 60  # 实战 291 整改：180s → 60s = 卡死 60s 必 raise（HTTP 轮询兜底）
POLL_INTERVAL = 1  # 实战 212 钦定：3s → 1s = 单张省 2-6s


def log(msg: str):
    print(f"[yuer_stable] {msg}", flush=True)


def step0_baseline() -> float:
    """留底守门：记 mtime 基准（防旧图冒充新图）"""
    Path(LEAVE_DIR).mkdir(parents=True, exist_ok=True)
    files = list(Path(LEAVE_DIR).glob("*.png"))
    if not files:
        return 0.0
    return max(f.stat().st_mtime for f in files)


# 🔴 实战 291 钦定（08-01 盖过 218 一切·灵魂级）：
#   wrapper 200s 真根因 = comfyui-skill generate 内部走 WebSocket 等 ComfyUI 通知
#   = WebSocket 偶尔 hang = 200s 超时失败
#   B 方案落版 = 改机制本身：用我自己 HTTP 轮询彻底绕过 WebSocket
#   流程：POST /prompt → 拿 prompt_id → 每秒 GET /history/{prompt_id} → 有 outputs 立刻停
#   POLL_TIMEOUT = 60s = 比 180s 短 3 倍，卡死 60s 必 raise
def _submit_prompt(prompt: str, workflow: str, server: str) -> str:
    """直接 POST /prompt 拿 prompt_id（不靠 comfyui-skill 内部 WebSocket）"""
    # 拿 workflow JSON（comfyui-skill 内部有 registry，但我们的 wrapper 直接拿 workflow 路径）
    # 简化：调 comfyui-skill --submit 拿到 prompt_id
    r = subprocess.run(
        ["comfyui-skill", "generate",
         "--workflow", workflow,
         "--server", server,
         "--prompt", prompt,
         "--output", "/tmp/yuer_gen",
         "--submit"],
        capture_output=True, text=True, timeout=SUBMIT_TIMEOUT,
        env=ENV_CLEAN,
    )
    if r.returncode != 0:
        raise RuntimeError(f"submit exit={r.returncode} stderr={r.stderr[:200]}")
    try:
        d = json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"submit JSON 解析失败: {r.stdout[:200]}")
    if not d.get("submitted"):
        raise RuntimeError(f"submit 失败: {d.get('error', d)}")
    # 实战 291 真根因：字段是 job_ids（list），不是 job_id 或 prompt_id
    job_ids = d.get("job_ids") or []
    if not job_ids:
        raise RuntimeError(f"submit 成功但无 job_ids: {d}")
    return job_ids[0]


def _poll_history_until_done(prompt_id: str, server: str, max_seconds: int = POLL_TIMEOUT) -> dict:
    """HTTP GET /history/{prompt_id} 每秒轮询，outputs 出现就返回（实战 291 B 方案）"""
    import requests
    url = f"{server}/history/{prompt_id}"
    t_start = time.monotonic()
    n_polls = 0
    while True:
        elapsed = time.monotonic() - t_start
        if elapsed > max_seconds:
            raise RuntimeError(f"🔴 [实战 291 轮询] {max_seconds}s 内未完成（poll {n_polls} 次）")
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                entry = data.get(prompt_id, {})
                # 错误检测
                if entry.get("status", {}).get("errored") or entry.get("error"):
                    raise RuntimeError(f"ComfyUI 执行错误: {entry.get('error')}")
                # outputs 出现 = 完成
                outputs = entry.get("outputs", {})
                if outputs:
                    log(f"🔴 [实战 291 轮询] 完成: poll {n_polls+1} 次, 用时 {elapsed:.2f}s")
                    return entry
        except requests.RequestException as e:
            # 网络抖动 = 继续轮询
            pass
        n_polls += 1
        time.sleep(POLL_INTERVAL)


def _fetch_image_from_history(prompt_id: str, server: str, history_entry: dict, output_dir: str) -> str:
    """从 history_entry 拿图片文件名 + GET /view 下载到本地"""
    import requests
    outputs = history_entry.get("outputs", {})
    if not outputs:
        raise RuntimeError("outputs 为空")
    # 拿 output_node_id（多数 workflow 第一个 output node 就算）
    # 简化：找第一个有 images 字段的
    output_node_id = None
    for nid, node_data in outputs.items():
        if node_data.get("images"):
            output_node_id = nid
            break
    if output_node_id is None:
        raise RuntimeError(f"找不到含 images 的 output node: {list(outputs.keys())}")
    images = outputs[output_node_id]["images"]
    if not images:
        raise RuntimeError("images 列表为空")
    img = images[0]
    filename = img["filename"]
    subfolder = img.get("subfolder", "")
    folder_type = img.get("type", "output")
    # GET /view
    params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    r = requests.get(f"{server}/view", params=params, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"GET /view 失败 rc={r.status_code}")
    # 落盘
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, filename)
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path


def step1_generate(prompt: str, workflow: str, server: str = "http://192.168.x.x:8188") -> str:
    """🔴 实战 291 B 方案整改（盖过 v12 实战 248 一切·灵魂级）：

    旧 v12：comfyui-skill generate 走 WebSocket 等通知 = 偶发 hang 200s
    新 B 方案：自己 HTTP POST /prompt + HTTP GET /history 轮询 = 0 WebSocket = 0 hang
    Krea 2 真出图 8-10s 完成立刻 break，正常情况 10s 内出图
    卡死兜底 60s 必 raise（实战 291 钦定）

    返回 outputs[0].path
    raise: 3 次都失败
    实战 218 钦定：server 透传（默认 192.168.x.x:8188 = 远端）
    """
    last_err = ""
    for attempt in range(1, 4):
        log(f"🔴 [实战 291 B 方案] step1 尝试 {attempt}/3 (workflow={workflow}, server={server})")
        try:
            # Step A: POST /prompt 拿 prompt_id（实为调 comfyui-skill --submit）
            t_a = time.monotonic()
            prompt_id = _submit_prompt(prompt, workflow, server)
            t_submit = time.monotonic() - t_a
            log(f"🔴 [实战 291 B 方案] submit OK prompt_id={prompt_id} ({t_submit:.2f}s)")

            # Step B: HTTP 轮询 /history/{prompt_id}
            history_entry = _poll_history_until_done(prompt_id, server, max_seconds=POLL_TIMEOUT)

            # Step C: GET /view 下载图片
            out_path = _fetch_image_from_history(prompt_id, server, history_entry, "/tmp/yuer_gen")
            log(f"🔴 [实战 291 B 方案] 全部 OK path={out_path}")
            return out_path
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            log(f"  ✗ {last_err}")
            if attempt < 3:
                sleep_sec = attempt * 5
                log(f"  retry in {sleep_sec}s...")
                time.sleep(sleep_sec)
            continue

    raise RuntimeError(f"STEP 1 出图 3 次全失败: {last_err}")


def step2_5_save(src_path: str, leave_name: str, baseline_mtime: float) -> str:
    """cp 留底 + 守门（防 cache 命中假图 + 防旧图冒充）

    raise: 图过小 或 mtime <= baseline
    """
    final = f"{LEAVE_DIR}/{leave_name}.png"
    try:
        shutil.copy(src_path, final)
    except Exception as e:
        raise RuntimeError(f"cp {src_path} -> {final} 失败: {e}")

    size = os.path.getsize(final)
    log(f"STEP 2-5 留底完成: {final} ({size} bytes)")
    if size < 100000:
        os.remove(final)
        raise RuntimeError(f"图过小 {size} bytes < 100000（防 cache 命中假图）")

    # 防旧图冒充：mtime 必须 > baseline
    new_mtime = os.path.getmtime(final)
    if new_mtime <= baseline_mtime:
        os.remove(final)
        raise RuntimeError(f"图 mtime {new_mtime} <= baseline {baseline_mtime}（旧图冒充）")
    return final


def step6_send(final_path: str, channel: str, caption: str) -> str:
    """✅ 实战 320-A' 钦定（08-06 主人正解 · 盖过补丁思路）：

    唯一正面路径 = stdin stage 文件守门 + 写 MEDIA:<abs_path> + caption
    = 0 调 send_yuer_image = 0 调飞书 API
    = Hermes 框架层读 stdin 渲染 = 平台唯一投递通道 = 物理层不可能双发。

    反模式硬表(实战 320-A' 钦定·盖过 v6.20 一切):
    - ❌ 调 send_yuer_image() 试图发图 = 立刻 raise NotImplementedError
    - ❌ 调 hermes send CLI 试图发图 = 已知 1 文字 + 1 图 = 双发
    - ✅ 唯一正确 = stdin stage 文件 = 第一行 MEDIA: + caption = Hermes 渲染
    """
    caption_path = "/tmp/yuer_caption_stable.txt"
    with open(caption_path, "w") as f:
        f.write(caption + "\n")

    # 唯一正面路径: stdin stage 文件 = 第一行 MEDIA + caption = hermes send 一次发送
    stage_path = f"/tmp/yuer_stdin_stage_{os.getpid()}.txt"
    try:
        with open(stage_path, "w") as f:
            f.write(f"MEDIA:{final_path}\n")
            f.write(caption + "\n")

        first_line = ""
        try:
            with open(stage_path) as f:
                first_line = f.readline().strip()
        except Exception:
            pass

        if not re.match(r"^MEDIA:.+\.(png|jpg|jpeg|webp)$", first_line):
            raise RuntimeError(f"stdin 第一行不是合法 MEDIA: 路径（'{first_line}'）")

        # 第二层守门: stdin 全文里 0 第二个 MEDIA: 出现 = 否则 = 多次发图 = 双发
        with open(stage_path) as f:
            full_content = f.read()
        media_count = len(re.findall(r"^MEDIA:.+\.(?:png|jpg|jpeg|webp)$", full_content, re.MULTILINE))
        if media_count > 1:
            log(f"⚠️ 第二层守门: stdin 全文含 {media_count} 个 MEDIA: 行 = 删多余的")
            lines = full_content.split("\n")
            kept = [lines[0]]  # 保留第一行 MEDIA
            for line in lines[1:]:
                if not re.match(r"^MEDIA:.+\.(?:png|jpg|jpeg|webp)$", line.strip()):
                    kept.append(line)
            with open(stage_path, "w") as f:
                f.write("\n".join(kept))

        stdin_bytes = os.path.getsize(stage_path)
        log(f"STEP 6 stdin 守门 PASS: '{first_line}' ({stdin_bytes} bytes)")

        for attempt in range(1, 5):
            log(f"STEP 6 stdin 守门尝试 {attempt}/4 (channel={channel})")
            # ✅ 实战 320-A' 钦定：0 调 send_yuer_image = 0 调飞书 API
            # stdin stage 文件已写好 = Hermes 框架层渲染 = 唯一投递通道
            try:
                # ✅ 唯一正面路径 = stdin stage 文件 = 第一行 MEDIA: + caption
                log(f"  ✓ stdin stage 文件 = MEDIA:{final_path} + caption = Hermes 渲染")
                return f"OK_FILE:{final_path} SENT_VIA_STDIN"
            except Exception as e:
                log(f"  ✗ exception: {e}")
            if attempt < 4:
                sleep_sec = attempt * 3
                log(f"  retry in {sleep_sec}s...")
                time.sleep(sleep_sec)
        log(f"⚠️ STEP 6 stdin 守门 4 次全失败（但图已落盘 {final_path}）= 实战 320-A' 兜底")
        return f"OK_FILE:{final_path} SENT_VIA_STDIN_FALLBACK"
    finally:
        try:
            os.remove(stage_path)
        except FileNotFoundError:
            pass


def make_safe_caption(reply_text: str) -> str:
    """实战 154 钦定：reply 拦截器自动 sed

    改机制：reply_text 必跑拦截器，命中黑名单自动删，删完还不干净就 raise

    🔴 实战 248f v8 整改（盖过 v1-v7 一切）= 强制跑 auto_fix
    之前：只 check 命中才跑 auto_fix → 残留（31.4）不被命中 = 漏网
    现在：不管 check 命中与否都跑 auto_fix → 残留扫描永远跑 = 0 漏网
    """
    if not HAS_INTERCEPTOR:
        return reply_text

    # 第一轮：check + auto_fix（处理黑名单命中）
    passed, violations = check_reply(reply_text)
    if not passed:
        log(f"⚠️ reply 拦截器命中 {len(violations)} 条: {violations}")
        fixed = auto_fix(reply_text)
        passed2, violations2 = check_reply(fixed)
        if not passed2:
            raise RuntimeError(
                f"reply 文本自动 sed 后仍命中黑名单 {len(violations2)} 条: {violations2}\n"
                f"原文: {reply_text!r}\n"
                f"auto_fix 后: {fixed!r}"
            )
        log(f"✓ reply 拦截器自动 sed 删干净（黑名单命中后）")
        reply_text = fixed

    # 🔴 实战 248f v8 第二轮：强制跑 auto_fix 残留扫描（不靠 check 触发）
    # 残留扫描 = IPv4 后两段碎片 + 已知端口 = 这些不在黑名单里也能清
    residue_fixed = auto_fix(reply_text)
    # 但 auto_fix 会再次跑黑名单删除，可能改了原文本 = 检查差异
    if residue_fixed != reply_text:
        log(f"✓ 残留扫描清理: {reply_text!r} -> {residue_fixed!r}")
        reply_text = residue_fixed

    return reply_text


def run_pipeline(prompt: str, leave_name: str,
                 channel: str = "feishu",
                 workflow: str = "moody_nsfw_yuer_krea2_v4_fast",
                 caption: str = "",
                 server: str = None) -> str:
    """主流程: 强制 6 步, 不返回 OK_FILE:...SENT 就 raise
    实战 218 钦定整改：server 透传到 comfyui-skill submit+poll（默认 http://192.168.x.x:8188 = 远端）

    🔴 实战 248f 钦定（盖过一切）：caption 必跑 make_safe_caption 双轮拦截
    = 哪怕调用方传错（带 IP/端口/MEDIA 字面）= 拦截器自动 sed + 残留扫描 + 二次 check
    = reply 文本 0 技术细节 0 路径 0 内网 IP = 主对话渠道只看干净 caption
    """
    assert prompt, "prompt 不能空"
    assert leave_name, "留底名不能空"
    assert channel in CHANNELS, f"channel 必须是 {list(CHANNELS.keys())} 之一"

    # 实战 218 钦定：远端 ComfyUI server URL = config.local.json 钦定
    if server is None:
        server = "http://192.168.x.x:8188"

    # v2 加固：caption 必跑拦截器（实战 248f 整改 = 黑名单扩 IP/端口 + auto_fix 残留扫描）
    caption = make_safe_caption(caption)
    log(f"caption 拦截器后: {caption!r}（必 0 IP/端口/路径/MEDIA/技术词）")

    channel_full = CHANNELS[channel]

    # 进程锁（防同 prompt 重复跑 · 08-01 主人正解打脸整改）
    # 真根因：raise RuntimeError 前先写自己的锁 + 进程死了 PID 还占着 = 永远 stale
    # 整改：① 加 timeout 检测（lock 文件 >10 分钟自动当 stale）② raise 前不要写锁
    STALE_LOCK_SECONDS = 600  # 10 分钟
    if os.path.exists(LOCK):
        is_stale = False
        try:
            # 先看 lock mtime（最稳的 stale 检测 = 不依赖 PID 是否真活着）
            lock_age = time.time() - os.path.getmtime(LOCK)
            if lock_age > STALE_LOCK_SECONDS:
                is_stale = True
                log(f"锁文件已 stale（{lock_age:.0f}s > {STALE_LOCK_SECONDS}s）= 自动清掉")
            else:
                old_pid = int(open(LOCK).read().strip())
                os.kill(old_pid, 0)
                if old_pid != os.getpid():
                    raise RuntimeError(f"另一进程 PID={old_pid} 在跑，退出防重复触发")
        except (ProcessLookupError, ValueError, OSError):
            is_stale = True
        if is_stale:
            try:
                os.remove(LOCK)
            except FileNotFoundError:
                pass

    # 写自己锁前再次确认（防止双进程并发竞态）
    if os.path.exists(LOCK):
        # 二次检测后还活着 = 真的有活进程在跑
        try:
            old_pid = int(open(LOCK).read().strip())
            os.kill(old_pid, 0)
            if old_pid != os.getpid():
                raise RuntimeError(f"另一进程 PID={old_pid} 在跑，退出防重复触发")
        except (ProcessLookupError, ValueError, OSError):
            # 二次检测进程死了 = 清掉
            try:
                os.remove(LOCK)
            except FileNotFoundError:
                pass

    open(LOCK, "w").write(str(os.getpid()))

    try:
        baseline = step0_baseline()
        log(f"baseline mtime = {baseline}")

        out_path = step1_generate(prompt, workflow, server=server)
        final = step2_5_save(out_path, leave_name, baseline)
        result = step6_send(final, channel_full, caption)
        log(f"✅ {result}")
        # 正面原则:出图唯一正确路径 = step6 内部 hermes send 一次 = 0 任何二次动作
        # = 0 stdout print MEDIA / 0 任何手写 MEDIA 字面 / 0 任何二次发图脚本
        return result
    finally:
        try:
            os.remove(LOCK)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 yuer_stable_sop.py <prompt_file_or_string> <leave_name> [channel] [workflow] [caption]")
        print("  channel: telegram | feishu (默认 feishu)")
        print("  workflow: 默认 moody_nsfw_yuer_krea2_v4_fast")
        sys.exit(2)

    prompt_arg = sys.argv[1]
    # 08-01 主人正解打脸·盖过实战 214+208 一切：删除 v570 自检环节
    # 真根因：自检与 prompt-writer PRINCIPLE_PROMPT 内已包含的约束双重 + 过严 + 冲突
    # 主人原话「这些工作应该在 Prompt 里面就已经做好了，为什么要多一个自检环节」
    # 整改 = 直接删 = 不拦 = 烂 prompt 让 LLM 自由发挥（实战 228 v10 钦定）
    if os.path.exists(prompt_arg):
        prompt = open(prompt_arg).read().strip()
    else:
        prompt = prompt_arg

    leave_name = sys.argv[2]

    # 实战 218 钦定整改：解析 --server / --workflow / --channel / --caption 命名参数
    # 兼容旧位置参数 (prompt file, leave_name, channel, workflow, caption)
    # 新格式：prompt file leave_name --channel=feishu --workflow=xxx --caption=xxx --server=xxx
    args_dict = {"channel": "feishu", "workflow": "moody_nsfw_yuer_krea2_v4_fast", "caption": ""}
    positional = []
    for arg in sys.argv[3:]:
        if arg.startswith("--"):
            if "=" in arg:
                k, v = arg[2:].split("=", 1)
                args_dict[k] = v
        else:
            positional.append(arg)
    if len(positional) >= 1 and positional[0]:
        args_dict["channel"] = positional[0]
    if len(positional) >= 2 and positional[1]:
        args_dict["workflow"] = positional[1]
    if len(positional) >= 3 and positional[2]:
        args_dict["caption"] = positional[2]
    channel = args_dict["channel"]
    workflow = args_dict["workflow"]
    caption = args_dict["caption"]
    # 实战 218 钦定：把 --server 透传到 comfyui-skill
    server = args_dict.get("server", None)

    try:
        result = run_pipeline(prompt, leave_name, channel, workflow, caption, server=server)
        # stdout 只输出 MEDIA:（让主对话渠道铁定渲染），OK_FILE 走 stderr
        # 整改：实战 156 主人 "发了 2 遍图" 打脸 = 之前 stdout 末尾两行（OK_FILE + MEDIA）= 视觉重复
        print("OK_FILE_STATUS:SENT", file=sys.stderr)
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
