"""R06 scene adapter. Upstream source copies are immutable; no numeric gate changes."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[n]='1'
import ast,copy,json,math,sys,types,hashlib,itertools,time
from pathlib import Path
import xml.etree.ElementTree as E
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
SPEC=json.loads((H/'sources/stations.json').read_text(encoding='utf-8'))
INIT=json.loads((H/'sources/initial_joints.json').read_text(encoding='utf-8'))
sys.path.insert(0,str(H/'upstream_r05'))
from distance import Bounds
from point_bound import PointBound
import fast_bounds
fast_bounds.install()
def write(n,v):
 (H/n).parent.mkdir(parents=True,exist_ok=True);(H/n).write_text(json.dumps(v,indent=2,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist() if isinstance(x,np.ndarray) else str(x)),encoding='utf-8')
def fmt(a):return ' '.join(f'{float(v):.12g}' for v in a)
def quat(r):return fmt(r.as_quat()[[3,0,1,2]])
WORLD_TOOL=Rotation.from_euler('x',180,degrees=True)
PREP_LOCAL=Rotation.from_euler('y',-90,degrees=True)
TARGET_ROT=(WORLD_TOOL*PREP_LOCAL).as_matrix()
def exact_functions(file,classname,names,env):
 tree=ast.parse((H/'upstream_r05'/file).read_text(encoding='utf-8'))
 ns=tree.body if classname is None else next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==classname).body
 nodes=[n for n in ns if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in names]
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(H/'upstream_r05'/file),'exec'),env)
 return {n:env[n] for n in names}
REF=dict(np=np,mujoco=mujoco,math=math,PAD=0.,MU=.5,SF=1.5,NORMAL_SUM_N=150.,KEY_FORCE_N=150.,KEY_MOMENT_NM=15.)
exact_functions('reference.py',None,['offset_vector','rotation'],REF)
RM=exact_functions('reference.py','Checker',['forbidden','grip','side','gripper'],REF)
ARM=['R_'+n for n in ('shoulder_pan_joint','shoulder_lift_joint','elbow_joint','wrist_1_joint','wrist_2_joint','wrist_3_joint')]
CK=types.SimpleNamespace(ARMS={'R':ARM},JOINTS=ARM,LIM={n:{'continuous_Nm':1} for n in ARM})
for _n in ('MU','SF','NORMAL_SUM_N','KEY_FORCE_N','KEY_MOMENT_NM','offset_vector'):setattr(CK,_n,REF[_n])
ENV=dict(np=np,mujoco=mujoco,json=json,HERE=H,ck=CK)
TM=exact_functions('solver.py','Checker',['torque_multi','grip_side'],ENV)
def namespaced():
 r=E.parse(H/'sources/ur5e/ur5e.xml').getroot()
 for e in r.iter():
  if e.tag=='mesh':
   p=e.get('file');e.set('name',e.get('name',Path(p).stem));e.set('file',str((H/'sources/ur5e/assets'/p).resolve()))
 for i,g in enumerate(r.findall('.//worldbody//geom')):
  if not g.get('name'):g.set('name',f'geom_{i}')
 for e in r.iter():
  for a in ('name','class','childclass','mesh','material','joint','joint1','joint2','body1','body2','target'):
   if a in e.attrib:e.set(a,'R_'+e.get(a))
 for b in r.findall('.//worldbody//body'):b.set('name','R_arm_'+b.get('name')[2:])
 for b in r.findall('.//worldbody//body'):
  for g in list(b.findall('geom')):
   if 'visual' in g.get('class','') and b.get('name')!='R_arm_base':b.remove(g)
   else:
    if b.get('name')=='R_arm_base':g.attrib.pop('class',None);g.set('type','mesh')
    g.set('contype','2');g.set('conaffinity','3');g.set('margin','.01')
 r.find(".//joint[@name='R_elbow_joint']").set('range',fmt(np.radians([-160,160])))
 return r
def make_scene(variant=1,held=None,at=None,container_poses=None):
 wt=WORLD_TOOL if variant<2 else Rotation.from_euler('z',180,degrees=True)*WORLD_TOOL
 tr=(wt*PREP_LOCAL).as_matrix()
 r=E.Element('mujoco',model='R06_workstation');E.SubElement(r,'compiler',angle='radian',autolimits='true')
 E.SubElement(r,'option',gravity='0 0 -9.81',integrator='implicitfast');d=E.SubElement(r,'default');E.SubElement(d,'geom',margin='.01',friction='.5 .005 .0001')
 vis=E.SubElement(r,'visual');E.SubElement(vis,'global',offwidth='1440',offheight='960');assets=E.SubElement(r,'asset');w=E.SubElement(r,'worldbody')
 E.SubElement(w,'geom',name='floor',type='box',pos='0 .375 -.025',size='1 1 .025',rgba='.25 .28 .30 1')
 bodies={};changes=[]
 for item in SPEC['bodies']:
  p=copy.deepcopy(item);pos=p['pose']['position_m'];ori=p['pose']['quaternion_wxyz'];n=p['id']
  # Replace the rear cantilever by a top mount; preserve its two full-sized solids.
  if variant and n=='robot_pedestal':pos=[0,.70,1.89];changes.append(n)
  if variant>=3 and n.startswith('carrier_'):pos[2]+=.012
  if variant>=4 and n=='follower':pos[0]+=.08
  if variant>=4 and n=='cell_clamp_left':pos[0]-=.08
  if variant>=4 and n=='cell_clamp_right':pos[0]+=.08
  if variant>=5 and n=='blade_carriage':pos[2]+=.31
  if variant>=7 and n=='dry_controller':
   pos=[0,.31,.40];p['mass_kg']=12
  if container_poses and n in container_poses:pos=container_poses[n]
  parent=w if p['parent']=='world' else bodies[p['parent']]
  if variant>=5 and n in ('wash_brush','root_roller'):
   park=E.SubElement(parent,'body',name=n+'_parking_stage',pos=fmt(pos));E.SubElement(park,'joint',name=n+'_parking_joint',type='slide',axis='-1 0 0' if n=='wash_brush' else '0 1 0',range='0 .175' if n=='wash_brush' else '0 .085')
   E.SubElement(park,'inertial',mass='.3',pos='0 0 0',diaginertia='.001 .001 .001');parent=park;pos=[0,0,0]
  b=E.SubElement(parent,'body',name=n,pos=fmt(pos),quat=fmt(ori));bodies[n]=b
  E.SubElement(b,'inertial',pos=fmt(p.get('com_local_m',[0,0,0])),mass=str(p['mass_kg']),diaginertia=fmt(p.get('inertia_kg_m2',[.001]*3)))
  j=p.get('joint')
  if j:
   if j['type']=='free':E.SubElement(b,'freejoint',name=n+'_joint')
   else:
    rg=j['range']
    if variant>=5 and n=='cell_door':rg=[0,.6]
    if variant>=5 and n=='blade_carriage':rg=[0,.585]
    if variant>=6 and n=='access_door':rg=[-1.6,0]
    E.SubElement(b,'joint',name=n+'_joint',type=j['type'],axis=fmt(j['axis']),range=fmt(rg),damping='1')
  for g in p['geometry']:
   args=dict(name=g['id'],type=g['type'],pos=fmt(g['pose']['position_m']),quat=fmt(g['pose']['quaternion_wxyz']),rgba=fmt(g.get('rgba',[.65,.7,.74,1])),contype='1',conaffinity='2')
   args['size']=fmt(np.array(g['size_m'])/2) if g['type']=='box' else fmt([g['radius_m'],g['height_m']/2])
   if variant>=7 and g['id']=='controller_box':args['size']=fmt(np.maximum(g['size_m'],[.460,.254,.449])/2)
   if variant>=2 and g['id'].startswith(('key_','clean_leaf_key')):
    v=np.array(g['pose']['position_m']);v[2]+=.02;args['pos']=fmt(v)
   if variant>=6 and g['id'].startswith('wash_lift_'):
    v=np.array(g['pose']['position_m']);v[0]*=.10/.115;args['pos']=fmt(v)
   if variant>=6 and g['id'] in ('cell_land_a','cell_land_b'):
    v=np.array(g['pose']['position_m']);v[0]*=.09/.115;v[2]+=.012;args['pos']=fmt(v)
   if variant and n=='robot_pedestal':
    if g['id']=='pedestal_post':args['quat']=quat(Rotation.from_euler('y',90,degrees=True))
    else:args['pos']='0 -.1 0'
   if variant>=4 and g['id'] in ('cell_roof','cell_front_header'):
    # Park complete guards upward; retain all solids and close before processing.
    hinge=E.SubElement(b,'body',name=g['id']+'_retract',pos='0 .175 .52')
    E.SubElement(hinge,'joint',name=g['id']+'_retract_joint',type='hinge',axis='1 0 0',range='-1.6 0');E.SubElement(hinge,'inertial',mass='1',pos='0 0 0',diaginertia='.005 .005 .005')
    args['pos']=fmt(np.array(g['pose']['position_m'])-[0,.175,.52]);E.SubElement(hinge,'geom',**args)
   else:E.SubElement(b,'geom',**args)
 # Fixed mounting coordinate implemented as an immobile slide, no rail movement.
 mount=E.SubElement(w,'body',name='rail_structure',pos=fmt([0,.648,1.34] if not variant else [0,.53,1.77]),quat=quat(Rotation.from_euler('x',90 if not variant else 155,degrees=True)))
 E.SubElement(mount,'joint',name='R_carriage_x',type='slide',axis='1 0 0',range='-1e-12 1e-12');E.SubElement(mount,'inertial',mass='.001',pos='0 0 0',diaginertia='1e-6 1e-6 1e-6')
 arm=namespaced()
 for a in arm.find('default'):d.append(copy.deepcopy(a))
 for a in arm.find('asset'):assets.append(copy.deepcopy(a))
 armroot=copy.deepcopy(arm.find('worldbody/body'));mount.append(armroot)
 if variant>=7:
  # A connected rigid bolted mount, not a floating orientation transform.
  # The original post and plate retain their dimensions. The plate is turned
  # to the OEM base plane; the post is transverse at the roof rear.
  rmt=Rotation.from_euler('x',155,degrees=True);base=np.array([0,.53,1.77])
  frame=bodies['robot_pedestal'];w.remove(frame);mount.append(frame)
  frame.set('name','R_frame_pedestal');frame.set('pos','0 0 0');frame.set('quat','1 0 0 0')
  for g in frame.findall('geom'):
   if g.get('name')=='pedestal_post':
    g.set('pos',fmt(rmt.inv().apply(np.array([0,.687,1.87])-base)));g.set('quat',quat(rmt.inv()*Rotation.from_euler('y',90,degrees=True)))
   else:g.set('pos','0 0 -.008');g.set('quat',quat(Rotation.from_euler('x',90,degrees=True)))
   g.set('name','R_mount_'+g.get('name'));g.set('contype','2');g.set('conaffinity','3')
  for x in (-.065,.065):
   a=[x,0,-.029];b=rmt.inv().apply(np.array([x,.687,1.834])-base)
   E.SubElement(frame,'geom',name='R_mount_brace_'+('left' if x<0 else 'right'),type='capsule',fromto=fmt([*a,*b]),size='.014',rgba='.42 .46 .50 1',contype='2',conaffinity='3')
  # Complete the load path to the module frame. These fixed workstation
  # members are environment geometry for every moving arm/held-object gate.
  # Only the physically bolted fixed assembly shares the mount weld identity.
  for n in ('frame','worktop'):
   b=bodies[n];w.remove(b);mount.append(b)
   wp=np.fromstring(b.get('pos'),sep=' ');wr=Rotation.from_quat(np.fromstring(b.get('quat'),sep=' ')[[1,2,3,0]])
   b.set('pos',fmt(rmt.inv().apply(wp-base)));b.set('quat',quat(rmt.inv()*wr))
  bridge=E.SubElement(mount,'body',name='workstation_overhead_bridge',pos=fmt(rmt.inv().apply(np.array([0,.687,1.87])-base)),quat=quat(rmt.inv()))
  E.SubElement(bridge,'inertial',mass='8',pos='0 0 -.4',diaginertia='.6 1.3 1.6')
  E.SubElement(bridge,'geom',name='overhead_crossbeam',type='box',size='.675 .020 .020',rgba='.38 .42 .45 1',contype='1',conaffinity='2')
  for sign in (-1,1):
   E.SubElement(bridge,'geom',name='overhead_column_'+str(sign),type='box',pos=fmt([sign*.655,0,-.47]),size='.020 .020 .480',rgba='.38 .42 .45 1',contype='1',conaffinity='2')
  E.SubElement(w,'geom',name='controller_drip_shield',type='box',pos='0 .31 .65',size='.25 .235 .004',rgba='.4 .44 .48 1',contype='1',conaffinity='2')
  for n,x,z,rad in [('cold_water_coupler',-.56,.25,.017),('drain_coupler',-.50,.16,.022)]:
   E.SubElement(w,'geom',name=n,type='cylinder',pos=fmt([x,.726,z]),quat=quat(Rotation.from_euler('x',90,degrees=True)),size=fmt([rad,.016]),rgba='.3 .45 .58 1',contype='1',conaffinity='2')
  E.SubElement(w,'geom',name='single_household_power_inlet',type='box',pos='.1 .736 .23',size='.03 .014 .04',rgba='.15 .18 .21 1',contype='1',conaffinity='2')
 flange=armroot.find(".//site[@name='R_attachment_site']");par=next(b for b in armroot.iter('body') if flange in list(b));ap=np.fromstring(flange.get('pos'),sep=' ');ar=Rotation.from_quat(np.fromstring(flange.get('quat'),sep=' ')[[1,2,3,0]])
 tool=E.SubElement(par,'body',name='R_tool',pos=fmt(ap),quat=quat(ar))
 E.SubElement(tool,'inertial',mass='1',pos='0 0 .08',diaginertia='.005 .005 .002')
 eoat=SPEC['EOAT']['geometry']
 for g in eoat:
  if g['id'] in ('eoat_key_left','eoat_key_right'):continue
  E.SubElement(tool,'geom',name='R_'+g['id'],type='box',pos=fmt(g['pose']['position_m']),size=fmt(np.array(g['size_m'])/2),rgba=fmt(g['rgba']),contype='2',conaffinity='3')
 for sign,l in ((-1,'minus'),(1,'plus')):
  g=next(g for g in eoat if g['id']==('eoat_key_left' if sign<0 else 'eoat_key_right'))
  b=E.SubElement(tool,'body',name='R_jaw_'+l,pos=fmt(g['pose']['position_m']));E.SubElement(b,'joint',name='R_jaw_'+l,type='slide',axis=fmt([-sign,0,0]),range='-.01 .04' if variant>=5 else '0 .04')
  E.SubElement(b,'inertial',mass='.1',pos='0 0 0',diaginertia='.00002 .00008 .00008');E.SubElement(b,'geom',name='R_'+g['id'],type='box',pos='0 0 0',size=fmt(np.array(g['size_m'])/2),rgba=fmt(g['rgba']),contype='2',conaffinity='3')
 E.SubElement(tool,'site',name='R_prep',pos='0 0 .09',quat=quat(PREP_LOCAL),size='.004')
 com=[0,0,0]
 if held:
  obj=bodies[held];w.remove(obj)
  weighted=[]
  def accumulate(b,p=np.zeros(3),rot=Rotation.identity(),root=True):
   if not root:
    p=p+rot.apply(np.fromstring(b.get('pos','0 0 0'),sep=' '));rot=rot*Rotation.from_quat(np.fromstring(b.get('quat','1 0 0 0'),sep=' ')[[1,2,3,0]])
   ine=b.find('inertial');mass=float(ine.get('mass'));weighted.append((mass,p+rot.apply(np.fromstring(ine.get('pos','0 0 0'),sep=' '))))
   for child in b.findall('body'):accumulate(child,p.copy(),rot,False)
  accumulate(obj)
  assembly_com=sum(kg*p for kg,p in weighted)/sum(kg for kg,p in weighted)
  free=obj.find('freejoint');obj.remove(free)
  gp=np.array(next(g for g in SPEC['grasp_handles'] if g['object_id']==held)['pose_local']['position_m']);gp[2]+=.02 if variant>=2 else 0
  rt=tr;obj.set('pos',fmt(np.array([0,0,.09])-wt.inv().apply(gp)));obj.set('quat',quat(wt.inv()));tool.append(obj)
  obj.set('name','R_held_'+held)
  for b in obj.iter('body'):
   if b is not obj:b.set('name','R_held_'+b.get('name'))
   # External held mass is added exactly once by unchanged reference wrench.
   ine=b.find('inertial');ine.set('mass','1e-9');ine.set('diaginertia','1e-12 1e-12 1e-12')
   for g in b.findall('geom'):g.set('name','R_held_'+g.get('name'));g.set('contype','2');g.set('conaffinity','3')
  com=rt.T@(assembly_com-np.array(gp))
 for sn in ('work','mass'):E.SubElement(tool,'site',name='R_'+sn,pos=fmt(np.array([0,0,.09])+PREP_LOCAL.apply(com if sn=='mass' else [0,0,0])),size='.001')
 used={g.get('mesh') for g in r.findall('.//worldbody//geom') if g.get('mesh')}
 for a in list(assets.findall('mesh')):
  if a.get('name') not in used:assets.remove(a)
 return E.tostring(r,encoding='unicode'),com
class Cell:
 forbidden_literal=RM['forbidden'];grip=RM['grip'];side=RM['side'];gripper=RM['gripper'];torque_multi=TM['torque_multi'];grip_side=TM['grip_side']
 def __init__(self,variant=1,held=None,container_poses=None):
  self.xml,self.com=make_scene(variant,held,container_poses=container_poses);self.m=mujoco.MjModel.from_xml_string(self.xml);self.d=mujoco.MjData(self.m);m=self.m
  self.variant=variant;self.rot=TARGET_ROT if variant<2 else (Rotation.from_euler('z',180,degrees=True)*WORLD_TOOL*PREP_LOCAL).as_matrix()
  self.jid={m.joint(i).name:i for i in range(m.njnt)};self.qa={n:int(m.jnt_qposadr[j]) for n,j in self.jid.items()};self.da={n:int(m.jnt_dofadr[j]) for n,j in self.jid.items()}
  self.gnames=[m.geom(i).name for i in range(m.ngeom)];self.bnames=[m.body(b).name.lower() for b in m.geom_bodyid];self.weld=m.body_weldid[m.geom_bodyid]
  self.robot=np.array([n.startswith('R_') for n in self.gnames]);self.held=np.array([n.startswith('R_held_') for n in self.gnames]);self.acm=set();self.intended=set();self.allowed=[];self.contact_windows=[];self.working_stroke=False;self.held_id=held
  self.q0=m.qpos0.copy()
  for n,v in INIT.items():
   if n in self.qa and m.jnt_type[self.jid[n]] in (2,3):self.q0[self.qa[n]]=v
  for n in ('R_jaw_minus','R_jaw_plus'):self.q0[self.qa[n]]=.005 if held else 0
  if variant>=4:
   self.q0[self.qa['wash_lift_joint']]=.12
   for n in ('cell_roof_retract_joint','cell_front_header_retract_joint'):self.q0[self.qa[n]]=-1.6
  if variant>=5:
   self.q0[self.qa['wash_brush_parking_joint']]=.175;self.q0[self.qa['root_roller_parking_joint']]=.085;self.q0[self.qa['cell_door_joint']]=.6
   if not held:
    for n in ('R_jaw_minus','R_jaw_plus'):self.q0[self.qa[n]]=-.01
  self.d.qpos[:]=self.q0;mujoco.mj_forward(m,self.d);self.bounds=Bounds(self,required)
 def set_contacts(self,hands):self.hands=hands;self.allowed=[]
 def forbidden(self,q):return contacts(self,q)[0]
 def pose(self,q):
  self.d.qpos[:]=q;mujoco.mj_kinematics(self.m,self.d);sid=self.m.site('R_prep').id;return self.d.site_xpos[sid].copy(),self.d.site_xmat[sid].reshape(3,3).copy()
 def solve(self,target,rot,q0):
  q=np.array(q0).copy();ix=[self.qa[n] for n in ARM];bounds=np.array([self.m.jnt_range[self.jid[n]] for n in ARM]).T
  def res(x):
   q[ix]=x;p,r=self.pose(q);return np.r_[(p-target)*10,Rotation.from_matrix(rot.T@r).as_rotvec()*2]
  ls=least_squares(res,np.clip(q[ix],bounds[0]+1e-8,bounds[1]-1e-8),bounds=bounds,max_nfev=100,ftol=1e-7,xtol=1e-7,gtol=1e-7);q[ix]=ls.x;p,r=self.pose(q)
  return q,dict(position_mm=float(np.linalg.norm(p-target)*1000),orientation_deg=float(np.linalg.norm(Rotation.from_matrix(rot.T@r).as_rotvec())*180/math.pi),evaluations=ls.nfev)
def required(ch,a,b):
 ra,rb=ch.robot[a],ch.robot[b]
 if not ra and not rb:return None
 m=ch.m
 if ch.weld[a]==ch.weld[b] or tuple(sorted((a,b))) in ch.acm:return None
 wa,wb=ch.weld[a],ch.weld[b]
 if ra and rb and (m.body_weldid[m.body_parentid[wa]]==wb or m.body_weldid[m.body_parentid[wb]]==wa):return None
 if ra and rb:
  if ch.gripper(a) and ch.gripper(b) and ch.side(a)==ch.side(b):return None
  return (0.,'self') if ch.side(a)==ch.side(b) else (.01,'arm_arm')
 g=a if ra else b
 return (.005,'held_gripper_environment') if ch.gripper(g) or ch.held[g] else (.01,'robot_environment')
def permitted(ch):
 allow=set()
 cw=getattr(ch,'capture_window',None)
 if cw and cw['kind']=='grasp_release_support' and cw['support_id']=='eoat_key_capture':
  owner=cw.get('object_id');own_key=('key_'+owner.removeprefix('output_')) if isinstance(owner,str) and owner.startswith('output_') else 'clean_leaf_key' if owner=='clean_leaf_basket' else None
  p,r=ch.pose(ch.d.qpos.copy());dp=p-np.array(cw['tcp_origin_m']);axis=np.array(cw['normal']);t=dp@axis
  if np.linalg.norm(dp-t*axis)<=2e-5 and -2e-5<=t<=.05000001 and np.max(abs(r-np.array(cw['tcp_rotation'])))<=.0002:
   for a_name,b_name in cw['pairs']:
    if own_key is None or a_name not in (own_key,'R_held_'+own_key) or b_name not in ('R_eoat_key_left','R_eoat_key_right'):continue
    a,b=(ch.gnames.index(n) for n in (a_name,b_name));valid=True
    if ch.bounds.pair(a,b)['lower_m']>=.005-1e-6:continue
    for c in ch.d.contact[:ch.d.ncon]:
     if c.dist>0 or set(map(int,c.geom))!={a,b}:continue
     local=ch.d.geom_xmat[a].reshape(3,3).T@(c.pos-ch.d.geom_xpos[a]);normal=ch.d.geom_xmat[a].reshape(3,3).T@c.frame[:3]
     if abs(normal[0])<.85 or abs(abs(local[0])-ch.m.geom_size[a,0])>.00002:valid=False
    if valid:allow.add(frozenset([a_name,b_name]))
 for w in ch.contact_windows:
  if w.get('kind') not in ('grasp_release_support','working_stroke') or w.get('object_id')!=ch.held_id:continue
  # R06 review finding 1: a supplied support label is not authorization.
  # Resolve the exact face against the scene's interface registry.
  registry=getattr(ch,'support_registry',{
   **{'dock_'+p:{'faces':['dock_'+p+'_land'],'objects':['output_'+p]} for p in ('carrot','potato','bok_choy','tomato')},
   'wash_basin':{'faces':['wash_lift_left','wash_lift_right'],'objects':['output_'+p for p in ('carrot','potato','bok_choy','tomato')]+['clean_leaf_basket']},
   'process_cell':{'faces':['cell_land_a','cell_land_b'],'objects':['output_'+p for p in ('carrot','potato','bok_choy','tomato')]+['clean_leaf_basket']},
   'inspection_dock':{'faces':['inspection_land'],'objects':['clean_leaf_basket']}})
  owner=registry.get(w.get('support_id'),{})
  if w.get('face') not in owner.get('faces',[]) or w.get('object_id') not in owner.get('objects',[]):continue
  if w['kind']=='working_stroke' and not ch.working_stroke:continue
  p,r=ch.pose(ch.d.qpos.copy());dp=p-np.array(w['tcp_origin_m']);axis=np.array(w['normal']);t=dp@axis
  if not np.isclose(np.linalg.norm(axis),1,atol=1e-8):continue
  if w['kind']=='grasp_release_support':
   support_geom=ch.gnames.index(w['face']);face_normal=ch.d.geom_xmat[support_geom].reshape(3,3)[:,2]
   if np.linalg.norm(axis-face_normal)>1e-8:continue
  if np.linalg.norm(dp-t*axis)>2e-5 or not -2e-5<=t<=.05000001 or np.max(abs(r-np.array(w['tcp_rotation'])))>.0002:continue
  for name in w['held_parts']:
   canonical='R_held_'+name
   if canonical not in ch.gnames:continue
   body=int(ch.m.geom_bodyid[ch.gnames.index(canonical)]);own=False
   while body:
    if ch.m.body(body).name=='R_held_'+w['object_id']:own=True;break
    body=int(ch.m.body_parentid[body])
   if not own:continue
   pair=frozenset([w['face'],'R_held_'+name])
   if not pair.issubset(set(ch.gnames)):continue
   a,b=[ch.gnames.index(n) for n in pair]
   if ch.bounds.pair(a,b)['lower_m']>=.005-1e-6:continue
   valid=True
   for c in ch.d.contact[:ch.d.ncon]:
    if c.dist>0 or set(map(int,c.geom))!={a,b}:continue
    g=ch.gnames.index(w['face']);local=ch.d.geom_xmat[g].reshape(3,3).T@(c.pos-ch.d.geom_xpos[g]);normal=ch.d.geom_xmat[g].reshape(3,3).T@c.frame[:3]
    if ch.m.geom_type[g]!=6 or abs(normal[2])<.85 or local[2]<ch.m.geom_size[g,2]-.00002:valid=False
   if valid:allow.add(pair)
 return allow
def contacts(ch,q):
 for n,j in ch.jid.items():
  if ch.m.jnt_type[j] in (2,3) and ch.m.jnt_limited[j]:
   lo,hi=ch.m.jnt_range[j];v=q[ch.qa[n]]
   if not lo-1e-9<=v<=hi+1e-9:
    return [dict(pair=[n,'physical_joint_limit'],q=float(v),range=[float(lo),float(hi)],reason='Actual released joint range; no fictitious rail travel')],{},dict(proof='Joint-domain rejection before gap audit')
 literal=ch.forbidden_literal(q);allow=permitted(ch)
 negative=[];earlymins={}
 for row in literal:
  if row['real_gap_mm']>=-.001 or frozenset(row['pair']) in allow:continue
  a,b=(ch.gnames.index(n) for n in row['pair']);req=required(ch,a,b)
  if req is None:continue
  negative.append(row);need,cat=req
  val=dict(pair=row['pair'],clearance_mm=row['real_gap_mm'],required_mm=need*1000,reserve_mm=row['real_gap_mm']-need*1000,lower_bound=False,method='Unchanged literal reference signed penetration witness; failed-state short circuit, not global minimum')
  if cat not in earlymins or val['reserve_mm']<earlymins[cat]['reserve_mm']:earlymins[cat]=val
 if negative:return negative,earlymins,dict(proof='Rejected by unchanged literal reference penetration witness; all-pair certificate unnecessary to reject',intended_pairs=[sorted(x) for x in allow])
 hits,mins,proof=ch.bounds.check(frozenset(allow))
 for row in literal:
  if frozenset(row['pair']) in allow:continue
  # Positive margin contacts never override a valid exact shape lower bound.
  a,b=(ch.gnames.index(n) for n in row['pair'])
  if row['real_gap_mm']>0 and ch.bounds.pair(a,b)['lower_m']>=row['required_gap_mm']/1000-1e-6:continue
  if required(ch,a,b) is not None:hits.append(row)
 return hits,mins,dict(proof=proof,intended_pairs=[sorted(x) for x in allow])
def hand(ch,pos,load='carry'):
 kg=0 if ch.held_id is None else next(a['combined_mass_kg'] for a in SPEC['grasp_handles'] if a['object_id']==ch.held_id)
 force=next(a for a in SPEC['force_cases'] if a['id']==load)
 # Carry acceleration acts at the assembly CoM, not at the grasp key.
 # The copied wrench routine applies forces at R_work (the key). Its adapter
 # supplies the equivalent r x F couple; grip_side already uses this offset.
 offset=list(ch.com) if load=='carry' else [0,0,0]
 return {'R':dict(pos=list(pos),held='empty' if ch.held_id is None else ch.held_id,held_kg=kg,work_offset_m=offset,mass_offset_m=list(ch.com),grip='keyed',contacts=[],load_case_id=load,force_application='held_assembly_CoM' if load=='carry' else 'key_loading_point',check_forces_N=[force['force_N'],list(-np.array(force['force_N']))],check_moments_Nm=[force.get('moment_Nm',[0,0,0])])}
s=types.SimpleNamespace(ck=CK,model=types.SimpleNamespace(SIDES=('R',)),PARK=None)
# Original planner is loaded unchanged. This named adapter supplies its scene API.
sys.modules['final_check']=sys.modules[__name__]
from planner_r05 import Planner
