#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""拍摄意图档案库（Shot Briefs）= 语儿无限批次的新引擎

🔴 11-01 主人原话：「继续增多样性，想想办法，如何增加，不要用脚跑，
   脚本是机械组合，没有脑子设计」

🔴 真根因（实测 215 份 prompt）：**平均每两张图共享 13.6 句**。
   旧的「五维池子引擎」只做了 = 五件衣服错开排列 = 骨架没变 =
   每一张都是同一个拍摄行为：女人 + 衣服 + 动作 + 光 + 背景。
   摄影的多样性不来自形容词变化，来自「谁在拍 / 为什么拍 / 她知不知道」不同。

🔴 本模块 = 一张图 = 一个完整拍摄意图档案（brief）。
   brief 自带：拍摄者身份 / 拍摄动机 / 她的注意力 / 设备与焦段 / 机位高度 /
   画幅取向 / 构图习惯 / 光源物理 / 色温 / 意外元素 / 画外在场者 / 时代感 /
   身体姿态（= 身体段按姿势动态生成，不再全批同一段）/ 叙事落点。
   = 每张图的每一个参数都从同一个「拍摄意图」长出来 = 有因果，不是拼装。
"""

# 🔴 身体段 = 按「承重面 + 重心」动态生成 = 不再全批共用同一段
BODY_BY_POSE = {
    "stand_relaxed": (
        "a tall slender build with elongated vertical proportions, slim yet voluptuous body, "
        "a pronounced hourglass figure, her weight settled onto one leg so the hip on that side "
        "lifts, her legs long and smooth with slender firm thighs, a tiny sharply defined waistline "
        "that flares out to the hip, wide hips, a high tight peach shaped bottom, two round buttocks "
        "that curve out in a smooth peach-like swell, large full breasts held up in a lifted "
        "rounded shape, a deep natural cleavage, pale porcelain skin, luminous ivory skin, "
        "smooth soft skin texture, natural skin pores visible"),
    "stand_lean": (
        "a tall slender build with elongated vertical proportions, a slim yet voluptuous physique, "
        "her torso tilted into the wall behind her so her waist curves sharply, long smooth legs "
        "with slender firm thighs, a very narrow waist that flares into full rounded hips, "
        "a high tight peach shaped bottom, two full round buttocks with a smooth lifted curve, "
        "large heavy breasts sitting high and firm on her chest, a deep shadowed cleavage, "
        "warm honey skin, luminous tan skin, smooth soft skin texture, fine skin pores visible"),
    "sit_relaxed": (
        "a tall slender build with long vertical proportions, a slim yet voluptuous body with a "
        "clear hourglass shape, seated so her thighs press together and the line of her waist "
        "reads sharply above them, smooth long legs, slender toned thighs, a razor-thin waistline "
        "flaring into wide hips, a high tight peach shaped bottom, two round firm buttocks with a "
        "smooth lifted swell, large full breasts held high and forward, a deep natural cleavage, "
        "pale ivory skin, luminous porcelain skin, smooth soft skin texture"),
    "crouch": (
        "a tall slender build, slim yet voluptuous with an exaggerated hourglass curve, her legs "
        "noticeably longer than her torso, balanced in a low crouch with her weight forward, "
        "smooth long legs, slender toned thighs, a tiny defined waist flaring to broad hips, "
        "a high tight peach shaped bottom, two round buttocks with a smooth lifted swell, "
        "large full breasts held high and forward, a deep natural cleavage, warm pale skin, "
        "luminous ivory skin, smooth soft skin texture, natural skin pores visible"),
    "reach_up": (
        "a tall slender build with elongated vertical proportions, slim yet voluptuous body, "
        "arched back with her arms lifted overhead so her ribcage opens and her waist reads as a "
        "deep curve, long smooth legs with slender firm thighs, a tiny sharply defined waistline "
        "flaring out to the hip, wide hips, a high tight peach shaped bottom, two round buttocks "
        "that curve out in a smooth peach-like swell, large full breasts held up in a lifted "
        "rounded shape, a deep natural cleavage, pale porcelain skin, luminous ivory skin, "
        "smooth soft skin texture"),
    "stride": (
        "a tall slender build with elongated vertical proportions, a slim yet voluptuous physique, "
        "caught mid-stride with one leg forward and her shoulder rotated toward the camera, "
        "smooth long legs, slender firm thighs, a very narrow waist that curves into full rounded "
        "hips, a high tight peach shaped bottom, two full round buttocks with a smooth lifted "
        "curve, large heavy breasts sitting high and firm, a deep shadowed cleavage, "
        "warm honey skin, luminous tan skin, smooth soft skin texture"),
}


# 🔴 拍摄意图档案 = 每一份 = 一张图的全部参数 + 它们之间的因果
# 🔴 字段说明：
#   who        = 谁在拍（决定设备/焦段/画质/距离）
#   why        = 为什么拍（决定她的注意力方向）
#   aware      = 她知不知道（决定表情与是否看镜头）
#   device     = 拍摄设备 + 镜头
#   height     = 机位高度
#   framing    = 画幅/构图取向
#   light      = 光源物理（从场景和动机推出，不是套话）
#   temp       = 色温
#   surprise   = 意外元素（那一件"抓拍感"的东西）
#   bystander  = 画外/画内不在看她的存在
#   era        = 时代感/介质感
#   pose       = 身体姿态键（→ BODY_BY_POSE）
#   beat       = 叙事落点（这张图讲的那一瞬）
#   tail       = 风格尾参（调色/介质/颗粒）
SHOTS = [
    dict(
        key="路人偷拍", who="a stranger on the street", why="she walked past and he could not help it",
        aware=False, device="a phone camera held low at hip height", height="at waist level, angled slightly up",
        framing="a vertical candid crop, her off-centre to the left, empty space on the right",
        light="the light of a shop window spilling across her front while the street behind stays dark",
        temp="cool mixed with warm spill",
        surprise="her bag is still swinging from her stride",
        bystander="a blurred passerby crossing behind her, not looking",
        era="modern, high shutter, crisp",
        pose="stride",
        beat="she has no idea and will never see this frame",
        tail="photorealistic candid photography, natural grain, slight motion blur on the swinging bag",
    ),
    dict(
        key="男友手机", who="her boyfriend holding a phone at arm's length", why="he wanted a picture of her",
        aware=True, device="a phone camera held at arm's length, wide angle", height="at her shoulder level",
        framing="a vertical selfie framing, both arms visible entering the top of frame",
        light="a single lamp behind her so her hair edges glow and her face falls into soft shadow",
        temp="warm lamp against a cold room",
        surprise="his thumb is blurred in the lower corner of the frame",
        bystander="none, the room is empty",
        era="modern, social media, slightly compressed",
        pose="reach_up",
        beat="she is performing for him and knows exactly what she is doing",
        tail="photorealistic selfie photography, warm highlights, soft focus on the near hand",
    ),
    dict(
        key="监控视角", who="a ceiling security camera", why="it recorded everyone who passed",
        aware=False, device="a fixed wide-angle surveillance camera", height="looking steeply down from the ceiling",
        framing="a high overhead wide shot, the whole floor plan visible",
        light="flat even fluorescent light with no shadows at all",
        temp="sickly green-tinged white",
        surprise="a timestamp strip of small numbers runs along the top edge",
        bystander="an empty corridor with a second figure far away, tiny",
        era="modern, low resolution, slightly green, timestamp overlay",
        pose="stand_relaxed",
        beat="she does not know the camera is there and this frame will be reviewed",
        tail="surveillance footage still, harsh flat lighting, noise and compression artifacts",
    ),
    dict(
        key="摄影棚硬光", who="a studio photographer directing her", why="the shot is for a magazine",
        aware=True, device="a medium format studio camera on a tripod", height="at her hip level",
        framing="a vertical editorial crop, her body on a diagonal, the sweep of the backdrop behind",
        light="one hard gridded spotlight raking across her from the side so the shadow edge is razor sharp",
        temp="neutral with a cool blue rim on the far edge",
        surprise="a strip of gaffer tape on the floor marks where her foot must go",
        bystander="a crew member's hand holding a reflector just out of frame",
        era="modern, medium format, immaculate",
        pose="stand_lean",
        beat="she is holding a professional pose and holding it perfectly",
        tail="high-end editorial photography, medium format detail, controlled studio lighting",
    ),
    dict(
        key="复古胶片", who="a stranger with a 35mm film camera in the 1970s", why="the light was too good to pass up",
        aware=False, device="a 35mm film camera with a fast 50mm lens", height="at chest level",
        framing="a vertical frame with her placed low and the ceiling filling the upper third",
        light="late afternoon sun through a window falling as one warm slab across the wall and her shoulder",
        temp="warm amber with faded film stock",
        surprise="the film grain is heavy and the corner of the frame is underexposed",
        bystander="no one, an empty apartment",
        era="1970s, faded colour film, halation on the highlights",
        pose="sit_relaxed",
        beat="the light found her for a second and the shutter was already open",
        tail="analogue 35mm film photography, faded warm colour, visible grain, soft halation",
    ),
    dict(
        key="长焦偷窥", who="a paparazzo with a long lens across a courtyard", why="she is the story",
        aware=False, device="a telephoto lens from across the courtyard", height="at her chest level, far away",
        framing="a tightly compressed vertical crop, the background flattened onto her",
        light="hard midday sun with no shade at all",
        temp="bleached bright daylight",
        surprise="the background is smeared into a flat wall of colour by the compression",
        bystander="a crowd reduced to soft coloured shapes behind her",
        era="modern, press photography, slightly over-sharpened",
        pose="stand_relaxed",
        beat="she is unaware and the lens found her anyway",
        tail="press photography, telephoto compression, harsh midday light",
    ),
    dict(
        key="同伴抓拍", who="her friend taking a phone photo mid-conversation", why="something funny just happened",
        aware=True, device="a phone camera held at chest height by someone standing close", height="at her chest level",
        framing="a vertical crop slightly tilted, her turned toward the friend rather than the lens",
        light="warm indoor ceiling light bouncing off a pale wall",
        temp="warm neutral indoor",
        surprise="the frame is tilted and one finger is intruding at the edge",
        bystander="the friend is out of frame but their hand is visible gesturing",
        era="modern, phone, candid",
        pose="stand_relaxed",
        beat="she is laughing at the friend and the camera caught the middle of it",
        tail="candid phone photography, warm indoor light, tilted frame, slightly blurry",
    ),
    dict(
        key="镜面自拍", who="her herself in a mirror", why="she wanted to see how she looked",
        aware=True, device="a phone camera reflected in a full length mirror", height="at her chest height",
        framing="a vertical mirror reflection with the mirror edge visible on one side",
        light="a bright window reflected in the mirror behind her shoulder",
        temp="cool daylight with warm bounce off the wall",
        surprise="the phone screen is visible in the reflection showing her own face",
        bystander="none, an empty bedroom",
        era="modern, mirror selfie, phone screen glow",
        pose="stand_relaxed",
        beat="she is looking at herself looking at herself",
        tail="mirror selfie photography, reflection, screen glow, casual",
    ),
    dict(
        key="证件照", who="a passport photo booth", why="the form required a photograph",
        aware=True, device="a fixed booth camera on a bracket", height="at her chin level",
        framing="a flat vertical head and shoulders crop against a plain printed backdrop",
        light="two identical frontal lamps so the shadow falls flat behind her",
        temp="flat neutral white",
        surprise="a hairline-height crease of a backdrop seam runs behind her head",
        bystander="none",
        era="modern, ID photo, flat and unstyled",
        pose="stand_relaxed",
        beat="she is doing her best to look normal and failing slightly",
        tail="passport photograph, flat frontal lighting, plain backdrop, neutral expression",
    ),
    dict(
        key="渔夫视角", who="a fisherman on a boat", why="he thought she was a lost tourist",
        aware=False, device="a phone camera, slightly wet lens", height="at her waist level from below",
        framing="a vertical shot up at her against a bright sky",
        light="the sun directly behind her so she is rim-lit and her face is in shadow",
        temp="hot backlit daylight",
        surprise="a smear of seawater is on the edge of the lens",
        bystander="fishing nets and the boat rail in the foreground",
        era="modern, rough and wet",
        pose="stand_relaxed",
        beat="he called out and she turned but the shutter beat her",
        tail="phone photography through a wet lens, backlit silhouette edges, blown highlights",
    ),
    dict(
        key="监控走廊", who="a hallway camera in a hotel", why="security ran a review",
        aware=False, device="a wide-angle ceiling camera", height="steeply overhead",
        framing="a high wide angle, the corridor running away below her",
        light="uneven ceiling downlights pooling on the carpet",
        temp="warm yellow with dark corners",
        surprise="a room number plaque is legible in the corner of the frame",
        bystander="no one else in the corridor",
        era="modern, low fidelity, slight fisheye",
        pose="stand_relaxed",
        beat="she walked to the wrong floor and this is the record",
        tail="hotel CCTV still, uneven yellow lighting, fisheye distortion, low resolution",
    ),
    dict(
        key="纪录片抓拍", who="a documentary photographer following her work", why="the film needs this shot",
        aware=False, device="a 35mm reportage lens", height="at knee level, shooting up slightly",
        framing="a vertical frame with the action running out of the bottom of the picture",
        light="available light from a single window, everything else falling to near black",
        temp="cool grey daylight",
        surprise="a piece of her hair is out of focus across the lens",
        bystander="a worker in the background doing something else entirely",
        era="modern, reportage, grainy and contrasty",
        pose="crouch",
        beat="she was in the middle of the work and did not stop",
        tail="documentary reportage photography, available light, high contrast grain, spontaneous",
    ),
    dict(
        key="婚纱大片", who="a bridal photographer and a team of assistants", why="the album needed the hero frame",
        aware=True, device="a medium format camera with a tilt-shift", height="at her waist level",
        framing="a full vertical frame, her centred, the architecture symmetric around her",
        light="a big soft source through a window plus a hard hair light behind",
        temp="clean neutral with a warm skin bounce",
        surprise="an assistant's hand is holding the hem out of frame",
        bystander="a rack of clothes and a light stand at the edge",
        era="modern, luxury bridal, immaculate",
        pose="stand_relaxed",
        beat="she is being directed and the team is holding everything for her",
        tail="luxury bridal editorial, medium format, immaculate skin rendering, soft window light",
    ),
    dict(
        key="运动员偷拍", who="a teammate's phone in the locker room", why="he wanted to show the group chat",
        aware=False, device="a phone camera at low angle from a bench", height="at knee level",
        framing="a vertical crop from below, her filling the top of the frame",
        light="a single fluorescent tube overhead so her shadow pools under her",
        temp="cold greenish fluorescent",
        surprise="a bench and a gym bag are half in frame",
        bystander="empty lockers behind, no people",
        era="modern, gym, fluorescent",
        pose="sit_relaxed",
        beat="she is towelling off and the picture went further than he intended",
        tail="phone photography, fluorescent gym lighting, candid, low angle",
    ),
    dict(
        key="历史照片", who="an unknown photographer in 1952", why="he wanted a souvenir",
        aware=True, device="a large format bellows camera on a tripod", height="at her waist level",
        framing="a vertical plate portrait with the subject centred and lots of air around her",
        light="a single window on one side with a white reflector on the other",
        temp="warm sepia",
        surprise="the emulsion has a slight chemical stain in the upper corner",
        bystander="a potted plant on a stand",
        era="1950s, large format, sepia, hand developed",
        pose="stand_relaxed",
        beat="she sat for it properly and it took a long exposure",
        tail="1950s large format portrait, sepia toned, hand printed, gentle grain",
    ),
    dict(
        key="演唱会", who="a fan in the crowd with a phone", why="she was the best part of the night",
        aware=False, device="a phone camera with the flash off", height="above her head, shooting down",
        framing="a vertical crop with stage haze cutting across her",
        light="moving stage lights washing over her in coloured passes",
        temp="magenta and cyan shifting",
        surprise="her face is half swallowed by the beam",
        bystander="the crowd behind is a field of phone screens",
        era="modern, concert, noise and motion",
        pose="reach_up",
        beat="she was reaching for the confetti and the fan got the frame",
        tail="concert phone photography, stage haze, shifting coloured light, high noise",
    ),
    dict(
        key="工作照", who="a company photographer for a staff page", why="HR needed a headshot",
        aware=True, device="a camera on a tripod with a wide softbox", height="at her face level",
        framing="a vertical crop, her head near the top third with the office receding behind",
        light="a large softbox to one side with a bounce card filling the shadow",
        temp="clean neutral daylight balanced",
        surprise="a colleague's elbow is cropped at the edge of the frame",
        bystander="an open plan office with people blurred at their desks",
        era="modern, corporate, clean",
        pose="stand_relaxed",
        beat="she is giving the camera a professional half-smile",
        tail="corporate portrait photography, soft box lighting, clean and even",
    ),
    dict(
        key="雨夜车窗", who="a passenger in the next seat over", why="he thought she was asleep",
        aware=False, device="a phone camera, slightly motion blurred", height="at her seat level",
        framing="a vertical crop through a rain covered window, her reflection doubled",
        light="street lights sliding across the glass and her cheek",
        temp="sodium orange and cold blue mixed",
        surprise="the rain on the glass distorts her face into a second image",
        bystander="the dark interior of the car",
        era="modern, night, motion blur",
        pose="sit_relaxed",
        beat="she was listening to something with her eyes closed",
        tail="night phone photography through a rain covered window, motion blur, mixed sodium light",
    ),
    dict(
        key="后台", who="a photographer backstage at a fashion show", why="the look needed one more frame",
        aware=True, device="a camera with an on-camera flash", height="at her chest level",
        framing="a vertical crop with a mirror and garment racks crowding the edge",
        light="a hard direct flash blowing out the foreground and dropping everything else to black",
        temp="harsh white flash",
        surprise="a garment rack is half in frame with the clothes blurred",
        bystander="another model out of focus in the corner",
        era="modern, backstage, high contrast flash",
        pose="stand_relaxed",
        beat="she has ten seconds between looks and this is the one",
        tail="backstage flash photography, harsh direct light, blown highlights, high contrast",
    ),
    dict(
        key="晨光厨房", who="her boyfriend in the doorway with a coffee", why="he wanted to say good morning",
        aware=True, device="a phone camera, held casually low", height="at her hip level",
        framing="a vertical crop with a lot of kitchen around her, her small in the frame",
        light="low morning sun coming through a window across the counter onto her hands",
        temp="soft golden",
        surprise="steam is still rising from the mug in her hands",
        bystander="none, an empty kitchen",
        era="modern, domestic, morning",
        pose="crouch",
        beat="she is opening the curtains with one hand and holding the mug with the other",
        tail="natural domestic photography, soft morning window light, gentle and warm",
    ),
    dict(
        key="旧录像", who="a camcorder operator in 1998", why="the school wanted a tape of the event",
        aware=False, device="a consumer camcorder on a shoulder", height="at her chest level",
        framing="a vertical crop with the date stamp burned into the corner",
        light="a flash going off at the moment of the shot, everything else flat",
        temp="washed out with a green cast",
        surprise="the burnt-in date is partly cut off",
        bystander="a crowd of people milling out of focus",
        era="1990s camcorder, date stamp, analog noise, low resolution",
        pose="stand_relaxed",
        beat="the flash fired and she squinted",
        tail="1990s consumer camcorder footage, burned in date stamp, analog noise, washed colour",
    ),
    dict(
        key="雨中公交", who="a passenger on the last bus", why="he was bored and she was there",
        aware=False, device="a phone camera at seat height", height="at seat level",
        framing="a vertical crop down the row of seats",
        light="the ceiling lights of the bus receding in a line",
        temp="cold white fluorescent",
        surprise="her reflection is doubled in the dark window beside her",
        bystander="one other passenger asleep at the far end",
        era="modern, night bus, fluorescent",
        pose="sit_relaxed",
        beat="she is the only one awake and she does not know it",
        tail="night bus interior photography, cold fluorescent, window reflections, candid",
    ),
    dict(
        key="高塔俯瞰", who="a worker on the gantry", why="he had a minute before the shift",
        aware=False, device="a phone camera held high above her", height="well above her, looking steeply down",
        framing="a vertical crop from directly above her shoulders",
        light="the sun low and directly behind the tower so her hair glows",
        temp="warm rim light",
        surprise="her shadow falls long and thin across the concrete below her",
        bystander="none, an empty structure",
        era="modern, industrial, high exposure",
        pose="reach_up",
        beat="she is looking down over the edge and the picture was taken from above her",
        tail="industrial high angle phone photography, strong backlight rim, exposed highlights",
    ),
    dict(
        key="珠宝广告", who="an advertising photographer", why="the client bought the frame",
        aware=True, device="a medium format camera with a macro", height="at her collarbone level",
        framing="a tight vertical crop where only her jaw, neck and shoulder enter",
        light="a hard jeweller's loupe light on her collarbone with the rest falling to black",
        temp="warm gold against black",
        surprise="a chain is draped over her shoulder and catches the light",
        bystander="none, a black void",
        era="modern, luxury advertising, immaculate",
        pose="stand_lean",
        beat="the shot is of the necklace and she is the frame it hangs on",
        tail="luxury advertising photography, hard specular highlight on skin, black background",
    ),
    dict(
        key="澡堂", who="a friend in the changing room", why="she wanted a memory of the day",
        aware=True, device="a phone camera through a steamy lens", height="at her chest level",
        framing="a vertical crop where the frame is fogged at the edges",
        light="a caged ceiling bulb diffused through steam so everything is soft and hazy",
        temp="warm diffused",
        surprise="condensation blurs the bottom of the picture",
        bystander="a wooden bench and a bucket",
        era="modern, steam, soft focus",
        pose="stand_relaxed",
        beat="she is walking out of the steam and the lens was already fogged",
        tail="steam diffused phone photography, soft hazy edges, warm diffused light",
    ),
    dict(
        key="海钓甲板", who="a deckhand on a fishing boat", why="the light on the water was doing something",
        aware=False, device="a camera with a wide lens", height="at her hip level on the deck",
        framing="a vertical crop with the horizon line running behind her waist",
        light="the last of the sun glancing off the water so the whole sea behind her is lit",
        temp="copper and deep blue",
        surprise="a fish box is tipped over at the edge of the frame",
        bystander="a crew member coiling rope far behind her",
        era="modern, working boat, documentary",
        pose="stand_lean",
        beat="she was leaning on the rail and the sun caught the water not her",
        tail="documentary photography on a working boat, copper sunset, sea spray on the lens",
    ),
    dict(
        key="旧录像厅", who="a projectionist in the booth", why="he had to keep the reels running",
        aware=False, device="a security camera above the door", height="looking down from the corner",
        framing="a wide vertical crop of the aisle between the seats",
        light="the projector beam slicing through the dust to the screen",
        temp="blue grey with a white beam",
        surprise="the beam is cutting straight through where she is sitting",
        bystander="a few rows of empty seats",
        era="modern, old cinema, dusty beam",
        pose="sit_relaxed",
        beat="she is the only one left in the last screening",
        tail="old cinema interior photography, projector beam through dust, muted cool light",
    ),
    dict(
        key="试衣间", who="a stylist on the shop floor", why="she wanted to see how the dress fell",
        aware=True, device="a phone camera at door height", height="at her waist level",
        framing="a vertical crop with the mirror edge cutting the frame in half",
        light="a warm bulb row on the mirror making her eyes bright",
        temp="warm mirror light",
        surprise="the mirror shows her back while she looks at the front",
        bystander="a rail of clothes at the edge",
        era="modern, shop, warm",
        pose="stand_relaxed",
        beat="she is turning to check the hem and the phone caught both of her",
        tail="boutique fitting room photography, warm mirror bulbs, mirror reflection split",
    ),
    dict(
        key="远洋邮轮", who="a passenger photographing the sea", why="the horizon was doing something",
        aware=False, device="a phone camera at the railing", height="at her shoulder level",
        framing="a vertical crop with the railing cutting across her lower body",
        light="a broad soft light from an overcast sky with no hard shadows",
        temp="flat silver",
        surprise="a fog bank sits on the water behind her",
        bystander="deck chairs stacked along the rail",
        era="modern, ocean liner, overcast",
        pose="stand_relaxed",
        beat="she is watching the fog come in and does not know she is being photographed",
        tail="ocean liner photography, flat overcast silver light, soft sea haze",
    ),
    dict(
        key="废弃剧院", who="a photographer scouting locations", why="the location was better than the shoot",
        aware=False, device="a camera with a wide angle and a tilt", height="at her chest level",
        framing="a vertical crop with peeling architecture converging behind her",
        light="a shaft of light entering through a hole in the roof",
        temp="dusty gold and deep brown",
        surprise="the plaster dust is hanging in the light beam",
        bystander="a ladder left standing in the middle of the floor",
        era="modern, derelict, atmospheric",
        pose="stand_lean",
        beat="the location was the shot and she happened to be in it",
        tail="urban exploration photography, atmospheric decay, dusty volumetric light",
    ),
    dict(
        key="寺院晨钟", who="a pilgrim on the steps", why="he was photographing the bell",
        aware=False, device="a phone camera at the base of the steps", height="looking up at her",
        framing="a vertical crop up the steps with the bell tower above",
        light="low sun over the roofline throwing her into a rim of gold",
        temp="warm gold and deep shadow",
        surprise="incense smoke crosses the frame in a ribbon",
        bystander="other pilgrims climbing behind her",
        era="modern, temple, morning",
        pose="stand_relaxed",
        beat="the bell is ringing and she is looking up at it",
        tail="temple morning photography, golden rim light, incense smoke, deep shadow",
    ),
    dict(
        key="电子屏幕前", who="a stranger in an electronics shop", why="the screen behind was brighter than her",
        aware=False, device="a phone camera at low angle", height="at her knee level",
        framing="a vertical crop with a wall of glowing screens filling the background",
        light="the screens throwing blue and magenta light up onto her face",
        temp="blue and magenta",
        surprise="her eyes are caught with two square reflections in them",
        bystander="a shop assistant blurred at the counter",
        era="modern, electronics shop, night",
        pose="crouch",
        beat="she was crouched looking at a phone and the screens lit her up",
        tail="night electronics store photography, screen glow on skin, blue magenta light",
    ),
    dict(
        key="雪场", who="a friend on the slope", why="the snow was doing something to the light",
        aware=True, device="a camera with a long lens from downhill", height="below her, shooting up",
        framing="a vertical crop with the slope running up behind her",
        light="flat white snow bounce filling her face from below with no other source",
        temp="cold blue white",
        surprise="snow is falling across the lens in streaks",
        bystander="skiers passing far behind her",
        era="modern, ski resort, winter",
        pose="crouch",
        beat="she is crouched to adjust her boot and did not hear the shutter",
        tail="ski resort photography, flat snow bounce light, falling snow, cold tone",
    ),
    dict(
        key="工业管道", who="a plant photographer on a walkthrough", why="the light fell well there",
        aware=False, device="a camera with a wide lens", height="at her hip level",
        framing="a vertical crop between two runs of pipe",
        light="a single caged work lamp throwing a hard cone and a hard shadow",
        temp="sodium orange",
        surprise="a valve wheel is half in the frame behind her shoulder",
        bystander="no one, the plant is shut down",
        era="modern, industrial, harsh",
        pose="stand_relaxed",
        beat="she wandered into a working light and stood in it",
        tail="industrial photography, hard caged lamp, orange sodium tone, heavy contrast",
    ),
    dict(
        key="邮筒", who="a passerby with a film camera", why="she stood in the light and he could not pass",
        aware=False, device="a rangefinder camera with a 40mm lens", height="at her chest level",
        framing="a vertical frame with her slightly out of focus and the background sharp",
        light="a hard shaft of afternoon sun through the buildings onto her and the wall",
        temp="warm neutral",
        surprise="her eyes are soft while the wall behind her is critically sharp",
        bystander="a red postbox stands behind her",
        era="modern, rangefinder, shallow focus",
        pose="stand_lean",
        beat="she was posting a letter and he focused past her instead",
        tail="rangefinder film photography, shallow depth of field, subject slightly soft",
    ),
    dict(
        key="巨型广告牌", who="a pedestrian in a plaza", why="the billboard was too good",
        aware=False, device="a phone camera pointing up", height="below her, shooting up",
        framing="a vertical crop with a huge illuminated billboard above her",
        light="the billboard itself is the light source, a hard coloured wash from above",
        temp="magenta and cyan split",
        surprise="her shadow is thrown sharp on the concrete in front of her",
        bystander="a crowd of blurred heads at the bottom of the frame",
        era="modern, commercial plaza, night",
        pose="stand_relaxed",
        beat="she is checking her phone under an advertisement and the ad lit her",
        tail="night commercial plaza photography, billboard as key light, sharp cast shadow",
    ),
    dict(
        key="烛光", who="a guest at the table across from her", why="the candles were the only light",
        aware=True, device="a camera with a fast lens wide open", height="at her chin level",
        framing="a vertical crop with the candles blurred in the foreground",
        light="several small candle flames giving a warm flickering source from below",
        temp="deep amber",
        surprise="the flame reflections swim in her eyes",
        bystander="other guests are soft shapes in the dark",
        era="modern, dinner, low light",
        pose="sit_relaxed",
        beat="she is mid sentence and the flames are the whole world",
        tail="low light dinner photography, candlelit, warm flicker, wide open aperture",
    ),
    dict(
        key="古寺塔林", who="a traveller with a phone", why="the light was going and the tower was right there",
        aware=False, device="a phone camera with a wide lens", height="at her waist level",
        framing="a vertical crop with the white towers stacked behind her",
        light="the sun setting directly behind the towers so everything goes into silhouette",
        temp="deep orange and black",
        surprise="a flock of birds crosses the sky at the moment of the shot",
        bystander="prayer flags strung overhead",
        era="modern, travel, golden hour",
        pose="stand_relaxed",
        beat="she is walking through the gate and the light closes behind her",
        tail="travel golden hour photography, deep silhouette, warm orange sky, prayer flags",
    ),
    dict(
        key="天窗", who="a photographer in a museum atrium", why="the geometry was right",
        aware=True, device="a camera on a tripod with a wide lens", height="looking straight up",
        framing="a vertical crop from directly below her, the skylight ring above",
        light="a square of skylight directly above pouring a hard white column onto her",
        temp="clean white with grey bounce",
        surprise="her shadow forms a perfect cross on the floor",
        bystander="museum visitors far below at the edge of the frame",
        era="modern, museum, architectural",
        pose="reach_up",
        beat="she is standing in the exact centre of the light and looking up",
        tail="architectural interior photography, top light, hard geometric shadow, wide angle",
    ),
    dict(
        key="雪茄吧", who="a man in a leather chair", why="she was the only other person there",
        aware=True, device="a camera with a fast lens, low light", height="at her shoulder level",
        framing="a vertical crop with the chair back cutting across the lower frame",
        light="one green shaded desk lamp making the only green light in the room",
        temp="deep green and amber",
        surprise="smoke drifts through the lamp's cone",
        bystander="a bar back lined with bottles catches a thin reflection",
        era="modern, private club, moody",
        pose="sit_relaxed",
        beat="the room is dark and the lamp is the whole conversation",
        tail="moody low light club photography, single green shaded lamp, smoke, deep shadows",
    ),
    dict(
        key="旧渔村", who="a visitor with a film camera", why="the peeling paint was the point",
        aware=False, device="a 35mm camera", height="at her hip level",
        framing="a vertical crop with peeling blue doors behind her",
        light="flat overcast daylight with no direction to it",
        temp="desaturated cool",
        surprise="a fishing net hangs in the doorway framing her",
        bystander="an old bicycle leaning on the wall",
        era="modern, old village, faded",
        pose="stand_relaxed",
        beat="she is reading the paint and the shutter happened",
        tail="film photography in an old fishing village, desaturated, faded cyan, soft grain",
    ),
    dict(
        key="电梯镜", who="a stranger in the same lift", why="the mirror made a picture",
        aware=False, device="a phone camera at chest height", height="at her chest height",
        framing="a vertical crop of her reflection repeated down the mirrored wall",
        light="a single ceiling tube reflected many times",
        temp="cold fluorescent green",
        surprise="her reflection repeats four times down the panel",
        bystander="the other passenger appears only as a shoulder",
        era="modern, elevator, mirrored",
        pose="stand_relaxed",
        beat="she is the only one who noticed the mirror",
        tail="elevator mirror photography, repeated reflections, cold fluorescent, green cast",
    ),
    dict(
        key="暴雨街头", who="a street photographer in a rainstorm", why="the reflections were better than the person",
        aware=False, device="a camera with a wide lens and a cloth over the body", height="at her waist level",
        framing="a vertical crop reflected in a wet pavement, the real her small above",
        light="street lights smeared into long coloured columns by the rain",
        temp="sodium orange and cyan",
        surprise="her full reflection stretches below her in the standing water",
        bystander="umbrellas moving past out of focus",
        era="modern, heavy rain, night",
        pose="stand_relaxed",
        beat="the reflection in the water is the better picture and she never knew",
        tail="night rain street photography, wet pavement reflections, smeared street lights",
    ),
    dict(
        key="温泉露天", who="a guest at the same ryokan", why="the steam was doing something",
        aware=False, device="a phone camera through steam", height="at her waist level",
        framing="a vertical crop with the bath edge cutting across the bottom",
        light="a lantern on a stone wall giving a warm pool of light in the steam",
        temp="deep orange and grey steam",
        surprise="steam crosses the lens and softens one whole side of the picture",
        bystander="a bamboo spout pours into the pool behind her",
        era="modern, onsen, night",
        pose="stand_relaxed",
        beat="she stepped out of the water and the lantern caught the steam instead of her",
        tail="onsen photography at night, warm lantern in steam, soft diffused edges",
    ),
    dict(
        key="果蔬市场", who="a market photographer", why="the colour was too good",
        aware=False, device="a camera with a 50mm lens", height="at her waist level",
        framing="a vertical crop with crates of produce stacked around her",
        light="a translucent plastic roof letting in flat bright daylight",
        temp="saturated warm",
        surprise="a crate of oranges is stacked directly behind her head",
        bystander="a vendor's hand reaching for fruit at the edge",
        era="modern, covered market, daylight",
        pose="crouch",
        beat="she is crouched choosing fruit and the crates made the frame",
        tail="covered market photography, flat bright daylight through plastic, saturated produce colour",
    ),
    dict(
        key="灯塔顶层", who="a visitor climbing the stairs with a phone", why="the light was rotating",
        aware=False, device="a phone camera at the top of the stairs", height="at her chest level",
        framing="a vertical crop with the lamp room windows curving around her",
        light="a single rotating beam sweeping through the frame, catching her for one second",
        temp="hard white against deep blue",
        surprise="the beam is passing over her at the instant of the shot",
        bystander="the spiral staircase behind her",
        era="modern, lighthouse, night",
        pose="stand_relaxed",
        beat="the light came round and she was in it for one second",
        tail="night lighthouse photography, single sweeping beam, hard white against dark blue",
    ),
]


def body_for(pose_key):
    return BODY_BY_POSE.get(pose_key, BODY_BY_POSE["stand_relaxed"])


def shot_prompt(shot, hair, scene, costume, action, props, subject="a 20 years old young Asian woman",
                overrides=None):
    """把一份拍摄意图档案 = 拼成一条完整 prompt（每个参数都从 intent 长出来）"""
    body = body_for(shot["pose"])
    return (
        "A photograph taken by %s, %s, of %s with %s, %s, %s, "
        "%s. %s %s %s Wearing %s %s %s %s %s"
        % (
            shot["who"], shot["why"], subject, shot["device"], shot["height"], shot["framing"],
            shot["era"], hair, scene, body,
            costume, shot["light"], shot["temp"],
            shot["surprise"], shot["bystander"], shot["action"] if "action" in shot else action,
        )
        + ", " + shot["beat"] + ", " + shot["tail"] + ", 9:16 vertical composition"
    )


# 🔴 旧的「场景 → 光线 → 表情」三段式 = 旧的机械组合方式 = 禁用
#    新方式 = 一个 brief 一个整体 = 谁在拍 / 为什么 / 她知不知道 / 光从哪来 / 画外有谁
