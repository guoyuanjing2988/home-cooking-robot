"""Isolated layout runtime, full both-arm checker and staged scene."""
import os,json,copy,xml.etree.ElementTree as E
from pathlib import Path
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
H=Path(__file__).resolve().parent;O=H/'results';ID=os.environ.get('R07_LAYOUT','L03')
cfg=json.loads((O/'layouts'/f'{ID}.json').read_text());P=json.loads((O/'layouts'/f'{ID}_process.json').read_text());baseline=json.loads((O/'v1_process_v3.json').read_text())
import r07_model
r07_model.CONFIG=cfg
import r07_runtime as rt
s=rt.s;f=rt.f
_base_payload=f.payload
def payload(ch,q,hands):
 rows=_base_payload(ch,q,hands)
 for row in rows:
  side=row['side'];arm=cfg['arms'][0 if side=='R' else 1]
  if arm=='xArm6':
   row['OEM_payload_chart_ok']=row['total_flange_kg']<=2 and row['CoM_xy_m']<=.200 and abs(row['CoM_flange_m'][2])<=.180
   row['chart_gate']='xArm6 documented conservative2kg curve: <=200mm radial and<=180mm axial, including EOAT; no UR5e chart applied to xArm principal'
   if side=='R':row['principal_3kg_service_qualified']=False
 return rows
f.payload=payload
raw_build=r07_model.build
def build(config=None):
 c=dict(cfg if config is None else config);empty=bool(c.get('transport_only'));tr,meta=raw_build(dict(c,transport_only=True));w=tr.getroot().find('worldbody')
 if not empty:
  for a in baseline['installed_geometry']:
   if a['name'].startswith('slicer_'):continue
   a=copy.deepcopy(a)
   if a['name']=='secondary_drive_guard':a['pos']=[-1.27,.47,.70]
   if a['name']=='presence_sensor':a['pos']=next(g['pos'] for g in P['installed_geometry'] if g['name']=='presence_sensor')
   if a['type']=='box':s.model.box(w,a['name'],a['pos'],a['size'],robot=False,color=a.get('rgba',(.5,.65,.6,1)))
   else:s.model.shell(w,a['name'],a['pos'],a['size'],robot=False)
  s.model.box(w,'bfp610_complete_envelope',[.425,.16,1.0475],[.395,.295,.395],robot=False,color=(.2,.3,.38,1))
 meta['config']=c;return tr,meta
s.model.CONFIG=cfg;s.model.build=build;s.ck.build=build;s.P=P;s.ck.configure(cfg)
Base=rt.Checker
def group(n):
 if n.startswith(('raw_','staged_raw_')):return 'raw'
 if n.startswith('peel_') or n=='clamped_food':return 'peel'
 if n.startswith('secondary_'):return 'secondary'
 if n.startswith('bfp610_'):return 'slicer'
 if n.startswith('root_brush_'):return 'wash'
 if n.startswith('dock_'):return next(('dock_'+t for t in ('peeler','wash_pad','eye_core_spoon') if n.startswith('dock_'+t)),None)
 if n.startswith('output_'):return 'output_leafy_greens' if n.startswith('output_leafy_greens') else 'output_'+n.split('_')[1]
 return None
def move_xml(root,include_bodies=True):
 w=root.find('worldbody')
 for g in w.findall('geom'):
  name=g.get('name','');st=group(name)
  if st:
   if st=='wash' and st not in cfg['station_frames']:continue
   fr=cfg['station_frames'][st];r=Rotation.from_euler('z',fr['yaw_deg'],degrees=True);pos=np.fromstring(g.get('pos','0 0 0'),sep=' ');g.set('pos',s.model.fmt(r.apply(pos-fr['old_center'])+fr['new_center']))
   old=Rotation.from_quat(np.fromstring(g.get('quat','1 0 0 0'),sep=' ')[[1,2,3,0]]);g.set('quat',s.model.quat(r*old))
  if name=='secondary_drive_guard':g.set('pos',s.model.fmt([cfg['station_frames']['secondary']['new_center'][0],.47,.70]))
  if name=='secondary_open_lid':g.set('pos',s.model.fmt(cfg['lid_storage']['center_m']));g.set('quat',s.model.quat(Rotation.from_euler('xyz',cfg['lid_storage']['rotation_deg'],degrees=True)))
 if cfg.get('peel_horizontal_supports'):
  rods=sorted((g for g in w.findall('geom') if g.get('name','').startswith('peel_riser_')),key=lambda g:g.get('name'))
  assert len(rods)==4
  for i,g in enumerate(rods):
   pc=cfg['station_frames']['peel']['new_center']
   g.set('pos',s.model.fmt([pc[0]+(-.12,-.04,.04,.12)[i],pc[1],.859]));g.set('quat',s.model.quat(Rotation.from_euler('x',90,degrees=True)))
 if include_bodies:
  for body in w.findall('body'):
   n=body.get('name','')
   if n.startswith('stored_bowl_'):
    prod=n[len('stored_bowl_'):];fr=cfg['station_frames']['output_'+prod];pos=np.fromstring(body.get('pos'),sep=' ');pos[:2]=np.array(fr['new_center'])[:2];body.set('pos',s.model.fmt(pos))
   elif n.startswith('stored_') and n[len('stored_'):] in ('peeler','wash_pad','eye_core_spoon'):
    fr=cfg['station_frames']['dock_'+n[len('stored_'):]];pos=np.fromstring(body.get('pos'),sep=' ');body.set('pos',s.model.fmt(pos-np.array(fr['old_center'])+fr['new_center']))
 s.model.box(w,'bfp_receiving_bowl_land',[.10,.115,.856],[.21,.21,.012],robot=False)
 s.model.box(w,'secondary_lid_storage_slot',[.65,.17,.86],[.025,.29,.020],robot=False)
class Checker(Base):
 def __init__(self,ph,sg,c=None):
  super().__init__(ph,sg,cfg);root=E.fromstring(self.xml);move_xml(root);self.xml=E.tostring(root,encoding='unicode');self.bind_model(mujoco.MjModel.from_xml_string(self.xml));self.set_contacts(self.hands)
 def torque_multi(self,q,hands,forces,moments=None):
  # Same inherited demand equation, evaluated directly so an alternative
  # principal's joint names never look up the selected UR5e global envelope.
  m,d=self.m,self.d;d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d);tau=d.qfrc_bias.copy();jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
  for side,h in hands.items():
   force=np.array(forces[side]);moment=np.array((moments or {}).get(side,[0,0,0]))
   # A zero external wrench contributes exactly zero. Empty-hand auxiliary
   # deployment may use the other arm without inventing a nonexistent work
   # site; native arm/EOAT gravity above remains fully included.
   if np.any(force) or np.any(moment):
    mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_work').id);tau-=jp.T@force+jr.T@moment
   if h['held_kg']:
    mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_mass').id);tau-=jp.T@np.array([0,0,-h['held_kg']*9.81])
  result=dict(demand_Nm={n:float(abs(tau[self.da[n]])) for n in s.ck.JOINTS},reference_type='rated_payload_envelope',published_output_torque_ratios=None)
  file=O/'layouts'/f'{ID}_envelope.json'
  if file.exists():
   env=json.loads(file.read_text())['envelope_Nm'];rat={n:v/env[n] for n,v in result['demand_Nm'].items()};joint=max(rat,key=rat.get);result.update(ratio=rat[joint],joint=joint,required_Nm=result['demand_Nm'][joint],reference_Nm=env[joint],joints=rat)
  else:raise RuntimeError('No rated-payload envelope for actual mount '+ID)
  return result
rt.Checker=Checker;s.Checker=Checker;rt.SUPPORT_REGISTRY.clear();rt.WORK_REGISTRY.clear()
for ph in P['phases']:
 for sg in ph['segments']:
  for hands in sg['poses']:
   for h in hands.values():
    for c in h.get('contacts',[]):(rt.WORK_REGISTRY if c['kind']=='working_stroke' else rt.SUPPORT_REGISTRY).setdefault(rt.object_identity(h),set()).add(c['face'])
items=[(p,sg,p['id']+'__'+sg['label'].replace(' ','_')) for p in P['phases'] for sg in p['segments']]
def scene(index):
 ph,sg,key=items[index];ch=Checker(ph,sg);root=E.fromstring(ch.xml);w=root.find('worldbody');active={h['product'] for h in sg['poses'][0].values() if h['held'] in ('root_food','food_cup','cut_cassette','colander','carried_bowl')}
 if w.find("geom[@name='clamped_food']") is not None:active.add(next(iter(sg['poses'][0].values()))['product'])
 completed={'carrot':index>40,'potato':index>79,'leafy_greens':index>91,'tomato':index>99}
 fr=cfg['station_frames']['raw'];r=Rotation.from_euler('z',fr['yaw_deg'],degrees=True)
 for prod,x,y in [('carrot',-1.685,.095),('potato',-1.535,.095),('leafy_greens',-1.685,.245),('tomato',-1.535,.245)]:
  if prod in active:continue
  size=next(a['input_size_m'] for a in P['finished_products'] if a['product']==prod)
  if completed[prod]:
   body=w.find("body[@name='stored_bowl_"+prod+"']")
   if body is not None:s.model.box(body,'retained_contents_'+prod,[.179-size[2]/2,0,0],[size[2],size[1],size[0]],robot=False)
  else:s.model.box(w,'staged_raw_'+prod,r.apply(np.array([x,y,.942+size[2]/2])-fr['old_center'])+fr['new_center'],size,robot=False)
 ch.xml=E.tostring(root,encoding='unicode');ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.set_contacts(sg['poses'][0]);return ch
