import json,copy
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results/layouts';c=json.loads((O/'L65.json').read_text());p=json.loads((O/'L65_process_v7.json').read_text());ss=[s for ph in p['phases'] for s in ph['segments']]
def vec(x):return [x,0,0] if isinstance(x,(int,float)) else x
for i in (10,15,28,34,46,53):
 for hh in ss[i]['poses']:
  h=hh['R'];h.update(approach=[0,1,0],jaw_axis=[0,0,1],object_rotation_deg=[0,0,90],jaw_opening_m=.020)
  for key in ('work_offset_m','mass_offset_m'):
   x,y,z=vec(h[key]);h[key]=[-y,x,z]
 ss[i]['grasp_revision']='Horizontal front approach; R_front*Rz90=old R_down. Entire bowl, contents and original key remain in the same world orientation.20mm original key dimension faces unchanged full fingers; no dimensional scaling.'
for i in (12,13,30,31):
 for hh in ss[i]['poses']:
  h=hh['R'];h.update(approach=[0,1,0],jaw_axis=[1,0,0])
  if h['held']=='root_food':h['object_rotation_deg']=[180,0,-90]
  for key in ('work_offset_m','mass_offset_m'):
   x,y,z=vec(h[key]);h[key]=[-y,z,-x]
 if ss[i]['poses'][0]['R']['held']=='empty':ss[i]['action']='transfer'
 ss[i]['grasp_revision']='Horizontal front approach; full vertical food presentation preserved by rigid object-frame rotation, not food scaling. World wrench vectors unchanged; local COM/work offsets transformed.'
c.update(id='L66',orientation='R07_v7_L66',reason='Evidence-led horizontal approach to rear bowl keys and processor opening, retaining exact world object orientation. Removes overhead-wrist demand in cabinet band; direct spray wash and open-lid withdrawal retained from L65.')
for suffix,data in [('',c),('_process_v4',p),('_process_v7',p),('_process',json.loads((O/'L65_process.json').read_text()))]:(O/('L66'+suffix+'.json')).write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=json.loads((O/('L65'+suffix+'.json')).read_text());d['config']=c
 if suffix=='_park_full':d.update(pass_=False,warm_start_only=True)
 (O/('L66'+suffix+'.json')).write_text(json.dumps(d,indent=2))
print('L66 rigid grasp frame correction, full hardware unchanged')
