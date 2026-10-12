"""Full public carriage range, analytic-Jacobian IK, no changed acceptance."""
import time
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
def fast_ik(ch,q0,hands,k=0,max_iter=180,deadline=None,extra_names=(),lock_carriages=False,position_tolerance_mm=.5,orientation_tolerance_deg=.2):
 q=np.asarray(q0,float).copy();m,d=ch.m,ch.d
 names=sum([__import__('r07_runtime').s.ck.ARMS[s] for s in hands],[])+([] if lock_carriages else [s+'_carriage_x' for s in hands])+list(extra_names)
 names=list(dict.fromkeys(names));ix=[ch.qa[n] for n in names];di=[ch.da[n] for n in names]
 lim=np.array([m.jnt_range[ch.jid[n]] for n in names]);q[ix]=np.clip(q[ix],lim[:,0]+1e-8,lim[:,1]-1e-8)
 targets={s:(np.array(h['pos']),ch.target_rotation(h,k)) for s,h in hands.items()};jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
 score=float('inf');best=q.copy();errors=[]
 for iteration in range(max_iter):
  if deadline is not None and time.monotonic()>deadline:break
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);mujoco.mj_comPos(m,d);es=[];js=[];errors=[]
  for side,(pos,rot) in targets.items():
   site=m.site(side+'_prep').id;p=pos-d.site_xpos[site];r=Rotation.from_matrix(rot@d.site_xmat[site].reshape(3,3).T).as_rotvec()
   mujoco.mj_jacSite(m,d,jp,jr,site);es.extend(np.r_[p,.25*r]);js.extend(np.vstack([jp[:,di],.25*jr[:,di]]))
   errors.append(dict(side=side,position_mm=float(np.linalg.norm(p)*1000),orientation_deg=float(np.degrees(np.linalg.norm(r)))))
  e=np.array(es);J=np.array(js);value=float(e@e)
  if value<score:score=value;best=q.copy()
  if all(v['position_mm']<position_tolerance_mm and v['orientation_deg']<orientation_tolerance_deg for v in errors):break
  damp=.012 if np.linalg.norm(e)>.1 else .003 if np.linalg.norm(e)>.01 else .0003
  step=J.T@np.linalg.solve(J@J.T+np.eye(len(e))*damp*damp,e)
  norm=max(abs(step),default=0);step*=min(1.,.28/max(norm,1e-30));q[ix]=np.clip(q[ix]+step,lim[:,0]+1e-7,lim[:,1]-1e-7)
 d.qpos[:]=best;mujoco.mj_kinematics(m,d);errors=[]
 for side,(pos,rot) in targets.items():
  site=m.site(side+'_prep').id;p=pos-d.site_xpos[site];r=Rotation.from_matrix(rot@d.site_xmat[site].reshape(3,3).T).as_rotvec()
  errors.append(dict(side=side,position_mm=float(np.linalg.norm(p)*1000),orientation_deg=float(np.degrees(np.linalg.norm(r)))))
 return best,errors,iteration+1
def dexterity(ch,q,side):
 m,d=ch.m,ch.d;d.qpos[:]=q;mujoco.mj_kinematics(m,d);mujoco.mj_comPos(m,d);jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
 names=__import__('r07_runtime').s.ck.ARMS[side]+[side+'_carriage_x'];di=[ch.da[n] for n in names]
 mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_prep').id);values=np.linalg.svd(np.vstack([jp[:,di],.25*jr[:,di]]),compute_uv=False)
 return dict(min_singular_value=float(min(values)),condition_number=float(max(values)/max(min(values),1e-20)),orientation_characteristic_length_m=.25)
