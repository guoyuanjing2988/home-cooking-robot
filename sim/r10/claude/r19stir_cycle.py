"""R19 #3: the R15 stir cycle with velocity-continuous returns (and the stop-at-hand-off variant for comparison),
re-checked at <= 4 mm with the plume rule, timed under joint speed / acceleration limits, stored as a library entry.

Method (geometry and timing are separate, as in R19_SMOOTH.md):
 works    every plume-clear stroke-start candidate (r19stir_reach.py, KEEP=48) follows its stroke's working part
          (phase 0 .. 0.76 of the 2.4 s bench stroke) by IK continuation exactly as r15stirwalk2.py / r19stir_save.py
          (10 ms steps, pose <= 5 mm / 3 deg, fast check every step, full check every 25th, plume every step).
          Candidates that end on the same IK branch (end state mod 2pi, 1 deg) are one branch; per branch the member
          with the largest reserve is kept. A working part is stored as an interpolating quintic B-spline q_w(tau)
          through its IK states (tau = bench time, C4); one whose IK sat on a joint limit gets a range-safe smoothing
          spline instead (work_spline()).
 returns  the air move from the end of stroke k's working part to the start of stroke k+1's (and stroke 4 -> 0),
          for every combination of branches (chains), with the 2pi joint labels nearest to the previous part:
            variant A (velocity-continuous): a quintic spline r(u), u in [0, T] (T = nominal duration 0.2 .. 1.2 s),
                      with r, r', r'' = q_w, q_w', q_w'' of both working parts at the hand-offs, so the whole cycle
                      q(s) (s = tau on the works, u on the returns) is ONE closed C2 path;
            variant B (stop at each hand-off): rest to rest, a straight joint line or a natural cubic through the vias
                      (chord-length parameter; the time law starts and ends at rest).
          Vias (16 sets, each with lift h = 3, 6, 10, 15 cm): 'mid' = the TCP pose half-way between the two hand-off
          poses lifted h; 'ends' = the end pose lifted h (at T/3) then the start pose lifted h (at 2T/3); '_back' =
          the same, but pulled back h along the tool axis (the spatula drawn back along its handle) instead of up.
          Each option is screened (fast check + ranges + plume at <= 8 mm by the global point bound); round 0: no via,
          later rounds (resumable, ROUNDS= / PART=) every via set for the returns with no pass yet.
 cycle    the chain with the smallest proxy time (sum of the working parts' own TOPP times and the returns' proxies)
          among those with a screened return for every hand-off; then
          - the geometry (works + returns) re-checked at <= 4 mm (point_bound, as r19enc_check.py) with
            Checker.check(full=True) (contacts + GJK lower-bound certificate, 10 / 5 mm, self, joint ranges), the R11
            held-box mesh rule (r19enc_check.meshheld) and the plume rule (every arm geom except the spatula, cart
            and dock >= 0 mm outside the 0.20 m cylinder about the wok axis, rim .. 1.25 m);
          - the time law: TOPP (reachability analysis, closed form for per-joint linear constraints) on the path,
            joint speed <= the arm's datasheet limit, joint acceleration <= A, the working parts never faster than
            the bench (ds/dt <= 1); variant A periodic (3 cycles unrolled, the middle one kept), variant B rest to
            rest per piece; then a moving-average jerk filter (W) and local slow-downs until every limit holds on
            a 2 ms grid. Retiming never changes the geometry, so it needs no new check.
          - a library entry with its certificate (as r19enc_adopt.py: written only when the re-check is clean, an
            existing file is renamed first): results/r19/stir/lib_stir_cycle_<arm>.json.
Limits: joint speed = arms.speeds(ARM) (UR5e datasheet 180 deg/s; FR5 180 deg/s, arms.py). Joint acceleration:
 UR publishes no maximum; A_UR = 800 deg/s^2 is UR's own guidance for movej ("moveJ accelerations should be less than
 800deg/sec^2", Universal Robots staff, forum.universal-robots.com/t/maximum-axis-speed-acceleration/13338);
 A_R15 = 360 deg/s^2 is the R15 assumption (r15stirwalk2.py). Fairino publishes none (its MoveIt config uses
 0.7 rad/s^2, a planning default): for the FR5 both values are ASSUMPTIONS. No jerk limit is sourced; the jerk
 filter window W (default 0.1 s) is a choice and the peak jerk is reported.
Each command < 5 min (28 workers); see R19_STIR.md for the lanes actually run:
python r19stir_reach.py ARM=<arm> KEEP=48                     -> results/r19/stir/reach/ (stroke-start candidates)
python r19stir_cycle.py works   ARM=<arm>                     -> results/r19/stir/cycle_<arm>/works.json
python r19stir_cycle.py returns ARM=<arm> [ROUNDS=0,1,2,3] [PART=i/n] [FRESH=1] [REDO=<key part>]
                                                              -> .../returns.json (+ returns_cache.json, resumable)
python r19stir_cycle.py cycle   ARM=<arm> [W=.1]              -> .../cycle.json, results/r19/stir/lib_stir_cycle_<arm>.json
python r19stir_report.py                                      -> results/r19/stir/summary.json (independent re-evaluation)"""
import sys,os,json,time,math,hashlib
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
ARM=KV.get('ARM','ur5e_enc2_pgc');os.environ['ARM']=ARM
OUT=f'results/r19/stir/cycle_{ARM}'
KEYS='results/r15/stir_h_scrape_dice_keys.json';GRIP=.45;LIFT=.01;DT=.01;PLUME=.20;KPS=16;NS=5;P=2.4;WORKF=.76
REACH=KV.get('REACH','results/r19/stir/reach/reach_stir_h_scrape_dice_i{i:03d}_g0.45_cx.55_r19_k48_'+ARM+'.json')
WK=int(KV.get('WORKERS',28));STEP=.004;SCREEN=.008
A_LIM={'A_UR':800.,'A_R15':360.}   # deg/s^2, see the docstring
# ---------------------------------------------------------------- bench path (r15stirwalk2.py tcp())
_B={}
def bench():
 if _B:return _B
 from scipy.spatial.transform import Rotation,RotationSpline
 from scipy.interpolate import CubicSpline
 import kitchen15 as K
 keys=json.load(open(KEYS))['keys'];KT=np.array([k['t'] for k in keys])
 _B.update(KT=KT,PS=CubicSpline(KT,np.array([k['p'] for k in keys]),bc_type='clamped'),RS=RotationSpline(KT,Rotation.from_matrix(np.array([k['R'] for k in keys]))),
  b=K.SP.grip_point(GRIP),K=K);return _B
def tcp(t,sign):
 from checker import reference
 B=bench();K=B['K'];p=B['PS'](t);R=B['RS'](t).as_matrix();n=K.SP.C-p;n/=np.linalg.norm(n);pw=p+LIFT*n+K.WOK0
 return pw+R@B['b'],reference.rotation(R@(-K.HD),R@(sign*np.array([1.,0,0])))
def t0_of(k):return float(bench()['KT'][k*KPS])
# ---------------------------------------------------------------- model (r19stir_save.py model(sign), SCENE=r17, + r19enc_check rules)
_M={}
def model(sign):
 if sign in _M:return _M[sign]
 import chain,mujoco,xml.etree.ElementTree as E
 from scene import build,fmt
 from checker import Checker
 import kitchen15 as K15,kitchen16 as K16,arms,r19enc_check as RC,r19smooth as S
 assert arms.current()==ARM,(arms.current(),ARM)
 K16.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K16.TOOL_XY['spider']=(1.52,.36)
 SCN=dict(r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None,'spatula':None})
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_spatula=GRIP,r15_spatula_jaw=sign,**SCN);tree,meta=build(cfg,None);RC.meshheld(tree);ch=Checker(tree,meta)
 E.SubElement(tree.find('worldbody'),'geom',name='r15_plume',type='cylinder',pos=fmt([K15.WOK0[0],K15.WOK0[1],(K15.RIM_Z+1.25)/2]),size=fmt([PLUME,(1.25-K15.RIM_Z)/2]),contype='0',conaffinity='0')
 pm=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));pd=mujoco.MjData(pm);pl=pm.geom('r15_plume').id
 rob=[g for g in range(pm.ngeom) if pm.geom(g).name.startswith('R_') and not pm.geom(g).name.startswith(('R_gripper_spatula','R_cart','R_dock'))]
 def plume(q):
  pd.qpos[:]=q;mujoco.mj_forward(pm,pd);ft=np.zeros(6);best=(1e9,None)
  for g in rob:
   v=1000*mujoco.mj_geomDistance(pm,pd,g,pl,1.,ft)
   if v<best[0]:best=(v,pm.geom(g).name)
  return best
 m=ch.m;ids=ch.arm_ids
 lo=np.array([m.jnt_range[j,0] for j in range(m.njnt)])[ids];hi=np.array([m.jnt_range[j,1] for j in range(m.njnt)])[ids]
 _M[sign]=dict(ch=ch,plume=plume,fb=S.FastBound(ch),ids=ids,lo=lo,hi=hi,sid=m.site('R_prep').id,cfg_md5=hashlib.md5(ch.xml.encode()).hexdigest());return _M[sign]
def _init():
 os.environ['ARM']=ARM
# ---------------------------------------------------------------- stage 1: working parts
def follow(args):
 """r19stir_save.follow, unchanged gates; also records the per-step pose error and joint-limit contact."""
 import mujoco
 from scipy.optimize import least_squares
 from scipy.spatial.transform import Rotation
 k,ci,c=args;sign=c['jaw_sign'];M=model(sign);ch=M['ch'];m,d=ch.m,ch.d;ids=M['ids'];sid=M['sid'];lo,hi=M['lo'],M['hi']
 t0=t0_of(k);t1=t0+WORKF*P;q=np.array(c['q'],float);qs=[];minres=1e9;minpl=(1e9,None);pes=[];res_=[];pinned=0
 for i,t in enumerate(np.arange(t0,t1+1e-9,DT)):
  p,Rt=tcp(t,sign)
  def res(x):
   q[ids]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
   return np.r_[(d.site_xpos[sid]-p)*10,Rotation.from_matrix(Rt@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
  sol=least_squares(res,np.clip(q[ids],lo+1e-8,hi-1e-8),bounds=(lo+1e-9,hi-1e-9),max_nfev=200,xtol=1e-10,ftol=1e-10);q[ids]=sol.x
  pe,re=ch.pose_error(q,p,Rt);qs.append(q.tolist());pes.append(pe*1e3);res_.append(float(np.degrees(re)))
  pinned+=bool(np.any(np.minimum(sol.x-lo,hi-sol.x)<1e-6))
  full=i%25==0;chk=ch.check(q,full=full,mass=0.)
  if full:minres=min(minres,min((v['reserve_mm'] for cat,v in chk['clearance'].items() if cat!='self'),default=1e9))
  pl=M['plume'](q);minpl=min(minpl,pl)
  if pe>.005 or re>np.radians(3) or chk['hits'] or pl[0]<0:
   return dict(stroke=k,cand=ci,sign=sign,ok=False,stop_t=round(t,3),phase=round((t-t0)/P,3),pose_mm=round(pe*1e3,2),rot_deg=round(float(np.degrees(re)),2),hits=[h['pair'] for h in chk['hits']][:3],plume_mm=round(pl[0],1))
 Q=np.array(qs);vf=np.degrees(np.diff(Q[:,3:9],axis=0)/DT);af=np.diff(vf,axis=0)/DT
 return dict(stroke=k,cand=ci,sign=sign,ok=True,states=qs,t0=t0,dt=DT,max_pose_mm=round(max(pes),3),max_rot_deg=round(max(res_),3),pinned_steps=pinned,
  min_reserve_mm=round(minres,2),min_plume_mm=round(minpl[0],2),min_plume_geom=minpl[1],fd_vmax_degps=np.abs(vf).max(0).round(1).tolist(),fd_amax_degps2=np.abs(af).max(0).round(0).tolist())
def works():
 import multiprocessing as mp
 os.makedirs(OUT,exist_ok=True);t00=time.monotonic();jobs=[]
 for k in range(NS):
  R=json.load(open(REACH.format(i=k*KPS)))
  for ci,c in enumerate(R['cands']):
   if c['plume_mm'] is not None and c['plume_mm']>=0:jobs.append((k,ci,c))
 print('follows',len(jobs),{k:sum(1 for j in jobs if j[0]==k) for k in range(NS)},flush=True)
 pool=mp.Pool(WK,initializer=_init);out=pool.map(follow,jobs,chunksize=1);pool.close()
 per={k:[o for o in out if o['stroke']==k] for k in range(NS)}
 for k in range(NS):
  ok=[o for o in per[k] if o['ok']]
  print('stroke',k,'ok %d/%d'%(len(ok),len(per[k])),'pinned',sum(1 for o in ok if o['pinned_steps']),'fails',[ (o['phase'],o['hits'][:1],o['plume_mm']) for o in per[k] if not o['ok']][:4],flush=True)
 json.dump(dict(arm=ARM,reach=REACH,keys=KEYS,grip_m=GRIP,lift_m=LIFT,dt=DT,period_bench_s=P,work_fraction=WORKF,works=out,elapsed_s=round(time.monotonic()-t00)),open(f'{OUT}/works.json','w'))
 print('saved',f'{OUT}/works.json','%.0f s'%(time.monotonic()-t00))
# ---------------------------------------------------------------- geometry helpers
ARMI=list(range(3,9))   # the 6 arm joints in the 11-vector (cart x, base y, base yaw, q1..q6, jaws)
def wspline(Q):
 """interpolating quintic B-spline through a working part's IK states, parameter = bench time from 0"""
 from scipy.interpolate import make_interp_spline
 Q=np.asarray(Q,float);return make_interp_spline(np.arange(len(Q))*DT,Q[:,ARMI],k=5)
def pose_track(M,sp,k,sign,q0,n=None):
 """max TCP position (mm) / rotation (deg) error of a working-part spline against the bench pose, on a 2 ms grid"""
 import mujoco
 from scipy.spatial.transform import Rotation
 L=float(sp.t[-1]);u=np.linspace(0,L,int(L/.002)+1);Q=full_q(q0,sp(u));ch=M['ch'];pe=0.;re=0.
 for t,q in zip(u,Q):
  p,R=tcp(t0_of(k)+t,sign);a,b=ch.pose_error(q,p,R);pe=max(pe,a);re=max(re,b)
 return round(pe*1e3,3),round(float(np.degrees(re)),3)
class SqSpline:
 """a spline whose coordinates j in sq = {j: (limit, sign)} are stored as h with q_j = limit + sign*h^2 (as
 r19smooth.Path's sq), so they can never cross that joint limit; call / derivatives as scipy's BSpline"""
 def __init__(self,base,sq):self.base=base;self.sq=sq;self.t=base.t;self.k=base.k;self.c=base.c
 def __call__(self,x,nu=0):
  H=[self.base(x,n) for n in range(nu+1)];y=np.array(H[nu],float)
  for j,(lim,sg) in self.sq.items():
   h=[v[...,j] for v in H]
   y[...,j]=lim+sg*h[0]**2 if nu==0 else sg*(2*h[0]*h[1] if nu==1 else 2*(h[1]**2+h[0]*h[2]) if nu==2 else 2*(3*h[1]*h[2]+h[0]*self.base(x,3)[...,j]))
  return y
_WS={}
def work_spline(Q,k,sign):
 """the stored geometry of a working part. Normally the interpolating quintic (wspline). If the IK sat on a joint
 limit (least squares at its bound: the joint path has a velocity kink where it leaves the limit, and an
 interpolant would overshoot the range), a C2 cubic smoothing spline instead (scipy make_smoothing_spline, the
 first / last 3 states held; a joint that touches its limit is fitted as limit + h^2, SqSpline), with the most
 smoothing for which the whole spline stays in the joint ranges and within 3.5 mm / 3 deg of the bench pose (2 ms
 grid; the IK gate of r15stirwalk2 is 5 mm / 3 deg: 1.5 mm margin on position). -> spline, info"""
 Q=np.asarray(Q,float);key=(k,sign,hashlib.md5(Q.tobytes()).hexdigest())
 if key in _WS:return _WS[key]
 from scipy.interpolate import make_smoothing_spline,BSpline
 M=model(sign);X=Q[:,ARMI];tau=np.arange(len(Q))*DT;q0=Q[0]
 pin=np.minimum(X-M['lo'],M['hi']-X).min(0)<1e-6
 if not pin.any():
  sp=wspline(Q);_WS[key]=(sp,dict(kind='interp',pinned_joints=[]));return _WS[key]
 wt=np.ones(len(Q));wt[:3]=wt[-3:]=1e4;best=None
 sq={int(j):((float(M['lo'][j]),1.) if (X[:,j]-M['lo'][j]).min()<1e-6 else (float(M['hi'][j]),-1.)) for j in np.nonzero(pin)[0]}
 Xt=X.copy()
 for j,(lim,sg) in sq.items():Xt[:,j]=np.sqrt(np.maximum(sg*(X[:,j]-lim),0.))
 wf=f'{OUT}/work_splines.json';disk=json.load(open(wf)) if os.path.exists(wf) else {};dk='%d:%d:%s'%key
 for lam in ([disk[dk]['lam']] if dk in disk else np.logspace(-10,-3,29)):   # the chosen smoothing is kept on disk (the search takes ~20 s)
  cs=[make_smoothing_spline(tau,Xt[:,j],w=wt,lam=lam) for j in range(6)];sp=SqSpline(BSpline(cs[0].t,np.stack([c_.c for c_ in cs],axis=1),3),sq)
  u=np.linspace(0,tau[-1],int(tau[-1]/.001)+1);Y=sp(u)
  if np.any(Y<M['lo']-1e-9) or np.any(Y>M['hi']+1e-9):continue
  pe,re=pose_track(M,sp,k,sign,q0)
  if pe<=3.5 and re<=3.:best=(sp,dict(kind='smoothing',lam=float(lam),pinned_joints=[int(j) for j in np.nonzero(pin)[0]],sq={str(j):v for j,v in sq.items()},pose_mm=pe,rot_deg=re,max_dev_from_ik_deg=round(float(np.degrees(np.abs(sp(tau)-X).max())),3)))
 if best is None:raise RuntimeError(f'no smoothing of the pinned working part {k} stays in range and within 3.5 mm / 3 deg')
 _WS[key]=best
 if dk not in disk:
  disk=json.load(open(wf)) if os.path.exists(wf) else {};disk[dk]=best[1];json.dump(disk,open(wf,'w'),indent=1)
 return best
def label_shift(qa_end,Qb,lo,hi):
 """2*pi shift per arm joint of working part Qb (n x 11) nearest to the state qa_end, among the shifts that keep
 every state of Qb inside the joint range (the same pose: joints with a +-2pi range carry a label)."""
 Qb=np.asarray(Qb,float)[:,ARMI];sh=np.zeros(6)
 for j in range(6):
  best=None
  for n in (-1,0,1):
   x=Qb[:,j]+2*np.pi*n
   if x.min()<lo[j]-1e-9 or x.max()>hi[j]+1e-9:continue
   d=abs(x[0]-qa_end[ARMI[j]])
   if best is None or d<best[0]:best=(d,n)
  sh[j]=2*np.pi*best[1]
 return sh
def ik_via(M,qa,qb,lift,w=.5,mode='up'):
 """joint state whose TCP is at fraction w between the TCPs of qa and qb (orientation slerped), moved `lift` m
 up (mode 'up') or back along the tool axis, i.e. the spatula pulled back along its handle (mode 'back'); IK from
 the joint state at the same fraction (pose least squares, as follow()). w=0 / 1: at qa / qb."""
 import mujoco
 from scipy.optimize import least_squares
 from scipy.spatial.transform import Rotation,Slerp
 ch=M['ch'];m,d=ch.m,ch.d;ids=M['ids'];sid=M['sid'];P=[];R=[]
 for q in (qa,qb):
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);P.append(d.site_xpos[sid].copy());R.append(d.site_xmat[sid].reshape(3,3).copy())
 Rt=Slerp([0,1],Rotation.from_matrix(R))(w).as_matrix();p=(1-w)*P[0]+w*P[1]+(np.array([0,0,lift]) if mode=='up' else -lift*Rt[:,0])   # tool x = approach (blade side)
 q=(1-w)*np.asarray(qa,float)+w*np.asarray(qb,float)
 def res(x):
  q[ids]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
  return np.r_[(d.site_xpos[sid]-p)*10,Rotation.from_matrix(Rt@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
 sol=least_squares(res,np.clip(q[ids],M['lo']+1e-8,M['hi']-1e-8),bounds=(M['lo']+1e-9,M['hi']-1e-9),max_nfev=200);q[ids]=sol.x
 pe,re=ch.pose_error(q,p,Rt);return q,round(pe*1e3,2)
def ret_A(qe,ve,ae,qs,vs,as_,T,vias=(),fs=()):
 """variant A return: quintic spline on u in [0,T] through qe, the vias (at fs*T), qs with r'=ve, r''=ae at u=0 and
 r'=vs, r''=as_ at u=T (bench-time derivatives of the working parts): the cycle is C2 across the hand-off."""
 from scipy.interpolate import make_interp_spline
 x=[0.]+[f*T for f in fs]+[T];y=[qe[ARMI]]+[np.asarray(v)[ARMI] for v in vias]+[qs[ARMI]]
 return make_interp_spline(x,np.array(y),k=5,bc_type=([(1,ve),(2,ae)],[(1,vs),(2,as_)]))
def ret_B(qe,qs,vias=()):
 """variant B return (rest to rest; the stop at the hand-off is in the time law): straight joint line, or a
 natural cubic spline through the vias; parameter = joint-space chord length (rad)"""
 from scipy.interpolate import make_interp_spline
 y=np.array([qe[ARMI]]+[np.asarray(v)[ARMI] for v in vias]+[qs[ARMI]]);u=np.r_[0,np.cumsum(np.linalg.norm(np.diff(y,axis=0),axis=1))]
 if not len(vias):   # straight line as a quintic in u (so that 3 derivatives exist; it is linear)
  return make_interp_spline(u,y,k=5,bc_type=([(1,(y[1]-y[0])/u[1]),(2,0*y[0])],[(1,(y[1]-y[0])/u[1]),(2,0*y[0])]))
 return make_interp_spline(u,y,k=3,bc_type='natural')
def full_q(q0,X):
 Q=np.tile(np.asarray(q0,float),(len(X),1));Q[:,ARMI]=X;return Q
def cut(M,q0,sp,a,b,step,sub=.0005):
 """parameters of spline sp on [a,b] with point_bound <= step between consecutive states (sum of segment bounds
 over sub-steps <= sub, as r19smooth.sample_path); -> params, max spacing (m)"""
 fb=M['fb'];n=max(3,int((b-a)/.002)+1)
 while True:
  u=np.linspace(a,b,n);Q=full_q(q0,sp(u));bd=np.array([fb(Q[i],Q[i+1]) for i in range(n-1)])
  if bd.max()<=sub*1.0001:break
  n=int(n*bd.max()/sub*1.1)+2
 out=[0];acc=0.;spm=0.
 for i in range(n-1):
  if acc+bd[i]>step:out.append(i);spm=max(spm,acc);acc=0.
  acc+=bd[i]
 if out[-1]!=n-1:out.append(n-1)
 return u[out],max(spm,acc)
def cutg(M,q0,sp,a,b,step):
 """parameters on [a,b] with the GLOBAL point bound (r19smooth.FastBound.g7: max over geoms of lever x |dq|, valid
 for any motion, >= the per-state segment bound) <= step between consecutive states"""
 n=max(3,int((b-a)/.002)+1)
 while True:
  u=np.linspace(a,b,n);X=sp(u);D=np.zeros((n-1,7));D[:,1:]=np.diff(X,axis=0);bd=M['fb'].g7(D)
  if bd.max()<=step/8:break
  n=int(n*bd.max()/(step/8)*1.1)+2
 out=[0];acc=0.
 for i in range(n-1):
  if acc+bd[i]>step:out.append(i);acc=0.
  acc+=bd[i]
 if out[-1]!=n-1:out.append(n-1)
 return u[out]
def screen(M,q0,sp,a,b):
 """fast screening of a return: contacts (Checker.check full=False) + ranges + plume at <= 8 mm (global bound);
 every 4th state first, so that a failing option fails fast"""
 ch=M['ch'];u=cutg(M,q0,sp,a,b,SCREEN);Q=full_q(q0,sp(u));mp_=1e9;order=list(range(0,len(Q),4))+[i for i in range(len(Q)) if i%4]
 for i in order:
  q=Q[i];c=ch.check(q,full=False,mass=0.);pl=M['plume'](q)[0];mp_=min(mp_,pl)
  if c['hits'] or not c['ranges'] or pl<0:return False,dict(at=round(float((u[i]-a)/(b-a)),3),hits=[h['pair'] for h in c['hits']][:2],ranges=bool(c['ranges']),plume_mm=round(pl,1))
 return True,dict(states=len(Q),min_plume_mm=round(mp_,1))
def in_range(M,sp,a,b,n=400):
 X=sp(np.linspace(a,b,n));return bool(np.all(X>=M['lo']-1e-9) and np.all(X<=M['hi']+1e-9))
# ---------------------------------------------------------------- time law (TOPP-RA, closed form for per-joint limits)
def topp(s,qp,qpp,V,A,cap,x0=0.,xN=0.):
 """max x = s'^2 on grid s (N+1) under |q' s'| <= V, |q' s'' + q'' s'^2| <= A (per grid point and joint; A may be
 an (N+1, n) array), x <= cap; x0 / xN fixed (None = free). Returns x, the max-velocity curve."""
 N=len(s)-1;D=np.diff(s);A=np.broadcast_to(A,qp.shape).astype(float);a=qp;b=qpp;eps=1e-12
 with np.errstate(divide='ignore',invalid='ignore'):
  xv=np.min(np.where(np.abs(a)>eps,(V/np.maximum(np.abs(a),eps))**2,np.inf),axis=1)
  deg=np.abs(a)<=1e-9;xd=np.min(np.where(deg&(np.abs(b)>eps),A/np.maximum(np.abs(b),eps),np.inf),axis=1)
  w=np.where(deg,np.nan,A/np.maximum(np.abs(a),eps));be=np.where(deg,np.nan,-b/np.where(deg,1.,a))   # u in [-w_j + be_j x, w_j + be_j x]
  dB=be[:,:,None]-be[:,None,:];sw=w[:,:,None]+w[:,None,:]
  xp=np.nanmin(np.where(dB>eps,sw/np.where(dB>eps,dB,1.),np.inf),axis=(1,2))
 xmax=np.minimum.reduce([xv,xd,xp,np.broadcast_to(cap,xv.shape).astype(float)]);xmax=np.where(np.isfinite(xmax),xmax,1e6)
 K=np.zeros(N+1);K[N]=xmax[N] if xN is None else min(xN,xmax[N])
 for i in range(N-1,-1,-1):
  wi,bi=w[i],be[i];ok=~np.isnan(wi)
  if not ok.any():K[i]=xmax[i];continue
  c=1+2*D[i]*bi[ok];wo=wi[ok];ub=[xmax[i]]
  pos=c>1e-12;ub+=list((K[i+1]+2*D[i]*wo[pos])/c[pos])
  neg=c<-1e-12;ub+=list(2*D[i]*wo[neg]/(-c[neg]))
  K[i]=max(0.,min(ub))
 x=np.zeros(N+1);x[0]=K[0] if x0 is None else min(x0,K[0])
 for i in range(N):
  wi,bi=w[i],be[i];ok=~np.isnan(wi)
  hi_=np.min(wi[ok]+bi[ok]*x[i]) if ok.any() else np.inf
  u=min(hi_,(K[i+1]-x[i])/(2*D[i]));x[i+1]=min(max(x[i]+2*D[i]*u,0.),K[i+1])
  if 0<i+1<N:x[i+1]=max(x[i+1],min(1e-8,K[i+1]))
 return x,xmax
class Path:
 """C2 composite path q(s) (6 arm joints): consecutive segments (spline, local a, b); periodic (s mod L) if per"""
 def __init__(self,segs,per=False):
  self.segs=segs;self.B=np.r_[0,np.cumsum([b-a for sp,a,b in segs])];self.L=float(self.B[-1]);self.per=per
 def __call__(self,s,nu=0):
  s=np.atleast_1d(np.asarray(s,float))
  if self.per:
   r=np.mod(s,self.L);r=np.where((r<1e-12)&(s>1e-12),self.L,r);s=r
  else:s=np.clip(s,0,self.L)
  k=np.clip(np.searchsorted(self.B,s,side='right')-1,0,len(self.segs)-1);out=np.zeros((len(s),6))
  for j in np.unique(k):
   sp,a,b=self.segs[j];m=k==j;out[m]=sp(a+s[m]-self.B[j],nu)
  return out
def grid(path,ds=.002,reps=1):
 g=[]
 for r in range(reps):
  for j,(sp,a,b) in enumerate(path.segs):
   n=max(4,int(math.ceil((b-a)/ds)));g.append(r*path.L+path.B[j]+np.linspace(0,b-a,n+1)[:-1])
 g.append([reps*path.L]);return np.concatenate(g)
def verify(path,t,s,sd,V,A,capf):
 """joint speed / acceleration / jerk and s' against its cap on the time grid; ratios per sample"""
 H=t[1]-t[0];sdd=np.gradient(sd,H);sddd=np.gradient(sdd,H)
 q1,q2,q3=path(s,1),path(s,2),path(s,3)
 v=q1*sd[:,None];a=q2*sd[:,None]**2+q1*sdd[:,None];j=q3*sd[:,None]**3+3*q2*(sd*sdd)[:,None]+q1*sddd[:,None]
 rat=dict(v=np.max(np.abs(v)/V,axis=1),a=np.max(np.abs(a)/A,axis=1),cap=sd/np.sqrt(capf(s)))
 return rat,dict(v=np.abs(v).max(0),a=np.abs(a).max(0),j=np.abs(j).max(0))
EXP=dict(v=2.,a=1.,cap=2.)
def timelaw(path,V,A,capf,x0=0.,xN=0.,W=.1,reps=1,iters=25):
 """TOPP + r19smooth.timelaw (erosion + moving-average jerk filter W, 2 ms grid) + local slow-downs until every
 limit holds on the 2 ms grid -> dict(t, s, sd, worst ratios, peaks)"""
 import r19smooth as S
 from types import SimpleNamespace as NS
 sg=grid(path,reps=reps);qp,qpp=path(sg,1),path(sg,2);cap=capf(sg);kap=np.ones(len(sg));seg=NS(N=len(sg)-1,s=sg,dsv=np.diff(sg),path=NS(L=float(sg[-1])))
 for it in range(iters):
  x,_=topp(sg,qp,qpp,V,A*kap[:,None],cap*kap,x0,xN);t,s,sd=S.timelaw(seg,x,W);rat,pk=verify(path,t,s,sd,V,A,capf)
  worst={k_:float(v_.max()) for k_,v_ in rat.items()}
  if max(worst.values())<=1+1e-3:break
  need=np.ones(len(s))
  for k_,v_ in rat.items():need=np.minimum(need,np.where(v_>1,(.98/np.maximum(v_,1e-9))**EXP[k_],1.))
  idx=np.nonzero(need<1)[0];kn=kap.copy()
  for s_,n_,sd_ in zip(s[idx],need[idx],sd[idx]):
   sel=np.abs(sg-s_)<=sd_*W+.01;kn[sel]=np.minimum(kn[sel],kap[sel]*n_)
  kap=np.maximum(kn,1e-4)
  if reps>1:   # periodic geometry: the same slow-downs in every unrolled cycle, so the middle cycle is exactly periodic
   n_=(len(sg)-1)//reps;km=kap[:-1].reshape(reps,n_).min(0);kap[:-1]=np.tile(km,reps);kap[-1]=km[0]
 return dict(t=t,s=s,sd=sd,worst={k_:round(v_,4) for k_,v_ in worst.items()},peaks=pk,iters=it+1,kappa_min=float(kap.min()),converged=max(worst.values())<=1+1e-3)
# ---------------------------------------------------------------- stage 2: returns
def limits():
 import arms
 return np.radians(arms.speeds(ARM)),{k:math.radians(v) for k,v in A_LIM.items()}
def groups(W):
 """distinct working parts per (stroke, jaw sense): the same IK branch = the same end state mod 2pi (1 deg);
 representative = the member with the largest min reserve"""
 G={}
 for w in W:
  if not w['ok']:continue
  e=np.array(w['states'][-1])[ARMI];key=(w['stroke'],w['sign'])+tuple(int(x) for x in np.round(np.degrees((e+np.pi)%(2*np.pi)-np.pi)))
  G.setdefault(key,[]).append(w)
 out={}
 for key,g in sorted(G.items()):
  out.setdefault((key[0],key[1]),[]).append(dict(rep=max(g,key=lambda w:w['min_reserve_mm']),n=len(g)))
 return out
def wtime(Q,V,A,free,k,sign):
 """proxy: TOPP time of a working part alone (s' <= 1 = never faster than the bench), free or rest ends"""
 sp=work_spline(Q,k,sign)[0];L=(len(Q)-1)*DT;s=np.linspace(0,L,int(L/.002)+1)
 x,_=topp(s,sp(s,1),sp(s,2),V,A,np.ones(len(s)),None if free else 0.,None if free else 0.)
 return float(np.sum(2*np.diff(s)/np.maximum(np.sqrt(x[1:])+np.sqrt(x[:-1]),1e-9)))
def chains_of(G,lo,hi):
 """every combination of one working-part branch per stroke (same jaw sense), with the 2pi labels of each part
 chosen nearest to the previous part's end (stroke 0 as found); the close return goes back to stroke 0's labels"""
 import itertools
 out=[]
 for sign in (-1,1):
  if not all((k,sign) in G for k in range(NS)):continue
  for combo in itertools.product(*[range(len(G[(k,sign)])) for k in range(NS)]):
   sh=[np.zeros(6)];prev=np.array(G[(0,sign)][combo[0]]['rep']['states'])
   for k in range(1,NS):
    Q=np.array(G[(k,sign)][combo[k]]['rep']['states']);s_=label_shift(prev[-1],Q,lo,hi);sh.append(s_);Q[:,ARMI]+=s_;prev=Q
   out.append(dict(sign=sign,combo=list(combo),shift_n=[[int(round(v/(2*np.pi))) for v in s_] for s_ in sh]))
 return out
def wstates(G,sign,k,gi,shift_n):
 Q=np.array(G[(k,sign)][gi]['rep']['states']);Q[:,ARMI]+=2*np.pi*np.array(shift_n);return Q
def handoff(Qe,Qs,key,sign):
 """state, velocity, acceleration (bench time) where the working parts of a return's key end / start (from their
 stored splines: the state is the spline's, = the IK state for an interpolating one)"""
 ke,ks=int(key[0]),int(key.split('>')[1][0]);spe,sps=work_spline(Qe,ke,sign)[0],work_spline(Qs,ks,sign)[0];Le=(len(Qe)-1)*DT
 return full_q(Qe[0],spe(Le))[0],spe(Le,1),spe(Le,2),full_q(Qs[0],sps(0.))[0],sps(0.,1),sps(0.,2)
def ret_spline(var,o,H):
 qe,ve,ae,qs,vs,as_=H;vias=[np.array(v) for v in o['via']]
 if var=='A':return ret_A(qe,ve,ae,qs,vs,as_,o['T'],vias,o['f']),o['T']
 sp=ret_B(qe,qs,vias);return sp,float(sp.t[-1])
def plan_options(job):
 """phase 1 of a return: the vias (IK) and every option with its proxy time (no collision check yet).
 A: quintic C2 hand-offs, nominal duration T x via lift; proxy = T x the uniform slow-down that its own peak joint
 speed / acceleration need. B: rest-to-rest line / via spline; proxy = its rest-to-rest TOPP time."""
 key,sign,Qe,Qs=job;M=model(sign);V,AL=limits();A=AL['A_UR'];H=handoff(Qe,Qs,key,sign);qe,ve,ae,qs,vs,as_=H
 assert np.allclose(np.delete(qe,ARMI),np.delete(qs,ARMI)),'cart / base / jaws differ between the strokes'
 VS={('none',0.):([],[],[])}
 for h in LIFTS:
  for mode,tag in (('up',''),('back','_back')):
   q1,p1=ik_via(M,qe,qs,h,.5,mode);VS[('mid'+tag,h)]=([q1.tolist()],[.5],[p1])
   q1,p1=ik_via(M,qe,qs,h,0.,mode);q2,p2=ik_via(M,qe,qs,h,1.,mode);VS[('ends'+tag,h)]=([q1.tolist(),q2.tolist()],[1/3,2/3],[p1,p2])
 optA=[];optB=[]
 for (kind,h),(vq,vf,vp) in VS.items():
  for T in TGRID:
   o=dict(T=round(float(T),3),via_kind=kind,lift=h,via=vq,f=vf,via_pose_mm=vp);sp,L=ret_spline('A',o,H)
   if not in_range(M,sp,0,L):continue
   u=np.linspace(0,L,400);pv=np.abs(sp(u,1)).max(0);pa=np.abs(sp(u,2)).max(0)
   optA.append(dict(o,proxy_s=round(float(T*max(1.,float(np.max(pv/V)),math.sqrt(float(np.max(pa/A))))),4),peak_v_degps=round(float(np.degrees(pv.max())),1),peak_a_degps2=round(float(np.degrees(pa.max())),0)))
  o=dict(via_kind=kind,lift=h,via=vq,f=vf,via_pose_mm=vp);sp,L=ret_spline('B',o,H)
  if not in_range(M,sp,0,L):continue
  sg=np.linspace(0,L,int(L/.001)+2);x,_=topp(sg,sp(sg,1),sp(sg,2),V,A,np.full(len(sg),1e12),0.,0.)
  optB.append(dict(o,L=L,proxy_s=round(float(np.sum(2*np.diff(sg)/np.maximum(np.sqrt(x[1:])+np.sqrt(x[:-1]),1e-9))),4)))
 optA.sort(key=lambda o:o['proxy_s']);optB.sort(key=lambda o:o['proxy_s'])
 return dict(key=key,sign=sign,A=optA,B=optB,handoff=dict(end_v_degps=np.degrees(ve).round(1).tolist(),end_a_degps2=np.degrees(ae).round(0).tolist(),start_v_degps=np.degrees(vs).round(1).tolist(),start_a_degps2=np.degrees(as_).round(0).tolist()))
def screen_option(job):
 """phase 2: screen one option (fast check + ranges + plume, <= 8 mm by the global point bound)"""
 key,sign,var,i,o,Qe,Qs=job;M=model(sign);H=handoff(Qe,Qs,key,sign);sp,L=ret_spline(var,o,H);t0=time.monotonic()
 ok,info=screen(M,H[0],sp,0,L);return dict(key=key,var=var,i=i,ok=ok,info=info,s=round(time.monotonic()-t0,2))
TGRID=np.round(np.arange(.20,1.201,.10),3);LIFTS=(.03,.06,.10,.15);NROUND=4
def pairs_of(G,ch):
 """the 5 returns of a chain: (key, from-stroke states, to-stroke states)"""
 sign=ch['sign'];P=[]
 for k in range(NS):
  k2=(k+1)%NS;sh2=ch['shift_n'][k2] if k2 else [0]*6
  key='%d:%d%s>%d:%d%s'%(k,ch['combo'][k],ch['shift_n'][k],k2,ch['combo'][k2],sh2)
  P.append((key,wstates(G,sign,k,ch['combo'][k],ch['shift_n'][k]),wstates(G,sign,k2,ch['combo'][k2],sh2)))
 return P
def returns():
 import multiprocessing as mp,arms
 t00=time.monotonic();W=json.load(open(f'{OUT}/works.json'))['works'];G=groups(W)
 M=model(-1 if (0,-1) in G else 1);lo,hi=M['lo'],M['hi'];V,AL=limits()
 CH=chains_of(G,lo,hi);print('branches',{f'{k}': len(v) for k,v in G.items()},'chains',len(CH),flush=True)
 wt={}
 for (k,sign),gs in G.items():
  for gi,g in enumerate(gs):
   Q=np.array(g['rep']['states']);wt[f'{k}:{sign}:{gi}']=dict(free_s=round(wtime(Q,V,AL['A_UR'],True,k,sign),4),rest_s=round(wtime(Q,V,AL['A_UR'],False,k,sign),4),
    free_R15_s=round(wtime(Q,V,AL['A_R15'],True,k,sign),4),spline=work_spline(Q,k,sign)[1],n=g['n'],cand=g['rep']['cand'],pinned=g['rep']['pinned_steps'],fd_amax=max(g['rep']['fd_amax_degps2']))
 jobs={}
 for ch in CH:
  for key,Qe,Qs in pairs_of(G,ch):jobs.setdefault((ch['sign'],key),(key,ch['sign'],Qe,Qs))
 print('returns to plan',len(jobs),flush=True)
 pool=mp.Pool(WK,initializer=_init);cf=f'{OUT}/returns_cache.json'
 # resumable (each command < 5 min): ROUNDS=<r,...> runs those screening rounds only; PART=i/n runs part i of n of
 # each; the options and every screening result are cached in returns_cache.json and reused by the next command
 cache=json.load(open(cf)) if os.path.exists(cf) and 'FRESH' not in KV else None
 if cache:
  opts,sc=cache['opts'],cache['sc']
  if 'REDO' in KV:   # REDO=<substring>: re-plan and re-screen only the returns whose key contains it
   red=KV['REDO'];opts=[o for o in opts if red not in o['key']];sc=[x for x in sc if red not in x['key']]
   opts+=pool.map(plan_options,[j for (sg_,k_),j in jobs.items() if red in k_],chunksize=1);json.dump(dict(opts=opts,sc=sc),open(cf,'w'),default=float)
 else:opts=pool.map(plan_options,list(jobs.values()),chunksize=1);sc=[];json.dump(dict(opts=opts,sc=sc),open(cf,'w'),default=float)
 assert {(o['sign'],o['key']) for o in opts}==set(jobs),'cache is for another set of returns: FRESH=1'
 done={(x['key'],x['var'],x['i']) for x in sc}
 RR=[int(r) for r in KV.get('ROUNDS',','.join(map(str,range(NROUND)))).split(',')];pi,pn=map(int,KV.get('PART','0/1').split('/'))
 for rnd in RR:
  # round 0: no via (A: its 3 cheapest durations; B: the straight line); round r >= 1, only for the returns (and
  # variant) with no pass yet: the (r-1)-th cheapest option of every via set (B has one option per via set)
  J=[]
  for o in opts:
   _,sign,Qe,Qs=jobs[(o['sign'],o['key'])]
   for var in 'AB':
    if rnd and any(x['ok'] for x in sc if x['key']==o['key'] and x['var']==var):continue
    if rnd>1 and var=='B':continue
    seen={}
    for i,x in enumerate(o[var]):
     vk=(x['via_kind'],x['lift']);seen[vk]=seen.get(vk,-1)+1
     if (rnd==0 and vk[0]=='none' and seen[vk]<3) or (rnd and vk[0]!='none' and seen[vk]==rnd-1):J.append((o['key'],sign,var,i,x,Qe,Qs))
  J=[j for j in J if (j[0],j[2],j[3]) not in done][pi::pn]
  print('round',rnd,'part %d/%d'%(pi,pn),'options screened',len(J),'%.0f s'%(time.monotonic()-t00),flush=True)
  new=pool.map(screen_option,J,chunksize=1);sc+=new;done|={(x['key'],x['var'],x['i']) for x in new};json.dump(dict(opts=opts,sc=sc),open(cf,'w'),default=float)
 pool.close()
 res=[]
 for o in opts:
  r_=dict(key=o['key'],handoff=o['handoff'],A_options=len(o['A']),B_options=len(o['B']))
  for var in 'AB':
   ss={x['i']:x for x in sc if x['key']==o['key'] and x['var']==var}
   r_[var]=[dict(o[var][i],screen=ss[i]['info']) for i in sorted(ss) if ss[i]['ok']]
   r_[var+'_fails']=[dict(T=o[var][i].get('T'),via_kind=o[var][i]['via_kind'],lift=o[var][i]['lift'],**ss[i]['info']) for i in sorted(ss) if not ss[i]['ok']]
  res.append(r_)
 R={(r_['key']):r_ for r_ in res}
 for ch in CH:
  P=pairs_of(G,ch);ra=[R[k]['A'][0]['proxy_s'] if R[k]['A'] else None for k,_,_ in P];rb=[R[k]['B'][0]['proxy_s'] if R[k]['B'] else None for k,_,_ in P]
  wa=[wt[f"{k}:{ch['sign']}:{ch['combo'][k]}"]['free_s'] for k in range(NS)];wb=[wt[f"{k}:{ch['sign']}:{ch['combo'][k]}"]['rest_s'] for k in range(NS)]
  ch.update(returns=[k for k,_,_ in P],cost_A=None if None in ra else round(sum(wa)+sum(ra),3),cost_B=None if None in rb else round(sum(wb)+sum(rb),3),ret_A=ra,ret_B=rb,work_free=wa,work_rest=wb)
 for ch in sorted(CH,key=lambda c:(c['cost_A'] is None,c['cost_A'] or 0))[:12]:print(ch['combo'],ch['shift_n'],'A',ch['cost_A'],ch['ret_A'],'B',ch['cost_B'],ch['ret_B'],flush=True)
 for r_ in res:print(r_['key'],'A',[(o['T'],o['via_kind'],o['lift'],o['proxy_s']) for o in r_['A'][:3]],'of',r_['A_options'],'fails',len(r_['A_fails']),[(f['T'],f['via_kind'],f['lift'],f['at'],f['hits'][:1],f['plume_mm']) for f in r_['A_fails'][:2]],'B',[(o['via_kind'],o['lift'],o['proxy_s']) for o in r_['B'][:2]],'Bfails',[(f['via_kind'],f['lift'],f['at'],f['hits'][:1]) for f in r_['B_fails'][:3]],flush=True)
 json.dump(dict(arm=ARM,limits_degps=np.degrees(V).tolist(),A_limits_degps2=A_LIM,work_times=wt,chains=CH,returns=res,tgrid=TGRID.tolist(),lifts=LIFTS,elapsed_s=round(time.monotonic()-t00)),open(f'{OUT}/returns.json','w'),default=float)
 print('saved',f'{OUT}/returns.json','%.0f s'%(time.monotonic()-t00))
# ---------------------------------------------------------------- stage 3: cycle, certificate, time laws, library entry
def _chk(args):
 """Checker.check(full=True) + plume of each state (r19enc_check.one: hit pairs classed by the exact convex bound)"""
 import r19enc_check as RC
 sign,Q=args;M=model(sign);return [RC.one(M,np.asarray(q)) for q in Q]
def certify(pool,sign,segs,q0):
 """every segment cut at <= 4 mm (point_bound, as r19smooth.sample_path / r19enc_check) and fully checked"""
 import r19enc_check as RC
 M=model(sign);out=[];jobs=[];idx=[]
 for j,(name,sp,a,b) in enumerate(segs):
  u,spm=cut(M,q0,sp,a,b,STEP);Q=full_q(q0,sp(u));out.append(dict(name=name,params=u,Q=Q,max_step_bound_mm=round(spm*1e3,3)))
  for i in range(0,len(Q),12):jobs.append((sign,Q[i:i+12].tolist()));idx.append(j)
 res=pool.map(_chk,jobs,chunksize=1)
 for o in out:o['rs']=[]
 for j,r_ in zip(idx,res):out[j]['rs']+=r_
 for o in out:o['summary']=RC.summarize(o['rs'],np.arange(len(o['rs'])))
 return out
def seg_summary(c):
 s_=c['summary'];return dict(name=c['name'],states=len(c['Q']),max_step_bound_mm=c['max_step_bound_mm'],ok=s_['ok'],hit_states=s_['hit_states'],out_of_range_states=s_['out_of_range_states'],
  hit_pairs=list(s_['hit_pairs'])[:4],min_reserve_by_category=s_['min_reserve_by_category'],min_plume_mm=s_.get('min_plume_mm'),min_plume_geom=s_.get('min_plume_geom'),plume_violations=s_.get('plume_violations'))
def law_summary(path,L_cyc,tl,V,A,capf,mid=True,nseg=None):
 """period of the middle cycle (periodic law) or total time, and the peaks over it"""
 t,s,sd=tl['t'],tl['s'],tl['sd']
 if mid:
  t1,t2=np.interp(L_cyc,s,t),np.interp(2*L_cyc,s,t);m=(t>=t1)&(t<=t2)
 else:t1,t2=0.,t[-1];m=np.ones(len(t),bool)
 rat,pk=verify(path,t[m],s[m],sd[m],V,A,capf)
 out=dict(cycle_s=round(float(t2-t1),3),period_per_stroke_s=round(float(t2-t1)/NS,3),peak_v_degps=np.degrees(pk['v']).round(1).tolist(),peak_a_degps2=np.degrees(pk['a']).round(0).tolist(),
  peak_j_degps3=np.degrees(pk['j']).round(0).tolist(),worst_ratio={k:round(float(v.max()),4) for k,v in rat.items()},converged=tl['converged'],iters=tl['iters'],kappa_min=round(tl['kappa_min'],4))
 if mid:
  out['sdot_at_cycle_ends']=[round(float(np.interp(L_cyc,s,sd)),4),round(float(np.interp(2*L_cyc,s,sd)),4)]
  out['three_cycles_from_rest_s']=round(float(t[-1]),3)
  if nseg is not None:   # time of every segment inside the middle cycle
   B=nseg;out['segment_s']=[round(float(np.interp(L_cyc+B[j+1],s,t)-np.interp(L_cyc+B[j],s,t)),3) for j in range(len(B)-1)]
 return out
def cycle():
 import multiprocessing as mp,r19enc_check as RC,arms
 t00=time.monotonic();W=json.load(open(f'{OUT}/works.json'));G=groups(W['works']);RJ=json.load(open(f'{OUT}/returns.json'));R={r_['key']:r_ for r_ in RJ['returns']}
 V,AL=limits();WL=float(KV.get('W',.1))
 CH=sorted([c for c in RJ['chains'] if c['cost_A'] is not None],key=lambda c:c['cost_A'])
 if not CH:print('no chain with a screened velocity-continuous return for every hand-off');return
 ch=CH[0];sign=ch['sign'];P=pairs_of(G,ch);M=model(sign);q0=P[0][1][0].copy()
 for key,Qe,Qs in P:assert np.allclose(np.delete(Qe[0],ARMI),np.delete(q0,ARMI))
 print('chain',ch['combo'],ch['shift_n'],'proxy A',ch['cost_A'],'B',ch['cost_B'],flush=True)
 import pickle
 pool=mp.Pool(WK,initializer=_init);cf=f'{OUT}/cert_cache.pkl'   # certification results (Q, per-state checks) of this chain, reused by a re-run
 cache=pickle.load(open(cf,'rb')) if os.path.exists(cf) else {}
 if cache.get('chain')!=(ch['combo'],ch['shift_n']):cache=dict(chain=(ch['combo'],ch['shift_n']))
 works_=[(f'work{k}',work_spline(Qe,k,sign)[0],0.,(len(Qe)-1)*DT) for k,(key,Qe,Qs) in enumerate(P)]
 wsp_info=[dict(work_spline(Qe,k,sign)[1],**dict(zip(('pose_mm','rot_deg'),pose_track(M,work_spline(Qe,k,sign)[0],k,sign,q0)))) for k,(key,Qe,Qs) in enumerate(P)]
 print('work splines',wsp_info,flush=True)
 if 'works' not in cache:cache['works']=certify(pool,sign,works_,q0);pickle.dump(cache,open(cf,'wb'))
 cw=cache['works'];print('works',[seg_summary(c)['ok'] for c in cw],'%.0f s'%(time.monotonic()-t00),flush=True)
 assert all(c['summary']['ok'] for c in cw),[seg_summary(c) for c in cw if not c['summary']['ok']]
 # returns: every return of both variants at its cheapest option in one batch; a failing one moves to its next option
 pick={(var,k):0 for var in 'AB' for k in range(NS)};done={}
 while len(done)<2*NS:
  todo=[(var,k) for (var,k) in pick if (var,k) not in done];batch=[]
  for var,k in todo:
   key,Qe,Qs=P[k];opts_=R[key][var]
   if pick[(var,k)]>=len(opts_):raise SystemExit(f'{var}: no option of {key} certifies')
   o=opts_[pick[(var,k)]];ck=(var,key,pick[(var,k)])
   if ck not in cache:sp,L=ret_spline(var,o,handoff(Qe,Qs,key,sign));batch.append((ck,(f'return{k}->{(k+1)%NS}',sp,0.,L)))
  if batch:
   for (ck,_),c in zip(batch,certify(pool,sign,[b_ for _,b_ in batch],q0)):cache[ck]=c
   pickle.dump(cache,open(cf,'wb'))
  for var,k in todo:
   key=P[k][0];i=pick[(var,k)];o=R[key][var][i];c=cache[(var,key,i)]
   print(var,key,'option',i,o.get('T'),o['via_kind'],o['lift'],'certified' if c['summary']['ok'] else 'FAILS %s'%list(c['summary']['hit_pairs'])[:2],c['summary'].get('min_plume_mm'),'%.0f s'%(time.monotonic()-t00),flush=True)
   if c['summary']['ok']:done[(var,k)]=i
   else:pick[(var,k)]+=1
 chosen={};cr={}
 for var in 'AB':
  segs=[];certs=[]
  for k,(key,Qe,Qs) in enumerate(P):
   i=done[(var,k)];o=R[key][var][i];sp,L=ret_spline(var,o,handoff(Qe,Qs,key,sign))
   segs.append((sp,0.,L));certs.append(cache[(var,key,i)]);chosen.setdefault(var,[]).append(dict(key=key,option=i,**{k_:v_ for k_,v_ in o.items() if k_ not in ('screen',)}))
  cr[var]=dict(segs=segs,certs=certs)
 # ---- the geometry of each variant (works + returns, in cycle order) and its time laws
 out=dict(arm=ARM,chain=ch,works_file=f'{OUT}/works.json',returns_file=f'{OUT}/returns.json',limits=dict(v_degps=np.degrees(V).round(3).tolist(),A_degps2=A_LIM,
  v_source=arms.ARMS[ARM]['speeds_source'],A_UR_source='UR guidance, not a datasheet value: "moveJ accelerations should be less than 800deg/sec^2" (Universal Robots staff, https://forum.universal-robots.com/t/maximum-axis-speed-acceleration/13338); for a non-UR arm an ASSUMPTION',
  A_R15_source='ASSUMPTION of R15 (r15stirwalk2.py AMAX)',jerk='no limit; moving-average filter W=%g s (r19smooth.timelaw), peaks reported'%WL),variants={})
 wseg=[(sp,a,b) for name,sp,a,b in works_];bench=[]
 for k,(sp,a,b) in enumerate(wseg):
  u=np.linspace(a,b,2000);bench.append(dict(stroke=k,bench_s=round(b-a,3),peak_v_degps=round(float(np.degrees(np.abs(sp(u,1)).max())),1),peak_a_degps2=round(float(np.degrees(np.abs(sp(u,2)).max())),0)))
 out['works_at_bench_timing']=bench;out['work_splines']=wsp_info
 for var in 'AB':
  segs=[];names=[]
  for k in range(NS):segs+=[wseg[k],cr[var]['segs'][k]];names+=[f'work{k}',f'return{k}->{(k+1)%NS}']
  isw=np.array([n.startswith('work') for n in names])
  path=Path(segs,per=(var=='A'));Lc=path.L;B=path.B
  def capf(s,path=path,isw=isw):
   r=np.mod(np.asarray(s,float),path.L);k=np.clip(np.searchsorted(path.B,r,side='right')-1,0,len(path.segs)-1);return np.where(isw[k],1.,1e12)
  vo=dict(segments=names,returns=chosen[var],laws={})
  if var=='A':   # nominal: works at bench timing, returns at their nominal duration (s' = 1)
   sg=grid(path);vo['nominal_s_dot_1']=dict(cycle_s=round(Lc,3),period_per_stroke_s=round(Lc/NS,3),peak_v_degps=np.degrees(np.abs(path(sg,1)).max(0)).round(1).tolist(),peak_a_degps2=np.degrees(np.abs(path(sg,2)).max(0)).round(0).tolist())
  for an,A_ in AL.items():
   if var=='A':
    tl=timelaw(path,V,A_,capf,0.,0.,WL,reps=3);vo['laws'][an]=law_summary(path,Lc,tl,V,A_,capf,True,B)
    if an=='A_UR':keep=tl
   else:   # rest to rest per segment
    tot=0.;pv=np.zeros(6);pa=np.zeros(6);pj=np.zeros(6);segt=[];conv=True;wr={}
    for j,sg_ in enumerate(segs):
     p1=Path([sg_]);cf=(lambda s,w=isw[j]:np.full(len(np.atleast_1d(s)),1. if w else 1e12));tl=timelaw(p1,V,A_,cf,0.,0.,WL)
     ls=law_summary(p1,p1.L,tl,V,A_,cf,False);tot+=ls['cycle_s'];segt.append(ls['cycle_s']);conv&=tl['converged']
     pv=np.maximum(pv,ls['peak_v_degps']);pa=np.maximum(pa,ls['peak_a_degps2']);pj=np.maximum(pj,ls['peak_j_degps3'])
     for k_,v_ in ls['worst_ratio'].items():wr[k_]=max(wr.get(k_,0),v_)
    vo['laws'][an]=dict(cycle_s=round(tot,3),period_per_stroke_s=round(tot/NS,3),segment_s=segt,peak_v_degps=pv.round(1).tolist(),peak_a_degps2=pa.round(0).tolist(),peak_j_degps3=pj.round(0).tolist(),worst_ratio=wr,converged=conv)
   print(var,an,json.dumps({k_:v_ for k_,v_ in vo['laws'][an].items() if k_ not in ('segment_s',)}),'%.0f s'%(time.monotonic()-t00),flush=True)
  certs=cw+cr[var]['certs'];allrs=[r_ for c in certs for r_ in c['rs']];S_=RC.summarize(allrs,np.arange(len(allrs)))
  vo['certificate']=dict(ok=S_['ok'],states=len(allrs),max_step_bound_mm=max(c['max_step_bound_mm'] for c in certs),hit_states=S_['hit_states'],out_of_range_states=S_['out_of_range_states'],
   min_env_reserve_mm=S_['min_env_reserve_mm'],min_env_pair=S_['min_env_pair'],min_self_reserve_mm=S_['min_self_reserve_mm'],min_self_pair=S_['min_self_pair'],min_reserve_by_category=S_['min_reserve_by_category'],
   min_plume_mm=S_['min_plume_mm'],min_plume_geom=S_['min_plume_geom'],plume_violations=S_['plume_violations'],segments=[seg_summary(c) for c in certs])
  vo['path']=path;vo['certs']=certs
  if var=='A':vo['law_keep']=keep
  out['variants'][var]=vo
 pool.close();write_outputs(out,ch,P,q0,sign,cw,t00)
def jsonable(o):
 if isinstance(o,dict):return {str(k):jsonable(v) for k,v in o.items()}
 if isinstance(o,(list,tuple)):return [jsonable(v) for v in o]
 if isinstance(o,np.ndarray):return jsonable(o.tolist())
 if isinstance(o,(np.floating,)):return float(o)
 if isinstance(o,(np.integer,)):return int(o)
 if isinstance(o,np.bool_):return bool(o)
 return o
def bspl(sp):
 d=dict(type='bspline',k=int(sp.k),knots=sp.t.tolist(),coef=np.asarray(sp.c).tolist())
 if hasattr(sp,'sq'):d['sq']={str(j):[float(l),float(g)] for j,(l,g) in sp.sq.items()};d['sq_note']='coordinate j stored as h: q_j = limit + sign*h^2'
 return d
def write_outputs(out,ch,P,q0,sign,cw,t00):
 """cycle.json (all numbers) and the library entry lib_stir_cycle_<arm>.json (geometry, time law, stored states,
 certificate as r19enc_adopt.py)"""
 import arms
 M=model(sign);A=out['variants']['A'];Bv=out['variants']['B']
 summ=json.loads(json.dumps({k:v for k,v in out.items() if k!='variants'},default=float))
 summ['variants']={var:{k:v for k,v in vo.items() if k not in ('path','certs','law_keep')} for var,vo in out['variants'].items()}
 json.dump(summ,open(f'{OUT}/cycle.json','w'),indent=1,default=float)
 path=A['path'];geo=[];Bd=path.B
 for j,(name,(sp,a,b)) in enumerate(zip(A['segments'],path.segs)):geo.append(dict(name=name,s0=round(float(Bd[j]),9),s1=round(float(Bd[j+1]),9),local=[a,b],**bspl(sp)))
 from scipy.interpolate import CubicSpline
 tl=A['law_keep'];t,s=tl['t'],tl['s'];L=path.L;t1,t2=np.interp(L,s,t),np.interp(2*L,s,t);tg=np.arange(0,t2-t1-1e-9,t[1]-t[0]);sg=CubicSpline(t,s)(t1+tg)-L   # one period from s = 0 at t = 0, 2 ms grid
 st=[q.tolist() for c in A['certs'] for q in c['Q']];kinds=[c['name'] for c in A['certs'] for _ in c['Q']]
 gmd5=hashlib.md5(json.dumps(geo).encode()).hexdigest();smd5=hashlib.md5(json.dumps(st).encode()).hexdigest()
 cert=dict(arm=ARM,cache=f'{OUT}/cert_cache.pkl (per-state results of the certification, reused by a re-run of this stage)',checker='checker.Checker.check(full=True): MuJoCo contacts + GJK lower-bound certificate (distance.Bounds), 10 mm robot-environment, 5 mm gripper/held-environment, 0 mm self, joint ranges; R11 mesh rule for the held boxes (r19enc_check.meshheld); hit pairs re-measured with the exact convex bound (r19enc_check.one)',
  plume_rule='every robot geom except R_gripper_spatula*, R_cart*, R_dock* >= 0 mm from a cylinder of radius 0.20 m about the wok axis, rim .. 1.25 m (r15reach.py / r19stir_save.py), while the heat is on',
  spacing='consecutive checked states <= 4 mm apart by point_bound.segment_bound (r19smooth.FastBound, sub-steps <= 0.5 mm)',scene='r19stir_save.py SCENE=r17 (R17 kitchen: lid rack, spider rest at (1.52, .36), faucet), spatula held 0.45 m, jaw sense %d, cart at x %.3f'%(sign,q0[0]),
  scene_model_md5=M['cfg_md5'],geometry_md5=gmd5,states_md5=smd5,**{k:v for k,v in A['certificate'].items() if k!='segments'},segments=A['certificate']['segments'],
  works_reach=REACH,elapsed_s_this_run=round(time.monotonic()-t00),date=time.strftime('%Y-%m-%d'))
 lib=dict(id='STIR_CYCLE',arm=ARM,arm_name=arms.ARMS[ARM]['name'],variant='A: velocity-continuous (C2) periodic cycle',params=dict(stroke='h_scrape_dice (results/r15/stir_h_scrape_dice_keys.json)',strokes_per_cycle=NS,grip_m=GRIP,lift_m=LIFT,bench_period_s=P,work_fraction=WORKF),
  start_hub='H_stir0',end_hub='H_stir0',hub=dict(id='H_stir0',q=[round(float(x),9) for x in path(0.)[0]],state=[float(x) for x in full_q(q0,path(0.))[0]],note='stroke 0 start; the periodic law passes it at speed s_dot=%g; from rest the same geometry is run with a ramp (three cycles from rest to rest: %s s)'%(A['laws']['A_UR']['sdot_at_cycle_ends'][0],A['laws']['A_UR']['three_cycles_from_rest_s'])),
  pre=['spatula in hand, jaw sense %d, cart parked at x %.2f'%(sign,q0[0]),'wok keyed on the cooker','heat <= half while the spatula stops (R15 policy)','nobody within reach of the wok'],
  post=['spatula at H_stir0 (stroke 0 start)'],
  geometry=dict(dof='6 arm joints (rad); cart x, base y, base yaw, jaws constant = state_const',state_const=[float(x) for x in q0],param='s = bench time on the working parts (s <= bench speed: ds/dt <= 1), nominal time on the returns; q(s) is C2 across every hand-off and around the cycle',length=L,segments=geo),
  time_law=dict(limits=out['limits'],law='A_UR, periodic (middle of 3 unrolled cycles), one period from t = 0 (s = 0) on a 2 ms grid; repeat with t + period, s + length; q(t) = q(s(t))',period_s=float(t2-t1),t=tg.round(6).tolist(),s=sg.round(9).tolist(),**{k:v for k,v in A['laws']['A_UR'].items()}),
  time_law_A_R15=A['laws']['A_R15'],stop_variant=dict(period_per_stroke_s={k:v['period_per_stroke_s'] for k,v in Bv['laws'].items()},certificate={k:v for k,v in Bv['certificate'].items() if k!='segments'}),
  states=dict(layout='[carriage_x, base_y, base_yaw, q1..q6, finger_l, finger_r]',note='the certified states, <= 4 mm apart, in cycle order',kinds=kinds,q=st),
  verification=dict(status='verified',certificate=cert))
 ce=A['certificate'];assert ce['ok'] and ce['hit_states']==0 and ce['out_of_range_states']==0 and ce['plume_violations']==0 and ce['max_step_bound_mm']<=4.0+1e-9,'not certified: no library entry'   # as r19enc_adopt: only a clean re-check is adopted
 fn=f'results/r19/stir/lib_stir_cycle_{ARM}.json'
 if os.path.exists(fn):
  n=1
  while os.path.exists(fn[:-5]+f'.replaced_{n}.json'):n+=1
  os.rename(fn,fn[:-5]+f'.replaced_{n}.json')
 json.dump(jsonable(lib),open(fn,'w'));print('saved',f'{OUT}/cycle.json',fn,'%.0f s'%(time.monotonic()-t00))
if __name__=='__main__':
 {'works':works,'returns':returns,'cycle':cycle}[sys.argv[1]]()
