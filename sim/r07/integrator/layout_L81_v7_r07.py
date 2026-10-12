"""Full processor forward on counter; side grasp preserves full world food."""
import os,json,copy
import numpy as np
from scipy.spatial.transform import Rotation
os.environ['R07_LAYOUT']='L80'
import runtime_v7_r07 as v
O=v.O/'layouts';c=copy.deepcopy(v.cfg);p=copy.deepcopy(v.P);items=[s for ph in p['phases'] for s in ph['segments']];oldcenter=np.array(c['station_frames']['slicer']['new_center']);newcenter=oldcenter.copy();newcenter[1]=.1575;delta=newcenter-oldcenter;c['station_frames']['slicer']['new_center']=newcenter.tolist();c['station_overrides']['slicer']['new_center']=newcenter.tolist()
for i,sg in enumerate(items):
 if sg['station']=='slicer':
  for hands in sg['poses']:
   for h in hands.values():h['pos']=(np.array(h['pos'])+delta).tolist()
for i,lower in ((12,.05),(30,.025)):
 for hands in items[i]['poses']:
  h=hands['R'];oldR=v.s.rot(h);oldO=Rotation.from_euler('xyz',h.get('object_rotation_deg') or [0,0,0],degrees=True).as_matrix();oldCenter=np.array(h.get('food_center_local_m',[0,0,0]));oldPos=np.array(h['pos']);worldCenter=oldPos+oldR@oldO@oldCenter;worldFoodR=oldR@oldO;newPos=oldPos-[0,0,lower]
  h.update(approach=[0,1,0],jaw_axis=[1,0,0],roll_deg=0);newR=v.s.rot(h);newO=newR.T@worldFoodR;h['object_rotation_deg']=Rotation.from_matrix(newO).as_euler('xyz',degrees=True).tolist();h['food_center_local_m']=(worldFoodR.T@(worldCenter-newPos)).tolist();h['pos']=newPos.tolist()
  for name in ('work_offset_m','mass_offset_m'):h[name]=(newR.T@(oldPos+oldR@v.s.ck.offset_vector(h[name])-newPos)).tolist()
  h['r07_full_food_pose_preserved']=True
 for j,hands in enumerate(items[i+1]['poses']):
  h=hands['R'];h.update(pos=(np.array(items[i]['poses'][-1]['R']['pos'])+np.array([0,0,0] if j==0 else [0,-.075,0])).tolist(),approach=[0,1,0],jaw_axis=[1,0,0],roll_deg=0)
 items[i]['layout_fix']='Full processor front is10mm behind counter edge; full input food world pose retained after station move, side-grip/lower TCP keeps wrist in front of closed cabinet leaves. No dimensions reduced.'
c.update(id='L81',orientation='R07_v7_L81',reason='Move full BFP forward67.5mm toY.1575 (front at.010m). Lower side-grip preserves full world food; empty withdrawal moves toward counter front. Left full lid stow and low-spout move retained fromL80.')
for suffix,data in [('',c),('_process_v4',p),('_process_v7',p),('_process',json.loads((O/'L80_process.json').read_text()))]:(O/f'L81{suffix}.json').write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=json.loads((O/f'L80{suffix}.json').read_text());d['config']=c;(O/f'L81{suffix}.json').write_text(json.dumps(d,indent=2))
print('L81 full geometry forward processor, side/lower grip; proposed, not admitted')
