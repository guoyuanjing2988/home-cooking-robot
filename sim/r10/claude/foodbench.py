"""R13 food-variety grasp bench (MuJoCo 3.2.5, no-slip friction).

A floating gripper (PGC-140-50 housing, synchronised jaws, a 3D-printed finger set
from foods.SETS built by fingers.dyn_parts) is welded to a mocap target that runs a
pick -> lift -> carry -> place script. The item is a free body lying on the raw
basket floor (RoboCasa mesh resized to the catalog size, or a primitive); it is never
welded. Profile 'stress' is above the planned chains (SD/WD peaks: 1.2 m/s^2,
1.8 rad/s, 3.7 rad/s^2): 3 m/s^2, 0.6 m/s, 2 rad/s, 6 rad/s^2, a protective stop at
7.5 m/s^2 mid-carry, and two 45 deg tilts (about the jaw axis: gravity along the
pads; about the pad-height axis: gravity into one finger), 90 deg yaw.
Grip modes: force:F (gripper force mode, PGC 40..140 N per jaw) or ctl:F (position
mode closed on a finger-root force sensor to F per finger, then held; small
corrections at 50 Hz if the force leaves 0.7..1.5 F).
Usage: python foodbench.py <item> [KEY=VALUE ...]  keys: SET GR MODE MU SIZE MASS
 SHIFT=x,y,z (grasp offset error in the world, m) PROFILE=stress|chain FRAMES=1 TAG=..."""
import sys,os,json,time,numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation,Slerp
import fingers,foods,foodmesh
from fingers import JAW_Y
ITEM=sys.argv[1];KV=dict(a.split('=',1) for a in sys.argv[2:])
it=dict(foods.ITEMS[ITEM])
if 'SIZE' in KV:it=foods.size_variant(it,float(KV['SIZE']))
if 'MASS' in KV:it['kg']=float(KV['MASS'])
GR=KV.get('GR','PGC');gr=foods.GRIPPERS[GR];MU=float(KV.get('MU',it['mu']))
LIP=float(KV.get('LIP',0));GRASP=KV.get('GRASP','pinch');SUP=GRASP=='support'
# supported grasp: jaws vertical, the lower finger slides under the item between the
# ribs of a slot tray and carries its weight; the jaw range must cover the item height
SET=KV.get('SET') or foods.pick_set(dict(it,dims=[it['dims'][2]*1.1+.008]+it['dims'][1:]) if SUP else it,GR,lip=LIP);PROFILE=KV.get('PROFILE','stress')
mode=KV.get('MODE');MODE,FT,FRIC_OK=(mode.split(':')[0],float(mode.split(':')[1]),None) if mode else foods.pick_mode(it,GR,SET)
if SUP and not mode:
 # the lower finger carries the weight; the clamp only has to stop sliding under the
 # 7.5 m/s^2 protective stop at the design friction (both pads: mu (2F + m g) >= m a)
 FT=float(np.clip(it['kg']*(7.5/it['mu_d']-foods.G)/2,.5,max(.5,it['dmg']/1.4-it['kg']*foods.G)));MODE='ctl';FRIC_OK=True
SHIFT=np.array([float(x) for x in KV.get('SHIFT','0,0,0').split(',')])
TAG=f"{ITEM}_{SET}{'_lip%g'%(LIP*1000) if LIP else ''}{'_sup' if SUP else ''}_{GR}_{MODE}{FT:.3g}_mu{MU:g}"+(f"_s{KV['SIZE']}" if 'SIZE' in KV else '')+(f"_m{KV['MASS']}" if 'MASS' in KV else '')+('_sh'+'_'.join(f'{x*1000:+.0f}' for x in SHIFT) if SHIFT.any() else '')+(f'_{PROFILE}' if PROFILE!='stress' else '')+KV.get('TAG','')
os.makedirs('results/r13',exist_ok=True)
def done(res):
 json.dump(res,open(f'results/r13/{TAG}.json','w'),indent=1);print(json.dumps({k:v for k,v in res.items() if k!='segments'},indent=1));raise SystemExit
base=dict(item=ITEM,zh=it['zh'],set=SET,lip=LIP,grasp=GRASP,gripper=GR,mode=MODE,F=FT,mu=MU,kg=it['kg'],dims=it['dims'],dmg=it['dmg'],dsrc=it.get('dsrc'),friction_rule_ok=FRIC_OK,profile=PROFILE,shift=SHIFT.tolist())
if SET is None:done(dict(base,ok=False,reason='no finger set covers this width'))
d_=dict(foods.SETS[SET]);STROKE=gr['stroke']
for kv in filter(None,KV.get('SETP','').split(',')):  # finger-set overrides, e.g. SETP=profile:flat,P:.05
 k_,v_=kv.split(':');d_[k_]=v_ if k_=='profile' else float(v_)
if 'SETP' in KV:TAG+='_'+KV['SETP'].replace(':','').replace(',','_')
if LIP:d_.update(lip=LIP,lip_ang=float(KV.get('LIPANG',15)),lip_t=.0015)
if SUP and 'H' not in KV.get('SETP',''):  # supported grasp: a narrow spatula finger for the rib channel
 # two 16 mm tines two channels apart (long or wide items rest on two points)
 d_['H']=.016;d_['w']=.0065;d_['rock']=0.
 # tines two pitches apart for long items (>= 150 mm); one tine otherwise
 if it['dims'][1]>=.15:d_['tines']=[-(d_['H']+.018),(d_['H']+.018)];d_['rock']=8.  # the fork rocks so both tines bear
  # (a one-pitch fork for 70-150 mm items was tried and made round items worse; reverted)
W=it['dims'][0];DT=float(KV.get('DT','.0005'));FPS=30;CLR=.008
q_open=STROKE/2  # set from the measured item after settling
def fmt(v):return ' '.join(f'{float(x):.9g}' for x in v)
# ---------------- model ----------------
root=E.Element('mujoco',model='foodbench');E.SubElement(root,'compiler',angle='radian',autolimits='true')
E.SubElement(root,'option',timestep=str(DT),cone='elliptic',impratio='10',noslip_iterations=KV.get('NOSLIP','10'))
vis=E.SubElement(root,'visual');E.SubElement(vis,'global',offwidth='1280',offheight='720');E.SubElement(vis,'quality',shadowsize='4096')
E.SubElement(vis,'headlight',ambient='.4 .4 .4',diffuse='.5 .5 .5')
asset=E.SubElement(root,'asset');wb=E.SubElement(root,'worldbody');eq=E.SubElement(root,'equality');act=E.SubElement(root,'actuator')
E.SubElement(wb,'light',pos='.3 -.6 1.2',dir='-.1 .5 -1',diffuse='.6 .6 .6',castshadow='true')
SC=dict(contype='1',conaffinity='5',friction='.4 .002 .0001')
def sbox(name,p,half,rgba='.75 .7 .62 1',par=wb):return E.SubElement(par,'geom',name=name,type='box',pos=fmt(p),size=fmt(half),rgba=rgba,**SC)
E.SubElement(wb,'geom',name='counter',type='plane',size='2 2 .01',rgba='.82 .8 .78 1',**SC)
# raw basket (tray): 5 mm floor, 40 mm walls, inner 0.32 x 0.48 m
BF=.005;sbox('basket_floor',[0,0,BF/2],[.16,.275,BF/2]);HR=0.
if SUP:
 # slot tray: 35 mm ribs along x; the finger channel (pad height + 12 mm) is centred
 # under the item; ribs stop 5 mm short of the item's near side (open front)
 # uniform channels (finger width + 12 mm) between 6 mm ribs; the robot uses the
 # channel nearest the item's centre of mass
 HR=.035;g_=d_['H']+.012;PITCH=g_+.006;TS=d_.get('tines',[0.]);x0_,x1_=-(it['dims'][0]/2-.005),it['dims'][0]/2+.06
 ys=[(k+.5)*PITCH for k in range(-12,12) if abs((k+.5)*PITCH)<.24]
 # V-topped ribs (10 deg each side, low point at x = 0) keep round items from rolling
 # along the channels and centre them where the fork expects them
 tv=np.radians(10)
 for i,y_ in enumerate(ys):
  sbox(f'rib{i}',[(x0_+x1_)/2,y_,BF+(HR-.006)/2],[(x1_-x0_)/2,.003,(HR-.006)/2],'.62 .5 .38 1')
  for j,(xa,xb) in enumerate(((x0_,0.),(0.,x1_))):
   L_=(xb-xa)/np.cos(tv);sg=-1 if j==0 else 1;cx=(xa+xb)/2;cz=BF+HR+abs(cx)*np.tan(tv)-.003/np.cos(tv)
   g=sbox(f'rib{i}v{j}',[cx,y_,cz],[L_/2,.003,.003],'.62 .5 .38 1');g.set('quat',fmt(Rotation.from_euler('y',-sg*tv).as_quat()[[3,0,1,2]]))
else:
 for s in (-1,1):sbox(f'basket_wx{s}',[s*.163,0,.02],[.003,.278,.02]);sbox(f'basket_wy{s}',[0,s*.278,.02],[.163,.003,.02])
# target: 240 mm bowl (100 mm deep) or, for long items, a 0.30 x 0.46 m tray (60 mm walls)
TX=np.array([.65,0,0]);LONG=max(it['dims'][:2])>.2
if LONG:  # long side along x: the item arrives yawed by 90 deg
 sbox('tgt_floor',TX+[0,0,.0025],[.25,.17,.0025],'.6 .65 .7 1')
 for s in (-1,1):sbox(f'tgt_wx{s}',TX+[s*.253,0,.03],[.003,.173,.03],'.6 .65 .7 1');sbox(f'tgt_wy{s}',TX+[0,s*.173,.03],[.253,.003,.03],'.6 .65 .7 1')
 TFLOOR,TR,TRIM=.005,None,.06
else:
 b=E.SubElement(wb,'body',name='bowl',pos=fmt(TX));E.SubElement(b,'geom',name='tgt_floor',type='cylinder',pos='0 0 .0025',size='.12 .0025',rgba='.6 .65 .7 1',**SC)
 for k in range(32):
  a=k*2*np.pi/32;g=sbox(f'tgt_w{k}',[.121*np.cos(a),.121*np.sin(a),.05],[.0015,.121*np.tan(np.pi/32),.05],'.6 .65 .7 1',b);g.set('quat',fmt(Rotation.from_euler('z',a).as_quat()[[3,0,1,2]]))
 TFLOOR,TR,TRIM=.005,.118,.10
# item (free body); collision geoms carry no friction (pads / scene set the pair value)
FI=dict(contype='1',conaffinity='7',friction='0 0 0',condim='4',solref=KV.get('SOLREF','.002 1'))
fb=E.SubElement(wb,'body',name='food',pos='0 0 0.2');E.SubElement(fb,'freejoint',name='food_free')
if it['src']:
 mk=foodmesh.make(ITEM+(f"_s{KV['SIZE']}" if 'SIZE' in KV else ''),it['src'],it['dims'])
 for i,p in enumerate(mk['col']):
  E.SubElement(asset,'mesh',name=f'fc{i}',file=p);E.SubElement(fb,'geom',name=f'food_c{i}',type='mesh',mesh=f'fc{i}',rgba='0 0 0 0',density='1000',**FI)
 E.SubElement(asset,'mesh',name='fvis',file=mk['vis'])
 if mk['tex']:E.SubElement(asset,'texture',name='ftex',type='2d',file=mk['tex']);E.SubElement(asset,'material',name='fmat',texture='ftex',specular='.3')
 E.SubElement(fb,'geom',name='food_vis',type='mesh',mesh='fvis',contype='0',conaffinity='0',group='1',density='0',**(dict(material='fmat') if mk['tex'] else dict(rgba=fmt(it['rgba']))))
else:
 prims=it['prim'] if isinstance(it['prim'],list) else [(it['prim'][0],it['prim'][1:],(0,0,0))]
 for i,(k,sz,pp) in enumerate(prims):E.SubElement(fb,'geom',name=f'food_c{i}',type=k,size=fmt(sz),pos=fmt(pp),rgba=fmt(it['rgba']),density='1000',
  quat=fmt(Rotation.from_euler('x',np.pi/2).as_quat()[[3,0,1,2]]) if k=='capsule' and not isinstance(it['prim'],list) else '1 0 0 0',**FI)
# gripper: tool frame x = approach, y = jaw axis, z = pad height; TCP = item centre
Dd,c=d_['D'],d_['c'];MUT=.004*MU;FR=f'{MU} {MUT:.6g} .0001'
gb=E.SubElement(wb,'body',name='G_tool',pos='0 0 .5');E.SubElement(gb,'freejoint',name='G_free')
GC=dict(contype='4',conaffinity='0',friction=FR)
E.SubElement(gb,'geom',name='G_gripper_housing',type='box',pos=fmt([-Dd-.06925,0,c]),size='.06925 .0375 .0375',mass='1',rgba='.25 .27 .3 1',**GC)
E.SubElement(gb,'geom',name='G_gripper_flange',type='cylinder',pos=fmt([-Dd-.1385-.02,0,c]),size='.0375 .02',quat=fmt(Rotation.from_euler('y',np.pi/2).as_quat()[[3,0,1,2]]),mass='.2',rgba='.6 .62 .65 1',**GC)
for jn,s in (('G_jaw_minus',-1),('G_jaw_plus',1)):
 jb=E.SubElement(gb,'body',name=jn,pos=fmt([.015-Dd,s*JAW_Y,c]));E.SubElement(jb,'joint',name=jn,type='slide',axis=fmt([0,s,0]),range=f'0 {STROKE/2}',damping='100',armature='.01')
 E.SubElement(jb,'inertial',pos='0 0 0',mass='.05',diaginertia='1e-5 1e-5 1e-5');fingers.dyn_parts(root,jb,s,d_,FR)
for g in gb.iter('geom'):g.set('solref',KV.get('SOLREF','.002 1'))  # stiff pad contacts: compliance is modelled by the sprung pad, not by contact softness
mb=E.SubElement(wb,'body',name='G_mocap',mocap='true',pos='0 0 .5')
E.SubElement(eq,'weld',body1='G_mocap',body2='G_tool',solref='.002 1')
E.SubElement(eq,'joint',joint1='G_jaw_minus',joint2='G_jaw_plus',polycoef='0 1 0 0 0')
FRANGE=FT if MODE=='force' else gr['Fmax']
for jn in ('G_jaw_minus','G_jaw_plus'):E.SubElement(act,'position',name='act_'+jn,joint=jn,kp='50000',forcerange=f'{-FRANGE} {FRANGE}',ctrlrange=f'-.01 {STROKE/2+.01}')
def compile_():return mujoco.MjModel.from_xml_string(E.tostring(root,encoding='unicode'))
m=compile_();m0=m.body_mass[m.body('food').id]
for g in fb.findall('geom'):
 if g.get('density')!='0':g.set('density',f"{1000*it['kg']/m0:.6g}")
m=compile_();d=mujoco.MjData(m)
FB=m.body('food').id;FGEOMS={g for g in range(m.ngeom) if m.geom_bodyid[g]==FB}
GB={b for b in range(m.nbody) if m.body(b).name.startswith('G_')}
def side(b):
 while b>0:
  n=m.body(b).name
  if n=='G_jaw_minus':return 0
  if n=='G_jaw_plus':return 1
  b=m.body_parentid[b]
SIDE={b:side(b) for b in GB};SOFT={b for b in GB if m.body(b).name.endswith('_soft')}
JQ=[m.jnt_qposadr[m.joint(n).id] for n in ('G_jaw_minus','G_jaw_plus')];TOOL=m.body('G_tool').id;MOC=m.body_mocapid[m.body('G_mocap').id]
SCENE={g for g in range(m.ngeom) if m.geom_bodyid[g] not in GB and g not in FGEOMS}
ctl=dict(target=q_open,held=False)
# ---------------- settle the item in the basket ----------------
FA=m.jnt_qposadr[m.joint('food_free').id]
d.qpos[FA:FA+3]=[0,0,BF+HR+it['dims'][2]/2+.002];d.qpos[FA+3:FA+7]=[1,0,0,0]
R_TD=np.array([[0,1,0],[0,0,-1],[-1,0,0]])  # top-down: tool x = -z, tool y = +x, tool z = -y (world)
R_SV=np.array([[1,0,0],[0,0,-1],[0,1,0]])   # supported: tool x = +x (horizontal), tool y = +z (plus finger on top), tool z = -y
R0=R_SV if SUP else R_TD
def set_mocap(p,R):d.mocap_pos[MOC]=p;d.mocap_quat[MOC]=Rotation.from_matrix(R).as_quat()[[3,0,1,2]]
park=np.array([-.25,0,.3]) if SUP else np.array([0,0,.45]);set_mocap(park,R0);d.qpos[m.jnt_qposadr[m.joint('G_free').id]:][:3]=park;d.qpos[m.jnt_qposadr[m.joint('G_free').id]+3:][:4]=d.mocap_quat[MOC]
d.qpos[JQ]=q_open;d.ctrl[:]=q_open;mujoco.mj_forward(m,d)
for _ in range(int(.6/DT)):mujoco.mj_step(m,d)
# grasp target from the settled item: AABB centre (what a camera would see) + offset error
def food_aabb():
 P=[]
 for g in FGEOMS:
  if m.geom_contype[g]==0:continue
  if m.geom_type[g]==mujoco.mjtGeom.mjGEOM_MESH:
   mi=m.geom_dataid[g];v=m.mesh_vert[m.mesh_vertadr[mi]:m.mesh_vertadr[mi]+m.mesh_vertnum[mi]];P.append(d.geom_xpos[g]+v@d.geom_xmat[g].reshape(3,3).T)
  else:
   c_=m.geom_aabb[g][:3];h=m.geom_aabb[g][3:];P.append(d.geom_xpos[g]+(np.array([[sx,sy,sz] for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)])*h+c_)@d.geom_xmat[g].reshape(3,3).T)
 P=np.vstack(P);return P.min(0),P.max(0)
def food_pts():
 P=[]
 for g in FGEOMS:
  if m.geom_contype[g]==0:continue
  if m.geom_type[g]==mujoco.mjtGeom.mjGEOM_MESH:
   mi=m.geom_dataid[g];v=m.mesh_vert[m.mesh_vertadr[mi]:m.mesh_vertadr[mi]+m.mesh_vertnum[mi]];P.append(d.geom_xpos[g]+v@d.geom_xmat[g].reshape(3,3).T)
  else:  # primitives: sample the surface
   u=np.random.default_rng(0).normal(size=(4000,3));u/=np.linalg.norm(u,axis=1)[:,None];sz=m.geom_size[g]
   if m.geom_type[g]==mujoco.mjtGeom.mjGEOM_ELLIPSOID:v=u*sz
   elif m.geom_type[g]==mujoco.mjtGeom.mjGEOM_CAPSULE:
    v=u*sz[0];v[:,2]+=np.sign(v[:,2])*sz[1];a_=np.linspace(0,2*np.pi,60);z_=np.linspace(-sz[1],sz[1],80);A_,Z_=np.meshgrid(a_,z_)
    v=np.r_[v,np.c_[sz[0]*np.cos(A_.ravel()),sz[0]*np.sin(A_.ravel()),Z_.ravel()]]
   else:v=u/np.max(abs(u)/sz[:3],axis=1)[:,None]
   P.append(d.geom_xpos[g]+v@d.geom_xmat[g].reshape(3,3).T)
 return np.vstack(P)
lo,hi=food_aabb()
# grasp point as a depth camera would fit it: at the item's centroid along its long
# axis (world y), the centre of the local cross-section (+-6 mm slice) in x and z
# grasp point as a depth camera would fit it: at the item's centroid along its long
# axis (world y), inside the pad span (+-H/2), the widest cross-section (2 mm bins)
pts_w=food_pts();com=d.xipos[FB].copy()
# yaw: a camera sees the item's long axis; pinch grasps align the pad height with it
# (supported grasps rely on the V-ribs, which already align items across the channels)
ev,evec=np.linalg.eigh(np.cov((pts_w[:,:2]-com[:2]).T));ax=evec[:,1]
YAW=0. if (SUP or np.sqrt(ev[1]/max(ev[0],1e-12))<1.2) else float((np.arctan2(ax[1],ax[0])-np.pi/2+np.pi/2)%np.pi-np.pi/2)
RZ=Rotation.from_euler('z',YAW).as_matrix()
pts=(pts_w-[com[0],com[1],0])@RZ;yc=0.  # item frame: x across the long axis, y along it, z up
sl_=pts[abs(pts[:,1]-yc)<d_['H']/2]
zb=np.arange(sl_[:,2].min(),sl_[:,2].max()+.002,.002);wid=[np.ptp(sl_[abs(sl_[:,2]-z)<.0015,0]) if np.sum(abs(sl_[:,2]-z)<.0015)>1 else 0 for z in zb]
wmax=max(wid);ix=np.flatnonzero(np.array(wid)>=wmax-.001);zw=float(zb[ix[len(ix)//2]]);band=sl_[abs(sl_[:,2]-zw)<.0015]
ctr=np.array([(band[:,0].min()+band[:,0].max())/2,yc,zw]);W_local=wmax
TIPCLR=.0025  # fingertip clearance above the basket floor (touch-down calibrated)
if LIP:
 # touch down beside the item: the lip rests 1 mm above the floor; the open lips must
 # clear the item's footprint at lip height, then close under it
 zg=BF+.001+d_['lip_t']+(d_['P']-Dd);low=sl_[sl_[:,2]<BF+LIP*np.sin(np.radians(d_['lip_ang']))+.004]
 w_low=float(np.max(abs(low[:,0]-ctr[0]))) if len(low) else 0.
 q_need=max(W_local/2+d_['e']+.004,w_low+LIP*np.cos(np.radians(d_['lip_ang']))+.003)-d_['fo']
 if not (zg-(d_['P']-Dd)<=ctr[2]<=zg+Dd):done(dict(base,ok=False,reason='equator outside the pad span with lips'))
else:
 zg=max(ctr[2],BF+(d_['P']-Dd)+TIPCLR);q_need=W_local/2+d_['e']+.004-d_['fo']
if SUP:
 # one tine: the channel nearest the centre of mass; two tines: the rib between two
 # channels nearest it (tines are one pitch apart, each in a channel)
 TS=d_.get('tines',[0.]);two_close=len(TS)==2 and abs(TS[1]-TS[0])<1.5*PITCH
 # channel centre nearest the COM (item frame); a one-pitch fork straddles the rib nearest it
 yc=((np.floor(com[1]/PITCH)+.5)*PITCH if two_close else round(com[1]/PITCH)*PITCH)-com[1]
 # TCP 2 mm above the mid height of the item over the finger channel: the lower finger
 # meets the bottom first and lifts it 4 mm off the ribs before the upper one touches
 span=max(abs(t) for t in TS)+d_['H']/2+.003  # all tines (and their clearance)
 col=pts[(abs(pts[:,1]-yc)<span)&(abs(pts[:,0]-ctr[0])<W_local/2)];zb_,zt_=col[:,2].min(),col[:,2].max()
 ctr=np.array([ctr[0],yc,(zb_+zt_)/2+.002]);zg=ctr[2]
 q_need=max(zt_-zg+.006,zg-zb_+.004)+d_['e']-d_['fo']
 base['item_height_mm']=round(1000*(zt_-zb_),1)
 if zg-(d_['fo']+min(q_need,STROKE/2))-(d_['T']+d_['tp'])<BF+.002:done(dict(base,ok=False,reason='lower finger does not fit under the item'))
if q_need>STROKE/2+1e-9:done(dict(base,ok=False,reason='item wider than the open fingers',width_local_mm=round(1000*W_local,1)))
q_open=float(min(STROKE/2,q_need+.002 if SUP else max(q_need,W_local/2+d_['e']+CLR-d_['fo'])));ctl['target']=q_open
d.ctrl[:]=q_open
p_grasp=np.r_[com[:2]+RZ[:2,:2]@ctr[:2],zg]+SHIFT;base['yaw_deg']=round(np.degrees(YAW),1)
if not SUP:R0=RZ@R_TD
grasp_above_centre=zg-ctr[2]
base['width_local_mm']=round(1000*W_local,1)
# ---------------- motion ----------------
PR=dict(stress=dict(v=.6,a=3.,w=2.,al=6.,stop=7.5,tilt=45.),chain=dict(v=.4,a=1.2,w=1.2,al=3.,stop=None,tilt=30.))[PROFILE]
def trap(L,v,a):
 if L<1e-12:return 0.,lambda t:0.
 if L>=v*v/a:T=L/v+v/a;return T,lambda t:(.5*a*t*t if t<v/a else (L-.5*a*(T-t)**2 if t>T-v/a else v*t-.5*v*v/a))
 T=2*np.sqrt(L/a);return T,lambda t:(.5*a*t*t if t<T/2 else L-.5*a*(T-t)**2)
def move(p0,R0,p1,R1,v,a,w=None,al=None,stop=None):
 """Straight line + slerp, trapezoid on the dominant metric; stop: end with a
 hard deceleration (protective stop) instead of the normal ramp."""
 w=w or PR['w'];al=al or PR['al'];L=np.linalg.norm(p1-p0);A=Rotation.from_matrix(R1@R0.T).magnitude()
 T1,f1=trap(L,v,a);T2,f2=trap(A,w,al)
 if stop:  # accelerate at a to v, cruise, stop at `stop`
  v_=min(v,np.sqrt(2*L/(1/a+1/stop)));ta=v_/a;ts=v_/stop;tc=(L-.5*v_*ta-.5*v_*ts)/v_;T1=ta+tc+ts
  f1=lambda t:(.5*a*t*t if t<ta else (.5*v_*ta+v_*(t-ta) if t<ta+tc else L-.5*stop*(T1-t)**2))
 sl=Slerp([0,1],Rotation.from_matrix([R0,R1]))
 if T1>=T2:T,f,Ln=T1,f1,L
 else:T,f,Ln=T2,f2,A
 return T,lambda t:(p0+(p1-p0)*(f(t)/Ln if Ln>0 else 1),sl([min(1,f(t)/Ln if Ln>0 else 1)]).as_matrix()[0])
# ---------------- state, sensing ----------------
SCSEG={};log=dict(fing=[],mom=[],scene=[],t=[]);frames=[];seg_log=[];nxt=0.;t_sim=0.;grip_ref=None;slip=dict(mm=0.,deg=0.);dropped=None;cur='settle'
def contacts():
 """per-finger total normal force on the item, per-finger moment about the jaw
 guide (tool frame), max gripper-scene normal force."""
 fs=np.zeros(2);M=np.zeros((2,3));sc=0.;f6=np.zeros(6);Rt=d.xmat[TOOL].reshape(3,3);pt=d.xpos[TOOL]
 for i in range(d.ncon):
  con=d.contact[i];b1,b2=m.geom_bodyid[con.geom1],m.geom_bodyid[con.geom2]
  gin=(b1 in GB)+(b2 in GB)
  if gin!=1:continue
  mujoco.mj_contactForce(m,d,i,f6);fw=con.frame.reshape(3,3).T@f6[:3]
  gb_,fon=(b1,-fw) if b1 in GB else (b2,fw)  # force on the gripper geom
  other=con.geom2 if b1 in GB else con.geom1
  if other in SCENE:sc=max(sc,abs(f6[0]));continue
  s=SIDE[gb_]
  if s is None:continue
  fs[s]+=abs(f6[0]);q=d.qpos[JQ[s]];ref=pt+Rt@np.array([-Dd-.01,(2*s-1)*(JAW_Y+q),c])
  M[s]+=Rt.T@np.cross(con.pos-ref,fon)
 return fs,M,sc
def tool_rel():
 Rt=d.xmat[TOOL].reshape(3,3);return Rt.T@(d.xpos[FB]-d.xpos[TOOL]),Rt.T@d.xmat[FB].reshape(3,3)
def jaw_cmd(phase):
 if phase=='release':return STROKE/2  # lips sit under the item: open fully to let go
 return q_open if phase=='open' else ctl['target']
CTL_N=int(.02/DT)
def step(p,R,phase,k):
 global t_sim,nxt,dropped
 set_mocap(p,R)
 if MODE=='force' and phase=='grip':ctl['target']=max(ctl['target']-.04*DT,-.005)  # PGC closes ~40 mm/s per jaw
 if MODE=='ctl' and phase=='grip' and k%CTL_N==0:
  fs,_,_=contacts();f=fs.min() if SUP else fs.mean()  # supported: control the clamp (upper) finger
  if not ctl['held']:
   # close 20 mm/s, 2.5 mm/s once the finger force passes 30 % of the target
   # 20 mm/s until first contact, then 0.05 mm steps (the PGC's position resolution)
   if f<FT:ctl['target']=max(ctl['target']-(.0004 if f<.2 else .00005),-.005)
   else:ctl['held']=True
  elif f<.7*FT:ctl['target']-=.00005                       # 0.05 mm corrections (1 permille of stroke)
  elif f>1.5*FT:ctl['target']+=.00005
 d.ctrl[:]=jaw_cmd(phase);mujoco.mj_step(m,d);t_sim+=DT
 if grip_ref is not None:
  fs,M,sc=contacts();log['fing'].append(fs);log['mom'].append(np.linalg.norm(M,axis=1));log['scene'].append(sc);log['t'].append(t_sim)
  if sc>20:SCSEG[cur]=max(SCSEG.get(cur,0),round(sc,1))
  pr,Rr=tool_rel();sl=1000*np.linalg.norm(pr-grip_ref[0]);slip['mm']=max(slip['mm'],sl);slip['deg']=max(slip['deg'],np.degrees(Rotation.from_matrix(Rr@grip_ref[1].T).magnitude()))
  if sl>40 and dropped is None:dropped=cur
 if KV.get('FRAMES') and t_sim>=nxt:frames.append(d.qpos.copy());nxt+=1/FPS
 if grip_ref is None and cur in ('release','pour','pour_hold','retreat','settle'):VMAX['v']=max(VMAX['v'],-float(d.qvel[m.jnt_dofadr[m.joint('food_free').id]+2]))
VMAX=dict(v=0.)
def run_move(name,T,f,phase):
 global cur;cur=name;n=int(np.ceil(T/DT))
 for k in range(n):p,R=f(min((k+1)*DT,T));step(p,R,phase,k)
 seg_log.append(dict(seg=name,T=round(T,2),slip_mm=round(slip['mm'],2),food=np.round(d.xpos[FB],4).tolist()))
 if KV.get('VERBOSE'):
  pr,Rr=tool_rel();print(seg_log[-1],'rot tool',np.degrees(Rotation.from_matrix(Rr@grip_ref[1].T).as_rotvec()).round(1) if grip_ref is not None else '','fing',np.round(contacts()[0],1))
def hold(name,sec,p,R,phase):run_move(name,sec,lambda t:(p,R),phase)
# ---------------- script ----------------
pre=p_grasp-[.12,0,0] if SUP else p_grasp+[0,0,.10]
T,f=move(park,R0,pre,R0,.3,1.);run_move('to_pregrasp',T,f,'open')
T,f=move(pre,R0,p_grasp,R0,.08,.8);run_move('approach',T,f,'open')
# close: ramp the command, then hold (the grip reference is taken after closing)
cur='close';k=0
while True:  # force mode: 0.5 s; ctl: until the force target is reached (3 s timeout), then 0.2 s
 step(p_grasp,R0,'grip',k);k+=1
 if MODE=='force' and k*DT>=.5:break
 if MODE=='ctl' and (ctl['held'] and ctl.setdefault('t_held',k)<=k-int(.2/DT) or k*DT>3):break
grip_ref=tool_rel();fs0,_,_=contacts();seg_log.append(dict(seg='close',finger_N=fs0.round(2).tolist(),q=float(d.qpos[JQ[0]])))
def preview(path,views=((90,-10,.35),(180,-20,.35),(135,-60,.4))):
 from PIL import Image
 r=mujoco.Renderer(m,480,640);cam=mujoco.MjvCamera();cam.lookat[:]=d.xpos[FB];ims=[]
 for az,el,dist in views:cam.azimuth,cam.elevation,cam.distance=az,el,dist;r.update_scene(d,cam);ims.append(r.render().copy())
 Image.fromarray(np.concatenate(ims,1)).save(path);print('preview',path,'finger N',fs0,'q',d.qpos[JQ])
if KV.get('DUMP'):
 f6=np.zeros(6);Rt=d.xmat[TOOL].reshape(3,3)
 for i in range(d.ncon):
  con=d.contact[i];mujoco.mj_contactForce(m,d,i,f6);n=Rt.T@con.frame[:3]
  print(m.geom(con.geom1).name,m.geom(con.geom2).name,'fn %.2f'%f6[0],'n_tool',n.round(2),'pos_tool',(Rt.T@(con.pos-d.xpos[TOOL])*1000).round(1),'dist mm %.2f'%(1000*con.dist))
 print('jaw q',d.qpos[JQ],'food rel',(tool_rel()[0]*1000).round(2))
 raise SystemExit
if KV.get('PREVIEW'):preview(KV['PREVIEW']);raise SystemExit
p_lift=p_grasp+[0,0,.12];T,f=move(p_grasp,R0,p_lift,R0,.25,1.5 if PROFILE=='stress' else 1.2);run_move('lift',T,f,'grip')
# carry altitude: a tilted long item must clear the counter and basket (half length x sin(tilt) + margin)
zc=max(p_lift[2]+.06,.06+max(it['dims'])/2*np.sin(np.radians(PR['tilt']))+.06)
if zc>p_lift[2]+1e-6:
 p_up=np.array([p_lift[0],p_lift[1],zc]);T,f=move(p_lift,R0,p_up,R0,.25,1.5);run_move('raise',T,f,'grip');p_lift=p_up
above=TX+[0,0,zc]
tilt=np.radians(PR['tilt'])
# a cradled (lip) grasp is carried level: the planner keeps the tilt about the jaw
# axis (which would let the item slide out of the open cradle sides) within 10 deg
tiltj=np.radians(float(KV.get('TILTJ',10 if LIP else PR['tilt'])))
RA=Rotation.from_euler('z',np.pi/6).as_matrix()@R0@Rotation.from_euler('y',tiltj).as_matrix()   # about the jaw axis (tool y)
RB=Rotation.from_euler('z',np.pi/3).as_matrix()@R0@Rotation.from_euler('z',tilt).as_matrix()   # about the pad-height axis (tool z)
RC_=Rotation.from_euler('z',np.pi/2).as_matrix()@R0
if SUP:  # jaw axis kept within 20 deg of vertical (planner constraint for supported grasps)
 RA=Rotation.from_euler('z',np.pi/6).as_matrix()@R_SV
 RB=Rotation.from_euler('z',np.pi/3).as_matrix()@R_SV@Rotation.from_euler('z',np.radians(20)).as_matrix()
 RC_=Rotation.from_euler('z',np.pi/2).as_matrix()@R_SV
P1=p_lift+(above-p_lift)/3;P2=p_lift+2*(above-p_lift)/3
T,f=move(p_lift,R0,P1,RA,PR['v'],PR['a'],stop=PR['stop']);run_move('carry_A_tilt_jaw_axis'+('_estop' if PR['stop'] else ''),T,f,'grip')
hold('pause',.3,P1,RA,'grip')
T,f=move(P1,RA,P2,RB,PR['v'],PR['a']);run_move('carry_B_tilt_pad_axis',T,f,'grip')
T,f=move(P2,RB,above,RC_,PR['v'],PR['a']);run_move('carry_C',T,f,'grip')
hold('pause2',.2,above,RC_,'grip')
lo,hi=food_aabb();drop_h=.004 if it['dmg']<30 else .015
if LIP:  # lower until the lips are 1 mm above the target floor
 lz=min(d.geom_xpos[g][2]-m.geom_rbound[g] for g in range(m.ngeom) if m.geom(g).name.endswith('_lip'))
 p_place=above-[0,0,max(0.,lz-(TFLOOR+.001))]
elif SUP:  # the horizontal gripper cannot enter the bowl: pour from 10 mm above the rim
 lz=min(d.geom_xpos[g][2]-m.geom_rbound[g] for g in range(m.ngeom) if m.geom_bodyid[g] in GB and SIDE.get(m.geom_bodyid[g])==0 and m.geom_contype[g])
 p_place=above-[0,0,max(0.,lz-(TRIM+.01))]
else:p_place=above-[0,0,max(0.,lo[2]-(TFLOOR+drop_h))]
T,f=move(above,RC_,p_place,RC_,.15,1.);run_move('lower',T,f,'grip')
rel_slip=dict(slip);fl=np.array(log['fing']);mo=np.array(log['mom']);sc_=np.array(log['scene'])
grip_ref=None;cur='release'
if SUP:
 # pour: open 10 mm (the item rides down on the lower finger), tip the fingertip down
 # 55 deg about the pad-height axis so the item slides off, then open fully
 for k in range(int(.5/DT)):ctl['target']=min(ctl['target']+.02*DT,STROKE/2);step(p_place,RC_,'grip',1)
 Rp=RC_@Rotation.from_euler('z',-np.radians(55)).as_matrix();T,f=move(p_place,RC_,p_place,Rp,.1,1.,w=1.2,al=4.);run_move('pour',T,f,'grip');RC_=Rp
 hold('pour_hold',.6,p_place,RC_,'grip')
 for k in range(int(.4/DT)):step(p_place,RC_,'release',k)
else:
 for k in range(int(.6/DT)):step(p_place,RC_,'release' if LIP else 'open',k)
p_ret=p_place+[0,0,.15]-(RC_[:,0]*.1 if SUP else 0)
T,f=move(p_place,RC_,p_ret,RC_,.2,1.);run_move('retreat',T,f,'release' if (LIP or SUP) else 'open')
hold('settle',1.0,p_ret,RC_,'release' if (LIP or SUP) else 'open')
# ---------------- result ----------------
def winmax(x,n=int(.01/DT)):
 if len(x)<n:return float(np.max(x)) if len(x) else 0.
 c=np.cumsum(np.r_[0,x]);return float(np.max((c[n:]-c[:-n])/n))
fN=np.max(fl,axis=1) if len(fl) else np.zeros(1)
fin=d.xpos[FB].copy();lo,hi=food_aabb()
# inside: centre over the target floor and the item resting below the rim
if LONG:in_t=abs(fin[0]-TX[0])<.25 and abs(fin[1]-TX[1])<.17 and lo[2]<TRIM-.02
else:in_t=np.linalg.norm(fin[:2]-TX[:2])<TR and lo[2]<TRIM-.02
res=dict(base,q_open=q_open,grasp_above_centre_mm=round(1000*grasp_above_centre,1),dropped=dropped,max_slip_mm=round(rel_slip['mm'],2),max_slip_deg=round(rel_slip['deg'],2),
 finger_N_10ms_max=round(winmax(fN),2),finger_N_median=round(float(np.median(fN)),2),finger_N_p95=round(float(np.percentile(fN,95)),2),
 moment_Nm_10ms_max=round(winmax(np.max(mo,axis=1)) if len(mo) else 0.,2),scene_contact_N_max=round(float(np.max(sc_)) if len(sc_) else 0.,1),
 final_pos=fin.round(4).tolist(),in_target=bool(in_t),scene_contact_segments=SCSEG,impact_v_mps=round(VMAX['v'],2),drop_equiv_mm=round(1000*VMAX['v']**2/(2*foods.G),0),need_N=round(foods.need_N(it,MU),2),sim_s=round(t_sim,2),segments=seg_log)
res['unstable']=bool(d.warning[mujoco.mjtWarning.mjWARN_BADQACC].number>0)
res['ok']=bool(not res['unstable'] and dropped is None and rel_slip['mm']<10 and in_t and res['finger_N_10ms_max']<=it['dmg'] and (gr['M_allow'] is None or res['moment_Nm_10ms_max']<=gr['M_allow']))
res['fail']=[k for k,v in (('dropped',dropped is not None),('slip>=10mm',rel_slip['mm']>=10),('not in target',not in_t),('force>damage',res['finger_N_10ms_max']>it['dmg']),
 ('moment>allow',gr['M_allow'] is not None and res['moment_Nm_10ms_max']>gr['M_allow'])) if v]
if KV.get('FRAMES'):
 np.save(f'results/r13/{TAG}_frames.npy',np.array(frames));open(f'results/r13/{TAG}.xml','w',encoding='utf-8').write(E.tostring(root,encoding='unicode'))
done(res)
