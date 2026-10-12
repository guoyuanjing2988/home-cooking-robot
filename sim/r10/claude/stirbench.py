"""R15 stir-fry bench (MuJoCo 3.2.5, no fluid, no heat): does a stirring method keep every
piece of food moving over the hot part of the wok, without throwing food out, and what
force does the spatula feel?
Wok: 34 cm carbon-steel wok as a spherical cap (sphere radius 0.20 m, rim radius 0.17 m,
depth 95 mm) built from 12 mm thick tiles (thin plates let fast pieces tunnel through soft
contacts). Origin = the inner bottom point. Hot zone = the wok surface within horizontal
radius HOT (default 0.09 m: the bottom ~18 cm, an assumption for a concave induction coil).
Food: FOOD=dice (15 mm cubes, 3.5 g), shreds (Ø6 x 50 mm capsules), slices (30x30x3 mm),
leaf (50x50x2 mm). N pieces dropped in and settled.
Methods (METHOD=):
 none   - no stirring (baseline)
 scrape - 翻炒 stroke for one arm: the spatula (spatula15.py) scrapes from the near side up the
          far wall with its blade under the food (handle 62° -> 38° above horizontal), lifts and
          returns in the air to the next start; strokes cycle through 5 yaw/offset lines.
 push2  - the same, plus a roll of the spatula about its handle (wrist 3, +-ROLL°) at the far
          end to turn the load over sideways.
 flip2  - the same push, then the loaded blade is carried back over the middle of the pile
          and rolled there, so the bottom layer lands on top.
 drum   - motorised tilted wok (kept for reference; a shallow wok tilted 30-40° spills, so it is
          not a fair model of a drum machine and is not used as evidence).
The spatula is a free body welded to a mocap target through a compliant weld (WELD solref,
like a force-limited arm); the lowest point of its edge rides CLEAR (default 1.5 mm) off the
steel, so it scrapes the wok like a real spatula (spatula-wok contacts are on).
Earlier variants (rigid blade 3 mm off the steel, upright blade, pull-backs) are in
stirbench.py.bak2: thin food jammed in the gap, and the reach probes showed the arm cannot
follow their far-end and pull-back poses.
Metrics (sampled every 10 ms after a 1.5 s settle):
 hot_frac per piece  - share of time touching a hot-zone tile; mean, CV, min, p10, max
 dwell_max_s         - longest unbroken hot contact of any piece (burn risk)
 cold_max_s          - longest unbroken spell of any piece away from the hot zone
 flips_per_10s       - how often a piece's down-facing face changes (both sides get heat)
 spilled             - pieces outside the wok at the end
 spatula F / M       - contact force on the spatula and its moment about the grip point
                       (GRIP m from the blade edge along the handle): p95 and max
Usage: python stirbench.py METHOD=push2 FOOD=dice N=90 T=12 PERIOD=2.4 MU=.3 [HOTS=.09,.13]
 [PAUSE=6 PAUSE_EVERY=10] [CLEAR=-.001 WELD='.005 1'] [U0 U1 E0 E1 ROLL] [EXPORT=1]
 [TILT=40 RPM=20] [FRAMES=1] [TAG=..]  -> results/r15/stir_<tag>.json"""
import sys,os,json,time,numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation,RotationSpline
from scipy.interpolate import CubicSpline
KV=dict(a.split('=',1) for a in sys.argv[1:])
METHOD=KV.get('METHOD','push');FOOD=KV.get('FOOD','dice');N=int(KV.get('N',150));T=float(KV.get('T',12));PERIOD=float(KV.get('PERIOD',1.))
MU=float(KV.get('MU',.3));HOTS=[float(x) for x in KV.get('HOTS','.09,.13').split(',')];HOT=HOTS[0];PAUSE=float(KV.get('PAUSE',0));PAUSE_EVERY=float(KV.get('PAUSE_EVERY',10));TILT=float(KV.get('TILT',40));RPM=float(KV.get('RPM',20));GRIP=float(KV.get('GRIP',.30))
SEED=int(KV.get('SEED',1));CLEAR=float(KV.get('CLEAR',.0015));WELD=KV.get('WELD','.005 1');DT=float(KV.get('DT',.001));FPS=30;SETTLE=1.5;
TAG=KV.get('TAG',f"{METHOD}_{FOOD}_n{N}_p{PERIOD:g}_mu{MU:g}"+(f"_t{TILT:g}_r{RPM:g}" if METHOD=='drum' else ''))
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
# ---- wok (fixed, or a tilted spinning drum) ----
WOK0=np.array([0.,0.,0.])
if METHOD=='drum':
 Rt=Rotation.from_euler('x',np.radians(TILT)).as_matrix()   # axis tilts toward -y (the robot side)
 # pivot so that the tilted wok's lowest inner point stays near the origin
 low=Rt@np.array([0,0,RS])-RS*np.array([0,0,1.]);wpos=-low
 wk=E.SubElement(wb,'body',name='wok',pos=fmt(wpos),quat=fmt(quat(Rt)))
 E.SubElement(wk,'joint',name='spin',type='hinge',axis='0 0 1',pos=fmt([0,0,RS]),damping='.5',armature='.05')   # armature: keeps the explicit velocity servo stable at dt 1 ms
 E.SubElement(wk,'inertial',pos=fmt([0,0,.03]),mass='1.4',diaginertia='.012 .012 .02')
 E.SubElement(act,'velocity',joint='spin',kv='10',ctrlrange='-20 20')
else:wk=E.SubElement(wb,'body',name='wok',pos=fmt(WOK0))
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
if METHOD=='drum':  # 3 radial fins (lifters) from near the pole to the rim
 for k in range(3):
  ph=2*np.pi*k/3
  for j,tm in enumerate(np.linspace(np.radians(12),TH_MAX-np.radians(3),8)):
   r=np.array([np.sin(tm)*np.cos(ph),np.sin(tm)*np.sin(ph),-np.cos(tm)]);et=np.array([np.cos(tm)*np.cos(ph),np.cos(tm)*np.sin(ph),np.sin(tm)]);ep=np.array([-np.sin(ph),np.cos(ph),0])
   c=np.array([0,0,RS])+(RS-.0125)*r
   E.SubElement(wk,'geom',name=f'fin{k}_{j}',type='box',size=fmt([.003,RS*(TH_MAX-np.radians(12))/16*1.1,.0125]),pos=fmt(c),quat=fmt(quat(np.c_[ep,et,r])),**WC)
# ---- spatula (spatula15.py, shared with the reach probes): free body welded to a mocap ----
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
# ---- food ----
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
# ---- stroke keyframes in the wok frame ----
PATTERN=[tuple(map(float,x.split(':'))) for x in KV.get('PATTERN','0:0,30:0,0:.05,30:-.06,0:-.05').split(',')]   # (stroke yaw deg, lateral offset m), cycled: covers the whole bottom
# (no -30° yaw: with the cart parked left of the wok its handle points at the arm base, r15reach finds no pose)
U0,U1=float(KV.get('U0',-.08)),float(KV.get('U1',.10));E0,E1=float(KV.get('E0',62)),float(KV.get('E1',38));ROLL=float(KV.get('ROLL',60))
blade_deg=[]
def P_(u,e,psi,f):
 """blade pose at stroke fraction f in [0,1] (handle elevation goes E0 -> E1 along the push)"""
 p,R,bd=SP.pose(u,e,psi,E0+(E1-E0)*f,clear=CLEAR);blade_deg.append(bd);return p,R
def keyframes():
 K=[];t=SETTLE;k=0
 while t<SETTLE+T+PERIOD:
  ps,e=PATTERN[k%len(PATTERN)];psi=np.radians(ps);ps2,e2=PATTERN[(k+1)%len(PATTERN)]
  # 翻炒 as a wrist-friendly stroke: scrape from the near side up the far wall with the blade under
  # the food, then (push2) roll the spatula about its handle (wrist 3) to turn the load over
  # sideways, and return in the air to the next stroke's start
  for f in np.linspace(0,1,12):K.append((t+.45*f*PERIOD,*P_(U0+(U1-U0)*f,e,psi,f)))
  # lift off the far wall first: the roll swings the blade corners ~6 cm about the handle axis
  p,R=P_(U1-.04,e,psi,1.);p=p+np.array([0,0,.05]);K.append((t+.56*PERIOD,p,R))
  if METHOD=='push2':
   sg=1 if k%2==0 else -1;K.append((t+.76*PERIOD,*SP.roll(p+np.array([0,0,.015]),R,GRIP,sg*ROLL)))
  elif METHOD=='flip2':   # carry the scraped-up bottom layer back over the pile and roll it off on top
   sg=1 if k%2==0 else -1;pc,Rc=P_((U0+U1)/2,e,psi,.5);K.append((t+.76*PERIOD,*SP.roll(pc+np.array([0,0,.06]),Rc,GRIP,sg*ROLL)))
  else:K.append((t+.76*PERIOD,p+np.array([0,0,.015]),R))
  p0,R0=P_(U0,e2,np.radians(ps2),0.)
  K.append((t+.88*PERIOD,(p+p0)/2+np.array([0,0,.05]),R0))
  K.append((t+.97*PERIOD,p0+np.array([0,0,.015]),R0))
  t+=PERIOD;k+=1
  if PAUSE and (t-SETTLE)//PAUSE_EVERY>(t-PERIOD-SETTLE)//PAUSE_EVERY:   # arm busy (fetching an addition): spatula parked above the wok
   p,R=K[-1][1],K[-1][2];K.append((t+.4,p+np.array([0,0,.15]),R));K.append((t+PAUSE-.45,p+np.array([0,0,.15]),R));K.append((t+PAUSE-.05,p+np.array([0,0,.012]),R));t+=PAUSE
 return K
KF=keyframes() if METHOD in SPAT else []
if KF:
 KT=np.array([k[0] for k in KF]);PS=CubicSpline(KT,np.array([k[1] for k in KF]),bc_type='clamped');RSPL=RotationSpline(KT,Rotation.from_matrix(np.array([k[2] for k in KF])))
def target_at(t):
 if t<=KT[0]:
  p,R=KF[0][1],KF[0][2];return p+np.array([0,0,.12*min(1,(KT[0]-t)/.5)]),R
 t=min(t,KT[-1]);return PS(t),RSPL(t).as_matrix()
# blade path speed / acceleration / angular rate (what the arm must do), from the splines
if KF:
 ts=np.arange(SETTLE+.05,SETTLE+T,.002);path_v=np.linalg.norm(PS(ts,1),axis=1);path_a=np.linalg.norm(PS(ts,2),axis=1);path_w=np.linalg.norm(RSPL(ts,1),axis=1)
# ---- run ----
if KF:
 p,R=target_at(0.);d.mocap_pos[0]=p;d.mocap_quat[0]=quat(R);sb=m.body('spatula').id
 adr=m.jnt_qposadr[m.body_jntadr[sb]];d.qpos[adr:adr+3]=p;d.qpos[adr+3:adr+7]=quat(R)
mujoco.mj_forward(m,d)
NH=len(HOTS);SAMPLE=.01;ns=0;hot=np.zeros((NH,N));run=np.zeros((NH,N));cold=np.zeros((NH,N));dmax=np.zeros((NH,N));cmax=np.zeros((NH,N));flips=np.zeros(N);down=None
F=[];M=[];FW=[];frames=[];t=0.;nxt=SETTLE;beg=time.monotonic();cf=np.zeros(6)
if METHOD=='drum':d.ctrl[0]=RPM*2*np.pi/60
while t<SETTLE+T:
 if KF:
  p,R=target_at(t);d.mocap_pos[0]=p;d.mocap_quat[0]=quat(R)
 mujoco.mj_step(m,d);t+=DT
 if KV.get('FRAMES') and t>=len(frames)/FPS:frames.append(d.qpos.copy())
 if t>=nxt:
  nxt+=SAMPLE
  touch=np.zeros((NH,N),bool);f=np.zeros(3);mo=np.zeros(3);fwall=np.zeros(3);HS=hot_sets()
  if KF:gp=d.xpos[sb]+d.xmat[sb].reshape(3,3)@GRIP_LOCAL
  for i_ in range(d.ncon):
   c=d.contact[i_];a,b=int(c.geom[0]),int(c.geom[1])
   if b in FG and a in TILEG:
    for k_,hs in enumerate(HS):touch[k_,FG[b]]|=a in hs
   elif a in FG and b in TILEG:
    for k_,hs in enumerate(HS):touch[k_,FG[a]]|=b in hs
   if a in SPG or b in SPG:
    mujoco.mj_contactForce(m,d,i_,cf);fw=c.frame.reshape(3,3).T@cf[:3]
    fw=fw if b in SPG else -fw   # force on the spatula
    if a in TILEG or b in TILEG:fwall+=fw;continue   # steel on steel (the scraping edge)
    f+=fw;mo+=np.cross(c.pos-gp,fw)
  if t>SETTLE:
   ns+=1;hot+=touch;run=np.where(touch,run+SAMPLE,0);cold=np.where(touch,0,cold+SAMPLE);dmax=np.maximum(dmax,run);cmax=np.maximum(cmax,cold)
   Rb=d.xmat[FB].reshape(N,3,3);loc=np.einsum('nji,j->ni',Rb,np.array([0,0,-1.]));dn=np.argmax(np.abs(loc),1)*2+(np.take_along_axis(loc,np.argmax(np.abs(loc),1)[:,None],1)[:,0]>0)
   if down is not None:flips+=(dn!=down)
   down=dn
   if KF:F.append(np.linalg.norm(f));M.append(np.linalg.norm(mo));FW.append(np.linalg.norm(fwall))
   if KV.get('DEBUG') and KF and np.linalg.norm(fwall)>300:print('steel',round(t,3),round(((t-SETTLE)%PERIOD)/PERIOD,2),round(float(np.linalg.norm(fwall))),flush=True)
pos=d.xpos[FB]
if METHOD=='drum':
 Rw=d.xmat[m.body('wok').id].reshape(3,3);loc=(pos-d.xpos[m.body('wok').id])@Rw;rr=np.hypot(loc[:,0],loc[:,1]);inside=(rr<A_RIM+.01)&(loc[:,2]<DEPTH+.03)&(loc[:,2]>-.02)
else:rr=np.hypot(pos[:,0],pos[:,1]);inside=(rr<A_RIM+.01)&(pos[:,2]>-.02)&(pos[:,2]<DEPTH+.06)
q=lambda x,p_:round(float(np.percentile(x,p_)),3)
def zone(k):
 hf=(hot[k]/max(ns,1))[inside];dm,cm=dmax[k][inside],cmax[k][inside]
 return dict(hot_r_m=HOTS[k],hot_frac=dict(mean=round(float(hf.mean()),3),cv=round(float(hf.std()/max(hf.mean(),1e-9)),3),min=q(hf,0),p10=q(hf,10),p90=q(hf,90),max=q(hf,100)),
  never_hot=int((hf==0).sum()),dwell_max_s=round(float(dm.max()),2),dwell_p90_s=q(dm,90),cold_max_s=round(float(cm.max()),2),cold_p50_s=q(cm,50),cold_p90_s=q(cm,90))
zsurf=lambda r:RS-np.sqrt(np.maximum(RS**2-np.minimum(r,A_RIM)**2,0))
nh=(hot[-1]==0)&inside;lay=pos[:,2]-zsurf(rr)
diag=dict(never_hot_final_r_m=[round(float(x),3) for x in rr[nh]],never_hot_height_above_steel_mm=[round(float(x)*1000) for x in lay[nh]],
 pieces_more_than_12mm_above_steel_at_end=int(((lay>.012)&inside).sum()))
res=dict(method=METHOD,food=FOOD,n=N,mass_g=round(float(m.body_mass[FB].sum()*1000)),period_s=PERIOD if KF else None,mu=MU,stir_s=T,pause_s=PAUSE or None,pause_every_s=PAUSE_EVERY if PAUSE else None,
 tilt_deg=TILT if METHOD=='drum' else None,rpm=RPM if METHOD=='drum' else None,zones=[zone(k) for k in range(NH)],
 flips_per_10s=dict(mean=round(float(flips.mean()/T*10),2),min=round(float(flips.min()/T*10),2)),spilled=int((~inside).sum()),spilled_far_side=int(((~inside)&(pos[:,1]>0)).sum()),
 wall_s=round(time.monotonic()-beg,1),diag=diag)
if KF:
 res.update(blade_to_steel_deg=dict(min=round(min(blade_deg),1),max=round(max(blade_deg),1)),handle_elev_deg=[E0,E1],roll_deg=ROLL if METHOD=='push2' else 0,edge_on_steel_N=dict(p95=q(FW,95),mean=round(float(np.mean(FW)),2)),weld=WELD,edge_clear_m=CLEAR,spatula_F_N=dict(p95=q(F,95),max=round(float(np.max(F)),1),mean=round(float(np.mean(F)),2)),jam_samples_over_30N=int(np.sum(np.array(F)>30)),spatula_M_grip_Nm=dict(p95=q(M,95),max=round(float(np.max(M)),2)),
  grip_from_edge_m=GRIP,blade_v_mps=dict(max=round(float(path_v.max()),2),p95=q(path_v,95)),blade_a_mps2=dict(p95=q(path_a,95),max=round(float(path_a.max()),1)),blade_w_degps=dict(p95=round(float(np.degrees(np.percentile(path_w,95)))),max=round(float(np.degrees(path_w.max())))))
os.makedirs('results/r15',exist_ok=True);json.dump(res,open(f'results/r15/stir_{TAG}.json','w'),indent=1);print(json.dumps(res))
if KV.get('EXPORT'):json.dump(dict(note='spatula keyframes in the wok frame (origin = inner bottom point, +y = away from the robot); grip = handle point GRIP m from the blade edge',grip_local=GRIP_LOCAL.tolist(),clear_m=CLEAR,keys=[dict(t=k[0],p=np.asarray(k[1]).tolist(),R=np.asarray(k[2]).tolist()) for k in KF]),open(f'results/r15/stir_{TAG}_keys.json','w'),indent=1)
if KV.get('FRAMES'):np.save(f'results/r15/stir_{TAG}_frames.npy',np.array(frames));open(f'results/r15/stir_{TAG}.xml','w').write(xml)
