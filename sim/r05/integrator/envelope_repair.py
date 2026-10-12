"""Constrained replacement for an unreachable OEM envelope witness."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import json,math,copy,xml.etree.ElementTree as E
import numpy as np,mujoco
from scipy.optimize import differential_evolution
import model,reference as ck
H=model.HERE;ck.configure(dict(model.CONFIG,transport_only=True))
ch=object.__new__(ck.Checker);ch.desc=ck.hand([0,0,1],jaw_axis=[0,1,0])
ch.bind_model(mujoco.MjModel.from_xml_string(E.tostring(ck.TEMPLATE.getroot(),encoding='unicode')))
m,d=ch.m,ch.d
for s in model.SIDES:
 for n in (s+'_tool',s+'_jaw_minus',s+'_jaw_plus'):
  bid=m.body(n).id;m.body_mass[bid]=1e-9;m.body_inertia[bid]=1e-12
mujoco.mj_setConst(m,d)
env=json.loads((H/'results/torque_envelope.json').read_text());audit=json.loads((H/'results/envelope_reachability_audit.json').read_text());runs=[]
for row in audit['rows']:
 if row['OEM_self_collision_free'] and row['public_ranges_ok']:continue
 n=row['joint'];s=n[0];names=ck.ARMS[s];j=names.index(n);dof=[ch.da[a] for a in names];bounds=[m.jnt_range[ch.jid[a]].tolist() for a in names];site=m.site(s+'_attachment_site').id
 jp=np.zeros((3,m.nv));jr=np.zeros_like(jp);best=None
 def evaluate(x):
  global best
  q=m.qpos0.copy()
  for a,v in zip(names,x):q[ch.qa[a]]=v
  d.qpos[:]=q;mujoco.mj_forward(m,d);mujoco.mj_jacSite(m,d,jp,jr,site)
  tau=d.qfrc_bias[dof]+49.05*jp[2,dof];rot=d.site_xmat[site].reshape(3,3)
  coef=np.array([49.05*np.cross(jr[:,dof].T,rot[:,i])[...,2] for i in range(3)]).T
  z=.015 if abs(tau[j]+.015*coef[j,2])>abs(tau[j]) else 0
  cap=max(abs(tau[j]),abs(tau[j]+.015*coef[j,2]))+.030*np.linalg.norm(coef[j,:2])
  hits=[h for h in ch.forbidden(q) if all(a.startswith(s+'_') and not any(k in a for k in ('gripper','finger','held','adapter','bridge','drive')) for a in h['pair'])]
  if not hits and (best is None or cap>best['static_Nm']):
   sign=1 if tau[j]+z*coef[j,2]>=0 else -1
   best=dict(joints_rad=np.array(x).tolist(),CoM_flange_m=[*(sign*.030*coef[j,:2]/max(np.linalg.norm(coef[j,:2]),1e-12)).tolist(),z],rated_payload_total_kg=5,static_Nm=float(cap),OEM_self_collision_free=True)
  return -cap+5000*sum(max(0,-h['real_gap_mm']/1000) for h in hits)
 for seed in (204,205,206):
  r=differential_evolution(evaluate,bounds,popsize=10,maxiter=75,tol=1e-7,seed=seed,polish=True,workers=1)
  runs.append(dict(joint=n,seed=seed,evaluations=r.nfev,feasible_max_Nm=best['static_Nm'] if best else None));print(runs[-1],flush=True)
 if best is None:raise RuntimeError('No reachable envelope replacement')
 env['envelope_Nm'][n]=best['static_Nm'];env['witnesses'][n]=best
env['config']=model.CONFIG;env['reachability_repair_runs']=runs;env['all_maximum_witnesses_OEM_self_collision_free']=True
env['method']+='; self-colliding maximum was replaced using3 constrained differential-evolution starts and exact reference OEM self-collision replay.'
env['limitation']='Numerical lower estimate of global maxima. Every retained denominator has a public-joint-bounded, OEM self-collision-free witness; no torque inflation. Kitchen collisions do not define manufacturer payload capability.'
ck.json_write(H/'results/torque_envelope_reachable.json',env)
