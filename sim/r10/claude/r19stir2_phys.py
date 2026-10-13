"""R19 #40 gap 2: the R15 stir-fry physics (stirbench.py, MuJoCo 3.2.5, rigid food, no heat) re-run with the
spatula driven by the STORED velocity-continuous arm cycle (results/r19/stir/lib_stir_cycle_<arm>.json, #3) instead
of the bench's own keyframe timing. New file; stirbench.py and results/r15 are not touched.

The model (wok of 12 mm tiles, 90 x 15 mm dice dropped and settled, the R15 spatula as a free body on a compliant
weld to a mocap target, friction, hot zones) and every metric are stirbench.py's, copied verbatim (stirbench.py
runs on import, and it writes results/r15). Only the mocap target differs (DRIVER=):
 bench  stirbench's own target_at(): the keyframe splines of METHOD=scrape (the R15 'h_scrape_dice' run). This is
        the reproduction check: with T=12 it must give results/r15/stir_h_scrape_dice.json.
 arm    the arm's stored cycle. Geometry: the library B-splines q(s) (6 joints, cart at state_const); time law:
        the stored A_UR law entered FROM REST (the same TOPP + filter + slow-down procedure of r19stir_cycle.py,
        three cycles unrolled from rest; its middle cycle must equal the stored period, checked). The blade pose
        is the arm's: forward kinematics of the tool site (stir scene, r19stir_cycle.model), mapped to the blade
        frame by the inverse of r19stir_cycle.tcp() (grip 0.45 m, jaw -1), MINUS the 1 cm planning lift
        (LIFT along the wok-centre normal, r15stirwalk2 / r19stir_cycle): the arm path is the bench path lifted
        1 cm for the collision check; the stroke itself scrapes the steel like the bench. Before SETTLE the
        spatula hovers / descends onto its first pose exactly as stirbench's target_at().
        Stroke-0 start = the arm's H_stir0 = bench keyframe 0; t = SETTLE + time on the arm's law.
Metrics (stirbench): sampled every 10 ms after SETTLE for T s: hot-zone contact share per piece (mean, CV, p10,
 never_hot), longest hot dwell, cold spells, flips per 10 s, spill, spatula force / grip moment, blade speed.
python r19stir2_phys.py DRIVER=bench|arm [ARM=<arm>] [T=12] [TAG=..] (+ stirbench options; defaults = the
 h_scrape_dice run: METHOD=scrape FOOD=dice N=90 PERIOD=2.4 GRIP=.45 MU=.3 SEED=1)
 -> results/r19/stir/phys/stir2_<tag>.json
 [STOP=<sim t>] / [RESUME=1]  exact checkpoint / resume (MuJoCo integration state + accumulators) so that a run can be
                              split into commands of < 5 min; chunked == unchunked was checked bit for bit
 [DIAG=1]                     blade kinematics only (edge gap to the steel per work / return, arrival speed), no physics
                              -> results/r19/stir/phys/diag_<tag>.json
 [LIB=<retimed entry> LAWNPZ=<its from-rest law npz>]  drive with a retimed law (r19stir2_retime.py) instead"""
import sys,os,json,time,numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation,RotationSpline
from scipy.interpolate import CubicSpline
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
DEF=dict(METHOD='scrape',FOOD='dice',N='90',T='12',PERIOD='2.4',GRIP='.45',MU='.3')   # the R15 h_scrape_dice run (results/r15/stir_h_scrape_dice.json)
for k_,v_ in DEF.items():KV.setdefault(k_,v_)
DRIVER=KV.get('DRIVER','bench');ARM=KV.get('ARM','ur5e_enc2_pgc')
OUTD='results/r19/stir/phys'
# ======================================================================= stirbench.py, verbatim from here (model, keyframes)
METHOD=KV.get('METHOD','push');FOOD=KV.get('FOOD','dice');N=int(KV.get('N',150));T=float(KV.get('T',12));PERIOD=float(KV.get('PERIOD',1.))
MU=float(KV.get('MU',.3));HOTS=[float(x) for x in KV.get('HOTS','.09,.13').split(',')];HOT=HOTS[0];PAUSE=float(KV.get('PAUSE',0));PAUSE_EVERY=float(KV.get('PAUSE_EVERY',10));TILT=float(KV.get('TILT',40));RPM=float(KV.get('RPM',20));GRIP=float(KV.get('GRIP',.30))
SEED=int(KV.get('SEED',1));CLEAR=float(KV.get('CLEAR',.0015));WELD=KV.get('WELD','.005 1');DT=float(KV.get('DT',.001));FPS=30;SETTLE=1.5;
TAG=KV.get('TAG',f"{DRIVER}{'_'+ARM if DRIVER=='arm' else ''}_{METHOD}_{FOOD}_t{T:g}")
assert METHOD in ('push2','scrape','flip2'),'only the spatula methods'
RS,A_RIM=.20,.17;TH_MAX=np.arcsin(A_RIM/RS);DEPTH=RS-np.sqrt(RS**2-A_RIM**2);TT=.012
def fmt(v):return ' '.join(f'{float(x):.9g}' for x in v)
def quat(Rm):return Rotation.from_matrix(Rm).as_quat()[[3,0,1,2]]
rng=np.random.default_rng(SEED)
root=E.Element('mujoco');E.SubElement(root,'compiler',angle='radian',autolimits='true')
E.SubElement(root,'option',timestep=str(DT),cone='pyramidal');E.SubElement(root,'size',memory='256M')
v=E.SubElement(root,'visual');E.SubElement(v,'global',offwidth='1280',offheight='720');E.SubElement(v,'headlight',ambient='.45 .45 .45',diffuse='.5 .5 .5')
wb=E.SubElement(root,'worldbody');eq=E.SubElement(root,'equality');act=E.SubElement(root,'actuator')
E.SubElement(wb,'light',pos='.3 -.5 1.5',dir='-.2 .4 -1',diffuse='.5 .5 .5')
E.SubElement(wb,'geom',name='floor',type='plane',pos='0 0 -.25',size='2 2 .01',rgba='.82 .8 .78 1')
WOK0=np.array([0.,0.,0.])
wk=E.SubElement(wb,'body',name='wok',pos=fmt(WOK0))
WC=dict(rgba='.18 .18 .2 1',friction=f'{MU} .005 .0001',contype='2',conaffinity='2',solref='.004 1',priority='1')  # priority: the wok's μ (oiled steel) governs food-wok contacts
tiles=[]  # (name, polar angle mid)
E.SubElement(wk,'geom',name='wok_t0',type='cylinder',size=fmt([RS*np.sin(np.radians(6))+.004,TT/2]),pos=fmt([0,0,-TT/2]),**WC);tiles.append(('wok_t0',0.))
edges=np.radians(np.r_[6:np.degrees(TH_MAX):5.,np.degrees(TH_MAX)])
for i in range(len(edges)-1):
 ta,tb=edges[i],edges[i+1];tm=(ta+tb)/2;naz=max(10,int(np.ceil(2*np.pi*RS*np.sin(tm)/.03)))
 for k in range(naz):
  ph=2*np.pi*(k+.5)/naz;r=np.array([np.sin(tm)*np.cos(ph),np.sin(tm)*np.sin(ph),-np.cos(tm)])
  et=np.array([np.cos(tm)*np.cos(ph),np.cos(tm)*np.sin(ph),np.sin(tm)]);ep=np.array([-np.sin(ph),np.cos(ph),0])
  c=np.array([0,0,RS])+(RS+TT/2)*r;n=f'wok_t{i+1}_{k}'
  E.SubElement(wk,'geom',name=n,type='box',size=fmt([RS*np.sin(tm)*np.pi/naz*1.12,RS*(tb-ta)/2*1.12,TT/2]),pos=fmt(c),quat=fmt(quat(np.c_[ep,et,r])),**WC);tiles.append((n,tm))
import spatula15 as SP
SPAT=('push2','scrape','flip2')
if METHOD in SPAT:
 E.SubElement(wb,'body',name='target',pos='0 0 .3',mocap='true')
 sp=E.SubElement(wb,'body',name='spatula',pos='0 0 .3');E.SubElement(sp,'freejoint')
 E.SubElement(eq,'weld',body1='target',body2='spatula',solref=WELD)   # compliant (force-limited arm): the edge rides on the steel
 SC=dict(rgba='.75 .76 .8 1',friction=f'{MU} .005 .0001',density='7800',contype='3',conaffinity='3',solref='.004 1',priority='1')   # touches the wok (2) and the food (1)
 for k,(c_,h_) in enumerate(SP.blade_parts()):E.SubElement(sp,'geom',name=f'blade{k}',type='box',size=fmt(h_),pos=fmt(c_),**SC)
 a_=np.array([0,SP.BH,0]);GRIP_LOCAL=SP.grip_point(GRIP)
 E.SubElement(sp,'geom',name='handle',type='capsule',fromto=fmt(np.r_[a_,GRIP_LOCAL]),size='.008',**{**SC,'density':'1500'})
FD={'dice':('box',[.0075,.0075,.0075],1050),'shreds':('capsule',[.003,.025],1050),'slices':('box',[.015,.015,.0015],1050),'leaf':('box',[.025,.025,.001],600)}
ft,fs,den=FD[FOOD];FC=dict(friction=f'{max(MU,.4)} .005 .0001',solref='.004 1',density=str(den),contype='3',conaffinity='3')  # food touches the wok (2) and the spatula (1); spatula-wok pairs are off
foods=[];placed=[]
cnt=0
while len(foods)<N and cnt<20000:
 cnt+=1;p=np.array([rng.uniform(-.09,.09),rng.uniform(-.09,.09),rng.uniform(.03,.03+N*.0012)])
 if any(np.linalg.norm(p-q)<.022 for q in placed):continue
 placed.append(p);bn=f'f{len(foods)}';b=E.SubElement(wb,'body',name=bn,pos=fmt(p),quat=fmt(Rotation.random(random_state=rng.integers(1<<30)).as_quat()[[3,0,1,2]]));E.SubElement(b,'freejoint')
 col=(.85,.62,.42,1) if FOOD!='leaf' else (.45,.75,.35,1)
 E.SubElement(b,'geom',name=bn+'_g',type=ft,size=fmt(fs),rgba=fmt(col),**FC);foods.append(bn)
xml=E.tostring(root,encoding='unicode');m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m)
FB=np.array([m.body(n).id for n in foods]);FG={m.geom(n+'_g').id:i for i,n in enumerate(foods)}
TILEG=[m.geom(n).id for n,tm in tiles];TILEA=np.array(TILEG)
HOTCHORDS=[2*RS*np.sin(np.arcsin(h/RS)/2) for h in HOTS]   # 3-D distance from the heat centre that matches horizontal radius h on the fixed wok
def hot_sets():
 dist=np.linalg.norm(d.geom_xpos[TILEA]-np.array([0,0,-TT/2]),axis=1);return [set(TILEA[dist<=hc+TT/2].tolist()) for hc in HOTCHORDS]
TILEG=set(TILEG)
SPG=set(m.geom(n).id for n in [f'blade{k}' for k in range(5)]+['handle']) if METHOD in SPAT else set()
PATTERN=[tuple(map(float,x.split(':'))) for x in KV.get('PATTERN','0:0,30:0,0:.05,30:-.06,0:-.05').split(',')]
U0,U1=float(KV.get('U0',-.08)),float(KV.get('U1',.10));E0,E1=float(KV.get('E0',62)),float(KV.get('E1',38));ROLL=float(KV.get('ROLL',60))
blade_deg=[]
def P_(u,e,psi,f):
 p,R,bd=SP.pose(u,e,psi,E0+(E1-E0)*f,clear=CLEAR);blade_deg.append(bd);return p,R
def keyframes():
 K=[];t=SETTLE;k=0
 while t<SETTLE+T+PERIOD:
  ps,e=PATTERN[k%len(PATTERN)];psi=np.radians(ps);ps2,e2=PATTERN[(k+1)%len(PATTERN)]
  for f in np.linspace(0,1,12):K.append((t+.45*f*PERIOD,*P_(U0+(U1-U0)*f,e,psi,f)))
  p,R=P_(U1-.04,e,psi,1.);p=p+np.array([0,0,.05]);K.append((t+.56*PERIOD,p,R))
  if METHOD=='push2':
   sg=1 if k%2==0 else -1;K.append((t+.76*PERIOD,*SP.roll(p+np.array([0,0,.015]),R,GRIP,sg*ROLL)))
  elif METHOD=='flip2':
   sg=1 if k%2==0 else -1;pc,Rc=P_((U0+U1)/2,e,psi,.5);K.append((t+.76*PERIOD,*SP.roll(pc+np.array([0,0,.06]),Rc,GRIP,sg*ROLL)))
  else:K.append((t+.76*PERIOD,p+np.array([0,0,.015]),R))
  p0,R0=P_(U0,e2,np.radians(ps2),0.)
  K.append((t+.88*PERIOD,(p+p0)/2+np.array([0,0,.05]),R0))
  K.append((t+.97*PERIOD,p0+np.array([0,0,.015]),R0))
  t+=PERIOD;k+=1
  if PAUSE and (t-SETTLE)//PAUSE_EVERY>(t-PERIOD-SETTLE)//PAUSE_EVERY:
   p,R=K[-1][1],K[-1][2];K.append((t+.4,p+np.array([0,0,.15]),R));K.append((t+PAUSE-.45,p+np.array([0,0,.15]),R));K.append((t+PAUSE-.05,p+np.array([0,0,.012]),R));t+=PAUSE
 return K
KF=keyframes()
KT=np.array([k[0] for k in KF]);PS=CubicSpline(KT,np.array([k[1] for k in KF]),bc_type='clamped');RSPL=RotationSpline(KT,Rotation.from_matrix(np.array([k[2] for k in KF])))
def target_bench(t):
 if t<=KT[0]:
  p,R=KF[0][1],KF[0][2];return p+np.array([0,0,.12*min(1,(KT[0]-t)/.5)]),R
 t=min(t,KT[-1]);return PS(t),RSPL(t).as_matrix()
# ======================================================================= the arm driver (new)
def arm_series():
 """blade pose (wok frame) of the arm's stored cycle on the sim's time grid, + diagnostics"""
 os.environ['ARM']=ARM;sys.argv=[sys.argv[0],'cycle',f'ARM={ARM}']   # r19stir_cycle reads ARM from its argv
 import r19stir_cycle as C,r19stir_report as RP,arms,kitchen15 as K15
 from checker import reference
 LIBF=KV.get('LIB',f'results/r19/stir/lib_stir_cycle_{ARM}.json')   # LIB= a retimed entry (r19stir2_retime.py) with LAWNPZ= its from-rest law
 L_=json.load(open(LIBF));G=L_['geometry'];segs=[RP.Seg(g) for g in G['segments']];names=[g['name'] for g in G['segments']]
 path=C.Path([(sg,sg.a,sg.e) for sg in segs],per=True);isw=np.array([n.startswith('work') for n in names])
 def capf(s):
  r=np.mod(np.asarray(s,float),path.L);k=np.clip(np.searchsorted(path.B,r,side='right')-1,0,len(path.segs)-1);return np.where(isw[k],1.,1e12)
 cf=KV.get('LAWNPZ',f'{OUTD}/fromrest_{ARM}.npz')
 if os.path.exists(cf):z=np.load(cf);t_,s_=z['t'],z['s']
 elif 'LAWNPZ' in KV:raise SystemExit(f'no law file {cf}')
 else:
  V=np.radians(arms.speeds(ARM));tl=C.timelaw(path,V,np.radians(800.),capf,0.,0.,.1,reps=3);t_,s_=tl['t'],tl['s'];np.savez(cf,t=t_,s=s_,sd=tl['sd'])
 Lc=path.L;per=float(np.interp(2*Lc,s_,t_)-np.interp(Lc,s_,t_))
 assert abs(per-L_['time_law']['period_s'])<2e-3,(per,L_['time_law']['period_s'])
 M=C.model(-1);ch=M['ch'];mm,dd=ch.m,ch.d;sid=M['sid'];q0=np.array(G['state_const'])
 rot0=reference.rotation(-K15.HD,np.array([-1.,0,0]));b=K15.SP.grip_point(GRIP)
 def blade(q):
  dd.qpos[:]=q;mujoco.mj_kinematics(mm,dd);pt=dd.site_xpos[sid].copy();Rt=dd.site_xmat[sid].reshape(3,3).copy()
  R=Rt@rot0.T;pw=pt-R@b-K15.WOK0;p=pw.copy()
  for _ in range(6):n_=K15.SP.C-p;n_/=np.linalg.norm(n_);p=pw-C.LIFT*n_   # invert pw = p + LIFT n(p): the arm path minus its 1 cm planning lift
  return p,R
 nt=int(round((SETTLE+T+.5)/DT))+2;tg=np.arange(nt)*DT;tau=np.maximum(tg-SETTLE,0.)
 assert tau[-1]<=t_[-1],'law too short'
 sg_=np.interp(tau,t_,s_);Q=np.tile(q0,(nt,1));Q[:,3:9]=path(sg_);P=np.zeros((nt,3));Rs=np.zeros((nt,3,3))
 for i in range(nt):P[i],Rs[i]=blade(Q[i])
 # diagnostics: on the working parts the arm's blade must be the bench path (to the IK / smoothing error)
 B=path.B;dev_p=dev_r=0.;cnt=0
 for i in range(0,nt,7):
  if tg[i]<SETTLE:continue
  r=np.mod(sg_[i],Lc);k=int(np.clip(np.searchsorted(B,r,side='right')-1,0,len(segs)-1))
  if not isw[k]:continue
  tb=C.t0_of(k//2)+(r-B[k]);pb,Rb=PS(tb),RSPL(tb).as_matrix();dev_p=max(dev_p,float(np.linalg.norm(P[i]-pb)));dev_r=max(dev_r,float(np.degrees(Rotation.from_matrix(Rs[i]@Rb.T).magnitude())));cnt+=1
 info=dict(library=LIBF,law_file=cf,period_s=round(per,4),stored_period_s=L_['time_law']['period_s'],per_stroke_s=round(per/5,4),strokes_in_window=round(float(np.interp(T,t_,s_)/Lc*5),2),
  works_vs_bench_max_mm=round(dev_p*1e3,3),works_vs_bench_max_deg=round(dev_r,3),samples=cnt,law='A_UR 800 deg/s^2, W .1, entered from rest (3 cycles unrolled, r19stir_cycle.timelaw)' if 'LAWNPZ' not in KV else L_['time_law']['law'],lift_removed_m=C.LIFT)
 return tg,P,Rs,info
if DRIVER=='arm':
 TG,AP,AR,ARMINFO=arm_series();P0,R0=AP[np.searchsorted(TG,SETTLE)],AR[np.searchsorted(TG,SETTLE)]
 def target_at(t):
  if t<=SETTLE:return P0+np.array([0,0,.12*min(1,(SETTLE-t)/.5)]),R0   # stirbench's approach to the first pose
  i=min(int(round(t/DT)),len(TG)-1);return AP[i],AR[i]
 ts=TG[(TG>=SETTLE+.05)&(TG<SETTLE+T)];ii=np.searchsorted(TG,ts)
 vv=np.gradient(AP,DT,axis=0);aa=np.gradient(vv,DT,axis=0);ww=np.array([Rotation.from_matrix(AR[i+1]@AR[i].T).magnitude()/DT for i in range(len(AR)-1)]+[0.])
 path_v=np.linalg.norm(vv[ii],axis=1);path_a=np.linalg.norm(aa[ii],axis=1);path_w=ww[ii]
else:
 target_at=target_bench;ARMINFO=None
 ts=np.arange(SETTLE+.05,SETTLE+T,.002);path_v=np.linalg.norm(PS(ts,1),axis=1);path_a=np.linalg.norm(PS(ts,2),axis=1);path_w=np.linalg.norm(RSPL(ts,1),axis=1)
# ======================================================================= (new) DIAG=1: blade kinematics only, no physics
if KV.get('DIAG')=='1':
 """the blade's lowest edge point vs the steel (sphere RS about C) along the driven target: per stroke, the
 minimum gap on the working part (bench: CLEAR = 1.5 mm), the lowest gap during the air return, the speed toward
 the steel when the blade arrives at the next stroke start, and the peak blade speed; t in the stirring window"""
 cor=SP.bottom_corners();nt=int(round((SETTLE+T)/DT));tg=np.arange(nt)*DT
 if DRIVER=='arm':Pz,Rz=AP[:nt],AR[:nt]
 else:
  Z=[target_bench(x) for x in tg];Pz=np.array([z_[0] for z_ in Z]);Rz=np.array([z_[1] for z_ in Z])
 gap=np.array([RS-np.max(np.linalg.norm(Pz[i]+cor@Rz[i].T-SP.C,axis=1)) for i in range(nt)])   # lowest corner: largest distance from the centre
 vel=np.gradient(Pz,DT,axis=0);nrm=(SP.C-Pz)/np.linalg.norm(SP.C-Pz,axis=1)[:,None];vn=-np.sum(vel*nrm,axis=1)   # > 0: moving toward the steel
 if DRIVER=='arm':
  import r19stir_cycle as C
  z_=np.load(KV.get('LAWNPZ',f'{OUTD}/fromrest_{ARM}.npz'));s_=np.interp(np.maximum(tg-SETTLE,0.),z_['t'],z_['s']);L_=json.load(open(KV.get('LIB',f'results/r19/stir/lib_stir_cycle_{ARM}.json')))
  B=np.array([g['s0'] for g in L_['geometry']['segments']]+[L_['geometry']['segments'][-1]['s1']]);Lc=B[-1];seg=np.clip(np.searchsorted(B,np.mod(s_,Lc),side='right')-1,0,9)+10*(s_//Lc).astype(int)
 else:
  ph=np.maximum(tg-SETTLE,0.)/PERIOD;seg=2*np.floor(ph).astype(int)+(np.mod(ph,1.)>=.76)   # works 0 .. .76 P, then the return
 rows=[];w=tg>=SETTLE
 for sgi in np.unique(seg[w]):
  m_=w&(seg==sgi);i1=np.nonzero(m_)[0][-1]
  rows.append(dict(seg=int(sgi),kind='work' if sgi%2==0 else 'return',t0=round(float(tg[m_][0]),3),t1=round(float(tg[i1]),3),min_gap_mm=round(float(gap[m_].min()*1e3),1),max_gap_mm=round(float(gap[m_].max()*1e3),1),
   end_speed_to_steel_mps=round(float(vn[i1]),3),peak_speed_mps=round(float(np.linalg.norm(vel[m_],axis=1).max()),3)))
 out=dict(driver=DRIVER,arm=ARM if DRIVER=='arm' else None,window_s=T,segments=rows,
  work_min_gap_mm=round(min(r['min_gap_mm'] for r in rows if r['kind']=='work'),1),work_max_gap_mm=round(max(r['max_gap_mm'] for r in rows if r['kind']=='work'),1),
  return_min_gap_mm=round(min(r['min_gap_mm'] for r in rows if r['kind']=='return'),1),return_min_gap_median_mm=round(float(np.median([r['min_gap_mm'] for r in rows if r['kind']=='return'])),1),
  max_arrival_speed_to_steel_mps=round(max(r['end_speed_to_steel_mps'] for r in rows if r['kind']=='return'),3))
 os.makedirs(OUTD,exist_ok=True);json.dump(out,open(f'{OUTD}/diag_{TAG}.json','w'),indent=1);print(json.dumps({k:v for k,v in out.items() if k!='segments'}));sys.exit(0)
# ======================================================================= stirbench.py, verbatim (run + metrics)
p,R=target_at(0.);d.mocap_pos[0]=p;d.mocap_quat[0]=quat(R);sb=m.body('spatula').id
adr=m.jnt_qposadr[m.body_jntadr[sb]];d.qpos[adr:adr+3]=p;d.qpos[adr+3:adr+7]=quat(R)
mujoco.mj_forward(m,d)
NH=len(HOTS);SAMPLE=.01;ns=0;hot=np.zeros((NH,N));run=np.zeros((NH,N));cold=np.zeros((NH,N));dmax=np.zeros((NH,N));cmax=np.zeros((NH,N));flips=np.zeros(N);down=None
F=[];M=[];FW=[];t=0.;nxt=SETTLE;beg=time.monotonic();cf=np.zeros(6)
# ---- (new) exact checkpoint / resume, so that a long run can be split into commands of < 5 min: STOP=<sim time> saves
# the MuJoCo integration state (mj_getState, mjSTATE_INTEGRATION: time, qpos, qvel, act, warm start, mocap, ...) and
# every metric accumulator, RESUME=1 restores them; the continuation is bit-identical (checked: chunked == unchunked)
import pickle
CK=f'{OUTD}/ckpt_{TAG}.pkl';SPEC=mujoco.mjtState.mjSTATE_INTEGRATION;STOP=float(KV.get('STOP',1e9));wall0=0.
if KV.get('RESUME')=='1':
 z=pickle.load(open(CK,'rb'));assert z['xml_md5']==__import__('hashlib').md5(xml.encode()).hexdigest()
 mujoco.mj_setState(m,d,z['state'],SPEC);ns,hot,run,cold,dmax,cmax,flips,down,F,M,FW,t,nxt,wall0=[z[k_] for k_ in ('ns','hot','run','cold','dmax','cmax','flips','down','F','M','FW','t','nxt','wall')]
 print('resumed at t',t,flush=True)
while t<SETTLE+T:
 if t>=STOP:
  st=np.zeros(mujoco.mj_stateSize(m,SPEC));mujoco.mj_getState(m,d,st,SPEC);os.makedirs(OUTD,exist_ok=True)
  pickle.dump(dict(xml_md5=__import__('hashlib').md5(xml.encode()).hexdigest(),state=st,ns=ns,hot=hot,run=run,cold=cold,dmax=dmax,cmax=cmax,flips=flips,down=down,F=F,M=M,FW=FW,t=t,nxt=nxt,wall=wall0+time.monotonic()-beg),open(CK,'wb'))
  print('checkpoint at t',t,'->',CK,'%.0f s'%(time.monotonic()-beg),flush=True);sys.exit(0)
 p,R=target_at(t);d.mocap_pos[0]=p;d.mocap_quat[0]=quat(R)
 mujoco.mj_step(m,d);t+=DT
 if t>=nxt:
  nxt+=SAMPLE
  touch=np.zeros((NH,N),bool);f=np.zeros(3);mo=np.zeros(3);fwall=np.zeros(3);HS=hot_sets()
  gp=d.xpos[sb]+d.xmat[sb].reshape(3,3)@GRIP_LOCAL
  for i_ in range(d.ncon):
   c=d.contact[i_];a,b=int(c.geom[0]),int(c.geom[1])
   if b in FG and a in TILEG:
    for k_,hs in enumerate(HS):touch[k_,FG[b]]|=a in hs
   elif a in FG and b in TILEG:
    for k_,hs in enumerate(HS):touch[k_,FG[a]]|=b in hs
   if a in SPG or b in SPG:
    mujoco.mj_contactForce(m,d,i_,cf);fw=c.frame.reshape(3,3).T@cf[:3]
    fw=fw if b in SPG else -fw
    if a in TILEG or b in TILEG:fwall+=fw;continue
    f+=fw;mo+=np.cross(c.pos-gp,fw)
  if t>SETTLE:
   ns+=1;hot+=touch;run=np.where(touch,run+SAMPLE,0);cold=np.where(touch,0,cold+SAMPLE);dmax=np.maximum(dmax,run);cmax=np.maximum(cmax,cold)
   Rb=d.xmat[FB].reshape(N,3,3);loc=np.einsum('nji,j->ni',Rb,np.array([0,0,-1.]));dn=np.argmax(np.abs(loc),1)*2+(np.take_along_axis(loc,np.argmax(np.abs(loc),1)[:,None],1)[:,0]>0)
   if down is not None:flips+=(dn!=down)
   down=dn
   F.append(np.linalg.norm(f));M.append(np.linalg.norm(mo));FW.append(np.linalg.norm(fwall))
pos=d.xpos[FB]
rr=np.hypot(pos[:,0],pos[:,1]);inside=(rr<A_RIM+.01)&(pos[:,2]>-.02)&(pos[:,2]<DEPTH+.06)
q=lambda x,p_:round(float(np.percentile(x,p_)),3)
def zone(k):
 hf=(hot[k]/max(ns,1))[inside];dm,cm=dmax[k][inside],cmax[k][inside]
 return dict(hot_r_m=HOTS[k],hot_frac=dict(mean=round(float(hf.mean()),3),cv=round(float(hf.std()/max(hf.mean(),1e-9)),3),min=q(hf,0),p10=q(hf,10),p90=q(hf,90),max=q(hf,100)),
  never_hot=int((hf==0).sum()),dwell_max_s=round(float(dm.max()),2),dwell_p90_s=q(dm,90),cold_max_s=round(float(cm.max()),2),cold_p50_s=q(cm,50),cold_p90_s=q(cm,90))
zsurf=lambda r:RS-np.sqrt(np.maximum(RS**2-np.minimum(r,A_RIM)**2,0))
nh=(hot[-1]==0)&inside;lay=pos[:,2]-zsurf(rr)
diag=dict(never_hot_final_r_m=[round(float(x),3) for x in rr[nh]],never_hot_height_above_steel_mm=[round(float(x)*1000) for x in lay[nh]],
 pieces_more_than_12mm_above_steel_at_end=int(((lay>.012)&inside).sum()))
res=dict(driver=DRIVER,arm=ARM if DRIVER=='arm' else None,arm_law=ARMINFO,method=METHOD,food=FOOD,n=N,mass_g=round(float(m.body_mass[FB].sum()*1000)),period_s=PERIOD if DRIVER=='bench' else ARMINFO['per_stroke_s'],mu=MU,stir_s=T,seed=SEED,
 zones=[zone(k) for k in range(NH)],flips_per_10s=dict(mean=round(float(flips.mean()/T*10),2),min=round(float(flips.min()/T*10),2)),spilled=int((~inside).sum()),spilled_far_side=int(((~inside)&(pos[:,1]>0)).sum()),
 wall_s=round(wall0+time.monotonic()-beg,1),diag=diag,xml_md5=__import__('hashlib').md5(xml.encode()).hexdigest())
res.update(edge_on_steel_N=dict(p95=q(FW,95),mean=round(float(np.mean(FW)),2)),weld=WELD,edge_clear_m=CLEAR,spatula_F_N=dict(p95=q(F,95),max=round(float(np.max(F)),1),mean=round(float(np.mean(F)),2)),jam_samples_over_30N=int(np.sum(np.array(F)>30)),spatula_M_grip_Nm=dict(p95=q(M,95),max=round(float(np.max(M)),2)),
 grip_from_edge_m=GRIP,blade_v_mps=dict(max=round(float(path_v.max()),2),p95=q(path_v,95)),blade_a_mps2=dict(p95=q(path_a,95),max=round(float(path_a.max()),1)),blade_w_degps=dict(p95=round(float(np.degrees(np.percentile(path_w,95)))),max=round(float(np.degrees(path_w.max())))))
os.makedirs(OUTD,exist_ok=True);json.dump(res,open(f'{OUTD}/stir2_{TAG}.json','w'),indent=1);print(json.dumps(res))
