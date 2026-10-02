import urllib.request, json, time, sys

IMAGE = sys.argv[1] if len(sys.argv) > 1 else 'example.png'  # 参考图文件名（放 ComfyUI/input/ 下）

prompt = {
    '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': 'Illustrious-XL-v2.0.safetensors'}},
    '2': {'class_type': 'LoadImage', 'inputs': {'image': IMAGE}},
    '3': {'class_type': 'ControlNetLoader', 'inputs': {'control_net_name': 'noob_sdxl_controlnet_canny.fp16.safetensors'}},
    '4': {'class_type': 'Canny', 'inputs': {'image': ['2', 0], 'low_threshold': 0.4, 'high_threshold': 0.8}},
    '5': {'class_type': 'CLIPTextEncode', 'inputs': {'text': '1girl, solo, masterpiece, best quality', 'clip': ['1', 1]}},
    '6': {'class_type': 'CLIPTextEncode', 'inputs': {'text': 'lowres, bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, cropped, worst quality', 'clip': ['1', 1]}},
    '7': {'class_type': 'EmptyLatentImage', 'inputs': {'width': 832, 'height': 1216, 'batch_size': 1}},
    '8': {'class_type': 'ControlNetApplyAdvanced', 'inputs': {'positive': ['5', 0], 'negative': ['6', 0], 'control_net': ['3', 0], 'image': ['4', 0], 'vae': ['1', 2], 'strength': 1.0, 'start_percent': 0.0, 'end_percent': 1.0}},
    '9': {'class_type': 'KSampler', 'inputs': {'model': ['1', 0], 'positive': ['8', 0], 'negative': ['8', 1], 'latent_image': ['7', 0], 'seed': 12345, 'steps': 28, 'cfg': 7.0, 'sampler_name': 'euler', 'scheduler': 'normal', 'denoise': 1.0}},
    '10': {'class_type': 'VAEDecode', 'inputs': {'samples': ['9', 0], 'vae': ['1', 2]}},
    '11': {'class_type': 'SaveImage', 'inputs': {'images': ['10', 0], 'filename_prefix': 'canny_test'}},
}

req = urllib.request.Request('http://127.0.0.1:8188/prompt', data=json.dumps({'prompt': prompt, 'client_id': 'claude-canny'}).encode(), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=60) as r:
    resp = json.loads(r.read())
print('submit:', json.dumps(resp, ensure_ascii=False)[:200])
pid = resp.get('prompt_id')
if resp.get('node_errors'):
    print('NODE_ERRORS:', json.dumps(resp['node_errors'], ensure_ascii=False)[:600])
else:
    for i in range(200):
        time.sleep(3)
        with urllib.request.urlopen('http://127.0.0.1:8188/history/' + pid, timeout=15) as r:
            h = json.loads(r.read())
        if pid in h:
            st = h[pid].get('status', {})
            if st.get('status_str') in ('success', 'error'):
                print('status:', st.get('status_str'))
                print('outputs:', json.dumps(h[pid].get('outputs', {}), ensure_ascii=False)[:300])
                break
