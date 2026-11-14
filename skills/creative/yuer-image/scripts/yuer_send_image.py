#!/usr/bin/env python3
"""
yuer_send_image.py · 出图链路唯一交付物 (实战 320-A' 方案 · 08-06 主人正解 · 盖过补丁思路)

唯一职责变更(08-06 实战 320 · 主人正解「正向唯一原则」):
- ❌ 旧: send_yuer_image() = upload + send 一步走完 = 0 路径 = 主人体感双发 bug
- ✅ 新: send_yuer_image() = 顶层 raise NotImplementedError = 0 任何 caller 调 = 0 发图
- ✅ 唯一正面路径 = 出图脚本只落盘 + stdout 输出 MEDIA:路径 = caller 自己把 MEDIA: 塞到 reply
- ✅ Hermes 框架渲染 MEDIA: 行为 = 平台唯一投递通道 = 物理层不可能双发

正面约束(实战 320-A' 钦定·盖过补丁思路·盖过实战 313 v6.20 双发防御思路):
- ✅ 出图脚本 = 0 发图 = 0 调飞书 API = 0 upload + 0 send
- ✅ send_yuer_image() 顶层 raise = 任何 caller 试图调 = 立刻报错 = 我无法凭印象行动
- ✅ v6.20 物理防御保留 = caption 含 MEDIA: 字面 = 立即 raise (双发触发器拦截)

物理防御(实战 165 钦定·盖过行为约束):
- ✅ caption 含 MEDIA: 字面 = 立即 raise
- ✅ caption 含 /vol2/ 路径 = 立即 raise
"""
import sys
import os
import asyncio
import io as _io
import json
from pathlib import Path

# 添加 hermes-agent 库路径
HERMES_LIB = "/usr/local/lib/hermes-agent"
if HERMES_LIB not in sys.path:
    sys.path.insert(0, HERMES_LIB)
if os.path.exists(f"{HERMES_LIB}/venv/lib/python3.11/site-packages"):
    if f"{HERMES_LIB}/venv/lib/python3.11/site-packages" not in sys.path:
        sys.path.insert(0, f"{HERMES_LIB}/venv/lib/python3.11/site-packages")


def _load_hermes_env() -> None:
    """从 ~/.hermes/.env 加载 FEISHU_APP_ID / FEISHU_APP_SECRET 等"""
    try:
        from dotenv import load_dotenv
    except Exception:
        load_dotenv = None

    env_path = Path("~/.hermes") / ".env"
    if load_dotenv and env_path.exists():
        try:
            load_dotenv(str(env_path), override=True, encoding="utf-8")
        except UnicodeDecodeError:
            try:
                load_dotenv(str(env_path), override=True, encoding="latin-1")
            except Exception:
                pass
        except Exception:
            pass


def send_yuer_image(image_path: str, caption: str, chat_id: str = "oc_3c7f585b3c86f29b7e9b152ed6eec41d") -> bool:
    """
    ✅ 实战 320-A' 钦定（08-06 主人正解 · 盖过补丁思路）：

    唯一正面路径 = 出图脚本只落盘 + stdout 输出 MEDIA:路径 = 0 发图。
    send_yuer_image() 顶层 raise = 0 任何 caller 调发图 API。
    Hermes 框架渲染 MEDIA: 行为 = 平台唯一投递通道 = 物理层不可能双发。

    反模式硬表(实战 320-A' 钦定·盖过一切):
    - ❌ 调 send_yuer_image() 试图发图 = 立刻 raise = 0 行动
    - ❌ 调 hermes send CLI 试图发图 = 已知 1 文字 + 1 图 = 双发
    - ❌ 调 yuer_stable_sop/yuer_run_one_brief 等脚本尝试发图 = 0 行为
    - ✅ 唯一正确 = caller 读 stdout 第一行 MEDIA:路径 = 拼到 reply = 平台渲染

    v6.20 物理防御保留(实战 313 钦定):
    - ✅ caption 含 MEDIA: 字面 = 立即 raise
    - ✅ caption 含 /vol2/ 路径 = 立即 raise
    """
    # ✅ 实战 320-A' 钦定顶层 raise（盖过一切补丁思路）
    raise NotImplementedError(
        "send_yuer_image() 已被 08-06 实战 320-A' 方案钦定删除（盖过实战 313 v6.20 双发防御思路）\n"
        "正面约束: 出图脚本 = 0 发图 = 0 调飞书 API\n"
        "唯一正面路径: caller 读 stdout 第一行 MEDIA:<abs_path> = 拼到 reply = Hermes 框架渲染\n"
        f"当前调用参数 image_path={image_path} caption={caption[:30]!r} chat_id={chat_id}\n"
        "请立刻停止调用本函数,改用 stdout MEDIA: 路径"
    )
    if not os.path.exists(image_path):
        print(f"[yuer_send_image] ❌ 图不存在: {image_path}", file=sys.stderr)
        return False

    # 物理防御: caption 必 0 MEDIA 字面 = 否则 raise (实战 165 钦定)
    if "MEDIA:" in caption:
        raise RuntimeError(
            f"[yuer_send_image] ❌ caption 含 MEDIA: 字面 = 双发触发器 = 拒绝发送\n"
            f"caption: {caption!r}\n"
            f"正面约束: caption = 1-3 句骚话,0 任何 MEDIA:/vol2/.png 字面"
        )
    if "/vol2/" in caption:
        raise RuntimeError(
            f"[yuer_send_image] ❌ caption 含 /vol2/ 路径 = 双发触发器 = 拒绝发送\n"
            f"caption: {caption!r}\n"
            f"正面约束: caption = 1-3 句骚话,0 任何 MEDIA:/vol2/.png 字面"
        )

    # 加载 feishu env (FEISHU_APP_ID + FEISHU_APP_SECRET)
    _load_hermes_env()

    app_id = os.environ.get("FEISHU_APP_ID", "").strip()
    app_secret = os.environ.get("FEISHU_APP_SECRET", "").strip()

    if not app_id or not app_secret:
        print(f"[yuer_send_image] ❌ FEISHU_APP_ID 或 FEISHU_APP_SECRET 未设置", file=sys.stderr)
        return False

    async def _send():
        # 绕开 v0.20.0 损坏的 FeishuAdapter._build_lark_client(用 lark.Client, 但 SDK 改名 lark_oapi)
        # 直接用 lark_oapi.Client 构造 + 上传图 + 发 post 消息
        import lark_oapi as lark
        from lark_oapi.api.im.v1 import (
            CreateImageRequest, CreateImageRequestBody,
            CreateMessageRequest, CreateMessageRequestBody,
        )

        client = (
            lark.Client.builder()
            .app_id(app_id)
            .app_secret(app_secret)
            .domain("https://open.feishu.cn")
            .log_level(lark.LogLevel.WARNING)
            .build()
        )

        # 1. 上传图片
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        image_file = _io.BytesIO(image_bytes)
        image_file.name = os.path.basename(image_path)

        body = CreateImageRequestBody.builder() \
            .image_type("message") \
            .image(image_file) \
            .build()
        req = CreateImageRequest.builder().request_body(body).build()
        resp = await asyncio.to_thread(client.im.v1.image.create, req)

        if resp.code != 0:
            raise RuntimeError(f"upload failed: code={resp.code} msg={resp.msg}")

        image_key = resp.data.image_key

        # 2. 发 post 消息 (img + caption 合并成 1 条消息)
        content = {
            "zh_cn": {
                "title": "",
                "content": [
                    [{"tag": "img", "image_key": image_key}],
                    [{"tag": "text", "text": caption}],
                ],
            }
        }
        content_json = json.dumps(content, ensure_ascii=False)

        body = CreateMessageRequestBody.builder() \
            .receive_id(chat_id) \
            .msg_type("post") \
            .content(content_json) \
            .build()
        req = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(body) \
            .build()
        resp = await asyncio.to_thread(client.im.v1.message.create, req)

        if resp.code != 0:
            raise RuntimeError(f"send failed: code={resp.code} msg={resp.msg}")

        return True

    try:
        asyncio.run(_send())
        print(f"[yuer_send_image] ✅ 1 条 post 消息含 1 张图 caption={caption[:40]}... (0 双发,正面唯一路径)", file=sys.stderr)
        return True
    except Exception as e:
        print(f"[yuer_send_image] ❌ exception: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 yuer_send_image.py <image_path> <caption> [chat_id]", file=sys.stderr)
        sys.exit(2)
    image_path = sys.argv[1]
    caption = sys.argv[2]
    chat_id = sys.argv[3] if len(sys.argv) > 3 else "oc_3c7f585b3c86f29b7e9b152ed6eec41d"
    success = send_yuer_image(image_path, caption, chat_id)
    sys.exit(0 if success else 1)