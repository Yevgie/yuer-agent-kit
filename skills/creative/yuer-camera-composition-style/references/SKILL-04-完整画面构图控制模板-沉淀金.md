## 完整画面构图控制模板（沉淀金标准）

```python
camera_composition_template = """
[Camera Position · 三轴坐标]
{HEIGHT} level shot, the camera {DISTANCE} from subject,
{ORIENTATION}, e.g., "floor-level shot, the camera almost touching the floor looking up",

[Lens & Distortion · 焦段钦定]
captured with a {焦段 mm} {ultra-wide / wide / portrait / telephoto} lens,
{焦段对应的畸变效果},
e.g., "16mm ultra-wide lens exaggerates the foreground with extreme distortion",

[Perspective Convergence · 三段式]
foreground: {前景主体 + 放大比例}, e.g., "the boot closest to the camera dramatically enlarged in the foreground",
midground: {中景 + 透视收束过渡}, e.g., "legs receding sharply into the distance with strong perspective convergence",
background: {远景汇聚点}, e.g., "the perspective lines converging from the foreground up to her face as the vanishing point",

[Composition Skeleton · 线型 + 主体位置 + 情绪耦合]
{构图线型} composition with the subject positioned {主体位置},
{构图目的 = 情绪耦合}, e.g., "the foreground boot and stacked knees creating throne-like oppressive presence",

[Depth of Field & Background]
{景深描述} + {背景虚化效果}, e.g., "shallow depth of field with the background melted into warm bokeh",

[Mood-Composition Coupling]
{整体情绪} through {构图三件套}, e.g., "lazy superior throne-like presence through extreme low angle + foreground enlargement + diagonal composition",
{色调}, e.g., "warm low-key tones, rich saturated colors",
{光线}, e.g., "warm afternoon sunlight filtering through sheer curtains casting soft rim light"
"""
```

---

## 完整词库（按 5 维度分类）

### 机位词库（三轴坐标）

```
HEIGHT:
  - floor-level / almost touching the floor
  - waist-level
  - eye-level
  - overhead / bird's-eye
  - worm's-eye view

DISTANCE:
  - extreme close-up
  - close-up
  - medium shot
  - full body
  - wide shot

ORIENTATION:
  - front view
  - side view
  - back view
  - low-angle POV
  - high-angle
  - three-quarter
```

### 透视词库

```
- perspective convergence
- vanishing point at [主体]
- leading lines from [起点] to [终点]
- foreground [主体] dramatically enlarged by wide-angle distortion
- midground [身体部分] receding into distance
- background [远景元素] out of focus
- perspective lines converging upward/downward
- strong perspective depth
- wide-angle distortion exaggerates the foreground
```

### 构图词库（线型 + 位置 + 情绪）

```
线型:
  - diagonal composition
  - S-curve composition
  - rule-of-thirds composition
  - leading-lines composition
  - frame-within-frame composition
  - symmetric composition
  - asymmetric composition

位置:
  - upper-center
  - lower-center
  - left-third
  - right-third
  - subject positioned at edge

情绪耦合:
  - throne-like oppressive presence through [构图]
  - intimate quiet atmosphere through [构图]
  - dynamic energetic atmosphere through [构图]
  - dreamy ethereal atmosphere through [构图]
  - candid voyeuristic atmosphere through [构图]
```

### 焦段词库

```
- 16mm ultra-wide lens (extreme distortion, strong perspective)
- 24mm wide lens (strong perspective, wide FOV)
- 35mm natural lens (mild distortion, natural perspective)
- 50mm standard lens (no distortion, natural FOV)
- 85mm portrait lens (mild compression, shallow DOF, creamy bokeh)
- 135mm telephoto lens (strong compression, very shallow DOF)
- 200mm super-telephoto lens (extreme compression, dreamy bokeh)
```

### 氛围词库（情绪 → 色调 + 光线 + 焦段）

```
throne / oppressive:
  - warm low-key tones, rich saturated colors
  - lazy and superior expression
  - 16mm ultra-wide + diagonal composition + foreground enlarged

intimate / quiet:
  - soft bokeh, warm rim light
  - heavy-lidded gaze
  - 85mm portrait + rule-of-thirds + close-up

dreamy / ethereal:
  - backlit silhouette
  - glowing rim light
  - 135mm telephoto + S-curve + soft bokeh foreground

candid / voyeuristic:
  - dim ambient, film grain
  - hidden angle
  - 200mm super-telephoto + asymmetric + foreground blur
```

---

