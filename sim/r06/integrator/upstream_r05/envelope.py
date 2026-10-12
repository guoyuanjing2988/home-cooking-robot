"""2026-10-08 rated payload envelope: 5kg TOTAL flange load, OEM CoM box/circle."""
import os,sys,json,copy,math
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
sys.dont_write_bytecode=True
import numpy as np,mujoco
from scipy.optimize import differential_evolution,minimize
import model,reference as ck
tree,meta=model.build(dict(model.CONFIG,transport_only=True));m=mujoco.MjModel.from_xml_string(__import__('xml.etree.ElementTree',fromlist=['']).tostring(tree.getroot(),encoding='unicode'))
# The 5kg rated load includes all EOAT. Remove simulated gripper before adding it.
for s in model.SIDES:
    for n in (s+'_tool',s+'_jaw_minus',s+'_jaw_plus'):
        bid=m.body(n).id;m.body_mass[bid]=1e-9;m.body_inertia[bid]=1e-12
d=mujoco.MjData(m);mujoco.mj_setConst(m,d)
qa={m.joint(i).name:int(m.jnt_qposadr[i]) for i in range(m.njnt)};da={m.joint(i).name:int(m.jnt_dofadr[i]) for i in range(m.njnt)}
names=meta['arms']['R'];dof=[da[n] for n in names];bounds=[m.jnt_range[m.joint(n).id].tolist() for n in names]
jp=np.zeros((3,m.nv));jr=np.zeros_like(jp);site=m.site('R_attachment_site').id
def evalq(x):
    d.qpos[:]=m.qpos0
    for n,v in zip(names,x):d.qpos[qa[n]]=v
    d.qvel[:]=0;mujoco.mj_forward(m,d);mujoco.mj_jacSite(m,d,jp,jr,site)
    tau=d.qfrc_bias[dof]+49.05*jp[2,dof]
    rot=d.site_xmat[site].reshape(3,3)
    coeff=np.array([49.05*np.cross(jr[:,dof].T,rot[:,i])[...,2] for i in range(3)]).T
    a=tau;b=tau+.015*coeff[:,2]
    # For every joint independently, choose its permitted CoM azimuth and Lz.
    cap=abs(tau)+.350*np.linalg.norm(coeff,axis=1)
    return cap,tau,coeff
out={};wit={};convergence=[]
for j,n in enumerate(names):
    best=None
    for seed in (100,101,102):
        res=differential_evolution(lambda x:-evalq(x)[0][j],bounds,popsize=12,maxiter=100,tol=1e-8,seed=seed,polish=True,workers=1)
        if best is None or res.fun<best.fun:best=res
        convergence.append(dict(joint=n,seed=seed,maximum_Nm=float(-res.fun),evaluations=res.nfev))
    caps,tau,coef=evalq(best.x);sign=1 if tau[j]>=0 else -1
    offset=sign*.350*coef[j]/max(np.linalg.norm(coef[j]),1e-12)
    for s in ('R',):
        nm=s+n[1:];out[nm]=float(caps[j]);wit[nm]=dict(joints_rad=best.x.tolist(),CoM_flange_m=offset.tolist(),rated_payload_total_kg=5,static_Nm=float(caps[j]))
    print(n,out[n],flush=True)
names=meta['arms']['L'];dof=[da[n] for n in names];bounds=[m.jnt_range[m.joint(n).id].tolist() for n in names];site=m.site('L_attachment_site').id
def evalL(x):
    d.qpos[:]=m.qpos0
    for n,v in zip(names,x):d.qpos[qa[n]]=v
    d.qvel[:]=0;mujoco.mj_forward(m,d);mujoco.mj_jacSite(m,d,jp,jr,site)
    tau=d.qfrc_bias[dof]+49.05*jp[2,dof];rot=d.site_xmat[site].reshape(3,3)
    coeff=np.array([49.05*np.cross(jr[:,dof].T,rot[:,i])[...,2] for i in range(3)]).T
    a=tau;b=tau+.015*coeff[:,2]
    return np.maximum(abs(a),abs(b))+.030*np.linalg.norm(coeff[:,:2],axis=1),tau,coeff
for j,n in enumerate(names):
    best=None
    for seed in (100,101,102):
        res=differential_evolution(lambda x:-evalL(x)[0][j],bounds,popsize=12,maxiter=100,tol=1e-8,seed=seed,polish=True,workers=1)
        if best is None or res.fun<best.fun:best=res
        convergence.append(dict(joint=n,seed=seed,maximum_Nm=float(-res.fun),evaluations=res.nfev))
    caps,tau,coef=evalL(best.x);z=.015 if abs(tau[j]+.015*coef[j,2])>abs(tau[j]) else 0;sign=1 if tau[j]+z*coef[j,2]>=0 else -1
    offset=[*(sign*.030*coef[j,:2]/max(np.linalg.norm(coef[j,:2]),1e-12)).tolist(),z]
    out[n]=float(caps[j]);wit[n]=dict(joints_rad=best.x.tolist(),CoM_flange_m=offset,rated_payload_total_kg=5,static_Nm=float(caps[j]));print(n,out[n],flush=True)
ck.json_write(model.HERE/'results/torque_envelope.json',dict(config=model.CONFIG,envelope_Nm=out,witnesses=wit,optimisation=convergence,source='https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf',helper_source='https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf',CoM_boundary=dict(R_radius_m=.350,L_radius_xy_m=.030,L_z_range_m=[0,.015]),method='Three independent differential-evolution maxima per joint, analytic maximisation over OEM permitted CoM sphere (UR5e) / radial disk+Lz (xArm6), actual separate mounting angles. 5kg total load replaces EOAT.',limitation='Numerical lower estimate of global maxima over OEM joint-bounded workspace; no collision-filtering of manufacturer envelope. Observed convergence reported, no inflation factor; manufacturer continuous output ratings unavailable.',published_joint_output_rated_Nm=None,brake_evidence='OEM documented joint brakes/holding and ceiling/angle mounting; rail brake is de-energize-to-apply'))
