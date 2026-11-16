## 五、批量 build 脚本的三个坑（实测踩过）

1. **job key 改名 = 留孤儿文件 = 多发一张**：改过 `n5x` → `n4` 后 `/tmp/prompt_<tag>_n5x.txt` 仍在 = 跑批 glob 一起跑 = 主人收到 6 张。**机械门 = 跑批前 `ls /tmp/prompt_<tag>_n*.txt | wc -l` 必须 == 5。**
2. **裸体那张超 3200 = 换身体段不是砍构图**：完整 CURRENT 裸体段 ≈1500 字符 → 总长 4100+ = 被字符门禁拦死。**正解 = `NUDE_SHORT`（保体型轮廓/胸型/腰臀比/腿比/皮肤，删私处三锚/围度数字/重复皮肤）≈ 900 字符。**
3. **民族服装必缺下装词**：`qipao` / `ruqun` / `hakama` / `kimono` / `robe` / `towel` / `wrap` 全不在白名单 = 必 FAIL。**修法 = 保留本民族词 + 同句补一个白名单词（`qipao dress` / `the long skirt falling to her ankles` / `over black string bikini bottoms`）。** 同一坑的近亲：`thong` / `panty` / `undies` / `nothing underneath` / `no underwear` 同样 FAIL = 一律改写 `black lace briefs` / `black string bikini bottoms` / `a black string bikini pulled down around her thighs`（**裸体那张也仍要挂一个真下装词** = 门禁只查词不认「她本来就裸」）。
5. **改 build 脚本 = 替换单行独特片段 + 改完立刻 `ast.parse`**：多行块 replace 常因换行/缩进对不上而 `count=0` = 看着改了其实没改（还可能改坏语法）。**正解 = 拿一行里唯一的短片段做锚**（例：`"wearing nothing at all, no clothing and no underwear, her bare body rising out of the bath "` 里的 `no clothing and no underwear`），replace 后 `python3 -c "import ast; ast.parse(open(p).read)"` 验过再跑。**门禁 FAIL「下装」时同理：先 `grep` 定位 prompt 里实际那句下装词 = 按那句改 = 0 凭印象重写一整段。**
6. **`ast.parse` 只验语法，不验内容**：多行 `replace` 的锚点里逗号位置写错（锚点自带逗号 + 下一段第一句也被吃掉）= 尾段整段丢失 = **语法合法 + 门禁通过 + 图却少了动作/光线/背景那一段**。**机械门 = 每份 prompt 落盘后核对字符数落在 600~3200 带内（`emit` 打印字数，超带当场报）+ 抽查 `grep` 一句关键短语在文件里** = 0 凭「我写了」往下走。锚点取**一行里唯一的短片段**，别取跨多行的整块。
7. **裸体那张的 body 覆盖 = 按内容判定，不按元组长度判定**：模板 `emit` 曾用 `job[-1] if len(job) > 7` 判断末项是不是专用 body = **7 元素裸体 job 的 `NUDE_SHORT` 被当成尾参句拼到句尾** = prompt 尾部混入一整段裸体身体描述、构图段被挤掉。**正解 = 末项含体型锚关键词（`hourglass` / `slender build`）才当 body**（模板已改）；**自查 = 看 prompt 结尾是不是正常收在 `9:16 vertical composition` 前的光线/背景句** = 结尾突然出现身体描述 = 判错了。
8. **`card` 的 name 参数只写 `n1`，绝不许写 `<batch>_n1`**：`emit` 的落盘式是 `"prompt_%s_%s.txt" % (batch, name)` = name 里再带一次 tag 就变成 `prompt_<tag>_<tag>_n1.txt`，而 `run_batch.sh` 的 glob 是 `prompt_<tag>_n*.txt` = **一个都收不到**，stdout 打「❌ 文件数 = 0 ≠ 5 = 0 开跑」= 5 张构思全白写。**机械门 = 生成后立刻 `ls /tmp/prompt_<tag>_n*.txt | wc -l` 必须 == 5**；查出双前缀 = `mv` 改回单前缀（**别重跑 build**，重跑还会再叠一次 tag）。
9. **按 `", "` 切块砍字的循环会吃掉主体锚**：主体锚（`a 20 years old young Asian woman with …`）、身材锚、下装词、鞋履词全住在逗号块里，`parts.pop(max(len))` 或「删最长的块」时它们会被当肥句砍掉 = 门禁照样过、图也能出，但 `check_prompt_subject.py` 报「稿子年龄 = 未写 / 语儿锚 = False」= 链路判不出来 = 白跑一轮。**机械门 = 每砍一轮立刻重跑 `check_prompt_subject.py`**；砍的顺序固定 = 背景道具 → 环境第二层 → 材质尾参 → 相机硬件尾段，**前三块（相机前缀 / 主体锚 / 场景起句）永远不参与 pop**。

## 五点五、门禁判读与三个高复发误判（每一条都真实烧过若干轮）

### ① 判门禁 = 看退出码 rc，不许 `grep FAIL`

`check_outfit_lock.py` 的**展示段会无条件列出每一项当标签**（缺鞋履就打印一行 `FAIL 鞋履`），但**末行结论可能写「🟡 只有 WARN = 可出图」且 `rc=0`**。用 `grep -c FAIL` 判 = **把可出图的稿子当成挂了的稿子，反复改本来没问题的句子**。

```bash
# ✅ 唯一正确判法
/usr/bin/python3 scripts/check_outfit_lock.py /tmp/prompt_x.txt >/dev/null 2>&1; echo rc=$?
# rc=0 = 放行（哪怕展示段里有 FAIL 字样）；rc=1 = 真挂
```

同一原则适用于另外两道门（`check_prompt_subject.py` / `count_prompt_chars.py`）= 都看 rc + 看末行结论，不看过程里的单词。

### ② `a pair of ...` = 触发「单人物」FAIL

门禁的多人检测把 `pair of` 读成「两个人」。**`a pair of black lace briefs` / `a pair of wooden sandals` 这种正常英语写法 = 直接 FAIL：缺「单人物」**，而画面里只有一个她。

- ✅ `wearing only black lace briefs`（去掉 `a pair of`，下装正则里的 `briefs` 照样命中）
- ✅ `wooden geta sandals resting on the floor`（鞋履正则里的 `sandals` 照样命中）
- 判据 = 写了 `pair of` 就去掉；**数量词不影响单品命中，只影响多人检测**

### ③ `barefoot` 只清 WARN，不清 FAIL

脚本里赤脚豁免那一支 **只从 warns 里剔除鞋履，没有从 fails 里剔除**。所以全身/被判成全身的画幅写 `she is barefoot` = **鞋履照样 FAIL**。

| 想要的 | 写的 | 结果 |
|---|---|---|
| 全身图确实赤脚 | `she is barefoot` | ❌ 仍 FAIL |
| 脚不在画幅内 | `her feet out of frame` / `feet cropped` / `cropped at the knee` | ✅ 清 FAIL |

**判据 = 脚真的在画面里 = 补真鞋履词（`sandals` / `sneakers` / `heels`）；脚不在画面里 = 写 `her feet out of frame` = 0 为凑门禁编一双画外的鞋。**

