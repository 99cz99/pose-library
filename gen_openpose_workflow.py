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
    N(1, 'LoadImage', [40, 40], ['complex_pose_01.png', 'image'], [], [outp('IMAGE','IMAGE'), outp('MASK','MASK')]),
    N(2, 'ControlNetLoader', [340, 300], ['noob_openpose_pre.safetensors'], [], [outp('CONTROL_NET','CONTROL_NET')]),
    N(3, 'CheckpointLoaderSimple', [40, 300], ['Illustrious-XL-v2.0.safetensors'], [], [outp('MODEL','MODEL'), outp('CLIP','CLIP'), outp('VAE','VAE')]),
    N(4, 'CLIPTextEncode', [640, 40], ['1girl, solo, full body, masterpiece, best quality', None], [inp('text','STRING'), inp('clip','CLIP')], [outp('CONDITIONING','CONDITIONING')]),
    N(5, 'CLIPTextEncode', [640, 300], ['lowres, bad anatomy, bad hands, extra fingers, missing fingers, fused fingers, cropped, worst quality', None], [inp('text','STRING'), inp('clip','CLIP')], [outp('CONDITIONING','CONDITIONING')]),
    N(6, 'EmptyLatentImage', [940, 40], [832, 1216, 1], [], [outp('LATENT','LATENT')]),
    N(7, 'ControlNetApplyAdvanced', [940, 300], [1.0, 0.0, 1.0], [inp('positive','CONDITIONING'), inp('negative','CONDITIONING'), inp('control_net','CONTROL_NET'), inp('image','IMAGE'), inp('vae','VAE')], [outp('positive','CONDITIONING'), outp('negative','CONDITIONING')]),
    N(8, 'KSampler', [1240, 40], [12345, 28, 7.0, 'euler', 'normal', 1.0], [inp('model','MODEL'), inp('positive','CONDITIONING'), inp('negative','CONDITIONING'), inp('latent_image','LATENT')], [outp('LATENT','LATENT')]),
    N(9, 'VAEDecode', [1540, 40], [], [inp('samples','LATENT'), inp('vae','VAE')], [outp('IMAGE','IMAGE')]),
    N(10, 'SaveImage', [1540, 300], ['openpose_out'], [inp('images','IMAGE')], [outp('IMAGE','IMAGE')]),
]

links = [
    [1, 1, 0, 7, 3, 'IMAGE'],     # skeleton -> ControlNetApply.image
    [2, 2, 0, 7, 2, 'CONTROL_NET'],
    [3, 3, 1, 4, 1, 'CLIP'],      # clip -> pos
    [4, 3, 1, 5, 1, 'CLIP'],      # clip -> neg
    [5, 4, 0, 7, 0, 'CONDITIONING'],
    [6, 5, 0, 7, 1, 'CONDITIONING'],
    [7, 3, 2, 7, 4, 'VAE'],
    [8, 3, 0, 8, 0, 'MODEL'],
    [9, 7, 0, 8, 1, 'CONDITIONING'],
    [10, 7, 1, 8, 2, 'CONDITIONING'],
    [11, 6, 0, 8, 3, 'LATENT'],
    [12, 8, 0, 9, 0, 'LATENT'],
    [13, 3, 2, 9, 1, 'VAE'],
    [14, 9, 0, 10, 0, 'IMAGE'],
]

for l in links:
    lid, fn, fs, tn, ts, typ = l
    nodes[tn-1]['inputs'][ts]['link'] = lid
    nodes[fn-1]['outputs'][fs]['links'].append(lid)

wf = {'id': str(uuid.uuid4()), 'revision': 0, 'last_node_id': 10, 'last_link_id': 14,
      'nodes': nodes, 'links': links, 'groups': [], 'config': {}, 'extra': {}, 'version': 0.4}

path = r'E:\ComfyUI_windows_portable\ComfyUI\user\default\workflows\OpenPoseIllustrious.json'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
print('written', path)
print('nodes', len(nodes), 'links', len(links))
