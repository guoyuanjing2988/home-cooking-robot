import json,time,sys,numpy as np,mujoco
import final_check as f
from point_bound import PointBound
import distance,fast_bounds
old_functions=(distance.Bounds.check,distance.Bounds.support,distance.Bounds.pair)
fast_bounds.install();new_functions=(distance.Bounds.check,distance.Bounds.support,distance.Bounds.pair)
H=f.s.HERE;w=json.loads((H/'results/static_all.json').read_text())['witnesses'];rows=[]
for index in [0,4,9,35,40,79,83,92,99,103]:
 ph,sg=[(p,g) for p in f.s.P['phases'] for g in p['segments']][index];key=ph['id']+'__'+sg['label'].replace(' ','_');ch=f.s.Checker(ph,sg);q=np.array(w[key]['poses'][0]['q']);ch.set_contacts(sg['poses'][0])
 distance.Bounds.check,distance.Bounds.support,distance.Bounds.pair=old_functions
 original=f.contacts(ch,q)[0]
 distance.Bounds.check,distance.Bounds.support,distance.Bounds.pair=new_functions
 accelerated=f.contacts(ch,q)[0];bound=PointBound(ch);rng=np.random.default_rng(index);dq=np.zeros_like(q)
 for n in f.s.ck.JOINTS+f.s.ck.JAWS+[s+'_carriage_x' for s in f.s.model.SIDES]:dq[ch.qa[n]]=rng.uniform(-.002,.002)
 positions=[]
 # geom centres plus eight local enclosing vertices bound mesh/primitive
 # excursions empirically; the validity proof is the chain triangle bound.
 for qq in [q,q+dq]:
  ch.d.qpos[:]=qq;mujoco.mj_kinematics(ch.m,ch.d);pts=[]
  for g in np.flatnonzero(ch.robot):
   r=ch.m.geom_rbound[g];rt=ch.d.geom_xmat[g].reshape(3,3)
   for axis in np.eye(3):pts.extend([ch.d.geom_xpos[g]+rt@axis*r,ch.d.geom_xpos[g]-rt@axis*r])
  positions.append(np.array(pts))
 observed=np.max(np.linalg.norm(positions[1]-positions[0],axis=1));predicted=bound.segment_bound(q,q+dq)
 rows.append(dict(stroke=key,original_hits=original,accelerated_hits=accelerated,observed_point_motion_mm=float(observed*1000),bound_mm=predicted*1000,global_bound_mm=bound.bound(dq)*1000,pass_=bool(original==accelerated and observed<=predicted+1e-8)))
(H/'results/path_check_validation.json').write_text(json.dumps(dict(rows=rows,pass_=all(r['pass_'] for r in rows),derivation='Arc chord <= radius times angle; radius bounded by downstream fixed transform translation lengths plus geometry bounding radius; slide displacements added. max over full robot and held points.',reference_unchanged=True),indent=2));print('validation',all(r['pass_'] for r in rows))
