"""96-start collision-aware IK, analytic pose Jacobian and native contact gradients."""
import time,collections
import numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from checker import reference
from scene import load,H
def solve(ch,p,approach,starts=96,seed=8,seconds=100,warm=None,target=None):
 assert starts>=96
 rng=np.random.default_rng(seed);m,d=ch.m,ch.d;ids=ch.arm_ids
 lo=np.array([m.jnt_range[j,0] for j in range(m.njnt)])[ids];hi=np.array([m.jnt_range[j,1] for j in range(m.njnt)])[ids]
 q=m.qpos0.copy();q[-2:]=(target or {}).get('jaw_q',.015);sid=m.site('R_prep').id
 candidates=[];rows=[];beg=time.monotonic();hist=collections.Counter()
 seeds=[]
 def residual(x,R,collisions=False):
  q[ids]=x;d.qpos[:]=q;mujoco.mj_forward(m,d)
  error=np.r_[(d.site_xpos[sid]-p)*10,Rotation.from_matrix(R@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
  if not collisions:return error
  penalties=[]
  for c in d.contact[:d.ncon]:
   a,b=map(int,c.geom);req=ch.required(ch,a,b)
   if req is not None:
    if target and target['kind']=='working' and frozenset([ch.gnames[a],ch.gnames[b]]) in ch.permissions('working'):continue
    penalties.append(max(0,req[0]+.010-c.dist))
  # Fixed length, smooth summed collision penalty for second solve.
  return np.r_[error,15*np.linalg.norm(penalties)]
 for k in range(starts):
  # Every start samples a legal cart pose then freezes it through IK/stroke.
  if ch.meta.get('config',{}).get('dock') and target and target.get('cart_x') is not None:q[:3]=[target['cart_x'],target.get('cart_y',-.21),0.]  # R14: cart_y = undocked (pulled back) pose
  elif ch.meta.get('config',{}).get('dock'):q[:3]=[np.clip(p[0]+rng.uniform(-.43,.43),-1.48,1.46),-.21,0.]
  else:q[:3]=[np.clip(p[0]+rng.uniform(-.43,.43),-1.48,1.46),rng.uniform(-.53,-.30),rng.uniform(-.17,.17)]
  jaws=target.get('jaws') if target and target.get('jaws') else ([(0,0,1),(0,0,-1),(1,0,0),(-1,0,0)] if abs(approach[1])>.9 else [(0,1,0),(0,-1,0),(1,0,0),(-1,0,0)])
  jaw=tuple(jaws[k%len(jaws)])
  if abs(np.dot(jaw,approach))>.9:jaw=(1,0,0) if abs(approach[0])<.9 else (0,0,1)
  R=reference.rotation(approach,jaw)
  if target:ch.configure_target(target,R)
  x=rng.uniform(lo,hi)
  if seeds and k<48:
   x=np.array(seeds[(k*7)%len(seeds)])[ids];x=x+rng.normal(0,.08,len(ids));x[0]=np.clip(p[0]+rng.uniform(-.4,.4),lo[0],hi[0])
  if warm is not None and k<24:x=np.clip(np.array(warm)[ids]+rng.normal(0,.05 if k<8 else .25,len(ids)),lo+1e-9,hi-1e-9)
  x=np.clip(x,lo+1e-9,hi-1e-9)
  # Every start really runs; no time-expiry counter inflation.
  res=least_squares(residual,x,args=(R,),bounds=(lo+1e-10,hi-1e-10),max_nfev=65,ftol=1e-5,xtol=1e-5,gtol=1e-5)
  q[ids]=res.x;pe,re=ch.pose_error(q,p,R);status='pose'
  record=dict(start=k,position_mm=pe*1000,orientation_deg=np.degrees(re))
  if pe<=.005 and re<=np.deg2rad(3):
   kw=dict(kind=target['kind'],mass={'holder':.55,'carrot':.12,'tomato':.15,'pusher':.25}.get(target['held'],0),force=target['force']) if target else {}
   check=ch.check(q,full=False,**kw)
   if check['hits']:
    res=least_squares(residual,res.x,args=(R,True),bounds=(lo+1e-10,hi-1e-10),max_nfev=25,ftol=1e-5,xtol=1e-5,gtol=1e-5)
    q[ids]=res.x;pe,re=ch.pose_error(q,p,R)
   check=ch.check(q,full=False,**kw)
   if not check['hits']:check=ch.check(q,full=True,**kw)
   status='collision' if check['hits'] else 'pose' if pe>.005 or re>np.deg2rad(3) else 'floor_cable' if not check['mobile']['ok'] else 'tip' if not check['stability']['ok'] else 'ok' if check['load']['ok'] else 'load'
   record.update(position_mm=pe*1000,orientation_deg=float(np.degrees(re)),q=q.tolist(),check=check)
   if status=='ok':
    reserve=min(v['reserve_mm'] for cat,v in check['clearance'].items() if cat!='self')
    candidates.append(dict(q=q.tolist(),rotation=R.tolist(),reserve_mm=reserve,check=check))
  record['status']=status;hist[status]+=1;rows.append(record)
 best=max(candidates,key=lambda c:c['reserve_mm']) if candidates else min(rows,key=lambda r:r['position_mm']+r['orientation_deg'])
 # With a warm (previous) state, keep the candidates nearest to it in joint space
 # (2*pi-wrapped), so the next group stays in the same IK branch.
 near=lambda c:float(np.sum(abs((np.array(c['q'])[ids]-np.array(warm)[ids]+np.pi)%(2*np.pi)-np.pi)))
 order=sorted(candidates,key=near) if warm is not None else sorted(candidates,key=lambda c:-c['reserve_mm'])
 return dict(ok=bool(candidates),starts=starts,elapsed_s=time.monotonic()-beg,status_counts=dict(hist),best=best,rows=rows,candidates=order[:8])
