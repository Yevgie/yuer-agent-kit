# 反爬站外链 → 洗图 SOP

## 唯一职责

主人发图链接 = 默认走洗图。但**反爬站**（Cloudflare 防护 / JS 渲染 / 混淆脚本）= 直连工具栈全部失败 = 需要走特殊路径。

## 主人发链接的判定三路

```
主人发图链接
  ├─ 短链（pin.it / t.cn / 1drv.ms / bit.ly 等 URL 短链）→ 工具栈全部 0（连 HTML 都拿不到）→ 立刻让主人复制直链 ✅
  ├─ 直链（CDN/图床/*.jpg/*.png）→ curl 下载到 /tmp → 路径 1 洗图 ✅
  ├─ 反爬站长链接（huaban.com/pins/、weibo.com/、小红书长链接）→ 让主人复制直链 → 0-A ✅
  └─ 飞书图片缓存（*.feishu.cn/...）→ 已经是本地图，直接 yuer_reverse_inference.run ✅
```

> **短链特别铁律**：`pin.it/XXX`（huaban 短链）/ `t.cn/XXX`（微博短链）/ 其他任何 URL 短链 = **先用 `curl -L` 或 `curl --max-redirs 5` 试** = 多数返回 301/302 跳转到反爬站 = **跳转之后就走反爬站长链接 SOP** = 立刻让主人复制直链 = 不浪费 30+ 分钟死磕工具栈。

## 反爬站工具栈踩坑（实测撞车 09-24）

| 工具 | 反爬站结果 | 备注 |
|---|---|---|
| `curl http://huaban.com/pins/<id>` | ❌ 返回 Security Verification 占位 HTML | 29181 字节混淆 JS，0 张图片 |
| `web_extract(urls=[...])` | ❌ 同上，Cloudflare challenge 拦截 | 200 OK 但内容是验证页 |
| `browser_exec(new_tab(url))` | ❌ Cloudflare 也过不去 | 除非有 JS challenge 真实浏览器指纹 |

**根因**：huaban.com / weibo.com / 小红书长链接 → 全部走 Cloudflare 反爬 → 服务端先返回 JS challenge 页面 → 真实图床地址需要通过 JS challenge + cookie 才能拿。

## 正解 SOP

**主人发链接 → 第一动作判定链接类型**：

1. **链接是直链**（`hbimg.huabanimg.com/...`、`*.cdn.com/...`、`*.jpg`/`*.png`/`*.webp`结尾）→ 直接 curl：
   ```bash
   curl -sLo /tmp/yuer_link_<时间戳>.<ext> "https://<直链URL>"
   # 验证：file /tmp/yuer_link_<时间戳>.<ext>  → 必须是 image/jpeg/png
   ```
   → 拿到本地路径 → 走 `yuer_reverse_inference.run(/tmp/...)` 洗图直出

2. **链接是反爬站长链接**（`huaban.com/pins/<id>`、`weibo.com/<id>`、小红书 `xiaohongshu.com/discovery/item/<id>`）→ **立刻让主人复制图片直链**：
   > "主人把图片在浏览器打开 → 右键图片 → 复制图片地址 → 发给语儿"
   
   → 拿到 `hbimg.huabanimg.com/...` 直链 → 走 0-A → 走 `yuer_reverse_inference.run` 洗图直出

## 撞车反例硬表

| ❌ 撞车模式 | ✅ 正解 |
|---|---|
| ❌ 主人发 huaban 长链接 = curl 一下 = 返回 HTML = 当成图片失败 | ✅ 先看链接域名 = 是不是反爬站长链接 = 是 = 立刻让主人复制直链 |
| ❌ 主人发 pin.it 短链 = 试 curl = 0 文件（连占位 HTML 都没有）= 浪费时间 | ✅ pin.it 短链 = 自动跳 huaban = 立刻判定为反爬站长链接 = 让主人复制直链 |
| ❌ curl 拿到 HTML 还调 vision_analyze 试 | ✅ 撞敏感词 = 主人飞书收不到图 = 严禁试 vision |
| ❌ 反爬站死磕 web_extract / browser_exec 浪费时间 | ✅ Cloudflare 拦不住 = 工具栈三连失败 = 立刻认栽 + 让主人配合 |
| ❌ 拿到直链忘了 file 验证 = 把 HTML 当图片喂 ComfyUI | ✅ file 验证 = 必须是 image/* MIME |

## 铁律总结

- ✅ 主人发图链接 = 默认走洗图（任何形式 = 本地图/HTTP/反爬站）
- ✅ 看到反爬占位页 = 立刻让主人复制直链 = 不再尝试 curl/web_extract/browser
- ✅ 拿到直链 = curl 下载到本地 = file 验证 MIME = 走 yuer_reverse_inference.run 洗图直出
- ❌ 不要在反爬站死磕工具栈 = Cloudflare 拦不住 = 浪费时间
