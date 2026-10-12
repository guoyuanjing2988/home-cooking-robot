"""Rated 5kg/350mm CoM envelope in actual mount orientation.

Analytic maximisation over the spherical CoM boundary followed by two numeric
joint-space restarts. Complete EOAT removed from gravity; only OEM arm retained.
Feasible self-clear witnesses, not a certified global optimum. Near-zero upright
base-yaw gravity envelope is reported literally, never replaced by motor guesses.
"""
import sys,copy,xml.etree.ElementTree as E
import numpy as np,mujoco
from scipy.optimize import differential_evolution
from scene import build,variants,save
def main(tilt):
 cfg=variants()[1];cfg['mount_tilt_deg']=tilt;t,_=build(cfg)
 tool=t.find(".//body[@name='R_tool']")
 for p in t.iter('body'):
  if tool in list(p):p.remove(tool);break
 m=mujoco.MjModel.from_xml_string(E.tostring(t.getroot(),encoding='unicode'));d=mujoco.MjData(m)
 names=['R_shoulder_pan_joint','R_shoulder_lift_joint','R_elbow_joint','R_wrist_1_joint','R_wrist_2_joint','R_wrist_3_joint'];ids=[m.joint(n).qposadr[0] for n in names];dids=[m.joint(n).dofadr[0] for n in names]
 sid=m.site('R_attachment_site').id;bid=m.site_bodyid[sid];jp=np.zeros((3,m.nv));jr=jp.copy()
 armgeoms={g for g in range(m.ngeom) if (m.geom(g).name or '').startswith('R_geom_')};rows=[];vals={}
 def evaluate(x,k,detail=False):
  d.qpos[ids]=x;mujoco.mj_forward(m,d)
  for c in d.contact[:d.ncon]:
   if set(map(int,c.geom))<=armgeoms and c.dist<0:return None if detail else 1e5-c.dist
  p=d.site_xpos[sid];mujoco.mj_jac(m,d,jp,jr,p,bid);j=dids[k]
  base=d.qfrc_bias[j]+5*9.81*jp[2,j]
  # derivative of z wrt joint at offset r is (axis x r).z
  v=np.cross(np.array([0.,0.,1.]),jr[:,j]);vn=np.linalg.norm(v)
  radius=.35;off=np.zeros(3) if vn<1e-14 else np.sign(base or 1)*radius*v/vn
  value=abs(base)+5*9.81*radius*vn
  return dict(joint=names[k],q=d.qpos.tolist(),offset_world_m=off.tolist(),torque_Nm=float(value),mount_tilt_deg=tilt) if detail else -value
 for k,n in enumerate(names):
  best=None
  for seed in [901,902]:
   r=differential_evolution(lambda x:evaluate(x,k),m.jnt_range[ids],seed=seed,popsize=10,maxiter=70,polish=True,tol=1e-7)
   w=evaluate(r.x,k,True)
   if w and (best is None or w['torque_Nm']>best['torque_Nm']):best=w
  assert best is not None
  vals[n]=best['torque_Nm'];rows.append(best);print(tilt,n,vals[n],flush=True)
 save(f'assets/envelope_{tilt}.json',dict(envelope_Nm=vals,witnesses=rows,rated_payload_kg=5,CoM_radius_m=.35,method=__doc__,source='https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf'))
if __name__=='__main__':main(int(sys.argv[1]))
