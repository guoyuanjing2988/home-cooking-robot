"""Full keyed bail60deg forward, retaining every bowl solid and adding locks."""
import os,json,copy
import numpy as np
from scipy.spatial.transform import Rotation
os.environ['R07_LAYOUT']='L81'
import runtime_v6_r07 as v
O=v.O/'layouts';c=copy.deepcopy(v.cfg);p=copy.deepcopy(v.P);items=[s for ph in p['phases'] for s in ph['segments']];old=json.loads((O/'L65_process_v4.json').read_text());olditems=[s for ph in old['phases'] for s in ph['segments']];angle=60;rot=Rotation.from_euler('z',-angle,degrees=True);pivot=np.array([.093,0,0]);key=pivot-rot.apply(pivot)
for i in (10,15,28,34,46,53):
 for h,oh in zip((q['R'] for q in items[i]['poses']),(q['R'] for q in olditems[i]['poses'])):
  oldr=v.s.rot(oh);newr=oldr@rot.as_matrix();h.update(pos=(np.array(oh['pos'])+oldr@key).tolist(),approach=newr[:,0].tolist(),jaw_axis=(-newr[:,1]).tolist(),roll_deg=0,object_rotation_deg=[0,0,0],jaw_opening_m=.028,held_kg=oh['held_kg']+.04)
  for name in ('work_offset_m','mass_offset_m'):h[name]=rot.inv().apply(v.s.ck.offset_vector(oh[name])-key).tolist()
 items[i]['layout_fix']='Complete bowl/collar remain at original world pose; full bail/key locked60deg forward using full added pins/stops,40g added per bowl. All original solids unchanged.'
p['tools']['carried_bowl']['mass_kg']+=.04;p['tools']['carried_bowl']['r07_bail_adaptation']=dict(swing_deg=angle,added_mass_kg=.04,source_solids_dimensions_unchanged=True,full_pin_size_m=[.003,.006],full_stop_size_m=[.010,.012,.014],pins=2,stops=2,key_force_capacity_N=150,key_moment_capacity_Nm=15,locked_during_robot_operations=True)
c.update(id='L82',orientation='R07_v6_L82',bowl_bail_swing_deg=angle,reason='L81 full forward processor plus60deg locked full bowl bail, placing wrist in front of rail band while all shells/collars remain fixed. Four40g lock adaptations; no geometry reduction.',bail_adaptation_allowance_cny=1000)
for suffix,data in [('',c),('_process_v4',p),('_process_v6',p),('_process',json.loads((O/'L81_process.json').read_text()))]:(O/f'L82{suffix}.json').write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=json.loads((O/f'L81{suffix}.json').read_text());d['config']=c;(O/f'L82{suffix}.json').write_text(json.dumps(d,indent=2))
print('L82 candidate full60deg bowl bail with40g addition per bowl; not admitted')
