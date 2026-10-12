"""R14 fridge: is the handle arc 0 -> MAX° one continuous, collision-free arm path from the
docked cart (x = -1.48)? Starting from the checked 0° solution, step the door angle, rebuild
the scene with the door there (bar held = removed), solve local IK from the previous joints
(no restarts, so a branch flip would show as a failure or a jump) and run the full checker.
Like solver.solve, the local IK carries the contact penalty (pairs inside required gap + 10 mm)
and the result is accepted within the solver's tolerance (5 mm, 3°). DIR=back starts from the
checked MAX° solution and walks down to 0°.
RELAX=1 uses the real task constraints of a vertical bar instead of one fixed pose: the pad
centre on the bar axis anywhere in z 0.99-1.21 (bar 0.95-1.25), the jaw axis along the door
normal (one finger between bar and door), the approach free to tilt up/down within ±45°.
python fridge14_arc.py [MAX=55] [STEP=2.5] [DIR=fwd|back] [RELAX=1]  -> results/r14/fridge_arc_<dir>.json"""
import sys,json,glob,numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
import chain,kitchen14 as K
from scene import build,save
from checker import Checker,reference
KV=dict(a.split('=',1) for a in sys.argv[1:]);RELAX=KV.get('RELAX')=='1';ZR=(.99,1.21);MAX=float(KV.get('MAX',55));STEP=float(KV.get('STEP',2.5));ZG=1.10
F=K.FRIDGE;H=np.array([F['x'][0],F['y_face']+F['door_t']]);BAR=np.array([F['bar_x'],F['bar_y']])
rz=lambda th,v:np.array([v[0]*np.cos(th)+v[1]*np.sin(th),-v[0]*np.sin(th)+v[1]*np.cos(th)])
DIR=KV.get('DIR','fwd');A=np.arange(0,MAX+1e-9,STEP)
if DIR=='back':A=A[::-1]
start=glob.glob(f"results/r14/reach_pt*_cx-1.48_cy-0.21_fr{A[0]:g}_hdl*.json");start=[f for f in start if json.load(open(f))['ok']][0]
q=np.array(json.load(open(start))['best_q']);print('start',start)
rows=[];prev=None
for a in A:
 th=np.radians(a);p=np.r_[H+rz(th,BAR-H),ZG];ap=np.r_[rz(th,(-1,0)),0];jw=np.r_[rz(th,(0,1)),0]
 cfg=chain.chain_cfg('SD',r14=True,present=[],r14_fridge=True,r14_fridge_door_deg=float(a),r14_held_handle=True)
 tree,meta=build(cfg,None);ch=Checker(tree,meta);m,d=ch.m,ch.d;ids=ch.arm_ids;sid=m.site('R_prep').id
 R=reference.rotation(tuple(ap),tuple(jw))
 target=dict(name='arc',points=[list(p)]*2,held=None,kind='transfer',force=None,approach=list(ap),jaws=[tuple(jw)],jaw_q=0.,cart_x=-1.48);ch.configure_target(target,R)
 lo=np.array([m.jnt_range[j,0] for j in range(m.njnt)])[ids];hi=np.array([m.jnt_range[j,1] for j in range(m.njnt)])[ids]
 def res(x):
  q[ids]=x;d.qpos[:]=q;mujoco.mj_forward(m,d)
  pen=[max(0,req[0]+.010-c.dist) for c in d.contact[:d.ncon] for req in [ch.required(ch,*map(int,c.geom))] if req is not None]
  if RELAX:
   S=d.site_xmat[sid].reshape(3,3);sp=d.site_xpos[sid];phi=np.arctan2(S[:,0]@[0,0,1],S[:,0]@ap)
   return np.r_[(sp[:2]-p[:2])*10,10*max(0,ZR[0]-sp[2],sp[2]-ZR[1]),np.cross(S[:,1],jw),max(0,abs(phi)-np.pi/4),.02*(x-x0),15*np.linalg.norm(pen) if pen else 0.]
  return np.r_[(d.site_xpos[sid]-p)*10,Rotation.from_matrix(R@d.site_xmat[sid].reshape(3,3).T).as_rotvec(),.02*(x-x0),15*np.linalg.norm(pen) if pen else 0.]
 x0=q[ids].copy();r=least_squares(res,np.clip(x0,lo+1e-9,hi-1e-9),bounds=(lo,hi),max_nfev=200,xtol=1e-8,ftol=1e-8)
 q[ids]=r.x;pe,re=ch.pose_error(q,p,R);c=ch.check(q,full=True,kind='transfer',mass=0,force=None)
 if RELAX:
  S=d.site_xmat[sid].reshape(3,3);sp=d.site_xpos[sid].copy();pe=float(np.linalg.norm(sp[:2]-p[:2])+max(0,ZR[0]-sp[2],sp[2]-ZR[1]))
  re=float(np.arcsin(min(1,np.linalg.norm(np.cross(S[:,1],jw)))));tilt=float(np.degrees(np.arctan2(S[:,0]@[0,0,1],S[:,0]@ap)))
  pe=pe if abs(tilt)<=45.5 else 1.
 jump=float(np.max(abs(r.x-x0)))
 reserve=min((v['reserve_mm'] for k,v in c['clearance'].items() if k!='self'),default=None)
 row=dict(deg=float(a),**(dict(z=round(float(d.site_xpos[sid][2]),3),tilt_deg=round(tilt,1)) if RELAX else {}),pos_mm=round(pe*1000,2),rot_deg=round(float(np.degrees(re)),2),collision=bool(c['hits']),reserve_mm=None if reserve is None else round(reserve,1),max_joint_step_deg=round(np.degrees(jump),1),hits=[h if isinstance(h,str) else str(h)[:90] for h in c['hits'][:2]])
 rows.append(row);print(json.dumps(row),flush=True)
ok=all(r['pos_mm']<=5 and r['rot_deg']<=3 and not r['collision'] and r['max_joint_step_deg']<=20 for r in rows)
save(f'results/r14/fridge_arc_{DIR}{"_relax" if RELAX else ""}.json',dict(relax=RELAX,max_deg=MAX,step_deg=STEP,dir=DIR,start=start,cart_x=-1.48,grasp_z=ZG,ok=ok,rows=rows));print('continuous path ok:',ok)
