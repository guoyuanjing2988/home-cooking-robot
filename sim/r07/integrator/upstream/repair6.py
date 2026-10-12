import json
from pathlib import Path
H=Path(__file__).resolve().parent;p=json.loads((H/'results/process_v3.json').read_text())
for ph in p['phases']:
 for sg in ph['segments']:
  if ph['id']=='Q12.carrot' and sg['label']=='deliver':
   for po in sg['poses']:po['R'].update(pos=[-1.665,.435,po['R']['pos'][2]],jaw_axis=[0,1,0])
  if sg['label']=='soak_bok_choy':
   for po in sg['poses']:po['R']['pos']=[-.47,.23,.90]
for g in p['installed_geometry']:
 if g['name']=='output_carrot_land':g['pos'][1]=.435
p['decision_log']+=['R04 iteration6: carrot bowl returns to y435mm with jawY, clearing retained raw stands; full upright colander to(-.47,.23,.90) clears crease legs and brush drive. No dimension, water, load or force reduction.']
(H/'results/process_v3.json').write_text(json.dumps(p,indent=2))
