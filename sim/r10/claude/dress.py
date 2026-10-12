"""Render-only look for a scene tree; the checker never uses this.
Adds the UR5e visual meshes (MuJoCo Menagerie), the user's kitchen colours from
RoboCasa textures (warm wood cabinets, dark red-brown granite, white tiles,
stainless), RoboCasa food meshes sized to fit inside the checked shapes, and lights
with shadows. Checked geometry stays in the model, moved to group HIDE (not drawn)."""
from pathlib import Path
import os,copy,numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
SIM=Path(__file__).resolve().parents[2]
MEN=SIM/'r01/concept/sources/menagerie/universal_robots_ur5e'
RC=SIM/'vendor/robocasa/robocasa/models/assets'
HIDE=5
def gen(kind,i):return RC/'generative_textures'/kind/sorted(os.listdir(RC/'generative_textures'/kind))[i]
# name: (texture file or None, rgba, texrepeat per metre or None, specular, shininess, reflectance)
MAT={'counter':(RC/'textures/marble/granite.png',(.52,.38,.33,1),2.,.6,.8,.12),
 'cab':(gen('cabinet',8),(1,1,1,1),1.5,.25,.3,0),'tile':(gen('floor',9),(1,1,1,1),1.6,.7,.8,.06),
 'floor':(gen('floor',5),(1,1,1,1),.8,.2,.2,.05),'wall':(RC/'textures/cream-plaster.png',(1,1,1,1),1.,.1,.1,0),
 'steel':(RC/'textures/metals/bright_metal.png',(.62,.64,.67,1),4.,.9,.9,.2),'wood':(gen('cabinet',2),(1,1,1,1),3.,.2,.2,0),
 'white':(None,(.86,.86,.84,1),None,.3,.3,0),'dark':(None,(.15,.15,.16,1),None,.3,.3,0),'cart':(None,(.82,.83,.84,1),None,.4,.4,0),
 'rubber':(None,(.07,.07,.07,1),None,.1,.1,0),'grip':(None,(.20,.21,.23,1),None,.6,.6,0),'pad':(None,(.92,.90,.85,1),None,.2,.2,0),
 'glass':(None,(.05,.05,.06,1),None,.9,.9,.2),'alu':(None,(.76,.78,.81,1),None,.6,.6,.05),'ceramic':(None,(.96,.96,.95,1),None,.6,.6,.05),
 'clear':(None,(.82,.86,.9,.55),None,.8,.8,0),'tpu':(None,(.2,.55,.75,1),None,.2,.2,0),'petg':(None,(.88,.9,.93,1),None,.4,.5,0)}
RULES=[(('counter_',),'counter'),(('north_cabinet','sink_cabinet','south_cabinets','upper_cabinet','r07_closed_door'),'cab'),
 (('north_wall',),'tile'),(('south_wall',),'wall'),(('sink_','dish_rack','wash_basket','slicer_out_bowl','lever_','R_held_lever'),'steel'),
 (('faucet_',),'steel'),(('stove','gas_knob'),'glass'),(('outlet','door_pause','appliance_power','raw_pad','slicer_base','slicer_spout','stored_bowl'),'white'),
 (('reel_case','floor_cable','wash_cradle'),'dark'),(('raw_tray','raw_rib'),'wood'),(('P16_','peel_','linear_peeler'),'alu'),(('slicer_chute',),'clear'),
 (('R_cart_chassis','R_cart_mast','R_cart_beam','R_cart_electrics','R_base_plate','R_current151mm'),'cart'),(('R_cart_wheel','R_dock_bumper'),'rubber'),
 (('R_gripper_','G_gripper_'),'grip'),(('R_finger_','G_finger_'),'pad')]
HIDDEN=('R_geom_','south_','protected_stove')  # arm collision capsules, camera-side walls, keep-out envelope
FOOD={'tomato':RC/'objects/objaverse/tomato/tomato_0','carrot':RC/'objects/objaverse/carrot/carrot_2',
 'potato':RC/'objects/objaverse/potato/potato_1','greens':RC/'objects/aigen_objs/lettuce/lettuce_0'}
FOOD_GEOMS={'raw_tomato':'tomato','R_held_tomato':'tomato','raw_carrot':'carrot','R_held_carrot':'carrot','raw_potato':'potato','raw_greens':'greens'}
def food_asset(kind):
 x=E.parse(FOOD[kind]/'model.xml').getroot();me=next(m for m in x.iter('mesh') if m.get('file','').startswith('visual/'))
 tx=next(t for t in x.iter('texture') if t.get('file','').startswith('visual/'))
 return FOOD[kind]/me.get('file'),me.get('refquat','1 0 0 0'),FOOD[kind]/tx.get('file')
def mesh_box(f,refquat):
 """AABB of an OBJ (scale 1, given refquat) in the frame of a geom at pos 0, quat 1."""
 m=mujoco.MjModel.from_xml_string(f'<mujoco><asset><mesh name="p" file="{f.as_posix()}" refquat="{refquat}"/></asset><worldbody><geom type="mesh" mesh="p"/></worldbody></mujoco>')
 d=mujoco.MjData(m);mujoco.mj_forward(m,d);v=m.mesh_vert[m.mesh_vertadr[0]:m.mesh_vertadr[0]+m.mesh_vertnum[0]]
 w=d.geom_xpos[0]+v@d.geom_xmat[0].reshape(3,3).T;return w.min(0),w.max(0)
def fmt(v):return ' '.join(f'{float(x):.9g}' for x in v)
def dress(tree):
 tree=copy.deepcopy(tree);root=tree.getroot();asset=root.find('asset');world=root.find('worldbody')
 base=mujoco.MjModel.from_xml_string(E.tostring(root,encoding='unicode'))
 # lights, shadows, sky
 vis=root.find('visual');E.SubElement(vis,'headlight',ambient='.22 .22 .22',diffuse='.26 .26 .26',specular='.05 .05 .05')
 E.SubElement(vis,'quality',shadowsize='4096',offsamples='8')
 E.SubElement(asset,'texture',name='sky',type='skybox',builtin='gradient',rgb1='.95 .96 .98',rgb2='.78 .81 .85',width='256',height='1536')
 for nm,x in (('key_a',-1.3),('key_b',.1)):
  E.SubElement(world,'light',name=nm,pos=fmt([x,-.9,2.5]),dir=fmt([0,.45,-1]),cutoff='62',exponent='2',diffuse='.42 .41 .39',specular='.2 .2 .2',castshadow='true')
 E.SubElement(world,'light',name='fill',directional='true',dir='.2 .6 -.8',diffuse='.22 .22 .22',specular='0 0 0',castshadow='false')
 for k,(tf,rgba,rep,spec,shin,refl) in MAT.items():
  a=dict(name='M_'+k,rgba=fmt(rgba),specular=str(spec),shininess=str(shin),reflectance=str(refl))
  if tf:E.SubElement(asset,'texture',name='T_'+k,type='2d',file=Path(tf).as_posix());a.update(texture='T_'+k,texrepeat=fmt([rep,rep]),texuniform='true')
  E.SubElement(asset,'material',**a)
 # UR5e visual meshes onto the R_arm_* bodies
 have={m.get('name') for m in asset.iter('mesh')}
 for me in E.parse(MEN/'ur5e.xml').getroot().find('asset').iter('mesh'):
  st=Path(me.get('file')).stem
  if 'R_'+st not in have:E.SubElement(asset,'mesh',name='R_'+st,file=(MEN/'assets'/me.get('file')).as_posix())
 for b in E.parse(MEN/'ur5e.xml').getroot().find('worldbody').iter('body'):
  ours=root.find(f".//body[@name='R_arm_{b.get('name')}']")
  for g in b.findall('geom'):
   if g.get('class')!='visual':continue
   a=dict(name='R_vis_'+g.get('mesh'),type='mesh',mesh='R_'+g.get('mesh'),material='R_'+g.get('material'),contype='0',conaffinity='0',group='2')
   for k in ('pos','quat'):
    if g.get(k):a[k]=g.get(k)
   E.SubElement(ours,'geom',**a)
 # materials and hiding by name
 for g in root.iter('geom'):
  n=g.get('name','')
  if n.startswith(HIDDEN) or (g.get('rgba') and float(g.get('rgba').split()[3])==0):g.set('group',str(HIDE));continue
  if n.startswith('G_jaw_'):
   # R12 finger parts in the physics model: soft pads / Fin Ray front strap TPU, structure PETG
   k='tpu' if any(t in n for t in ('softpad','_pad','_ch','_pk','_f')) else 'petg';g.set('material','M_'+k);g.attrib.pop('rgba',None);continue
  if n=='floor':g.set('material','M_floor');g.attrib.pop('rgba',None);continue
  for pre,k in RULES:
   if n.startswith(pre):g.set('material','M_'+k);g.attrib.pop('rgba',None);break
 # food meshes fitted inside the checked food shapes (attached to the same body)
 for gi in range(base.ngeom):
  n=base.geom(gi).name;kind=FOOD_GEOMS.get(n)
  if not kind:continue
  t=base.geom_type[gi];s=base.geom_size[gi]
  if t==mujoco.mjtGeom.mjGEOM_CYLINDER:c,h=np.zeros(3),np.array([s[0],s[0],s[1]])
  elif t==mujoco.mjtGeom.mjGEOM_CAPSULE:c,h=np.zeros(3),np.array([s[0],s[0],s[1]+s[0]])
  elif t==mujoco.mjtGeom.mjGEOM_MESH:c,h=base.geom_aabb[gi][:3],base.geom_aabb[gi][3:]
  else:c,h=np.zeros(3),np.array(s[:3])
  # Fit in the raw OBJ frame: the long axis of an elongated item (carrot) maps to
  # the shape's long axis and is stretched to fill it; other axes scale uniformly.
  f,_,tx=food_asset(kind);lo,hi=mesh_box(f,'1 0 0 0');e=hi-lo;mc=(hi+lo)/2
  a_,b_=int(np.argmax(e)),int(np.argmax(h));long_=kind in('carrot',)
  A=np.eye(3) if a_==b_ or not long_ else Rotation.from_rotvec(np.pi/2*np.cross(np.eye(3)[a_],np.eye(3)[b_])).as_matrix()
  r=2*h/(abs(A)@e);sc=np.full(3,.97*float(np.min(r) if not long_ else np.min(np.delete(r,b_))))
  if long_:sc[a_]=.97*r[b_]
  Q=base.geom_quat[gi];Rg=Rotation.from_quat(Q[[1,2,3,0]]).as_matrix()
  pos=base.geom_pos[gi]+Rg@(c-A@(sc*mc));q=Rotation.from_matrix(Rg@A).as_quat()[[3,0,1,2]]
  E.SubElement(asset,'texture',name=f'T_{n}',type='2d',file=tx.as_posix());E.SubElement(asset,'material',name=f'M_{n}',texture=f'T_{n}',specular='.35',shininess='.4')
  E.SubElement(asset,'mesh',name=f'F_{n}',file=f.as_posix(),scale=fmt(sc))
  bid=base.geom_bodyid[gi];parent=world if bid==0 else root.find(f".//body[@name='{base.body(bid).name}']")
  E.SubElement(parent,'geom',name=f'F_{n}',type='mesh',mesh=f'F_{n}',material=f'M_{n}',pos=fmt(pos),quat=fmt(q),contype='0',conaffinity='0',group='1')
  root.find(f".//geom[@name='{n}']").set('group',str(HIDE))
 return mujoco.MjModel.from_xml_string(E.tostring(root,encoding='unicode'))
