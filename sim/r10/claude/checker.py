"""Read-only import of the binding R05 checker, with stricter named contacts.

The shim only supplies model metadata at import time; the reference source is
executed unchanged, and its forbidden/grip/rotation methods are called directly.
No legacy builder is allowed to write to earlier rounds.
"""
import sys,types,importlib.util,xml.etree.ElementTree as E,json
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
from scene import H,ROOT,load,build
from mobile import floor_check,stability
from distance import Bounds
from point_bound import PointBound
ENV=load('assets/envelope.json')['envelope_Nm']
_shim=types.ModuleType('model');_shim.CONFIG={};_shim.SIDES={'R':'UR5e'}
_meta=dict(torque_limits={n:{'continuous_Nm':v} for n,v in ENV.items()},disabled_robot_pairs=[],base=['R_carriage_x'],arms={'R':list(ENV)},jaws=['R_jaw_minus','R_jaw_plus'])
_shim.build=lambda *args:(E.parse(H/'models/base.xml'),_meta)
_previous=sys.modules.get('model');sys.modules['model']=_shim
_spec=importlib.util.spec_from_file_location('r08_binding_reference',ROOT/'sim/r05/integrator/reference.py')
reference=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(reference)
if _previous is None:del sys.modules['model']
else:sys.modules['model']=_previous
assert (reference.PAD,reference.MU,reference.SF,reference.KEY_FORCE_N,reference.KEY_MOMENT_NM)==(0,.5,1.5,150,15)
class Checker(reference.Checker):
 def __init__(self,tree,meta=None):
  self.desc={'intended':[]};self.meta=meta or {};self.xml=E.tostring(tree.getroot(),encoding='unicode')
  self.bind_model(mujoco.MjModel.from_xml_string(self.xml));self.intended=set()
  mujoco.mj_forward(self.m,self.d)
  import arms;arm=arms.current(self.meta.get('config'))   # R19: the arm option (default UR5e: assets/envelope_<tilt>.json, 0.35 m, as before)
  ep=H/arms.envelope_file(self.meta.get('config',{}).get('mount_tilt_deg',0),arm);self.com_radius=arms.ARMS[arm]['com_radius_m']
  if not ep.exists():raise ValueError('actual mounting envelope missing')
  self.env=load(str(ep.relative_to(H)))['envelope_Nm']
  canonical_tree,_=build(self.meta.get('config',{}),self.meta.get('held')) if self.meta.get('config') else (tree,{})
  canonical=mujoco.MjModel.from_xml_string(E.tostring(canonical_tree.getroot(),encoding='unicode'))
  self.canonical={n:self.shape_identity(canonical,canonical.geom(n).id) for n in self.gnames if n.startswith('R_held_') or n in ('R_finger_minus','R_finger_plus','R_gripper_palm','R_gripper_oem_envelope')}
  if any(self.identity(n)!=v for n,v in self.canonical.items()):raise ValueError('canonical grasp geometry mismatch')
  self.grasp_registry={}
  item=self.meta.get('held')
  expected={'carrot':([0,0,0],[.0175,.0175,.080]),'holder':([.055,0,0],[.065,0,0])}
  if item:
   known_parts={'carrot':{'R_held_carrot'},'tomato':{'R_held_tomato'},'pusher':{'R_held_lever_pusher','R_held_lever_pusher_stem','R_held_lever_pusher_knob'},'holder':{'R_held_holder','R_held_key_shoulder-1','R_held_key_shoulder1'},'catch_tray':{'R_held_tray_handle','R_held_tray_stem','R_held_tray_floor','R_held_tray_side-1','R_held_tray_side1','R_held_tray_end-1','R_held_tray_end1','R_held_key_shoulder-1','R_held_key_shoulder1'}}
   for g,n in enumerate(self.gnames):
    if not n.startswith('R_held_'):continue
    if n not in known_parts.get(item,set()):continue
    cg=canonical.geom(n).id
    if self.shape_identity(self.m,g)!=self.shape_identity(canonical,cg):raise ValueError('noncanonical held geometry, rotation or attachment')
    if item in expected and n=='R_held_'+item:
     pos,size=expected[item]
     gp,gs=self.m.geom_pos[g],self.m.geom_size[g];tol=1e-10
     if self.m.geom_type[g]==mujoco.mjtGeom.mjGEOM_MESH:
      # R11 box mesh: compare its body-frame vertex AABB (centre, half extents).
      a_=self.m.mesh_vertadr[self.m.geom_dataid[g]];v=self.m.mesh_vert[a_:a_+self.m.mesh_vertnum[self.m.geom_dataid[g]]].astype(float)
      w=Rotation.from_quat(self.m.geom_quat[g][[1,2,3,0]]).as_matrix();v=v@w.T+gp;gp,gs=(v.max(0)+v.min(0))/2,(v.max(0)-v.min(0))/2;tol=1e-7
     if np.max(abs(gp-pos))>tol or np.max(abs(gs-size))>tol:raise ValueError('held object dimensions/frame do not match real grasp identity')
    if item=='catch_tray' and n not in {'R_held_tray_handle','R_held_key_shoulder-1','R_held_key_shoulder1'}:continue
    self.grasp_registry[n]=dict(object=item,support='R_tool',identity=self.identity(n),fingers=('R_finger_minus','R_finger_plus'))
  self.bounds=Bounds(self,self.required);self.point_bound=PointBound(self)
  self.base_ids=[self.qa[n] for n in ['R_carriage_x','base_y','base_yaw']]
  self.arm_ids=[self.qa[n] for n in ENV]
  self.active=self.base_ids+self.arm_ids
  self.registry={};self.windows=[];self.last=None
 def body_half(self,g):
  # Half extents of a mesh geom's vertex AABB in its body (tool) frame.
  a_=self.m.mesh_vertadr[self.m.geom_dataid[g]];v=self.m.mesh_vert[a_:a_+self.m.mesh_vertnum[self.m.geom_dataid[g]]].astype(float)
  w=Rotation.from_quat(self.m.geom_quat[g][[1,2,3,0]]).as_matrix();v=v@w.T
  return (v.max(0)-v.min(0))/2
 def wall_mating(self,g):
  if self.gnames[g] not in {f'r07_wall_bracket_{k}' for k in range(4)}:return False
  wall=self.gnames.index('north_wall');r=self.d.geom_xmat[g].reshape(3,3);p=self.d.geom_xpos[g];size=self.m.geom_size[g]
  return bool(np.max(abs(r-np.eye(3)))<1e-9 and abs(p[1]+size[1]-(self.d.geom_xpos[wall,1]-self.m.geom_size[wall,1]))<1e-8)
 def required(self,ch,a,b):
  ra,rb=self.robot[a],self.robot[b];m=self.m
  if not ra and not rb:return None
  names=[self.gnames[a],self.gnames[b]]
  if self.meta.get('held') and bool(self.held[a])!=bool(self.held[b]):
   held=a if self.held[a] else b;other=b if held==a else a
   if self.robot[other] and self.gripper(other):
    if self.grasp_allowed(held,other):return None
    return (0.,'self')
  if 'north_wall' in names and self.wall_mating(b if names[0]=='north_wall' else a):return None
  # R10 docked cart: only the named bumper may bear on base-cabinet fronts.
  if 'R_dock_bumper' in names:
   other=names[1] if names[0]=='R_dock_bumper' else names[0]
   if other.startswith(('north_cabinet','sink_cabinet')) and not self.robot[self.gnames.index(other)]:return None
  # Restore full non-mating OEM base-versus-rail checks even across ancestry.
  frames=('rail_beam_','rail_guide_','cable_chain_','r07_wall_tie_')
  if any(n.startswith('R_geom_') for n in names) and any(n.startswith(frames) for n in names):return (.01,'arm_arm_or_frame')
  if self.weld[a]==self.weld[b] or tuple(sorted((a,b))) in self.acm:return None
  wa,wb=self.weld[a],self.weld[b]
  if m.body_weldid[m.body_parentid[wa]]==wb or m.body_weldid[m.body_parentid[wb]]==wa:return None
  if 'floor' in names and not(self.held[a] or self.held[b]):
   other=b if names[0]=='floor' else a
   if not any(k in self.bnames[other] for k in ('arm','tool','gripper','finger')):return None
  if ra and rb:
   if self.gripper(a) and self.gripper(b) and self.side(a)==self.side(b):return None
   return (0.,'self') if self.side(a)==self.side(b) else (.01,'arm_arm_or_frame')
  g=a if ra else b
  return (.005,'held_gripper_environment') if self.gripper(g) or self.held[g] else (.01,'robot_environment')
 def grasp_allowed(self,held,finger):
  n=self.gnames[held];record=self.grasp_registry.get(n)
  return bool(record and record['object']==self.meta.get('held') and record['support']=='R_tool' and record['identity']==self.identity(n) and self.gnames[finger] in record['fingers'] and self.identity(self.gnames[finger])==self.canonical[self.gnames[finger]] and self.m.body(self.m.geom_bodyid[held]).name=='R_tool')
 def permissions(self,kind):
  mujoco.mj_forward(self.m,self.d)
  allowed=set()
  for w in self.windows:
   # Capability must come from the real registry, not text supplied by a path.
   obj=self.registry.get(w.get('object'))
   if obj is None or obj.get('support')!=w.get('support') or obj.get('parts')!=w.get('parts'):continue
   if json.dumps(w,sort_keys=True) not in obj.get('authorized_windows',[]):continue
   if obj.get('support_signature')!=self.support_signature(obj.get('faces',[])):continue
   if w.get('kind') not in ('grasp_release_support','working_stroke'):continue
   if w['kind']=='working_stroke' and kind!='working':continue
   maximum=.050000001
   if w.get('length_m',1)>maximum or w.get('face') not in obj.get('faces',[]):continue
   sid=self.m.site('R_prep').id;p=self.d.site_xpos[sid];R=self.d.site_xmat[sid].reshape(3,3)
   delta=p-np.asarray(w['origin']);n=np.asarray(w['normal']);axial=delta@n
   if np.linalg.norm(delta-axial*n)>.00002 or not(-.00002<=axial<=w['length_m']+.00002):continue
   if np.max(abs(R-np.asarray(w['rotation'])))>.0002:continue
   for part in w['parts']:
    if part not in self.gnames or w['face'] not in self.gnames:continue
    g=self.gnames.index(part)
    if not self.held[g]:continue
    # Bind the complete compiled part shape and attachment to the registry.
    if obj.get('compiled_identity')!=self.identity(part):continue
    a=self.gnames.index(w['face']);valid=True
    for c in self.d.contact[:self.d.ncon]:
     if set(map(int,c.geom))!={a,g} or c.dist>0:continue
     if w['object']=='holder' and w['face'] in ('mandoline_deck','mandoline_blade') and (w['kind']=='working_stroke' or w.get('golden_proxy_lift',False)):continue
     # Named top plane only; no permission on guard sides or below the support.
     local=self.d.geom_xmat[a].reshape(3,3).T@(c.pos-self.d.geom_xpos[a])
     if abs(local[2]-self.m.geom_size[a,2])>.0065 or abs(c.frame[2])<.85:valid=False
    if valid:allowed.add(frozenset([part,w['face']]))
  return allowed
 def set_working(self,origin,end,R):
  if 'R_held_holder' not in self.gnames:return
  parts=['R_held_holder'];faces=['mandoline_deck','mandoline_blade']
  g=self.gnames.index('mandoline_deck');gr=self.d.geom_xmat[g].reshape(3,3);gp=self.d.geom_xpos[g]
  expected=[gp+gr@np.array([x,0,.110]) for x in [-.10,.10]]
  if max(np.linalg.norm(np.asarray(p)-a) for p,a in zip([origin,end],expected))>1e-7:raise ValueError('forged working origin or support')
  self.registry['holder']=dict(support='mandoline_station',parts=parts,faces=faces,compiled_identity=self.identity(parts[0]),support_signature=self.support_signature(faces))
  delta=np.array(end)-origin;length=float(np.linalg.norm(delta))
  self.windows=[dict(kind='working_stroke',object='holder',support='mandoline_station',parts=parts,face=face,origin=(np.array(origin)+delta*k/4).tolist(),normal=(delta/length).tolist(),rotation=np.array(R).tolist(),length_m=length/4) for face in faces for k in range(4)]
  self.registry['holder']['authorized_windows']=[json.dumps(w,sort_keys=True) for w in self.windows]
 def support_signature(self,faces):
  return tuple((n,tuple(self.d.geom_xpos[self.gnames.index(n)]),tuple(self.d.geom_xmat[self.gnames.index(n)]),tuple(self.m.geom_size[self.gnames.index(n)])) for n in faces if n in self.gnames)
 def configure_target(self,t,R):
  self.windows=[];self.registry={}
  if t['name']=='mandoline_work':self.set_working(t['points'][0],t['points'][-1],R);return
  item=self.meta.get('held');part='R_held_'+str(item)
  if part not in self.gnames:return
  proxy=False
  base=t['name'].split('@')[0]
  if base=='raw_pick':
   real=self.meta['raw_objects'][item];origin=np.array(real['position'])+([0,0,__import__('scene').tomato_dz(self.meta.get('config',{}))] if item=='tomato' and self.meta.get('config',{}).get('r11_tomato') else 0);normal=[0,0,1];faces=(['raw_rib-1','raw_rib1'] if item=='carrot' else ['raw_pad_'+item]) if self.meta.get('config',{}).get('rib_tray') else ['raw_tray'];support='raw_tray'
   g=self.gnames.index(part);sz=self.m.geom_size[g]
   if self.m.geom_type[g]==mujoco.mjtGeom.mjGEOM_CYLINDER:sz=np.array([sz[0],sz[0],sz[1]])
   if self.m.geom_type[g]==mujoco.mjtGeom.mjGEOM_MESH:sz=self.body_half(g)
   extent=abs(np.array(R))@sz
   if np.max(abs(extent-np.array(real['size'])/2))>1e-7:return
   if np.linalg.norm(np.array(t['points'][0])-origin)>1e-7:return
  elif t['name'] in ('peel_load','peel_retrieve'):
   faces=['peel_cradle-1','peel_cradle1'];support='peeler_station';normal=[0,0,1] if self.meta.get('config',{}).get('peel_top') else [0,-1,0]
   gs=[self.gnames.index(n) for n in faces];origin=np.mean([self.d.geom_xpos[g] for g in gs],axis=0)
   gg=self.gnames.index(part);half=abs(np.array(R))@(self.body_half(gg) if self.m.geom_type[gg]==mujoco.mjtGeom.mjGEOM_MESH else self.m.geom_size[gg])
   # R11 peel_hover: the carrot slides in 1 mm above the cradle tops and drops 1 mm on release.
   origin[2]=max(self.d.geom_xpos[g,2]+self.m.geom_size[g,2] for g in gs)+half[2]+self.meta.get('config',{}).get('peel_hover',0.)
   expected=t['points'][-1] if t['name']=='peel_load' else t['points'][0]
   if np.linalg.norm(np.array(expected)-origin)>1e-7:return
  elif t['name']=='holder_retreat':
   faces=['mandoline_deck','mandoline_blade'];support='mandoline_station';normal=[0,0,1];proxy=True
   g=self.gnames.index('mandoline_deck');origin=self.d.geom_xpos[g]+self.d.geom_xmat[g].reshape(3,3)@np.array([.10,0,.110])
   if np.linalg.norm(np.array(t['points'][0])-origin)>1e-7:return
  elif base=='wedge_load':
   faces=['lever_blade_plate'];support='lever_station';normal=[0,0,1];origin=np.array(t['points'][-1])
  else:return
  self.registry[item]=dict(support=support,parts=[part],faces=faces,compiled_identity=self.identity(part),support_signature=self.support_signature(faces))
  self.windows=[dict(kind='grasp_release_support',object=item,support=support,parts=[part],face=f,origin=origin.tolist(),normal=normal,rotation=np.array(R).tolist(),length_m=.05,golden_proxy_lift=proxy) for f in faces]
  self.registry[item]['authorized_windows']=[json.dumps(w,sort_keys=True) for w in self.windows]
 def identity(self,part):
  g=self.gnames.index(part)
  return self.shape_identity(self.m,g)
 @staticmethod
 def shape_identity(m,g):
  b=int(m.geom_bodyid[g]);chain=[]
  while b:
   chain.append((m.body(b).name,tuple(m.body_pos[b]),tuple(m.body_quat[b]),int(m.body_jntnum[b])))
   if m.body(b).name=='R_tool':break
   b=int(m.body_parentid[b])
  return (int(m.geom_type[g]),tuple(m.geom_size[g]),tuple(m.geom_pos[g]),tuple(m.geom_quat[g]),int(m.geom_dataid[g]),tuple(chain))
 def check(self,q,kind='transfer',force=None,mass=0,work=.08,full=True):
  identity_ok=all(self.identity(n)==v for n,v in self.canonical.items())
  literal=reference.Checker.forbidden(self,np.asarray(q));allowed=self.permissions(kind)
  hits=[]
  for h in literal:
   a,b=[self.gnames.index(n) for n in h['pair']]
   if self.required(self,a,b) is not None and frozenset(h['pair']) not in allowed:hits.append(h)
  # The legacy same-gripper/weld shortcut is narrowed for held-object grasp
  # identities; wrong/fabricated attachments cannot retain that broad skip.
  if self.meta.get('held'):
   for c in self.d.contact[:self.d.ncon]:
    a,b=map(int,c.geom)
    if bool(self.held[a])==bool(self.held[b]):continue
    req=self.required(self,a,b)
    if req is not None and c.dist<req[0]-1e-6 and frozenset([self.gnames[a],self.gnames[b]]) not in allowed:
     hits.append(dict(pair=[self.gnames[a],self.gnames[b]],real_gap_mm=float(c.dist*1000),required_gap_mm=req[0]*1000,reason='strict real-object grasp identity / full held pair'))
  if full:
   more,mins,proof=self.bounds.check(frozenset(allowed));hits+=more
  else:mins={};proof={}
  ranges=bool(all(self.m.jnt_range[j,0]-1e-8<=q[a]<=self.m.jnt_range[j,1]+1e-8 for j,a in enumerate(self.m.jnt_qposadr)))
  # The inherited finger model has more unused travel than the selected PGC.
  # Keep its solids/point bound, but enforce the real50mm total actuator stroke.
  ranges=ranges and all(q[self.qa[n]]<=.025+1e-10 for n in ('R_jaw_minus','R_jaw_plus'))
  if force is None:forces=[(np.eye(3)[axis]*sign*mass*.45).tolist() for axis in range(3) for sign in [-1,1]]
  else:forces=[force]
  if self.meta.get('held')=='holder' and kind=='working':forces=[(np.array(self.meta['mandoline_rotation'])@np.array([-60,lat,20])).tolist() for lat in [-10,10]]
  loads=[self.loads(q,f,mass,work) for f in forces]
  load=max(loads,key=lambda l:max(l['max_ratio'],1/max(l['grip']['margin'],1e-12)))
  load=dict(load,ok=all(l['ok'] for l in loads),force_cases_N=forces)
  mobile=floor_check(self,q)
  tips=[stability(self,q,f,mass,work) for f in forces]
  tip=min(tips,key=lambda r:r['min_margin_m'])
  result=dict(ok=not hits and ranges and load['ok'] and mobile['ok'] and tip['ok'] and identity_ok,identity_ok=identity_ok,hits=hits[:30],clearance=mins,ranges=ranges,load=load,proof=proof,mobile=mobile,stability=tip)
  self.last=result;return result
 def loads(self,q,force,mass,work):
  self.d.qpos[:]=q;self.d.qvel[:]=0;mujoco.mj_forward(self.m,self.d)
  sid=self.m.site('R_prep').id;R=self.d.site_xmat[sid].reshape(3,3);p=self.d.site_xpos[sid];bid=self.m.site_bodyid[sid]
  item=self.meta.get('held')
  com=np.array([.08,0,0]) if item=='holder' else np.zeros(3)
  if item=='catch_tray':
   gs=[g for g,n in enumerate(self.gnames) if n.startswith('R_held_')];vol=np.array([np.prod(self.m.geom_size[g]*2) for g in gs]);com=sum(v*self.m.geom_pos[g] for g,v in zip(gs,vol))/sum(vol)
   # 0.43kg tray +0.12kg contents placed over the real tray floor.
   com=(.43*com+.12*np.array([.11,.025,0]))/.55
  work_v=np.array([work,0,0]) if item=='holder' else np.array([.0175,0,0]) if item=='carrot' else np.zeros(3)
  jp=np.zeros((3,self.m.nv));jr=jp.copy();mujoco.mj_jac(self.m,self.d,jp,jr,p+R@work_v,bid)
  jmass=jp.copy();mujoco.mj_jac(self.m,self.d,jmass,jr,p+R@com,bid)
  tau=self.d.qfrc_bias-jp.T@np.array(force)-jmass.T@np.array([0,0,-mass*9.81])
  ratios={n:float(abs(tau[self.da[n]])/max(v,1e-10)) for n,v in self.env.items()}
  # R11: the lever-cutter pusher knob seats in a key pocket of the 3D-printed
  # finger pads (form fit along the push), like the holder/tray keys.
  grip_mode='keyed' if self.meta.get('held') in ('holder','catch_tray','pusher') or not self.meta.get('held') else 'friction'
  hd=dict(held_kg=mass,work_offset_m=work_v,mass_offset_m=com,grip=grip_mode)
  grip=reference.Checker.grip(self,q,hd,force)
  eoat_ids=[self.m.body(n).id for n in ['R_tool','R_jaw_minus','R_jaw_plus']];total=mass+sum(self.m.body_mass[b] for b in eoat_ids)
  centre=(sum(self.m.body_mass[b]*self.d.xipos[b] for b in eoat_ids)+mass*(p+R@com))/total
  flange=self.m.site('R_attachment_site').id;radius=float(np.linalg.norm(centre-self.d.site_xpos[flange]))
  eoat_moment=float(np.linalg.norm(np.cross(R@work_v,np.asarray(force))+np.cross(R@com,[0,0,-mass*9.81])))
  return dict(ok=max(ratios.values())<=1 and grip['margin']>=1 and total<=5 and radius<=self.com_radius and eoat_moment<=7,ratios=ratios,max_ratio=max(ratios.values()),grip=grip,PGC_moment_Nm=eoat_moment,PGC_moment_limit_Nm=7,payload_kg=float(total),flange_com_radius_m=radius,held_com_local_m=com.tolist(),work_local_m=work_v.tolist())
 def pose_error(self,q,p,R):
  self.d.qpos[:]=q;mujoco.mj_kinematics(self.m,self.d);sid=self.m.site('R_prep').id
  return float(np.linalg.norm(self.d.site_xpos[sid]-p)),float(np.linalg.norm(Rotation.from_matrix(R@self.d.site_xmat[sid].reshape(3,3).T).as_rotvec()))
