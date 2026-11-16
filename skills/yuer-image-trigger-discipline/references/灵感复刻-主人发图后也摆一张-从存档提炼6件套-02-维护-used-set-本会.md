# 维护 used set = 本会话已用过的记录号（不跨会话持久化）
used = {"080", "019"}  # 本会话主人的图谱用过的号
cANDIDATES = [(n, t.strip) for n, t in records if n not in used]
chosen_num, chosen_theme = random.choice(candidates)
print(f"🎲 抽中: 记录 {chosen_num} · {chosen_theme}")
```

**踩坑**：`used` 只在本轮会话内存里维护，不跨会话持久化。fresh session 默认 used 为空 = 整个池都可能抽到（避免新会话立刻撞死几个号）。

**第 2 步 · 拉取该记录全文解析 6 维度**

```python
block_re = rf"---\n\n## 记录 {chosen_num} · {chosen_theme}[\s\S]*?(?=\n\n---|\Z)"
m = re.search(block_re, content)
if m:
    print(m.group(0))  # 拿到完整字段表
```

**关键字段必看**：场景、机位角度、姿势、服饰、光线、氛围、**🆕 角色外观**、**🆕 骚姿势标注** = 后两个双字段是借壳骚内核金标准的素材源。

**第 3 步 · 写新 prompt（必做姿势大变化 + 露馅走光金标准）**

**灵魂脸 PREFIX 必带**：每张图必须以 `a 20 years old young Asian woman with fair luminous translucent skin showing natural dewy glow...` 开头。

**借装策略**：用抽中记录的【角色外观】当语儿装扮（举牌 ≠ 写真装扮），配【骚姿势标注】做姿势基底。

**姿势大变化铁律**：跨记录号 = 必换姿势大类，绝不照搬。

| 原记录号姿势类 | 跨号后必换的姿势类 |
|---|---|
| 跪 / 趴 | → 站立 / 坐 / 靠墙 |
| 站立回眸 | → 背后偷看 / 钻进 / 单腿翘靠 |
| 坐 / 蹲 | → 躺 / 站起 / 反向坐 |
| 背影 | → 正面 / 侧脸 |
| 静态抓拍 | → 动态瞬间（风 / 滑 / 崩 / 跑）|

**露馅金标准 v1.3.0**：默认套用「风掀裙摆 / 弯腰衣领掉 / 浴巾滑 / 丝袜滑到腿根 / 板甲侧扣崩」之一 = 「撞见瞬间」> 主动脱光。

**第 4 步 · 端到端出图（用 pipx venv Python，** 不是 sandbox**）**

```python
import subprocess
PYTHON = "/usr/bin/python3"   # 🔴 10-03 改：系统 python（pipx venv 那份没人读）

# 写最小调用脚本通过 subprocess 传给 pipx venv python
runner_code = '''
import sys
sys.path.insert(0, "~/.hermes/skills/creative/yuer-image/scripts")
import yuer_run_one_brief as yrob
yrob.run_with_prompt(
    prompt=open(sys.argv[1]).read,
    leave_name=sys.argv[2],
    channel=sys.argv[4],
    caption=sys.argv[3],
    workflow="yuer_moody_fast",
    server="http://192.168.x.x:8188"
)
'''
with open("/tmp/yuer_runner_<topic>.py", "w") as f:
    f.write(runner_code)

proc = subprocess.run(
    [PYTHON, "/tmp/yuer_runner_<topic>.py",
     "/tmp/<topic>_prompt.txt", leave_name, caption, channel],
    capture_output=True, text=True, timeout=300
)
assert proc.returncode == 0
assert "✅ 发图成功" in proc.stdout
```

**踩坑（撞车复发沉淀）**：
- ❌ 用 sandbox `python3.11` 跑 = `ModuleNotFoundError: No module named 'comfyui'`
- ✅ 唯一正解 = `/usr/bin/python3` via subprocess（🔴 10-03 改，原写 pipx venv，但 PATH 上的 CLI shebang 是 `#!/usr/bin/python3`，那份根本没人执行）
- ❌ 在 sandbox `from yuer_run_one_brief import run_with_prompt` = 同上撞 ModuleNotFoundError

**第 5 步 · reply（v1.38 钦定）**

✅ 看到 exit 0 + `✅ 发图成功` 后 → 随机抽 1 句 100 条骚话库 → 只这一句 + 不可接 MEDIA 字面 + 不可接 .png/.jpg 扩展名 + 不可接留底路径。

### 反例硬表（新增）

| ❌ 错 | ✅ 对 |
|---|---|
| ❌ 主人说「继续」= 凭印象出上次同主题 = 撞撞撞 | ✅ random.choice 抽新记录号 = 跨号变题材变姿势 |
| ❌ 抽中 R19 后照样写「站立回眸」= 跟上次同姿势 | ✅ 跨号 = 必换姿势大类 = 站 → 坐 / 躺 / 钻 |
| ❌ 主人说「继续」= 语儿问「风格选哪个」 | ✅ 0 反问 = 语儿自己脑补抽 = 霸道主动 |
| ❌ sandbox 跑 yuer_run_one_brief = ModuleNotFoundError | ✅ pipx venv python subprocess |
| ❌ reply 带 MEDIA:/vol2/... = 双发 | ✅ reply 只 1 句随机骚话 |

## 关联技能

- `yuer-prompt-writer`（写英文 prompt 的 7 维度规则 · user-owned）
- `yuer-run-one-brief`（v1.33 回话模板 · user-owned）
- `yuer-image`（出图主路）
- `yuer-character-roster`（角色卡随机池 = 100 条抽签机制源头）
