"""10mm extra search objective with rigid-pair/roundoff handling; gates unchanged."""
import numpy as np,mujoco
from search_distance_v2_r07 import hits as normal_hits
def hits(ch,q):
 out=normal_hits(ch,q)
 if not getattr(ch,'night_robust',False):return out
 import runtime_v2_r07 as v
 v.f.contacts(ch,q);b=ch.bounds;seen={frozenset(x['pair']) for x in out};m,d=ch.m,ch.d;mujoco.mj_comPos(m,d);di=[ch.da[n] for n in v.s.ck.JOINTS+[s+'_carriage_x' for s in v.s.model.SIDES]]
 for i,(a,bb,need,cat) in enumerate(b.pairs):
  if need<=0 or not any(ch.gnames[g].startswith(('R_','L_')) for g in (a,bb)):continue
  if b.last_lower[i]>=need+.010-1e-6:continue
  names=[ch.gnames[a],ch.gnames[bb]]
  if frozenset(names) in seen:continue
  certificate=b.pair(a,bb)
  if certificate['lower_m']>=need+.010-1e-6:continue
  points=np.zeros(6);gap=float(mujoco.mj_geomDistance(m,d,a,bb,need+.025,points));normal=points[:3]-points[3:];length=np.linalg.norm(normal);sensitive=True
  if length>1e-12:
   normal/=length;ja=np.zeros((3,m.nv));jb=np.zeros_like(ja);jr=np.zeros_like(ja);mujoco.mj_jac(m,d,ja,jr,points[:3],int(m.geom_bodyid[a]));mujoco.mj_jac(m,d,jb,jr,points[3:],int(m.geom_bodyid[bb]));sensitive=np.linalg.norm(normal@(ja-jb)[:,di])>1e-8
  if not sensitive and certificate['lower_m']>=need-1e-6:
   if not hasattr(ch,'immobile_extra_objective'):ch.immobile_extra_objective={}
   ch.immobile_extra_objective[' / '.join(names)]=dict(required_gate_mm=need*1000,actual_lower_mm=certificate['lower_m']*1000,desired_extra_mm=10,reason='Local distance insensitive to all available joints; requires layout change, not relaxed acceptance')
   continue
  if gap<need+.010-1e-6:out.append(dict(pair=names,required_gap_mm=(need+.010)*1000,real_gap_mm=gap*1000,category=cat,search_objective_only=True))
 return out
