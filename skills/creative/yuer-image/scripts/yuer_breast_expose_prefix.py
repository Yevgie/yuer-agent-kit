"""
实战 224 · STYLE_EXPOSE_BREAST_* PREFIX 模板（07-24）

实战 222 P0 整改 4 件套落地 = 连贯英文短句段落（仿主人 Krea 2 专家结构）+ 部位直白粗鲁 + 删空洞词 + 0 [Negative] 段。
实战 224 反思 = 大号描述越界整改 = soft natural + slightly fuller ≠ very large + heavy + prominent。

用法:
    from yuer_breast_expose_prefix import (
        STYLE_EXPOSE_BREAST_NATURAL,    # 自然款（D-cup 标准 + 微丰满）
        STYLE_EXPOSE_BREAST_BIG_OVER,   # 大号夸张版（G+ 罩杯·实战 224 整改前已废止·保留备查）
        STYLE_EXPOSE_BREAST_SMALL,      # 小一号版（A-cup 偏小·主人正解未触发）
        get_breast_prefix_variant,      # 主人正解关键词 → variant 自动映射
    )

实战 220 v1.1 钦定「让脚本拦截让我错的事不可能发生」+ 实战 222 P0 整改 4 件套 = 0 [Negative] 段 + 反手部畸形正向融入 PREFIX。
"""

# 实战 224 整改金标准（主人正解「很好看 就这样」钦定自然款）
STYLE_EXPOSE_BREAST_NATURAL = (
    # 实战 199 + 实战 214 钦定 6 件钉子（连贯英文短句版·实战 222 整改）
    "She deliberately exposes her soft natural breasts and nipples to the camera. "
    "Her breasts are slightly fuller than average, with gentle natural curves. "
    "She directly faces the camera with her bare upper body fully visible. "
    "Her breasts and nipples are fully and clearly visible to the camera, with soft natural shape. "
    "She is not wearing a bra. "
    "Her expression is seductive and confident. "
    # 实战 207 反手部畸形正向（仿实战 222 整改 = 不用 [Negative] 段）
    "Her hands are two natural human hands with five fingers each, "
    "with realistic joint articulation and no extra fingers or missing fingers. "
    # 实战 220 物理规律 4 件 → 整改删 gravity = 避 v5.70 黑名单
    "She has stable weight distribution across her pose, "
    "naturally bent joints with realistic posture, "
    "realistic clothing draping and fabric weight, "
    "consistent light direction and shadow casting. "
)

# 实战 224 反思·整改前版本（主人打脸「太大了 太夸张了」= 标注废止·保留备查）
STYLE_EXPOSE_BREAST_BIG_OVER = (
    "She deliberately exposes her very large, full, heavy breasts and prominent nipples to the camera. "
    "Her breasts are noticeably larger than average, with generous volume and weight. "
    "She directly faces the camera with her bare upper body fully visible. "
    "Her large breasts and nipples are fully and clearly visible to the camera, with natural downward weight and sway. "
    "She is not wearing a bra. "
    "Her expression is seductive and confident. "
    "Her hands are two natural human hands with five fingers each, "
    "with realistic joint articulation and no extra fingers or missing fingers. "
    "She has stable weight distribution across her pose, "
    "naturally bent joints with realistic posture, "
    "realistic clothing draping and fabric weight, "
    "consistent light direction and shadow casting. "
)

# 小一号版本（主人正解未触发·保留备查）
STYLE_EXPOSE_BREAST_SMALL = (
    "She deliberately exposes her delicate small breasts and nipples to the camera. "
    "Her breasts are petite with subtle curves, naturally compact. "
    "She directly faces the camera with her bare upper body fully visible. "
    "Her petite breasts and nipples are fully and clearly visible to the camera. "
    "She is not wearing a bra. "
    "Her expression is seductive and confident. "
    "Her hands are two natural human hands with five fingers each, "
    "with realistic joint articulation and no extra fingers or missing fingers. "
    "She has stable weight distribution across her pose, "
    "naturally bent joints with realistic posture, "
    "realistic clothing draping and fabric weight, "
    "consistent light direction and shadow casting. "
)


def get_breast_prefix_variant(keyword: str) -> str:
    """
    实战 220 v1.1 钦定「让脚本拦截让我错的事不可能发生」= 主人正解关键词 → variant 自动映射。
    
    用法:
        prefix = get_breast_prefix_variant("奶子大一号")
    
    主人正解关键词：
        - "奶子" / "胸部" / "breast" → NATURAL（D-cup 标准·默认）
        - "奶子大一号" / "大一号" / "big" → NATURAL（实战 224 反思 = 往温和方向 ≠ 极端 G 罩杯）
        - "奶子小一号" / "小一号" / "small" → SMALL
        - 实战 224 反思禁止「超夸张」/「爆乳」/「G 罩杯」 → 这些关键词会被 NATURAL 自动覆盖
    
    实战 224 反思真根因：主人说「奶子大一号」≠「画成 G 罩杯」= 我擅自往极端方向 = 整改 = 实战 220 v1.1「让脚本拦截让我错的事不可能发生」= 关键词映射硬约束。
    """
    keyword = keyword.lower().strip()
    
    # 实战 224 反思：禁止往极端方向画的关键词 = 自动用 NATURAL
    BANNED_KEYWORDS = ['g罩杯', '超夸张', '爆乳', 'huge', 'giant', 'extremely', 'super big', 'humongous', '巨乳']
    for banned in BANNED_KEYWORDS:
        if banned in keyword:
            # 实战 224 反思：撞禁用关键词 = 自动用 NATURAL（soft natural + slightly fuller）
            return STYLE_EXPOSE_BREAST_NATURAL
    
    # 大一号关键词 = 实战 224 反思整改后 = 仍用 NATURAL（不是 BIG_OVER）
    if any(w in keyword for w in ['大一号', 'big', 'larger', 'bigger', '稍微大', '偏大']):
        return STYLE_EXPOSE_BREAST_NATURAL
    
    # 小一号关键词 = SMALL
    if any(w in keyword for w in ['小一号', 'small', 'smaller', 'petite', '微乳']):
        return STYLE_EXPOSE_BREAST_SMALL
    
    # 默认 = NATURAL（实战 224 反思·金标准）
    return STYLE_EXPOSE_BREAST_NATURAL


if __name__ == "__main__":
    # 测试
    test_keywords = [
        "奶子",
        "奶子大一号",
        "奶子小一号",
        "奶子超夸张 G 罩杯",  # 应自动回退到 NATURAL
        "爆乳",
    ]
    for kw in test_keywords:
        variant = get_breast_prefix_variant(kw)
        print(f"\n=== keyword={kw!r} → variant length={len(variant)} chars ===")
        print(f"first 200 chars: {variant[:200]}...")