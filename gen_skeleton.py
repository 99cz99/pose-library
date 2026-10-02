from PIL import Image, ImageDraw

W, H = 1536, 1024

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

def person(cx):
    return [
        (cx, 0.12), (cx, 0.25),
        (cx-0.06, 0.28), (cx-0.10, 0.40), (cx-0.12, 0.52),
        (cx+0.06, 0.28), (cx+0.10, 0.40), (cx+0.12, 0.52),
        (cx-0.03, 0.55), (cx-0.03, 0.70), (cx-0.03, 0.85),
        (cx+0.03, 0.55), (cx+0.03, 0.70), (cx+0.03, 0.85),
        (cx-0.02, 0.11), (cx+0.02, 0.11),
        (cx-0.04, 0.13), (cx+0.04, 0.13),
    ]

people = [person(0.17), person(0.5), person(0.83)]

img = Image.new('RGB', (W, H), (0, 0, 0))
draw = ImageDraw.Draw(img)

for kpts in people:
    pts = [(kpts[i][0] * W, kpts[i][1] * H) for i in range(18)]
    for (k1, k2), color in zip(limbSeq, colors):
        p1, p2 = pts[k1-1], pts[k2-1]
        c = tuple(int(x * 0.6) for x in color)
        draw.line([p1, p2], fill=c, width=5)
    for i, color in enumerate(colors):
        x, y = pts[i]
        draw.ellipse([x-5, y-5, x+5, y+5], fill=tuple(color))

out = r'E:\ComfyUI_windows_portable\ComfyUI\input\three_pose.png'
img.save(out)
print('saved', out, img.size)
