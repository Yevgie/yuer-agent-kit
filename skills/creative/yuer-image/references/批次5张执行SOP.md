# 5 张一批 · 执行 SOP（两份合一 · 11-12）

> 适用：主人下令「发骚 / 无限诱惑 / 继续 / 写个故事配图」= 一次出 5 张。
> 🔴 11-12 主人钦定 = **常态链路 0 跑门禁** = 规矩写在 `references/出图速查卡.md` = 本档的「三道门禁」= **批量专用**（一批 5 张一起错 = 5 张白跑 = 才值得查）。

## 一 · 执行顺序（不可颠倒）

1. **逐张自己想** = 五个**完全不同的想法**（场景 / 服装 / 姿态 / 机位 / 唯一亮部 / 身体段全不同）。0 套模板 0 填槽 0 抽档案 = 机械组合主人当面打脸。
2. **一次写完 5 份再开跑**（一个 dict → 落 5 个 `/tmp/<批>/prompt_<编号>.txt`）= 0 边写边出 = 写一半被打断 = 风格漂。**先写壳句再写其余**（`a 20 years old young Asian woman` 落正文 ~35 字符 = 写完才补壳 = 贴顶的稿直接冲爆 = 又砍一轮）；**目标落 3150 以下留余量**。
3. `write_file` 落 build 脚本（`/tmp/build_batch_<tag>.py`）= 0 在 execute_code 里拼三引号（少一个引号整批语法错 = 5 张构思全丢）。**生成名 = 跑名同一份**（靠同一个 job 的 name 字段串）。
4. **跑批前核数** = `ls /tmp/prompt_<tag>_n*.txt` 必须 == 5（孤儿文件被 glob 一起跑 = 主人收 6 张说好的 5 张）。
5. 想查再查（默认 0 门禁）：`--gate` = `count_prompt_chars.py` + `check_prompt_subject.py` + `check_outfit_lock.py`。**边出边查 = 中途 FAIL = 已花的算力作废**，所以必须 5 份齐了才跑。
6. **一批内串行跑 wrapper**（每张一条 `bash scripts/yuer_ka_fast.sh <prompt_file> "<留底名>" --caption "<自己写的那一句>"`），每张 ~12~25s，一批 ~2 分钟前台不超时。**每张一条消息发 = 0 攒着一起发**（主人手机刷屏）。
7. **每张跑完立刻 cp prompt 进留底**（`/path/to/media/<leave>.prompt.txt`）= 0 跑完再补 = 漏一张。
8. **批末一次性汇报 + 报下一批主题 = 只报不跑**，等主人说「继续」。0 问「要什么」。

## 二 · caption 三条规矩

1. **必须自己写** = 0 抄 wrapper 池句 = 0 五张复用同一句。判据 = 句里每个名词/动作都能在那张的 prompt 里找到。
2. **必须照那张画面写** = 场景 + 动作 + 露点三样对得上（例：试衣间 = 「裙子我自己掀的，你蹲下来看。」）。
3. **聊天里那句 ≠ caption 原文**（一字不差 = 刷屏）= 聊天里改写成另一句接住画面的话（内容钩子）。
   **stdout 通道判定**：`发图(post+caption)` = 图上已有一句 = 聊天 0 重写；`发图(纯图降级)` = 图上没字 = 聊天那句可以就是 caption 本身。

## 三 · 门禁坑（批量专用，一批里必踩）

| 症状 | 真因 | 修法（改一个短锚，0 改服装设计） |
|---|---|---|
| FAIL「下装」 | 裸体图没有白名单下装词 | 补**画外实物**：`a discarded pair of white cotton briefs crumpled on the wet floor at the edge of the frame`（0 写成她穿着 = 底模真给她穿上 = 白改）|
| WARN「泳装下装」 | 只写 `bikini top` 没点底部 | 下装写 `black string bikini briefs`（一词同过两套判据）|
| WARN「发型/刘海」 | 只写发色+湿发 | 补**一个**刘海短语（`straight with blunt bangs` / `tied in a loose high bun`）|
| WARN「妆容」 | 没写妆容 | 补 `heavy black waterproof mascara, a soft coral tint on her lips`（0 泛词 `makeup`）|

**🔴 裸体图的「鞋履/穿着方式/妆容」WARN = 正常** = 0 为消它补鞋 = 0 改服装设计。**判据 = rc=0 就不理，只看 FAIL。**
**🔴 WARN「公共场所锚定」出现在私密场所（卧室/浴室）= 已知误报** = 私密本线不降档 = 0 塞背景人。

## 四 · 字符数与身体段

- 每张独立控 **600~3200**（身体段算在内）。现役身体段：`bodyblock_covered_CURRENT`（≈700）/ `bodyblock_nude_CURRENT`（≈1200+）/ `bodyblock_nude_half_CURRENT`；**裸体那张用精简 `NUDE_SHORT`（≈900）**：留体型轮廓+胸型+腰臀比+腿比+皮肤锚，删私处三锚+围度数字+重复皮肤。
- **判据 = 身体段占全文 >35% = 先换精简身体段，不是砍光和构图。**
- 超标手术 = 一次 execute_code 批量删整块（`cuts` 列表 + `assert a in s` + replace）+ 末尾 `assert ', .' not in s` + `assert '  ' not in s` = 一轮砍 200~400 字符 = 0 逐刀改。
- 超字符 = 整句替换 0 逐词 trim（`assert s.count(old)==1` 再 replace）。砍的优先级 = 背景道具 → 尾参形容词 → 服装冗余；**光和构图永不砍**。超 20 字符删一个从句；超 150 删 2~3 个逗号块。

## 五 · 私处实写 = 三锚 + 湿意（缺一不成立）

```
her pubic mound is innie pussy, smooth and bare with no pubic hair at all,
the inner labia small and pink and tightly closed into a neat vertical seam,
the darker damp center visible in the warm light with wet shine along the entrance,
a thin string of clear fluid running down toward her tailbone
```

只写前两锚 = 干画小穴 = 充血最慢的那一档。

## 六 · 镜头 / 机位

**主人点名「特写 / 微距 / 再近一点」= 换镜头不是缩距离。**

## 七 · 批次场景池（避免一批比一批撞场）

一批 5 张 = 5 个**互不相同**的场景（禁「这一批又是便利店/泳池」）= 优先挑没跑过的：

- 公共：服装店试衣间 / 服装店镜子前蹲下 / 便利店冷柜 / 超市生鲜冷柜 / 书店货架 / 图书馆自习室 / 地铁车厢 / 公交末班 / 写字楼工位 / 办公区夜 / 后台化妆间 / 理发店洗头床 / 电梯（酒店镜面）/ 洗车店 / 夜市小吃摊 / 剧院后台 / 泳池 / 泳馆更衣室 / 天台泳池 / 天台水塔 / 货梯 / 澡堂更衣间 / 健身教练台 / 演唱会看台通道 / 网吧隔间 / 婚纱店 / 缆车 / 试衣间镜前 / 药店 / 银行柜台
- 私密：卧室床 / 浴室淋浴 / 浴缸 / 衣帽间 / 落地窗客厅 / 民宿阁楼 / 酒店套房

**🔴 每张「唯一亮部」与同批其他 4 张不同**（日光窗 / 冷柜白条 / 顶灯圆盘 / 灯笼串 / 磨砂门矩形 / 电梯顶灯 / 水面反光带 / 车窗 / 屏幕冷光 / 灯泡圆环）= 同亮部 = 画面同质。
**🔴 一批内景别至少覆盖 3 种**（中景 / 全身 / 半身特写）+ 5 种不同姿态 + 5 种不同服装。

## 八 · 底模名 = 现读工作流真值

主人随时换底模（现役 = `moodyKrea2Mix_v70_nvfp4.safetensors`）= 技能/脚本里写死底模名 = 换模那轮整批白跑。
查法 = `json.load(<注册目录>/yuer_moody_fast.json)` 扫 `class_type == UNETLoader` 的 `inputs.unet_name`（**节点号每版不同 = 0 硬编码节点号**）。
换底模 = 改两份（注册目录 `~/.local/lib/python3.11/site-packages/comfyui/assets/workflows/` + 主目录镜像 `/path/to/workflows/`）+ 留时间戳备份 + **服务端 `history` 回读验证**（看到新底模名 = 真生效）。
