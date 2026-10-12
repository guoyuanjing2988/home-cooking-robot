"""R05 least-squares collision search, full car range and movable staging arm.
Copied checker/planner files are untouched; this is a proposal generator.
"""
import time,numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from ik_v2_r07 import fast_ik
from search_distance_v2_r07 import hits as proposal_hits

def solve(ch,q,hands,k,deadline):
 import runtime_v2_r07 as v
 ch.search_termination=None
 m,d=ch.m,ch.d;names=v.s.ck.JOINTS+[side+'_carriage_x' for side in ('R','L')];ix=[ch.qa[n] for n in names]
 limits=np.array([m.jnt_range[ch.jid[n]] for n in names]);targets={side:(np.array(h['pos']),ch.target_rotation(h,k)) for side,h in hands.items()}
 q,errors,_=fast_ik(ch,q,hands,k,max_iter=200,deadline=deadline,lock_carriages=getattr(ch,'lock_initial_carriage',False))
 pairs={};best=q.copy();best_errors=errors;best_hits=[];best_score=1e99;evals=0
 class Deadline(Exception):pass
 for outer in range(12):
  ch.hands=hands;ch.set_contacts(hands);hs=proposal_hits(ch,q)
  if not hs:hs=v.f.contacts(ch,q)[0]
  d.qpos[:]=q;mujoco.mj_kinematics(m,d)
  errors=[dict(side=side,position_mm=float(np.linalg.norm(d.site_xpos[m.site(side+'_prep').id]-pos)*1000),orientation_deg=float(np.degrees(np.linalg.norm(Rotation.from_matrix(rt.T@d.site_xmat[m.site(side+'_prep').id].reshape(3,3)).as_rotvec())))) for side,(pos,rt) in targets.items()]
  score=sum(max(0,e['position_mm']-4)+3*max(0,e['orientation_deg']-2.5) for e in errors)+sum(max(0,h['required_gap_mm']-h['real_gap_mm']) for h in hs)
  if score<best_score:best=q.copy();best_errors=errors;best_hits=hs;best_score=score
  if not hs and all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in errors):return q.copy(),errors,[],evals
  if time.monotonic()>=deadline:break
  old_pairs=set(pairs)
  for hit in hs:pairs[tuple(ch.gnames.index(n) for n in hit['pair'])]=hit['required_gap_mm']/1000
  before=q[ix].copy()
  def residual(x):
   nonlocal evals
   if time.monotonic()>=deadline:raise Deadline()
   evals+=1;q[ix]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d);mujoco.mj_comPos(m,d);vals=[]
   for side,(pos,rt) in targets.items():
    sid=m.site(side+'_prep').id;vals.extend((d.site_xpos[sid]-pos)*20);vals.extend(Rotation.from_matrix(rt.T@d.site_xmat[sid].reshape(3,3)).as_rotvec()*2)
   for (a,b),gap in pairs.items():
    dist=mujoco.mj_geomDistance(m,d,a,b,gap+.045,None);vals.append(max(0,gap+.001-dist)*50)
   return np.array(vals)
  try:
   res=least_squares(residual,np.clip(q[ix],limits[:,0]+1e-8,limits[:,1]-1e-8),bounds=(limits[:,0],limits[:,1]),max_nfev=80,xtol=1e-7,ftol=1e-7,gtol=1e-7)
   q[ix]=res.x
   # A converged local minimum with a stable collision active set is a
   # completed multistart attempt, not a global impossibility certificate.
   # Do not burn the rest of its20s allowance repeating the same minimum.
   if outer>=2 and set(pairs)==old_pairs and res.success and res.optimality<1e-5:
    ch.search_termination=dict(kind='converged_local_minimum',scipy_status=int(res.status),optimality=float(res.optimality),step_norm=float(np.linalg.norm(res.x-before)),active_pairs=len(pairs),outer_iterations=outer+1)
    break
  except Deadline:break
 return best,best_errors,best_hits,evals
