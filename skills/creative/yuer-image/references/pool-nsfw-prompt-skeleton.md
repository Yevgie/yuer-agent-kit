# 泳池 / 水边 NSFW 提示词骨架（Anima 2D · Krea2 主力通用）

**来源** = 渡鸦词库拆解层太薄（只给 `pool`）时改手写；主人在飞书要中文直出。
**适用** = 「动漫 泳池诱惑」「泳池」「海边湿身」这类题材。

## 🔴 判据 = 拆解结果撑不起一幅画就手写

渡鸦拆解 + 翻译层给的是**词库原文**，不保证能出画面。三层拆解后：
- 词数 < 5 且全是通用词（`pool` / `water` / `outdoors`）= 撑不起来 = 手写
- 翻译层给错词（如 Danbooru 里是 `seductive`，翻译层给 `seducing`）= 手写

## 🔴 骨架（照抄改主题即可）

```
pool, swimming pool, water, surface of water, splashing,
wet clothes, wet body, wet hair, see-through swimsuit, revealing clothing,
string bikini / micro bikini / undone bikini, bikini top slipping,
cleavage, underboob, sideboob, sweat drops, water drops, wet skin, glistening,
sitting in pool / half submerged  或  standing in pool / thigh-deep water,
leaning back, arched back, looking at viewer, looking back, over shoulder,
blush, open mouth, parted lips, seductive smile, sweat,
bare shoulders, collarbone, tan line, wet hair sticking to skin,
sunlight, bright midday sun, sparkling water, caustics, outdoors, summer, blue sky,
(from slightly below:1.2) / low angle, medium shot, cowboy shot, full body, dynamic angle
```

## 🔴 三条实测有效的写法

| 写法 | 效果 |
|---|---|
| `(from slightly below:1.2)` | 低机位真落地（反推实测「相机略低于水面高度仰拍」）—— 比写 `low angle` 有效 |
| `wet hair sticking to skin` + `glistening` | 湿身感真的上（单写 `wet hair` 不够）|
| `bikini top slipping` / `undone bikini` | 半露比「半裸泳衣」这类标签有效 |

## 🔴 主体段必写（与画风无关）= 姿势6物理量 + 表情物理化

只用上面的词堆 = 出来是「商品图」。身体怎么摆必须给：
- 重心/支撑（`leaning back on hands` / `knees on pool edge` / `thigh-deep water`）
- 躯干曲线（`arched back` / `hip thrust` / `spine curved`）
- 头的朝向（`looking back over shoulder` / `looking down at water`）
- 表情物理化（`parted lips with breath` / `blush on cheeks` / `wet eyelashes`）
- 手在做什么（`fingers gripping pool edge` / `both hands in hair`）
