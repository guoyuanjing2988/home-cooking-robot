"""Collision-aware IK with both arms free, preserving all final gates."""
import numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
import r07_runtime as rt
def solve(ch,q0,hands,k):
 m,d=ch.m,ch.d;names=rt.s.ck.JOINTS+[s+'_carriage_x' for s in ('R','L')]
 ix=[ch.qa[n] for n in names];bounds=np.array([m.jnt_range[ch.jid[n]] for n in names]).T
 targets={side:(np.array(h['pos']),ch.target_rotation(h,k)) for side,h in hands.items()};q=q0.copy();pairs={}
 def residual(x,collisions=False):
  q[ix]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d);out=[]
  for side,(pos,rot) in targets.items():
   sid=m.site(side+'_prep').id;out.extend((d.site_xpos[sid]-pos)*30);out.extend(Rotation.from_matrix(rot.T@d.site_xmat[sid].reshape(3,3)).as_rotvec()*3)
  if collisions:
   for (a,b),gap in pairs.items():
    value=mujoco.mj_geomDistance(m,d,a,b,gap+.050,None);out.append(max(0,gap+.001-value)*120)
  return np.array(out)
 x=np.clip(q[ix],bounds[0]+1e-8,bounds[1]-1e-8)
 result=least_squares(residual,x,bounds=bounds,max_nfev=160,xtol=1e-8,ftol=1e-8,gtol=1e-8);q[ix]=result.x
 for _ in range(7):
  hits=ch.forbidden(q)
  if not hits:break
  for h in hits:pairs[tuple(ch.gnames.index(n) for n in h['pair'])]=h['required_gap_mm']/1000
  result=least_squares(lambda x:residual(x,True),q[ix].copy(),bounds=bounds,max_nfev=140,xtol=1e-7,ftol=1e-7,gtol=1e-7);q[ix]=result.x
 d.qpos[:]=q;mujoco.mj_kinematics(m,d);errors=[]
 for side,(pos,rot) in targets.items():
  sid=m.site(side+'_prep').id;errors.append(dict(side=side,position_mm=float(np.linalg.norm(d.site_xpos[sid]-pos)*1000),orientation_deg=float(np.degrees(np.linalg.norm(Rotation.from_matrix(rot.T@d.site_xmat[sid].reshape(3,3)).as_rotvec())))))
 return q.copy(),errors
def install():
 rt.Checker.solve_least=solve
