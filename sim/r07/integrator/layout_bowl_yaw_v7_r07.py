"""Reorient complete upright bowls and keyed bails, no part resizing/removal."""
import os,sys,json,copy
import numpy as np
from scipy.spatial.transform import Rotation
os.environ['R07_LAYOUT']='L74'
import runtime_v7_r07 as v
O=v.O/'layouts';ID=sys.argv[1];angle=float(sys.argv[2]);yaw=Rotation.from_euler('z',angle,degrees=True).as_matrix();cfg=copy.deepcopy(v.cfg);P=copy.deepcopy(v.P)
for ph in P['phases']:
 for sg in ph['segments']:
  for pose in sg['poses']:
   for h in pose.values():
    if h['held']!='carried_bowl':continue
    rotation=yaw@v.s.rot(h);h.update(approach=rotation[:,0].tolist(),jaw_axis=(-rotation[:,1]).tolist(),roll_deg=0)
cfg.update(id=ID,orientation='R07_v7_'+ID,whole_bowl_yaw_deg=angle,reason=f'L74 hardware; turn every full upright bowl and complete keyed bail{angle}degrees about its vertical axis. Same bowl centres/supports, masses and full solid dimensions; side approach instead of rear-facing grasp. No added mechanism.')
for suffix,data in [('',cfg),('_process_v4',P),('_process_v7',P),('_process',json.loads((O/'L74_process.json').read_text()))]:(O/f'{ID}{suffix}.json').write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=json.loads((O/f'L74{suffix}.json').read_text());d['config']=cfg;(O/f'{ID}{suffix}.json').write_text(json.dumps(d,indent=2))
print('FULL_BOWL_YAW',ID,angle)
