"""语儿提示词资产池 · 路径唯一真值
🔴 11-09 22:20 主人钦定「提示词池 = 一条完整的英文自然语言提示词」
= 一行一条 `N|<整段英文>` = 0 字段 0 元信息 0 表格
= 旧 9 字段参考库已退役

所有读池子的脚本一律 import 这里 = 0 各写各的路径 = 0 漂
"""
import os

# 🔴 唯一资产池（NAS 上也有同内容副本，供主人直接看/改）
PROMPT_POOL = os.path.expanduser(
    "~/.hermes/skills/creative/yuer-image/references/提示词库-nsfw.txt"
)

# 🔴 11-09 23:15 提示词资产池 = 主人钦定两池（🔴 11-12 = 合并池文件已删 = 全量现算）
#    nsfw = NSFW 向（女主体，含男伴/男视角同框）41952 条
#    sfw  = 小红书 / ins 日常颜值博主向（含男女同框）2455 条
#    全量 = nsfw + sfw = 44407 条（🔴 11-12 = 合并池文件已删 = `--pool all` 读两池现算）
#    🔴 儿童、男性主体一律不保留（11-09 23:10 主人钦定）
PROMPT_POOL = os.path.expanduser(
    "~/.hermes/skills/creative/yuer-image/references/提示词库-nsfw.txt"
)
PROMPT_POOL_SFW = os.path.expanduser(
    "~/.hermes/skills/creative/yuer-image/references/提示词库-sfw.txt"
)
# 🔴 入库时写这个路径（存档 = 抽卡 = 同一条池 = 闭环）
PROMPT_POOL_WRITE = PROMPT_POOL

# 🔴 池登记表 = 两池（🔴 11-12 = 无合并池文件 = all = 读两池现算）
# 🔴 11-12 减法 = 合并池文件删了（50 MB 派生产物）= "all" = nsfw + sfw 现算
POOLS = {"nsfw": PROMPT_POOL, "sfw": PROMPT_POOL_SFW}
POOL_ALIASES = {
    "nsfw": "nsfw", "主": "nsfw", "main": "nsfw", "骚": "nsfw",
    "sfw": "sfw", "小红书": "sfw", "xhs": "sfw", "ins": "sfw", "日常": "sfw",
    "all": "all", "合并": "all", "全部": "all", "both": "all",
}


def pool_path(which="nsfw"):
    return POOLS[POOL_ALIASES.get(str(which).lower(), "nsfw")]

# 🔴 旧库路径 = 已退役 = 已删除（备份在 ~/.hermes/backups/prompt_pool_migration_20261109_2225/）


def read_pool():
    """返回 [(编号, 完整提示词)]。"""
    out = []
    with open(PROMPT_POOL, encoding="utf-8") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            if "|" not in ln:
                continue
            num, _, body = ln.partition("|")
            num = num.strip()
            body = body.strip()
            if num.isdigit() and body:
                out.append((num, body))
    return out


if __name__ == "__main__":
    rows = read_pool()
    print(f"池子 = {PROMPT_POOL}")
    print(f"条数 = {len(rows)}")
