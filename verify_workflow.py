import urllib.request, json, time

BASE_POS = '3girls, multiple girls, group, full body, standing, looking at viewer, simple background, masterpiece, best quality'
NEG = 'lowres, bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, extra digits, fewer digits, multiple views, cropped, worst quality'
P1 = 'hatsune_miku, 1girl, aqua hair, teal hair, very long hair, twintails, hair ornament, headphones, green eyes'
P2 = 'rem_(re:zero), 1girl, blue hair, short hair, maid, hair flower, blue eyes'
P3 = 'zero_two_(darling_in_the_franxx), 1girl, pink hair, long hair, red horns, green eyes'

def ksp(cfg=8.0):
    return {'cfg': cfg, 'sampler_name': 'euler', 'scheduler': 'karras', 'sigma_factor': 1.0}

def region(enc, pipe, prov, mask, rp, P, x, w):
    return {
        str(enc): {'class_type': 'CLIPTextEncode', 'inputs': {'text': P, 'clip': ['1', 1]}},
        str(pipe): {'class_type': 'ToBasicPipe', 'inputs': {'model': ['1', 0], 'clip': ['1', 1], 'vae': ['1', 2], 'positive': [str(enc), 0], 'negative': ['3', 0]}},
        str(prov): {'class_type': 'KSamplerAdvancedProvider', 'inputs': {**ksp(), 'basic_pipe': [str(pipe), 0]}},
        str(mask): {'class_type': 'MaskRectArea', 'inputs': {'x': x, 'y': 0, 'width': w, 'height': 100, 'blur_radius': 0}},
        str(rp): {'class_type': 'RegionalPrompt', 'inputs': {'mask': [str(mask), 0], 'advanced_sampler': [str(prov), 0]}},
    }

prompt = {
    '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': 'Illustrious-XL-v2.0.safetensors'}},
    '2': {'class_type': 'CLIPTextEncode', 'inputs': {'text': BASE_POS, 'clip': ['1', 1]}},
    '3': {'class_type': 'CLIPTextEncode', 'inputs': {'text': NEG, 'clip': ['1', 1]}},
    '4': {'class_type': 'EmptyLatentImage', 'inputs': {'width': 1536, 'height': 1024, 'batch_size': 1}},
    '5': {'class_type': 'ToBasicPipe', 'inputs': {'model': ['1', 0], 'clip': ['1', 1], 'vae': ['1', 2], 'positive': ['2', 0], 'negative': ['3', 0]}},
    '6': {'class_type': 'KSamplerAdvancedProvider', 'inputs': {**ksp(), 'basic_pipe': ['5', 0]}},
}
prompt.update(region(7, 8, 9, 10, 11, P1, 0, 33))
prompt.update(region(12, 13, 14, 15, 16, P2, 33, 34))
prompt.update(region(17, 18, 19, 20, 21, P3, 67, 33))
prompt.update({
    '22': {'class_type': 'CombineRegionalPrompts', 'inputs': {'regional_prompts1': ['11', 0], 'regional_prompts2': ['16', 0], 'regional_prompts3': ['21', 0]}},
    '23': {'class_type': 'RegionalSampler', 'inputs': {'samples': ['4', 0], 'base_sampler': ['6', 0], 'regional_prompts': ['22', 0],
        'seed': 0, 'seed_2nd': 0, 'seed_2nd_mode': 'ignore', 'steps': 30, 'base_only_steps': 2, 'denoise': 1.0,
        'overlap_factor': 20, 'restore_latent': True, 'additional_mode': 'ratio between', 'additional_sampler': 'AUTO', 'additional_sigma_ratio': 0.3}},
    '24': {'class_type': 'VAEDecode', 'inputs': {'samples': ['23', 0], 'vae': ['1', 2]}},
    '25': {'class_type': 'SaveImage', 'inputs': {'images': ['24', 0], 'filename_prefix': 'multi_char'}},
})

req = urllib.request.Request('http://127.0.0.1:8188/prompt', data=json.dumps({'prompt': prompt, 'client_id': 'claude-verify'}).encode(), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=60) as r:
    resp = json.loads(r.read())
print('submit:', json.dumps(resp, ensure_ascii=False)[:400])
pid = resp.get('prompt_id')
if resp.get('node_errors'):
    print('NODE_ERRORS:', json.dumps(resp['node_errors'], ensure_ascii=False)[:800])
else:
    for i in range(200):
        time.sleep(3)
        with urllib.request.urlopen('http://127.0.0.1:8188/history/' + pid, timeout=15) as r:
            h = json.loads(r.read())
        if pid in h:
            st = h[pid].get('status', {})
            if st.get('status_str') in ('success', 'error'):
                print('status:', st.get('status_str'))
                print('outputs:', json.dumps(h[pid].get('outputs', {}), ensure_ascii=False)[:400])
                break
