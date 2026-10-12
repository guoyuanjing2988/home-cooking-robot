"""Evidence-led wash/grasp/staging variants; no hardware solids scaled."""
import json,copy
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results'
base=json.loads((O/'layouts/L59.json').read_text());process=json.loads((O/'layouts/L59_process_v7.json').read_text())
variants=[('L60',.805,.40,[-.35,.30,.805]),('L61',.815,.41,[-.40,.28,.805]),('L62',.825,.42,[-.35,.30,.795]),('L63',.805,.43,[-.30,.29,.805]),('L64',.815,.43,[-.38,.30,.800]),('L65',.825,.40,[-.35,.27,.800])]
for ID,z,y,storage in variants:
 c=copy.deepcopy(base);c.update(id=ID,orientation='R07_v7_'+ID,reason='Direct whole-food coarse spray washing replaces transfer cup; full food and forces retained. Secondary lid stays in its existing open dock until withdrawal. Wash height/jet corridor and full colander storage varied from L59 planner collisions.',persistent_storage={'colander':storage},retired_transfer_vessels=['cup'])
 p=copy.deepcopy(process);ss=[sg for ph in p['phases'] for sg in ph['segments']]
 for i in (35,47):
  sg=ss[i];prod=sg['poses'][0]['R']['product'];mass=next(f['input_mass_kg'] for f in p['finished_products'] if f['product']==prod);size=next(f['input_size_m'] for f in p['finished_products'] if f['product']==prod)
  h=copy.deepcopy(sg['poses'][0]['R']);h.update(held='root_food',held_kg=mass,grip='friction',work_offset_m=0,mass_offset_m=0,jaw_opening_m=size[1],object_rotation_deg=[0,0,0],food_state='whole',approach=ss[2]['poses'][0]['R']['approach'],jaw_axis=ss[2]['poses'][0]['R']['jaw_axis'],contacts=[])
  sg.update(label=('Coarse direct spray wash bok choy' if i==35 else 'Direct spray wash unpeeled tomato'),process_change_reason='Same water action and sourced forces; full whole-food geometry replaces food cup, avoiding a redundant container load/unload.',poses=[{'R':dict(h,pos=[-.58,y,z])},{'R':dict(h,pos=[-.58,y+.02,z])}])
 ss[52]['station']='secondary';ss[52]['action']='transfer';ss[52]['guard_state']='open_during_withdrawal; close only after hand clears'
 # Inspection needs camera view, not a vertical approach into both bowls.
 ss[54]['poses']=[copy.deepcopy(ss[0]['poses'][0]),copy.deepcopy(ss[58]['poses'][-1])]
 ss[54]['action']='transfer';ss[54]['label']='Observe all outputs from fixed calibrated cameras'
 p['night_process_change']['retired_transfer_vessels']=['food_cup'];p['night_process_change']['essential_unqualified']=['Physical guard/pusher/batch bowl operations require checked paths; food quality alone is declared']
 for suffix,data in [('',c),('_process_v4',p),('_process_v7',p),('_process',json.loads((O/'layouts/L59_process.json').read_text()))]:(O/'layouts'/f'{ID}{suffix}.json').write_text(json.dumps(data,indent=2))
 env=json.loads((O/'layouts/L59_envelope.json').read_text());env['same_mount_envelope_reuse']='L59: identical full principal geometry, mount, payload and joint limits; only station target/ownership workflow changes';env['config']=c;(O/'layouts'/f'{ID}_envelope.json').write_text(json.dumps(env,indent=2))
 park=json.loads((O/'layouts/L59_park_full.json').read_text());park.update(config=c,pass_=False,warm_start_only=True);(O/'layouts'/f'{ID}_park_full.json').write_text(json.dumps(park,indent=2))
print('Created L60-L65, no scale changes; source kitchen and mounted arm unchanged')
