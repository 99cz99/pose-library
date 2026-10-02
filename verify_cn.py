import urllib.request, json, time

POS = ('3girls, multiple girls, group, full body, standing, looking at viewer, '
       'hatsune_miku, aqua hair, teal hair, twintails, green eyes, '
       'rem_(re:zero), blue hair, short hair, maid, hair flower, blue eyes, '
       'zero_two_(darling_in_the_franxx), pink hair, long hair, red horns, green eyes, '
       'simple background, masterpiece, best quality')
NEG = 'lowres, bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, extra digits, fewer digits, multiple views, cropped, worst quality'

prompt = {
    '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': 'Illustrious-XL-v2.0.safetensors'}},
    '2': {'class_type': 'LoadImage', 'inputs': {'image': 'three_pose.png'}},
    '3': {'class_type': 'ControlNetLoader', 'inputs': {'control_net_name': 'thibaud_xl_openpose.safetensors'}},
    '4': {'class_type': 'CLIPTextEncode', 'inputs': {'text': POS, 'clip': ['1', 1]}},
    '5': {'class_type': 'CLIPTextEncode', 'inputs': {'text': NEG, 'clip': ['1', 1]}},
    '6': {'class_type': 'EmptyLatentImage', 'inputs': {'width': 1536, 'height': 1024, 'batch_size': 1}},
    '7': {'class_type': 'ControlNetApplyAdvanced', 'inputs': {'positive': ['4', 0], 'negative': ['5', 0], 'control_net': ['3', 0], 'image': ['2', 0], 'vae': ['1', 2], 'strength': 1.0, 'start_percent': 0.0, 'end_percent': 1.0}},
    '8': {'class_type': 'KSampler', 'inputs': {'model': ['1', 0], 'positive': ['7', 0], 'negative': ['7', 1], 'latent_image': ['6', 0], 'seed': 12345, 'steps': 30, 'cfg': 7.0, 'sampler_name': 'euler', 'scheduler': 'normal', 'denoise': 1.0}},
    '9': {'class_type': 'VAEDecode', 'inputs': {'samples': ['8', 0], 'vae': ['1', 2]}},
    '10': {'class_type': 'SaveImage', 'inputs': {'images': ['9', 0], 'filename_prefix': 'multi_cn'}},
}

req = urllib.request.Request('http://127.0.0.1:8188/prompt', data=json.dumps({'prompt': prompt, 'client_id': 'claude-cn'}).encode(), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=60) as r:
    resp = json.loads(r.read())
print('submit:', json.dumps(resp, ensure_ascii=False)[:300])
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
