"""CPU EEVEE layout render from actual FreeCAD STL solids, 1500px max."""
import bpy, json, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
manifest=json.load(open(os.path.join(ROOT,'cad','cad_manifest.json'),encoding='utf-8'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=10
scene.render.threads_mode='FIXED';scene.render.threads=1
scene.render.resolution_x=1500;scene.render.resolution_y=840;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.70,.74,.80,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.15
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.5
def material(name,color,metal=0,alpha=1):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,alpha);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,alpha);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.38;p.inputs['Alpha'].default_value=alpha
    if alpha<1:p.inputs['Transmission Weight'].default_value=.55
    return m
for item in manifest['instances']:
    path=os.path.join(ROOT,item['mesh'])
    bpy.ops.wm.stl_import(filepath=path)
    o=bpy.context.object;o.name=item['name'];o.scale=(.001,.001,.001)
    alpha=.25 if item['name']=='PressGuards' or 'GuardDoor' in item['name'] else 1
    o.data.materials.append(material(item['name'],item['color'],.6 if item['color'][0]==.55 else .1,alpha))
def cube(name,loc,scale,color):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material(name,color));return o
cube('backwall',(-.1,.64,.4),(3.75,.025,.85),(.86,.86,.82))
# Cabinet outlines are above actual work area; transparent/open-door region reserved.
for x,w in [(-1.25,1.1),(.29,.8)]:cube('uppercabinet',(x,.415,.80),(w,.37,.60),(.72,.76,.78))
# Simplified existing faucet envelope only, never a changed installation.
cube('faucet_stem',(-.4,.56,.155),(.049,.049,.15),(.55,.64,.68))
cube('faucet_spout',(-.4,.49,.216),(.0715,.18,.068),(.55,.64,.68))
cube('floor',(-.4,.1,-.07),(4.1,1.6,.025),(.93,.93,.91))
def text_obj(body,location,size=.055,rotation=(0,0,0),color=(.03,.08,.11)):
    c=bpy.data.curves.new('label','FONT');c.body=body;c.size=size;c.align_x='CENTER';c.extrude=0
    o=bpy.data.objects.new('label',c);scene.collection.objects.link(o);o.location=location;o.rotation_euler=rotation;o.data.materials.append(material('ink',color));return o
for label,x in [('CARROT',-1.665),('POTATO',-1.415),('GREENS',-1.165),('TOMATO',-.915)]:text_obj(label,(x,.435,.205),.031)
for label,loc in [('RAW',(-1.615,.04,.105)),('DRAIN',(-1.295,.04,.13)),('PEEL',(-.935,.04,.145)),('TOOLS',(0,.04,.14)),('GUARDED CUT CELL',(.40,.065,.395)),('STOVE KEEP-OUT',(1.08,.28,.055))]:text_obj(label,loc,.037)
text_obj('R02  |  Robot-friendly preparation',(-.58,-.38,.09),.07)
text_obj('One powered cell  /  Removable food paths  /  Dimensions in counter frame',(-.58,-.49,.09),.034)
bpy.ops.object.light_add(type='AREA',location=(-.5,-.7,2.5));bpy.context.object.data.energy=100;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=4
bpy.ops.object.light_add(type='AREA',location=(1.7,.2,1.6));bpy.context.object.data.energy=40;bpy.context.object.data.size=2
bpy.ops.object.camera_add(location=(2.0,-3.8,3.7));cam=bpy.context.object
direction=Vector((-.45,.27,.15))-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4.7;scene.camera=cam
scene.render.filepath=os.path.join(ROOT,'renders','layout_perspective.png');bpy.ops.render.render(write_still=True)
# Annotatedplanisgeneratedseparatelyfromthesamedimensionregistry; cabinetswouldoccludetopview.
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'renders','layout.blend'))
print('RENDERS_DONE',flush=True)
