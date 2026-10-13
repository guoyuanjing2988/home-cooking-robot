"""R19 state-saving copy of r15stirwalk2.py (same method, same checks, same timing; arm option ARM=<id>).
It also stores every arm state of the passing cycle (the working part of each stroke at the 10 ms IK
steps, each return as its 41 checked joint-line points, unwrapped joint values) in
results/r19/stir/stirwalk2_<tag>[_<arm>].json; results/r15 is never written.

R15 stir cycle as the arm would run it: the working part of each stroke (scrape + lift + roll,
stroke phase 0 .. 0.76) follows the stir bench's spatula path exactly by IK continuation; the
return through the air to the next stroke's start is a straight joint-space move (the blade is
out of the food, so its path is free), checked for collisions and the plume rule at 40 points.
Start pose of each stroke: the r15reach candidate at that stroke's first keyframe nearest (in
joint space) to where the previous stroke ended. Joint speeds: the working part at the bench
timing (PERIOD); the return at <= 180 °/s with a trapezoid (accel 360 °/s², an assumption).
Unchanged checker, plume rule as in r15reach.py. Reports the stroke period the arm can keep.
python r15stirwalk2.py KEYS=<keys json> REACH=<reach json pattern with {i}> [GRIP=.45] [LIFT=.01]
 [KPS=16 keys per stroke] [NSTROKE=5] [PERIOD=2.4]   -> results/r15/stirwalk2_<tag>.json"""
import sys,os,json,numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation,RotationSpline
from scipy.interpolate import CubicSpline
import chain
from scene import build,save,fmt
from checker import Checker,reference
import kitchen15 as K
KV=dict(a.split('=',1) for a in sys.argv[1:])
GRIP=float(KV.get('GRIP',.45));LIFT=float(KV.get('LIFT',.01));DT=.01;PLUME=.20;KPS=int(KV.get('KPS',16));NS=int(KV.get('NSTROKE',5));P=float(KV.get('PERIOD',2.4))
VMAX,AMAX=180.,360.
import arms;ARM=arms.current();VJ=np.array(arms.speeds(ARM))   # R19: per-joint speed limits of the arm option (ur5e: 180 all, as VMAX)
SCN={}
if KV.get('SCENE')=='r17':   # R18: the current (R17) kitchen: lid rack, spider rest at (1.52, .36), faucet, no tools on the counter end
 import kitchen16 as K16;K16.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K16.TOOL_XY['spider']=(1.52,.36)
 SCN=dict(r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None,'spatula':None})
keys=json.load(open(KV['KEYS']))['keys'];KT=np.array([k['t'] for k in keys])
PS=CubicSpline(KT,np.array([k['p'] for k in keys]),bc_type='clamped');RSPL=RotationSpline(KT,Rotation.from_matrix(np.array([k['R'] for k in keys])))
b=K.SP.grip_point(GRIP);ex=np.array([1.,0,0])
def tcp(t,sign):
 p=PS(t);R=RSPL(t).as_matrix();n=K.SP.C-p;n/=np.linalg.norm(n);pw=p+LIFT*n+K.WOK0
 return pw+R@b,reference.rotation(R@(-K.HD),R@(sign*ex))
models={}
def model(sign):
 if sign in models:return models[sign]
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_spatula=GRIP,r15_spatula_jaw=sign,**SCN);tree,meta=build(cfg,None);ch=Checker(tree,meta)
 E.SubElement(tree.find('worldbody'),'geom',name='r15_plume',type='cylinder',pos=fmt([K.WOK0[0],K.WOK0[1],(K.RIM_Z+1.25)/2]),size=fmt([PLUME,(1.25-K.RIM_Z)/2]),contype='0',conaffinity='0')
 pm=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));pd=mujoco.MjData(pm);pl=pm.geom('r15_plume').id
 rob=[g for g in range(pm.ngeom) if pm.geom(g).name.startswith('R_') and not pm.geom(g).name.startswith(('R_gripper_spatula','R_cart','R_dock'))]
 def plume(q):
  pd.qpos[:]=q;mujoco.mj_forward(pm,pd);ft=np.zeros(6);return 1000*min(mujoco.mj_geomDistance(pm,pd,g,pl,1.,ft) for g in rob)
 models[sign]=(ch,plume);return models[sign]
def jd(q1,q2,ids):return np.degrees(np.abs((np.asarray(q2)[ids]-np.asarray(q1)[ids]+np.pi)%(2*np.pi)-np.pi))
def follow(c,t0,t1):
 sign=c['jaw_sign'];ch,plume=model(sign);m,d=ch.m,ch.d;ids=ch.arm_ids;sid=m.site('R_prep').id
 lo=np.array([m.jnt_range[j,0] for j in range(m.njnt)])[ids];hi=np.array([m.jnt_range[j,1] for j in range(m.njnt)])[ids]
 q=np.array(c['q'],float);vmax=np.zeros(len(ids));prev=None;minres=1e9;minpl=1e9;qs=[]
 for i,t in enumerate(np.arange(t0,t1+1e-9,DT)):
  p,Rt=tcp(t,sign)
  def res(x):
   q[ids]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
   return np.r_[(d.site_xpos[sid]-p)*10,Rotation.from_matrix(Rt@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
  sol=least_squares(res,np.clip(q[ids],lo+1e-8,hi-1e-8),bounds=(lo+1e-9,hi-1e-9),max_nfev=200,xtol=1e-10,ftol=1e-10);q[ids]=sol.x
  pe,re=ch.pose_error(q,p,Rt);qs.append(q.tolist())
  if prev is not None:vmax=np.maximum(vmax,np.degrees(np.abs(sol.x-prev))/DT)
  prev=sol.x.copy();full=i%25==0;chk=ch.check(q,full=full,mass=0.)
  if full:minres=min(minres,min((v['reserve_mm'] for cat,v in chk['clearance'].items() if cat!='self'),default=1e9))
  pl=plume(q);minpl=min(minpl,pl)
  if pe>.005 or re>np.radians(3) or chk['hits'] or pl<0:return None,dict(stop_t=round(t,3),phase=round((t-t0)/P,2),pose_mm=round(pe*1000,1),rot_deg=round(float(np.degrees(re)),1),hits=[h['pair'] for h in chk['hits']][:3],plume_mm=round(pl,1))
 return q.copy(),dict(vmax=vmax.round(0).tolist(),min_reserve_mm=round(minres,1),min_plume_mm=round(minpl,1),states=qs,t0=float(t0),dt=DT)
def transfer(q1,q2,sign):
 ch,plume=model(sign);ids=ch.arm_ids;dq=(np.asarray(q2)[ids]-np.asarray(q1)[ids]+np.pi)%(2*np.pi)-np.pi
 for s in np.linspace(0,1,41)[1:-1]:
  q=np.array(q1,float);q[ids]=np.asarray(q1)[ids]+s*dq;chk=ch.check(q,full=False,mass=0.)
  if chk['hits'] or plume(q)<0:return None,dict(blocked_at=round(float(s),2),hits=[h['pair'] for h in chk['hits']][:3])
 a=float(np.degrees(np.abs(dq)).max());tt=max((2*np.sqrt(aj/AMAX) if aj<v**2/AMAX else aj/v+v/AMAX) for aj,v in zip(np.degrees(np.abs(dq)),VJ))   # per joint (R19); = the VMAX formula when all limits are equal
 Q=[];q=np.array(q1,float)
 for s in np.linspace(0,1,41):q[ids]=np.asarray(q1)[ids]+s*dq;Q.append(q.tolist())
 return tt,dict(max_joint_deg=round(a,1),time_s=round(tt,2),states=Q)
R0=[json.load(open(KV['REACH'].format(i=k*KPS))) for k in range(NS)]
starts=[[c for c in r['cands'] if c['plume_mm'] is not None and c['plume_mm']>=0] for r in R0]
best=None;log=[]
def strip(x):
 if isinstance(x,dict):return {k:strip(v) for k,v in x.items() if k!='states'}
 if isinstance(x,list):return [strip(v) for v in x]
 return x
def stroke_chain(k,c,q_prev_end,sign,acc):
 """depth-first: start stroke k at candidate c (reached from q_prev_end by a joint move), follow it, recurse"""
 if q_prev_end is not None:
  tt,tinfo=transfer(q_prev_end,c['q'],sign)
  if tt is None:return False,acc+[dict(stroke=k,ok=False,ret_into=tinfo)]
 else:tinfo=None
 t0=KT[k*KPS];q_end,info=follow(c,t0,t0+.76*P)
 if q_end is None:return False,acc+[dict(stroke=k,ok=False,**info)]
 acc=acc+[dict(stroke=k,ok=True,ret_into=tinfo,work=info)]
 if k==NS-1:   # close the cycle: back to stroke 0's start
  tt,tinfo=transfer(q_end,acc[0]['q0'],sign)
  return (tt is not None),acc+[dict(stroke='close',ok=tt is not None,ret_into=tinfo)]
 ch,_=model(sign);nxt=sorted([c2 for c2 in starts[k+1] if c2['jaw_sign']==sign and abs(c2['q'][0]-q_end[0])<1e-3],key=lambda c2:jd(q_end,c2['q'],ch.arm_ids).max())[:4]
 last=acc
 for c2 in nxt:
  ok,res=stroke_chain(k+1,c2,q_end,sign,acc)
  if ok:return True,res
  last=res
 return False,last
for c0 in sorted(starts[0],key=lambda c:-c['reserve_mm'])[:int(KV.get('TRIES',8))]:
 ok,strokes=stroke_chain(0,c0,None,c0['jaw_sign'],[dict(q0=c0['q'])])
 strokes=strokes[1:];log.append(dict(start_reserve=c0['reserve_mm'],jaw_sign=c0['jaw_sign'],ok=ok,strokes=strokes));print(json.dumps(strip(log[-1]))[:700],flush=True)
 if ok:best=log[-1];break
if best:
 W=[s for s in best['strokes'] if s.get('work')];Rr=[s['ret_into'] for s in best['strokes'] if s.get('ret_into')]
 vw=max(max(s['work']['vmax']) for s in W);scale=max(1.,max(float(np.max(np.array(s['work']['vmax'])/VJ)) for s in W));ret=max(r['time_s'] for r in Rr)   # per joint (R19)
 period=max(P*scale*.76+ret,P)   # working part slowed to the speed limit + the slowest return
 summary=dict(ok=True,working_part_joint_speed_max_degps=round(vw),working_slowdown=round(scale,2),return_time_max_s=ret,feasible_period_s=round(period,2),
  min_reserve_mm=min(s['work']['min_reserve_mm'] for s in W),min_plume_mm=min(s['work']['min_plume_mm'] for s in W))
else:summary=dict(ok=False)
tag=os.path.basename(KV['KEYS'])[5:-10]+('_'+KV['SCENE'] if 'SCENE' in KV else '')+arms.tag(ARM)
states=None
if best:
 # the cycle as commanded: stroke 0 work, then per stroke the return into it and its work, then the close
 seq=[];kinds=[]
 for st in best['strokes']:
  if st.get('ret_into') and st['ret_into'].get('states'):seq+=st['ret_into']['states'];kinds+=['return']*len(st['ret_into']['states'])
  if st.get('work'):seq+=st['work']['states'];kinds+=[f"work{st['stroke']}"]*len(st['work']['states'])
 Q=np.array(seq);U=Q.copy();U[:,3:9]=np.unwrap(Q[:,3:9],axis=0)
 states=dict(layout='[carriage_x, base_y, base_yaw, q1..q6, finger_l, finger_r]',note='joint values unwrapped (np.unwrap along the sequence); work = 10 ms IK steps of the working part (the first work state follows the reach candidate the return ended at); return = the 41 checked points of the straight joint move',
  kinds=kinds,q=U.tolist(),label_jumps_removed_2pi=np.round((U[:,3:9]-Q[:,3:9])/(2*np.pi)).astype(int).tolist()[-1])
os.makedirs('results/r19/stir',exist_ok=True);fn=f'results/r19/stir/stirwalk2_{tag}.json'
save(fn,dict(keys=KV['KEYS'],reach=KV['REACH'],arm=ARM,grip_m=GRIP,period_bench_s=P,**summary,attempts=strip(log),states=states));print(fn);print(json.dumps(summary))
