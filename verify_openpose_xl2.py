import urllib.request, json, time, sys

REF = sys.argv[1] if len(sys.argv) > 1 else '139782352_p2.png'
SCALE_STICK = sys.argv[2] if len(sys.argv) > 2 else 'enable'  # xinsir 系 CN 用 enable

prompt = {
    '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': 'Illustrious-XL-v2.0.safetensors'}},
    '2': {'class_type': 'LoadImage', 'inputs': {'image': REF}},
    '3': {'class_type': 'ControlNetLoader', 'inputs': {'control_net_name': 'OpenPoseXL2.safetensors'}},
    '4': {'class_type': 'DWPreprocessor', 'inputs': {'image': ['2', 0], 'detect_hand': 'enable', 'detect_body': 'enable', 'detect_face': 'enable', 'resolution': 1024, 'bbox_detector': 'yolox_l.onnx', 'pose_estimator': 'dw-ll_ucoco_384.onnx', 'scale_stick_for_xinsr_cn': SCALE_STICK}},
    '5': {'class_type': 'CLIPTextEncode', 'inputs': {'text': '1girl, solo, full body, masterpiece, best quality', 'clip': ['1', 1]}},
    '6': {'class_type': 'CLIPTextEncode', 'inputs': {'text': 'lowres, bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, cropped, worst quality', 'clip': ['1', 1]}},
    '7': {'class_type': 'EmptyLatentImage', 'inputs': {'width': 832, 'height': 1216, 'batch_size': 1}},
    '8': {'class_type': 'ControlNetApplyAdvanced', 'inputs': {'positive': ['5', 0], 'negative': ['6', 0], 'control_net': ['3', 0], 'image': ['4', 0], 'vae': ['1', 2], 'strength': 1.0, 'start_percent': 0.0, 'end_percent': 1.0}},
    '9': {'class_type': 'KSampler', 'inputs': {'model': ['1', 0], 'positive': ['8', 0], 'negative': ['8', 1], 'latent_image': ['7', 0], 'seed': 12345, 'steps': 28, 'cfg': 7.0, 'sampler_name': 'euler', 'scheduler': 'normal', 'denoise': 1.0}},
    '10': {'class_type': 'VAEDecode', 'inputs': {'samples': ['9', 0], 'vae': ['1', 2]}},
    '11': {'class_type': 'SaveImage', 'inputs': {'images': ['10', 0], 'filename_prefix': 'openpose_xl2'}},
}

req = urllib.request.Request('http://127.0.0.1:8188/prompt', data=json.dumps({'prompt': prompt, 'client_id': 'claude-xl2'}).encode(), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=60) as r:
    resp = json.loads(r.read())
pid = resp.get('prompt_id')
print('submit:', pid, 'node_errors:', bool(resp.get('node_errors')))
for i in range(300):
    time.sleep(3)
    with urllib.request.urlopen('http://127.0.0.1:8188/history/' + pid, timeout=15) as r:
        h = json.loads(r.read())
    if pid in h:
        st = h[pid].get('status', {})
        if st.get('status_str') in ('success', 'error'):
            print('status:', st.get('status_str'))
            print('outputs:', json.dumps(h[pid].get('outputs', {}), ensure_ascii=False)[:300])
            break
