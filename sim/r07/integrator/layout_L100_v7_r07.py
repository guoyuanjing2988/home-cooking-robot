"""Clear certified palm/drive and wrist/guard conflicts with full handle poses."""
import json,copy
import numpy as np
from scipy.spatial.transform import Rotation
from pathlib import Path
O=Path(__file__).resolve().parent/'results/layouts'
def read(n):return json.loads((O/n).read_text())
c=read('L99.json');p=read('L99_process_v4.json');old=read('L65_process_v4.json');items=[s for ph in p['phases'] for s in ph['segments']];prior=[s for ph in old['phases'] for s in ph['segments']]
angle=45;rot=Rotation.from_euler('z',-angle,degrees=True);pivot=np.array([.093,0,0]);key=pivot-rot.apply(pivot)
def vector(x):return np.array([x,0,0]) if np.isscalar(x) else np.array(x)
for i in (10,15,28,34,46,53):
 for h,oh in zip((q['R'] for q in items[i]['poses']),(q['R'] for q in prior[i]['poses'])):
  a=np.array(oh['approach']);b=np.array(oh['jaw_axis']);oldr=np.column_stack((a,-b,-np.cross(a,b)));newr=oldr@rot.as_matrix()
  h.update(pos=(np.array(oh['pos'])+oldr@key).tolist(),approach=newr[:,0].tolist(),jaw_axis=(-newr[:,1]).tolist(),roll_deg=0,object_rotation_deg=[0,0,0],jaw_opening_m=.028,held_kg=oh['held_kg']+.04)
  for name in ('work_offset_m','mass_offset_m'):h[name]=rot.inv().apply(vector(oh[name])-key).tolist()
  if i==53:
   yaw=Rotation.from_euler('z',90,degrees=True);center=np.array(c['station_frames']['output_tomato']['new_center']);h['pos']=(center+yaw.apply(np.array(h['pos'])-center)).tolist();h['approach']=yaw.apply(h['approach']).tolist();h['jaw_axis']=yaw.apply(h['jaw_axis']).tolist()
 items[i]['layout_fix']='Full45degree bail raises wrist above peeler drive; tomato whole bowl rotated90degrees to approach from the side of the complete secondary guard. Original solids and all gaps retained.'
p['tools']['carried_bowl']['r07_bail_adaptation']['swing_deg']=angle
# Empty potato withdrawal takes the opposite allowed roll used by the food
# grasp; the former empty orientation had a wrist/appliance certificate.
for j,hands in enumerate(items[31]['poses']):
 source=items[30]['poses'][-1]['R'];h=hands['R'];h['jaw_axis']=(-np.array(source['jaw_axis'])).tolist();h['pos'][2]=source['pos'][2]+.030+.065*j
c.update(id='L100',orientation='R07_v7_L100',bowl_bail_swing_deg=angle,bowl_yaw_by_product={'tomato':90},reason='L98 target certificates still reject75degree bowl palms against peeler drive and tomato wrist against secondary guard. Full45degree bails raise the palms; full tomato bowl/dock orientation turns90degrees. Potato empty withdrawal uses alternate roll. Retain L99 complete wallward mount.')
c['headroom_design']['bowl_bail_swing_deg']=angle
for suffix,data in [('',c),('_process_v4',p),('_process_v7',p),('_process',read('L99_process.json'))]:(O/f'L100{suffix}.json').write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=read('L99'+suffix+'.json');d['config']=c
 if suffix=='_park_full':d.update(pass_=False,warm_start_only=True)
 (O/f'L100{suffix}.json').write_text(json.dumps(d,indent=2))
print('L100 full45deg bails, full tomato bowl90deg, empty potato wrist alternative')
