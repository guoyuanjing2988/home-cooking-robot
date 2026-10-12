import json
from pathlib import Path
H=Path(__file__).resolve().parent;p=json.loads((H/'results/process_v3.json').read_text())
for ph in p['phases']:
 for sg in ph['segments']:
  if ph['id'] in ('Q13','Q21') and sg['poses'][0]['R']['held']=='food_cup':
   for po in sg['poses']:po['R']['pos']=[-.55,.375,1.025]
  if ph['id']=='Q12.carrot' and sg['label']=='deliver':
   for po in sg['poses']:po['R']['jaw_axis']=[1,0,0]
  if sg['label']=='soak_bok_choy':
   for po in sg['poses']:
    h=po['R'];h['pos']=[-.30,.29,.90];h['approach']=[0,0,-1];h['jaw_axis']=[0,1,0];h['object_rotation_deg']=[0,0,0]
    h['mass_offset_m']=p['tools']['colander']['com_local_m']
p['decision_log']+=['R04 iteration2: cup TCP lowered40mm and moved30mm forward for faucet clearance; carrot bowl transverse jaw; submerged colander upright instead of side approach. No force or dimensions changed.']
(H/'results/process_v3.json').write_text(json.dumps(p,indent=2));print('repair2 poses applied')
