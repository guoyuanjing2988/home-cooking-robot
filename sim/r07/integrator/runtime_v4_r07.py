"""Night process/fixture adapter on the immutable R05 checker stack."""
import json,copy,xml.etree.ElementTree as E,os
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
import runtime_v2_r07 as v
H=v.H;O=v.O;ID=v.ID;cfg=v.cfg;P=json.loads((O/'layouts'/f'{ID}_process_v4.json').read_text())
original_scene=v.scene
v.P=P;v.s.P=P
items=[(p,sg,p['id']+'__'+sg['label'].replace(' ','_')) for p in P['phases'] for sg in p['segments']]
v.items=items
base_intentional=v.f.intentional
def oriented_intentional(ch,contact):
 if not cfg.get('horizontal_tool_docks'):return base_intentional(ch,contact)
 names=[ch.gnames[int(g)] for g in contact.geom]
 for c in ch.allowed:
  if c['face'] not in ('dock_wash_pad_face','dock_eye_core_spoon_face'):continue
  if c.get('kind')!='grasp_release_support' or c.get('object_id')!=v.rt.object_identity(ch.hands[c['side']]):continue
  for part in c['held_parts']:
   if set(names)!={c['face'],c['side']+'_held_'+part}:continue
   g=ch.gnames.index(c['face']);r=ch.d.geom_xmat[g].reshape(3,3);p=r.T@(contact.pos-ch.d.geom_xpos[g]);sz=ch.m.geom_size[g]
   return bool(abs(np.array(contact.frame[:3])@r[:,2])>=.85 and p[2]>=sz[2]-.0065 and all(abs(p[i])<=sz[i]+.0065 for i in (0,1)))
 if any(n in ('dock_wash_pad_face','dock_eye_core_spoon_face') for n in names):return False
 return base_intentional(ch,contact)
v.f.intentional=oriented_intentional
def scene(index):
 ph,sg,key=items[index]
 ch=v.Checker(ph,sg);v.s.ck.ARMS.setdefault('L',[]);root=E.fromstring(ch.xml);w=root.find('worldbody')
 # The commodity machine removes the retired hand-peeler and its dock,
 # not the eye/core fixture, residual wash tools, or any kitchen geometry.
 for g in list(w.findall('geom')):
  if g.get('name','').startswith('dock_peeler'):w.remove(g)
 body=w.find("body[@name='stored_peeler']")
 if body is not None:w.remove(body)
 if cfg.get('horizontal_tool_docks'):
  r=Rotation.from_euler('x',90,degrees=True)
  for typ in ('wash_pad','eye_core_spoon'):
   x,y,_=cfg['station_frames']['dock_'+typ]['new_center'];pivot=np.array([x,y,1.0])
   nodes=[g for g in w.findall('geom') if g.get('name','').startswith('dock_'+typ)]
   body=w.find("body[@name='stored_"+typ+"']")
   if body is not None:nodes.append(body)
   for node in nodes:
    pos=np.fromstring(node.get('pos'),sep=' ');node.set('pos',v.s.model.fmt(pivot+r.apply(pos-pivot)+[0,0,cfg.get('horizontal_dock_lift',0)]))
    old=Rotation.from_quat(np.fromstring(node.get('quat','1 0 0 0'),sep=' ')[[1,2,3,0]]);node.set('quat',v.s.model.quat(r*old))
   lift=cfg.get('horizontal_dock_lift',0);forward=cfg.get('stand_forward',0)
   v.s.model.box(w,'dock_'+typ+'_new_stand',[x+.035,y+.125-forward,.97+lift/2],[.020,.020,.24+lift],robot=False)
   v.s.model.box(w,'dock_'+typ+'_new_foot',[x+(.05 if typ=='wash_pad' else .025),y+.12-forward,.855],[.09,.09,.010],robot=False)
 x,y=cfg['m5_center_xy']
 if cfg.get('peeler_model')=='Rotato Express':
  v.s.model.box(w,'rotato_complete_guard_reservation',[x,y,1.025],[.300,.300,.350],robot=False,color=(.55,.60,.62,1))
 else:v.s.model.box(w,'sammic_m5_complete_exterior',[x,y,1.095],[.333,.367,.490],robot=False,color=(.55,.60,.62,1))
 # OEM's bottom water/drain hoses: conservative fixed service routing below
 # counter, within original wall/counter footprint. No robot contact waived.
 v.s.model.box(w,'m5_water_drain_service',[x,.505,.69],[.12,.15,.25],robot=False)
 active={h['product'] for h in sg['poses'][0].values() if h['held'] in ('root_food','food_cup','cut_cassette','colander','carried_bowl')}
 if sg.get('source_stroke_index')==87:v.s.model.box(w,'wash_food',[-.23,.17,.96],[.17,.03,.012],robot=False)
 if w.find("geom[@name='clamped_food']") is not None:active.add(next(iter(sg['poses'][0].values()))['product'])
 # Same complete stationary objects in every diagnostic, not a claimed
 # persistent meal scene. Final sequence explicitly records missing events.
 for prod,x,y in [('carrot',-.995,.085),('potato',-.845,.085),('leafy_greens',-.995,.235),('tomato',-.845,.235)]:
  if prod in active:continue
  size=next(a['input_size_m'] for a in P['finished_products'] if a['product']==prod)
  if index==len(items)-1:
   body=w.find("body[@name='stored_bowl_"+prod+"']")
   if body is not None:v.s.model.box(body,'retained_contents_'+prod,[.179-size[2]/2,0,0],[size[2],size[1],size[0]],robot=False)
   continue
  if cfg.get('staged_food_matches_lands'):
   land=w.find("geom[@name='raw_"+prod+"_land']");pos=np.fromstring(land.get('pos'),sep=' ');half=np.fromstring(land.get('size'),sep=' ');x,y=pos[:2];z=pos[2]+half[2]+size[2]/2
  else:z=.942+size[2]/2
  v.s.model.box(w,'staged_raw_'+prod,[x,y,z],size,robot=False)
 ch.xml=E.tostring(root,encoding='unicode');ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.set_contacts(sg['poses'][0]);return ch
v.scene=scene
for name in ('rt','s','f','Checker'):globals()[name]=getattr(v,name)
