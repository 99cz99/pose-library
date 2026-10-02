from PIL import Image, ImageDraw
import json, os

W, H = 1024, 1536
OUT = r'E:\ComfyUI_windows_portable\ComfyUI\input'

limbSeq = [
    [2,3],[2,6],[3,4],[4,5],[6,7],[7,8],
    [2,9],[9,10],[10,11],[2,12],[12,13],[13,14],
    [2,1],[1,15],[15,17],[1,16],[16,18],
]
colors = [
    [255,0,0],[255,85,0],[255,170,0],[255,255,0],[170,255,0],[85,255,0],[0,255,0],
    [0,255,85],[0,255,170],[0,255,255],[0,170,255],[0,85,255],[0,0,255],[85,0,255],
    [170,0,255],[255,0,255],[255,0,170],[255,0,85],
]

# 每个姿势：18 个关键点 (x, y) 归一化 0-1。顺序：nose,neck,R-sh,R-elb,R-wri,L-sh,L-elb,L-wri,R-hip,R-knee,R-ank,L-hip,L-knee,L-ank,R-eye,L-eye,R-ear,L-ear
poses = {
    'on_all_fours': [
        (0.30,0.38),(0.36,0.46),(0.32,0.50),(0.26,0.66),(0.24,0.80),
        (0.42,0.48),(0.46,0.64),(0.48,0.80),
        (0.52,0.42),(0.66,0.60),(0.70,0.80),
        (0.58,0.44),(0.72,0.60),(0.76,0.80),
        (0.28,0.37),(0.33,0.37),(0.26,0.39),(0.36,0.39),
    ],
    'kneeling_arch': [
        (0.40,0.30),(0.42,0.38),(0.38,0.42),(0.30,0.52),(0.26,0.60),
        (0.48,0.40),(0.54,0.50),(0.58,0.58),
        (0.42,0.60),(0.40,0.78),(0.40,0.92),
        (0.50,0.60),(0.50,0.78),(0.50,0.92),
        (0.38,0.29),(0.43,0.29),(0.36,0.31),(0.45,0.31),
    ],
    'sitting_spread': [
        (0.50,0.22),(0.50,0.30),(0.44,0.34),(0.34,0.40),(0.26,0.46),
        (0.56,0.34),(0.66,0.40),(0.74,0.46),
        (0.46,0.46),(0.30,0.62),(0.20,0.78),
        (0.54,0.46),(0.70,0.62),(0.80,0.78),
        (0.48,0.21),(0.52,0.21),(0.46,0.23),(0.54,0.23),
    ],
    'bent_over': [
        (0.50,0.18),(0.50,0.26),(0.44,0.30),(0.40,0.46),(0.38,0.62),
        (0.56,0.30),(0.60,0.46),(0.62,0.62),
        (0.48,0.52),(0.46,0.70),(0.46,0.88),
        (0.52,0.52),(0.54,0.70),(0.54,0.88),
        (0.48,0.17),(0.52,0.17),(0.46,0.19),(0.54,0.19),
    ],
    'w_sit': [
        (0.50,0.24),(0.50,0.32),(0.44,0.36),(0.36,0.44),(0.30,0.52),
        (0.56,0.36),(0.64,0.44),(0.70,0.52),
        (0.46,0.52),(0.34,0.66),(0.28,0.78),
        (0.54,0.52),(0.66,0.66),(0.72,0.78),
        (0.48,0.23),(0.52,0.23),(0.46,0.25),(0.54,0.25),
    ],
}

def draw_pose(kpts, out_png):
    img = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(int(x * W), int(y * H)) for x, y in kpts]
    for (k1, k2), color in zip(limbSeq, colors):
        c = tuple(int(v * 0.6) for v in color)
        d.line([pts[k1-1], pts[k2-1]], fill=c, width=5)
    for i, color in enumerate(colors):
        x, y = pts[i]
        d.ellipse([x-5, y-5, x+5, y+5], fill=tuple(color))
    img.save(out_png)

def write_json(kpts, out_json):
    flat = []
    for x, y in kpts:
        flat += [x * W, y * H, 1.0]
    data = {'width': W, 'height': H, 'people': [{'pose_keypoints_2d': flat}]}
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

names = ['on_all_fours', 'kneeling_arch', 'sitting_spread', 'bent_over', 'w_sit']
for i, name in enumerate(names, 1):
    kpts = poses[name]
    png = os.path.join(OUT, f'nsfw_pose_{i:02d}.png')
    js = os.path.join(OUT, f'nsfw_pose_{i:02d}.json')
    draw_pose(kpts, png)
    write_json(kpts, js)
    print('saved', f'nsfw_pose_{i:02d}', name)
