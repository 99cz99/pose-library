import bpy
from mathutils import Vector

OUT = r'E:\ComfyUI_windows_portable\ComfyUI\input'

# ---------- 找人体网格（排除 armature/相机/灯光）----------
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and any(m.type == 'ARMATURE' for m in o.modifiers) and 'joints' not in o.name.lower()]
if not meshes:
    raise SystemExit('NO_MESH: 场景里没有带骨架的网格，请先 File -> Import -> FBX 导入人体')

# 隐藏角色以外的网格（默认 Cube 等会遮挡人体下半身）
for o in bpy.data.objects:
    if o.type == 'MESH' and o not in meshes:
        o.hide_render = True

# ---------- 摆后姿态的包围盒（用 depsgraph 拿形变网格，不是 T-pose）----------
depsgraph = bpy.context.evaluated_depsgraph_get()
mins = Vector((1e9, 1e9, 1e9))
maxs = Vector((-1e9, -1e9, -1e9))
for o in meshes:
    oe = o.evaluated_get(depsgraph)
    me = oe.to_mesh()
    if me is None:
        continue
    for v in me.vertices:
        w = oe.matrix_world @ v.co
        mins.x = min(mins.x, w.x); mins.y = min(mins.y, w.y); mins.z = min(mins.z, w.z)
        maxs.x = max(maxs.x, w.x); maxs.y = max(maxs.y, w.y); maxs.z = max(maxs.z, w.z)
    oe.to_mesh_clear()
center = (mins + maxs) / 2.0
size = maxs - mins

# ---------- 材质：普通（浅灰发光）----------
body_mat = bpy.data.materials.get('BodyMat')
if body_mat is None:
    body_mat = bpy.data.materials.new('BodyMat')
    body_mat.use_nodes = True
    bn = body_mat.node_tree.nodes
    bn.clear()
    bem = bn.new('ShaderNodeEmission')
    bem.inputs['Color'].default_value = (0.85, 0.85, 0.88, 1.0)
    bout = bn.new('ShaderNodeOutputMaterial')
    body_mat.node_tree.links.new(bem.outputs['Emission'], bout.inputs['Surface'])

# ---------- 材质：深度（相机距离 → 亮度，近亮远暗）----------
depth_mat = bpy.data.materials.get('DepthMat')
if depth_mat is None:
    depth_mat = bpy.data.materials.new('DepthMat')
    depth_mat.use_nodes = True
    dn = depth_mat.node_tree.nodes
    dl = depth_mat.node_tree.links
    dn.clear()
    cam = dn.new('ShaderNodeCameraData')
    cam.location = (-400, 0)
    mr = dn.new('ShaderNodeMapRange')
    mr.location = (-150, 0)
    mr.inputs['To Min'].default_value = 1.0
    mr.inputs['To Max'].default_value = 0.0
    em = dn.new('ShaderNodeEmission')
    em.location = (150, 0)
    out = dn.new('ShaderNodeOutputMaterial')
    out.location = (400, 0)
    dl.new(cam.outputs['View Distance'], mr.inputs['Value'])
    dl.new(mr.outputs['Result'], em.inputs['Color'])
    dl.new(em.outputs['Emission'], out.inputs['Surface'])

def assign(mat):
    for o in meshes:
        mats = o.data.materials
        if len(mats) == 0:
            mats.append(mat)
        else:
            for i in range(len(mats)):
                mats[i] = mat

# ---------- 相机：正交，正前方自动框全身（无透视，适合姿势参考）----------
import math
dist = max(size.z, size.y) * 2.0 + 1.0
cam_obj = bpy.context.scene.camera
if cam_obj is None:
    cam_data = bpy.data.cameras.new('Cam')
    cam_obj = bpy.data.objects.new('Cam', cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
cam_obj.data.type = 'ORTHO'
cam_obj.data.ortho_scale = max(size.z, size.x * (1536.0 / 1024.0)) * 1.15
cam_obj.location = Vector((center.x, center.y - dist, center.z))
cam_obj.rotation_euler = (math.pi / 2, 0.0, 0.0)  # 看向 +Y，up 为 +Z

# 深度映射范围：跟着相机距离走，让人体落在「近=亮」区间
mr_node = next(n for n in depth_mat.node_tree.nodes if n.bl_idname == 'ShaderNodeMapRange')
mr_node.inputs['From Min'].default_value = dist - 0.2
mr_node.inputs['From Max'].default_value = dist + 1.0

# ---------- 渲染设置 ----------
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1024
scene.render.resolution_y = 1536
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.cycles.samples = 32

# 普通图
assign(body_mat)
scene.render.filepath = OUT + r'\blender_pose_render.png'
bpy.ops.render.render(write_still=True)
print('RENDER:', scene.render.filepath)

# 深度图
assign(depth_mat)
scene.render.filepath = OUT + r'\blender_pose_depth.png'
bpy.ops.render.render(write_still=True)
print('DEPTH:', scene.render.filepath)

print('DONE')
