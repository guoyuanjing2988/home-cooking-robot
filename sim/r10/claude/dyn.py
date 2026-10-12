"""Rigid-body dynamics check of a closed chain (handling steps only).
The cart and arm follow the checked path exactly (prescribed joint motion, as an
industrial controller would track it) with trapezoidal timing: leading arm joint
0.8 rad/s, base 0.25 m/s, 0.5 s ramps (1.6 rad/s^2, 0.5 m/s^2), stopping at the end
of every stroke. The jaws are synchronised (equality) and force-limited (PGC-140-50:
40..140 N per jaw, force mode). The food is a free rigid body with mass and friction; it is never welded.
Not simulated: cutting, peeling, washing water, tomato softness, controller error.
Usage: python dyn.py <preset> [mu=0.6] [grip_N=40]
R12 options (environment): FINGER=<fingers.DESIGNS key> replaces the gripper's fingers
(default: the preset's own design, else stock); ITEM_D / ITEM_M item diameter (m) /
mass (kg); GRIP=pos:<squeeze m> drives the jaws in position mode (compliant pads,
force set by the squeeze, PGC 140 N cap) instead of force mode."""
import sys,json,time,numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
import chain
from scene import build,TOMATO_DZ,tomato_dz
import fingers,os
P=sys.argv[1];MU=float(sys.argv[2]) if len(sys.argv)>2 else .6;FG=float(sys.argv[3]) if len(sys.argv)>3 else 40.
ITEM='tomato' if chain.config(P).get('r11_tomato') else 'carrot'
GRIP=os.environ.get('GRIP','');SQ=float(GRIP.split(':')[1]) if GRIP.startswith('pos:') else 0.;OPEN=.025;SQUEEZE=.006;DT=.0005;FPS=30
MASS={'tomato':.15,'carrot':.12}
d_=json.load(open(f'results/chain_{P}/full.json'));Q=np.array(d_['path']);L=d_['labels']
runs=[];i=0
while i<len(L):
 j=i
 while j+1<len(L) and L[j+1]==L[i]:j+=1
 runs.append((L[i],np.array(Q[i:j+1])));i=j+1
def held(label):
 g,_,s=label.partition(':')
 if g.startswith('C'):return ITEM if not (ITEM=='tomato' and g=='C3') else None
 if s in ('chute_retreat','tomato_release_retreat','release','return'):return None
 return chain.target(P,s)['held']
# Script entries: (kind, label, path, seconds, gripping) with kind move/release/grasp/hold.
# Tomato stops after its release on the blade plate (pressing = cutting, not
# simulable); the carrot runs to the chute drop, with the checked peel release /
# return inserted as in video.py.
script=[('hold','start',runs[0][1][:1],.6,True)]
for k,(lab,qs) in enumerate(runs):
 h=held(lab)
 if h not in (ITEM,None):break
 g=h==ITEM;prev=script[-1][4]
 if lab=='G3:peel_retrieve':
  load=runs[k-1][1];op=np.c_[load[:,:9],np.full((len(load),2),OPEN)]
  script+=[('release','G3:release',load[-1:],.5,False),('move','G3:release',op[::-1],0,False),('hold','peeling (not simulated)',op[:1],1.,False),
   ('move','G3:return',op,0,False),('grasp','G3:regrasp',qs[:1],.6,True)]
 elif prev and not g:script.append(('release',lab,qs[:1],.5,False))
 script.append(('move',lab,qs,0,g))
 if ITEM=='tomato' and lab=='GT3:tomato_release_retreat':break
script.append(('hold','settle',script[-1][2][-1:],1.5,script[-1][4]))
# --- model: no welded item; free food body; margins 0; robot touches only the food
cfg=chain.chain_cfg(P);tree,meta=build(cfg,None);root=tree.getroot()
for g in root.iter('geom'):
 g.set('margin','0')
 if g.get('name','').startswith('R_'):g.set('contype','2');g.set('conaffinity','0')
for g in list(root.iter('geom')):
 if g.get('name') in ('raw_tomato','raw_carrot'):
  for par in root.iter():
   if g in list(par):par.remove(g)
for dflt in root.iter('default'):
 for g in dflt.findall('geom'):g.set('margin','0')
import os
opt=root.find('option');opt.set('timestep',str(DT));opt.set('cone','elliptic');opt.set('impratio','10')
if os.environ.get('NOSLIP'):opt.set('noslip_iterations',os.environ['NOSLIP'])  # removes soft-contact creep
# initial food pose = the welded pose of the checked model at the first state
tm,_=build(cfg,ITEM);mh=mujoco.MjModel.from_xml_string(E.tostring(tm.getroot(),encoding='unicode'));dh=mujoco.MjData(mh)
dh.qpos[:]=Q[0];mujoco.mj_kinematics(mh,dh);gh=mh.geom(f'R_held_{ITEM}').id;p0=dh.geom_xpos[gh].copy();R0=dh.geom_xmat[gh].reshape(3,3)
if ITEM=='carrot':
 ax=R0[:,int(np.argmax(mh.geom_aabb[gh][3:]))];z=np.array([0,0,1.])
 Rb=Rotation.align_vectors([ax],[z])[0].as_matrix();gtype,gsize='capsule','.0175 .0625'
else:Rb=R0;gtype,gsize='ellipsoid','.035 .035 .03'
ID=float(os.environ['ITEM_D']) if os.environ.get('ITEM_D') else None  # item diameter override (m)
if ID:gsize=f'{ID/2} .0625' if ITEM=='carrot' else f'{ID/2} {ID/2} {ID/2*6/7}'
if os.environ.get('ITEM_M'):MASS[ITEM]=float(os.environ['ITEM_M'])
# a larger or smaller item still rests on its support: its centre moves by the change in half height
if ID:p0=p0+[0,0,(ID/2-.0175) if ITEM=='carrot' else (ID/2-.035)*6/7]
FINGER=os.environ.get('FINGER') or cfg.get('finger')
MUT=.004*MU  # torsional friction = (2/3) mu a, contact patch radius a ~ 6 mm (Hertz, tomato at 40 N)
FR=f'{MU} {MUT:.6g} .0001'
import os
SHIFT=np.array([float(x) for x in os.environ.get('FOOD_SHIFT','0,0,0').split(',')])  # food offset in the tool frame (what-if grasps)
if SHIFT.any():
 mt=dh.xmat[mh.body('R_tool').id].reshape(3,3);p0=p0+mt@SHIFT
q0=Rotation.from_matrix(Rb).as_quat()[[3,0,1,2]]
wb=root.find('worldbody');b=E.SubElement(wb,'body',name='food',pos=' '.join(map(str,p0)),quat=' '.join(map(str,q0)))
E.SubElement(b,'freejoint',name='food_free')
# The food carries no friction of its own: MuJoCo uses the larger coefficient of a
# pair, so the pad (gripper) values set the grip and the scene's own values the rest.
E.SubElement(b,'geom',name=f'raw_{ITEM}',type=gtype,size=gsize,mass=str(MASS[ITEM]),friction='0 0 0',condim='4',
 solref='.004 1',contype='1',conaffinity='7',margin='0',rgba='.9 .3 .2 1')
# Floating gripper (standard grasp-simulation setup): a copy of the R_tool subtree is a
# free body welded stiffly to a mocap target that follows the planned tool pose. The
# copy carries the gripper mass, the synchronised force-mode jaws and all food contacts.
# The cart and arm are set kinematically for display only (their clearance to the food
# is already checked), so no artificial inertia is needed.
import copy
def fmt(v):return ' '.join(f'{float(x):.9g}' for x in v)
RT0=mh.body('R_tool').id;pt0=dh.xpos[RT0].copy();qt0=dh.xquat[RT0].copy()
# Item centre in the planning tool frame; a design gripper has its TCP at the item centre.
p_item=dh.xmat[RT0].reshape(3,3).T@(dh.geom_xpos[gh]-dh.xpos[RT0])  # welded (unshifted) item centre
if FINGER and FINGER!=cfg.get('finger'):
 src=build(dict(cfg,finger=FINGER,tomato_dz=0.),None)[0].getroot();OFF=p_item
else:src=root;OFF=np.zeros(3) if not FINGER else p_item
G=copy.deepcopy(src.find(".//body[@name='R_tool']"))
for el in G.iter():
 for k in ('name','joint'):
  if el.get(k,'').startswith('R_'):el.set(k,'G_'+el.get(k)[2:])
 if el.tag=='geom':el.set('contype','4');el.set('conaffinity','0');el.set('margin','0');el.set('friction',FR)  # gripper touches only the food
pt0=pt0+dh.xmat[RT0].reshape(3,3)@OFF
D_=fingers.get(dict(finger=FINGER)) if FINGER else None
if D_:
 for jn,s_ in (('G_jaw_minus',-1),('G_jaw_plus',1)):fingers.dyn_parts(root,G.find(f".//body[@name='{jn}']"),s_,D_,FR)
G.set('pos',fmt(pt0));G.set('quat',fmt(qt0));G.set('childclass','R_ur5e');G.insert(0,E.Element('freejoint',name='G_free'))
for g in root.find(".//body[@name='R_tool']").iter('geom'):g.set('group','5')
for g in root.iter('geom'):
 if g.get('name','').startswith('R_'):g.set('contype','0');g.set('conaffinity','0')
wb=root.find('worldbody');wb.append(G);E.SubElement(wb,'body',name='G_mocap',mocap='true',pos=fmt(pt0),quat=fmt(qt0))
for bd in root.find(".//body[@name='rail_structure']").iter('body'):bd.set('gravcomp','1')
eq=root.find('equality') if root.find('equality') is not None else E.SubElement(root,'equality')
E.SubElement(eq,'weld',body1='G_mocap',body2='G_tool',solref='.002 1')
# PGC-140 jaws are mechanically synchronised: couple them (q_minus = q_plus).
E.SubElement(eq,'joint',joint1='G_jaw_minus',joint2='G_jaw_plus',polycoef='0 1 0 0 0')
act=E.SubElement(root,'actuator')
for jn in ('G_jaw_minus','G_jaw_plus'):
 root.find(f".//joint[@name='{jn}']").set('damping','100')
 E.SubElement(act,'position',name='act_'+jn,joint=jn,kp='50000',forcerange=f'{-FG} {FG}' if not GRIP else '-140 140',ctrlrange='-.01 .045')
EXT=0. if FINGER else float(os.environ.get('FINGER_EXT','0'))  # what-if: longer finger pads (m, along the approach axis)
if EXT>0:
 m0=mujoco.MjModel.from_xml_string(E.tostring(root,encoding='unicode'))
 for fn,jb in (('G_finger_minus','G_jaw_minus'),('G_finger_plus','G_jaw_plus')):
  gi=m0.geom(fn).id;Rg=Rotation.from_quat(m0.geom_quat[gi][[1,2,3,0]]).as_matrix();c,h=m0.geom_aabb[gi][:3],m0.geom_aabb[gi][3:]
  corners=np.array([[sx,sy,sz] for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)])*h+c;V=m0.geom_pos[gi]+corners@Rg.T;lo,hi=V.min(0),V.max(0)
  E.SubElement(root.find(f".//body[@name='{jb}']"),'geom',name=fn+'_ext',type='box',pos=fmt([hi[0]+EXT/2,(lo[1]+hi[1])/2,(lo[2]+hi[2])/2]),
   size=fmt([EXT/2,(hi[1]-lo[1])/2,(hi[2]-lo[2])/2]),contype='2',conaffinity='0',margin='0',friction=f'{MU} .005 .0001',rgba='.9 .9 .85 1')
m=mujoco.MjModel.from_xml_string(E.tostring(root,encoding='unicode'));d=mujoco.MjData(m)
RJ=[m.joint(n).id for n in ['R_carriage_x','base_y','base_yaw','R_shoulder_pan_joint','R_shoulder_lift_joint','R_elbow_joint','R_wrist_1_joint','R_wrist_2_joint','R_wrist_3_joint']]
QA=np.array([m.jnt_qposadr[j] for j in RJ]);VA=np.array([m.jnt_dofadr[j] for j in RJ])
RJA=[m.jnt_qposadr[m.joint(n).id] for n in ('R_jaw_minus','R_jaw_plus')];JA=[m.jnt_qposadr[m.joint(n).id] for n in ('G_jaw_minus','G_jaw_plus')]
FA=m.jnt_qposadr[m.joint('food_free').id];FB=m.body('food').id;RTOOL=m.body('R_tool').id;MOC=m.body_mocapid[m.body('G_mocap').id]
TOOL=m.body('G_tool').id;FOODG=m.geom(f'raw_{ITEM}').id
GB={b_ for b_ in range(m.nbody) if m.body(b_).name.startswith('G_')}
def _side(b_):
 while b_>0:
  n_=m.body(b_).name
  if n_=='G_jaw_minus':return 0
  if n_=='G_jaw_plus':return 1
  b_=m.body_parentid[b_]
 return None
SIDE={b_:_side(b_) for b_ in GB};FING=[]  # per-step total normal force on the food from each finger while gripping
r_=float(gsize.split()[0])
QC=(fingers.standoff(D_,ITEM,r_,(r_*6/7 if ITEM=='tomato' else None))-D_['fo']) if D_ else r_-cfg.get('finger_offset',0.)
QC+=float(os.environ.get('QC_ERR',0))  # item-width estimate error per side (m): + = believed bigger, less squeeze
d.qpos[QA]=Q[0][:9];d.qpos[RJA]=Q[0][9:11];d.qpos[JA]=np.clip(QC,0,.045) if D_ else Q[0][9:11];mujoco.mj_forward(m,d)
if os.environ.get('PREVIEW'):
 # close-up stills of the gripper and item at the first state, then exit
 from PIL import Image
 m.vis.global_.offwidth=1280;m.vis.global_.offheight=960;r=mujoco.Renderer(m,480,640);cam=mujoco.MjvCamera();cam.lookat[:]=d.xpos[FB];opt=mujoco.MjvOption();opt.geomgroup[5]=0
 ims=[]
 for g_ in range(m.ngeom):
  if m.geom_bodyid[g_] not in GB and g_!=FOODG and not m.geom(g_).name.startswith(('raw_pad','raw_rib','raw_tray')):m.geom_rgba[g_,3]=0
 m.geom_rgba[FOODG]=(.85,.2,.12,1) if ITEM=='tomato' else (.95,.5,.12,1)
 for g_ in range(m.ngeom):
  n_=m.geom(g_).name
  if n_.startswith('G_jaw_') and m.geom_rgba[g_,3]>0:m.geom_rgba[g_]=(.2,.55,.75,1) if any(t in n_ for t in ('softpad','_pad','_ch','_pk','_f')) else (.9,.91,.93,1)
  elif n_.startswith('G_finger_') and m.geom_rgba[g_,3]>0:m.geom_rgba[g_]=(.9,.91,.93,1)
  elif n_.startswith('G_gripper_'):m.geom_rgba[g_]=(.25,.27,.3,1)
 views=[tuple(map(float,v.split(','))) for v in os.environ['PV_VIEWS'].split(';')] if os.environ.get('PV_VIEWS') else ((90,-5,.30),(180,-25,.30),(135,-70,.30))
 m.vis.headlight.ambient[:]=.45;m.vis.headlight.diffuse[:]=.55
 dr_=mujoco.Renderer(m,480,640);dr_.enable_depth_rendering()
 for az,el,dist in views:
  cam.azimuth,cam.elevation,cam.distance=az,el,dist;r.update_scene(d,cam,opt);im=r.render().copy()
  dr_.update_scene(d,cam,opt);dep=dr_.render();im[dep>=dep.max()-1e-6]=(236,238,241);ims.append(im)
 Image.fromarray(np.concatenate(ims,1)).save(os.environ['PREVIEW']);print('preview',os.environ['PREVIEW']);raise SystemExit
def timing(qs):
 """Trapezoidal time law on the leading-joint metric (full speed = 1 s per unit)."""
 s=np.r_[0,np.cumsum([max(np.max(abs(b_[3:9]-a_[3:9]))/.8,abs(b_[0]-a_[0])/.25,abs(b_[1]-a_[1])/.25,abs(b_[2]-a_[2])/.8) for a_,b_ in zip(qs[:-1],qs[1:])])];Lr=s[-1];Ta=.5
 T=Lr+Ta if Lr>=Ta else 2*np.sqrt(Lr*Ta)
 def sig(t):
  if Lr>=Ta:return t*t/(2*Ta) if t<Ta else (t-Ta/2 if t<T-Ta else Lr-(T-t)**2/(2*Ta))
  return t*t/(2*Ta) if t<T/2 else Lr-(T-t)**2/(2*Ta)
 return s,T,sig
def tool_rel():
 Rt=d.xmat[TOOL].reshape(3,3);return Rt.T@(d.xpos[FB]-d.xpos[TOOL]),Rt.T@d.xmat[FB].reshape(3,3)
log=[];frames=[];events=[];t_sim=0.;nxt=0.;fmax=0.;fpad=0.;cur=None
def step(qr,vr,jaw,g=False):
 global t_sim,nxt,fmax,fpad
 d.qpos[QA]=qr;d.qvel[VA]=vr;d.qpos[RJA]=d.qpos[JA];mujoco.mj_kinematics(m,d)
 d.mocap_pos[MOC]=d.xpos[RTOOL]+d.xmat[RTOOL].reshape(3,3)@OFF;d.mocap_quat[MOC]=d.xquat[RTOOL];d.ctrl[:]=jaw;mujoco.mj_step(m,d);t_sim+=DT
 f6=np.zeros(6);fs=[0.,0.]
 for c in range(d.ncon):
  con=d.contact[c]
  if FOODG in (con.geom1,con.geom2):
   mujoco.mj_contactForce(m,d,c,f6);fmax=max(fmax,abs(f6[0]))
   ob=m.geom_bodyid[con.geom1 if con.geom2==FOODG else con.geom2]
   if ob in GB:
    fpad=max(fpad,abs(f6[0]))
    if SIDE[ob] is not None:fs[SIDE[ob]]+=abs(f6[0])
 if g:FING.append(fs)
 if t_sim>=nxt:frames.append((d.qpos.copy(),cur));nxt+=1/FPS
grip_ref=None;slip=dict(mm=0.,deg=0.);release_pose=None
def grip_target(q):
 # force mode: command fully closed, the force limit sets the grip; position mode:
 # close to the contact opening minus the squeeze (compliant pads set the force)
 return np.full(2,QC-SQ) if GRIP else np.zeros(2)
t0=time.time()
def run_piece(qs,s,T,sig,g):
 for k in range(int(np.ceil(T/DT))):
  t=min((k+1)*DT,T);sg=sig(t);qa=np.array([np.interp(sg,s,qs[:,c]) for c in range(11)]);qb=np.array([np.interp(sig(max(t-DT,0)),s,qs[:,c]) for c in range(11)])
  step(qa[:9],(qa[:9]-qb[:9])/DT,grip_target(qa) if g else np.full(2,OPEN),g)
  if g and grip_ref is not None:
   pr,Rr=tool_rel();slip['mm']=max(slip['mm'],1000*np.linalg.norm(pr-grip_ref[0]));slip['deg']=max(slip['deg'],np.degrees(Rotation.from_matrix(Rr@grip_ref[1].T).magnitude()))
for kind,lab,qs,sec,g in script:
 cur=lab;q=qs[0]
 if kind!='move':
  n=int(sec/DT)
  for k in range(n):
   r_=min(1,(k+1)/(.3/DT))
   if kind=='release':jaw=OPEN*r_
   elif kind=='grasp':jaw=OPEN+(grip_target(q)-OPEN)*r_
   else:jaw=grip_target(q) if g else np.full(2,OPEN)
   step(q[:9],np.zeros(9),jaw,g and kind=='hold')
  if kind=='release':release_pose=d.xpos[FB].copy();grip_ref=None;events.append(dict(event='release',at=lab,pos=release_pose.tolist()))
  if kind=='grasp' or lab=='start':grip_ref=tool_rel()
  if release_pose is not None and not g:events[-1]['moved_after_release_mm']=round(1000*float(np.linalg.norm(d.xpos[FB]-release_pose)),2)
  continue
 # Stop at every joint-space corner (direction change > 5 deg in the speed-scaled
 # metric), as a controller does at unblended waypoints; trapezoid on each piece.
 W_=np.r_[np.full(3,1/.25),np.full(6,1/.8)];W_[2]=1/.8;dq=np.diff(qs[:,:9],axis=0)*W_;nrm=np.linalg.norm(dq,axis=1)
 cut=[0]+[i+1 for i in range(len(dq)-1) if nrm[i]>1e-9 and nrm[i+1]>1e-9 and dq[i]@dq[i+1]/(nrm[i]*nrm[i+1])<np.cos(np.radians(5))]+[len(qs)-1]
 pieces=[qs[a_:b_+1] for a_,b_ in zip(cut[:-1],cut[1:]) if b_>a_];T=0.
 for qs_ in pieces:
  s,T_,sig=timing(qs_);T+=T_;run_piece(qs_,s,T_,sig,g)
 if release_pose is not None and not g:events[-1]['moved_after_release_mm']=round(1000*float(np.linalg.norm(d.xpos[FB]-release_pose)),2)
 log.append(dict(seg=lab,T=round(T,2),pieces=len(pieces),slip_mm=round(slip['mm'],2),slip_deg=round(slip['deg'],2),food=np.round(d.xpos[FB],4).tolist()))
 print(lab,'T',round(T,2),'pieces',len(pieces),'slip so far mm',round(slip['mm'],2),'deg',round(slip['deg'],2),'food',np.round(d.xpos[FB],3),flush=True)
final=d.xpos[FB].copy();res=dict(preset=P,item=ITEM,mu=MU,grip_N_per_jaw=FG,sim_s=round(t_sim,2),wall_s=round(time.time()-t0,1),max_slip_in_grip_mm=round(slip['mm'],2),max_slip_in_grip_deg=round(slip['deg'],2),
 max_food_contact_N=round(fmax,1),max_pad_contact_N=round(fpad,1),finger_N_max=round(float(np.max(FING)) if FING else 0.,1),finger_N_p95=round(float(np.percentile(np.max(FING,axis=1),95)) if FING else 0.,1),finger_N_median=round(float(np.median(np.max(FING,axis=1))) if FING else 0.,1),finger=FINGER,item_d=ID,item_kg=MASS[ITEM],grip=GRIP or f'force {FG} N',contact_q=QC,events=events,final_food_pos=final.tolist(),segments=log)
if ITEM=='tomato':
 seat=np.array(chain.target(P,'wedge_load@tomato')['points'][-1])-[0,0,tomato_dz(cfg)];lo=np.array(meta['lever_origin'])
 res.update(seat=seat.tolist(),final_minus_seat_mm=(1000*(final-seat)).round(1).tolist(),on_plate=bool(np.all(abs(final[:2]-lo[:2]-[0,cfg.get('lever_plate_dy',0)])<.065)))
else:
 ct=np.array(meta['chute_top']);res.update(chute_top=ct.tolist(),in_chute=bool(abs(final[0]-ct[0])<.05 and abs(final[1]-ct[1])<.035 and final[2]-(.0625+float(gsize.split()[0]))<ct[2]-.02))  # bottom end >= 20 mm inside the chute
TAG=f'{P}_mu{MU}_F{int(FG)}'+(f'_f{FINGER}' if FINGER and FINGER!=cfg.get('finger') else '')+(f'_d{ID:.3f}' if ID else '')+(f"_m{os.environ['ITEM_M']}" if os.environ.get('ITEM_M') else '')+(f'_pos{SQ:.4f}' if GRIP else '')+(f"_qe{os.environ['QC_ERR']}" if os.environ.get('QC_ERR') else '')+(f'_ns{os.environ["NOSLIP"]}' if os.environ.get('NOSLIP') else '')+(f'_ext{EXT:.3f}' if EXT>0 else '')+('_shift'+'_'.join(f'{x:+.3f}' for x in SHIFT) if SHIFT.any() else '');res['food_shift_tool_m']=SHIFT.tolist();res['finger_ext_m']=EXT
json.dump(res,open(f'results/dyn_{TAG}.json','w'),indent=1)
print(json.dumps({k:v for k,v in res.items() if k!='segments'},indent=1))
np.save(f'results/dyn_{TAG}_frames.npy',np.array([f[0] for f in frames]))
json.dump([f[1] for f in frames],open(f'results/dyn_{TAG}_labels.json','w'))
open(f'results/dyn_{TAG}.xml','w',encoding='utf-8').write(E.tostring(root,encoding='unicode'))  # same model for dynvideo.py
