"""R05-style constrained differential IK with both carriages and inactive staging.
Search velocities are numerical steps, never credited as an executed path.
Every proposed static witness still receives the unchanged full reference replay.
"""
import time
import numpy as np,mujoco,mink
from ik_v2_r07 import fast_ik
from robust_search_v7_r07 import hits as proposal_hits
def solve(ch,q,hands,k,deadline):
 import runtime_v2_r07 as v
 ch.search_termination=None
 q,errors,_=fast_ik(ch,q,hands,k,max_iter=180,deadline=deadline,lock_carriages=getattr(ch,'lock_initial_carriage',False))
 m=ch.m;cfg=mink.Configuration(m,q=q.copy());tasks=[];frames=[];pairs={};best=(float('inf'),q.copy(),errors,[]);evaluations=0
 for side,h in hands.items():
  t=mink.FrameTask(side+'_prep','site',position_cost=1.,orientation_cost=.35,lm_damping=1e-4)
  t.set_target(mink.SE3.from_rotation_and_translation(mink.SO3.from_matrix(ch.target_rotation(h,k)),np.array(h['pos'])));tasks.append(t);frames.append((side,t))
 posture=mink.PostureTask(m,cost=1e-6);posture.set_target(q.copy());tasks.append(posture)
 frozen=[n for n in v.s.ck.BASE if not n.endswith('_carriage_x')]+v.s.ck.JAWS
 speeds={n:0. if n in frozen else .7 if 'carriage_x' in n else 2. for n in ch.da}
 for iteration in range(200):
  if time.monotonic()>=deadline:break
  q=cfg.q.copy();ch.hands=hands;ch.set_contacts(hands);hits=proposal_hits(ch,q);evaluations+=1
  errors=[]
  for side,t in frames:
   e=t.compute_error(cfg);errors.append(dict(side=side,position_mm=float(np.linalg.norm(e[:3])*1000),orientation_deg=float(np.degrees(np.linalg.norm(e[3:])))))
  score=sum(e['position_mm']+3*e['orientation_deg'] for e in errors)+sum(max(0,h['required_gap_mm']-h['real_gap_mm']) for h in hits)
  if score<best[0]:best=(score,q.copy(),errors,hits)
  if not hits and all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in errors):
   full=v.f.contacts(ch,q)[0]
   if not full:return q,errors,[],evaluations
   hits=full
  for h in hits:pairs[tuple(sorted(h['pair']))]=h['required_gap_mm']/1000
  limits=[mink.ConfigurationLimit(m),mink.VelocityLimit(m,speeds)]
  for gap in sorted(set(pairs.values())):
   pp=[([a],[b]) for (a,b),need in pairs.items() if need==gap]
   limits.append(mink.CollisionAvoidanceLimit(m,pp,minimum_distance_from_collisions=gap+.001,collision_detection_distance=gap+.045,gain=.65))
  try:velocity=mink.solve_ik(cfg,tasks,.05,'daqp',1e-4,limits=limits)
  except Exception:break
  for name in frozen:velocity[ch.da[name]]=0.
  cfg.integrate_inplace(velocity,.05)
 return best[1],best[2],best[3],evaluations
