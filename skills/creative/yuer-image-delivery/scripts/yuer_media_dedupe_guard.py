#!/usr/bin/env python3
"""yuer_media_dedupe_guard · 出图交付双发守卫（物理机制层）

🔴 病根 = 两层发图通道同时对同一张图生效
────────────────────────────────────────────
出图链路（`yuer_ka_fast.sh` → `yuer_ka_pai_zhi_chu.py` → `feishu_send.py`）**内部已经
真发飞书** = 图 + caption 绑成一条气泡 = 主人手机里已经有这张图。

同一轮 reply 里再写一行 `MEDIA:/abs/path.png` → gateway 的 `extract_media()` 把它当
**第二次投递指令** → 再上传一遍 → 主人收 2 张。

🔴 为什么文档层的铁律修不掉
────────────────────────────────────────────
`yuer_reply_interceptor.py` 的 `enforce_clean_reply` 只在脚本内部管 caption 参数，
**管不到最终 chat reply 那段文本** = 半扇门 = 靠「我自己记得删」= 复发。

🔴 正解 = 框架层 `transform_llm_output`（最终 reply 落库/投递前改写它）
────────────────────────────────────────────
命中判据（窄到不误伤）：reply 里的 `MEDIA:<path>` 指向的文件**旁边有一个新鲜的
`.sent` 标记**（`<path>.sent` 或 `<stem>.sent`）= 刚被脚本真发过 = 平台再取一次就是重复
→ 剥掉这个标签。

`.sent` 用 30 分钟新鲜度窗口（`YUER_DEDUPE_WINDOW_SEC` 可覆盖）= 只认「这一轮刚发过」的
→ 主人隔天喊「再发一遍」时旧标记不新鲜 = 标签不剥 = 照常能重发。

🔴 剥的方式 = 按 span 删（不是正则替换成空串）
────────────────────────────────────────────
v1 用「正则替换成空串」踩了两个坑（自测抓出来的）：
  ① 贴在一起的标签 `MEDIA:a.pngMEDIA:b.png` 被合成一个 = 漏剥
  ② 清残渣那步把**没被剥**的标签的 `MEDIA:` 字样也吃掉 = 主人要的那张图彻底收不到
现在改成 = 用 gateway 同款正则定位 span → 只删命中「刚发过」的那些 span → 其余一个字不动。

🔴 标签识别 = 用 gateway 自己的 `MEDIA_TAG_CLEANUP_RE`（唯一真值）= 0 自己造第二套正则
（自己写的会跟 gateway 的锚点规则漂移 = 强调包裹 / 引号包裹 / 多段扩展名 / 中文标点收尾
全认不出 = 守卫漏放）。扫之前先走 gateway 的 `_mask_media_scan_text`（代码块/引号/JSON
字符串值 = 不是投递指令）= 守卫跟 gateway 判定一致。

🔴 只认 Python 插件 = 0 认 shell hook
────────────────────────────────────────────
`transform_llm_output` 的返回契约 = 「第一个非 None 的 **字符串**生效」。shell hook 的
stdout 只被解析成 dict（`_parse_response` → `_parse_context`）= 永远不是 str = 改不动 reply。

用法：
  ① 被 `~/.hermes/plugins/yuer-media-dedupe/__init__.py` 当插件模块加载（安装见
     `scripts/install_media_dedupe_guard.sh`）
  ② 单元自测 = 直接 import 本文件调 `_on_transform_llm_output()`
"""

from __future__ import annotations

import logging
import os
import re
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

# 🔴 惰性 import = 插件加载那一刻不把 gateway.platforms.base 拽进来 = 避开启动期循环 import
_GATEWAY = None
_GATEWAY_TRIED = False


def _gateway():
    """拿到 gateway 的正则 + 掩码工具 = 拿不到就 None（走兜底）"""
    global _GATEWAY, _GATEWAY_TRIED
    if not _GATEWAY_TRIED:
        _GATEWAY_TRIED = True
        try:  # pragma: no cover - 运行环境差异
            from gateway.platforms import base as _base

            _GATEWAY = _base
        except Exception:  # noqa: BLE001
            _GATEWAY = None
    return _GATEWAY


# 扩展名清单 = 跟 gateway 的 MEDIA_DELIVERY_EXTS 对齐 = 漏一个 = 那种格式就剥不掉 = 双发复生
_MEDIA_EXT = (
    # 图片
    "png|jpg|jpeg|gif|webp|bmp|tiff|svg"
    # 视频
    "|mp4|mov|avi|mkv|webm|3gp"
    # 音频
    "|mp3|m2a|wav|ogg|opus|m4a|flac"
    # 文档
    "|pdf|docx|doc|odt|rtf|txt|md|epub"
    # 表格 / 数据
    "|xlsx|xls|ods|csv|tsv|json|xml|yaml|yml"
    # 地理
    "|kmz|kml|geojson|gpx"
    # 其他常见交付格式
    "|zip|tar|gz|tgz|7z|rar|bz2|xz|apk|ipa|html|htm|log"
)

# 中文收尾标点 = 跟 gateway 的 _MEDIA_CJK_TERMINATORS 同源（缺了 = 「MEDIA:a.png（782 KB）」认不出）
_CJK_TERMINATORS = "（）〈〉《》：，。；！？、\u201c\u201d\u2018\u2019【】"

# 兜底正则 = 只在 gateway import 不到时用 = 形状照抄 gateway 的锚点规则
# 🔴 关键两点 = ① 路径非贪婪 + 收尾 lookahead 含 `MEDIA:` = 贴边标签不粘连
#              ② 前后的强调/引号标记 = 跟 gateway 一致 = 剥完不留残渣
_FALLBACK_TAG_RE = re.compile(
    r'''[`"'*_]{0,3}MEDIA:\s*'''
    r'''(?P<path>`[^`\n]+?`|"[^"\n]+?"|'[^'\n]+?'|'''
    r'''(?:~/|/|[A-Za-z]:[/\\])\S+?(?:[^\S\n]+\S+?)*?\.(?:''' + _MEDIA_EXT + r'''))'''
    r'''(?=[\s`"'*_,;:)\]}[''' + _CJK_TERMINATORS + r''']|MEDIA:|\.(?:\s|$)|$)'''
    r'''[`"'*_]{0,3}\.?''',
    re.IGNORECASE,
)

# 「刚发过」的判定窗口 = 30 分钟 = 覆盖「脚本发完 → 我这一轮写 reply」的间隔（含长回合）
# 🔴 可用环境变量 YUER_DEDUPE_WINDOW_SEC 覆盖 = 主人嫌短就调长
# 🔴 窗口的意义 = 旧图（主人隔天喊重发）不新鲜 = 不剥 = 照常重发 1 次 = 不会「重发变没发」
try:
    _FRESH_SECONDS = int(os.environ.get("YUER_DEDUPE_WINDOW_SEC", "1800"))
except (TypeError, ValueError):
    _FRESH_SECONDS = 1800


def _tag_re() -> "re.Pattern[str]":
    base = _gateway()
    if base is not None:
        return base.MEDIA_TAG_CLEANUP_RE
    return _FALLBACK_TAG_RE


def _normalize(path: str) -> str:
    """剥掉路径外的引号 / 反引号 = 再 expanduser + 绝对化"""
    raw = path.strip().strip("`\"'")
    try:
        return os.path.abspath(os.path.expanduser(raw))
    except (OSError, RuntimeError, ValueError):
        return raw


def _markers_for(path: str) -> list[str]:
    """.sent 标记的两种真值写法 = `<path>.sent` 与 `<stem>.sent`"""
    out = [path + ".sent"]
    stem = os.path.splitext(path)[0]
    if stem and stem != path:
        out.append(stem + ".sent")
    return out


def _just_sent(path: str, now: float) -> bool:
    """这个文件刚被脚本真发过吗（=.sent 标记存在且新鲜）"""
    for mark in _markers_for(path):
        try:
            mtime = os.path.getmtime(mark)
        except OSError:
            continue
        age = now - mtime
        if -5 <= age <= _FRESH_SECONDS:
            return True
    return False


def _delete_spans(text: str, spans: list) -> str:
    """按 span 删文本 = 跟 gateway 的 `_delete_spans` 同语义（合并重叠 + 倒序删）"""
    if not spans:
        return text
    merged: list = []
    for s, e in sorted(spans):
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    chars = list(text)
    for start, end in reversed(merged):
        del chars[start:end]
    return "".join(chars)


def _clean_reply(text: str) -> str:
    """剥掉「刚发过」的 MEDIA 标签 = 其余一个字不动"""
    now = time.time()
    base = _gateway()
    rx = _tag_re()

    # gateway 会先把代码块/引号/JSON 字符串值掩码掉再扫（那些位置的 MEDIA: 不是投递指令）
    # = 守卫必须跟它一样掩码 = 否则代码块里的 MEDIA: 被我剥掉 = 主人看到代码少一行
    scan = text
    if base is not None:
        try:
            scan = base._mask_media_scan_text(text)
        except Exception:  # noqa: BLE001
            scan = text

    drop: list = []
    for match in rx.finditer(scan):
        raw = match.group("path")
        if not raw:
            continue
        if _just_sent(_normalize(raw), now):
            drop.append(match.span())

    if not drop:
        return text

    out = _delete_spans(text, drop)
    # 剥掉标签后可能留下空行 = 收一收（不碰别的文字）
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    return out


def _on_transform_llm_output(response_text: str = "", **_: Any) -> Optional[str]:
    """transform_llm_output = 出 reply 之前的最后一道闸 = 返回改写后的文本（None = 不改）"""
    if not response_text or "MEDIA:" not in response_text:
        return None
    try:
        cleaned = _clean_reply(response_text)
    except Exception as exc:  # noqa: BLE001 = 守卫永远不把主人的 reply 弄坏
        logger.warning("yuer-media-dedupe: 去重守卫异常 = 放行原文本 (%s)", exc)
        return None
    if cleaned != response_text:
        logger.info("yuer-media-dedupe: 剥掉已发图的 MEDIA 标签 = 主人只收 1 张")
        return cleaned
    return None


def register(ctx) -> None:
    ctx.register_hook("transform_llm_output", _on_transform_llm_output)
