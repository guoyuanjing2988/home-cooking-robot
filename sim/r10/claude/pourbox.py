"""R14 rotary 4-compartment pour drum (分格转筒料盒): one pick, compartments empty one
after another as the arm rolls its wrist over the wok.
The drum (Ø80 x 140 mm, axis = the wrist roll axis) has 4 compartments along its axis.
Each has a 40° slot in the wall; the slots are staggered at -75°, -25°, +25°, +75° from
the top, so while carried upright every slot faces up and contents up to half full stay
in. Rolling by alpha brings slot k down at alpha ~ 180 - phi_k (105, 155, 205, 255°),
so compartments release in a fixed order whatever the contents (granules, lumps; liquids
too, though they are not modelled here). A tiered-divider box was tried first and
rejected (pourbox_tiered_rejected.py): granules behind a divider only pass it once the
box is past vertical, so all compartments came out together.
Contents: spheres R (2.5 mm salt/sugar clumps; 6 mm chopped aromatics), N per compartment.
Usage: python pourbox.py [R=.0025] [N=30] [STEPS=120,170,220,270] [HOLD=1.5] [FRAMES=1]"""
import sys,os,json,numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
KV=dict(a.split('=',1) for a in sys.argv[1:])
R=float(KV.get('R',.0025));N=int(KV.get('N',30));STEPS=[float(x) for x in KV.get('STEPS','120,170,220,270').split(',')];HOLD=float(KV.get('HOLD',1.5))
DT=.0005;FPS=30;TAG=f"pourdrum_r{R*1000:g}_n{N}_s{'-'.join(f'{s:g}' for s in STEPS)}"+KV.get('TAG','')
def fmt(v):return ' '.join(f'{float(x):.9g}' for x in v)
RD,LC,NC=.04,.035,4;PHI=[-75,-25,25,75];SLOT=40.;NS=36   # drum radius, compartment length, slot angles from the top (deg), slot width, wall segments
COL=[(.95,.85,.2,1),(.85,.3,.2,1),(.3,.6,.9,1),(.4,.8,.4,1)]
root=E.Element('mujoco');E.SubElement(root,'compiler',angle='radian',autolimits='true')
E.SubElement(root,'option',timestep=str(DT),cone='elliptic',impratio='5');E.SubElement(root,'size',memory='64M')
v=E.SubElement(root,'visual');E.SubElement(v,'global',offwidth='1280',offheight='720');E.SubElement(v,'headlight',ambient='.45 .45 .45',diffuse='.5 .5 .5')
wb=E.SubElement(root,'worldbody');eq=E.SubElement(root,'equality')
E.SubElement(wb,'light',pos='.3 -.5 1.5',dir='-.2 .4 -1',diffuse='.5 .5 .5')
E.SubElement(wb,'geom',name='floor',type='plane',size='2 2 .01',rgba='.82 .8 .78 1')
# wok: thick floor and wall slabs (thin plates let fast granules tunnel through soft contacts)
wk=E.SubElement(wb,'body',name='wok');E.SubElement(wk,'geom',type='cylinder',size='.10 .012',pos='0 0 .01',rgba='.15 .15 .15 1')
for k in range(24):
 a=2*np.pi*k/24;g=E.SubElement(wk,'geom',type='box',size=fmt([.012,.17*np.tan(np.pi/24),.06]),pos=fmt([.125*np.cos(a),.125*np.sin(a),.06]),rgba='.15 .15 .15 1')
 g.set('quat',fmt((Rotation.from_euler('z',a)*Rotation.from_euler('y',np.radians(35))).as_quat()[[3,0,1,2]]))
P0=np.array([0.,0.,.22])
E.SubElement(wb,'body',name='target',pos=fmt(P0),mocap='true')
dr=E.SubElement(wb,'body',name='drum',pos=fmt(P0));E.SubElement(dr,'freejoint')
E.SubElement(eq,'weld',body1='target',body2='drum',solref='.002 1')
BC=dict(rgba='.88 .9 .93 .5',friction='.5 .005 .0001',density='800')
L=NC*LC;x0=-L/2
for c in range(NC):
 xc=x0+LC*(c+.5)
 for j in range(NS):  # wall segment at angle th from the top (z), around the x axis; skip the slot
  th=-180+360*(j+.5)/NS
  if abs(((th-PHI[c])+180)%360-180)<SLOT/2:continue
  t=np.radians(th);p=[xc,-RD*np.sin(t),RD*np.cos(t)]
  g=E.SubElement(dr,'geom',type='box',size=fmt([LC/2,RD*np.pi/NS*1.05,.0015]),pos=fmt(p),**BC);g.set('quat',fmt(Rotation.from_euler('x',t).as_quat()[[3,0,1,2]]))
for i in range(NC+1):E.SubElement(dr,'geom',type='cylinder',size=fmt([RD+.002,.0015]),pos=fmt([x0+LC*i,0,0]),quat=fmt(Rotation.from_euler('y',np.pi/2).as_quat()[[3,0,1,2]]),**BC)
# knob on the -x end cap for the gripper (form fit); the grasp itself is not simulated here
E.SubElement(dr,'geom',type='box',size='.015 .015 .015',pos=fmt([x0-.016,0,0]),rgba='.95 .6 .1 1',density='800')
bodies=[]
for c in range(NC):
 xc=x0+LC*(c+.5);i=0
 # fill the lower part of the compartment on a grid (no initial overlap)
 for zz in np.arange(-RD+.003+R,0,2.2*R):
  for yy in np.arange(-RD+R,RD-R,2.2*R):
   for xx in np.arange(xc-LC/2+.003+R,xc+LC/2-.003-R+1e-9,2.2*R):
    if i>=N or np.hypot(yy,zz)>RD-.003-R:continue
    b=E.SubElement(wb,'body',name=f'g{c}_{i}',pos=fmt(P0+[xx,yy,zz]));E.SubElement(b,'freejoint')
    E.SubElement(b,'geom',type='sphere',size=str(R),density='1200',rgba=fmt(COL[c]),friction='.4 .005 .0001',solref='.004 1');bodies.append((c,b.get('name')));i+=1
m=mujoco.MjModel.from_xml_string(E.tostring(root,encoding='unicode'));d=mujoco.MjData(m)
BID=[(c,m.body(n).id) for c,n in bodies];DRUM=m.body('drum').id
cur=[0.];t=[0.];frames=[];left={}
def in_drum(p):
 Rb=d.xmat[DRUM].reshape(3,3);l=Rb.T@(p-d.xpos[DRUM]);return abs(l[0])<=L/2+.003 and np.hypot(l[1],l[2])<=RD+.004
def step(n):
 for _ in range(n):
  d.mocap_quat[0]=Rotation.from_euler('x',np.radians(cur[0])).as_quat()[[3,0,1,2]];d.mocap_pos[0]=P0
  mujoco.mj_step(m,d);t[0]+=DT
  if KV.get('FRAMES') and t[0]>=len(frames)/FPS:frames.append(d.qpos.copy())
  for c,b in BID:
   if b not in left and not in_drum(d.xpos[b]):left[b]=(c,t[0],cur[0])
step(int(.5/DT))
for s in STEPS:
 a0=cur[0];n=int(abs(s-a0)/90/DT)+1   # wrist roll at 90 deg/s, then hold
 for i in range(n):cur[0]=a0+(s-a0)*(i+1)/n;step(1)
 step(int(HOLD/DT))
step(int(1./DT))
res=dict(r_mm=R*1000,n_per_compartment=[sum(1 for c,_ in BID if c==k) for k in range(NC)],slots_deg=PHI,steps_deg=STEPS,hold_s=HOLD,compartments=[])
for k in range(NC):
 ts=[v_[1] for b,v_ in left.items() if v_[0]==k];ang=[v_[2] for b,v_ in left.items() if v_[0]==k]
 ins=[b for c,b in BID if c==k and b in left and np.hypot(*d.xpos[b][:2])<.16 and d.xpos[b][2]<.12]
 res['compartments'].append(dict(released=len(ts),of=res['n_per_compartment'][k],t_first=round(min(ts),2) if ts else None,t_last=round(max(ts),2) if ts else None,
  roll_first_deg=round(min(ang),1) if ang else None,roll_last_deg=round(max(ang),1) if ang else None,in_wok=len(ins)))
c=res['compartments']
res['all_released']=all(x['released']==x['of'] for x in c);res['in_order']=bool(all(c[k]['t_first'] is not None and c[k+1]['t_last'] is not None and c[k]['t_first']>=c[k+1]['t_last']-.05 for k in range(NC-1)))  # 4, 3, 2, 1
res['in_wok_frac']=round(sum(x['in_wok'] for x in c)/max(1,sum(res['n_per_compartment'])),3)
os.makedirs('results/r14',exist_ok=True);json.dump(res,open(f'results/r14/{TAG}.json','w'),indent=1);print(json.dumps(res))
res['release_sequence']='compartment 4 (slot +75°) first, then 3, 2, 1: fill in that order'
if KV.get('FRAMES'):np.save(f'results/r14/{TAG}_frames.npy',np.array(frames));open(f'results/r14/{TAG}.xml','w').write(E.tostring(root,encoding='unicode'))
