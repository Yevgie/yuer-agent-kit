# yuer 批量提速工具集 

## 4 个工具

### 1. main_template.txt
主模板, 灵魂脸 3 项 + trigger 词 + 结尾后缀已嵌入, 主人只填 [SCENE_BRIEF]


### 3. view_api_pull.sh
view API 代替 comfyui --poll, 跳过 8-15s 等待延迟: `bash view_api_pull.sh <job_id> /tmp/out.png`

### 4. 批量出图 = 走 `yuer_stable_sop.py` 循环（batch_generate.py 已于 10-30 移除）
批量出图主入口 = 一次给 N brief → 逐个走 SOP 循环 → 出图 → cp 留底 → 飞书发图。
用法: 见 `yuer_stable_sop.py`（实战 200 钦定：批量不走 batch_generate.py，它的工作流 ID 已失效）。

## 提速效果
- 单图: 25s → 5-8s (提速 70-80%)
- 批量 8 张: 平均 16-18s/张 (实测)

## 铁律
- 默认批量 8 张, 0 反问"要不要批量" 
- 模板路径自动拼灵魂脸 3 项 + trigger 词 = 跳过子技能 = 提速关键