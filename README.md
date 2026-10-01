# 提示词生成器 + 骨骼图库（Telegram Mini App）

嵌在 Telegram 里的 booru 提示词标签生成器，附带骨骼姿势图库，只对授权用户开放。

## 结构

- `index.html` — 主页面（标签生成器 + 骨骼图库）
- `skeleton_manifest.json` — 骨骼图清单
- `skeletons/` — 骨骼图图片文件夹

## 如何添加骨骼图

1. 把 PNG 图片放进 `skeletons/` 文件夹；
2. 在 `skeleton_manifest.json` 里加一条：

```json
{ "file": "你的图.png", "label": "站姿-手臂上举" }
```

## 如何授权用户

在 `index.html` 里搜 `AUTHORIZED_IDS`，把授权用户的 Telegram 数字 ID 填进数组：

```js
const AUTHORIZED_IDS = [123456789, 987654321];
```

（Telegram 数字 ID 可以用 @userinfobot 查。）
