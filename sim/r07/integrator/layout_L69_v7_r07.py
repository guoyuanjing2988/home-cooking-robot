"""Rigid alternate grasp frames and a drain approach change; no smaller solids."""
import os,json,copy
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
os.environ['R07_LAYOUT']='L68'
import runtime_v7_r07 as v
O=v.O;cfg=copy.deepcopy(v.cfg);P=copy.deepcopy(v.P)
cfg.update(id='L69',orientation='R07_v7_L69',reason='Rigid alternate wrist/grasp frames preserve the full physical food/bowl orientation. Colander drains diagonally forward and up to clear the spout while starting under the same jet. All fixed kitchen, rail and appliance geometry equals L68.')
items=[sg for ph in P['phases'] for sg in ph['segments']]
def change(h,approach,jaw):
 old=v.s.rot(h);new=v.s.rot(dict(h,approach=approach,jaw_axis=jaw,roll_deg=0));local=new.T@old;obj=Rotation.from_euler('xyz',h.get('object_rotation_deg') or [0,0,0],degrees=True).as_matrix()
 h['object_rotation_deg']=Rotation.from_matrix(local@obj).as_euler('xyz',degrees=True).tolist()
 for key in ('work_offset_m','mass_offset_m','food_center_local_m'):
  if key in h:h[key]=(local@v.s.ck.offset_vector(h[key])).tolist()
 h.update(approach=approach,jaw_axis=jaw,roll_deg=0)
for i in (3,4,18,19):
 for pose in items[i]['poses']:
  h=pose['R'];rot=Rotation.from_euler('y',8,degrees=True).as_matrix();change(h,(rot@np.array(h['approach'])).tolist(),h['jaw_axis'])
 items[i]['layout_fix']='8degree wrist tilt with inverse full-object rotation; world food shape/orientation unchanged; same holder position and force.'
for i in (10,15,28,34,46,53):
 for pose in items[i]['poses']:change(pose['R'],[0,1,0],[0,0,-1])
 items[i]['layout_fix']='Opposite vertical jaw direction on the same full key; inverse object rotation preserves full bowl world pose.'
for i in (33,43):
 h=items[i]['poses'][-1]['R'];h['pos']=[-.40,.24,1.0]
 items[i]['layout_fix']='Same full colander and100mm rise, with100mm forward/right retreat. Start remains under spout; end bottom clears sink water for drain.'
(O/'layouts/L69.json').write_text(json.dumps(cfg,indent=2));(O/'layouts/L69_process_v4.json').write_text(json.dumps(P,indent=2))
(O/'layouts/L69_process_v7.json').write_text(json.dumps(P,indent=2));(O/'layouts/L69_process.json').write_bytes((O/'layouts/L68_process.json').read_bytes())
park=json.loads((O/'layouts/L68_park_full.json').read_text());park.update(config=cfg,pass_=False,warm_start_only=True);(O/'layouts/L69_park_full.json').write_text(json.dumps(park,indent=2))
env=json.loads((O/'layouts/L68_envelope.json').read_text());env['config']=cfg;env['reuse_note']='Identical arm, mounting transform,151mm base, public elbow range and rated5kg payload; only target grasp frames changed.';(O/'layouts/L69_envelope.json').write_text(json.dumps(env,indent=2))
(O/'layouts/L69_target_changes.json').write_text(json.dumps(dict(source='L68',changed=[3,4,10,15,18,19,28,33,34,43,46,53],full_world_object_orientation_preserved=True,geometry_scaled=False),indent=2))
print('L69 target alternatives saved')
