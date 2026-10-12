"""R14 4-compartment pour box (分格料盒): one pick, compartments empty in order as the
arm rolls the box over the wok. Compartments sit one behind the other along the pour
direction; each is held back by a divider taller than the one in front, so compartment
k only spills once the tilt passes about atan(h_(k-1) / w). The arm rolls in steps
(tilt, hold, tilt ...), so the time between additions is set by the arm, >= ~1.5 s.
Contents are modelled as granules (spheres): salt/sugar/MSG-sized clumps (r 2.5 mm),
or lumps (r 6 mm: chopped aromatics). Liquids are not modelled (no fluid solver).
Usage: python pourbox.py [R=.0025] [N=30] [STEPS=20,45,65,85] [HOLD=1.5] [FRAMES=1]"""
import sys,os,json,numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
KV=dict(a.split('=',1) for a in sys.argv[1:])
R=float(KV.get('R',.0025));N=int(KV.get('N',30));STEPS=[float(x) for x in KV.get('STEPS','20,45,65,85').split(',')];HOLD=float(KV.get('HOLD',1.5))
DT=.0005;FPS=30;TAG=f"pourbox_r{R*1000:g}_n{N}_s{'-'.join(f'{s:g}' for s in STEPS)}"+KV.get('TAG','')
def fmt(v):return ' '.join(f'{float(x):.9g}' for x in v)
W,L,HB=.07,.12,.06;WK=.03;LIP=.006;DIV=[.018,.032,.046]   # box width, length (pour direction), height; compartment depth; lip and divider heights
COL=[(.95,.85,.2,1),(.85,.3,.2,1),(.3,.6,.9,1),(.4,.8,.4,1)]
root=E.Element('mujoco');E.SubElement(root,'compiler',angle='radian',autolimits='true')
E.SubElement(root,'option',timestep=str(DT),cone='elliptic',impratio='5')
E.SubElement(root,'size',memory='64M')
v=E.SubElement(root,'visual');E.SubElement(v,'global',offwidth='1280',offheight='720');E.SubElement(v,'headlight',ambient='.45 .45 .45',diffuse='.5 .5 .5')
wb=E.SubElement(root,'worldbody');eq=E.SubElement(root,'equality')
E.SubElement(wb,'light',pos='.3 -.5 1.5',dir='-.2 .4 -1',diffuse='.5 .5 .5')
E.SubElement(wb,'geom',name='floor',type='plane',size='2 2 .01',rgba='.82 .8 .78 1')
# wok: 32 cm bowl approximated by a ring of tilted slabs + floor, rim at z = .10
wk=E.SubElement(wb,'body',name='wok',pos='0 0 0');E.SubElement(wk,'geom',type='cylinder',size='.09 .002',pos='0 0 .02',rgba='.15 .15 .15 1')
for k in range(24):
 a=2*np.pi*k/24;g=E.SubElement(wk,'geom',type='box',size=fmt([.004,.16*np.tan(np.pi/24),.06]),pos=fmt([.125*np.cos(a),.125*np.sin(a),.06]),rgba='.15 .15 .15 1')
 g.set('quat',fmt((Rotation.from_euler('z',a)*Rotation.from_euler('y',-np.radians(35))).as_quat()[[3,0,1,2]]))
# box: pour lip at local y = 0 (front), back at y = L; it rotates about its lip edge
# the box is a free body welded to a mocap target (an arm holding it): it has real
# velocity, so contacts with the granules are resolved properly while it rolls
E.SubElement(wb,'body',name='target',pos='0 -.02 .20',mocap='true')
bx=E.SubElement(wb,'body',name='box',pos='0 -.02 .20');E.SubElement(bx,'freejoint')
E.SubElement(eq,'weld',body1='target',body2='box',solref='.002 1')
BC=dict(rgba='.88 .9 .93 .55',friction='.5 .005 .0001',density='800')
E.SubElement(bx,'geom',type='box',size=fmt([W/2,L/2,.002]),pos=fmt([0,L/2,-.002]),**BC)
for s in (-1,1):E.SubElement(bx,'geom',type='box',size=fmt([.002,L/2,HB/2]),pos=fmt([s*(W/2+.002),L/2,HB/2]),**BC)
E.SubElement(bx,'geom',type='box',size=fmt([W/2+.004,.002,HB/2]),pos=fmt([0,L+.002,HB/2]),**BC)
E.SubElement(bx,'geom',type='box',size=fmt([W/2,.002,LIP/2]),pos=fmt([0,-.002,LIP/2]),**BC)
for i,h in enumerate(DIV):E.SubElement(bx,'geom',type='box',size=fmt([W/2,.0015,h/2]),pos=fmt([0,WK*(i+1),h/2]),**BC)
# granules in each compartment, layered without overlap
rng=np.random.default_rng(0);bodies=[]
for k in range(4):
 nx=int((W-.004)//(2.2*R));ny=int((WK-.006)//(2.2*R))
 for i in range(N):
  ix,iy,iz=i%nx,(i//nx)%ny,i//(nx*ny)
  p=[-W/2+.002+R*1.1+ix*2.2*R,WK*k+.003+R*1.1+iy*2.2*R,R*1.1+iz*2.2*R]
  b=E.SubElement(wb,'body',name=f'g{k}_{i}',pos=fmt(np.array([0,-.02,.20])+p));E.SubElement(b,'freejoint')
  E.SubElement(b,'geom',type='sphere',size=str(R),density='1200',rgba=fmt(COL[k]),friction='.4 .005 .0001',solref='.004 1');bodies.append((k,b.get('name')))
m=mujoco.MjModel.from_xml_string(E.tostring(root,encoding='unicode'));d=mujoco.MjData(m)
BID=[(k,m.body(n).id) for k,n in bodies];P0=np.array([0,-.02,.20])
def set_tilt(deg):
 # +x tilt: the back rises, the lip (y = 0) goes down
 q=Rotation.from_euler('x',np.radians(deg)).as_quat()[[3,0,1,2]];d.mocap_quat[0]=q;d.mocap_pos[0]=P0
t=0.;frames=[];left={};landed={}
BOX=m.body('box').id
def in_box(p):
 Rb=d.xmat[BOX].reshape(3,3);l=Rb.T@(p-d.xpos[BOX]);return -.004<=l[1]<=L+.004 and -.004<=l[2]<=HB+.004 and abs(l[0])<=W/2+.004
cur=[0.]
def step(n):
 global t
 for _ in range(n):
  set_tilt(cur[0]);mujoco.mj_step(m,d);t+=DT
  if KV.get('FRAMES') and t>=len(frames)/FPS:frames.append(d.qpos.copy())
 for k,b in BID:
  p=d.xpos[b]
  if b not in left and not in_box(p):left[b]=(k,t,cur[0])
step(int(.5/DT))
for s in STEPS:
 a0=cur[0];n=int(abs(s-a0)/60/DT)+1   # roll at 60 deg/s to the step, then hold
 for i in range(n):cur[0]=a0+(s-a0)*(i+1)/n;step(1)
 step(int(HOLD/DT))
step(int(1.0/DT))
res=dict(r_mm=R*1000,n_per_compartment=N,steps_deg=STEPS,hold_s=HOLD,compartments=[])
for k in range(4):
 ts=[v_[1] for b,v_ in left.items() if v_[0]==k];angs=[v_[2] for b,v_ in left.items() if v_[0]==k]
 ins=[b for kk,b in BID if kk==k and b in left and np.hypot(*d.xpos[b][:2])<.16 and d.xpos[b][2]<.12]
 res['compartments'].append(dict(released=len(ts),of=N,t_first=round(min(ts),2) if ts else None,t_last=round(max(ts),2) if ts else None,
  tilt_first_deg=round(min(angs),1) if angs else None,tilt_last_deg=round(max(angs),1) if angs else None,in_wok=len(ins)))
c=res['compartments'];order_ok=all(c[k]['t_first'] is not None and c[k+1]['t_first'] is not None and c[k+1]['t_first']>c[k]['t_last']-.05 for k in range(3))
res['all_released']=all(x['released']==N for x in c);res['in_order']=bool(order_ok);res['in_wok_frac']=round(sum(x['in_wok'] for x in c)/(4*N),3)
os.makedirs('results/r14',exist_ok=True);json.dump(res,open(f'results/r14/{TAG}.json','w'),indent=1);print(json.dumps(res))
if KV.get('FRAMES'):np.save(f'results/r14/{TAG}_frames.npy',np.array(frames));open(f'results/r14/{TAG}.xml','w').write(E.tostring(root,encoding='unicode'))
