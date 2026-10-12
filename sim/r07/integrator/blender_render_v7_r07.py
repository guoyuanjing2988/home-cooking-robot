"""CPU-only Cycles; no OpenGL or GPU rendering. <=1440px."""
import bpy,json,sys,math,time
from pathlib import Path
from mathutils import Matrix,Vector
args=sys.argv[sys.argv.index('--')+1:];path=Path(args[0]).resolve();data=json.loads(path.read_text());began=time.monotonic()
if 'meshes_file' in data:
 import hashlib
 source=(path.parent/data['meshes_file']).resolve();assert source.parent==path.parent
 blob=source.read_bytes();assert hashlib.sha256(blob).hexdigest()==data['meshes_sha256']
 data['meshes']=json.loads(blob)
bpy.context.preferences.filepaths.temporary_directory=str(path.parent/'tmp')
(path.parent/'tmp').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials={}
def material(rgba,name):
    # Display colours distinguish mechanisms; geometry remains exact MJCF.
    if name.startswith('R_'):rgba=(.12,.34,.72,1)
    elif name.startswith('L_'):rgba=(.92,.34,.09,1)
    elif name.startswith(('rail_','cable_carrier_','wall_mount_')):rgba=(.20,.24,.29,1)
    elif name.startswith('appliance_power_'):rgba=(.55,.22,.72,1)
    elif name.startswith(('cell_','front_','covered_tool_')):rgba=(.22,.53,.53,1)
    key=tuple(round(x,3) for x in rgba)
    if key not in materials:
        m=bpy.data.materials.new(name);m.diffuse_color=(*rgba[:3],1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgba[:3],1)
        p.inputs['Roughness'].default_value=.35 if 'geom_' in name else .60
        p.inputs['Metallic'].default_value=.45 if any(k in name for k in ('rail','faucet','knife','carriage')) else .05
        materials[key]=m
    return materials[key]
meshes={}
for n,a in data['meshes'].items():
    mesh=bpy.data.meshes.new(n);mesh.from_pydata(a['vertices'],[],a['faces']);mesh.update();meshes[n]=mesh
for a in data['geoms']:
    if time.monotonic()-began>180:raise TimeoutError('scene construction >180sec')
    typ=a['type'];s=a['size'];name=a['name']
    if typ==7:
        o=bpy.data.objects.new(name,meshes[a['mesh']]);bpy.context.collection.objects.link(o)
    elif typ==6:
        bpy.ops.mesh.primitive_cube_add(size=2);o=bpy.context.object;o.scale=s
    elif typ==2:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=s[0]);o=bpy.context.object
    elif typ in (3,5):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=s[0],depth=2*s[1]);o=bpy.context.object
        if typ==3:
            for sign in (-1,1):
                bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=s[0]);cap=bpy.context.object;cap.parent=o;cap.location=(0,0,sign*s[1]);cap.data.materials.append(material(a['rgba'],name))
    elif typ==0:
        bpy.ops.mesh.primitive_plane_add(size=12);o=bpy.context.object
    else:continue
    o.name=name;o.location=a['pos'];o.rotation_euler=Matrix(a['rot']).to_euler();o.data.materials.append(material(a['rgba'],name))
    if typ not in (6,0):
        for p in o.data.polygons:p.use_smooth=True
    if typ==6:
        b=o.modifiers.new('Small manufactured edge bevel','BEVEL');b.width=.002;b.segments=2
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=6;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=1
scene.render.resolution_x=data.get('resolution',[1200,800])[0];scene.render.resolution_y=data.get('resolution',[1200,800])[1];scene.render.resolution_percentage=100;scene.cycles.samples=data.get('samples',6)
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.45,.50,.60,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.12
for loc,power,size in [((0,-2,4),500,5),((-3,1,3),300,3),((3,0,2.5),250,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size
    o.rotation_euler=(Vector((-.3,.2,1))-o.location).to_track_quat('-Z','Y').to_euler()
label=data['label'];focus=Vector((-.4,.3,1.05)) if 'washing' in label else Vector((-.935,.17,1.05)) if label in ('peeling','eye_core') else Vector((.30,.30,1.05))
if data.get('focus'):focus=Vector(data['focus'])
if label=='overview':focus=Vector((-.3,.0,1.2));campos=Vector((3.4,-5.6,3.6));scale=5.5
elif label in ('parked','passing'):focus=Vector((-.3,.0,1.1));campos=Vector((3.4,-5.6,1.6));scale=5.5
else:campos=focus+Vector((1.9,-2.9,.35));scale=2.7
bpy.ops.object.camera_add(location=campos);camera=bpy.context.object;camera.rotation_euler=(focus-campos).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=scale;scene.camera=camera
if data.get('camera_scale'):scale=data['camera_scale'];camera.data.ortho_scale=scale
# Embedded visual label distinguishes admitted and rejected witnesses.
bpy.ops.object.text_add();txt=bpy.context.object;txt.data.body=f"{data['config']['arm']} / {data['config']['count']} arms, {data['config'].get('lane_count',2)} rail(s) | {label}\n{data['status']}\nBlue: single UR5e / red: stove exclusion";txt.data.size=.055;txt.data.extrude=0
txt.parent=camera;txt.location=(-scale*.46,scale*.29,-3);txt.rotation_euler=(0,0,0)
labelmat=bpy.data.materials.new('Unlit annotation');labelmat.use_nodes=True
nodes=labelmat.node_tree.nodes;nodes.clear();em=nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.025,.035,.05,1);em.inputs['Strength'].default_value=1
out=nodes.new('ShaderNodeOutputMaterial');labelmat.node_tree.links.new(em.outputs[0],out.inputs['Surface']);txt.data.materials.append(labelmat)
if True:
    txt.data.size=scale*.020
    bpy.ops.mesh.primitive_plane_add(size=1);panel=bpy.context.object;panel.name='Annotation backing';panel.parent=camera
    panel.location=(0,scale*.277,-3.02);panel.rotation_euler=(0,0,0);panel.scale=(scale*.97,scale*.075,1)
    back=bpy.data.materials.new('Unlit annotation backing');back.use_nodes=True
    nodes=back.node_tree.nodes;nodes.clear();em=nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.95,.95,.95,1)
    out=nodes.new('ShaderNodeOutputMaterial');back.node_tree.links.new(em.outputs[0],out.inputs['Surface']);panel.data.materials.append(back)
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.5
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(path.with_suffix('').with_suffix('.png'))
bpy.ops.wm.save_as_mainfile(filepath=str(path.parent/'concept_preview.blend')) if label=='overview' else None
bpy.ops.render.render(write_still=True)
print('CPU_RENDER',label,round(time.monotonic()-began,2),flush=True)
