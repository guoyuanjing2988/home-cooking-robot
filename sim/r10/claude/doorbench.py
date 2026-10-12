"""R14 fridge-door bench (MuJoCo 3.2.5, noslip): the floating PGC with finger set P2
grasps a vertical bar handle with its jaws across the door normal (one finger between
the bar and the door, so pulling is form closure, not friction), breaks the magnetic
seal and swings the door open along the hinge arc, then pushes it shut.
Door: 0.60 m wide fresh-food door, hinge on the left (x = -0.30); door + bins + bottles
= DOORKG; seal = attractive force SEAL N at the handle edge decaying with a 2 mm gap
constant (magnetic gasket), hinge friction 0.5 N m, damping 0.5 N m s.
Usage: python doorbench.py [SEAL=40] [DOORKG=9] [MU=.5] [ANG=100] [RAD_ERR=0] [FRAMES=1]
RAD_ERR: error in the robot's assumed hinge-to-handle radius (m), to test compliance."""
import sys,os,json,numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
import fingers,foods
from fingers import JAW_Y
KV=dict(a.split('=',1) for a in sys.argv[1:])
SEAL=float(KV.get('SEAL',40));DKG=float(KV.get('DOORKG',9));MU=float(KV.get('MU',.5));ANG=np.radians(float(KV.get('ANG',100)));RERR=float(KV.get('RAD_ERR',0))
DT=.0005;FPS=30;TAG=f"door_s{SEAL:g}_m{DKG:g}_mu{MU:g}_a{np.degrees(ANG):.0f}"+(f'_re{RERR:+.3f}' if RERR else '')+KV.get('TAG','')
def fmt(v):return ' '.join(f'{float(x):.9g}' for x in v)
W,HZ=.60,(.80,1.70);HX=-.30;BAR_X=.26;BAR_Y=-.09;BAR_R=.0125;BAR_Z=(1.15,1.45)
root=E.Element('mujoco',model='doorbench');E.SubElement(root,'compiler',angle='radian',autolimits='true')
E.SubElement(root,'option',timestep=str(DT),cone='elliptic',impratio='10',noslip_iterations='10')
v=E.SubElement(root,'visual');E.SubElement(v,'global',offwidth='1280',offheight='720');E.SubElement(v,'headlight',ambient='.45 .45 .45',diffuse='.5 .5 .5')
wb=E.SubElement(root,'worldbody');eq=E.SubElement(root,'equality');act=E.SubElement(root,'actuator')
E.SubElement(wb,'light',pos='.5 -1.5 2.5',dir='-.2 .6 -1',diffuse='.5 .5 .5')
E.SubElement(wb,'geom',name='floor',type='plane',size='3 3 .01',rgba='.8 .78 .75 1')
# fridge cabinet (behind the door plane y = 0)
E.SubElement(wb,'geom',name='fridge',type='box',pos=fmt([0,.33,.85]),size=fmt([W/2,.32,.85]),rgba='.92 .93 .95 1',contype='1',conaffinity='5')
# door: hinge at the left front corner; panel 50 mm thick in front of y = 0
door=E.SubElement(wb,'body',name='door',pos=fmt([HX,0,0]))
E.SubElement(door,'joint',name='hinge',type='hinge',axis='0 0 -1',range=f'0 {np.radians(130)}',damping='.5',frictionloss='.5',armature='.05')
E.SubElement(door,'geom',name='door_panel',type='box',pos=fmt([W/2,-.025,sum(HZ)/2]),size=fmt([W/2,.025,(HZ[1]-HZ[0])/2]),rgba='.85 .87 .9 1',contype='1',conaffinity='5',mass=str(DKG))
for z in BAR_Z:E.SubElement(door,'geom',name=f'bar_post{z}',type='box',pos=fmt([BAR_X-HX,(BAR_Y-.05)/2,z]),size=fmt([.008,(-.05-BAR_Y)/2,.008]),rgba='.7 .7 .72 1',contype='1',conaffinity='5',mass='.05')
E.SubElement(door,'geom',name='bar',type='cylinder',pos=fmt([BAR_X-HX,BAR_Y,sum(BAR_Z)/2]),size=fmt([BAR_R,(BAR_Z[1]-BAR_Z[0])/2]),rgba='.7 .7 .72 1',contype='1',conaffinity='7',friction='0 0 0',condim='4',mass='.2')
# gripper (same construction as foodbench.py), finger set P2, jaws along the door normal
d_=dict(foods.SETS['P2']);Dd,c=d_['D'],d_['c'];FR=f'{MU} {.004*MU:.6g} .0001';STROKE=.05
gb=E.SubElement(wb,'body',name='G_tool',pos='0 -.5 1.3');E.SubElement(gb,'freejoint')
GC=dict(contype='4',conaffinity='0',friction=FR,solref='.002 1')
E.SubElement(gb,'geom',name='G_housing',type='box',pos=fmt([-Dd-.06925,0,c]),size='.06925 .0375 .0375',mass='1',rgba='.25 .27 .3 1',**GC)
for jn,s in (('G_jaw_minus',-1),('G_jaw_plus',1)):
 jb=E.SubElement(gb,'body',name=jn,pos=fmt([.015-Dd,s*JAW_Y,c]));E.SubElement(jb,'joint',name=jn,type='slide',axis=fmt([0,s,0]),range=f'0 {STROKE/2}',damping='100',armature='.01')
 E.SubElement(jb,'inertial',pos='0 0 0',mass='.05',diaginertia='1e-5 1e-5 1e-5');fingers.dyn_parts(root,jb,s,d_,FR)
for g in gb.iter('geom'):g.set('solref','.002 1')
E.SubElement(wb,'body',name='G_mocap',mocap='true',pos='0 -.5 1.3')
# arm in impedance mode: a compliant weld (about 10 mm / 100 N) instead of a rigid one
E.SubElement(eq,'weld',body1='G_mocap',body2='G_tool',solref=KV.get('WELD','.02 1'))
E.SubElement(eq,'joint',joint1='G_jaw_minus',joint2='G_jaw_plus',polycoef='0 1 0 0 0')
for jn in ('G_jaw_minus','G_jaw_plus'):E.SubElement(act,'position',name='a_'+jn,joint=jn,kp='50000',forcerange='-40 40',ctrlrange='-.01 .035')
m=mujoco.MjModel.from_xml_string(E.tostring(root,encoding='unicode'));d=mujoco.MjData(m)
HJ=m.joint('hinge').id;HD=m.jnt_dofadr[HJ];HQ=m.jnt_qposadr[HJ];MOC=0;TOOL=m.body('G_tool').id;BAR=m.geom('bar').id
GB={b for b in range(m.nbody) if m.body(b).name.startswith('G_')};JQ=[m.jnt_qposadr[m.joint(n).id] for n in ('G_jaw_minus','G_jaw_plus')]
RAD=np.hypot(BAR_X-HX,BAR_Y)  # hinge axis to bar centre (m)
def bar_pos(th,rad=RAD):
 a0=np.arctan2(BAR_Y,BAR_X-HX);return np.array([HX+rad*np.cos(a0-th),rad*np.sin(a0-th),sum(BAR_Z)/2])  # opening = rotation about -z
# tool frame: approach +x (from the free-edge side, along the door face), jaws along the
# door normal (tool y = world -y at th=0), pads span z. Rotates with the door.
def tool_R(th):
 R0=np.array([[1,0,0],[0,-1,0],[0,0,-1]]).T@np.eye(3)
 R0=np.column_stack([[1,0,0],[0,-1,0],[0,0,-1]])
 return Rotation.from_euler('z',th).as_matrix()@R0
def set_mocap(p,R):d.mocap_pos[MOC]=p;d.mocap_quat[MOC]=Rotation.from_matrix(R).as_quat()[[3,0,1,2]]
log=dict(F=[],slip=[],th=[],seal=[]);frames=[];t=[0.]
def seal_torque():
 g=max(0.,d.qpos[HQ])*(W);return -SEAL*W*np.exp(-g/.002) if g<.02 else 0.
def contacts():
 f6=np.zeros(6);F=0.
 for i in range(d.ncon):
  con=d.contact[i];b1,b2=m.geom_bodyid[con.geom1],m.geom_bodyid[con.geom2]
  if ((con.geom1==BAR) and b2 in GB) or ((con.geom2==BAR) and b1 in GB):mujoco.mj_contactForce(m,d,i,f6);F+=abs(f6[0])
 return F
def step(p,R,jaw):
 set_mocap(p,R);d.ctrl[:]=jaw;d.qfrc_applied[HD]=seal_torque();mujoco.mj_step(m,d);t[0]+=DT
 if KV.get('FRAMES') and t[0]>=len(frames)/FPS:frames.append(d.qpos.copy())
def run(T,f,jaw,rec=False):
 n=int(T/DT)
 for k in range(n):
  p,R=f((k+1)/n);step(p,R,jaw(k/n) if callable(jaw) else jaw)
  if rec:
   bar=d.geom_xpos[BAR];Rt=d.xmat[TOOL].reshape(3,3);rel=Rt.T@(bar-d.xpos[TOOL])
   log['F'].append(contacts());log['slip'].append(rel);log['th'].append(d.qpos[HQ])
OPEN,CLOSE=.006,-.004  # 39 mm gap around the 25 mm bar: the inner finger stays 8 mm off the door face
# 1. approach: start 12 cm along +x beyond the bar (outside the door edge), move in
p_g=bar_pos(0.);R=tool_R(0.)@np.diag([-1,-1,1]);p_pre=p_g+np.array([.15,0,0])  # tool x (approach) = -x world
d.qpos[m.jnt_qposadr[m.body_jntadr[TOOL]]:][:3]=p_pre;d.qpos[m.jnt_qposadr[m.body_jntadr[TOOL]]+3:][:4]=Rotation.from_matrix(R).as_quat()[[3,0,1,2]]
d.qpos[JQ]=OPEN;mujoco.mj_forward(m,d)
# tool x = approach must point from the gripper toward the bar: approach -x world here
run(.6,lambda s:(p_pre,R),OPEN)
run(1.5,lambda s:(p_pre+(p_g-p_pre)*s,R),OPEN)
run(.6,lambda s:(p_g,R),lambda s:OPEN+(CLOSE-OPEN)*min(1,s*2))
ref=None
if KV.get('PREVIEW'):
 from PIL import Image
 r=mujoco.Renderer(m,480,640);cam=mujoco.MjvCamera();cam.lookat[:]=d.geom_xpos[BAR];ims=[]
 for az,el,ds in ((-90,-10,.6),(0,-60,.6),(-140,-20,.9)):cam.azimuth,cam.elevation,cam.distance=az,el,ds;r.update_scene(d,cam);ims.append(r.render().copy())
 Image.fromarray(np.concatenate(ims,1)).save(KV['PREVIEW'])
 f6=np.zeros(6)
 for i in range(d.ncon):
  con=d.contact[i];mujoco.mj_contactForce(m,d,i,f6);print(m.geom(con.geom1).name,m.geom(con.geom2).name,round(f6[0],1),round(con.dist*1000,1))
 print('jaw q',d.qpos[JQ],'tool',d.xpos[TOOL].round(3),'bar',d.geom_xpos[BAR].round(3));raise SystemExit
# 2. swing along the arc to ANG (trapezoid in angle, 1.2 s/rad), with the assumed radius RAD+RERR
T=max(1.5,1.2*ANG);rad=RAD+RERR
def arc(s):
 u=3*s*s-2*s**3;th=ANG*u;return bar_pos(th,rad),Rotation.from_euler('z',-th).as_matrix()@R
run(T,arc,CLOSE,rec=True);th_open=float(d.qpos[HQ])
run(.5,lambda s:arc(1.),CLOSE,rec=True)
# 3. close: swing back to 0 (the gripper still holds the bar), release, retreat
run(T,lambda s:arc(1-s),CLOSE,rec=True);run(.8,lambda s:arc(0.),CLOSE,rec=True)
th_closed=float(d.qpos[HQ])
run(.5,lambda s:arc(0.),OPEN)
F=np.array(log['F']);sl=np.array(log['slip']);sl=1000*np.linalg.norm(sl-sl[0],axis=1)
res=dict(seal_N=SEAL,door_kg=DKG,mu=MU,target_deg=round(np.degrees(ANG)),radius_err_m=RERR,opened_deg=round(np.degrees(th_open),1),closed_deg=round(np.degrees(th_closed),2),
 max_grip_contact_N=round(float(F.max()),1),handle_shift_in_grip_mm=round(float(sl.max()),1),ok=bool(np.degrees(th_open)>np.degrees(ANG)-5 and np.degrees(th_closed)<1.0 and sl.max()<15))
os.makedirs('results/r14',exist_ok=True);json.dump(res,open(f'results/r14/{TAG}.json','w'),indent=1);print(json.dumps(res))
if KV.get('FRAMES'):np.save(f'results/r14/{TAG}_frames.npy',np.array(frames));open(f'results/r14/{TAG}.xml','w',encoding='utf-8').write(E.tostring(root,encoding='unicode'))
