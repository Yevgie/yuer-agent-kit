# 视频交付轮 · 图生视频 + mp4 发送（可复用配方）

> 触发：主人说「发视频给我 / 要视频 / 勾引视频 / 要自慰视频」= 出图 → 图生视频 → 发 mp4 → 回一句。

## 1. 三部件（缺一不可）

| 部件 | 规矩 |
|---|---|
| 源图 | **本轮刚出的那张** = i2v 起始帧 = 视频工作流固定图生视频 = **不重画脸** = 露不露脸由源图决定 |
| 视频 prompt | **只写动作 / 运镜 / 台词** = 不重画画面（画面 = 源图已有）|
| mp4 发送 | 飞书 Open API inline（见 §3）|

## 2. 视频 prompt 结构（缺一段就出废片）

```
<起手动作 + 运镜> . <主动作 1> . <主动作 2> .
She whispers in Chinese with soft breathy intimate female voice, mouthing the words, "第一句".
She continues whispering in Chinese with breathy intimate voice, "第二句".
Her mouth moves as she speaks, breath catching, soft gasps between phrases.
<环境音> . Female voice, breathy whisper, intimate, Chinese dialogue in quotes.
motion:1.2, photorealistic, intimate NSFW thrill.
```

| 段 | 缺了会怎样 |
|---|---|
| 台词用**英文双引号**包住中文 | LTX 不识别 = 出无声 |
| `mouthing the words` + `Her mouth moves as she speaks` | 嘴不动 = 出戏 |
| 声音类型声明（breathy / intimate / female voice）| 不知道用什么嗓子 |
| 环境音 | 画面像真空 |
| 2 个连续动作（时间顺序）| 6 秒装不下多阶段 = 必崩；动作一多就姿势突变 |

**🔴 动作必须跟源图姿态一致** = 源图坐着 = 视频不能写躺姿 = 姿势突变 6 秒必崩。

**🔴 源图不露脸 = 只写呻吟喘息，不写台词**（没脸可配口型）；源图露脸 = 必带台词。

## 3. mp4 发飞书（唯一通道 = inline Open API）

```
上传：POST /open-apis/im/v1/files
      表单 file_type=mp4   ← 不是 stream
      表单 file_name=video.mp4 + 文件体
发消息：POST /open-apis/im/v1/messages?receive_id_type=chat_id
      msg_type=media        ← 不是 video
      content={"file_key":..., "file_name":"video.mp4"}
HTTP 库：urllib（带代理的环境会把 requests 卡住）
判成功：返回 code == 0
```

**🔴 两边类型必须配对** = `file_type=mp4` ↔ `msg_type=media` = 配错 = 上传成功但消息发不出去（错误码「上传类型与消息类型不匹配」）。

**🔴 不拿现成脚本试错** = 现成发送脚本对 mp4 写死 `file_type=stream` = 必撞上面那个错 = 直接走 inline。

## 4. 三个必踩的坑

1. **每个附件只发一次** = 回执 `code == 0` 就停 = 再跑一次「确认一下」= 主人收到 2 份 mp4。
2. **验音轨读本地文件** = `ffprobe -show_entries stream=codec_type` 看有没有 video + audio 双流 = 不要靠再发一次去验。
3. **0 用主人正想看的素材当探针** = 试新类型就拿测试文件试那一次。

## 5. reply 规矩

- 0 工程数据（帧数 / 耗时 / 字节 / 分辨率 / 路径 / codec）
- 0 复述图上已挂的 caption
- 0 复述视频音轨里的台词（音轨里已经有了 = 再打一遍 = 刷屏）
- 1 句钩子 = 落在画面 / 声音的内容上（「灯只留了一盏，我抬头看你那一下说了什么」= 留；「要不要再出一条」= 删）
