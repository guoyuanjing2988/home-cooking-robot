"""Same R04/05 rated-payload method, recomputed for R06 actual mount."""
from cell import *
from scipy.optimize import differential_evolution
ch=Cell(3);m,d=ch.m,ch.d
for n in ('R_tool','R_jaw_minus','R_jaw_plus'):
 b=m.body(n).id;m.body_mass[b]=1e-9;m.body_inertia[b]=1e-12
mujoco.mj_setConst(m,d);ix=[ch.qa[n] for n in ARM];dof=[ch.da[n] for n in ARM];bounds=[m.jnt_range[ch.jid[n]].tolist() for n in ARM];jp=np.zeros((3,m.nv));jr=np.zeros_like(jp);sid=m.site('R_attachment_site').id
def evalq(x):
 d.qpos[:]=ch.q0;d.qpos[ix]=x;d.qvel[:]=0;mujoco.mj_forward(m,d);mujoco.mj_jacSite(m,d,jp,jr,sid)
 tau=d.qfrc_bias[dof]+49.05*jp[2,dof];rot=d.site_xmat[sid].reshape(3,3);coef=np.array([49.05*np.cross(jr[:,dof].T,rot[:,i])[...,2] for i in range(3)]).T
 return abs(tau)+.350*np.linalg.norm(coef,axis=1),tau,coef
out={};wit={};conv=[];beg=time.monotonic()
for j,n in enumerate(ARM):
 best=None
 for seed in (100,101,102):
  z=differential_evolution(lambda x:-evalq(x)[0][j],bounds,popsize=10,maxiter=70,tol=1e-8,seed=seed,polish=True,workers=1)
  if best is None or z.fun<best.fun:best=z
  conv.append(dict(joint=n,seed=seed,maximum_Nm=float(-z.fun),evaluations=z.nfev))
 caps,tau,coef=evalq(best.x);sign=1 if tau[j]>=0 else -1;offset=sign*.35*coef[j]/max(np.linalg.norm(coef[j]),1e-12)
 out[n]=float(caps[j]);wit[n]=dict(joints_rad=best.x.tolist(),CoM_flange_m=offset.tolist(),rated_payload_total_kg=5,static_Nm=out[n]);print(n,round(out[n],4),flush=True)
write('results/torque_envelope.json',dict(envelope_Nm=out,witnesses=wit,optimisation=conv,mount_world_m=[0,.53,1.77],mount_x_degrees=155,rated_payload_total_kg=5,CoM_radius_m=.350,method='R04/05 equations: 3 DE restarts per joint, analytic maximization over OEM 350mm CoM sphere; no inflation; numerical lower estimates are conservative capacity denominators',elapsed_s=time.monotonic()-beg,published_joint_output_rated_Nm=None,brake_evidence='Copied UR5e SW5.21 manual documentary power-loss holding for arbitrary gravity mounting; home-tier decision',source='https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf'))
