"""Keep unobstructed rear bowl shells; swing the full bail toward the front."""
import os,json,copy
import numpy as np
from scipy.spatial.transform import Rotation
os.environ['R07_LAYOUT']='L95'
import runtime_v7_r07 as v
O=v.O/'layouts';c=copy.deepcopy(v.cfg);p=copy.deepcopy(v.P);base=json.loads((O/'L84.json').read_text());bproc=json.loads((O/'L65_process_v4.json').read_text());items=[s for ph in p['phases'] for s in ph['segments']];olditems=[s for ph in bproc['phases'] for s in ph['segments']]
for name,f in base['station_frames'].items():
 if name.startswith('output_'):
  c['station_frames'][name]=copy.deepcopy(f);c['station_overrides'][name]=copy.deepcopy(base['station_overrides'][name])
angle=75;rot=Rotation.from_euler('z',-angle,degrees=True);pivot=np.array([.093,0,0]);key=pivot-rot.apply(pivot)
# Retain a50mm front setback, rather than operating the body on the edge.
delta=.1975-c['station_frames']['slicer']['new_center'][1]
c['station_frames']['slicer']['new_center'][1]=.1975;c['station_overrides']['slicer']['new_center'][1]=.1975
for i in (12,13,30,31):
 for hands in items[i]['poses']:hands['R']['pos'][1]+=delta
for i in (10,15,28,34,46,53):
 for h,oh in zip((q['R'] for q in items[i]['poses']),(q['R'] for q in olditems[i]['poses'])):
  oldr=v.s.rot(oh);newr=oldr@rot.as_matrix();h.update(pos=(np.array(oh['pos'])+oldr@key).tolist(),approach=newr[:,0].tolist(),jaw_axis=(-newr[:,1]).tolist(),roll_deg=0,object_rotation_deg=[0,0,0],jaw_opening_m=.028,held_kg=oh['held_kg']+.04)
  for name in ('work_offset_m','mass_offset_m'):h[name]=rot.inv().apply(v.s.ck.offset_vector(oh[name])-key).tolist()
 items[i]['layout_fix']='Original full rear bowl shell/collar position; full75degree bail with full pins/stops. Wrist target moves forward/down;40g added mass, no source solid scaled.'
p['tools']['carried_bowl']['mass_kg']+=.04;p['tools']['carried_bowl']['r07_bail_adaptation']=dict(swing_deg=angle,added_mass_kg=.04,source_solids_dimensions_unchanged=True,pins=2,stops=2,key_force_capacity_N=150,key_moment_capacity_Nm=15,locked_during_robot_operations=True)
c.update(id='L96',orientation='R07_v7_L96',bowl_bail_swing_deg=angle,reason='Front processor and full-food side-grasp fromL95; restore rear bowls to avoid front appliance occupation, articulate complete bail75deg with locks. Full colander front withdrawal retained.',bail_adaptation_allowance_cny=1000)
c['headroom_design']['output_dock_y_m']=.452;c['headroom_design']['bowl_bail_swing_deg']=angle
c['headroom_design'].update(processor_front_y_m=.050,edge_stability='50mm body setback; near-edge OEM warning and exact feet/stability remain unqualified. No operational certification.')
for suffix,data in [('',c),('_process_v4',p),('_process_v7',p),('_process',json.loads((O/'L84_process.json').read_text()))]:(O/f'L96{suffix}.json').write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=json.loads((O/f'L84{suffix}.json').read_text());d['config']=c
 if suffix=='_park_full':d.update(pass_=False,warm_start_only=True)
 (O/f'L96{suffix}.json').write_text(json.dumps(d,indent=2))
print('L96 full-bail candidate created')
