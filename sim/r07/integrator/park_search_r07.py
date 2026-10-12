import os,time,json,sys,copy,xml.etree.ElementTree as E
import numpy as np,mujoco
from scipy.optimize import differential_evolution,minimize
from scipy.spatial.transform import Rotation
import r07_model
from distance import Bounds
H=r07_model.H;O=H/'results'
config=dict(r07_model.CONFIG,transport_only=True)
if (O/'config.json').exists():config.update(json.loads((O/'config.json').read_text()))
r07_model.install(config)
import r07_runtime as rt
rt.s.model.CONFIG=config
tr,meta=r07_model.build(config);m=mujoco.MjModel.from_xml_string(E.tostring(tr.getroot(),encoding='unicode'))
ch=object.__new__(rt.s.ck.Checker);ch.desc=rt.s.ck.hand([0,0,1],jaw_axis=[0,1,0]);ch.bind_model(m)
ch.allowed=[];b=Bounds(ch,rt.f.required)
q=m.qpos0.copy();records=[]
for side,cx in [('R',-1.15),('L',.95)]:
 q[ch.qa[side+'_carriage_x']]=-.95 if side=='R' else .46
names=meta['arms'];t0=time.monotonic()
for side in ('R','L'):
 ix=[ch.qa[n] for n in names[side]]
 ids=[g for g,n in enumerate(ch.gnames) if ch.robot[g] and n.startswith(side+'_') and not any(k in n for k in ('carriage','base_plate','mount_bracket','mount_arm','rail_brake'))]
 carr=m.body(side+'_carriage').id
 # Mount-y and mount-height are physical design variables, not geometry scaling.
 limits=[m.jnt_range[ch.jid[n]].tolist() for n in names[side]]+[[.29,.46],[1.15,1.26],[140,165]]
 if side=='R':limits[2]=[2.0,float(np.radians(160))]
 pairids=[(a,bb,need) for a,bb,need,cat in b.pairs if a in ids and bb in ids]
 best=None;evals=0
 def evaluate(x):
  global best,evals
  evals+=1;q[ix]=x[:6];m.body_pos[carr,1:]=x[6:8];m.body_quat[m.body(side+'_mount').id]=Rotation.from_euler('x',x[8],degrees=True).as_quat()[[3,0,1,2]];ch.d.qpos[:]=q;mujoco.mj_kinematics(m,ch.d)
  lo=np.array([[b.support(g,-v)[k] for k,v in enumerate(np.eye(3))] for g in ids]);hi=np.array([[b.support(g,v)[k] for k,v in enumerate(np.eye(3))] for g in ids])
  violation=np.r_[np.maximum(.242-lo[:,1],0),np.maximum(hi[:,1]-.588,0),np.maximum(.865-lo[:,2],0),np.maximum(hi[:,2]-1.265,0),np.maximum((hi[:,0].max()-lo[:,0].min())-.73,0)]
  selfv=[]
  for a,bb,need in pairids:
   gap=mujoco.mj_geomDistance(m,ch.d,a,bb,.014,None);selfv.append(max(0,need+.002-gap))
  score=float(np.sum(violation**2)*1000+sum(v*v for v in selfv)*1000)
  value=dict(score=score,joints_rad=x[:6].tolist(),mount_y_m=float(x[6]),mount_z_m=float(x[7]),mount_deg=float(x[8]),envelope_min_m=lo.min(axis=0).tolist(),envelope_max_m=hi.max(axis=0).tolist(),max_band_violation_mm=float(max(violation)*1000),self_violation_mm=float(max(selfv,default=0)*1000),evaluations=evals)
  if best is None or score<best['score']:best=value
  return score
 for seed in (707,708,709):
  res=differential_evolution(evaluate,limits,popsize=9,maxiter=95,tol=1e-8,seed=seed,polish=True,workers=1)
  print(side,seed,best,flush=True)
  if best['score']<1e-9:break
 q[ix]=best['joints_rad'];m.body_pos[carr,1:]=[best['mount_y_m'],best['mount_z_m']]
 m.body_quat[m.body(side+'_mount').id]=Rotation.from_euler('x',best['mount_deg'],degrees=True).as_quat()[[3,0,1,2]]
 records.append(dict(side=side,**best))
config.update(front_mount_y=records[0]['mount_y_m'],height=records[0]['mount_z_m'],helper_height=records[1]['mount_z_m'],helper_y=records[1]['mount_y_m'])
config.update(mount_deg=records[0]['mount_deg'],helper_mount_deg=records[1]['mount_deg'])
# The builder uses separate base-y settings after optimisation.
out=dict(config=config,q=q.tolist(),arms=records,elapsed_s=time.monotonic()-t0)
(O/'park_search.json').write_text(json.dumps(out,indent=2))
(O/('park_iteration_'+str(time.time_ns())+'.json')).write_text(json.dumps(out,indent=2))
(O/'config.json').write_text(json.dumps(config,indent=2))
print('park search elapsed',time.monotonic()-t0,flush=True)
