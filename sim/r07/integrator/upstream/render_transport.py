import json
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
import motion_check as mo
import render_setup as re
s=re.s;H=s.HERE;O=H/'results';R=H/'renders';motion=json.loads((O/'motion.json').read_text());ch,h=mo.empty_cell();q=motion['parking']['q']
re.export(ch,q,'overview','CANDIDATE CELL / MEAL FAIL',label='overview')
re.export(ch,q,'parked','IDLE FAIL: DOORS / HUMAN AISLE',label='parked')
re.export(ch,motion['passing']['q_crossing'],'passing','PASSING ROUTE PASS / MEAL FAIL',label='passing')
a=json.loads((R/'parked.scene.json').read_text())
for ci,(lo,hi) in enumerate([(-1.8,-.7),(-.1,.69),(1.47,1.8)]):
 pieces=2 if hi-lo>.6 else 1;width=(hi-lo)/pieces
 for i in range(pieces):
  hinge=lo+i*width if i==0 else hi;angle=-90 if i==0 else 90
  a['geoms'].append(dict(name=f'open_cabinet_door_{ci}_{i}',type=6,size=[width/2,.009,.3],pos=[hinge,.221-width/2,1.65],rot=Rotation.from_euler('z',angle,degrees=True).as_matrix().tolist(),rgba=[.85,.71,.42,1]))
a.update(label='parked',status='IDLE FAIL / OPEN DOORS INTERFERE: 26 PAIRS',door_visual='Five full-height hinged leaves at90degrees,18mm thickness; visual positions fit inside the inherited conservative sweep unions. Clearance audit uses full sweeps, not this single angle.')
(R/'parked_doors_open.scene.json').write_text(json.dumps(a))
ch.bind_model(mujoco.MjModel.from_xml_path(str(H/'models/persistent_meal.xml')));re.export(ch,q,'conserved_initial','CONSERVE 4 FOODS / UNVERIFIED STAGING',label='overview')
manifest=json.loads((R/'manifest.json').read_text());manifest['transport_views']=[dict(file=x+'.png',scene=x+'.scene.json',status='PASSING_ROUTE_PASS' if x=='passing' else 'MEAL_FAIL') for x in ['overview','parked','parked_doors_open','passing','conserved_initial']];manifest['size_px']='First three phase renders1440x960; remaining1200x800';(R/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('transport render scenes5',flush=True)
