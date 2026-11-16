## **🔴 外观锁 WARN 的消法 = 改一个短锚，不是补一段**

`check_outfit_lock.py` 报 WARN（缺鞋履）= 锁造型松 = 下一张就漂。**消法 = 一句短而具体的锚**：缺鞋履 → `she is barefoot`（泳池/沙滩/浴室/露台 = 0 写 `no shoes`）；缺妆容 → `light waterproof mascara and a soft coral tint on her lips`（0 写泛词 `makeup` = 门禁仍判缺；0 只写 `bare face` 除非剧情真素颜）。**禁为过门禁补长句 = 白烧字符预算**。**🔴 已知误报 = prompt 里明明写了 `she is barefoot`，门禁仍报 `WARN 鞋履` = 该脚本的赤脚消警在本机没生效 = WARN 不拦出图（rc=0）= 0 为它补鞋 = 0 重跑一轮。判据 = rc=0 就不理它，只看 FAIL 项**|**消 WARN「发型/刘海」= 在发色后面补一个刘海短语**（`long dyed pink hair with blunt bangs` = 0 命中 = 必 WARN）：只写发色 + 湿发状态 = 门禁判缺 = 补**一个**刘海/发型短语（`with blunt bangs` / `with a side part` / `hair pulled back into a loose bun`）= 0 为消它补整段发型描写。**消 WARN「鞋履」= 场景自带赤脚 = 写 `she is barefoot in the tub`（带场景名词）**；消警不生效的处理 = 同上段（rc=0 = 0 补鞋 0 重跑）。**消 WARN「公共场所锚定」= 私密场所已知误报处理 = 见 7c。** **「穿着方式/内层」这一项的正则是短语级命中 = 写对了也判 WARN**：命中词只有 `inner layer / underneath / briefs / thong / nothing underneath / open front / unbuttoned / unzipped / buttoned / slipped off / worn open / worn as her only` —— **`worn as the only layer`（少一个 `her`）0 命中** = 明明写了却报 WARN = 白改一轮。正解 = 写 `worn as her only layer`。**判据 = 门禁报这项 WARN 时，先 grep 自己 prompt 里 `worn as` 开头的短语带没带 `her`，别急着补长句。** 最省事 = 单件上装画面（背心 / 泳衣 / 围裙衬衫 / 运动内衣 / oversized 衬衫当裙子）的服装句里直接塞一个下装词 `briefs`（`black lace briefs` / `white bikini briefs`）= 一词同时过「下装」+「穿着方式/内层」两项 = 0 为消一个 WARN 反复补第二轮（验证连踩：超市 / 天台 / 厨房各白改一轮，白改的原因 = 我塞的是 `with an open neckline and no other layer under it` = 这两个短语都不在正则里）。**

## **🔴 下装必写，漏写 = 底模画成光腿**

## **🔴 风格档位 = 明快日常档（ins / 微博 / 朋友圈风）是默认档**

