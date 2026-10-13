"""R19 #41: counterfactual spatula drivers for the stir physics. New file; r19stir2_phys.py is NOT edited.

r19stir2_phys.py runs unchanged (DRIVER=bench, OUTD -> results/r19/stir/spill as in r19spill_trace.py); a wrapper
around mujoco.mj_step OVERWRITES the mocap target just before every step with this file's own blade series (same
1 ms grid and index convention as the arm driver: pose[round(t / DT)]), then steps and records the trace exactly as
r19spill_trace.py. Before SETTLE the series is stirbench's hover / descent onto keyframe 0, as in both drivers.
Only the physics metrics of the result json (hot share, never hot, flips, spill, forces) are valid; the blade_v /
blade_a / blade_w entries there describe the bench keyframes, not the driven series (the trace has the driven one).

The series is built per stroke k from two sources:
 arm    the arm's blade (forward kinematics of the library geometry along its law, exactly as r19stir2_phys.py's
        arm driver: LIB= / LAWNPZ=, default the #3 entry and its from-rest law)
 bench  stirbench's keyframe splines at bench time (stroke k: SETTLE + k*2.4 + x)
MODE=
 arm         the arm series itself (validation: must reproduce r19stir2_phys.py DRIVER=arm bit for bit)
 bret        arm working parts (arm timing) + the BENCH return geometry (.76 P .. P of the stroke), played over the
             bench's own 0.576 s (RET=bench) or over the arm's return duration (RET=arm)
 aret        bench working parts at bench timing (s' = 1) + the ARM return geometry and timing
 bench       bench working parts and returns, bench timing; RAMP=1: stroke 0 is entered from rest with the arm law's
             own ramp (bench geometry at the arm's bench time while the arm is in work 0)
 bwarp       bench geometry, bench time slowed to s' = c on [a, b] s of every working part (WARP=a,b,c,ramp; NSLOW=n:
             strokes < n only)
 bkeys       stirbench's keyframes rebuilt here (bench_keys, identical to the R15 export when unmodified) with
             KEYMOD=U1,E1,back for strokes < NMOD, or for the patterns PMOD=0,1 in every cycle
LABELS=1     write only the stroke / segment labels of the series (results/r19/stir/spill/labels_<TAG>.npz), no physics
python r19spill_drive.py MODE=.. [ARM=..] [LIB=.. LAWNPZ=..] [RET=bench|arm] [RAMP=1] [WARP=.. NSLOW=..] [KEYMOD=.. NMOD=.. | PMOD=..]
   SEED=.. TAG=.. [T=12] [STOP=/RESUME=1] [LABELS=1]"""
import sys,os,json,numpy as np,mujoco
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
OUTD='results/r19/stir/spill';os.makedirs(OUTD,exist_ok=True)
MODE=KV['MODE'];ARM=KV.get('ARM','ur5e_enc2_pgc');DT=.001;SETTLE=1.5;P=2.4;WORKF=.76;T=float(KV.get('T',12))
LIBF=KV.get('LIB',f'results/r19/stir/lib_stir_cycle_{ARM}.json');LAWF=KV.get('LAWNPZ',f'results/r19/stir/phys/fromrest_{ARM}.npz')
sys.argv=[sys.argv[0]]+[a for a in sys.argv[1:] if a.split('=')[0] not in ('MODE','RET','RAMP','LIB','LAWNPZ','ARM','DRIVER','KEYMOD','NMOD','PMOD','WARP','NSLOW','LABELS')]+(   # MODE=arm runs the
 [f'DRIVER=arm',f'ARM={ARM}',f'LIB={LIBF}',f'LAWNPZ={LAWF}'] if MODE=='arm' else ['DRIVER=bench'])   # base script's own arm driver underneath (validation)
NT=int(round((SETTLE+T+.5)/DT))+2;TG=np.arange(NT)*DT
# ---------------------------------------------------------------- the two sources
def bench_src():
 """stirbench's keyframe splines (r19stir2_phys / stirbench keyframes(), PERIOD 2.4), rebuilt from the R15 export"""
 from scipy.spatial.transform import Rotation,RotationSpline
 from scipy.interpolate import CubicSpline
 keys=json.load(open('results/r15/stir_h_scrape_dice_keys.json'))['keys'];KT=np.array([k['t'] for k in keys])
 PS=CubicSpline(KT,np.array([k['p'] for k in keys]),bc_type='clamped');RS=RotationSpline(KT,Rotation.from_matrix(np.array([k['R'] for k in keys])))
 def f(tb):tb=np.clip(np.asarray(tb,float),KT[0],KT[-1]);return PS(tb),RS(tb).as_matrix()
 return f,KT
PMOD=[int(x) for x in KV['PMOD'].split(',')] if 'PMOD' in KV else None   # bkeys: modify the strokes of these patterns (every cycle) instead of k < NMOD
def bench_keys(U1m,E1m,BACKm,nmod,T_=12.,check=False):
 """stirbench.keyframes() for METHOD=scrape (same code, PERIOD 2.4, default PATTERN / U0 U1 E0 E1, CLEAR .0015), with
 strokes k < nmod using U1 = U1m, E1 = E1m and the lift point U1 - BACKm; -> pose function of bench time"""
 import spatula15 as SP
 from scipy.spatial.transform import Rotation,RotationSpline
 from scipy.interpolate import CubicSpline
 PAT=[(0.,0.),(30.,0.),(0.,.05),(30.,-.06),(0.,-.05)];U0,U1,E0,E1=-.08,.10,62.,38.;CL=.0015
 K=[];t=SETTLE;k=0
 while t<SETTLE+T_+P:
  mod=(lambda kk:kk%5 in PMOD) if PMOD else (lambda kk:kk<nmod)
  u1,e1,bk=(U1m,E1m,BACKm) if mod(k) else (U1,E1,.04)
  def P_(u,e,psi,f,e1=e1):p,R,_=SP.pose(u,e,psi,E0+(e1-E0)*f,clear=CL);return p,R
  ps,e=PAT[k%5];psi=np.radians(ps);ps2,e2=PAT[(k+1)%5]
  for f in np.linspace(0,1,12):K.append((t+.45*f*P,*P_(U0+(u1-U0)*f,e,psi,f)))
  p,R=P_(u1-bk,e,psi,1.);p=p+np.array([0,0,.05]);K.append((t+.56*P,p,R))
  K.append((t+.76*P,p+np.array([0,0,.015]),R))
  u1n,e1n=(U1m,E1m) if mod(k+1) else (U1,E1)
  p0,R0=P_(U0,e2,np.radians(ps2),0.,e1n)
  K.append((t+.88*P,(p+p0)/2+np.array([0,0,.05]),R0));K.append((t+.97*P,p0+np.array([0,0,.015]),R0));t+=P;k+=1
 KT=np.array([x[0] for x in K]);PS=CubicSpline(KT,np.array([x[1] for x in K]),bc_type='clamped');RS=RotationSpline(KT,Rotation.from_matrix(np.array([x[2] for x in K])))
 if check:return K
 def f(tb):tb=np.clip(np.asarray(tb,float),KT[0],KT[-1]);return PS(tb),RS(tb).as_matrix()
 return f
def arm_src():
 """r19stir2_phys.arm_series(), the same code path (blade = FK of the tool site through the inverse of
 r19stir_cycle.tcp(), minus the 1 cm planning lift): -> blade P, R on TG, s(TG), segment bounds"""
 os.environ['ARM']=ARM;sv=sys.argv;sys.argv=[sv[0],'cycle',f'ARM={ARM}']
 import r19stir_cycle as C,r19stir_report as RP,kitchen15 as K15
 from checker import reference
 sys.argv=sv
 L_=json.load(open(LIBF));G=L_['geometry'];segs=[RP.Seg(g) for g in G['segments']]
 path=C.Path([(sg,sg.a,sg.e) for sg in segs],per=True);z=np.load(LAWF);t_,s_=z['t'],z['s']
 M=C.model(-1);ch=M['ch'];mm,dd=ch.m,ch.d;sid=M['sid'];q0=np.array(G['state_const'])
 rot0=reference.rotation(-K15.HD,np.array([-1.,0,0]));b=K15.SP.grip_point(.45)
 def blade(q):
  dd.qpos[:]=q;mujoco.mj_kinematics(mm,dd);pt=dd.site_xpos[sid].copy();Rt=dd.site_xmat[sid].reshape(3,3).copy()
  R=Rt@rot0.T;pw=pt-R@b-K15.WOK0;p=pw.copy()
  for _ in range(6):n_=K15.SP.C-p;n_/=np.linalg.norm(n_);p=pw-C.LIFT*n_
  return p,R
 tau=np.maximum(TG-SETTLE,0.);sg_=np.interp(tau,t_,s_);Q=np.tile(q0,(NT,1));Q[:,3:9]=path(sg_);Pa=np.zeros((NT,3));Ra=np.zeros((NT,3,3))
 for i in range(NT):Pa[i],Ra[i]=blade(Q[i])
 return Pa,Ra,sg_,path.B,path.L
LBK=np.zeros(NT,int);LBW=np.ones(NT,bool);LBT=np.zeros(NT)   # labels of the driven series: stroke k, working part?, bench time in the stroke
def lab_bench(tb):
 x=np.maximum(np.asarray(tb,float)-SETTLE,0.);k=np.floor(x/P).astype(int);f=x-k*P;return k,f<WORKF*P,f
def lab_arm(sg,B,L):
 cyc=np.floor(sg/L);r=sg-cyc*L;j=np.clip(np.searchsorted(B,r,side='right')-1,0,9);k=(cyc*5+j//2).astype(int);w=(j%2==0)
 f=np.where(w,r-B[j],WORKF*P+(r-B[j])/(B[j+1]-B[j])*(1-WORKF)*P);return k,w,f
def build():
 bf,KT=bench_src();Pb0,Rb0=bf(KT[0])
 if MODE=='arm':
  Pa,Ra,sg,B,L=arm_src();LBK[:],LBW[:],LBT[:]=lab_arm(sg,B,L);return Pa,Ra
 P_=np.zeros((NT,3));R_=np.zeros((NT,3,3))
 if MODE=='bench' and KV.get('RAMP')!='1':
  P_[:],R_[:]=bf(TG);LBK[:],LBW[:],LBT[:]=lab_bench(TG);return P_,R_
 if MODE=='bkeys':   # stirbench keyframes rebuilt here (same code path), strokes < NMOD with U1 / E1 / LIFTU changed (KEYMOD=U1,E1,back)
  bk=bench_keys(*[float(x) for x in KV.get('KEYMOD','.10,38,.04').split(',')],int(KV.get('NMOD',2)))
  P_[:],R_[:]=bk(TG);LBK[:],LBW[:],LBT[:]=lab_bench(TG);return P_,R_
 if MODE=='bwarp':   # bench geometry, bench time slowed to s' = c on [a, b] s of every working part (cosine ramps of r s), strokes < NSLOW
  a,b,c,rr_=[float(x) for x in KV.get('WARP','.75,1.25,.5,.1').split(',')];ns=int(KV.get('NSLOW',99))
  def sig(tb):
   k,w,f=lab_bench(tb)
   if not w or k>=ns:return 1.
   x=1. if a<=f<=b else (.5-.5*np.cos(np.pi*(f-(a-rr_))/rr_) if a-rr_<f<a else (.5+.5*np.cos(np.pi*(f-b)/rr_) if b<f<b+rr_ else 0.))
   return 1-(1-c)*x
  tb=np.full(NT,KT[0]);i0=int(np.searchsorted(TG,SETTLE));tb[i0]=SETTLE
  for i in range(i0,NT-1):tb[i+1]=tb[i]+DT*sig(tb[i])
  P_[:],R_[:]=bf(tb);LBK[:],LBW[:],LBT[:]=lab_bench(tb);return P_,R_
 Pa,Ra,sg,B,L=arm_src();kk,isw,_=lab_arm(sg,B,L)
 i0=int(np.searchsorted(TG,SETTLE))
 if MODE=='bench':   # RAMP=1: bench geometry; bench time = SETTLE + s while the arm is in work 0 (s = bench time there), then s' = 1
  ie=i0+int(np.nonzero(~(isw[i0:]&(kk[i0:]==0)))[0][0]);tb=SETTLE+sg.copy();tb[ie:]=tb[ie-1]+(TG[ie:]-TG[ie-1])
  P_[:],R_[:]=bf(tb);LBK[:],LBW[:],LBT[:]=lab_bench(tb);return P_,R_
 # stroke-wise splicing: windows of the arm law (index ranges after SETTLE) for work k and return k
 ws=[]
 for k in range(int(kk[-1])+1):
  w=np.nonzero(isw&(kk==k))[0];rt=np.nonzero((~isw)&(kk==k))[0];ws.append((w[w>=i0],rt[rt>=i0]))
 P_[:],R_[:]=bf(np.full(NT,KT[0]))   # the pre-SETTLE part is set in the step wrapper
 cur=i0;_,_,fa=lab_arm(sg,B,L)
 def put(Ps,Rs,k,w,f):
  nonlocal cur
  n=min(len(Ps),NT-cur)
  if n>0:P_[cur:cur+n]=Ps[:n];R_[cur:cur+n]=Rs[:n];LBK[cur:cur+n]=k;LBW[cur:cur+n]=w;LBT[cur:cur+n]=np.asarray(f)[:n];cur+=n
 for k,(w,rt) in enumerate(ws):
  if not len(w):break
  tb0=SETTLE+k*P
  if MODE=='bret':put(Pa[w],Ra[w],k,True,fa[w])                                       # arm work k, arm timing
  else:x=np.arange(0,WORKF*P,DT);Pw,Rw=bf(tb0+x);put(Pw,Rw,k,True,x)                  # bench work k at s' = 1
  if MODE=='bret':
   D=(1-WORKF)*P if KV.get('RET','bench')=='bench' else len(rt)*DT
   x=np.arange(0,D,DT)/D*(1-WORKF)*P;Pr,Rr=bf(tb0+WORKF*P+x);put(Pr,Rr,k,False,WORKF*P+x)   # bench return geometry over D
  else:
   if len(rt):put(Pa[rt],Ra[rt],k,False,fa[rt])                                      # arm return k, arm geometry + timing
  if cur>=NT:break
 if cur<NT:P_[cur:]=P_[cur-1];R_[cur:]=R_[cur-1];LBK[cur:]=LBK[cur-1];LBW[cur:]=LBW[cur-1];LBT[cur:]=LBT[cur-1]
 return P_,R_
DP,DR=build()
if KV.get('LABELS')=='1':   # labels only (for traces run before the labels were stored)
 np.savez(f"{OUTD}/labels_{KV['TAG']}.npz",t=TG,lab_k=LBK,lab_w=LBW,lab_tb=LBT);print('labels',KV['TAG']);sys.exit(0)
# before SETTLE: stirbench's hover / descent onto the first pose (both drivers): P0 + (0, 0, .12 min(1, (SETTLE - t) / .5)),
# evaluated in the step wrapper from d.time exactly as the arm driver's target_at(t) does
i0=int(np.searchsorted(TG,SETTLE));P0,R0=DP[i0].copy(),DR[i0].copy()
from scipy.spatial.transform import Rotation
def quat(Rm):return Rotation.from_matrix(Rm).as_quat()[[3,0,1,2]]   # r19stir2_phys.quat
Q0=quat(R0);DQ=np.array([quat(R) for R in DR])
# ---------------------------------------------------------------- the run (as r19spill_trace.py), with the target override
EVERY=10;src=open('r19stir2_phys.py',encoding='utf-8').read();old="OUTD='results/r19/stir/phys'"
assert src.count(old)==1;src=src.replace(old,f"OUTD='{OUTD}'")
REC=dict(t=[],fp=[],fv=[],fc=[],sp=[],sq=[],sv=[],mp=[],mq=[]);_S={}
_step=mujoco.mj_step
def _setup(m):
 FB=[];k=0
 while True:
  try:FB.append(m.body(f'f{k}').id);k+=1
  except KeyError:break
 FB=np.array(FB);sb=m.body('spatula').id;fadr=np.array([m.jnt_dofadr[m.body_jntadr[b]] for b in FB]);sadr=m.jnt_dofadr[m.body_jntadr[sb]]
 gmap=np.full(m.ngeom,-1);gmap[[m.geom(f'f{i}_g').id for i in range(len(FB))]]=np.arange(len(FB))
 spg=np.zeros(m.ngeom,bool);spg[[m.geom(f'blade{i}').id for i in range(5)]+[m.geom('handle').id]]=True
 _S.update(m=m,FB=FB,sb=sb,fadr=fadr,sadr=sadr,gmap=gmap,spg=spg,n=0)
def step(m,d,*a,**k):
 t=d.time   # the override (the script set target_at(t) just before; d.time == its loop t)
 if t<=SETTLE:d.mocap_pos[0]=P0+np.array([0,0,.12*min(1,(SETTLE-t)/.5)]);d.mocap_quat[0]=Q0
 else:i=min(int(round(t/DT)),NT-1);d.mocap_pos[0]=DP[i];d.mocap_quat[0]=DQ[i]
 _step(m,d,*a,**k)
 if not _S or _S['m'] is not m:_setup(m)
 _S['n']+=1
 if _S['n']%EVERY:return
 FB=_S['FB'];R=REC;R['t'].append(d.time);R['fp'].append(d.xpos[FB].astype(np.float32));R['fv'].append(d.qvel[_S['fadr'][:,None]+np.arange(3)].astype(np.float32))
 c=np.zeros(len(FB),bool)
 if d.ncon:
  g=d.contact.geom[:d.ncon];gm=_S['gmap'];sp=_S['spg']
  a_=g[sp[g[:,1]]&(gm[g[:,0]]>=0),0];b_=g[sp[g[:,0]]&(gm[g[:,1]]>=0),1];c[gm[a_]]=True;c[gm[b_]]=True
 R['fc'].append(c);R['sp'].append(d.xpos[_S['sb']].copy());R['sq'].append(d.xquat[_S['sb']].copy());R['sv'].append(d.qvel[_S['sadr']:_S['sadr']+6].copy())
 R['mp'].append(d.mocap_pos[0].copy());R['mq'].append(d.mocap_quat[0].copy())
mujoco.mj_step=step
def save(g):
 if not REC['t']:return
 tag=g.get('TAG','x');fn=f"{OUTD}/trace_{tag}_{int(round(REC['t'][0]*1000)):05d}.npz"
 ii=np.minimum(np.round(np.array(REC['t'])/DT).astype(int),NT-1);np.savez_compressed(fn,**{k:np.array(v) for k,v in REC.items()},every=EVERY,seed=int(g.get('SEED',-1)),mode=MODE,lab_k=LBK[ii],lab_w=LBW[ii],lab_tb=LBT[ii]);print('trace',fn,len(REC['t']),'samples',flush=True)
G={'__name__':'__main__','__file__':os.path.abspath('r19stir2_phys.py')}
try:exec(compile(src,os.path.abspath('r19stir2_phys.py'),'exec'),G)
except SystemExit as e:
 save(G);raise
save(G)
r=json.load(open(f"{OUTD}/stir2_{G['TAG']}.json"));r['spill_driver']=dict(mode=MODE,arm=ARM,lib=LIBF,law=LAWF,ret=KV.get('RET'),ramp=KV.get('RAMP'),note='mocap overridden by r19spill_drive.py; blade_* metrics are the bench keyframes, not the driven series')
json.dump(r,open(f"{OUTD}/stir2_{G['TAG']}.json",'w'),indent=1)
