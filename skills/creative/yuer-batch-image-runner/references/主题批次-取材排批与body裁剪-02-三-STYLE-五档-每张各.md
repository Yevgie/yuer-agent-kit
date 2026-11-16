## 三 · STYLE 五档 = 每张各占一档（相机前缀 + 调色尾参成对换）

**只换相机前缀 = 没换风格** = 五个参数一起换（光基调 + 情绪 + 景别 + 相机前缀 + 调色尾参）。

```python
STYLE = {
 "ins":    ("shot on an iPhone 15 Pro Max 1x lens at f/1.8, ", ", natural daylight color science, true-to-life skin tones, sharp micro contrast"),
 "cine":   ("A cinematic still captured with a Sony A7S III and 24mm f/1.4 GM lens at f/2.0, ", ", teal and amber color grade, volumetric haze, anamorphic soft falloff"),
 "doc":    ("A documentary photograph captured with a Canon EOS R5 and 50mm f/1.2 USM lens at f/1.8, ", ", warm tungsten white balance, visible film grain, honest unretouched skin texture"),
 "fashion":("An editorial fashion photograph captured with a Hasselblad X2D and 90mm f/2.5 lens at f/2.8, ", ", high fashion color grading, sculpted lighting, immaculate studio finish"),
 "ancient":("A cinematic photograph captured with a Hasselblad 500C with a Planar 80mm f/2.8 lens at f/2.8, ", ", warm amber tungsten glow, deep chiaroscuro, muted earth tones, soft bloom"),
}
```

**🔴 落笔时 STYLE 的前缀插在**句首**、尾参接在**句尾**= 中间那段才是画面本体 = 写 build 脚本时用 `.format(...)` 分三段拼，别把 STYLE 当一整句。

---

## 四 · body 段 = 从落盘 CURRENT 读 + **逐张裁**

**0 手抄身体段 = 与身材档漂移**。真值三个文件：

| 文件 | 用在哪 |
|---|---|
| `2026-10-28_bodyblock_covered_CURRENT.txt` | 穿着图（胸只写布下形状）|
| `2026-10-28_bodyblock_nude_CURRENT.txt` | 全身裸体 |
| `2026-10-28_bodyblock_nude_half_CURRENT.txt` | 半身裸体 |

**🔴🔴 裁剪必须按【每张画幅】单独决定 = 全批一刀切 = 白丢锚点**：
- 画幅到胯 / 到腰 / 半身 = 私处锚（`her pubic mound ... vertical seam` 整段）在画幅外 = **删** = 底模才 0 把画外的私处画进画面边缘
- 画幅全身 = 私处锚在画幅内 = **留着**

**判据 = 那一句在「描述身体」还是在「描述画框边界」** —— 按 `body == NUDE` 循环一刀切 = 全身那张也删了 = 白丢锚点。

**落地 = 先切两个具名变量，再让 job 各挑一个**（不是留一个 `NUDE` 到出图时按条件 strip —— 条件 strip 就是上面说的全批一刀切）：

```python
PRIV = "her pubic mound is smooth and bare with no pubic hair at all, the inner labia small and pink and tightly closed into a neat vertical seam"
NUDE_FULL = NUDE                                   # 全身 = 私处锚在画幅内 = 原样留着
NUDE_HALF = NUDE.replace(PRIV, "")                 # 半身/到胯/到腰 = 私处锚在画幅外 = 整段删
NUDE_SWIM = NUDE.replace(PRIV, "")                 # 泳装/湿身 = 同上

JOBS = [
  dict(name="n1", style="ins",  body=COVERED,   cap="..."),
  dict(name="n2", style="cine", body=NUDE_SWIM, cap="..."),   # 泳装 = 私处锚删掉
  dict(name="n3", style="doc",  body=NUDE_HALF, cap="..."),   # 半身 = 私处锚删掉
  dict(name="n4", style="fashion", body=COVERED, cap="..."),
  dict(name="n5", style="ancient", body=NUDE_FULL, cap="..."),# 全身裸 = 私处锚留着
]
```

**判据 = 变量名必须带画幅（FULL / HALF / SWIM）= 一眼看出这张该不该有私处锚**；写成 `NUDE` 一个变量 = 后面必然有人补一句 `if body == NUDE: body = body.replace(...)` = 又回到一刀切。

---

## 五 · caption 同源生成 = 0 手抄

```python
# job 里带 cap 字段 → 落盘时导出 captions.json
json.dump(caps, open(os.path.join(OUT, "captions.json"), "w"), ensure_ascii=False, indent=1)
```

出图时取出来传 `--caption`：

```bash
python3 -c "import json;print(json.load(open('/tmp/<批次>/captions.json'))['n1'])"
```

**🔴 池句在批量里 0 用**：`pick_saohua_reply.py` 出的是第三人称「语儿…」= 视角断裂 = 5 条 caption 全自己写。

---

## 六 · 三段式跑法（0 边跑边修）

```
1. N 段 prompt 全部落盘（/tmp/<批次>/n1.txt … nN.txt）
2. N 段全部过门禁（count_prompt_chars + check_prompt_subject + check_outfit_lock）
   = 判过不过看 EXIT CODE（0 = 过），不看 grep FAIL
3. N 张串行跑（每张一个 leave_name = 一次真发）
4. 跑完核对 N 个落盘 png 都存在 + N 个 ✅ 图已真发
```

**🔴 每张 leave_name = `<批次前缀>_<序号>_<场景词>_<日期>` = 跑完一次 glob 就核完**：`ls /path/to/media/<批次前缀>*.png | wc -l` = N 才算齐。批次前缀不带 = 核对要逐个敲文件名 = 漏一张看不出来（也接不上下一批「不撞场景」的排查）。

**🔴 为什么第 2 步不能省**：边跑边修 = 修到第 3 张才发现超长 = 前面 2 张已经白发给主人。

**🔴 串行跑 = 0 并发**（`.sent` 守卫 + 落盘覆盖 = 并发 = 双发 / 互相覆盖）。

---

## 七 · 收尾

- **每张 caption 各自不同** = 写这张画面正在发生的事
- **收尾报下一批主题 = 报 whereami 的 `下一项`** = 主人看着像「我接下来真要干的」
- **0 报张数 / 0 报耗时 / 0 报我排了什么** = 那是把施工图甩给主人

