"""Pose-exact seeds and collision nullspace descent; immutable final replay."""
import time,collections
import numpy as np,mujoco
import mink
from ik_v2_r07 import fast_ik
from robust_search_v4_r07 import hits as proposal_hits
def solve(ch,q,hands,k,deadline):
 import runtime_v2_r07 as v
 m,d=ch.m,ch.d;allnames=v.s.ck.JOINTS+[s+'_carriage_x' for s in v.s.model.SIDES];ix=[ch.qa[n] for n in allnames];di=[ch.da[n] for n in allnames];limits=np.array([m.jnt_range[ch.jid[n]] for n in allnames]);jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
 q,err,_=fast_ik(ch,q,hands,k,max_iter=220,deadline=deadline,lock_carriages=getattr(ch,'lock_initial_carriage',False));best=q.copy();best_score=1e99;best_errors=err;last=[];evaluations=0
 # A collision-free exact IK branch can return early; unresolved starts retain
 # the full caller's20s budget and explore coherent projected alternatives.
 for iteration in range(140):
  if time.monotonic()>=deadline:break
  ch.hands=hands;ch.set_contacts(hands);hits=proposal_hits(ch,q);evaluations+=1
  pe=sum(e['position_mm']+3*e['orientation_deg'] for e in err);pen=sum(max(0,h['required_gap_mm']-h['real_gap_mm']) for h in hits);score=pe+pen
  if score<best_score:best=q.copy();best_score=score;best_errors=err;last=hits
  if not hits and all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in err):
   final_hits,mins,audit=v.f.contacts(ch,q)
   if not final_hits:return q,err,[],evaluations
   hits=final_hits
  if any(e['position_mm']>10 or e['orientation_deg']>6 for e in err):break
  d.qpos[:]=q;mujoco.mj_forward(m,d);J=[]
  for side in hands:
   mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_prep').id);J.extend(np.vstack([jp[:,di],.25*jr[:,di]]))
  J=np.array(J);N=np.eye(len(ix))-.90*np.linalg.pinv(J,rcond=1e-5)@J;grad=np.zeros(len(ix));witness=np.zeros(6)
  distinct={}
  for h in hits:
   pair=tuple(sorted(h['pair']))
   if pair not in distinct or h['real_gap_mm']<distinct[pair]['real_gap_mm']:distinct[pair]=h
  for hit in sorted(distinct.values(),key=lambda h:h['real_gap_mm']-h['required_gap_mm'])[:20]:
   a,b=(ch.gnames.index(n) for n in hit['pair']);dist=mujoco.mj_geomDistance(m,d,a,b,.08,witness);delta=witness[:3]-witness[3:];norm=np.linalg.norm(delta)
   if norm<1e-9:
    delta=d.geom_xpos[a]-d.geom_xpos[b];norm=np.linalg.norm(delta)
   if norm<1e-9:continue
   n=delta/norm
   if dist<0:n=-n
   pja=np.zeros((3,m.nv));pjb=np.zeros_like(pja);rj=np.zeros_like(pja)
   mujoco.mj_jac(m,d,pja,rj,witness[:3] if norm else d.geom_xpos[a],int(m.geom_bodyid[a]));mujoco.mj_jac(m,d,pjb,rj,witness[3:] if norm else d.geom_xpos[b],int(m.geom_bodyid[b]))
   g=n@(pja-pjb)[:,di];grad+=g*max(.002,(hit['required_gap_mm']-hit['real_gap_mm']+1)/1000)
  step=N@grad
  if np.linalg.norm(step)<1e-8:break
  step*=min(20.,.12/max(abs(step)));q[ix]=np.clip(q[ix]+step,limits[:,0]+1e-7,limits[:,1]-1e-7)
  q,err,_=fast_ik(ch,q,hands,k,max_iter=80,deadline=deadline,position_tolerance_mm=4.0,orientation_tolerance_deg=2.5)
 return best,best_errors,last,evaluations
