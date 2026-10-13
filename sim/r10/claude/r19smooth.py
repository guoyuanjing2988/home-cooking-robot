"""R19 smooth: retime and blend the checked R17/R18 whole-action paths, then re-check every state.

For one checked chain (results/r17/chain_*.json, `play` = stored states) this script
 1. rebuilds the chain's scene in the current R18b layout (spatula lying at (-1.15, .30), flipped;
    for the spatula chain it is in the hand) and its unchanged checker; removes the 2*pi label jumps
    that the joins leave in `play` (the same pose; the unwrapped path stays inside every joint range);
 2. reconstructs the R17 timing law (r17chain: each stored step at the slowest of object 0.10 m/s,
    45 deg/s, joints 60 deg/s, cart 0.25 m/s; dwells; +0.6 s per join) and measures it: stops,
    velocity / acceleration / jerk peaks (finite differences at the stored steps), ramp time;
 3. cuts the path at the mandatory stops (start, end, dwells, path reversals) and keeps the grasp /
    release pieces (pick -> lifted, lowered -> set down, ...) as FIXED pieces: an interpolating cubic
    through every stored state (the slow straight segment, unchanged up to < 0.1 mm), R17 speed caps;
    every other piece is FREE and gets a smoothed geometry, one of
      spline  least-squares quintic B-spline through the stored states; per state the deviation
              (point bound of the joint difference) stays within TOL = clip(RF x the state's own
              clearance reserve, TMIN, TMAX);
      blend   Douglas-Peucker via points of the stored states (same tolerance), straight joint-space
              lines between them, C2 quintic Hermite blends at the vias (the UR blend-radius idea);
 4. re-checks every state of each path, resampled so that no robot or held-object point moves more
    than 4 mm between consecutive states (point_bound.segment_bound summed over <= 0.5 mm sub-steps),
    with Checker.check(full=True): MuJoCo contacts + the GJK lower-bound certificate, 10 mm / 5 mm
    gaps, joint ranges. The stored states (joint-linear in between) are re-checked the same way as the
    baseline. A smoothed piece with hits is refitted tighter around the hits (up to 3 rounds);
 5. times each checked geometry with a jerk-limited near-time-optimal law: TOPP by reachability
    analysis on a fine grid (constraints in (s'', s'^2): joint / cart / TCP / object speed, joint /
    cart / TCP acceleration, food centre-of-mass acceleration, PGC jaw moment incl. inertial loads),
    then a moving-average filter of s'(t) (jerk = 2 a / W), then local slow-downs until every limit
    holds on a 2 ms grid. Retiming never changes the geometry, so it needs no new collision check.
python r19smooth.py ACT=wok|spatula|lever|lid|spider [WORKERS=24] [VARIANTS=spline,blend]
       [PROFILES=same,fast] [RF=.5] [TMIN=.0005] [TMAX=.008]
 -> results/r19/smooth/<act>.json (summary) and <act>_<variant>_move.json (the stored movement)"""
import sys,os,json,time,math
sys.path.insert(0,'.')
import numpy as np
OUT='results/r19/smooth'
# ---- the checked chains; dwells and fixed (grasp / release) pieces as in r17chain.py's action() ----
CHAINS=dict(
 wok=dict(file='results/r17/chain_wok_s-1_final.json',dwell={5:2.,8:5.,10:1.},fixed=[(0,1),(15,16)]),
 spatula=dict(file='results/r17/chain_spatula_s-1_r18roll-1.15_.30.json',dwell={},fixed=[(0,1)]),
 lever=dict(file='results/r17/chain_lever_s+1_final.json',dwell={},fixed=[(0,1)]),
 lid=dict(file='results/r17/chain_lid_s-1_final.json',dwell={},fixed=[(0,1),(7,8)]),
 spider=dict(file='results/r17/chain_spider_s+1_final.json',dwell={6:5.},fixed=[(0,1),(17,18)]))
R17=dict(VW=.10,WW=45.,QW=60.,CW=.25,JOIN=.6,GRASP=.8,APPROACH_M=.06)
# ---- limits. Sources: UR5e datasheet (joint speed 180 deg/s); URScript manual defaults movej a=1.4
# rad/s^2, movel a=1.2 m/s^2, v=0.25 m/s; DH PGC-140 jaw moment 7 N.m (project value, R13-R17);
# cart 0.25 m/s (r17chain CW) and 0.15 m/s^2 (mobile.py stability case, R09 drive sizing).
# ASSUMPTIONS: jerk = a / 0.1 s (no OEM value published); food CoM <= 2.0 m/s^2 (see R19_SMOOTH.md:
# quasi-static spill of 0.3 L sauce in the 34 cm wok at 0.6 g, /2 dynamic slosh amplification, /1.5);
# 'same' = the R17 caps exactly (object origin 0.10 m/s, no separate TCP cap, as r17chain);
# 'fast' TCP and object 0.25 m/s = ISO 10218-1 reduced speed = movel default; wok rotation stays 45 deg/s (R15
# pour physics), other objects 90 deg/s.
LIMITS=dict(
 same=dict(v_lin=.10,v_tcp=1e9,w_rot=45.,v_joint=60.,v_cart=.25,a_joint=1.4,a_cart=.15,a_tcp=1.2,j_joint=14.,j_cart=1.5,a_food=2.0,pgc=7.),
 fast=dict(v_lin=.25,v_tcp=.25,w_rot=90.,w_rot_wok=45.,v_joint=180.,v_cart=.25,a_joint=1.4,a_cart=.15,a_tcp=1.2,j_joint=14.,j_cart=1.5,a_food=2.0,pgc=7.),
 fastcart=dict(v_lin=.25,v_tcp=.25,w_rot=90.,w_rot_wok=45.,v_joint=180.,v_cart=.25,a_joint=1.4,a_cart=.5,a_tcp=1.2,j_joint=14.,j_cart=5.,a_food=2.0,pgc=7.))
# fastcart: cart 0.5 m/s^2 (r19smooth_cart.py: mobile.dock_stability at 0.5 m/s^2 x 1.5 with the held wok
# keeps >= 42.7 mm margin over every wok state; R09 wheel torque demand stays far below 10 N.m rated)
STEP=.004;SUB=.0005;H=.002;REV=150.   # REV: a turn above this (deg, velocity-scaled joint space) is a reversal = a stop   # check spacing (point bound), sub-step for the bound sum, time grid
DOF=[0,3,4,5,6,7,8]          # cart x + 6 arm joints (base_y, base_yaw, jaws are constant in play)
MESHHELD=os.environ.get('R19MESHHELD','1')=='1'   # 0: the stock model (held R15+ boxes as MuJoCo box primitives)
_CTX={}
def setup(act):
 """Scene + checker of the chain (R18b layout), grasp transform and held masses."""
 if act in _CTX:return _CTX[act]
 import chain,mujoco
 from scene import build
 from checker import Checker
 import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
 c=CHAINS[act];r=json.load(open(c['file']))
 if r.get('wok_tilt'):K17.set_wok_tilt(r['wok_tilt'])
 for k,v in r.get('tool_xy',{}).items():K.TOOL_XY[k]=tuple(v)
 K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV=8.;K.SPAT_YAW=0.;K.SPAT_ROLL=180.   # R18b: the spatula lies left of the sink
 BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)
 cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),'r16_tools':{'ladle':None},**K17.held_cfg(r['obj'],r['grasp_sense'])})
 tree,meta=build(cfg,None)
 if MESHHELD:   # R11 rule (DECISIONS 2026-10-10) for the held parts kitchen14+ attach after scene.build's mesh_tool pass
  import xml.etree.ElementTree as E
  from scene import fmt
  asset=tree.getroot().find('asset');tool=tree.find(".//body[@name='R_tool']")
  for g in tool.iter('geom'):
   if g.get('type')!='box':continue
   h=np.fromstring(g.get('size'),sep=' ');mn='mb19_'+g.get('name')
   E.SubElement(asset,'mesh',name=mn,vertex=' '.join(fmt([sx*h[0],sy*h[1],sz*h[2]]) for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)))
   g.set('type','mesh');g.set('mesh',mn);g.attrib.pop('size',None)
 ch=Checker(tree,meta)
 T=K.T_tool_obj(r['obj'],r['grasp_sense'])
 # held parts (mass, CoM in the object frame, disc radius for an approximate inertia; 0 = point mass), r17chain MASS
 hm=(K15.HANDLE['root']+K15.HANDLE['end'])/2-K15.WOK0
 parts=dict(wok=[(1.5,np.array([0,0,.045]),.17),(.3,hm,0.)],lever=[],spider=[(.45,np.zeros(3),0.)],spatula_b=[(.3,np.zeros(3),0.)],lid=[(.8,np.array([0,0,.025]),.15)])[r['obj']]
 ctx=dict(act=act,r=r,ch=ch,m=ch.m,d=ch.d,sid=ch.m.site('R_prep').id,T=T,parts=parts,cfg=c,meshheld=MESHHELD)
 _CTX[act]=ctx;return ctx
# ---------------------------------------------------------------- kinematics
def fk(ctx,Q):
 """TCP positions (n,3), rotations (n,3,3) of states Q (n,11)."""
 import mujoco
 m,d,sid=ctx['m'],ctx['d'],ctx['sid'];Q=np.atleast_2d(Q);P=np.zeros((len(Q),3));R=np.zeros((len(Q),3,3))
 for i,q in enumerate(Q):
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);P[i]=d.site_xpos[sid];R[i]=d.site_xmat[sid].reshape(3,3)
 return P,R
def obj_pose(ctx,P,R):
 T=ctx['T'];Ro=R@T[:3,:3];return P+R@T[:3,3],Ro
def load_parts(ctx,food):
 """Held parts plus food / water (kg at [0,0,.02], disc .12 m) -> mass, CoM (object frame), inertia about the CoM (object frame)."""
 ps=list(ctx['parts'])+([(food,np.array([0,0,.02]),.12)] if food else [])
 if not ps:return 0.,np.zeros(3),np.zeros((3,3))
 M=sum(p[0] for p in ps);c=sum(p[0]*p[1] for p in ps)/M;I=np.zeros((3,3))
 for mm,cc,rr in ps:
  Id=np.diag([mm*rr*rr/4,mm*rr*rr/4,mm*rr*rr/2]);dd=cc-c;I+=Id+mm*(dd@dd*np.eye(3)-np.outer(dd,dd))
 return M,c,I
def unwrap(Q):
 Q=np.array(Q,float)
 for i in range(len(Q)-1):
  d=Q[i+1,3:9]-Q[i,3:9];Q[i+1:,3:9]-=np.round(d/(2*np.pi))*2*np.pi
 return Q
def rotang(Ra,Rb):
 c=np.clip((np.trace(Rb@np.swapaxes(Ra,-1,-2),axis1=-2,axis2=-1)-1)/2,-1,1);return np.arccos(c)
def logrot(R):
 from scipy.spatial.transform import Rotation
 return Rotation.from_matrix(R).as_rotvec()
# ---------------------------------------------------------------- point bound (vectorized segment_bound)
class FastBound:
 """point_bound.PointBound.segment_bound, vectorized (same formula; validated against it in main)."""
 def __init__(self,ch):
  import mujoco
  pb=ch.point_bound;self.pb=pb;self.ch=ch;self.W=pb.weights;nq=ch.m.nq
  self.G=np.array([g for g,j,k,dn in pb.levers]);self.J=np.array([j for g,j,k,dn in pb.levers]);self.K=np.array([k for g,j,k,dn in pb.levers])
  self.D=np.zeros((len(pb.levers),nq))
  for i,(g,j,k,dn) in enumerate(pb.levers):
   if len(dn):self.D[i,dn]=pb.weights[g,dn]
  self.rb=ch.m.geom_rbound[self.G];self.sl=pb.slides;self.ng=ch.m.ngeom;self.W7=self.W[:,DOF]
 def __call__(self,a,b):
  import mujoco
  dq=np.abs(np.asarray(b)-np.asarray(a));ch=self.ch;ch.d.qpos[:]=a;mujoco.mj_kinematics(ch.m,ch.d)
  r=np.linalg.norm(ch.d.geom_xpos[self.G]-ch.d.xanchor[self.J],axis=1)+self.rb+self.D@dq
  v=np.zeros(self.ng);np.add.at(v,self.G,r*dq[self.K]);v+=self.W[:,self.sl]@dq[self.sl]
  return min(float(np.max(self.W@dq)),float(v.max()))
 def glob(self,dq):return float(np.max(self.W@np.abs(dq)))
 def g7(self,D):
  """Global point bound of joint differences D (n,7) or (7,) over cart + arm (valid for any motion)."""
  D=np.atleast_2d(np.abs(D));return np.max(self.W7@D.T,axis=0)
# ---------------------------------------------------------------- R17 timing law (reconstructed)
def r17_timing(ctx,Q):
 """Per stored step dt as r17chain.follow (object step / VW, rotation / WW, max joint / QW, cart / CW);
 keyframe indices matched along the path; dwells added; +JOIN s at every meet."""
 r=ctx['r'];P,R=fk(ctx,Q);po,Ro=obj_pose(ctx,P,R)
 dist=np.linalg.norm(np.diff(po,axis=0),axis=1);ang=np.degrees(rotang(Ro[:-1],Ro[1:]))
 dq=np.degrees(np.abs(np.diff(Q[:,3:9],axis=0)).max(1));dc=np.abs(np.diff(Q[:,0]))
 dt=np.maximum.reduce([dist/R17['VW'],ang/R17['WW'],dq/R17['QW'],dc/R17['CW']])
 kfs=r['keyframes'];idx=[];i0=0
 for k in kfs:   # first local minimum within 8 mm (the keyframe p is rounded to 1 mm; IK pose error <= 5 mm)
  p=np.array(k['p']);dd=np.linalg.norm(po[i0:]-p,axis=1);ok=np.where(dd<.008)[0]
  if not len(ok):idx.append(None);continue
  j=ok[0]
  while j+1<len(dd) and dd[j+1]<dd[j]:j+=1
  idx.append(i0+j);i0=i0+j
 idx[0]=0;idx[-1]=len(Q)-1   # the play starts at the first keyframe and ends at the last
 dwell=np.zeros(len(Q))
 for k,s in ctx['cfg']['dwell'].items():dwell[idx[k]]+=s
 meets=[idx[i] for i,k in enumerate(kfs) if k['meet'] and idx[i] is not None and 0<i<len(kfs)-1]
 joins=len(r['joins'])
 return dict(dt=dt,dwell=dwell,kf_idx=idx,meet_idx=meets,joins=joins,po=po,Ro=Ro,P=P,R=R)
def fd_peaks(Q,dt,stops=()):
 """Velocity per stored step (constant over the step), acceleration / jerk by differences at the step
 boundaries; the R17 law has no acceleration limit, so these are sampling-dependent values."""
 v=np.diff(Q[:,DOF],axis=0)/np.maximum(dt,1e-9)[:,None];tm=np.cumsum(dt)-dt/2
 v=np.vstack([0*v[:1],v,0*v[:1]]);tm=np.r_[tm[0]-dt[0],tm,tm[-1]+dt[-1]]   # at rest before and after
 a=np.diff(v,axis=0)/np.maximum(np.diff(tm),1e-9)[:,None];ta=(tm[1:]+tm[:-1])/2
 j=np.diff(a,axis=0)/np.maximum(np.diff(ta),1e-9)[:,None]
 cv=lambda x:[round(float(np.abs(x[:,0]).max()),3)]+np.degrees(np.abs(x[:,1:]).max(0)).round(1).tolist()
 return dict(v=cv(v),a=cv(a),j=cv(j))
def turns(Y):
 """Turn angle (deg) at each interior state of polyline Y (zero steps skipped)."""
 D=np.diff(Y,axis=0);n=np.linalg.norm(D,axis=1);out=np.zeros(len(Y));last=None
 for i in range(len(D)):
  if n[i]<1e-12:continue
  u=D[i]/n[i]
  if last is not None:out[i]=np.degrees(np.arccos(np.clip(u@last,-1,1)))
  last=u
 return out
def stopgo_time(Q,dt_cap=None):
 """Every stored state as an unblended UR movej: rest-to-rest trapezoid per step, leading joint at
 60 deg/s / 1.4 rad/s^2 (URScript defaults scaled to the R17 joint cap), cart 0.25 m/s / 0.15 m/s^2."""
 tot=0.
 for a,b in zip(Q[:-1],Q[1:]):
  t=0.
  for d,v,acc in ((np.abs(b[3:9]-a[3:9]).max(),np.radians(60),1.4),(abs(b[0]-a[0]),.25,.15)):
   t=max(t,2*math.sqrt(d/acc) if d<v*v/acc else d/v+v/acc)
  tot+=t
 return tot
# ---------------------------------------------------------------- geometry: paths
class Path:
 """q(s) = f(s)/w for a piecewise polynomial f in the scaled joint space (cart m, joints rad x lever).
 sq = {dof: (limit, sign)}: that coordinate is stored as h with q = limit + sign*h^2, so a path whose
 stored states sit on a joint-range limit (the cart at its -1.48 m travel end) can never cross it."""
 def __init__(self,f,w,q0full,kind,meta=None,sq=None):
  self.f=f;self.w=w;self.q0=np.array(q0full,float);self.kind=kind;self.meta=meta or {};self.sq=sq or {}
  a,b=(f.t[f.k],f.t[-f.k-1]) if hasattr(f,'t') else (f.x[0],f.x[-1]);self.s0=float(a);self.L=float(b-a);self.d=[f.derivative(n) for n in (1,2,3)]
 def q(self,s,nu=0):
  s=np.asarray(s,float)+self.s0
  ys=[np.atleast_2d(self.f(s))/self.w]+([np.atleast_2d(self.d[k](s))/self.w for k in range(nu)] if self.sq else [])
  y=ys[-1] if self.sq else (ys[0] if nu==0 else np.atleast_2d(self.d[nu-1](s))/self.w)
  if self.sq:
   y=y.copy()
   for dd,(lim,sg) in self.sq.items():
    h=[v[:,dd] for v in ys]
    y[:,dd]=lim+sg*h[0]**2 if nu==0 else sg*(2*h[0]*h[1] if nu==1 else 2*(h[1]**2+h[0]*h[2]) if nu==2 else 2*(3*h[1]*h[2]+h[0]*h[3]))
  if nu==0:
   Q=np.tile(self.q0,(len(y),1));Q[:,DOF]=y;return Q
  return y
def to_sq(Y,w,sq):
 """Stored scaled coordinates -> fitting coordinates (h*w for the sq coordinates)."""
 Y=Y.copy()
 for dd,(lim,sg) in sq.items():Y[:,dd]=np.sqrt(np.maximum(sg*(Y[:,dd]/w[dd]-lim),0.))*w[dd]
 return Y
def chord(Y):
 u=np.r_[0,np.cumsum(np.linalg.norm(np.diff(Y,axis=0),axis=1))];return u
def dedup(Y,idx):
 keep=[0]
 for i in range(1,len(Y)):
  if np.linalg.norm(Y[i]-Y[keep[-1]])>1e-9:keep.append(i)
 if keep[-1]!=len(Y)-1:keep[-1]=len(Y)-1
 return Y[keep],[idx[i] for i in keep]
def fit_fixed(Y,w,q0,sq=None):
 """Interpolating cubic through every stored state (polyline densified to >= 6 states)."""
 from scipy.interpolate import make_interp_spline
 sq=sq or {}
 while len(Y)<6:Y=_mid(Y)
 u=chord(Y);return Path(make_interp_spline(u,to_sq(Y,w,sq),k=3),w,q0,'fixed',sq=sq)
def _mid(Y):
 out=[Y[0]]
 for a,b in zip(Y[:-1],Y[1:]):out+=[(a+b)/2,b]
 return np.array(out)
def fit_spline(Y,w,q0,tol,fb,lam0=1e-3,sq=None):
 """Weighted cubic smoothing spline (knot at every stored state, C2) through Y, the same smoothing
 weight lam for all 7 coordinates; states whose deviation (global point bound) exceeds their tolerance
 get 4x the weight until all are within; lam / 10 if 15 rounds are not enough."""
 from scipy.interpolate import make_smoothing_spline,BSpline
 sq=sq or {};u=chord(Y);n=len(Y);Yt=to_sq(Y,w,sq)
 if n<6 or u[-1]<.02:return fit_fixed(Y,w,q0,sq),np.zeros(n)
 Winv=1/w;lam=lam0
 for _ in range(4):
  wt=np.ones(n);wt[[0,-1]]=1e4
  for it in range(15):
   cs=[make_smoothing_spline(u,Yt[:,d],w=wt,lam=lam) for d in range(Y.shape[1])]
   sp=BSpline(cs[0].t,np.stack([c_.c for c_ in cs],axis=1),3)
   e0=Yt[0]-sp(0.);e1=Yt[-1]-sp(u[-1]);g=_greville(sp.t,3);lm=(g/u[-1])[:,None];sp=BSpline(sp.t,sp.c+(1-lm)*e0+lm*e1,3)   # exact ends
   p=Path(sp,w,q0,'spline',dict(lam=lam,n_coef=int(sp.c.shape[0]),max_weight=float(wt.max())),sq=sq)
   dev=fb.g7(p.q(u)[:,DOF]-Y*Winv);bad=dev>tol
   if not bad.any():return p,dev
   wt[bad]*=4
  lam/=10
 p=fit_fixed(Y,w,q0,sq);p.kind='spline-interp';return p,np.zeros(n)
def _greville(t,k):
 return np.array([t[i+1:i+k+1].mean() for i in range(len(t)-k-1)])
def dp_simplify(Y,tol,fb,w):
 """Douglas-Peucker on the polyline: a state may be dropped if its point-bound distance to the chord
 (at the same chord-length fraction) is <= its tolerance."""
 u=chord(Y);keep=[0,len(Y)-1];stack=[(0,len(Y)-1)];Winv=1/w
 while stack:
  a,b=stack.pop()
  if b-a<2:continue
  lam=((u[a+1:b]-u[a])/max(u[b]-u[a],1e-12))[:,None];C=Y[a]+(Y[b]-Y[a])*lam
  dev=fb.g7((Y[a+1:b]-C)*Winv)-tol[a+1:b]
  j=int(np.argmax(dev))
  if dev[j]>0:m_=a+1+j;keep.append(m_);stack+=[(a,m_),(m_,b)]
 return sorted(keep)
def hermite5(P0,P1,V0,V1,L):
 """Quintic Hermite (zero 2nd derivative at both ends) as coefficients in (s-s0), highest power first."""
 c=[P0,V0,np.zeros_like(P0),-10*P0-6*V0-4*V1+10*P1,15*P0+8*V0+7*V1-15*P1,-6*P0-3*V0-3*V1+6*P1]
 return np.array([c[n]/L**n for n in range(5,-1,-1)])
def fit_blend(Y,w,q0,tol,fb,rmax=.10):
 """Via points (DP) + straight lines + C2 quintic blends; blend size halved until its middle is
 within the via's tolerance of the via."""
 from scipy.interpolate import PPoly
 v=dp_simplify(Y,tol,fb,w);V=Y[v];Winv=1/w;br=[];pieces=[]
 if len(V)==2:
  d=V[1]-V[0];L=np.linalg.norm(d);c=np.zeros((6,1,len(d)));c[4,0]=d/L;c[5,0]=V[0]
  return Path(PPoly(c,[0,L]),w,q0,'blend',dict(vias=v,radii=[])),v
 starts=[V[0]];P=[]
 for k in range(1,len(V)-1):
  a,b=V[k]-V[k-1],V[k+1]-V[k];la,lb=np.linalg.norm(a),np.linalg.norm(b);di,do=a/la,b/lb
  r=min(rmax,.45*la,.45*lb)
  while True:
   B0,B1=V[k]-r*di,V[k]+r*do;L=max(np.linalg.norm(B1-B0),1e-6);cc=hermite5(B0,B1,L*di,L*do,L)
   mid=sum(cc[n]*(L/2)**(5-n) for n in range(6))
   if fb.g7((mid-V[k])*Winv)[0]<=tol[v[k]] or r<1e-4:break
   r/=2
  P.append((B0,B1,cc,L));br.append(r)
 x=[0.];C=[];cur=V[0]
 for (B0,B1,cc,L) in P:
  d=B0-cur;l=np.linalg.norm(d)
  if l>1e-9:cl=np.zeros((6,len(d)));cl[4]=d/l;cl[5]=cur;C.append(cl);x.append(x[-1]+l)
  C.append(cc);x.append(x[-1]+L);cur=B1
 d=V[-1]-cur;l=np.linalg.norm(d)
 if l>1e-9:cl=np.zeros((6,len(d)));cl[4]=d/l;cl[5]=cur;C.append(cl);x.append(x[-1]+l)
 pp=PPoly(np.stack(C,axis=1),np.array(x))
 return Path(pp,w,q0,'blend',dict(vias=v,radii=br,n_vias=len(v))),v
# ---------------------------------------------------------------- re-check at <= 4 mm
def sample_path(path,fb):
 """States along path with a point bound <= STEP between consecutive ones (sum of segment bounds over
 sub-steps <= SUB); returns states, s values, max spacing bound."""
 n=max(2,int(math.ceil(path.L/(SUB/3)))+1);s=np.linspace(0,path.L,n);Q=path.q(s)
 b=np.array([fb(Q[i],Q[i+1]) for i in range(n-1)])
 while b.max()>SUB*1.0001:   # refine where a sub-step is too long
  n=int(n*b.max()/SUB*1.1)+2;s=np.linspace(0,path.L,n);Q=path.q(s);b=np.array([fb(Q[i],Q[i+1]) for i in range(n-1)])
 out=[0];acc=0.;sp=[]
 for i in range(n-1):
  if acc+b[i]>STEP:out.append(i);sp.append(acc);acc=0.
  acc+=b[i]
 out.append(n-1);sp.append(acc)
 return Q[out],s[out],max(sp)
def sample_poly(Q,fb):
 """The stored states with joint-linear interpolation, subdivided as planner.edge (<= STEP each)."""
 out=[Q[0]];src=[0];sp=[]
 for i in range(len(Q)-1):
  b=fb(Q[i],Q[i+1]);n=max(1,int(math.ceil(b/STEP)))
  for k in range(1,n+1):out.append(Q[i]+(Q[i+1]-Q[i])*k/n);src.append(i+k/n)
  sp.append(b/n)
 return np.array(out),np.array(src),max(sp)
def _worker_init(act):
 setup(act)
def _worker(args):
 act,Qs=args;ctx=setup(act);ch=ctx['ch'];res=[]
 for q in Qs:
  c=ch.check(np.asarray(q),full=True,mass=0.)
  rv={k:round(v['reserve_mm'],2) for k,v in c['clearance'].items()}
  res.append(dict(hits=[h['pair'] for h in c['hits']][:2],gjk_hit=any(h.get('reason') for h in c['hits']),ranges=bool(c['ranges']),res=min([v for k,v in rv.items() if k!='self'],default=1e9),self_mm=rv.get('self',1e9)))
 return res
def check_all(pool,act,Q,chunk=40):
 jobs=[(act,Q[i:i+chunk].tolist()) for i in range(0,len(Q),chunk)];out=[]
 for r in pool.map(_worker,jobs):out+=r
 return out
def summarize_check(rs):
 hits=[i for i,r in enumerate(rs) if r['hits'] or not r['ranges']]
 return dict(states=len(rs),hit_states=len(hits),gjk_hit_states=sum(1 for r in rs if r.get('gjk_hit')),out_of_range_states=sum(1 for r in rs if not r['ranges']),first_hits=[(i,rs[i]['hits']) for i in hits[:4]],ranges_ok=all(r['ranges'] for r in rs),
  min_reserve_mm=round(min(r['res'] for r in rs),2),min_self_mm=round(min(r['self_mm'] for r in rs),2))
# ---------------------------------------------------------------- time law
class Seg:
 """Kinematic data of one path piece on the TOPP grid."""
 def __init__(self,ctx,path,food,lim,fixed,ds=.003):
  N=max(8,int(math.ceil(path.L/ds)));s=np.linspace(0,path.L,N+1)
  if not hasattr(path.f,'t'):   # piecewise path: grid points at every break and 8 inside each short piece (small blends)
   br=np.asarray(path.f.x,float)-path.s0;ex=[br]+[np.linspace(a_,b_,8) for a_,b_ in zip(br[:-1],br[1:]) if b_-a_<4*path.L/N]
   s=np.unique(np.clip(np.concatenate([s]+ex),0,path.L));s=s[np.r_[True,np.diff(s)>1e-7]];s[-1]=path.L
  self.path=path;self.s=s;self.N=len(s)-1;self.dsv=np.diff(s);self.ds=float(path.L/N)
  self.qp=path.q(s,1);self.qpp=path.q(s,2);Q=path.q(s);P,R=fk(ctx,Q);po,Ro=obj_pose(ctx,P,R)
  M,c,Ib=load_parts(ctx,food);self.M=M;C=po+np.einsum('nij,j->ni',Ro,c)
  g=lambda X:np.gradient(X,s,axis=0,edge_order=2)
  self.pp,self.ppp=g(P),g(g(P));self.op=g(po);self.cp,self.cpp=g(C),g(g(C))
  rv=logrot(R[1:]@np.transpose(R[:-1],(0,2,1)))/self.dsv[:,None]   # omega' at the midpoints (world frame)
  wp=np.vstack([rv[0],(rv[1:]+rv[:-1])/2,rv[-1]]);self.wp=wp;self.wpp=g(wp)
  self.food=food;self.fixed=fixed;self.lim=self.limits(lim,ctx,fixed)
  # PGC moment about the TCP: M = A u + B x + C (u = s'', x = s'^2)
  r=C-P;Iw=np.einsum('nij,jk,nlk->nil',Ro,Ib,Ro)
  self.A=M*np.cross(r,self.cp)+np.einsum('nij,nj->ni',Iw,wp)
  self.B=M*np.cross(r,self.cpp)+np.einsum('nij,nj->ni',Iw,self.wpp)+np.cross(wp,np.einsum('nij,nj->ni',Iw,wp))
  self.C=M*np.cross(r,np.array([0,0,9.81]))
  self.kappa=np.ones(self.N+1)
 def limits(self,lim,ctx,fixed):
  L=dict(LIMITS['same']) if fixed else dict(lim)
  if ctx['r']['obj']=='wok' and 'w_rot_wok' in L:L['w_rot']=L['w_rot_wok']
  return L
 def tables(self):
  """Per grid point: velocity cap xv, linear constraints (a,b,L), norm constraints (A,B,C,L)."""
  L=self.lim;k=self.kappa;N=self.N
  vj=np.r_[L['v_cart'],np.full(6,np.radians(L['v_joint']))];aj=np.r_[L['a_cart'],np.full(6,L['a_joint'])]
  with np.errstate(divide='ignore'):
   xv=np.min(np.c_[(vj/np.maximum(np.abs(self.qp),1e-12))**2,(L['v_tcp']/np.maximum(np.linalg.norm(self.pp,axis=1),1e-12))**2,
    (L['v_lin']/np.maximum(np.linalg.norm(self.op,axis=1),1e-12))**2,(np.radians(L['w_rot'])/np.maximum(np.linalg.norm(self.wp,axis=1),1e-12))**2],axis=1)*k
  lin=[[(float(self.qp[i,j]),float(self.qpp[i,j]),float(aj[j]*k[i])) for j in range(7)] for i in range(N+1)]
  nrm=[]
  for i in range(N+1):
   c=[(self.pp[i],self.ppp[i],np.zeros(3),L['a_tcp']*k[i])]
   if self.food:c.append((self.cp[i],self.cpp[i],np.zeros(3),L['a_food']*k[i]))
   if self.M>0:
    cs=float(np.linalg.norm(self.C[i]));c.append((self.A[i],self.B[i],self.C[i],max(cs+k[i]*(L['pgc']-cs),cs*1.001+1e-6)))
   nrm.append([tuple(map(float,(*a,*b,*cc,l))) for a,b,cc,l in c])
  return xv,lin,nrm
def uint(lin,nrm,x):
 lo,hi=-1e18,1e18
 for a,b,L in lin:
  bx=b*x
  if abs(a)<1e-12:
   if abs(bx)>L:return 1.,-1.
   continue
  u1=(-L-bx)/a;u2=(L-bx)/a
  if u1>u2:u1,u2=u2,u1
  if u1>lo:lo=u1
  if u2<hi:hi=u2
 for A0,A1,A2,B0,B1,B2,C0,C1,C2,L in nrm:
  w0=B0*x+C0;w1=B1*x+C1;w2=B2*x+C2;aa=A0*A0+A1*A1+A2*A2;ab=A0*w0+A1*w1+A2*w2;ww=w0*w0+w1*w1+w2*w2
  if aa<1e-14:
   if ww>L*L:return 1.,-1.
   continue
  disc=ab*ab-aa*(ww-L*L)
  if disc<0:return 1.,-1.
  sq=math.sqrt(disc);u1=(-ab-sq)/aa;u2=(-ab+sq)/aa
  if u1>lo:lo=u1
  if u2<hi:hi=u2
 return lo,hi
def topp(seg):
 """Time-optimal x = s'^2 on the grid (rest to rest): MVC by bisection, backward controllable sets,
 greedy forward pass (TOPP-RA)."""
 xv,lin,nrm=seg.tables();N=seg.N;DD=2*seg.dsv
 def feas(i,x,kn=None):
  lo,hi=uint(lin[i],nrm[i],x)
  if kn is not None:D=DD[i];lo=max(lo,-x/D);hi=min(hi,(kn-x)/D)
  return lo<=hi+1e-12
 def bis(i,xmax,kn=None):
  if feas(i,xmax,kn):return xmax
  a,b=0.,xmax
  for _ in range(40):
   m_=(a+b)/2
   if feas(i,m_,kn):a=m_
   else:b=m_
  return a
 xm=np.array([bis(i,min(xv[i],1e6)) for i in range(N+1)]);K=np.zeros(N+1);K[N]=0.
 for i in range(N-1,-1,-1):K[i]=bis(i,xm[i],K[i+1])
 x=np.zeros(N+1);u=np.zeros(N)
 for i in range(N):
  D=DD[i];lo,hi=uint(lin[i],nrm[i],x[i]);hi=min(hi,(K[i+1]-x[i])/D);lo=max(lo,-x[i]/D)
  u[i]=hi if hi>=lo else lo;x[i+1]=min(max(x[i]+D*u[i],0.),K[i+1])
  if i+1<N:x[i+1]=max(x[i+1],min(1e-6,K[i+1]))   # numerical trap guard (speed >= 1e-3); limits are verified on the time grid
  u[i]=(x[i+1]-x[i])/D
 return x,u
def timelaw(seg,x,W):
 """s(t) on the H grid from the TOPP profile: x(s) is first eroded in path space (min over the stretch
 covered in W, so that the filtered speed stays under the TOPP speed at every s), then s'(t) is
 filtered by a moving average over W (path jerk <= 2 s''max / W) and a short one (0.04 s) that rounds
 the jerk corners. The filters keep the area of s'(t), i.e. the path length."""
 N=seg.N;sg_=seg.s;v=np.sqrt(np.maximum(x,0));xe=x.copy();r_=v*(W/2+.02)   # half the box width (+ half the 0.04 s box) each side
 lo_=np.searchsorted(sg_,sg_-r_);hi_=np.searchsorted(sg_,sg_+r_,side='right')
 for i in range(N+1):
  if hi_[i]-lo_[i]>1:xe[lo_[i]:hi_[i]]=np.minimum(xe[lo_[i]:hi_[i]],x[i])
 v=np.sqrt(np.maximum(xe,0));vv=v[1:]+v[:-1];dt=np.where(vv>1e-12,2*seg.dsv/np.maximum(vv,1e-12),0.)
 bad=vv<=1e-12
 if bad.any():   # two zero-speed grid points in a row (erosion at the ends): constant accel from rest
  dt[bad]=2*np.sqrt(seg.dsv[bad]/1e-3)
 t=np.r_[0,np.cumsum(dt)]
 if t[-1]>3600:raise RuntimeError(f'time law diverged: {t[-1]:.3g} s')
 tg=np.arange(0,t[-1]+H,H);sd=np.interp(tg,t,v)
 for w_ in (W,.04):
  k=max(1,int(round(w_/H)));sd=np.convolve(sd,np.ones(k)/k,mode='full')   # zero padded: area (path length) kept
 s=np.r_[0,np.cumsum((sd[1:]+sd[:-1])/2*H)];sd*=seg.path.L/s[-1];s*=seg.path.L/s[-1]
 return np.arange(len(s))*H,s,sd
def verify(ctx,seg,s):
 """All limits on the H grid of s(t): ratio value/limit per sample and per constraint family."""
 L=seg.lim;Q=seg.path.q(np.clip(s,0,seg.path.L));q=Q[:,DOF];P,R=fk(ctx,Q);po,Ro=obj_pose(ctx,P,R)
 M,c,Ib=load_parts(ctx,seg.food);C=po+np.einsum('nij,j->ni',Ro,c)
 d1=lambda X:np.gradient(X,H,axis=0);v=d1(q);a=d1(v);j=d1(a)
 wm=logrot(R[1:]@np.transpose(R[:-1],(0,2,1)))/H;wv=np.vstack([wm[:1],(wm[1:]+wm[:-1])/2,wm[-1:]])
 vj=np.r_[L['v_cart'],np.full(6,np.radians(L['v_joint']))];aj=np.r_[L['a_cart'],np.full(6,L['a_joint'])];jj=np.r_[L['j_cart'],np.full(6,L['j_joint'])]
 rat=dict(v_joint=np.max(np.abs(v)/vj,axis=1),a_joint=np.max(np.abs(a)/aj,axis=1),j_joint=np.max(np.abs(j)/jj,axis=1),
  v_tcp=np.linalg.norm(d1(P),axis=1)/L['v_tcp'],v_obj=np.linalg.norm(d1(po),axis=1)/L['v_lin'],w=np.linalg.norm(wv,axis=1)/np.radians(L['w_rot']),
  a_tcp=np.linalg.norm(d1(d1(P)),axis=1)/L['a_tcp'])
 ac=d1(d1(C));mom=np.zeros(len(s))
 if seg.food:rat['a_food']=np.linalg.norm(ac,axis=1)/L['a_food']
 if M>0:
  r=C-P;Iw=np.einsum('nij,jk,nlk->nil',Ro,Ib,Ro);al=d1(wv)
  Mv=M*np.cross(r,ac+[0,0,9.81])+np.einsum('nij,nj->ni',Iw,al)+np.cross(wv,np.einsum('nij,nj->ni',Iw,wv));mom=np.linalg.norm(Mv,axis=1)
  rat['pgc']=mom/L['pgc']
 peaks=dict(v=[round(float(np.abs(v[:,0]).max()),3)]+np.degrees(np.abs(v[:,1:]).max(0)).round(1).tolist(),
  a=[round(float(np.abs(a[:,0]).max()),3)]+np.degrees(np.abs(a[:,1:]).max(0)).round(1).tolist(),
  j=[round(float(np.abs(j[:,0]).max()),3)]+np.degrees(np.abs(j[:,1:]).max(0)).round(1).tolist(),
  v_tcp=round(float(np.linalg.norm(d1(P),axis=1).max()),3),a_tcp=round(float(np.linalg.norm(d1(d1(P)),axis=1).max()),3),
  j_tcp=round(float(np.linalg.norm(d1(d1(d1(P))),axis=1).max()),2),a_com=round(float(np.linalg.norm(ac,axis=1).max()),3),
  pgc_Nm=round(float(mom.max()),3),pgc_static_Nm=round(float(np.linalg.norm(seg.C,axis=1).max()),3) if M>0 else None)
 return rat,peaks
EXP=dict(v_joint=2.,v_tcp=2.,v_obj=2.,w=2.,a_joint=1.,a_tcp=1.,a_food=1.,pgc=1.,j_joint=2/3)   # kappa (scales s'^2) needed per ratio: v ~ f, a ~ f^2, jerk ~ f^3
def verify2(ctx,seg,t,s):
 """verify() for a law given on another time grid: resampled to H."""
 tg=np.arange(0,t[-1]+H/2,H);return verify(ctx,seg,np.interp(tg,t,s))
def time_segment(ctx,seg,W=.2,iters=20):
 """TOPP + erosion + jerk filter; where a limit is still exceeded on the 2 ms grid, kappa (a factor on
 the speed^2 cap and on the acceleration limits) is lowered around that point; repeat."""
 xv0=seg.tables()[0]   # speed^2 caps from the velocity limits alone (for the stop/start time)
 for it in range(iters):
  try:x,u=topp(seg);t,s,sd=timelaw(seg,x,W)
  except RuntimeError:
   if it==0:raise
   break   # keep the previous law (stretched below)
  rat,pk=verify(ctx,seg,s)
  worst={k:float(v.max()) for k,v in rat.items()};mx=max(worst.values())
  if mx<=1.0+1e-3:break
  need=np.ones(len(s))
  for k_,v_ in rat.items():need=np.minimum(need,np.where(v_>1.,(.98/np.maximum(v_,1e-9))**EXP[k_],1.))
  kap=seg.kappa.copy();idx=np.nonzero(need<1.)[0]
  for s_,n_,sd_ in zip(s[idx],need[idx],sd[idx]):
   sel=np.abs(seg.s-s_)<=sd_*W+2*seg.ds;kap[sel]=np.minimum(kap[sel],seg.kappa[sel]*n_)
  seg.kappa=np.maximum(kap,1e-3)
  if os.environ.get('R19DBG'):print('   it',it,'T %.2f'%t[-1],{k:round(v,2) for k,v in worst.items() if v>1},'kappa min %.3g'%seg.kappa.min(),flush=True)
 if mx>1.0+1e-3:   # not converged: stretch the last law uniformly (v/f, a/f^2, jerk/f^3)
  f=max([1.]+[(v_/.999)**(EXP[k_]/2) for k_,v_ in worst.items() if v_>1]);t0_=t.copy()
  for _ in range(6):
   rat,pk=verify2(ctx,seg,t0_*f,s);w2={k:float(v.max()) for k,v in rat.items()}
   if max(w2.values())<=1.0+1e-3:break
   f*=max(w2.values())**.5
  t=t0_*f;sd=sd/f;worst=dict(w2,stretch=round(f,3))
 ramp=_ramp(t,sd,np.sqrt(np.interp(s,seg.s,np.minimum(xv0,1e6))))
 return dict(time_s=float(t[-1]),topp_s=float(np.sum(2*seg.dsv/np.maximum(np.sqrt(x[1:])+np.sqrt(x[:-1]),1e-12))),iters=it+1,worst={k:round(v,3) for k,v in worst.items()},peaks=pk,ramp_s=ramp,t=t,s=s,sd=sd)
def _ramp(t,sd,vcap):
 """Stop/start time: from rest until s' first reaches 90 % of the local cruise cap (the speed the
 velocity limits alone allow there), plus from the last such instant to rest; the whole piece if never."""
 i=np.nonzero(sd>=.9*vcap)[0]
 if not len(i):return float(t[-1])
 return float(t[i[0]]+t[-1]-t[i[-1]])
def scurve(dlen,v,a,j):
 """Rest-to-rest time of a straight move (jerk-limited trapezoid, symmetric)."""
 # accelerate to v with jerk j: ta=v/a+a/j (if v>=a*a/j); distance v*ta; else triangular
 if v>=a*a/j:ta=v/a+a/j
 else:ta=2*math.sqrt(v/j)
 if v*ta<=dlen:return dlen/v+ta
 lo,hi=0.,v
 for _ in range(60):
  vm=(lo+hi)/2;tm=vm/a+a/j if vm>=a*a/j else 2*math.sqrt(vm/j)
  if vm*tm<=dlen:lo=vm
  else:hi=vm
 vm=lo;return 2*(vm/a+a/j if vm>=a*a/j else 2*math.sqrt(vm/j))
# ---------------------------------------------------------------- main
def main():
 import multiprocessing as mp
 KV=dict(a.split('=',1) for a in sys.argv[1:]);act=KV['ACT'];WK=int(KV.get('WORKERS',24))
 VAR=KV.get('VARIANTS','spline,blend').split(',');PRO=KV.get('PROFILES','same,fast,fastcart').split(',')
 RF,TMIN,TMAX=float(KV.get('RF',.5)),float(KV.get('TMIN',.0005)),float(KV.get('TMAX',.008))
 os.makedirs(OUT,exist_ok=True);t00=time.monotonic()
 ctx=setup(act);r=ctx['r'];ch=ctx['ch'];fb=FastBound(ch);m=ctx['m']
 Q=unwrap(r['play']);lo,hi=m.jnt_range[:,0],m.jnt_range[:,1]
 rng=np.random.default_rng(1);val=max(abs(fb(Q[i],Q[i+1])-ch.point_bound.segment_bound(Q[i],Q[i+1])) for i in rng.integers(0,len(Q)-1,12))
 w=np.r_[1.,ch.point_bound.weights.max(0)[3:9]]   # scaled joint space: cart m, joint rad x its largest lever (m)
 lo7,hi7=lo[DOF],hi[DOF];lo7[0],hi7[0]=max(lo7[0],-1.48),min(hi7[0],1.46)   # cart travel as r17chain.solve_free
 SQ={d:((lo7[d],1.) if Q[:,DOF[d]].min()-lo7[d]<1e-3 else (hi7[d],-1.)) for d in range(7) if min(Q[:,DOF[d]].min()-lo7[d],hi7[d]-Q[:,DOF[d]].max())<1e-3}
 Y=Q[:,DOF]*w
 # ---- 1/2: the R17 timing law
 tl=r17_timing(ctx,Q);dt=tl['dt'];kf=tl['kf_idx'];tu=turns(Q[:,DOF]/np.r_[R17['CW'],np.full(6,np.radians(R17['QW']))])
 motion=float(dt.sum());dw=float(tl['dwell'].sum());joins=tl['joins']*R17['JOIN'];apps=[a['time_s'] for a in r['approaches']]
 before=dict(r17_time_s=r['time_s'],recon_time_s=round(motion+dw+joins+2*R17['GRASP']+sum(apps),1),
  motion_s=round(motion,2),dwell_s=dw,join_allowance_s=joins,stored_states=len(Q),label_jumps_2pi=int(np.sum(np.abs(np.round(np.diff(np.array(r['play'])[:,3:9],axis=0)/(2*np.pi)))>0)),
  unwrapped_in_range=bool(np.all(Q>=lo-1e-9) and np.all(Q<=hi+1e-9)),
  stops=dict(dwells=len(ctx['cfg']['dwell']),joins_stop_and_go=tl['joins'],reversals_gt150=int(np.sum(tu>REV)),corners_90_150=int(np.sum((tu>90)&(tu<=REV))),corners_30_90=int(np.sum((tu>30)&(tu<=90))),turn_le5=int(np.sum((tu>0)&(tu<=5)))),
  corner_states=[(int(i),round(float(tu[i]))) for i in np.nonzero(tu>30)[0]],kf_idx=kf,
  fd_peaks=fd_peaks(Q,dt),stopgo_every_state_s=round(stopgo_time(Q)+dw+2*R17['GRASP']+sum(apps),1),
  stop_start_fraction=round(joins/(motion+joins),3),step_bound_mm=dict(max=round(max(fb(Q[i],Q[i+1]) for i in range(len(Q)-1))*1e3,1)),fastbound_check_m=val)
 print(act,'before',json.dumps({k:v for k,v in before.items() if k not in ('kf_idx',)}),flush=True)
 # ---- segmentation
 must=set([0,len(Q)-1]+[kf[k] for k in ctx['cfg']['dwell']]+[kf[a] for a,b in ctx['cfg']['fixed']]+[kf[b] for a,b in ctx['cfg']['fixed']])
 rev=[int(i) for i in np.nonzero(tu>REV)[0] if min(abs(int(i)-j) for j in must)>2]   # path reversals (cusps) not already a stop
 stops=sorted(must|set(rev))
 fixed=set((kf[a],kf[b]) for a,b in ctx['cfg']['fixed'])
 segs=[(a,b,(a,b) in fixed) for a,b in zip(stops[:-1],stops[1:]) if b>a]
 # load per segment (wok: food until the plate tip, water from the tap to the emptying)
 def food_of(a,b):
  if r['obj']!='wok':return 0.
  if b<=kf[5]:return 1.15
  if a>=kf[8] and b<=kf[10]:return .5
  return 0.
 # ---- baseline re-check (stored states, joint-linear, <= 4 mm)
 pool=mp.Pool(WK,initializer=_worker_init,initargs=(act,))
 bfile=f'{OUT}/{act}_baseline'+('' if MESHHELD else '_stock')+'.json';key=float(np.sum(Q))
 if os.path.exists(bfile) and abs(json.load(open(bfile))['key']-key)<1e-9:   # cached baseline re-check of the same stored states
  bc=json.load(open(bfile));rb,src,base=bc['rb'],np.array(bc['src']),bc['base']
 else:
  QB,src,spB=sample_poly(Q,fb);rb=check_all(pool,act,QB);base=summarize_check(rb);base['max_spacing_mm']=round(spB*1e3,3)
  json.dump(dict(key=key,rb=rb,src=src.tolist(),base=base),open(bfile,'w'))
 # reserve near every stored state (min over the sub-states of its two steps)
 resv=np.full(len(Q),1e9)
 for rr,sv in zip(rb,src):
  for i in {int(math.floor(sv)),int(math.ceil(sv))}:
   if 0<=i<len(Q):resv[i]=min(resv[i],rr['res'],rr['self_mm'])
 print(act,'baseline',json.dumps(base),'%.0fs'%(time.monotonic()-t00),flush=True)
 r17seg=[round(float(dt[a:b].sum()+tl['dwell'][a+1:b].sum()+R17['JOIN']*sum(1 for mi in tl['meet_idx'] if a<mi<b)),2) for a,b,f in segs]
 prev=json.load(open(f'{OUT}/{act}.json')) if os.path.exists(f'{OUT}/{act}.json') else {}
 out=dict(act=act,file=CHAINS[act]['file'],meshheld=MESHHELD,sq={str(k):v for k,v in SQ.items()},before=before,baseline_check=base,segments=[dict(a=a,b=b,fixed=f,food=food_of(a,b),r17_s=r_) for (a,b,f),r_ in zip(segs,r17seg)],
  limits=LIMITS,R17=R17,variants={},notes=[])
 # ---- variants
 for var in VAR:
  tolscale=np.ones(len(Q));rounds=[]
  for rnd in range(4):
   tol=np.clip(RF*np.maximum(resv,0)/1e3,TMIN,TMAX)*tolscale;paths=[];geo=[]
   for a,b,f in segs:
    Ys,ix=dedup(Y[a:b+1],list(range(a,b+1)))
    if f or var=='none':p=fit_fixed(Ys,w,Q[0],SQ);dev=np.zeros(len(Ys))
    elif var=='spline':p,dev=fit_spline(Ys,w,Q[0],tol[ix],fb,sq=SQ)
    else:p,v_=fit_blend(Ys,w,Q[0],tol[ix],fb);dev=None
    paths.append((p,ix));geo.append(dict(a=a,b=b,kind=p.kind,L=round(p.L,3),**{k:v for k,v in p.meta.items() if k not in ('vias',)}))
   # re-check every path at <= 4 mm
   allQ=[];own=[];spm=0.;ss=[]
   for k,(p,ix) in enumerate(paths):
    Qs,s_,sp=sample_path(p,fb);allQ.append(Qs);own+= [k]*len(Qs);ss.append(s_);spm=max(spm,sp)
   QA=np.vstack(allQ);rc=check_all(pool,act,QA);summ=summarize_check(rc);summ['max_spacing_mm']=round(spm*1e3,3)
   own=np.array(own);bad=[i for i,x_ in enumerate(rc) if x_['hits'] or not x_['ranges']]
   rounds.append(dict(round=rnd,check=summ,geometry=geo))
   print(act,var,'round',rnd,json.dumps(summ),'%.0fs'%(time.monotonic()-t00),flush=True)
   if not bad or var=='none':break
   # tighten the tolerance of the stored states near each hit (by path parameter)
   off=np.r_[0,np.cumsum([len(x_) for x_ in allQ])]
   for i in bad:
    k=own[i];p,ix=paths[k];sv=ss[k][i-off[k]];Yk=Y[ix]
    near=np.argmin(np.linalg.norm(p.q(np.array([sv]))[:,DOF]*w-Yk,axis=1));lo_,hi_=max(0,near-3),min(len(ix),near+4)
    for j_ in ix[lo_:hi_]:tolscale[j_]*=.25
  # max deviation of the fixed pieces from the stored polyline (they stay "unchanged")
  fdev=0.
  for (p,ix),(a,b,f) in zip(paths,segs):
   if f:
    s_=np.linspace(0,p.L,400);Qp=p.q(s_);u=chord(Y[ix]);Yi=np.array([np.interp(s_,u,Y[ix][:,d]) for d in range(7)]).T
    fdev=max(fdev,float(fb.g7(Qp[:,DOF]-Yi/w).max()))
  # TCP of the fixed pieces vs the straight line through their stored TCP positions
  ftcp=0.
  for (p,ix),(a,b,f) in zip(paths,segs):
   if f:
    P_,_=fk(ctx,p.q(np.linspace(0,p.L,300)));Ps,_=fk(ctx,Q[a:b+1]);d0=Ps[-1]-Ps[0];d0/=np.linalg.norm(d0)
    ftcp=max(ftcp,float(np.max(np.linalg.norm((P_-Ps[0])-np.outer((P_-Ps[0])@d0,d0),axis=1))))
  # ---- time laws
  timing={}
  for pro in PRO:
   segt=[];tot=0.
   for (p,ix),(a,b,f) in zip(paths,segs):
    sg=Seg(ctx,p,food_of(a,b),LIMITS[pro],f);rt=time_segment(ctx,sg)
    segt.append(dict(a=a,b=b,fixed=f,time_s=round(rt['time_s'],2),ramp_s=round(rt['ramp_s'],2),iters=rt['iters'],worst=rt['worst'],peaks=rt['peaks']));tot+=rt['time_s']
    if pro==PRO[0]:p.meta['law_'+pro]=dict(t=rt['t'][::5].round(3).tolist(),s=rt['s'][::5].round(5).tolist())
   L_=LIMITS[pro];apt=scurve(R17['APPROACH_M'],LIMITS['same']['v_lin'],L_['a_tcp'],L_['a_tcp']/.1)
   total=tot+dw+2*R17['GRASP']+apt*len(apps)
   pk=lambda key:[max(st['peaks'][key][i] for st in segt) for i in range(7)]
   timing[pro]=dict(total_s=round(total,1),motion_s=round(tot,1),dwell_s=dw,grasp_release_s=2*R17['GRASP'],approach_s_each=round(apt,2),
    zero_velocity_points=len(segs)+1,ramp_s=round(sum(st['ramp_s'] for st in segt),1),ramp_fraction=round(sum(st['ramp_s'] for st in segt)/tot,3),
    peak_v=pk('v'),peak_a=pk('a'),peak_j=pk('j'),peak_v_tcp=max(st['peaks']['v_tcp'] for st in segt),peak_a_tcp=max(st['peaks']['a_tcp'] for st in segt),
    peak_j_tcp=max(st['peaks']['j_tcp'] for st in segt),peak_pgc_Nm=max((st['peaks']['pgc_Nm'] for st in segt),default=None),
    peak_pgc_static_Nm=max((st['peaks']['pgc_static_Nm'] or 0 for st in segt),default=None),peak_a_com=max(st['peaks']['a_com'] for st in segt),
    worst_ratio=max(max(v for k,v in st['worst'].items() if k!='stretch') for st in segt),stretched=[st['worst'].get('stretch') for st in segt if st['worst'].get('stretch')],segments=segt)
   print(act,var,pro,json.dumps({k:v for k,v in timing[pro].items() if k!='segments'}),'%.0fs'%(time.monotonic()-t00),flush=True)
  out['variants'][var]=dict(rounds=rounds,final_check=rounds[-1]['check'],fixed_piece_dev_mm=round(fdev*1e3,4),fixed_tcp_off_line_mm=round(ftcp*1e3,3),timing=timing,
   stored=dict(n_params=int(sum(_nparams(p) for p,ix in paths)),pieces=len(paths)))
  # the stored movement: geometry + check certificate + one time law
  mv=dict(act=act,variant=var,scale_w=w.tolist(),dof='cart x, 6 arm joints (q = f(s)/w); base_y, base_yaw, jaws as q0',q0=Q[0].tolist(),
   start=Q[0].tolist(),end=Q[-1].tolist(),check=rounds[-1]['check'],scene='R18b layout, chain scene of '+CHAINS[act]['file'],
   pieces=[_export(p,f,food_of(a,b),ctx['cfg']['dwell'],kf,b) for (p,ix),(a,b,f) in zip(paths,segs)])
  json.dump(mv,open(f'{OUT}/{act}_{var}_move.json','w'))
 pool.close()
 out['variants']={**prev.get('variants',{}),**out['variants']}   # keep variants of earlier runs
 out['elapsed_s']=round(time.monotonic()-t00);json.dump(out,open(f'{OUT}/{act}.json','w'),indent=1,default=float)
 print('saved',f'{OUT}/{act}.json',out['elapsed_s'],'s')
def _nparams(p):
 return int(np.size(p.f.c)) if hasattr(p.f,'c') else 0
def _export(p,fixed,food,dwell,kf,b):
 g=dict(kind=p.kind,L=p.L,fixed=fixed,food_kg=food,dwell_after_s=float(sum(v for k,v in dwell.items() if kf[k]==b)))
 if hasattr(p.f,'t'):g.update(type='bspline',k=int(p.f.k),knots=p.f.t.tolist(),coef=np.asarray(p.f.c).tolist())
 else:g.update(type='ppoly',breaks=p.f.x.tolist(),coef=np.asarray(p.f.c).tolist())
 if 'law_same' in p.meta:g['law_same']=p.meta['law_same']
 if 'radii' in p.meta:g['blend_radii']=[float(x) for x in p.meta['radii']]
 if p.sq:g['sq']={str(k):[float(l),float(sg)] for k,(l,sg) in p.sq.items()}   # coordinate k stored as h: q = limit + sign*(f/w)^2
 return g
if __name__=='__main__':main()
