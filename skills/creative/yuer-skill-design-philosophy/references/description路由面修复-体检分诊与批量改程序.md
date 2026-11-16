# description = 路由面 = 坏了 = 技能等于不存在

> **唯一职责 = 技能库体检时把「description 坏了」从「体积超标」里分出来 = 分诊 + 修 = 因为前者是**静默功能失效**（技能存在但永远不会被加载）= 比后者贵得多。**
> **主档指针 = `yuer-skill-design-philosophy` SKILL.md 第九部分。**

---

## 0 · 两类红灯 = 不是一类病

`skill_weight_gate.py` 报出来的红灯分两类，**处置完全不同**：

| 类 | 症状 | 后果 | 优先级 |
|---|---|---|---|
| **体积类** | 行数 / 字数 / 🔴 密度 / 版本号 / 考古行 | 加载成本高 = 慢 = 啰嗦 | 按主人排期慢慢砍 |
| **🔴 功能类** | **description 无触发词 / 句尾被截断 / Use when 重复两遍** | **技能在列表里 = 但主人说到那些词时永远不会被选中 = 静默失效** | **立刻修** |

**🔴 判据 = 静默 = 不报错 = 主人只会说「XX 怎么不干活」= 永远猜不到是 description 坏了 = 比体积问题更难被发现 = 体检时先查这类。**

---

## 1 · 诊断（机械）

```bash
# 红色线：已内置在 weight gate 的 desc_integrity 里 = 直接跑
G=~/.hermes/skills/creative/yuer-skill-design-philosophy/scripts/skill_weight_gate.py
python3 $G --all | grep -i description

# 自写扫描（要拿到具体清单时）= 只查自有技能 = bundled 技能用另一种 description 写法 = 不归我们改
python3 - <<'PY'
import os, re
R = os.path.expanduser("~/.hermes/skills")
for dp, dn, fn in os.walk(R):
    for f in fn:
        if f != "SKILL.md": continue
        p = os.path.join(dp, f); rel = p.replace(R + "/", "")
        if not (rel.startswith("yuer-") or "/yuer-" in rel): continue
        s = open(p, encoding="utf-8").read
        m = re.search(r"^---\n(.*?)\n---", s, re.S)
        if not m: continue
        d = re.search(r"description:\s*(.*?)(?=\n[a-z_]+:|\n---|\Z)", m.group(1), re.S)
        if not d: print("缺失  ", rel); continue
        v = d.group(1).strip
        if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]: v = v[1:-1]
        why = []
        if "Use when" not in v and not re.search(r"(触发词|触发|当主人|什么时候)", v): why.append("无触发词")
        if re.search(r"[（(、，/]$|[（(][^）)]*$", v): why.append("句尾截断")
        if len(re.findall(r"Use when[^。.]*", v)) > 1: why.append("Use when 重复")
        if why: print(f"{'+'.join(why):16s} {rel}")
PY
```

**🔴 三种坏法各自的成因**：
- **无触发词** = 批量压缩 description 时把「什么时候用」整段剪掉 = 只留了「是什么」= 技能有名字有职责 = 但没有一句能被匹配上
- **句尾截断** = 压缩时按字数砍 = 砍在半句上 = 读起来像乱码
- **Use when 重复两遍** = 压缩时把同一句贴了两遍

---

## 2 · 修法（🔴 触发词不许编）

**🔴 铁律 = 触发词必须从该档**自己正文**里已有的声明搬出来 = 0 自己编。**

**为什么**：编出来的触发词 = 可能把技能路由到不该路由的场景 = 修好了坏处又造了坏处。**每份技能正文里都已经写着它什么时候被触发**（触发场景行 / 唯一职责句 / frontmatter 里已有的 Use when）= 那是唯一可信的来源。

**取值优先级**（从准到不准）：
1. **frontmatter 里已有的 Use when** = 最短 = 直接用它
2. **正文里的「触发场景 / 什么时候用 / 何时用 / Use when」行** = 原文搬
3. **正文里第一句职责陈述** = 从里面抽触发名词
4. ❌ **0 自己想** = 编

**修完再做的减法**：description 里只剩「是什么」的版本 + 补一句 Use when = **同时删掉 description 里的版本考古**（`v3.4 实战307+308+309 盖过 v1.1` 这类）= 那是给人看的历史 = 不是给路由看的 = 删了既短又准。

---

## 3 · 批量修的安全程序（🔴 改 30 份 = 一次写坏 3 份）

**🔴 第一坑 = 正则偏移切 frontmatter**（改一份坏一份）：在 frontmatter **子串**上 `re.search` 拿 `d.start(1)` = 拿去切**全文** = 偏移基数不同 = 切出 `descripti` + 残留尾巴 = frontmatter 坏 = 技能加载不了。**正解 = 按行重建 frontmatter**（见 `creative/yuer-file-edit-safety` 铁律 ⑨）。

**🔴 第二坑 = 偏移切法会静默吃掉别的字段**：`version` / `author` / `license` / `metadata` 被一并切掉 = YAML 还能解析 = 看不出来 = 到下一轮写文件才炸。**验法 = 改完 frontmatter 里 `name` + `description` + 其余原有字段都在 = 才算没切坏。**

**🔴 第三坑 = 只验改过的那份**：批量 = 一份坏 = 那份技能加载不了 = 主人下次用到才发现。**验法 = 遍历全库 `yaml.safe_load` 每一份 frontmatter + 检查 `name` / `description` 都在 + 坏 0 份 = 才算完。**

**🔴 第四坑 = 改完忘了同步测试脚本的断言**：自测脚本可能断言了旧结构（比如「章节 5.3 在」= 那节已被合规删除）= 改完脚本必假失败 = 下一轮以为文件坏了。**判据 = 改结构 = 同步改断言 = 断言写新现实 = 不写「这节应该不存在」以外的软化版。**

**🔴 第五坑 = 顺手改 bundled 技能**：bundled 技能用另一种 description 写法 = 不是我们维护的 = 改了 = 下次技能更新被覆盖 = 白改。**判据 = rel 路径必须命中 `yuer-` 前缀 = 不命中 = 只报不动。**

---

## 4 · 完工判据

| # | 判据 |
|---|---|
| 1 | 功能类红灯 = **0**（description 类全清） |
| 2 | 全库 frontmatter `yaml.safe_load` = **0 报错** |
| 3 | 每份被改的 = `name` + `description` + 原有其余字段**都在** |
| 4 | 相关自测脚本 = **全绿**（断言同步改过） |
| 5 | 真跑一次真链路（出图 / 语音 / 抽卡）= 链路没坏 |
| 6 | 报告里列出**故意没动的**（体积类红灯 = 那是另一件事 = 要主人排期） |

**🔴 报告口径 = 分两类说**：功能类（已清零 = 修了 N 份）+ 体积类（还剩 M 份 = 没动 = 要不要排期）= 混成一句「已清理」= 主人以为全好了 = 下轮发现还是慢。
