### ② 门禁：**全批先过，再开跑**

边出边查 = 中途 FAIL = 已花掉的出图开销作废。

**🔴🔴 两条门禁口径不一样 —— 过了 `batch_gate_check.py` 不等于能跑**：
**🔴🔴 两条门禁口径不一样 —— 过了 `count_prompt_chars.py` 不等于能跑**：

| 门禁 | 字符上限 | 拦不拦 |
|---|---|---|
| `batch_gate_check.py` 单独跑 | 3200 软顶 | 报 FAIL 但经常放过 |
| `count_prompt_chars.py` 单独跑 | 3200 软顶 | 报 FAIL 但经常放过 |
| **`run_batch.sh` → `yuer_ka_fast.sh` 内部** | **🔴 11-07 起长度 0 阻断** | **超长不拦 = 整批照出** |

**🔴 11-07 起 = 长度 0 阻断** = 落盘前不用再为长度压字数 = 写完直接跑 = 真嫌长就删重复句。

**🔴 长度预算 = 主体锚 + 轻身体段 + 五段，目标 1100~1250**：
- 轻身体段（~250 字符）= 一条腿长锚 + 一条腰臀胸句。**把落盘的 COVER 身体段（~960 字符）直接拼进去 = 每张 2300+ = 必超**。
- 裁剪顺序 = 背景道具句 → 装饰性氛围句。**裁剪循环必须跳过前 3 个逗号块** = 主体锚（`a 20 years old young Asian woman`）在句首 = 按「删最长块」会先把主体锚删掉 → `check_prompt_subject.py` 立刻报「判不出来」。剪完必定再跑一次主体门禁。

```bash
cd <yuer-image>/scripts
for f in /tmp/<批次>/n*.txt; do
  printf "%s chars=%s " "$f" "$(python3 count_prompt_chars.py $f | grep -oE '[0-9]+' | head -1)"
  python3 check_prompt_subject.py $f >/dev/null; printf "sub=%s " $?
  python3 check_outfit_lock.py  $f >/dev/null; printf "outfit=%s\n" $?
done
```

**🔴 判过不过看 exit code（0 = 过），不看 `grep FAIL`**：`check_outfit_lock.py` 每行打的是**检查项的名字**（`FAIL 鞋履` / `FAIL 单人物`），不是结论 —— 末尾总判可能是 `🟡 只有 WARN = 可出图` 且 rc=0。`grep -c FAIL` 数出来的数字 = 假警报，会把合格稿当不过、白拖一轮（详见 `yuer-prompt-writer` §16 门禁与脚本）。

**🔴🔴 主体+外观锁只是两道门 = 背杀 / 裸体批次还缺第三道（每张逐个跑）**：上面那两道只查「是不是语儿」+「下装/鞋履/单人物」= **查不出「这张露脸了」「同部位写了两遍」「裸体图混了布料词」**。批量里最容易漏的就是这三类（每张视角不同 = 每张的背杀违规点不同）。**正解 = 每张 prompt 都跑一次 `scripts/batch_scan.py`**（脚本见本技能 scripts/）：
```bash
python3 <yuer-batch-image-runner>/scripts/batch_scan.py /tmp/<批次>/n1.txt   # 单张
python3 <yuer-batch-image-runner>/scripts/batch_scan.py /tmp/<批次>            # 整批
```
它一次扫完：主体 / 外观锁 / 背杀三道（0 脸头表情眼神 + 0 负向词 + 同部位各 1 次）/ 裸体稿漏布料词。**判据 = rc=0 = 过；rc!=0 = 看它打的哪一项 = 改那一项 = 重跑。**

三条实战修法：

- **裸体图 = 建议补「画外实物下装」**（🔴 11-12 默认 0 门禁 = 不补也照样出 = 但补了底模少画画外 = 写稿时自己判），挂在场景句里，**不要写成她穿着**：`a discarded grey pleated skirt crumpled on the floor at the edge of the frame` / `a discarded denim shorts lying on the wet tile floor beside the drain`。机制 = 门禁只认「下装」这个词，裸体图天然缺。
- **🔴 显露出图的「负向词」例外 = `no bra` / `no underwear` / `completely naked` 是【必需词】不是违规词**：机制 = 实战 375d 显露档 = 全裸必须直说 = `completely naked with no bra and no underwear` = 底模靠它判断画的是裸体。判据 = 那句在**描述画面里有什么**（`no bra` = 身上没内衣）→ 保留；那句在**否定画外的元信息**（`no CGI` / `no 3D` / `no watermark` / `no text`）→ 删。**「0 负向词」自检会把显露出图的必需词一起打出来 = 照着删 = 变半裸 = 主人当场看到。** 扫到 `no bra` / `no underwear` = 直接放过，别当违规处理。
- **🔴 微距/局部特写景别 = 画幅外的部位一个词都不许留**：写「极近距离特写」时，全身锚里的胸 / 腰 / 腿 / 背 / 发词全部在画幅外 = 底模会把画外的画进边缘。**判据 = 把 prompt 里每个身体部位词对着景别句读一遍 = 不在画幅内的删干净**（`tight macro framing on her buttocks` = 胸词腰词腿词全删，只留臀 + 缝 + 手 + 海绵）。配套 = 景别句必须**明写画幅里有什么**（`framing tight on the bare buttocks filling the entire frame`）= 底模才知道往哪儿裁。
- **私密场所（卧室/浴室）会 WARN「公共场所锚定」= 只是 WARN，不拦** = 不用改场景。
- **鞋履 WARN 在裸体/近景 = 正常** = **0 为了消 WARN 给她加鞋袜** = 加了反而破坏画面。
- **🔴 鞋履 FAIL 在特写/半身仍会出现** = 门禁把含 `from her collarbones down to her hips` 这类句子判成全身档 = 补一个**单数**白名单鞋词挂画外（`wooden geta sandals resting on the floor beyond the frame`）。
- **🔴 `a pair of XX` 会触发「单人物」FAIL** = 门禁把 `pair of` 读成两个人 = 鞋履/道具/**丢弃的下装**一律写单数（`a pair of wooden sandals` → `wooden sandals`；`a discarded pair of jeans` → `a discarded denim skirt`）。**判据 = 补的道具句里出现 `pair of` = 必 FAIL，改单数再跑。**
  **🔴 同一处「修一次就行」**：机制 = 门禁逐张独立判 = 改 n3 不影响 n1/n5 = 凭记忆以为「风格一样，改一处全批好」= 漏张。**正解 = 改完 build 脚本 → 重跑 build → 整批重出。（🔴 11-12 默认 0 门禁 = 常态链路 0 重扫门禁 = 想查才加 `--gate`）**
- **🔴 鞋履白名单只认** `sneakers?|shoes|boots?|heels?|sandals?|loafers?|slippers?|running shoes` = 和服木屐 / 足袋（`geta` / `tabi socks`）不算，同句必须带一个白名单词。
- **🔴 11-07 已修 = `bare feet` / `she is barefoot` 现在 BOTH 清 WARN 和 FAIL** = 旧版只清 WARN = 写了赤脚还被报「FAIL 鞋履」= 白改一轮。**现在写了赤脚还被报 = 真漏了 = 首选修法 = 在景别句里加 `her feet out of frame`**（特写/半身本来脚就不在画幅 = 不矛盾）；补齐单数鞋词挂画外是次选。
