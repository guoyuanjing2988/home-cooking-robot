import json
from pathlib import Path
H=Path(__file__).resolve().parent;p=json.loads((H/'results/process_v3.json').read_text())
for ph in p['phases']:
 for sg in ph['segments']:
  if ph['id']=='Q12.carrot' and sg['label']=='deliver':
   for po in sg['poses']:po['R']['pos'][1]=.345
  if ph['id'] in ('Q13','Q21') and sg['poses'][0]['R']['held']=='food_cup':
   for po in sg['poses']:po['R'].update(pos=[-.4,.255,1.020],jaw_axis=[1,0,0])
  if sg['label']=='soak_bok_choy':
   for po in sg['poses']:po['R']['pos']=[-.40,.27,.90]
for g in p['installed_geometry']:
 if g['name']=='output_carrot_land':g['pos'][1]=.345
p['decision_log']+=['R04 iteration5: full carrot bowl/land to y345mm; transverse upright cup atTCP(-.4,.255,1.020) places full food under outlet via150mmY offset; full upright soak colander shifted100mmleft/20mmfront, water and soak unchanged.']
(H/'results/process_v3.json').write_text(json.dumps(p,indent=2));print('repair5 poses/one land applied')
