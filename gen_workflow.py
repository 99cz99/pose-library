import json, uuid

def N(nid, ntype, pos, widgets, inputs, outputs):
    return {'id': nid, 'type': ntype, 'pos': pos, 'size': [320, 180], 'flags': {},
            'order': nid, 'mode': 0, 'inputs': inputs, 'outputs': outputs,
            'properties': {'Node name for S&R': ntype}, 'widgets_values': widgets}

def inp(name, typ, link=None):
    return {'name': name, 'type': typ, 'link': link, 'localized_name': name}

def outp(name, typ, links=None):
    return {'name': name, 'type': typ, 'links': links or [], 'localized_name': name}

BASE_POS = '3girls, multiple girls, group, full body, standing, looking at viewer, simple background, masterpiece, best quality'
NEG = 'lowres, bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, extra digits, fewer digits, multiple views, cropped, worst quality'
P1 = 'hatsune_miku, 1girl, aqua hair, teal hair, very long hair, twintails, hair ornament, headphones, green eyes'
P2 = 'rem_(re:zero), 1girl, blue hair, short hair, maid, hair flower, blue eyes'
P3 = 'zero_two_(darling_in_the_franxx), 1girl, pink hair, long hair, red horns, green eyes'

KSP = [8.0, 'euler', 'karras', 1.0]
RS = [0, 0, 'ignore', 30, 2, 1.0, 20, True, 'ratio between', 'AUTO', 0.3]

def text_encode(nid, pos, txt):
    return N(nid, 'CLIPTextEncode', pos, [txt, None], [inp('text','STRING'), inp('clip','CLIP')], [outp('CONDITIONING','CONDITIONING')])

def to_basic_pipe(nid, pos):
    return N(nid, 'ToBasicPipe', pos, [], [inp('model','MODEL'), inp('clip','CLIP'), inp('vae','VAE'), inp('positive','CONDITIONING'), inp('negative','CONDITIONING')], [outp('BASIC_PIPE','BASIC_PIPE')])

def ksampler_provider(nid, pos):
    return N(nid, 'KSamplerAdvancedProvider', pos, KSP, [inp('basic_pipe','BASIC_PIPE')], [outp('KSAMPLER_ADVANCED','KSAMPLER_ADVANCED')])

def mask_rect(nid, pos, x, w):
    return N(nid, 'MaskRectArea', pos, [x, 0, w, 100, 0], [], [outp('MASK','MASK')])

def regional_prompt(nid, pos):
    return N(nid, 'RegionalPrompt', pos, [], [inp('mask','MASK'), inp('advanced_sampler','KSAMPLER_ADVANCED')], [outp('REGIONAL_PROMPTS','REGIONAL_PROMPTS')])

nodes = [
    N(1, 'CheckpointLoaderSimple', [40, 40], ['Illustrious-XL-v2.0.safetensors'], [], [outp('MODEL','MODEL'), outp('CLIP','CLIP'), outp('VAE','VAE')]),
    text_encode(2, [40, 300], BASE_POS),
    text_encode(3, [40, 520], NEG),
    N(4, 'EmptyLatentImage', [40, 740], [1536, 1024, 1], [], [outp('LATENT','LATENT')]),
    to_basic_pipe(5, [340, 40]),
    ksampler_provider(6, [340, 300]),
    # region1 初音
    text_encode(7, [640, 40], P1),
    to_basic_pipe(8, [940, 40]),
    ksampler_provider(9, [1240, 40]),
    mask_rect(10, [1240, 300], 0, 33),
    regional_prompt(11, [1540, 40]),
    # region2 蕾姆
    text_encode(12, [640, 300], P2),
    to_basic_pipe(13, [940, 300]),
    ksampler_provider(14, [1240, 560]),
    mask_rect(15, [1240, 820], 33, 34),
    regional_prompt(16, [1540, 300]),
    # region3 02
    text_encode(17, [640, 560], P3),
    to_basic_pipe(18, [940, 560]),
    ksampler_provider(19, [1240, 1080]),
    mask_rect(20, [1240, 1340], 67, 33),
    regional_prompt(21, [1540, 560]),
    # combine + sample + decode + save
    N(22, 'CombineRegionalPrompts', [1840, 40], [], [inp('regional_prompts1','REGIONAL_PROMPTS'), inp('regional_prompts2','REGIONAL_PROMPTS'), inp('regional_prompts3','REGIONAL_PROMPTS')], [outp('REGIONAL_PROMPTS','REGIONAL_PROMPTS')]),
    N(23, 'RegionalSampler', [2140, 40], RS, [inp('samples','LATENT'), inp('base_sampler','KSAMPLER_ADVANCED'), inp('regional_prompts','REGIONAL_PROMPTS')], [outp('LATENT','LATENT')]),
    N(24, 'VAEDecode', [2440, 40], [], [inp('samples','LATENT'), inp('vae','VAE')], [outp('IMAGE','IMAGE')]),
    N(25, 'SaveImage', [2440, 300], ['multi_char'], [inp('images','IMAGE')], [outp('IMAGE','IMAGE')]),
]

def region_links(start, enc_id, pipe_id, prov_id, mask_id, rp_id):
    return [
        [start, 1, 0, pipe_id, 0, 'MODEL'],
        [start+1, 1, 1, pipe_id, 1, 'CLIP'],
        [start+2, 1, 2, pipe_id, 2, 'VAE'],
        [start+3, enc_id, 0, pipe_id, 3, 'CONDITIONING'],
        [start+4, 3, 0, pipe_id, 4, 'CONDITIONING'],
        [start+5, pipe_id, 0, prov_id, 0, 'BASIC_PIPE'],
        [start+6, prov_id, 0, rp_id, 1, 'KSAMPLER_ADVANCED'],
        [start+7, mask_id, 0, rp_id, 0, 'MASK'],
    ]

links = [
    [1, 1, 0, 5, 0, 'MODEL'],
    [2, 1, 1, 5, 1, 'CLIP'],
    [3, 1, 2, 5, 2, 'VAE'],
    [4, 2, 0, 5, 3, 'CONDITIONING'],
    [5, 3, 0, 5, 4, 'CONDITIONING'],
    [6, 5, 0, 6, 0, 'BASIC_PIPE'],
    [7, 1, 1, 2, 1, 'CLIP'],
    [8, 1, 1, 3, 1, 'CLIP'],
    [9, 1, 1, 7, 1, 'CLIP'],
    [10, 1, 1, 12, 1, 'CLIP'],
    [11, 1, 1, 17, 1, 'CLIP'],
]
links += region_links(12, 7, 8, 9, 10, 11)
links += region_links(20, 12, 13, 14, 15, 16)
links += region_links(28, 17, 18, 19, 20, 21)
links += [
    [36, 11, 0, 22, 0, 'REGIONAL_PROMPTS'],
    [37, 16, 0, 22, 1, 'REGIONAL_PROMPTS'],
    [38, 21, 0, 22, 2, 'REGIONAL_PROMPTS'],
    [39, 4, 0, 23, 0, 'LATENT'],
    [40, 6, 0, 23, 1, 'KSAMPLER_ADVANCED'],
    [41, 22, 0, 23, 2, 'REGIONAL_PROMPTS'],
    [42, 23, 0, 24, 0, 'LATENT'],
    [43, 1, 2, 24, 1, 'VAE'],
    [44, 24, 0, 25, 0, 'IMAGE'],
]

for l in links:
    lid, fn, fs, tn, ts, typ = l
    nodes[tn-1]['inputs'][ts]['link'] = lid
    nodes[fn-1]['outputs'][fs]['links'].append(lid)

wf = {'id': str(uuid.uuid4()), 'revision': 0, 'last_node_id': 25, 'last_link_id': 44,
      'nodes': nodes, 'links': links, 'groups': [], 'config': {}, 'extra': {}, 'version': 0.4}

path = r'E:\ComfyUI_windows_portable\ComfyUI\user\default\workflows\多人区域提示词.json'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
print('written', path)
print('nodes', len(nodes), 'links', len(links))
