import json, uuid

def N(nid, ntype, pos, widgets, inputs, outputs):
    return {'id': nid, 'type': ntype, 'pos': pos, 'size': [320, 180], 'flags': {},
            'order': nid, 'mode': 0, 'inputs': inputs, 'outputs': outputs,
            'properties': {'Node name for S&R': ntype}, 'widgets_values': widgets}

def inp(name, typ, link=None):
    return {'name': name, 'type': typ, 'link': link, 'localized_name': name}

def outp(name, typ, links=None):
    return {'name': name, 'type': typ, 'links': links or [], 'localized_name': name}

nodes = [
    N(1, 'LoadImage', [40, 40], ['example.png', 'image'], [], [outp('IMAGE','IMAGE'), outp('MASK','MASK')]),
    N(2, 'DepthAnythingPreprocessor', [340, 40], [512], [inp('image','IMAGE')], [outp('IMAGE','IMAGE')]),
    N(3, 'ControlNetLoader', [340, 300], ['noob_sdxl_controlnet_depth.safetensors'], [], [outp('CONTROL_NET','CONTROL_NET')]),
    N(4, 'CheckpointLoaderSimple', [40, 300], ['Illustrious-XL-v2.0.safetensors'], [], [outp('MODEL','MODEL'), outp('CLIP','CLIP'), outp('VAE','VAE')]),
    N(5, 'CLIPTextEncode', [640, 40], ['1girl, solo, full body, masterpiece, best quality', None], [inp('text','STRING'), inp('clip','CLIP')], [outp('CONDITIONING','CONDITIONING')]),
    N(6, 'CLIPTextEncode', [640, 300], ['lowres, bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, cropped, worst quality', None], [inp('text','STRING'), inp('clip','CLIP')], [outp('CONDITIONING','CONDITIONING')]),
    N(7, 'EmptyLatentImage', [940, 40], [832, 1216, 1], [], [outp('LATENT','LATENT')]),
    N(8, 'ControlNetApplyAdvanced', [940, 300], [1.0, 0.0, 1.0], [inp('positive','CONDITIONING'), inp('negative','CONDITIONING'), inp('control_net','CONTROL_NET'), inp('image','IMAGE'), inp('vae','VAE')], [outp('positive','CONDITIONING'), outp('negative','CONDITIONING')]),
    N(9, 'KSampler', [1240, 40], [12345, 28, 7.0, 'euler', 'normal', 1.0], [inp('model','MODEL'), inp('positive','CONDITIONING'), inp('negative','CONDITIONING'), inp('latent_image','LATENT')], [outp('LATENT','LATENT')]),
    N(10, 'VAEDecode', [1540, 40], [], [inp('samples','LATENT'), inp('vae','VAE')], [outp('IMAGE','IMAGE')]),
    N(11, 'SaveImage', [1540, 300], ['depth_out'], [inp('images','IMAGE')], [outp('IMAGE','IMAGE')]),
]

links = [
    [1, 1, 0, 2, 0, 'IMAGE'],     # LoadImage -> DepthAnything
    [2, 2, 0, 8, 3, 'IMAGE'],     # depth map -> ControlNetApply.image
    [3, 3, 0, 8, 2, 'CONTROL_NET'],
    [4, 4, 1, 5, 1, 'CLIP'],      # clip -> pos
    [5, 4, 1, 6, 1, 'CLIP'],      # clip -> neg
    [6, 5, 0, 8, 0, 'CONDITIONING'],
    [7, 6, 0, 8, 1, 'CONDITIONING'],
    [8, 4, 2, 8, 4, 'VAE'],
    [9, 4, 0, 9, 0, 'MODEL'],
    [10, 8, 0, 9, 1, 'CONDITIONING'],
    [11, 8, 1, 9, 2, 'CONDITIONING'],
    [12, 7, 0, 9, 3, 'LATENT'],
    [13, 9, 0, 10, 0, 'LATENT'],
    [14, 4, 2, 10, 1, 'VAE'],
    [15, 10, 0, 11, 0, 'IMAGE'],
]

for l in links:
    lid, fn, fs, tn, ts, typ = l
    nodes[tn-1]['inputs'][ts]['link'] = lid
    nodes[fn-1]['outputs'][fs]['links'].append(lid)

wf = {'id': str(uuid.uuid4()), 'revision': 0, 'last_node_id': 11, 'last_link_id': 15,
      'nodes': nodes, 'links': links, 'groups': [], 'config': {}, 'extra': {}, 'version': 0.4}

path = r'E:\ComfyUI_windows_portable\ComfyUI\user\default\workflows\深度图Illustrious.json'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
print('written', path)
print('nodes', len(nodes), 'links', len(links))
