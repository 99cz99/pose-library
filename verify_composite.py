import urllib.request, json, time

CKPT = 'Illustrious-XL-v2.0.safetensors'
NEG = 'lowres, bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, extra digits, fewer digits, cropped, worst quality'
P1 = '1girl, full body, standing, hatsune_miku, aqua hair, teal hair, twintails, green eyes, sleeveless shirt, necktie, pleated skirt, simple background, plain background, white background, masterpiece, best quality'
P2 = '1girl, full body, standing, rem_(re:zero), blue hair, short hair, maid, hair flower, blue eyes, simple background, plain background, white background, masterpiece, best quality'
P3 = '1girl, full body, standing, zero_two_(darling_in_the_franxx), pink hair, long hair, red horns, green eyes, red bodysuit, simple background, plain background, white background, masterpiece, best quality'

def gen(pos_id, latent_id, ksampler_id, decode_id, pos, seed, neg='3'):
    return {
        str(pos_id): {'class_type': 'CLIPTextEncode', 'inputs': {'text': pos, 'clip': ['1', 1]}},
        str(latent_id): {'class_type': 'EmptyLatentImage', 'inputs': {'width': 512, 'height': 1024, 'batch_size': 1}},
        str(ksampler_id): {'class_type': 'KSampler', 'inputs': {'model': ['1', 0], 'positive': [str(pos_id), 0], 'negative': [neg, 0], 'latent_image': [str(latent_id), 0], 'seed': seed, 'steps': 28, 'cfg': 7.0, 'sampler_name': 'euler', 'scheduler': 'normal', 'denoise': 1.0}},
        str(decode_id): {'class_type': 'VAEDecode', 'inputs': {'samples': [str(ksampler_id), 0], 'vae': ['1', 2]}},
    }

prompt = {
    '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': CKPT}},
    '3': {'class_type': 'CLIPTextEncode', 'inputs': {'text': NEG, 'clip': ['1', 1]}},
}
prompt.update(gen(2, 4, 5, 6, P1, 101))
prompt.update(gen(7, 8, 9, 10, P2, 202))
prompt.update(gen(11, 12, 13, 14, P3, 303))
prompt.update({
    '15': {'class_type': 'ImageBatch', 'inputs': {'image1': ['6', 0], 'image2': ['10', 0]}},
    '16': {'class_type': 'ImageBatch', 'inputs': {'image1': ['15', 0], 'image2': ['14', 0]}},
    '17': {'class_type': 'ImageGrid', 'inputs': {'images': ['16', 0], 'columns': 3, 'cell_width': 512, 'cell_height': 1024, 'padding': 12}},
    '18': {'class_type': 'SaveImage', 'inputs': {'images': ['17', 0], 'filename_prefix': 'composite'}},
})

req = urllib.request.Request('http://127.0.0.1:8188/prompt', data=json.dumps({'prompt': prompt, 'client_id': 'claude-comp'}).encode(), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=60) as r:
    resp = json.loads(r.read())
print('submit:', json.dumps(resp, ensure_ascii=False)[:200])
pid = resp.get('prompt_id')
if resp.get('node_errors'):
    print('NODE_ERRORS:', json.dumps(resp['node_errors'], ensure_ascii=False)[:600])
else:
    for i in range(250):
        time.sleep(3)
        with urllib.request.urlopen('http://127.0.0.1:8188/history/' + pid, timeout=15) as r:
            h = json.loads(r.read())
        if pid in h:
            st = h[pid].get('status', {})
            if st.get('status_str') in ('success', 'error'):
                print('status:', st.get('status_str'))
                print('outputs:', json.dumps(h[pid].get('outputs', {}), ensure_ascii=False)[:300])
                break
