## 五、🔴 批量 build 脚本 = 单一数据源 + 同构（踩过的坑）

- **所有 job 元组必须同长度** = 不等长就在 emit 里解包崩（`ValueError: not enough values to unpack`）= 整批白写。**正解 = emit 只取 `job[0]` 当名字，其余 `", ".join(job[1:])` 拼接** = 天然容错。
- **生成名必须等于跑名** = build 出来叫 `prompt_b4_n1.txt`，循环里去读 `prompt_b4_1.txt` = 全批 FileNotFound（`yuer-image` 7ah2 已记，这里再钉一次）。
- **一条命令里不要混「门禁」和「出图」** = 门禁 FAIL 的那份要单独修好再跑，**0 照跑**（照跑 = 门禁形同虚设 = 出的图不一定合规）。
- **门禁 FAIL「下装」= 修法先查词表**：正则只认 `skirt|shorts|dress|briefs|panties|pants|trousers|jeans|leggings|skort|bikini|swimsuit|swimwear|bathing suit|swim trunks`。`thong` / `panty` / `undies` / `bath towel` / `a wrap` / `a robe` **一律判漏下装** → 补一个白名单内的真下装词。
