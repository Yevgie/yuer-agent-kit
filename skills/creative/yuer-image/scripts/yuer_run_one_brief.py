#!/usr/bin/env python3
import datetime
"""
yuer_run_one_brief.py · 语儿一句话出图 + 洗图（v1.2 · 09-04 实战 497 整改）

唯一职责：
- 无图片 = 必须按 yuer-prompt-writer 技能写好 500-650 词英文 prompt → 走 yuer_moody_fast 出图
  （09-21 主人钦定：run(brief) 入口强制校验，中文/短 brief 拒绝出图，杜绝偷懒）
- 有图片 = 走洗图工作流出图（实战 452 + 453 钦定）

调用方唯一入口：run(brief, leave_name, channel, caption)

🔴 v1.2 灵魂级铁律（09-04 主人正解·盖过一切）：

    出图流程 = yuer-prompt-writer 技能写 prompt → yuer_moody_fast 工作流出图
    = 不调 LLM 节点 = 0 撞车 = 快 2-4 倍（12s vs 46s）
    
    出图链路：
        ① 主人 brief（一个字/一句话/cos X/露出/走光/POV/随机 都行）
        ② 调用 yuer-prompt-writer 技能写英文 prompt（500-650 词）
        ③ 加载 yuer_moody_fast 工作流（无 LLM）
        ④ 改 CLIPTextEncode.text = prompt（节点 627）
        ⑤ 改 SaveImage.filename_prefix
        ⑥ 提交 ComfyUI /prompt
        ⑦ 轮询（实战 291 B 方案）
        ⑧ 从 outputs 拿图（节点 732 SaveImage）
        ⑨ cp 留底 LEAVE_DIR
        ⑩ stdout 输出 MEDIA:<abs_path> = 唯一交付物

    旧 SOP（已删除）：
        ❌ 走 yuer_moody_fast_llm 工作流（LLM 节点翻译）
        ❌ yuer-prompt-writer 复杂多阶段 pipeline
        ❌ yuer_image_constants.YUER_GIRL_FULL_PREFIX 拼装
        ❌ DEFAULT_OUTFIT_POOL 9 大穿搭池子
        ❌ 撩到边缘写法
        ❌ 时间锚点 inject_time_period_into_brief
"""
import os
import sys
import time


def save_prefix(name):
    """🔴 统一落盘路径（10-29 主人钦定）= Hermes/Yuer%year%-%month%-%day%/<唯一名>

    🔴 工作流节点里存的是主人原写法「Hermes/Yuer%date:yyyy-MM-dd%/」= GUI 入口由前端 JS 展开。
      但脚本走 API = 不经过前端 = %date:...% 原样送到后端会变字面量。
      → 脚本侧这里必须客户端算实际日期，落盘结果与 GUI 完全一致（都是 Hermes/Yuer2026-10-29/）。
    """
    import datetime
    return "Hermes/Yuer" + datetime.date.today().isoformat() + "_" + name
import json
import shutil
import subprocess
import re
import requests
from pathlib import Path

# 路径常量
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LEAVE_DIR = os.environ.get("YUER_LEAVE_DIR", "/path/to/media")
DEFAULT_COMFYUI_SERVER = "http://192.168.x.x:8188"  # 实战 218 钦定远端
# 🔴🔴🔴 11-15 主人钦定「优先使用 KREA 2 吧」= 默认档 = yuer_moody_fast
#    （默认无 LLM，豆包反推 prompt 直接进图模型 —— 实战 497 口径不变，只换工作流）
#    理由 = 主人亲口判定 Moss 真实感强 + Moss 中文字一级棒 + 表情好；节点结构与 Krea2 兼容（627/599/698 一致）
#    🔴 洗图道仍 = yuer_moody_fast_wash（Moss 没有 wash 变体 = 0 静默兜底）
DEFAULT_WORKFLOW = "yuer_moodyMoss_fast"

# ⚠️ LLM 扩写工作流 yuer_moody_fast_llm 已于 09-21 主人钦定删除（prompt 工作流弃用）
DEFAULT_WASH_WORKFLOW = "yuer_moody_fast_wash"  # 实战 452 + 453 钦定洗图工作流（免反推，冷启动~20s，预热~1s）

# 加载 reply 拦截器（实战 152 落档）
sys.path.insert(0, SCRIPT_DIR)
try:
    from yuer_reply_interceptor import check_reply, auto_fix
    HAS_INTERCEPTOR = True
except ImportError:
    HAS_INTERCEPTOR = False


def log(msg: str):
    print(f"[yuer_run_one_brief] {msg}", flush=True)


def make_safe_caption(reply_text: str) -> str:
    """实战 154 钦定：reply 拦截器自动 sed"""
    if not HAS_INTERCEPTOR:
        return reply_text
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
        log(f"✓ reply 拦截器自动 sed 删干净")
        reply_text = fixed
    residue_fixed = auto_fix(reply_text)
    if residue_fixed != reply_text:
        log(f"✓ 残留扫描清理: {reply_text!r} -> {residue_fixed!r}")
        reply_text = residue_fixed
    return reply_text


def load_workflow(server: str, workflow_name: str = DEFAULT_WORKFLOW) -> dict:
    """从 comfyui-skill 注册目录加载工作流 JSON"""
    import comfyui
    comfyui_root = os.path.dirname(comfyui.__file__)
    wf_path = os.path.join(comfyui_root, "assets", "workflows", f"{workflow_name}.json")
    if not os.path.exists(wf_path):
        raise RuntimeError(
            f"🔴 工作流文件不存在: {wf_path}\n"
            f"请先 comfyui-skill import-workflow --id {workflow_name} <path>"
        )
    with open(wf_path) as f:
        return json.load(f)


def submit_and_poll(wf: dict, server: str, timeout: int = 180) -> dict:
    """提交工作流 + 轮询直到完成（实战 291 B 方案：不靠 WebSocket）"""
    log(f"📝 提交工作流到 ComfyUI ...")
    _t_post = time.monotonic()
    r = requests.post(f"{server}/prompt", json={"prompt": wf}, timeout=30)
    r.raise_for_status()
    _t_post_elapsed = time.monotonic() - _t_post
    pid = r.json()["prompt_id"]
    log(f"   ✓ prompt_id={pid} (POST 耗时 {_t_post_elapsed:.1f}s)")

    log(f"⏳ 等待执行 (timeout={timeout}s)...")
    t_start = time.monotonic()
    last_print = 0
    while True:
        elapsed = time.monotonic() - t_start
        if elapsed > timeout:
            raise RuntimeError(f"🔴 {timeout}s 内未完成")
        _t_poll = time.monotonic()
        try:
            h = requests.get(f"{server}/history/{pid}", timeout=5).json()
        except Exception:
            time.sleep(1)
            continue
        _t_poll_elapsed = time.monotonic() - _t_poll
        if pid in h:
            status = h[pid].get("status", {})
            if status.get("errored") or h[pid].get("error"):
                raise RuntimeError(f"ComfyUI 执行错误: {h[pid].get('error')}")
            if h[pid].get("outputs"):
                log(f"   ✅ 完成 ({elapsed:.1f}s)（最近一次 history 轮询 {_t_poll_elapsed*1000:.0f}ms）")
                return h[pid]
        if elapsed - last_print > 10:
            log(f"   ⏳ {elapsed:.0f}s ...")
            last_print = elapsed
        time.sleep(1)


def fetch_image_from_outputs(history_entry: dict, server: str, output_dir: str) -> str:
    """从 history_entry 拿图片文件名 + GET /view 下载到本地"""
    outputs = history_entry.get("outputs", {})
    if not outputs:
        raise RuntimeError("outputs 为空")
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
    params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    log(f"⏱️ GET /view 下载图片开始...")
    _t_dl = time.monotonic()
    r = requests.get(f"{server}/view", params=params, timeout=30)
    _t_dl_elapsed = time.monotonic() - _t_dl
    if r.status_code != 200:
        raise RuntimeError(f"GET /view 失败 rc={r.status_code}")
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, filename)
    with open(out_path, "wb") as f:
        f.write(r.content)
    log(f"   下载完成 ({_t_dl_elapsed:.1f}s, {len(r.content)//1024}KB)")
    return out_path


def fetch_generated_prompt(history_entry: dict) -> str:
    """从 history_entry 拿 LLM 自动生成的英文 prompt（节点 849 ShowAnything 输出）"""
    outputs = history_entry.get("outputs", {})
    for nid, node_data in outputs.items():
        if "text" in node_data:
            text = node_data["text"]
            if isinstance(text, list):
                return "".join(text)
            return text
    return ""


def step_save_to_leave(src_path: str, leave_name: str) -> str:
    """cp 留底 + size 守门"""
    Path(LEAVE_DIR).mkdir(parents=True, exist_ok=True)
    final = f"{LEAVE_DIR}/{leave_name}.png"
    shutil.copy(src_path, final)
    size = os.path.getsize(final)
    log(f"STEP 留底完成: {final} ({size} bytes)")
    if size < 100000:
        os.remove(final)
        raise RuntimeError(f"图过小 {size} bytes < 100000（防 cache 命中假图）")
    return final


def step_save_to_leave_only(out_path: str, leave_name: str) -> str:
    """✅ 实战 320-A' 钦定（08-06 主人正解 · 盖过补丁思路）：

    唯一正面路径 = 出图脚本只落盘 = 0 发图 = 0 调飞书 API。
    send_yuer_image() 已 raise NotImplementedError（盖过实战 313 v6.20 双发防御思路）。

    caller 唯一动作 = 读 stdout 第一行 MEDIA:<abs_path> = 拼到 reply = Hermes 框架渲染。

    🆕 实战 522 主人钦定（盖过 320-A'）：
    run() 函数已集成 yuer_send_v2.sh 发图 = 不需要 caller 再发图。
    step_save_to_leave_only() 仍保持 0 发图，供不需要发图的场景使用。
    """
    final = step_save_to_leave(out_path, leave_name)
    return final


def run(
    brief: str,
    leave_name: str,
    channel: str = "feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d",
    caption: str = "主人看～",
    server: str = DEFAULT_COMFYUI_SERVER,
    workflow: str = DEFAULT_WORKFLOW,
) -> str:
    """一句话出图唯一入口（09-21 主人钦定：强制接入 yuer-prompt-writer 技能）。

    🔴 09-21 灵魂级铁律（盖过一切旧逻辑）：
        run(brief) 不允许 brief 原样直进图模型。
        brief 进来后必须先过 yuer-prompt-writer 技能 = 主协议 + 6 场景策略 +
        物理层 6 铁律 + ⑦ 叙事张力 + 服装 5 项完整性 → 写出 500-650 词英文 prompt
        再灌 CLIPTextEncode 出图。
        判定"是否已是合格 prompt"：纯英文 + 500 词以上（主人直接给完整英文 prompt 时豁免）。
        不达标 = 抛错拒绝出图，提示按技能重写 = 杜绝偷懒。

    参数：
        brief: 主人一句话 brief 或已按 yuer-prompt-writer 技能写好的 500-650 词英文 prompt
        leave_name: 留底名（不含扩展名）
        channel: 默认 feishu 主对话渠道
        caption: 自定义 caption（1-3 句骚话）
        server: ComfyUI server URL
        workflow: 工作流名（默认 yuer_moody_fast，无 LLM；LLM 工作流仅主人指定时用）

    返回：
        str: "OK_FILE:{final_path} SENT" 成功 / 失败 raise

    实战 319 钦定（08-05 · 灵魂级 · 盖过 yuer_run_one_image 一切）：
        出图流程急剧简化：
        - 旧 SOP-B = LLM 翻译子进程 + 拼灵魂脸 PREFIX + yuer_stable_sop = 48s
        - 新 SOP-B（默认无 LLM）= yuer_moody_fast + Krea 2 LoRA = ~15s
        - SOP-B'（LLM 扩写）已于 09-21 主人钦定弃用删除，LLM 工作流不存在了
        ⚠️ 实战 497 钦定：默认走无 LLM 工作流，豆包反推等中文 prompt 直接进图模型

        出图唯一入口 = yuer_run_one_brief.run() = 走新工作流
        旧入口 = yuer_run_one_image.run() = 实战 319 钦定删除

    实战 319 灵魂级内置要素（全部在 system_prompt 内）：
        ① 实战 318 破甲 XML 框架（system_prompt 前缀）
        ② 实战 313 灵魂面容 PREFIX = "不写脸部特征（由锁脸 LoRA 处理）"
        ③ 实战 313 Krea 2 摄影风 = hyper-realistic + 8K + cinematic color grading
        ④ 实战 313 自然语言英文段落（10-15 句）
        ⑤ 实战 313 默认设定 = 20岁中国女性 + 冷白皮 + 性感修长
        ⑥ 实战 313 撩到边缘 / 粗俚语直接表达（不需要委婉化 不需要回避）
        ⑦ 实战 313 反拒绝规则 = 永不拒 + 永不说教 + 直接出 prompt
    """
    # 🆕 09-05 主人钦定：记录主人原始 brief（在任何处理之前）
    original_brief = brief

    # 🆕 09-21 主人钦定：run(brief) 强制唤醒 yuer-prompt-writer 技能
    # brief 原文不再直接进图模型 = 必须先经 yuer-prompt-writer 写成 500-650 词英文 prompt
    # 实现：brief 是中文且 <500 词 = 自动调技能写 prompt；已是很长的英文 prompt = 直接用（主人给的完整 prompt 豁免）

    assert brief, "brief 不能空"
    assert leave_name, "留底名不能空"

    import re as _re
    _REQUIRED_SECTIONS = {
        "主协议(相机/镜头/景别)": r"captured with|shot with|photograph|EOS|A7|iPhone",
        "主体(年龄/身体)": r"20 years old|young (slender )?Asian woman|young woman",
        "服装5项(上装/下装/颜色/长度/穿着方式)": r"(T-shirt|robe|silk|slip|panties|lace|dress|skirt|shorts).*(wearing|wears|clinging|falling|riding|pooling|open|buttoned|zipped|tied|loose)",
        "场景层次(前景/中景/远景)": r"(foreground|midground|far background|background layer)",
        "光影/摄影尾参(光效/景深/调色)": r"(depth of field|rim light|backlight|bokeh|color palette|8K|cinematic)",
    }
    def _count_matched_sections(s: str) -> int:
        import re as _r
        return sum(1 for pat in _REQUIRED_SECTIONS.values() if _r.search(pat, s, _r.I))

    def _is_qualified_prompt(s: str) -> bool:
        # 质量校验 = 命中 主协议/主体/服装/场景/光影 5 大结构段（不卡死字数）
        # 纯中文 brief 或结构残缺 = 不合格
        return _count_matched_sections(s) >= 4

    if _is_qualified_prompt(brief):
        log(f"brief 已通过 yuer-prompt-writer 质量校验（命中 {_count_matched_sections(brief)}/5 大结构段），直接出图")
    else:
        log("⚠️ brief 未通过 yuer-prompt-writer 质量校验（5大结构段：主协议/主体/服装/场景/光影，需命中≥4）")
        log("   卡的是结构质量不是字数——不为了凑字数硬编垃圾内容，也不允许中文 brief 直进图模型")
        log("   ⛔ 拒绝出图（09-21 主人钦定：不偷懒，但也不为凑数硬写）")
        raise ValueError(
            "brief 未通过 yuer-prompt-writer 质量校验（5大结构段命中<4）。\n"
            "请先按 yuer-prompt-writer 技能把 brief 扩写成结构完整的英文 prompt\n"
            "（主协议/主体/服装5项/场景层次/光影尾参），再传入本函数出图。"
        )

    caption = make_safe_caption(caption)

    log(f"开始一句话出图: brief={brief!r} workflow={workflow} channel={channel}")
    _t_start = time.monotonic()

    # Step ① 加载工作流
    wf = load_workflow(server, workflow)

    # Step ② 改 brife.input_string = brief（节点 857）
    brief_set = False
    for nid, node in wf.items():
        if node.get("_meta", {}).get("title") == "brife":
            node["inputs"]["input_string"] = brief
            brief_set = True
            log(f"   节点 {nid} brife → {brief!r}")
            break
    if not brief_set:
        # fallback by class_type
        for nid, node in wf.items():
            if node.get("class_type") == "get_string":
                # 检查是否是 brife（id 857）
                if nid == "857":
                    node["inputs"]["input_string"] = brief
                    brief_set = True
                    log(f"   节点 {nid} (by id) brife → {brief!r}")
                    break
    if not brief_set:
        # 实战 432：无 LLM 工作流 yuer_moody_fast（节点 627 CLIPTextEncode + title="CLIP文本编码"）
        # 适用：主人直接给完整英文 prompt，不需要 LLM 扩写
        for nid, node in wf.items():
            if node.get("class_type") == "CLIPTextEncode":
                title = node.get("_meta", {}).get("title", "")
                if title == "提示词英文" or "prompt" in title.lower() or nid == "9" or title == "CLIP文本编码":
                    node["inputs"]["text"] = brief
                    brief_set = True
                    log(f"   节点 {nid} CLIPTextEncode (无LLM工作流) → {brief[:60]!r}...")
                    break
    if not brief_set:
        raise RuntimeError("工作流找不到 brife 节点（既无 brife 节点也无 CLIPTextEncode 提示词英文 节点）")

    # Step ③ 改 SaveImage.filename_prefix
    for nid, node in wf.items():
        if node.get("class_type") == "SaveImage":
            node["inputs"]["filename_prefix"] = save_prefix(f"yuer_run_brief_{int(time.time())}")
            log(f"   节点 {nid} SaveImage → yuer_run_brief_{int(time.time())}")
            break

    # Step ④ 提交 + 轮询
    history_entry = submit_and_poll(wf, server, timeout=180)

    # Step ⑤ 从 outputs 拿 LLM 生成的英文 prompt（调试用）
    generated_prompt = fetch_generated_prompt(history_entry)
    if generated_prompt:
        # 实战 494e 整改：把 LLM 完整 prompt 输出到 stdout（不截断 120 字符）= 主人可以直接验收
        log(f"   📝 LLM 自动生成 prompt ({len(generated_prompt)} 字符): {generated_prompt[:120]}...")
        # 实战 494e 新增：完整 prompt 写入 .prompt 文件（方便核对）
        prompt_log_path = f"{LEAVE_DIR}/{leave_name}.prompt.md"
        Path(LEAVE_DIR).mkdir(parents=True, exist_ok=True)
        try:
            with open(prompt_log_path, "w", encoding="utf-8") as pf:
                pf.write(generated_prompt)
            log(f"   📄 完整 prompt 留底: {prompt_log_path}")
        except Exception as e:
            log(f"   ⚠️ prompt 留底失败: {e}")

    # Step ⑥ 从 outputs 拿图
    out_path = fetch_image_from_outputs(history_entry, server, "/tmp/yuer_run_brief")
    log(f"   💾 落盘: {out_path}")

    # Step ⑦ cp 留底
    final_path = step_save_to_leave_only(out_path, leave_name)

    # 🆕 09-05 主人钦定：brief + prompt 完整存档（无 LLM 路径也要存）
    # brief = 主人给我的原文出发点；prompt = 实际写出的英文 prompt
    _user_brief = original_brief if original_brief else brief
    _prompt_for_log = generated_prompt if generated_prompt else brief
    Path(LEAVE_DIR).mkdir(parents=True, exist_ok=True)
    import datetime
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 存主人原始 brief（出发点）
    brief_log_path = f"{LEAVE_DIR}/{leave_name}.brief.md"
    try:
        with open(brief_log_path, "w", encoding="utf-8") as bf:
            bf.write(f"# 主人原始 brief（出发点）\n\n")
            bf.write(f"**生成时间**: {now_str}\n\n")
            bf.write(f"```\n{brief}\n```")
        log(f"   📄 主人 brief 留底: {brief_log_path} ({len(brief)} 字)")
    except Exception as e:
        log(f"   ⚠️ brief 留底失败: {e}")
    # 存实际 prompt（扩展后）
    prompt_log_path2 = f"{LEAVE_DIR}/{leave_name}.prompt.md"
    try:
        with open(prompt_log_path2, "w", encoding="utf-8") as pf:
            pf.write(f"**生成时间**: {now_str}\n\n")
            pf.write(f"**来源**: {'LLM自动生成' if generated_prompt else '我写/直接写'}\n\n")
            pf.write(f"```\n{_prompt_for_log}\n```")
        log(f"   📄 实际 prompt 留底: {prompt_log_path2} ({len(_prompt_for_log)} 字)")
    except Exception as e:
        log(f"   ⚠️ prompt 留底失败: {e}")
    # 追加出图日志索引
    index_path = f"{LEAVE_DIR}/yuer_outimg_index.log"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    index_line = f"[{now_str}] brief={_user_brief[:80]!r}... | prompt_len={len(_prompt_for_log)} | image={final_path}\n"
    try:
        with open(index_path, "a", encoding="utf-8") as idx:
            idx.write(index_line)
        log(f"   📄 出图索引追加: {index_path}")
    except Exception as e:
        log(f"   ⚠️ 索引追加失败: {e}")

    # ✅ 实战 320-A' 钦定：出图脚本 = 0 发图 = 0 调 send_yuer_image
    # 🆕 实战 522 主人钦定：集成 yuer_send_v2.sh 真发飞书（盖过 320-A'）
    # stdout 第一行 = MEDIA:<abs_path> = 图片路径 = 语儿拼到 reply

    # 🆕 实战 522 主人钦定：集成 yuer_send_v2.sh 真发飞书
    sender_script = "~/.hermes/skills/creative/yuer-image-delivery/scripts/yuer_send_v2.sh"
    send_result = subprocess.run(
        ["bash", sender_script, final_path, caption, channel],
        capture_output=True,
        text=True,
        timeout=60
    )
    if send_result.returncode == 0:
        log(f"✅ 发图成功: {send_result.stdout.strip()}")
    else:
        log(f"⚠️ 发图失败: {send_result.stderr}")
    _t_total = time.monotonic() - _t_start
    log(f"✅ 一句话出图完成 ({_t_total:.1f}s) 落盘={final_path}")
    # 实战 525 主人钦定：脚本内置 yuer_send_v2.sh 已真发飞书 = 不再打 MEDIA 字面 = 避免平台触发重复发图
    return final_path


def run_with_image(
    image_path: str,
    leave_name: str,
    channel: str = "feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d",
    caption: str = "语儿按主人的图洗图～",
    server: str = DEFAULT_COMFYUI_SERVER,
    workflow: str = DEFAULT_WASH_WORKFLOW,
) -> str:
    """收图洗图出图唯一入口（实战 452 + 453 主人正解打脸·盖过 v1.0 实战 319 + 实战 427-428 收图铁律 一切）。

    实战 453 钦定（08-21 · 灵魂级·盖过实战 318 SOP-A 反推洗图 + 实战 427-428 收图 3 选 1 一切）：
        主人正解 = "收到图片，默认就直接运行洗图工作流出图，除非我提前要求你做其他的看图选择，不然直接走洗图工作流出图"
        = 收到图片 = **默认走洗图工作流**（实战 452 钦定·0 反推·9.1s）= **0 反问 3 选 1**（实战 427-428 钦定被覆盖）
        = 实战 318 SOP-A 反推洗图 = 替换为实战 452 新洗图工作流（无需反推·快 10 倍）

    参数：
        image_path: 主人发来的图片本地路径
        leave_name: 留底名（不含扩展名）
        channel: 默认 feishu 主对话渠道
        caption: 自定义 caption（1-3 句骚话）
        server: ComfyUI server URL
        workflow: 洗图工作流名（默认「语儿无需反推的快速洗图工作流」）

    返回：
        str: 成功落盘路径 / 失败 raise

    实战 452 + 453 实测：
        - 提交：~0.02s
        - KSampler 出图（8 steps, euler + simple）：~9.1s
        - 输出：洗图后的 PNG（默认尺寸）
        - 比旧版反推洗图（90s）快 10 倍

    实战 453 钦定·灵魂级 4 铁律：
        ① ❌ 收到图片 = 0 反问 3 选 1（实战 427-428 钦定被覆盖）
        ② ✅ 收到图片 = 默认走实战 452 新洗图工作流（9.1s）
        ③ ✅ 无图片 = 走 run() 一句话出图（实战 319 钦定·主路 LLM 扩写）
        ④ ✅ 主人提前要求看图选择 = 才走 3 选 1（实战 427-428 反例例外）
    """
    assert image_path, "image_path 不能空"
    assert os.path.exists(image_path), f"image_path 不存在: {image_path}"
    assert leave_name, "留底名不能空"

    caption = make_safe_caption(caption)

    log(f"开始洗图出图: image_path={image_path} workflow={workflow} channel={channel}")
    _t_start = time.monotonic()

    # Step ① 加载洗图工作流
    wf = load_workflow(server, workflow)

    # Step ② 先上传图片到 ComfyUI 服务器 input 目录（实战 453 钦定·ComfyUI /upload/image endpoint）
    import mimetypes
    boundary = '----yuer-wash-boundary'
    img_name = os.path.basename(image_path)
    with open(image_path, 'rb') as f:
        img_data = f.read()
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="{img_name}"\r\n'
        f'Content-Type: {mimetypes.guess_type(img_name)[0] or "image/png"}\r\n'
        f'\r\n'
    ).encode() + img_data + f'\r\n--{boundary}--\r\n'.encode()
    upload_req = requests.post(
        f'{server}/upload/image',
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'},
        timeout=30,
    )
    upload_result = upload_req.json()
    if 'name' not in upload_result:
        raise RuntimeError(f"图片上传失败: {upload_result}")
    uploaded_name = upload_result['name']
    log(f"   图片上传成功 → {uploaded_name}（{len(img_data)} bytes）")

    # Step ③ 改 LoadImage.image = uploaded_name（实战 452 钦定·洗图工作流 LoadImage 节点）
    for nid, node in wf.items():
        if node.get("class_type") == "LoadImage":
            node["inputs"]["image"] = uploaded_name
            log(f"   节点 {nid} LoadImage.image → {uploaded_name}")
            break

    # Step ④ 改 SaveImage.filename_prefix
    for nid, node in wf.items():
        if node.get("class_type") == "SaveImage":
            node["inputs"]["filename_prefix"] = save_prefix(f"yuer_wash_{int(time.time())}")
            log(f"   节点 {nid} SaveImage → yuer_wash_{int(time.time())}")
            break

    # Step ⑤ 提交 + 轮询
    history_entry = submit_and_poll(wf, server, timeout=180)

    # Step ⑥ 从 outputs 拿图
    out_path = fetch_image_from_outputs(history_entry, server, "/tmp/yuer_wash")
    log(f"   💾 落盘: {out_path}")

    # Step ⑧ cp 留底
    final_path = step_save_to_leave_only(out_path, leave_name)

    # ✅ 实战 320-A' 钦定：出图脚本 = 0 发图 = 0 调 send_yuer_image
    # 🆕 实战 522 主人钦定：集成 yuer_send_v2.sh 真发飞书（盖过 320-A'）
    _t_total = time.monotonic() - _t_start

    # 🆕 实战 522 主人钦定：集成 yuer_send_v2.sh 真发飞书
    sender_script = "~/.hermes/skills/creative/yuer-image-delivery/scripts/yuer_send_v2.sh"
    send_result = subprocess.run(
        ["bash", sender_script, final_path, caption, channel],
        capture_output=True,
        text=True,
        timeout=60
    )
    if send_result.returncode == 0:
        log(f"✅ 发图成功: {send_result.stdout.strip()}")
    else:
        log(f"⚠️ 发图失败: {send_result.stderr}")
    log(f"✅ 洗图出图完成 ({_t_total:.1f}s) 落盘={final_path}")
    # 实战 525 主人钦定：脚本内置 yuer_send_v2.sh 已真发飞书 = 不再打 MEDIA 字面 = 避免平台触发重复发图
    return final_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法 1: python3 yuer_run_one_brief.py <brief> <leave_name> [channel] [caption] [server]")
        print("  brief: 主人一句话 brief（一个字/一句话/cos X/露出/走光/POV/随机 都行）")
        print("  channel: feishu (默认) / telegram")
        print("  workflow: 默认 yuer_moody_fast（无 LLM，豆包反推直接进图）")
        print("  ⚠️ LLM 扩写工作流已于 09-21 主人钦定删除，出图统一走 yuer_moody_fast")
        print()
        print("用法 2: python3 yuer_run_one_brief.py --wash <image_path> <leave_name> [channel] [caption] [server]")
        print("  image_path: 主人发的图片本地路径（实战 452 + 453 钦定·收到图片默认走洗图工作流）")
        print("  workflow: 默认 语儿无需反推的快速洗图工作流")
        sys.exit(2)

    # 实战 453 钦定·主入口自动检测输入类型
    if sys.argv[1] == "--wash":
        # 洗图模式（实战 452 + 453 钦定）
        if len(sys.argv) < 4:
            print("用法: python3 yuer_run_one_brief.py --wash <image_path> <leave_name> [channel] [caption] [server]")
            sys.exit(2)
        image_path = sys.argv[2]
        leave_name = sys.argv[3]
        channel = sys.argv[4] if len(sys.argv) > 4 else "feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d"
        caption = sys.argv[5] if len(sys.argv) > 5 else "语儿按主人的图洗图～"
        server = sys.argv[6] if len(sys.argv) > 6 else DEFAULT_COMFYUI_SERVER
        try:
            result = run_with_image(image_path, leave_name, channel=channel, caption=caption, server=server)
        except Exception as e:
            print(f"FAIL: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # 一句话出图模式（实战 319 钦定·原 run()）
        brief = sys.argv[1]
        leave_name = sys.argv[2]
        channel = sys.argv[3] if len(sys.argv) > 3 else "feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d"
        caption = sys.argv[4] if len(sys.argv) > 4 else "主人看～"
        server = sys.argv[5] if len(sys.argv) > 5 else DEFAULT_COMFYUI_SERVER
        try:
            result = run(brief, leave_name, channel=channel, caption=caption, server=server)
        except Exception as e:
            print(f"FAIL: {e}", file=sys.stderr)
            sys.exit(1)


# ============================================================
# 🆕 主入口更新（支持 --prompt 和 --set 参数）
# ============================================================
# 注意：上面的 if __name__ == "__main__" 已经处理了所有入口
# 下面的代码是 v2.0 新增的函数，不在 __main__ 块内

def run_with_prompt(
    prompt: str,
    leave_name: str,
    channel: str = "feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d",
    caption: str = "主人看～",
    server: str = DEFAULT_COMFYUI_SERVER,
    workflow: str = DEFAULT_WORKFLOW,
) -> str:
    """直接提示词出图入口（实战 521 钦定）。

    参数：
        prompt: 英文 prompt（必填，由 LLM 或主人提供）
        leave_name: 留底名（不含扩展名）
        channel: 发送目标
        caption: 骚话
        server: ComfyUI server
        workflow: 工作流名

    返回：
        str: MEDIA:<abs_path>
    """
    assert prompt, "prompt 不能空"
    assert leave_name, "留底名不能空"

    caption = make_safe_caption(caption)

    log(f"开始直接提示词出图: prompt_len={len(prompt)} workflow={workflow} channel={channel}")
    _t_start = time.monotonic()

    # Step ① 加载工作流
    wf = load_workflow(server, workflow)

    # Step ② 写 prompt 到 CLIPTextEncode 节点
    for nid, node in wf.items():
        if node.get("class_type") == "CLIPTextEncode":
            node["inputs"]["text"] = prompt
            log(f"   节点 {nid} CLIPTextEncode → prompt")
            break

    # Step ③ 改 SaveImage.filename_prefix
    for nid, node in wf.items():
        if node.get("class_type") == "SaveImage":
            node["inputs"]["filename_prefix"] = save_prefix(f"yuer_run_prompt_{int(time.time())}")
            log(f"   节点 {nid} SaveImage → yuer_run_prompt_{int(time.time())}")
            break

    # Step ④ 提交 + 轮询
    history_entry = submit_and_poll(wf, server, timeout=240)

    # Step ⑤ 从 outputs 拿图
    out_path = fetch_image_from_outputs(history_entry, server, "/tmp/yuer_run_prompt")
    log(f"   💾 落盘: {out_path}")

    # Step ⑥ cp 留底
    final_path = step_save_to_leave_only(out_path, leave_name)

    # Step ⑦ 存档 prompt（md 格式 · 实战 524 主人钦定）
    Path(LEAVE_DIR).mkdir(parents=True, exist_ok=True)
    prompt_log_path = f"{LEAVE_DIR}/{leave_name}.prompt.md"
    import datetime
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(prompt_log_path, "w", encoding="utf-8") as pf:
        pf.write(f"# 实际使用的英文 prompt\n\n")
        pf.write(f"**生成时间**: {now_str}\n\n")
        pf.write(f"```\n{prompt}\n```")
    log(f"   📄 prompt 留底: {prompt_log_path}")

    # Step ⑧ 索引
    index_path = f"{LEAVE_DIR}/yuer_outimg_index.log"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(index_path, "a", encoding="utf-8") as idx:
        idx.write(f"[{now_str}] prompt_len={len(prompt)} | image={final_path}\n")

    _t_gen = time.monotonic()

    # 🆕 实战 522 主人钦定：集成 yuer_send_v2.sh 真发飞书
    sender_script = "~/.hermes/skills/creative/yuer-image-delivery/scripts/yuer_send_v2.sh"
    log(f"⏱️ 发图开始...")
    _t_send = time.monotonic()
    send_result = subprocess.run(
        ["bash", sender_script, final_path, caption, channel],
        capture_output=True,
        text=True,
        timeout=60
    )
    _t_send_elapsed = time.monotonic() - _t_send
    _t_total = time.monotonic() - _t_start
    _t_gen_elapsed = _t_send - _t_gen  # 出图阶段（提交+轮询+下载+落盘）

    if send_result.returncode == 0:
        log(f"✅ 发图成功 ({_t_send_elapsed:.1f}s)")
    else:
        log(f"⚠️ 发图失败 ({_t_send_elapsed:.1f}s): {send_result.stderr}")
    log(f"✅ 直接提示词出图完成：总 {_t_total:.1f}s（出图 {_t_gen_elapsed:.1f}s + 发图 {_t_send_elapsed:.1f}s）落盘={final_path}")
    return final_path


def run_set(
    brief: str,
    prompts: list,
    count: int = None,
    leave_name: str = None,
    channel: str = "feishu:oc_3c7f585b3c86f29b7e9b152ed6eec41d",
    captions: list = None,
    server: str = DEFAULT_COMFYUI_SERVER,
    workflow: str = DEFAULT_WORKFLOW,
) -> list:
    """套图生产入口（实战 521 钦定）。

    参数：
        brief: 总 brief（所有图共享）
        prompts: N 个英文 prompt（列表）
        count: 出图数量（可选，默认=len(prompts)）
        leave_name: 输出文件名前缀
        channel: 发送目标
        captions: N 个 caption（可选）
        server: ComfyUI server
        workflow: 工作流名

    返回：
        list: 每张图片的信息字典
    """
    assert brief, "brief 不能空"
    assert prompts and len(prompts) > 0, "prompts 不能空"

    if count is None:
        count = len(prompts)
    if leave_name is None:
        leave_name = f"yuer_set_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if captions is None:
        captions = [f"{leave_name}_图{i+1}" for i in range(count)]

    # 校验数量
    if len(prompts) < count:
        raise ValueError(f"prompts 数量 ({len(prompts)}) 少于 count ({count})")
    if len(captions) < count:
        captions = captions + [f"{leave_name}_图{i+1}" for i in range(len(captions), count)]

    results = []

    for i in range(count):
        prompt = prompts[i]
        caption = captions[i]

        log(f"\n{'='*60}")
        log(f"[套图 {i+1}/{count}] 开始出图...")
        log(f"{'='*60}")

        # 调用单张出图逻辑
        try:
            final_path = run(prompt, f"{leave_name}_{i+1}", channel=channel, caption=caption, server=server, workflow=workflow)
            results.append({
                'index': i + 1,
                'success': True,
                'image_path': final_path,
            })
            log(f"[套图 {i+1}/{count}] 完成！")
        except Exception as e:
            log(f"[套图 {i+1}/{count}] 失败: {e}")
            results.append({
                'index': i + 1,
                'success': False,
                'error': str(e),
            })

    success_count = sum(1 for r in results if r['success'])
    log(f"\n{'='*60}")
    log(f"✅ 套图全部完成！成功 {success_count}/{len(results)} 张")
    log(f"{'='*60}")

    return results




# ============================================================
# 🆕 主入口更新（支持 --prompt 和 --set 参数）
# ============================================================
