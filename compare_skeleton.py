import urllib.request, json, time, math

prompt = {
    '1': {'class_type': 'LoadImage', 'inputs': {'image': '139782352_p2.png'}},
    '2': {'class_type': 'LoadImage', 'inputs': {'image': 'openpose_xl2_00001_.png'}},
    '3': {'class_type': 'DWPreprocessor', 'inputs': {'image': ['1', 0], 'detect_hand': 'disable', 'detect_body': 'enable', 'detect_face': 'disable', 'resolution': 1024, 'bbox_detector': 'yolox_l.onnx', 'pose_estimator': 'dw-ll_ucoco_384.onnx', 'scale_stick_for_xinsr_cn': 'enable'}},
    '4': {'class_type': 'DWPreprocessor', 'inputs': {'image': ['2', 0], 'detect_hand': 'disable', 'detect_body': 'enable', 'detect_face': 'disable', 'resolution': 1024, 'bbox_detector': 'yolox_l.onnx', 'pose_estimator': 'dw-ll_ucoco_384.onnx', 'scale_stick_for_xinsr_cn': 'enable'}},
    '5': {'class_type': 'SaveImage', 'inputs': {'images': ['3', 0], 'filename_prefix': 'cmp_ref'}},
    '6': {'class_type': 'SaveImage', 'inputs': {'images': ['4', 0], 'filename_prefix': 'cmp_out'}},
}

req = urllib.request.Request('http://127.0.0.1:8188/prompt',
    data=json.dumps({'prompt': prompt, 'client_id': 'claude-cmp'}).encode(),
    headers={'Content-Type': 'application/json'})
try:
    resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print('HTTP', e.code, ':', body[:600])
    raise SystemExit

pid = resp['prompt_id']
print('submit ok:', pid)
for i in range(200):
    time.sleep(3)
    h = json.loads(urllib.request.urlopen('http://127.0.0.1:8188/history/' + pid, timeout=15).read())
    if pid in h and h[pid].get('status', {}).get('status_str') in ('success', 'error'):
        out = h[pid].get('outputs', {})
        def kp(node):
            try:
                j = json.loads(out[str(node)]['openpose_json'][0])
                p = j[0]['people'][0]['pose_keypoints_2d']
                return [p[k:k+3] for k in range(0, len(p), 3)]
            except Exception as e:
                print('parse err node', node, e)
                return None
        a = kp(3); b = kp(4)
        if a and b:
            body_idx = [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
            def norm(k):
                if len(k) > 6 and k[5][2] > 0.3 and k[6][2] > 0.3:
                    s = math.dist((k[5][0], k[5][1]), (k[6][0], k[6][1])) or 1
                else:
                    s = 1
                return [(k[i][0], k[i][1]) for i in body_idx if i < len(k) and k[i][2] > 0.3], s
            pa, sa = norm(a); pb, sb = norm(b)
            if pa and len(pa) == len(pb):
                dists = [math.dist(pa[i], pb[i]) / sa for i in range(len(pa))]
                avg = sum(dists) / len(dists)
                print('参考关键点数', len(a), '| 出图关键点数', len(b))
                print('身体关键点平均距离(肩距归一化):', round(avg, 3))
                print('结论:', '跟上了' if avg < 0.8 else ('部分跟上' if avg < 1.5 else '没跟上'))
            else:
                print('关键点不完整', len(a), len(b), len(pa), len(pb))
        else:
            print('骨架提取失败：', json.dumps(out, ensure_ascii=False)[:200])
        break
