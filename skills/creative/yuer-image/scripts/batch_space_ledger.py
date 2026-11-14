#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨批次时空防重复登记簿（无限勾引批次用）

为什么需要它：批次跑了几十批之后，「批与批之间不重复同一时空」靠记性必然撞
（实测敦煌/唐宫/雨夜便利店/泳池边在 30 批里反复出现 = 主人看到的是同一批换皮）。
本脚本 = 一个落盘的登记表 + 一个「还没用过」的查询 = 排批时先查再建。

🔴 11-01 主人当场指出「都是重复的 五张一重复 没意义」→ 根因 = 账本从来没被跑过
（登记文件根本不存在）= 100+ 批全靠脑内记性 = 必然撞。
    正解 = ① 池子扩到量级（65 → 300+ 空间条目 / 18 → 120+ 露出位）
          ② `seed` 子命令 = 从已跑批次的 prompt 反解时空键并回填登记（一次性补齐历史账）
          ③ `pick` 子命令 = 抽 N 个 0 次的条目（排批时直接用 = 0 靠脑内记性）

用法：
  /usr/bin/python3 scripts/batch_space_ledger.py list
      → 打印题材池每项的使用次数 + 0 次的（可优先用）
  /usr/bin/python3 scripts/batch_space_ledger.py add <tag> <key1,key2,...>
      → 把这一批用掉的时空登记进去（同 key 再登记 = 计数 +1）
  /usr/bin/python3 scripts/batch_space_ledger.py used
      → 打印全部登记明细（按批次）
  /usr/bin/python3 scripts/batch_space_ledger.py seed <prompt_glob>
      → 反解 /tmp/prompt_<tag>_n*.txt 里的时空键并回填登记（补历史账）
  /usr/bin/python3 scripts/batch_space_ledger.py pick <n> [pool]
      → 抽 n 个还没用过的条目（space=空间 / hook=露出位 / any=混抽）

登记表 = /path/to/media/.batch_space_ledger.tsv（持久化，重启不丢）
"""
import glob
import os
import random
import re
import sys
import time

LEDGER = "/path/to/media/.batch_space_ledger.tsv"

# 🔴 题材池 = 空间条目 + 露出位条目（两套分开登记，重复率最高的是露出位）
# 🔴 11-01 扩池 = 65 → 320 个空间条目 / 18 → 132 个露出位
#    = 跑满 100 批（500 张）不撞车的前提是池子 ≥ 批数 × 5
SPACE_POOL = [
    # ── 现实日常 ──
    "便利店夜班", "便利店外雨夜", "便利店后仓", "咖啡馆露台", "咖啡馆吧台后", "旧书店门口",
    "旧书店二楼", "学校走廊", "学校教室后排", "学校天台", "食堂打饭窗口", "澡堂更衣室",
    "小区快递柜", "菜市场摊位", "花店后间", "理发店洗头床", "美容院护理床", "美甲店沙发",
    "洗衣房", "员工宿舍", "合租房客厅", "出租屋厨房", "打印店", "手机维修店",
    "网约车后座", "出租车后座", "地铁末班车", "高铁卧铺", "绿皮车厢", "长途客车",
    "银行柜台", "医院走廊", "医院放射科", "药房", "诊所输液室", "体检中心",
    "派出所大厅", "居委会办公室", "快递分拣仓", "仓库货架", "服装店试衣间", "化妆品柜台",
    "书店讲堂", "健身房器械区", "瑜伽教室", "舞蹈排练房", "钢琴教室", "录音棚",
    "陶艺工坊", "花艺工作台", "裁缝铺", "修车厂", "汽修举升机", "洗车行",
    "停车场", "地下车库", "电梯轿厢", "楼梯间", "天台水塔", "楼道消防栓",
    "自助洗衣房", "公用电话亭", "报刊亭", "早餐摊", "夜市大排档", "大排档塑料凳",
    "食堂后厨", "冷库", "冰库", "烘焙厨房", "铁板烧台", "居酒屋吧台",
    "清吧角落", "KTV包厢", "桌球吧", "棋牌室", "麻将馆", "按摩店",
    "盲人按摩室", "纹身店", "美甲补光箱", "摄影棚", "影棚无缝背景", "绿幕棚",
    "练舞房镜墙", "试衣镜前", "电梯镜前", "车后视镜", "浴室镜前", "梳妆镜前",
    # ── 古代东方 ──
    "敦煌莫高窟", "唐宫夜宴", "唐宫寝殿", "唐宫纱帘后", "长安酒肆", "长安胡店",
    "宋代茶室", "宋代书院", "明朝绣楼", "明朝绣房", "明朝官窑", "徽州竹林",
    "徽州天井院", "苏州园林", "苏州绣房", "江南水乡乌篷船", "西湖断桥", "西湖画舫",
    "秦岭始皇陵", "汉长安未央宫", "汉代驿站", "魏晋竹林七贤", "隋代大运河",
    "唐代曲江", "唐代夜市", "五代宫闱", "宋代汴梁", "宋代临安茶肆", "元代草原帐",
    "明代紫禁城长廊", "清代圆明园", "清末上海滩", "民国茶馆",
    # ── 民国/近代 ──
    "1930上海舞厅", "1927酒肆", "民国弄堂", "老上海月历牌墙", "租界巡捕房",
    "民国火车站", "民国电车", "民国烟馆", "民国当铺", "民国绸缎庄", "民国照相馆",
    "民国戏台", "民国茶楼说书", "民国女校", "民国报馆", "民国电影院", "民国影院放映厅",
    "民国公共浴室", "民国轮船甲板", "民国飞机舷梯", "民国铁路卧铺", "民国旧式电梯",
    "1949工厂车间", "1960年代澡堂", "1970年代粮仓", "1980年代录像厅", "1990年代卡拉OK",
    "千禧年网吧", "2008奥运场馆", "2010高铁商务座",
    # ── 未来科幻 ──
    "月球基地", "月球采掘坑", "赛博后巷", "赛博天桥", "赛博天桥雨夜", "机械姬机房",
    "赛博义体诊所", "全息广告墙下", "机械姬检修间", "空间站穹顶", "空间站观察窗",
    "未来登机口", "未来航站楼", "未来数据中心", "未来机甲库", "未来太空港",
    "未来轨道站", "未来蜂巢都市", "未来空中花园", "未来医疗舱", "未来手术室",
    "未来引擎舱", "未来通勤幕墙", "未来电池工厂", "未来纳米车间", "未来农业穹顶",
    "未来废土城", "未来地下城", "未来虚拟偶像直播舱", "未来电竞舱", "未来虚拟现实房",
    "火星尘暴", "木卫二冰下基地", "土星环空间站", "金星浮空城", "流浪行星地表",
    "彗星观测站", "暗物质探测器舱", "粒子对撞机", "量子实验室", "克隆培养舱",
    "未来城市街道", "未来城市天台", "未来城市地铁", "未来城市停车塔", "未来城市下水道",
    "未来机器人厨房", "未来无人驾驶车", "未来芯片厂", "未来光伏塔", "未来风电场",
    # ── 异世界仙侠 ──
    "云海仙峰", "月下竹林", "莲池", "莲池深处", "仙宫回廊", "丹药房",
    "灵兽牧场", "符纸阵中", "渡劫天台", "瑶池", "东海龙宫阶", "幽冥忘川岸",
    "魔域血池", "雪山之巅", "仙门藏书阁", "天梯石阶", "混沌初开虚空", "星河渡口",
    "妖市夜集", "书生书斋", "剑冢", "仙鹤亭", "灵泉潭", "洞天福地",
    # ── cos 角色 ──
    "机甲驾驶舱", "机甲机甲库待命位", "未来警员巡逻岗", "魔法学院大教室", "魔法学院塔楼",
    "蒸汽朋克工厂", "海盗船甲板", "骑士城堡", "忍者屋顶", "忍者密道",
    "超能力都市天台", "侦探事务所", "飞行员座舱", "太空服更衣间", "女仆咖啡厅后厨",
    "赛车手维修区", "赛车手赛道维修道", "漫画格背景", "像素游戏场景", "二次元教室",
    # ── 旅行/度假 ──
    "巴黎咖啡馆露台", "巴黎铁塔观景台", "罗马许愿池", "巴塞罗那海边", "威尼斯贡多拉",
    "威尼斯面具舞会", "瑞士雪山火车", "瑞士观景山", "东京新宿街头", "东京涉谷",
    "京都鸟居道", "京都町屋", "首尔弘大", "曼谷湄南河", "巴厘岛梯田", "巴厘岛海崖",
    "纽约地铁车厢", "洛杉矶便利店", "旧金山金门大桥", "悉尼歌剧院台阶", "迪拜喷泉广场",
    "开罗金字塔下", "摩洛哥麦地那市集", "希腊圣托里尼", "圣托里尼日落露台", "冰岛黑沙滩",
    "冰岛瀑布", "冰岛苔原", "极光雪原", "芬兰极光玻璃屋", "挪威峡湾", "苏格兰高地",
    "爱尔兰悬崖", "葡萄牙海边", "西班牙塞维利亚", "土耳其热气球", "印度斋浦尔宫",
    "尼泊尔雪山", "北海道雪祭", "北海道花田", "冲绳海崖", "北海道热汤",
    "苏格兰海边灯塔", "加州公路", "黄石地热", "大峡谷观景台", "塞伦盖蒂草原",
    "亚马逊支流", "马丘比丘", "复活节岛", "撒哈拉绿洲", "埃及白沙漠",
    # ── 户外自然 ──
    "雨林瀑布", "雨林吊桥", "丛林瀑布", "苔藓洞穴", "荒漠矿井", "露天矿坑",
    "海上钻井平台", "灯塔灯室", "热气球", "火山岩浆", "冰川", "雪山峰顶",
    "雪山木屋", "雪地摩托", "雪夜加油站", "沙漠沙丘", "沙漠古城", "沙漠神像",
    "沙暴废墟", "热带海岛", "海钓码头", "海岛灯塔", "深海珊瑚礁", "深海沉没都市",
    "海底热泉", "海崖日出", "悬崖栈道", "峡谷河流", "草原蒙古包", "梯田灌水",
    "竹海小径", "红杉巨木林", "苔原冻湖", "冰川裂隙", "火山口边缘", "间歇泉旁",
    "盐湖结晶", "沙丘星夜", "月升沙漠", "极夜冰原", "原始丛林溪边", "瀑布水帘洞",
    # ── 工业/都市 ──
    "钢铁厂高炉", "化工厂反应釜", "重工车间行车", "港口集装箱堆场", "铁路编组场",
    "山隧道施工现场", "桥墩工地", "摩天大楼顶层", "施工脚手架", "地下停车场坡道",
    "垃圾焚烧厂", "污水处理池", "风电场检修平台", "水电站大坝", "变电所", "煤矿井下",
    "工厂食堂", "夜班公交终点站", "城市天台花园", "中央车站月台", "跨海大桥桥面",
    "旧城区菜市场", "城中村天台", "地下通道", "天桥", "加油站便利店",
    # ── 灾难/末世 ──
    "火山灰覆盖的城市", "海啸退去后的街道", "地震废墟", "雪灾后的城市", "沙尘暴街道",
    "核冬天废土", "瘟疫隔离区", "外星入侵封锁线", "洪水淹没的村庄", "火山灰下的博物馆",
    "停电的地下车库", "毒雾中的天台", "陨石坑荒原", "冰川融化的峡湾", "海平面上升的旧城",
    # ── 幻想/异质感 ──
    "梦境草原", "镜厅", "倒影湖", "巨大的图书馆", "钟表机械城", "水晶洞穴",
    "云端宫殿", "星空露台", "月球表面", "失重空间站", "镜面金字塔", "沙海迷宫",
    # ── 11-01 二次扩充（主人说「场景主题继续增加 还是不够」）──
    "飞行器机库", "信号塔顶", "戏剧后台", "盐矿", "梯田灌水", "气象站",
    "深海热泉", "藏经阁", "荒漠公路", "钟楼内部", "灯塔螺旋阶梯", "旧书库深处",
    "古堡地窖", "疯人院走廊", "游轮甲板", "邮轮餐厅", "雪橇道", "冰壶赛道",
    "赛车手维修区", "跳伞机舱", "滑翔伞起飞坡", "攀岩岩壁下", "瀑布水帘洞",
    "火山灰下的博物馆", "外星母舰内部", "时间图书馆", "镜中镜厅", "无限阶梯",
    "云端温室", "巨鲸养殖湾", "冰岛苔原", "高原湖泊", "草原蒙古包", "绿皮车厢顶",
    "货轮集装箱顶", "废弃游乐园", "老式理发店", "录像厅", "溜冰场", "保龄球馆",
    "台球厅", "射击馆", "攀岩馆", "室内冲浪池", "攀岩绳索墙", "冬泳池",
    "教堂彩窗下", "修道院回廊", "石窟凿壁", "金殿内部", "皇宫御花园", "黄鹤楼飞檐",
    "吊脚楼吊脚层", "客家围屋", "徽州木雕楼", "潮汕祠堂", "岭南骑楼", "上海弄堂亭子间",
    "香港天台", "澳门大三巴石阶", "台北眷村", "首尔汗蒸房", "曼谷霓虹巷",
    "香港叮叮车", "新加坡空中走廊", "迪拜沙漠冲沙", "迪拜商场滑冰场", "卡塔尔沙漠露营",
    "摩洛哥蓝城", "埃及金字塔内部", "希腊古剧场", "罗马浴场", "庞贝古城街道",
    "冰岛冰川崩口", "挪威峡湾码头", "芬兰桑拿", "拉普兰冰湖", "西伯利亚雪原",
    "蒙古沙漠星空", "青海湖边", "喀什老城", "丽江古城", "大理洱海", "西双版纳夜市",
    "涠洲岛海边", "青海盐湖", "长白山天池", "黄山云海", "泰山日出", "华山长空栈道",
    # ── 穿越（时代错位）──
    "现代地铁里的唐代仕女", "写字楼电梯里的民国小姐", "超市货架旁的宋代书生",
    "旧电影院里的玛雅祭司", "现代校园里的维京战士", "北京胡同里的江户武士",
    "现代医院里的古埃及祭司", "加油站里的中世纪骑士", "现代写字楼里的古罗马角斗士",
    "现代厨房里的唐代仕女", "现代地铁里的宋代书生", "现代酒店大堂里的古埃及艳后",
    "旧货市场里的中古海盗", "现代公园长椅上的维京人", "现代商场里的玛雅祭司",
    "现代理发店里的江户艺伎", "天台上的法国大革命女仆", "旧火车站候车厅里的中古骑士",
    "现代泳池边的古罗马人", "现代便利店里的维京战士", "写字楼格子间里的江户武士",
    "现代医院走廊里的古埃及祭司", "超市冷柜旁的宋代书生", "现代电梯里的唐代仕女",
    "现代理发店里的中世纪贵族", "现代餐厅里的玛雅祭司", "现代地铁车厢里的古罗马人",
    # ── 玄幻/仙侠 ──
    "宗门祭坛锁链台", "渡劫雷劫台", "万剑冢剑阵", "灵脉地脉裂口", "妖皇祭坛血池",
    "封印魔塔顶层", "幽冥忘川断桥", "瑶池蟠桃林", "天书阁浮空书海", "仙魔战场残旗",
    "骨龙巢穴", "神兽契约台", "灵植药园秘境", "星辰祭坛", "虚空裂缝边缘",
    "九重天阙云阶", "魔教圣女殿", "仙门问剑台", "上古遗迹石门", "妖市黑市后巷",
    "灵兽渡劫谷", "冥府鬼市", "水月洞天", "天工阁机关室", "龙宫珊瑚殿",
    "仙魔古战场", "神兵铸造炉", "万魂幡阵", "灵兽契约殿", "天机阁占星台",
    # ── 科幻/赛博 ──
    "轨道电梯舱内", "全息广告街", "义体诊所手术间", "克隆体培养舱阵列", "记忆档案图书馆",
    "神经接驳舱", "曲率引擎舱", "外星信号阵列", "量子计算冷却室", "反重力货仓",
    "赛博寺庙改装", "仿生人零件市场", "义眼调校间", "脑机接口躺椅", "虫洞观测台",
    "废弃空间站环廊", "能源塔内部", "海底数据中心", "火星农业穹顶", "AI仲裁法庭",
    "合成人养老院", "记忆黑市", "虚拟偶像录音棚", "反物质储存舱", "轨道垃圾场",
    "光速飞船货舱", "冷冻胚胎库", "语言翻译局", "时间线管理局", "意识上传舱",
    "纳米工厂车间", "重力环旋转舱", "深海空间站", "外星殖民地广场", "赛博僧侣经堂",
    # ── cos ──
    "cos 魔法学院入学", "cos 机甲驾驶员", "cos 江户巫女", "cos 未来特务", "cos 高铁乘务",
    "cos 校园制服", "cos 太空站工程师", "cos 战国武将", "cos 霓虹黑客", "cos 深海潜水员",
    "cos 芭蕾舞者", "cos 牛仔竞技", "cos 火线救援员", "cos 天文台研究员", "cos 蒸汽朋克机械师",
    "cos 啦啦队员", "cos 古埃及舞者", "cos 武侠侠女", "cos 未来警察", "cos 甜品店店员",
    "cos 战地记者", "cos 交响乐首席", "cos 花匠", "cos 快递员", "cos 街头涂鸦者",
    "cos 偶像练习生", "cos 冰球运动员", "cos 高空跳伞员", "cos 图书管理员", "cos 钟表匠",
    "cos 灯塔守塔人", "cos 渔家女", "cos 少林武僧", "cos 花魁", "cos 涂鸦涂装师",
    "cos 仿生人偶像", "cos 飞艇船长", "cos 敦煌飞天", "cos 罗马角斗士", "cos 摩托车骑手",
]

HOOK_POOL = [
    # 室内家具位
    "浴缸", "淋浴间", "大床", "沙发", "餐桌", "厨房台面", "窗台", "楼梯", "墙角",
    "桌子下", "阳台", "车里", "泳池边", "草坡", "温泉", "办公桌", "地板", "浴帘",
    "书架", "台阶", "榻榻米", "懒人沙发", "飘窗", "吧台", "柜台", "梳妆台",
    "晾衣绳", "洗衣篮", "储物柜", "工位隔断", "会议桌", "白板前", "钢琴凳",
    "琴键上", "吉他旁", "画架前", "缝纫机旁", "试衣镜前", "玄关", "走廊拐角",
    "储物间", "阁楼木地板", "地下室水泥地", "车后备箱", "副驾座", "驾驶座",
    "公交车最后一排", "地铁座位", "飞机舷窗边", "列车卧铺", "轮椅", "秋千",
    "吊床", "浴袍挂钩下", "更衣室凳子", "储物柜前", "自助洗衣房圆凳",
    "公共澡堂长凳", "理发椅", "美容院床", "按摩床", "纹身椅", "美甲凳",
    "收银台内侧", "货架之间", "仓库纸箱上", "梯子上", "脚手架", "吊车挂钩",
    "灯塔螺旋楼梯", "风车阁楼", "屋顶水箱盖", "树屋平台", "集装箱内",
    "集装箱顶", "卡车车厢", "谷仓阁楼", "洞穴石台", "树根间", "岩石凹陷",
    "溪水边石头", "沙滩沙丘凹陷", "草丛深处", "麦田中央", "稻田埂上", "苔藓石面",
    "攀岩岩壁下", "跳板", "蹦床", "瑜伽垫", "瑜伽球", "拉力绳锚点",
    "落地窗前", "飘窗坐垫", "榻上", "梳妆凳", "浴室地砖", "洗手台",
    "洗手台镜前", "落地灯下", "窗帘缝隙", "百叶窗后", "门缝偷看", "反光车窗前",
    "橱窗玻璃倒影", "电梯镜前", "汽车后视镜", "雨窗玻璃后", "车窗雾气上",
    "露台栏杆边", "屋顶边缘", "天台水塔下", "泳池浮排", "泳池台阶", "泳池躺椅",
    "海边礁石上", "沙滩遮阳伞下", "吊床绳上", "野餐毯上", "帐篷里", "睡袋里",
    "火堆旁", "篝火边", "瀑布下", "水帘后", "喷泉池中", "喷泉边沿",
    "游泳池里", "浴缸水中", "澡盆里", "木桶浴", "温泉池中", "热汤池沿",
    "按摩床巾", "治疗床", "手术台", "牙科椅", "理发洗头床", "化妆镜前凳",
    "更衣室镜子前", "试衣间里", "量衣台", "收银台", "吧凳", "高脚椅",
    "餐桌布上", "厨房料理台", "烤箱前", "酒窖桶上", "茶室榻榻米",
    "和室壁龛", "神龛前", "庙宇供桌", "佛龛前", "祭坛台阶", "石碑前",
    "图书馆书架间", "古籍桌", "学堂讲台", "考场桌面", "办公室转椅",
    "复印机旁", "白板前站立", "落地窗工位", "会议室长桌",
]

# 主体/脸部/妆容变体池（防"五张一重复"= 同一句式套五张）
FACE_POOL = [
    "light waterproof mascara and a soft coral tint on her lips",
    "bare face with only a light peach lip balm and a faint smudge of blush",
    "smoky grey eyeshadow and a deep wine lipstick",
    "fresh dewy skin with clear gloss on her lips and no visible makeup",
    "thick winged eyeliner and a nude matte lipstick",
    "sun-kissed tan with a copper shimmer on her cheekbones and a warm nude lip",
    "a scattering of freckles across her nose and a soft pink gloss",
    "cool-toned makeup with a muted mauve lip and brushed brows",
    "honey gloss lips and a soft brown smoky eye",
    "clean skin with just a red lip and defined brows",
]

EXPRESSION_POOL = [
    "her upper eyelids heavy and half-lowered, her gaze finding the lens, her lips parted",
    "her head tilted down, not aware of the camera, her mouth slightly open",
    "her eyes closed, the muscles of her jaw loose, mid-breath",
    "caught mid-turn, her eyes still on the room, her lower lip between her teeth",
    "she looks straight into the lens with a slow lazy smile, her lips closed",
    "her brow slightly furrowed, her lips pressed together, her gaze drifting past the camera",
    "her lips slightly open, her eyes bright and directly on the camera, an eager smile forming",
]

FRAMING_POOL = [
    "full body framing her entire body from the crown of her head to the soles of both feet contained inside the frame, the camera about four meters away at waist height",
    "full body framing her entire body from the crown of her head to the soles of both feet contained inside the frame, the camera about two meters away at knee height, looking slightly up",
    "a three-quarter body shot framing her from the crown of her head down to mid-thigh, the camera about two and a half meters away at chest height",
    "a medium shot framing her from the crown of her head down to her knees, the camera about two meters away at chest height",
    "a medium shot framing her from the crown of her head down to her hips, the camera about one and a half meters away at her own height",
    "a low angle shot from below her waist line looking up at her, the camera about one meter away at floor level, her legs and hips filling the lower frame",
    "shot from behind her over her shoulder, her back and the curve of her waist filling the frame, the camera about one and a half meters away",
    "a tight shot framing her from her collarbones down to her hips, her face cropped out above the mouth, the camera about one meter away",
]

# 唯一亮部池（防每张都"硬白圆盘"）
LIGHT_POOL = [
    "the single brightest thing in the frame is a hard white disc of sunlight burning through the gap in the shutters, everything else falling into deep blue shadow",
    "the single brightest thing in the frame is a warm strip of light thrown across her by a neon sign, the rest of the scene sinking to black",
    "the single brightest thing in the frame is the orange glow of a fire throwing her shadow long behind her, the surroundings going cold and dark",
    "the single brightest thing in the frame is the cold white light of a screen washing over her face and chest, the room behind her falling away",
    "the single brightest thing in the frame is the low golden sun flooding in from the horizon and rimming her whole body, the ground going deep amber",
    "the single brightest thing in the frame is one hard rectangular window beam landing on her, the rest of the room in heavy shadow",
    "the single brightest thing in the frame is a single burning candle flame at the edge of the frame casting long moving shadows",
    "the single brightest thing in the frame is the green wash of an instrument panel in front of her, the cabin going almost pitch black",
    "the single brightest thing in the frame is the headlight beam of a car parked behind her, the street dropping into darkness",
    "the single brightest thing in the frame is the sky itself burning bright behind a dark foreground, her body reading as a dark silhouette against it",
]

# 身体段变体池（防637张共用同一段身体描述）
BODY_VARIANTS = [
    # v0 = 现有 CURRENT 覆盖段（由 build 脚本读文件注入，这里保留占位）
    None,
    "a tall slender build with elongated vertical proportions, slim yet voluptuous body, a pronounced hourglass figure, her legs longer than her torso reaching up to her chest, smooth long legs with slender firm thighs, a tiny sharply defined waistline that flares out to the hip, wide hips, a high tight peach shaped bottom, two round buttocks that curve out in a smooth peach-like swell, large full breasts held up in a lifted rounded shape, a deep natural cleavage, pale porcelain skin, luminous ivory skin, smooth soft skin texture, natural skin pores visible",
    "a tall slender build with elongated vertical proportions, a slim yet voluptuous physique, a clearly hourglass silhouette, her thighs long and smooth with a firm muscle line, a very narrow waist that curves into full rounded hips, a high sculpted peach shaped bottom, two full round buttocks with a smooth lifted curve, large heavy breasts sitting high and firm on her chest, a deep shadowed cleavage, warm honey skin, luminous tan skin, smooth soft skin texture, fine skin pores visible",
    "a tall slender build with long vertical proportions, a slim yet voluptuous body with an hourglass shape, smooth long legs, slender firm thighs, a razor-thin waistline flaring into wide hips, a high tight peach shaped bottom, two round firm buttocks curving out in a smooth swell, large full breasts lifted into a rounded shape, a deep natural cleavage, pale ivory skin, luminous porcelain skin, smooth soft skin texture",
    "a tall slender build, slim yet voluptuous with an exaggerated hourglass curve, her legs noticeably longer than her torso, smooth long legs, slender toned thighs, a tiny defined waist flaring to broad hips, a high tight peach shaped bottom, two round buttocks with a smooth lifted swell, large full breasts held high and forward, a deep natural cleavage, warm pale skin, luminous ivory skin, smooth soft skin texture, natural skin pores visible",
]


def _read():
    rows = []
    if os.path.exists(LEDGER):
        with open(LEDGER, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line or line.startswith("#"):
                    continue
                rows.append(line.split("\t"))
    return rows


def _write(rows):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "w", encoding="utf-8") as f:
        f.write("# tag\tkeys\tts\n")
        for r in rows:
            f.write("\t".join(r) + "\n")


def _counts(rows):
    counts = {}
    for r in rows:
        if len(r) < 2:
            continue
        for k in r[1].split(","):
            k = k.strip()
            if k:
                counts[k] = counts.get(k, 0) + 1
    return counts


def cmd_seed(pattern):
    """反解已跑批次的 prompt 里的时空键 = 回填历史账"""
    files = sorted(glob.glob(pattern))
    if not files:
        print("没匹配到文件: %s" % pattern)
        return 1
    rows = _read()
    known = set()
    for r in rows:
        if len(r) > 1:
            known.update(k.strip() for k in r[1].split(",") if k.strip())
    added = 0
    for f in files:
        tag = os.path.basename(f)
        m = re.match(r"prompt_(.+?)_n\d+\.txt$", tag)
        tag = m.group(1) if m else tag
        text = open(f, encoding="utf-8").read()
        keys = []
        for pool in (SPACE_POOL, HOOK_POOL):
            for k in pool:
                hints = _zh_to_en_hint(k)
                if not hints:
                    continue
                if isinstance(hints, str):
                    hints = [hints]
                low = text.lower()
                if any(h.lower() in low for h in hints):
                    keys.append(k)
        if not keys:
            continue
        kk = ",".join(keys)
        if kk in known:
            continue
        rows.append([tag, kk, time.strftime("%Y-%m-%d %H:%M:%S")])
        known.add(kk)
        added += 1
    _write(rows)
    print("回填 %d 批 → %s" % (added, LEDGER))
    return 0


# 🔴 中文键 → prompt 里实际会出现的英文短语（部分同义，多个候选任一命中即算）
_ZH_EN = {
    "雨夜便利店": ["rain", "convenience"], "便利店外雨夜": ["convenience store", "alley"],
    "敦煌莫高窟": ["dunhuang"], "唐宫夜宴": ["tang dynasty", "palace"], "唐宫寝殿": ["tang dynasty", "bedchamber"],
    "唐宫纱帘后": ["gauze", "tang dynasty"], "长安酒肆": ["changan", "tavern"],
    "宋代茶室": ["song dynasty", "tea"], "明朝绣楼": ["ming dynasty", "boudoir"],
    "徽州竹林": ["bamboo", "huizhou"], "苏州园林": ["garden", "suzhou"],
    "1930上海舞厅": ["1930", "shanghai", "dance"], "1927酒肆": ["1927", "tavern"],
    "民国弄堂": ["republic-era", "lane"], "老上海月历牌墙": ["shanghai", "calendar poster"],
    "月球基地": ["moon base"], "赛博后巷": ["cyberpunk", "alley"], "赛博天桥": ["cyberpunk", "skybridge"],
    "机械姬机房": ["robotic", "facility"], "空间站穹顶": ["space station", "dome"],
    "未来登机口": ["terminal", "departure"], "未来航站楼": ["terminal"], "未来数据中心": ["data center"],
    "未来机甲库": ["hangar", "mecha"], "未来太空港": ["spaceport"], "未来轨道站": ["orbital station"],
    "未来蜂巢都市": ["honeycomb", "arcology"], "未来空中花园": ["sky garden"], "未来医疗舱": ["medical pod"],
    "未来手术室": ["operating theatre"], "未来引擎舱": ["engine"], "未来通勤幕墙": ["commuter", "glass"],
    "深海珊瑚礁": ["coral reef"], "海岛灯塔": ["lighthouse"], "沙漠沙丘": ["dune"],
    "沙漠古城": ["desert", "ruins"], "沙漠神像": ["statue", "desert"], "沙暴废墟": ["sandstorm"],
    "火山岩浆": ["volcano", "lava"], "冰岛黑沙滩": ["basalt", "beach"], "冰川": ["glacier"],
    "雪山峰顶": ["summit", "snow"], "雪地摩托": ["snowmobile"], "雪夜加油站": ["gas station", "snow"],
    "雨林瀑布": ["rainforest", "waterfall"], "雨林吊桥": ["rainforest", "rope bridge"],
    "荒漠矿井": ["mine"], "露天矿坑": ["open pit"], "海上钻井平台": ["drilling platform"],
    "灯塔灯室": ["lighthouse"], "热气球": ["hot air balloon"], "热带海岛": ["tropical", "island"],
    "海钓码头": ["pier", "fishing"], "巴黎咖啡馆露台": ["paris", "cafe"], "巴黎铁塔观景台": ["paris", "eiffel"],
    "罗马许愿池": ["rome", "fountain"], "巴塞罗那海边": ["barcelona", "sea"],
    "威尼斯贡多拉": ["venice", "gondola"], "威尼斯面具舞会": ["venice", "mask"],
    "云海仙峰": ["sea of clouds", "peak"], "月下竹林": ["bamboo", "moon"],
    "莲池": ["lotus pond"], "机甲驾驶舱": ["cockpit"], "未来警员巡逻岗": ["police"],
    "魔法学院大教室": ["magic academy"], "蒸汽朋克工厂": ["steampunk"], "海盗船甲板": ["pirate", "deck"],
    "骑士城堡": ["castle"], "忍者屋顶": ["ninja", "roof"], "侦探事务所": ["detective", "office"],
    "飞行员座舱": ["pilot", "cockpit"], "太空服更衣间": ["spacesuit"], "女仆咖啡厅后厨": ["cafe", "kitchen"],
    "赛车手维修区": ["pit lane"], "二次元教室": ["anime", "classroom"],
    "极光雪原": ["aurora", "snow"], "冰岛瀑布": ["waterfall", "iceland"], "苏格兰高地": ["scotland", "highlands"],
    "开罗金字塔下": ["pyramid", "cairo"], "希腊圣托里尼": ["santorini"], "东京新宿街头": ["tokyo", "shinjuku"],
    "京都鸟居道": ["torii"], "巴厘岛梯田": ["bali", "terrace"], "大峡谷观景台": ["grand canyon"],
    "浴缸": ["bathtub"], "大床": ["bed"], "沙发": ["sofa"], "餐桌": ["dining table", "table"],
    "厨房台面": ["kitchen counter", "counter"], "窗台": ["windowsill"], "楼梯": ["stairs", "staircase"],
    "墙角": ["corner of the room"], "桌子下": ["under the table"], "阳台": ["balcony"],
    "车里": ["car seat", "back seat"], "泳池边": ["pool edge", "poolside"], "草坡": ["grass slope", "grassy hill"],
    "温泉": ["hot spring"], "办公桌": ["office desk", "desk"], "地板": ["floor"], "浴帘": ["shower curtain"],
    "书架": ["bookshelf"], "台阶": ["steps"], "落地窗前": ["floor to ceiling window", "window"],
    "办公室转椅": ["office chair"], "手术台": ["operating table"], "吧台": ["bar counter"],
    "电梯轿厢": ["elevator"], "泳池里": ["in the pool"], "温泉池中": ["in the hot spring"],
}


def _zh_to_en_hint(zh):
    return _ZH_EN.get(zh)


def cmd_pick(n, pool):
    rows = _read()
    counts = _counts(rows)
    if pool == "hook":
        pool_list = HOOK_POOL
    elif pool == "space":
        pool_list = SPACE_POOL
    else:
        pool_list = SPACE_POOL + HOOK_POOL
    fresh = [k for k in pool_list if counts.get(k, 0) == 0]
    used = [k for k in pool_list if counts.get(k, 0) > 0]
    out = fresh[:n]
    if len(out) < n and used:
        random.seed(time.time())
        out += random.sample(used, min(n - len(out), len(used)))
    print(" | ".join(out))
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 0
    cmd = sys.argv[1]
    rows = _read()

    if cmd == "list":
        counts = _counts(rows)
        print("=== 空间条目 (%d 个) ===" % len(SPACE_POOL))
        for k in SPACE_POOL:
            c = counts.get(k, 0)
            print("%-16s %d%s" % (k, c, "  <== 没用过" if c == 0 else ""))
        print("=== 露出位条目 (%d 个) ===" % len(HOOK_POOL))
        for k in HOOK_POOL:
            c = counts.get(k, 0)
            print("%-16s %d%s" % (k, c, "  <== 没用过" if c == 0 else ""))
        return 0

    if cmd == "used":
        for r in rows:
            print("%s\t%s\t%s" % (r[0], r[1], r[2] if len(r) > 2 else ""))
        return 0

    if cmd == "add":
        if len(sys.argv) < 4:
            print("用法: add <tag> <key1,key2,...>")
            return 2
        tag = sys.argv[2]
        keys = sys.argv[3]
        rows.append([tag, keys, time.strftime("%Y-%m-%d %H:%M:%S")])
        _write(rows)
        print("已登记: %s -> %s" % (tag, keys))
        return 0

    if cmd == "seed":
        pattern = sys.argv[2] if len(sys.argv) > 2 else "/tmp/prompt_*_n*.txt"
        return cmd_seed(pattern)

    if cmd == "pick":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        pool = sys.argv[3] if len(sys.argv) > 3 else "any"
        return cmd_pick(n, pool)

    if cmd == "stats":
        counts = _counts(rows)
        print("登记批次: %d" % len(rows))
        print("用过的条目: %d / 空间 %d / 露出位 %d" % (len(counts), len(SPACE_POOL), len(HOOK_POOL)))
        print("池子总量: 空间 %d + 露出位 %d = %d" % (len(SPACE_POOL), len(HOOK_POOL), len(SPACE_POOL) + len(HOOK_POOL)))
        return 0

    print("未知命令: %s" % cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main())
