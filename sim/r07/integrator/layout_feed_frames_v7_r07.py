import os,sys,json
import numpy as np
from scipy.spatial.transform import Rotation
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v7_r07 as v
p=v.P;items=[s for ph in p['phases'] for s in ph['segments']]
for i in (12,30):
 lower=-items[i].pop('v7_grasp_offset_z',0)
 if not lower:continue
 for hands in items[i]['poses']:
  h=hands['R'];oldR=v.s.rot(h);oldO=Rotation.from_euler('xyz',h.get('object_rotation_deg') or [0,0,0],degrees=True).as_matrix();oldCenter=np.array(h.get('food_center_local_m',[0,0,0]));oldPos=np.array(h['pos']);worldCenter=oldPos+oldR@oldO@oldCenter;worldFoodR=oldR@oldO;newPos=oldPos-[0,0,lower]
  h.update(approach=[0,1,0],jaw_axis=[1,0,0],roll_deg=0);newR=v.s.rot(h);newO=newR.T@worldFoodR;h['object_rotation_deg']=Rotation.from_matrix(newO).as_euler('xyz',degrees=True).tolist();h['food_center_local_m']=(worldFoodR.T@(worldCenter-newPos)).tolist();h['pos']=newPos.tolist()
  for name in ('work_offset_m','mass_offset_m'):h[name]=(newR.T@(oldPos+oldR@v.s.ck.offset_vector(h[name])-newPos)).tolist()
  h['r07_full_food_pose_preserved']=True
 for j,hands in enumerate(items[i+1]['poses']):
  hands['R'].update(pos=(np.array(items[i]['poses'][-1]['R']['pos'])+[0,-.085*j,0]).tolist(),approach=[0,1,0],jaw_axis=[1,0,0],roll_deg=0)
for suffix in ('_process_v4','_process_v7'):(v.O/'layouts'/f'{v.ID}{suffix}.json').write_text(json.dumps(p,indent=2))
print(v.ID,'food world pose preserved, feed grasp repositioned')
