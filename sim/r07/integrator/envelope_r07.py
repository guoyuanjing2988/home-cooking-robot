"""Mounted, feasible rated-payload envelope; source inertias are unchanged."""
import time,json,xml.etree.ElementTree as E
import numpy as np,mujoco
from scipy.optimize import differential_evolution
import r07_runtime as rt
H=rt.H;O=rt.O
c=dict(rt.s.model.CONFIG,transport_only=True);tr,meta=rt.s.model.build(c)
ch=object.__new__(rt.s.ck.Checker);ch.desc=rt.s.ck.hand([0,0,1],jaw_axis=[0,1,0]);ch.bind_model(mujoco.MjModel.from_xml_string(E.tostring(tr.getroot(),encoding='unicode')))
m,d=ch.m,ch.d
for side in ('R','L'):
 for name in (side+'_tool',side+'_jaw_minus',side+'_jaw_plus'):
  bid=m.body(name).id;m.body_mass[bid]=1e-9;m.body_inertia[bid]=1e-12
mujoco.mj_setConst(m,d);jp=np.zeros((3,m.nv));jr=np.zeros_like(jp);result={};witness={};runs=[]
for side in ('R','L'):
 names=meta['arms'][side];ix=[ch.qa[n] for n in names];di=[ch.da[n] for n in names];site=m.site(side+'_attachment_site').id
 bounds=[m.jnt_range[ch.jid[n]].tolist() for n in names]
 def evaluate(x):
  d.qpos[:]=m.qpos0;d.qpos[ix]=x;mujoco.mj_forward(m,d);mujoco.mj_jacSite(m,d,jp,jr,site)
  tau=d.qfrc_bias[di]+49.05*jp[2,di];rot=d.site_xmat[site].reshape(3,3)
  coef=np.array([49.05*np.cross(jr[:,di].T,rot[:,i])[...,2] for i in range(3)]).T
  if side=='R':cap=abs(tau)+.35*np.linalg.norm(coef,axis=1)
  else:cap=np.maximum(abs(tau),abs(tau+.015*coef[:,2]))+.03*np.linalg.norm(coef[:,:2],axis=1)
  bad=[]
  for ct in d.contact[:d.ncon]:
   a,b=map(int,ct.geom)
   if ct.dist>=-1e-8:continue
   if not (ch.gnames[a].startswith(side+'_') and ch.gnames[b].startswith(side+'_')):continue
   if any(any(k in ch.gnames[g] for k in ('palm','finger','plate','mount','carriage','brake')) for g in (a,b)):continue
   req=rt.f.required(ch,a,b)
   if req is not None:bad.append(float(ct.dist))
  return cap,tau,coef,bad
 for j,name in enumerate(names):
  best=[None]
  def objective(x):
   cap,tau,coef,bad=evaluate(x)
   if not bad and (best[0] is None or cap[j]>best[0]['static_Nm']):
    if side=='R':offset=(1 if tau[j]>=0 else -1)*.35*coef[j]/max(np.linalg.norm(coef[j]),1e-30)
    else:
     z=.015 if abs(tau[j]+.015*coef[j,2])>abs(tau[j]) else 0.;sign=1 if tau[j]+z*coef[j,2]>=0 else -1
     offset=np.r_[sign*.03*coef[j,:2]/max(np.linalg.norm(coef[j,:2]),1e-30),z]
    best[0]=dict(joints_rad=list(x),CoM_flange_m=offset.tolist(),rated_payload_total_kg=5.,static_Nm=float(cap[j]),OEM_self_collision_free=True)
   return -cap[j]+10000*sum(abs(v) for v in bad)
  for seed in (707,708):
   r=differential_evolution(objective,bounds,popsize=8,maxiter=65,tol=1e-7,seed=seed,polish=True,workers=1)
   runs.append(dict(joint=name,seed=seed,evaluations=r.nfev,feasible_maximum_Nm=best[0]['static_Nm'] if best[0] else None))
  assert best[0] is not None
  result[name]=best[0]['static_Nm'];witness[name]=best[0];print(name,result[name],flush=True)
rt.write('torque_envelope.json',dict(config=c,envelope_Nm=result,witnesses=witness,optimisation=runs,method='Two differential-evolution restarts per joint; analytic maximisation over5kg OEM CoM boundary; only OEM self-collision-free public-range witnesses retained. Rated load replaces complete EOAT.',CoM_boundary=dict(R_radius_m=.350,L_radius_xy_m=.030,L_z_range_m=[0,.015]),limitation='Feasible numerical lower estimates of workspace maxima: conservative denominators, not a proven global maximum.',published_joint_output_rated_Nm=None,source='https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf',helper_source='https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf'))
