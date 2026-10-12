"""Analytic full-range collision Jacobian for proposal IK; reference admission unchanged."""
import time,numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from ik_v2_r07 import fast_ik
from robust_search_v6_r07 import hits as proposal_hits
def solve(ch,q,hands,k,deadline):
 import runtime_v2_r07 as v
 ch.search_termination=None;m,d=ch.m,ch.d;names=v.s.ck.JOINTS;ix=[ch.qa[n] for n in names];di=[ch.da[n] for n in names];limits=np.array([m.jnt_range[ch.jid[n]] for n in names]);targets={s:(np.array(h['pos']),ch.target_rotation(h,k)) for s,h in hands.items()};evals=0
 ch.lock_initial_carriage=True
 q,errors,_=fast_ik(ch,q,hands,k,max_iter=220,deadline=deadline,lock_carriages=getattr(ch,'lock_initial_carriage',False));pairs={};best=q.copy();best_errors=errors;best_hits=[];best_score=float('inf');jp=np.zeros((3,m.nv));jr=np.zeros_like(jp);ja=np.zeros_like(jp);jb=np.zeros_like(jp)
 class Deadline(Exception):pass
 def skew(x):return np.array([[0,-x[2],x[1]],[x[2],0,-x[0]],[-x[1],x[0],0]])
 def values(x,jac=False):
  nonlocal evals
  if time.monotonic()>=deadline:raise Deadline()
  evals+=1;q[ix]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d);mujoco.mj_comPos(m,d);rows=[];der=[]
  for side,(pos,rot) in targets.items():
   sid=m.site(side+'_prep').id;rv=Rotation.from_matrix(rot.T@d.site_xmat[sid].reshape(3,3)).as_rotvec();rows.extend((d.site_xpos[sid]-pos)*20);rows.extend(rv*2)
   if jac:
    mujoco.mj_jacSite(m,d,jp,jr,sid);theta=np.linalg.norm(rv);a=skew(rv);coef=1/12+theta*theta/720 if theta<1e-4 else (1-.5*theta/np.tan(theta/2))/(theta*theta);jlog=np.eye(3)-.5*a+coef*(a@a);der.extend(jp[:,di]*20);der.extend(jlog@rot.T@jr[:,di]*2)
  for (a,b),gap in pairs.items():
   witness=np.zeros(6);dist=float(mujoco.mj_geomDistance(m,d,a,b,gap+.045,witness));value=max(0,gap+.001-dist)*50;rows.append(value)
   if jac:
    gradient=np.zeros(len(ix))
    if value>0:
     delta=witness[:3]-witness[3:];norm=np.linalg.norm(delta)
     if norm>1e-12:
      normal=delta/norm*(-1 if dist<0 else 1);mujoco.mj_jac(m,d,ja,jr,witness[:3],int(m.geom_bodyid[a]));mujoco.mj_jac(m,d,jb,jr,witness[3:],int(m.geom_bodyid[b]));gradient=-50*(normal@(ja-jb)[:,di])
    der.append(gradient)
  return np.array(der) if jac else np.array(rows)
 for outer in range(30):
  ch.hands=hands;ch.set_contacts(hands);hs=proposal_hits(ch,q)
  if not hs:hs=v.f.contacts(ch,q)[0]
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);errors=[dict(side=s,position_mm=float(np.linalg.norm(d.site_xpos[m.site(s+'_prep').id]-p)*1000),orientation_deg=float(np.degrees(np.linalg.norm(Rotation.from_matrix(r.T@d.site_xmat[m.site(s+'_prep').id].reshape(3,3)).as_rotvec())))) for s,(p,r) in targets.items()]
  score=sum(max(0,e['position_mm']-4)+3*max(0,e['orientation_deg']-2.5) for e in errors)+sum(max(0,h['required_gap_mm']-h['real_gap_mm']) for h in hs)
  if score<best_score:best=q.copy();best_score=score;best_hits=hs;best_errors=errors
  if not hs and all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in errors):return q.copy(),errors,[],evals
  if time.monotonic()>=deadline:break
  old=set(pairs)
  for h in hs:pairs[tuple(ch.gnames.index(n) for n in h['pair'])]=h['required_gap_mm']/1000
  try:
   res=least_squares(values,np.clip(q[ix],limits[:,0]+1e-8,limits[:,1]-1e-8),jac=lambda x:values(x,True),bounds=(limits[:,0],limits[:,1]),max_nfev=160,xtol=1e-9,ftol=1e-9,gtol=1e-8)
   q[ix]=res.x
   if outer>=2 and old==set(pairs) and res.success and res.optimality<1e-5:
    ch.search_termination=dict(kind='converged_local_minimum',scipy_status=int(res.status),optimality=float(res.optimality),active_pairs=len(pairs),outer_iterations=outer+1,analytic_collision_jacobian=True);break
  except Deadline:break
 return best,best_errors,best_hits,evals
