"""Full lockable bail adaptation plus lower food grip at unchanged inlet pose."""
import os,json,copy
import numpy as np
from scipy.spatial.transform import Rotation
os.environ['R07_LAYOUT']='L71'
import runtime_v6_r07 as v
O=v.O/'layouts';cfg=copy.deepcopy(v.cfg);P=copy.deepcopy(v.P);items=[s for ph in P['phases'] for s in ph['segments']]
old=json.loads((O/'L65_process_v4.json').read_text());olditems=[s for ph in old['phases'] for s in ph['segments']]
angle=75;rot=Rotation.from_euler('z',-angle,degrees=True);pivot=np.array([.093,0,0]);key=pivot-rot.apply(pivot)
for i in (10,15,28,34,46,53):
 sg=items[i]
 for h,oh in zip((x['R'] for x in sg['poses']),(x['R'] for x in olditems[i]['poses'])):
  oldr=v.s.rot(oh);newr=oldr@rot.as_matrix();h.update(pos=(np.array(oh['pos'])+oldr@key).tolist(),approach=newr[:,0].tolist(),jaw_axis=(-newr[:,1]).tolist(),roll_deg=0,object_rotation_deg=[0,0,0],jaw_opening_m=.028,held_kg=oh['held_kg']+.04)
  for name in ('work_offset_m','mass_offset_m'):h[name]=rot.inv().apply(v.s.ck.offset_vector(oh[name])-key).tolist()
 sg['layout_fix']='All original bowl/key/collar/bail solids retained; full bail locked75deg forward on added pins/stops. Same world bowl shell,0.04kg added, full keyed grip, lower/forward physical key.'
P['tools']['carried_bowl']['mass_kg']+=.04
P['tools']['carried_bowl']['r07_bail_adaptation']=dict(swing_deg=75,added_mass_kg=.04,source_solids_dimensions_unchanged=True,full_pin_size_m=[.003,.006],full_stop_size_m=[.010,.012,.014],pins=2,stops=2,key_force_capacity_N=150,key_moment_capacity_Nm=15,locked_during_robot_operations=True)
for i,lower in ((12,.05),(30,.025)):
 for pose in items[i]['poses']:
  h=pose['R'];tool=v.s.rot(h);obj=Rotation.from_euler('xyz',h.get('object_rotation_deg') or [0,0,0],degrees=True).as_matrix();delta=np.array([0,0,lower]);h['pos']=(np.array(h['pos'])-delta).tolist();h['food_center_local_m']=(np.array(h.get('food_center_local_m',[0,0,0]))+(tool@obj).T@delta).tolist()
  for name in ('work_offset_m','mass_offset_m'):h[name]=(v.s.ck.offset_vector(h[name])+tool.T@delta).tolist()
 items[i]['layout_fix']='Grasp lower on the full unscaled food. Same inlet world food pose/orientation; larger actual grip moment retained in reference checks.'
 for pi,pose in enumerate(items[i+1]['poses']):
  pose['R']['pos']=(np.array(items[i]['poses'][-1]['R']['pos'])+np.array([0,0,0] if pi==0 else [-.10,-.135,.02])).tolist()
 items[i+1]['layout_fix']='Empty withdrawal begins at actual new release TCP and moves forward, below cabinet bottom.'
cfg.update(id='L72',orientation='R07_v6_L72',bowl_bail_swing_deg=angle,reason='Keep full bowls fixed upright but lock their complete bail/key75deg forward with full pins/stops and40g extra mass. Lower root grip at processor inlet50mm carrot/25mm potato while preserving full food world pose; empty withdrawal starts at release. L71 checked working engagement/retreat retained.')
for suffix,data in [('',cfg),('_process_v4',P),('_process_v6',P),('_process',json.loads((O/'L71_process.json').read_text()))]:(O/('L72'+suffix+'.json')).write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=json.loads((O/('L71'+suffix+'.json')).read_text());d['config']=cfg
 if suffix=='_park_full':d.update(pass_=False,warm_start_only=True)
 (O/('L72'+suffix+'.json')).write_text(json.dumps(d,indent=2))
print('L72 full bail swing and lower inlet grasp, no scaled solids')
