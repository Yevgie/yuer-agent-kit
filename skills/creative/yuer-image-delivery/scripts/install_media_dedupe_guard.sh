#!/usr/bin/env bash
# install_media_dedupe_guard.sh · 把出图双发守卫装成 Hermes 用户插件 + 启用
#
# 用法：bash scripts/install_media_dedupe_guard.sh
#
# 原理：
#   守卫本体 = 本技能 scripts/yuer_media_dedupe_guard.py（唯一真值，不拷第二份）
#   插件壳   = ~/.hermes/plugins/yuer-media-dedupe/__init__.py（import 本体 + register(ctx)）
#   启用     = plugins.enabled 里加 key + gateway 重新发现插件
#
# 🔴 为什么必须挂 transform_llm_output 而不是 shell hook：
#   transform_llm_output 的契约 = 「第一个非 None 的字符串生效」；shell hook 的 stdout
#   只被解析成 dict = 改不动 reply = 守卫等于没装。
set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GUARD_SRC="$SKILL_DIR/scripts/yuer_media_dedupe_guard.py"
PLUGIN_DIR="$HOME/.hermes/plugins/yuer-media-dedupe"
PLUGIN_KEY="yuer-media-dedupe"

[ -f "$GUARD_SRC" ] || { echo "ERR: 找不到守卫本体 $GUARD_SRC" >&2; exit 2; }
mkdir -p "$PLUGIN_DIR"

# ── plugin.yaml ──
cat > "$PLUGIN_DIR/plugin.yaml" <<'YAML'
name: yuer-media-dedupe
version: "1.0.0"
description: "出图交付双发守卫 = 脚本已真发飞书的图（旁边有新鲜 .sent 标记）= reply 里再写 MEDIA: 会被自动剥离 = 主人只收 1 张。"
author: "yuer (语儿)"
provides_hooks:
  - transform_llm_output
YAML

# ── __init__.py = import 本体（不拷第二份逻辑）──
cat > "$PLUGIN_DIR/__init__.py" <<'PY'
"""yuer-media-dedupe · 插件壳 = 逻辑真值在技能档 scripts/yuer_media_dedupe_guard.py

壳只做两件事：找到本体 + register(ctx)。
本体路径变了 = 改这一行 = 0 改逻辑。
"""
import importlib.util
import os

_SRC = os.path.expanduser(
    "~/.hermes/skills/creative/yuer-image-delivery/scripts/yuer_media_dedupe_guard.py"
)

_spec = importlib.util.spec_from_file_location("yuer_media_dedupe_guard", _SRC)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def register(ctx) -> None:
    _mod.register(ctx)
PY

echo "✅ 插件壳已写：$PLUGIN_DIR"

# ── 启用 = 写 config.yaml plugins.enabled + 让 gateway 重新发现 ──
if command -v hermes >/dev/null 2>&1; then
  hermes plugins enable "$PLUGIN_KEY" 2>&1 | tail -5
else
  echo "WARN: 找不到 hermes 命令 = 手动把 $PLUGIN_KEY 加进 ~/.hermes/config.yaml 的 plugins.enabled"
fi

# ── 强制 gateway 重新发现 = 插件体改了代码也要立刻生效（enable 已启用时不会再触发重载）──
if [ -x /usr/local/lib/hermes-agent/venv/bin/python ]; then
  /usr/local/lib/hermes-agent/venv/bin/python - <<'PY' 2>&1 | tail -3
import sys
sys.path.insert(0, "/usr/local/lib/hermes-agent")
from pathlib import Path
from gateway.control_socket import reload_gateway_plugins
r = reload_gateway_plugins(Path.home() / ".hermes", timeout=30.0) or {}
print("gateway reload-plugins →", "reloaded" if r.get("reloaded") else "没连上（稍后自然生效）")
PY
fi

# ── 自检 = 插件在不在列表里 + 状态是不是 enabled ──
if command -v hermes >/dev/null 2>&1; then
  hermes plugins list --plain --no-bundled 2>&1 | grep -i "$PLUGIN_KEY" || true
fi

echo ""
echo "验收：出图后看 gateway.log —— 同一文件应该有 0 条 'Sending image'"
echo "  （脚本那路直打飞书 Open API 不经过 gateway = 查不到 = 0 条 = 只发了一路）"
echo "  grep 'Sending image' ~/.hermes/logs/gateway.log | tail -5"
