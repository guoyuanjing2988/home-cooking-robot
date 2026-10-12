"""Geometry/pose-only repair; force and product objects remain byte-for-value."""
import json,copy
from pathlib import Path
H=Path(__file__).resolve().parent
p=json.loads((H/'results/process_v3.json').read_text());original=copy.deepcopy(p)
for g in p['installed_geometry']:
 if g['name'].startswith('root_brush_'):g['pos'][0]-=.085
 # Cleaning reaches from the open front; the full guards remain unchanged.
for ph in p['phases']:
 for sg in ph['segments']:
  if sg['label'] in ('wash','rinse') and ph['id'].split('.')[0] in ('Q02','Q08'):
   # Brush contacts only the left end of the root. Fingers remain at its centre.
   if ph['id'].endswith('potato'):
    for po in sg['poses']:po['R']['pos'][0]=-.4375
  if ph['id'] in ('Q13','Q21') and sg['poses'][0]['R']['held']=='food_cup':
   for po in sg['poses']:
    h=po['R'];h.update(approach=[0,0,-1],jaw_axis=[0,1,0],object_rotation_deg=[0,0,0])
    h['work_offset_m']=p['tools']['food_cup']['work_local_m'];h['mass_offset_m']=p['tools']['food_cup']['com_local_m']
    # The unchanged offset cup is turned upright: food is 150mm to the right
    # of the handle, below the unchanged lower-front outlet.
    h['pos']=[-.55,.405,1.065]
  if sg['label']=='soak_bok_choy':
   for po in sg['poses']:po['R']['pos'][1]=.305
  if ph['id'] in ('Q12.carrot','Q25') and sg['poses'][0]['R']['held']=='carried_bowl':
   # Translate full bowls and their own lands 30mm towards the front.
   for po in sg['poses']:po['R']['pos'][1]-=.030
  if sg['label']=='wipe_secondary':
   import math
   angle=math.radians(65)
   for po in sg['poses']:
    h=po['R'];h['approach']=[0,math.sin(angle),-math.cos(angle)];h['jaw_axis']=[1,0,0]
    h['pos'][1]=.17-.076*math.sin(angle)
    h['pos'][2]=.960-.005+.076*math.cos(angle)+.0125*math.sin(angle)
for g in p['installed_geometry']:
 if g['name'] in ('output_carrot_land','output_tomato_land'):g['pos'][1]-=.030
p['schema_version']='r04.integrator.process.v1'
p['decision_log']+=['R04 restores original UR5e base collision meshes; no threshold/model scaling changes.', 'Brush moved85mm left; potato grip moved37.5mm left to retain end-of-root bristle contact and centre-finger clearance.', 'Soft-food cup rotated upright below unchanged faucet; full cup/food retained.', 'Soak colander translated80mm forward; full240x100mm shell retained.', 'Carrot/tomato output bowls and lands translated30mm front; same dimensions.', 'Wipe approach changed to65deg with transverse jaw; no pad, guard or force reduction.']
assert all(p[k]==original[k] for k in ('finished_products','force_models','tools','acceptance'))
(H/'results/process_v3.json').write_text(json.dumps(p,indent=2))
(H/'audit/process_changes.json').write_text(json.dumps(dict(invariants=['finished_products','force_models','tools','acceptance'],geometry_before=original['installed_geometry'],geometry_after=p['installed_geometry'],decisions=p['decision_log'][-6:]),indent=2))
print('R04 process revised, invariants identical')
