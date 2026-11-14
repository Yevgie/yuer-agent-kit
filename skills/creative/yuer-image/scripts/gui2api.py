#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔴🔴🔴 GUI 工作流 → API 工作流（prompt 格式）转换器
LTX-2.5 官方工作流 = GUI 格式（子图 + 大量 MarkdownNote）= 服务端不收 = 必须转

核心规则（ComfyUI 官方语义）：
  1. 节点 inputs 数组 = 按【输入槽顺序】= widgets（控件）先、links（连线）后
  2. widgets_values 数组按顺序填进 widgets 部分
  3. 连线（link）= [源节点ID, 源输出槽位]
  4. 子图（subgraph）要展平 = 其内部节点变成普通节点，外部连线穿透进去

用法：
  python3 gui2api.py <gui.json> -o <api.json>
"""
import json, sys, argparse, urllib.request, os

DEFAULT_SERVER = os.environ.get(
    "YUER_COMFYUI_SERVER", "http://192.168.x.x:8188")


def fetch_object_info(server):
    with urllib.request.urlopen(server + "/object_info", timeout=60) as r:
        return json.loads(r.read().decode())


def _split_io(info):
    """把 object_info 的 required/optional 拆成 (inputs, widgets) 两类"""
    req = info.get("input", {}).get("required", {}) or {}
    opt = info.get("input", {}).get("optional", {}) or {}
    return req, opt


def build_api(gui, object_info, only_nodes=None):
    """GUI -> API"""
    links = gui.get("links", [])
    # links 是数组（新版）或 dict（旧版）
    link_map = {}
    if isinstance(links, list):
        for lk in links:
            if isinstance(lk, list):
                # [id, origin_id, origin_slot, target_id, target_slot, type]
                link_map[lk[0]] = (lk[1], lk[2])
            elif isinstance(lk, dict):
                link_map[lk["id"]] = (lk.get("origin_id"), lk.get("origin_slot"))
    elif isinstance(links, dict):
        for lid, lk in links.items():
            link_map[int(lid)] = (lk.get("origin_id"), lk.get("origin_slot"))

    api = {}

    def walk(nodes, prefix="", ctx_links=None):
        """把一层节点写进 api。子图递归展开。"""
        ctx_links = ctx_links if ctx_links is not None else link_map
        for n in nodes:
            ntype = n.get("type")
            if ntype in ("MarkdownNote", "Note", "Reroute", "PrimitiveNode"):
                continue
            if ntype in object_info or _is_subgraph_id(ntype):
                pass
            else:
                continue

            if _is_subgraph_id(ntype):
                sg = _find_subgraph(gui, ntype)
                if sg:
                    walk(sg.get("nodes", []), prefix, ctx_links)
                continue

            _emit_node(api, n, object_info, ctx_links, prefix)

    def _emit_node(api, n, object_info, ctx_links, prefix):
        ntype = n.get("type")
        info = object_info.get(ntype)
        if not info:
            return
        req, opt = _split_io(info)
        widget_defs = []
        link_defs = []
        for group in (req, opt):
            for name, spec in group.items():
                t = spec[0] if isinstance(spec, list) and spec else spec
                if isinstance(t, list):
                    t = t[0]
                # 判定是 widget 还是 link
                if isinstance(spec, list) and len(spec) > 1 and isinstance(spec[1], dict):
                    link_defs.append(name)
                else:
                    widget_defs.append(name)

        wv = n.get("widgets_values") or []
        inputs = {}
        wi = 0
        # 1) widgets
        for name in widget_defs:
            if wi < len(wv):
                inputs[name] = wv[wi]
                wi += 1
        # 2) links（节点 inputs 数组里带 link 的）
        for inp in n.get("inputs", []) or []:
            lid = inp.get("link")
            if lid is None:
                continue
            src = ctx_links.get(lid)
            if not src:
                continue
            inputs[inp.get("name")] = [str(src[0]), int(src[1])]

        nid = str(n.get("id"))
        if only_nodes and nid not in only_nodes:
            return
        api[nid] = {
            "class_type": ntype,
            "inputs": inputs,
            "_meta": {"title": n.get("_meta", {}).get("title", "") or
                      n.get("title", "") or ntype},
        }
        if n.get("mode") == 4:  # bypass
            api[nid]["_meta"]["bypass"] = True

    walk(gui.get("nodes", []))
    return api


def _is_subgraph_id(t):
    return isinstance(t, str) and len(t) == 36 and t.count("-") == 4


def _find_subgraph(gui, sid):
    for s in gui.get("definitions", {}).get("subgraphs", []):
        if s.get("id") == sid:
            return s
    return None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("gui")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--server", default=DEFAULT_SERVER)
    a = ap.parse_args()

    gui = json.load(open(a.gui, encoding="utf-8"))
    oi = fetch_object_info(a.server)
    api = build_api(gui, oi)
    json.dump(api, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✅ 转换完成 = {len(api)} 个节点 -> {a.out}")
