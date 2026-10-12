"""R15 plating bench (MuJoCo 3.2.5, no fluid): the arm lifts the wok by its grip block, carries
it to the plating spot left of the hood and tips it sideways (right rim down) over the plate,
as in the r15reach.py 'pour' probes (TIP=y, plate at kitchen15.PLATE). How much food lands on
the plate, how much stays in the wok, how much misses?
The wok (same tiles as stirbench.py) is a free body welded to a mocap target that follows the
pose sequence lift 4 cm -> carry -> tip 0..A_MAX at TIPRATE °/s -> hold HOLD s [-> SHAKE: +-6°
at 3 Hz for 1 s, 抖锅] -> back level. Plate: Ø240 mm, 20 mm rim, at the plating spot.
Food: dice (15 mm, 3.5 g), N pieces settled in the wok first (MU = food-wok friction).
Usage: python pourwok.py N=90 MU=.3 A_MAX=90 [TIPRATE=60] [HOLD=1] [SHAKE=1] [LIPX=-.05] [DROP=.08]
 [RIM=.02] [PMU=.5] [PR=plate radius] [GUARD=.08] [STICKY=1] [STEP=deg hold] [CARRY=1.2] [FRAMES=1] [TAG=..]
-> results/r15/pour_<tag>.json"""
import sys,os,json,numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
import kitchen15 as K
KV=dict(a.split('=',1) for a in sys.argv[1:])
N=int(KV.get('N',90));MU=float(KV.get('MU',.3));AMAX=float(KV.get('A_MAX',90));RATE=float(KV.get('TIPRATE',60));HOLD=float(KV.get('HOLD',1.));SHAKE=KV.get('SHAKE')=='1'
FOOD=KV.get('FOOD','dice');LIPX=float(KV.get('LIPX',-.05));DROP=float(KV.get('DROP',.08));RIM_H=float(KV.get('RIM',.02));CARRY=float(KV.get('CARRY',1.2));PMU=float(KV.get('PMU',.5));PR=float(KV.get('PR',K.PLATE['r']));STICKY=KV.get('STICKY')=='1';STEP=float(KV.get('STEP',0));GUARD=float(KV.get('GUARD',0));DT=.001;FPS=30;TAG=KV.get('TAG',f"{FOOD}_n{N}_mu{MU:g}_a{AMAX:g}"+('_shake' if SHAKE else ''))
RS,A_RIM,DEPTH,TT=K.RS,K.A_RIM,K.DEPTH,.012;TH_MAX=np.arcsin(A_RIM/RS)
def fmt(v):return ' '.join(f'{float(x):.9g}' for x in v)
def quat(R):return Rotation.from_matrix(R).as_quat()[[3,0,1,2]]
root=E.Element('mujoco');E.SubElement(root,'compiler',angle='radian',autolimits='true')
E.SubElement(root,'option',timestep=str(DT),cone='pyramidal');E.SubElement(root,'size',memory='256M')
v=E.SubElement(root,'visual');E.SubElement(v,'global',offwidth='1280',offheight='720');E.SubElement(v,'headlight',ambient='.45 .45 .45',diffuse='.5 .5 .5')
wb=E.SubElement(root,'worldbody');eq=E.SubElement(root,'equality')
E.SubElement(wb,'light',pos='.3 -.5 1.5',dir='-.2 .4 -1',diffuse='.5 .5 .5')
# world frame = the wok frame at rest on the cooker (origin = inner bottom point); counter top z = .85 - .925
ZC=.85-K.WOK0[2];E.SubElement(wb,'geom',name='counter',type='plane',pos=fmt([0,0,ZC]),size='2 2 .01',rgba='.55 .45 .4 1',friction='.5 .005 .0001')
PC=K.PLATE['c']-K.WOK0;PC[2]=ZC
E.SubElement(wb,'geom',name='plate',type='cylinder',pos=fmt(PC+[0,0,.004]),size=fmt([PR,.004]),rgba='.95 .95 .93 1',friction=f'{PMU} .005 .0001',priority='1')
for k in range(32):
 a=2*np.pi*k/32;g=E.SubElement(wb,'geom',name=f'plate_rim{k}',type='box',size=fmt([.004,PR*np.pi/32*1.1,RIM_H/2+.002]),pos=fmt(PC+[PR*np.cos(a),PR*np.sin(a),RIM_H/2+.002]),rgba='.95 .95 .93 1',friction=f'{PMU} .005 .0001',priority='1')
 g.set('quat',fmt(quat(Rotation.from_euler('z',a).as_matrix()@Rotation.from_euler('y',np.radians(-25)).as_matrix())))
if GUARD:   # plating-stand back guard: an arc wall GUARD m high behind the plate (far side, +x), -70..+70°
 for k in range(15):
  a=np.radians(-70+10*k);g=E.SubElement(wb,'geom',name=f'guard{k}',type='box',size=fmt([.003,(PR+.012)*np.radians(10)/2*1.1,GUARD/2]),pos=fmt(PC+[(PR+.012)*np.cos(a),(PR+.012)*np.sin(a),GUARD/2]),rgba='.7 .72 .75 1',friction=f'{PMU} .005 .0001')
  g.set('quat',fmt(quat(Rotation.from_euler('z',a).as_matrix())))
E.SubElement(wb,'body',name='target',pos='0 0 0',mocap='true')
wk=E.SubElement(wb,'body',name='wok',pos='0 0 0');E.SubElement(wk,'freejoint')
E.SubElement(eq,'weld',body1='target',body2='wok',solref='.004 1')
WC=dict(rgba='.18 .18 .2 1',friction=f'{MU} .005 .0001',priority='1',solref='.004 1',density='7800')
E.SubElement(wk,'geom',type='cylinder',size=fmt([RS*np.sin(np.radians(6))+.004,TT/2]),pos=fmt([0,0,-TT/2]),**WC)
edges=np.radians(np.r_[6:np.degrees(TH_MAX):5.,np.degrees(TH_MAX)]);C=np.array([0,0,RS])
for i in range(len(edges)-1):
 ta,tb=edges[i],edges[i+1];tm=(ta+tb)/2;naz=max(10,int(np.ceil(2*np.pi*RS*np.sin(tm)/.03)))
 for k in range(naz):
  ph=2*np.pi*(k+.5)/naz;r=np.array([np.sin(tm)*np.cos(ph),np.sin(tm)*np.sin(ph),-np.cos(tm)])
  et=np.array([np.cos(tm)*np.cos(ph),np.cos(tm)*np.sin(ph),np.sin(tm)]);ep=np.array([-np.sin(ph),np.cos(ph),0])
  E.SubElement(wk,'geom',type='box',size=fmt([RS*np.sin(tm)*np.pi/naz*1.12,RS*(tb-ta)/2*1.12,TT/2]),pos=fmt(C+(RS+TT/2)*r),quat=fmt(quat(np.c_[ep,et,r])),**WC)
rng=np.random.default_rng(1);foods=[];placed=[]
while len(foods)<N:
 p=np.array([rng.uniform(-.08,.08),rng.uniform(-.08,.08),rng.uniform(.03,.03+N*.0012)])
 if any(np.linalg.norm(p-q)<.022 for q in placed):continue
 placed.append(p);bn=f'f{len(foods)}';b=E.SubElement(wb,'body',name=bn,pos=fmt(p),quat=fmt(Rotation.random(random_state=rng.integers(1<<30)).as_quat()[[3,0,1,2]]));E.SubElement(b,'freejoint')
 E.SubElement(b,'geom',type='box',size='.0075 .0075 .0075',rgba='.85 .62 .42 1',density='1050',**(dict(friction='.5 .02 .01',condim='6',solref='.01 1') if STICKY else dict(friction='.4 .005 .0001',solref='.004 1')));foods.append(bn)   # STICKY: rolling/torsional friction as a proxy for sauce-coated pieces that do not roll
xml=E.tostring(root,encoding='unicode');m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m);FB=np.array([m.body(n).id for n in foods])
# pose sequence (wok frame -> world), as r15reach.wok_world with TIP=y
# tip about the rim centre (a level axis along y through the middle of the rim circle): the lip
# (right rim) sinks to its final spot LIPX from the plate centre, DROP above the plate rim, at A_MAX,
# while the wok is carried level and high enough before that
target=PC+[0,0,RIM_H+DROP]+np.array([LIPX,0,0])
def Ry(A):c,s=np.cos(np.radians(A)),np.sin(np.radians(A));return np.array([[c,0,s],[0,1,0],[-s,0,c]])
PIV=target-Ry(AMAX)@np.array([A_RIM,0,0])
def tipped(A):R=Ry(A);return PIV-R@np.array([0,0,DEPTH]),R
SEQ=[(0.,np.zeros(3),np.eye(3)),(1.5,np.zeros(3),np.eye(3)),(2.0,np.array([0,0,.04]),np.eye(3))]
o0,_=tipped(0.);SEQ.append((2.0+CARRY,o0,np.eye(3)))
t=2.0+CARRY;n=max(2,int(AMAX/15))
for A in np.linspace(0,AMAX,n+1)[1:]:
 t+=(AMAX/n)/RATE;SEQ.append((t,*tipped(A)))
 if STEP and abs(A-STEP)<1e-6:t+=1.5;SEQ.append((t,*tipped(A)))   # two-step tip: hold at STEP° so the load trickles out
t+=HOLD;SEQ.append((t,*tipped(AMAX)))
if SHAKE:
 for k in range(6):t+=1/6;SEQ.append((t,*tipped(AMAX+(6 if k%2==0 else -6))))
 t+=.2;SEQ.append((t,*tipped(AMAX)))
t+=AMAX/RATE;SEQ.append((t,o0,np.eye(3)));t+=1.;SEQ.append((t,o0,np.eye(3)))
def pose(tt):
 for (t0,p0,R0),(t1,p1,R1) in zip(SEQ,SEQ[1:]):
  if t0<=tt<=t1:
   s=(tt-t0)/max(t1-t0,1e-9);s=s*s*(3-2*s);Rs=Rotation.from_matrix(np.array([R0,R1]));from scipy.spatial.transform import Slerp
   return p0+(p1-p0)*s,Slerp([0,1],Rs)([s]).as_matrix()[0]
 return SEQ[-1][1],SEQ[-1][2]
frames=[];tt=0.;wid=m.body('wok').id;adr=m.jnt_qposadr[m.body_jntadr[wid]]
left_at={};phase=lambda tt:'settle' if tt<1.5 else 'carry' if tt<2.0+CARRY else 'tip';out_at_start=None
while tt<SEQ[-1][0]:
 p,R=pose(tt);d.mocap_pos[0]=p;d.mocap_quat[0]=quat(R)
 if tt==0:d.qpos[adr:adr+3]=p;d.qpos[adr+3:adr+7]=quat(R)
 mujoco.mj_step(m,d);tt+=DT
 if KV.get('FRAMES') and tt>=len(frames)/FPS:frames.append(d.qpos.copy())
 if out_at_start is None and tt>=1.5:out_at_start=set(i_ for i_,v_ in left_at.items())
 if int(tt/DT)%20==0:
  Rw_=d.xmat[wid].reshape(3,3);lc=(d.xpos[FB]-d.xpos[wid])@Rw_
  for i_ in np.where((np.hypot(lc[:,0],lc[:,1])>A_RIM+.01)|(lc[:,2]>DEPTH+.03))[0]:left_at.setdefault(int(i_),(round(tt,2),phase(tt)))
pos=d.xpos[FB];Rw=d.xmat[wid].reshape(3,3);loc=(pos-d.xpos[wid])@Rw;rr_w=np.hypot(loc[:,0],loc[:,1]);in_wok=(rr_w<A_RIM+.01)&(loc[:,2]<DEPTH+.03)&(loc[:,2]>-.03)
rp=np.hypot(pos[:,0]-PC[0],pos[:,1]-PC[1]);on_plate=(rp<PR+.005)&(pos[:,2]<ZC+.08)&~in_wok
res=dict(food=FOOD+('_sticky' if STICKY else ''),n=N,mu=MU,guard_m=GUARD or None,plate_r_m=PR,two_step_deg=STEP or None,lip_x_from_plate_centre_m=LIPX,lip_above_rim_m=DROP,plate_rim_m=RIM_H,plate_mu=PMU,carry_s=CARRY,tip_deg=AMAX,tip_rate_degps=RATE,hold_s=HOLD,shake=SHAKE,on_plate=int(on_plate.sum()),left_in_wok=int(in_wok.sum()),missed=int((~on_plate&~in_wok).sum()),
 on_plate_frac=round(float(on_plate.mean()),3),duration_s=round(SEQ[-1][0],1),
 left_wok_during={k_:sum(1 for v_ in left_at.values() if v_[1]==k_) for k_ in ('settle','carry','tip')},
 on_plate_frac_of_settled=round(float(on_plate.sum()/max(1,N-len(out_at_start or ()))),3),
 missed_offset_from_plate_m=dict(dx_mean=round(float((pos[~on_plate&~in_wok,0]-PC[0]).mean()),3) if (~on_plate&~in_wok).any() else None,dy_mean=round(float((pos[~on_plate&~in_wok,1]-PC[1]).mean()),3) if (~on_plate&~in_wok).any() else None,
  dist_p50=round(float(np.median(rp[~on_plate&~in_wok])),3) if (~on_plate&~in_wok).any() else None))
os.makedirs('results/r15',exist_ok=True);json.dump(res,open(f'results/r15/pour_{TAG}.json','w'),indent=1);print(json.dumps(res))
if KV.get('FRAMES'):np.save(f'results/r15/pour_{TAG}_frames.npy',np.array(frames));open(f'results/r15/pour_{TAG}.xml','w').write(xml)
