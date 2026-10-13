"""R19 prep movement sets in today's (R18b) kitchen, issue #4 step 2 (new file; method of r17chain.py,
which is not changed). The layout is kitchen19.LAYOUT (step 1, R19_PREP_LAYOUT.md):
 raw tray as today; the 卓晋 slicer resident in the far-left column, turned 90 deg (chute at the front);
 the fetched lever base (AY-403 class, R11 AW geometry) at the work spot by the sink (-0.90, 0.095);
 washing under the R17 single-lever faucet outlet (-0.40, 0.37, 1.10), opened by the checked R17 lever
 action (results/r17/chain_lever_s+1_final.json) before the set and closed after it.
Method (r17chain.py, unchanged in substance): object keyframes; between them the object moves in a
straight line (rotation slerp) every <= 1 cm / 2 deg, the cart linearly or as an IK variable ('F'); the
arm follows by IK continuation; the unchanged checker runs at every step (10 mm robot-environment, 5 mm
gripper/held-environment, joint ranges; the full bound every 5th step and at every keyframe). Anchors are
solved by 96-start collision-aware IK (solver.solve) and joined at MEET keyframes (DP over the anchor
candidates; a meet join is a straight joint move, cart fixed, checked every <= 1 deg, after a cart shuffle
under the held object if the carts differ). Grasp approach / release retreat: the empty gripper (jaws open
25 mm per side) moves APPROACH_M = 50 mm along the approach axis with the object in the world; for food the
contact window of the rules applies there and only there: finger / gripper geoms may come closer than
5 mm to that food item, never into it (penetration is checked separately, mj_geomDistance >= 0), and the
food item may touch its support (the 8 mm seat lift / set-down is inside the window). Nothing else gets a
window.
Scene ("union", so a set stays valid whichever way these are): the R18b kitchen of r17chain (spatula on
its flipped rest at (-1.15, .30), spider on its rest, lid in the rack, pour drum swung away), the fridge
(r14_fridge, door closed), the faucet lever closed AND open, the slicer and the lever base out, the
raw-tray items that are not in the hand.
Actions (ACT=):
 carrot  TRAY_PICK + CARRY + WASH_HELD + CARRY + CHUTE_DROP: front grasp of the carrot on its ribs, lift,
         carry to the sink, held under the running outlet (rinse dwell, shifted +-5 cm along its axis so
         the stream runs over both halves), carry back, turned upright on the way, lowered 80 mm into the
         slicer chute (bottom 20 mm inside), released (it drops into the appliance), gripper retreats
 tomato  TRAY_PICK + CARRY + WASH_HELD + LEVER_PLACE: front grasp at the equator off the R11 pad (position
         mode, D fingers), rinse under the outlet (rolled +-60 deg about the approach axis), carry to the
         lever base, slid in 8 mm above the blade plate and set down, released, gripper retreats
 press   LEVER_PRESS: front grasp of the pusher knob (keyed), press 102 mm (the tomato is cut: appliance-
         contained, as R11/WD), return, release; reports the arm's available push along the press
Rinse dwell times are ESTIMATES (no sourced washing time); no process force is applied (the R10 9.19 N
scrub force is not used: this is a rinse under the stream, no brush).
Held load: the object's mass (kitchen19.MASS) at its frame origin; PGC moment and joint torque ratios at
every keyframe. Timing caps as r17chain: TCP <= 0.10 m/s, 45 deg/s, joints <= 60 deg/s, cart <= 0.25 m/s.
python r19prepchain.py ACT=carrot|tomato|press [SEEDS=1|2] [TRIES=6] [KEEP=6] [RINSE=s] [TAG=..] [ARM=..]
 -> results/r19/prep/chain_<ACT>[_TAG][_arm].json (pieces, joins, approaches, loads, time, playback q)"""
import sys,os,json,time,numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation,Slerp
import chain
from scene import build,save
from checker import Checker
from solver import solve
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17,kitchen19 as K19
KV=dict(a.split('=',1) for a in sys.argv[1:]);ACT=KV['ACT'];SIGN=int(KV.get('SIGN',1))
SEEDS=(14,15,16)[:int(KV.get('SEEDS',2))];TRIES=int(KV.get('TRIES',6))
DESIGN=dict(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.set_design(**DESIGN)
K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=8.,0.,180.   # R18b spatula rest
VW,WW,QW,CW,CART_OFF=.10,45.,60.,.25,.30
import arms;ARM=arms.current();QW=min(QW,min(arms.speeds(ARM)))
APPROACH_M=.05;JAW_OPEN=.025
RINSE=float(KV.get('RINSE',3.))   # s per rinse keyframe dwell [est]
RL=float(KV.get('ROLL',30.))   # tomato rinse: rolled +-RL deg about the grasp approach axis
I=np.eye(3);L=dict(K19.LAYOUT)
if 'LEVER' in KV:L['lever']=tuple([float(v) for v in KV['LEVER'].split(',')]+[0.])   # tool spot override (x, y)
def kf(R,p,c=None,dw=0.,label='',anchor=False,meet=False,seat=0.):
 return dict(R=np.asarray(R,float),p=np.asarray(p,float),c=c,dw=dw,label=label,anchor=anchor,meet=meet,seat=seat)
def J(o):return json.loads(json.dumps(o,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else float(x)))
def scene_with(*stations,**kw):
 sc=K19.layout_scene(*stations,**kw)
 if 'lever' in sc['stations']:sc['stations']['lever']=L['lever']
 return sc
def action():
 """object, scene extras, keyframes, grasp/release list [(keyframe, world cfg r19, object in the world?)]"""
 dxy=L['tray_dxy'];car=('carrot',I,K19.tray('carrot',dxy));tom=('tomato',I,K19.tray('tomato',dxy))
 S=np.array([K19.FAUCET_OUT[0],K19.FAUCET_OUT[1],float(KV.get('RZ',.98))])   # held item centre under the outlet (1.10 m)
 def roll(R,deg):   # rotate the held item about the grasp approach axis (a wrist roll)
  a=R@K.OBJ['tomato' if ACT!='carrot' else 'carrot']['a'];return Rotation.from_rotvec(a*np.radians(deg)).as_matrix()@R
 if ACT=='carrot':
  c0=K19.tray('carrot',dxy);ch=K19.chute_top(*L['slicer']);Rv=K.Ry(90)   # upright: carrot axis (object x) vertical, jaws (object z) along x, approach still +y
  Rp=K.Rx(float(KV.get('PITCH',0.)));ln=np.array([float(v) for v in KV.get('LANE','-0.80,.10,1.15').split(',')])
  KF=[kf(I,c0+[0,0,.008],'A',0,'pick',anchor=True,seat=.008),kf(I,c0+[0,0,.05],'A',0,'lifted'),kf(I,c0+[0,-.04,.15],'F',0,'out and up'),
   kf(Rp,ln,'F',0,'lane',meet=True),
   kf(Rp,S,'F',RINSE,'under the tap',anchor=True),kf(Rp,S+[.05,0,0],'F',RINSE,'rinse right half'),kf(Rp,S+[-.05,0,0],'F',RINSE,'rinse left half'),kf(Rp,S,'F',0,'centre'),
   kf(Rp,ln,'F',0,'lane',meet=True),kf(Rv,ch+[0,-.10,.20],'F',0,'upright, in front of the chute'),
   kf(Rv,ch+[0,0,.14],'F',0,'over the chute',anchor=True),kf(Rv,ch+[0,0,.06],'A',0,'in the chute (bottom 20 mm inside)')]
  st=('lever',) if KV.get('TOOL','none')=='lever' else ();w0=scene_with(*st,objs=[tom]);w1=scene_with(*st,objs=[tom])
  return 'carrot',dict(r19=w0),KF,[(0,w0,True),(len(KF)-1,w1,False)]
 if ACT=='tomato':
  t0=K19.tray('tomato',dxy);seat=K19.lever_seat(*L['lever']);Rp=K.Rx(float(KV.get('PITCH',-30.)));lx=L['lever'][0]   # grasp pitched down 30 deg at the tap
  head=[kf(I,t0+[0,0,.008],'A',0,'pick',anchor=True,seat=.008),kf(I,t0+[0,0,.05],'A',0,'lifted')]
  if lx>S[0]:   # lever base right of the tap (plating area): nothing between the tray and the tap
   head+=[kf(I,t0+[0,-.04,.15],'F',0,'out and up'),kf(Rp,[-0.80,.10,1.15],'F',0,'lane',meet=True)]
   tail=[kf(Rp,[S[0]+float(KV.get('L2DX',.35)),.10,1.15],'F',0,'lane',meet=True)]
  else:         # lever base between the tray and the tap: carry behind it (y .30, under the cabinet), out in front right of it
   head+=[kf(I,t0+[0,.18,.10],'F',0,'back, behind the tray front'),kf(Rp,[-0.80,.30,1.05],'F',0,'back lane behind the lever base',meet=True),kf(Rp,[-0.50,.36,1.00],'F',0,'to the tap')]
   tail=[kf(Rp,[-0.60,.10,1.15],'F',0,'lane right of the lever base',meet=True)]
  KF=head+[kf(Rp,S,'F',RINSE,'under the tap',anchor=True),kf(roll(Rp,RL),S,'F',RINSE,f'rolled +{RL:g}'),kf(roll(Rp,-RL),S,'F',RINSE,f'rolled -{RL:g}'),kf(Rp,S,'F',0,'level')]+tail+[
   kf(I,seat+[0,-.135,.03],'F',0,'backed out, in front of the lever base'),kf(I,seat+[0,-.06,.008],'F',0,'in front of the blade plate',anchor=True),kf(I,seat+[0,0,.008],'A',0,'over its seat (8 mm)',seat=.008)]
  w0=scene_with('lever',objs=[car]);w1=scene_with('lever',objs=[car])
  return 'tomato',dict(r19=w0),KF,[(0,w0,True),(len(KF)-1,w1,True)]
 if ACT=='tap':   # exploration: the held item from a front lane point into the outlet and back out (one anchor at the tap)
  ob=KV.get('OBJ','tomato');th=float(KV.get('PITCH',0.));Rp=K.Rx(th)   # pitch the grasp down (th < 0) about the world x axis
  ln=np.array([float(v) for v in KV.get('LANE','-0.80,.10,1.15').split(',')])
  w=[np.array([float(v) for v in t.split(',')]) for t in KV.get('WP','').split(';') if t]
  KF=[kf(Rp,ln,'F',0,'lane in')]+[kf(Rp,x,'F',0,f'wp{i}') for i,x in enumerate(w)]+[kf(Rp,S,'F',RINSE,'under the tap',anchor=True)]+[kf(Rp,x,'F',0,f'wp{i}') for i,x in reversed(list(enumerate(w)))]+[kf(Rp,ln,'F',0,'lane out')]
  st=('lever',) if KV.get('TOOL','none')=='lever' else ();w0=scene_with(*st,objs=[tom if ob=='carrot' else car])
  return ob,dict(r19=w0),KF,[]
 if ACT=='press':
  Rp,kn=K19.pusher_pose(*L['lever'])
  KF=[kf(Rp,kn,'A',0,'knob at rest',anchor=True),kf(Rp,kn-[0,0,K19.LEVER_PRESS],'A',0,'pressed 102 mm'),kf(Rp,kn,'A',0,'returned')]
  sc=scene_with('lever',pusher=None,objs=[car])   # pusher in the hand; the tomato is cut (appliance-contained)
  w0=scene_with('lever',objs=[car,('tomato',I,K19.lever_seat(*L['lever']))]);w1=scene_with('lever',objs=[car])
  return 'pusher',dict(r19=sc),KF,[(0,w0,False),(2,w1,False)]   # the pusher is in the station at rest in both worlds
OBJ,SCENE,KF,GR=action();SCENE=J(SCENE);GR=[(k,J(w),inw) for k,w,inw in GR]
JAW_HELD=K19.JAW[OBJ];FOOD=OBJ in ('carrot','tomato')
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},r14_fridge=True,r17_lever=0.,**K19.base_cfg())
def model(extra,world_obj=None):
 """Checker for the scene (+ extra cfg). world_obj = (name, R, p): that object also lies in the world."""
 cfg=chain.chain_cfg('SD',**{**BASE,**SCENE,**extra})
 if world_obj is not None:cfg['r19']=dict(cfg['r19'],objs=list(cfg['r19'].get('objs',[]))+[J(world_obj)])
 tree,meta=build(cfg,None);K19.add(tree,cfg)
 R,p=K17.lever_pose(K17.LEVER_OPEN);K._add(tree.find('worldbody'),'u_open_',K.OBJ['lever']['parts'],R,p,rgba='.75 .77 .8 1')   # union: faucet lever closed (cfg) AND open (copy)
 return Checker(tree,meta)
ch=model(K17.held_cfg(OBJ,SIGN));m,d=ch.m,ch.d;ids=ch.arm_ids;sid=m.site('R_prep').id
lo=np.array([m.jnt_range[j,0] for j in range(m.njnt)])[ids];hi_=np.array([m.jnt_range[j,1] for j in range(m.njnt)])[ids]
def solve_to(c,q,pt_,Rt_):
 q=np.array(q,float)
 def res(x):
  q[ids]=x;c.d.qpos[:]=q;mujoco.mj_kinematics(c.m,c.d)
  return np.r_[(c.d.site_xpos[sid]-pt_)*10,Rotation.from_matrix(Rt_@c.d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
 x0=np.clip(q[ids],lo+1e-8,hi_-1e-8);sol=least_squares(res,x0,bounds=(lo+1e-9,hi_-1e-9),max_nfev=200,xtol=1e-10,ftol=1e-10)
 q[ids]=sol.x;pe,re=c.pose_error(q,pt_,Rt_);return q,pe,re,float(np.degrees(np.max(abs(sol.x-x0))))
W_CART,W_ARM=.02,.05
def solve_free(c,q,pt_,Rt_):
 q=np.array(q,float);v=[0]+list(ids);x0=q[v].copy();x0[1:]=np.clip(x0[1:],lo+1e-8,hi_-1e-8);x0[0]=np.clip(x0[0],-1.48+1e-6,1.46-1e-6)
 w=np.r_[W_CART,np.full(len(ids),W_ARM)]
 def res(x):
  q[v]=x;c.d.qpos[:]=q;mujoco.mj_kinematics(c.m,c.d)
  return np.r_[(c.d.site_xpos[sid]-pt_)*10,Rotation.from_matrix(Rt_@c.d.site_xmat[sid].reshape(3,3).T).as_rotvec(),w*(x-x0)]
 sol=least_squares(res,x0,bounds=(np.r_[-1.48,lo+1e-9],np.r_[1.46,hi_-1e-9]),max_nfev=300,xtol=1e-10,ftol=1e-10)
 q[v]=sol.x;pe,re=c.pose_error(q,pt_,Rt_);return q,pe,re,float(np.degrees(np.max(abs(sol.x[1:]-x0[1:])))),float(abs(sol.x[0]-x0[0]))
def state(c,q,full):
 r=c.check(q,full=full,mass=0.);rmin=min((v['reserve_mm'] for cat,v in r['clearance'].items() if cat!='self'),default=None) if full else None
 return r['hits'],rmin
def cart_of(k,cA):
 c=KF[k]['c'];return cA if c in ('A','F') else float(np.clip(KF[k]['p'][0]-CART_OFF,-1.48,1.46)) if c is None else float(c)
def follow(a,b,q):
 q=np.array(q,float);cA=q[0];out=[];st=1 if b>a else -1
 for i in range(a,b,st):
  A_,B_=KF[i],KF[i+st];ca,cb=cart_of(i,cA),cart_of(i+st,cA)
  ang=np.degrees(np.linalg.norm(Rotation.from_matrix(B_['R']@A_['R'].T).as_rotvec()));dist=np.linalg.norm(B_['p']-A_['p'])
  n=max(1,int(np.ceil(max(dist/.01,ang/2,abs(cb-ca)/.01))));sl=Slerp([0,1],Rotation.from_matrix([A_['R'],B_['R']]))
  for k in range(1,n+1):
   pt_,Rt_=K.tcp_pose(OBJ,sl(k/n).as_matrix(),A_['p']+(B_['p']-A_['p'])*k/n,SIGN)
   if B_['c']=='F':q,pe,re,dq,dc=solve_free(ch,q,pt_,Rt_)
   else:q[0]=ca+(cb-ca)*k/n;q,pe,re,dq=solve_to(ch,q,pt_,Rt_);dc=abs(cb-ca)/n
   hits,rmin=state(ch,q,k%5==0 or k==n)
   dt=max(dist/n/VW,ang/n/WW,dq/QW,dc/CW)+(B_['dw'] if k==n and st>0 else 0.)+(A_['dw'] if k==1 and st<0 else 0.)
   out.append(dict(kf=i+st if k==n else None,cart=round(q[0],3),step_deg=round(dq,2),pose_mm=round(pe*1000,2),reserve_mm=None if rmin is None else round(rmin,1),dt=dt,hits=[h['pair'] for h in hits][:3],q=q.tolist()))
   if pe>.005 or re>np.radians(3) or hits or dq>10:return out,dict(at=f"{A_['label']}->{B_['label']}",**{k_:v for k_,v in out[-1].items() if k_!='q'})
 return out,None
def shuffle(q,x,c):
 q=np.array(q,float);c0=q[0];n=max(1,int(np.ceil(abs(c-c0)/.01)));out=[];pt_,Rt_=K.tcp_pose(OBJ,KF[x]['R'],KF[x]['p'],SIGN)
 for k in range(1,n+1):
  q[0]=c0+(c-c0)*k/n;q,pe,re,dq=solve_to(ch,q,pt_,Rt_);hits,rmin=state(ch,q,k%5==0 or k==n)
  out.append(dict(q=q.tolist(),dq=dq,reserve_mm=rmin))
  if pe>.005 or re>np.radians(3) or hits or dq>10:return out,dict(cart=round(q[0],3),pose_mm=round(pe*1000,2),hits=[h['pair'] for h in hits][:3])
 return out,None
def meet_join(qa,qb,x,plan=False):
 qa,qb=np.array(qa,float),np.array(qb,float)
 if abs(qa[0]-qb[0])<1e-6:return join(qa,qb,plan,x)
 for frm,to,rev in ((qa,qb,False),(qb,qa,True)):
  out,f=shuffle(frm,x,to[0])
  if f:continue
  j=join(np.array(out[-1]['q']),to,plan,x) if not rev else join(to,np.array(out[-1]['q']),plan,x)
  if not j['ok']:continue
  ts=sum(max(.01/CW,o['dq']/QW) for o in out);sq=[o['q'] for o in out]
  j.update(cart_m=round(abs(qa[0]-qb[0]),3),shuffle_s=round(ts,1),s=round(j['s']+ts,2),arm_deg=round(j['arm_deg']+sum(o['dq'] for o in out),1),qs=(sq+j['qs']) if not rev else (j['qs']+sq[::-1]))
  return j
 return dict(ok=False,arm_deg=1e3,cart_m=round(abs(qa[0]-qb[0]),3),reason='shuffle or join blocked from both sides')
def join(qa,qb,plan=None,x=None):
 qa,qb=np.array(qa),np.array(qb)
 for j in range(6):
  c=[qb[3+j]+k*2*np.pi for k in (-2,-1,0,1,2) if lo[j]-1e-9<=qb[3+j]+k*2*np.pi<=hi_[j]+1e-9];qb[3+j]=min(c,key=lambda v:abs(v-qa[3+j]))
 dq=np.degrees(np.max(abs(qb[3:9]-qa[3:9])));n=max(1,int(np.ceil(dq)))
 for k in range(1,n):
  hits,_=state(ch,qa+(qb-qa)*k/n,False)
  if hits:
   if (KV.get('PLAN') if plan is None else plan):
    import planner;ch.active=ch.arm_ids;r=planner.plan(ch,qa,qb,budget_s=float(KV.get('PLAN_S',120)),seed=8)
    if r['ok']:
     P=np.array(r['path']);sweep=float(np.degrees(np.sum(np.max(abs(np.diff(P[:,3:9],axis=0)),axis=1))))
     return dict(ok=True,method='planned',arm_deg=round(float(dq),1),path_joint_deg=round(sweep,1),s=round(sweep/QW+.6,2),qs=P.tolist())
    return dict(ok=False,method='planner failed',arm_deg=round(float(dq),1),reason=r.get('reason'))
   return dict(ok=False,arm_deg=round(float(dq),1),at=round(k/n,2),hits=[h['pair'] for h in hits][:3])
 return dict(ok=True,arm_deg=round(float(dq),1),s=round(dq/QW+.6,2),qs=[(qa+(qb-qa)*k/n).tolist() for k in range(0,n+1,max(1,n//20))])
_empty={}
def approach(k,world,inw,q):
 """Empty gripper, jaws open, from the grasp at KF[k] (object at its support, i.e. without the seat
 lift) back APPROACH_M along the grasp approach axis; the object lies in the world if inw. Food: the
 contact window (fingers / gripper vs that food item closer than 5 mm allowed, never penetrating)."""
 R,p=KF[k]['R'],KF[k]['p']-[0,0,KF[k]['seat']];wo=(OBJ,R,p) if inw else None
 key=json.dumps([world,J(wo)],sort_keys=True)
 if key not in _empty:_empty[key]=model(dict(r19=world),wo)
 c=_empty[key];win=set();og=[]
 if inw and FOOD:
  og=[g for g in range(c.m.ngeom) if c.m.geom(g).name==f'r19_{OBJ}'];fg=[g for g in range(c.m.ngeom) if c.m.geom(g).name.startswith(('R_finger_','R_gripper_'))]
  win={frozenset([c.m.geom(a).name,c.m.geom(b).name]) for a in og for b in fg}
 perm=c.permissions;c.permissions=lambda kind:set(perm(kind))|win
 try:
  pt0,Rt=K.tcp_pose(OBJ,R,p,SIGN);q=np.array(q,float);q[-2:]=JAW_OPEN;c0=q[0];out=[];n=int(round(APPROACH_M/.01));pen=[]
  for s in range(n+1):
   dp=-Rt[:,0]*APPROACH_M*s/n;q[0]=c0+dp[0];q,pe,re,dq=solve_to(c,q,pt0+dp,Rt);hits,rmin=state(c,q,s%3==0 or s==n)
   if win:   # inside the window: never into the food item (exact convex bounds of distance.py, as the checker; upper bound > 0 = certified apart)
    c.d.qpos[:]=q;mujoco.mj_kinematics(c.m,c.d)
    bs=[c.bounds.pair(a,b) for a in og for b in fg];dmin=min(v['lower_m'] for v in bs);pen.append(dmin)
    if min(v['upper_m'] for v in bs)<=1e-6:hits=hits+[dict(pair=['window food','touching or penetrating'])]
   out.append(dict(step=s,pose_mm=round(pe*1000,2),step_deg=round(dq,2),reserve_mm=None if rmin is None else round(rmin,1),hits=[h['pair'] for h in hits][:3],q=q.tolist()))
   if pe>.005 or re>np.radians(3) or hits:return dict(ok=False,kf=k,stop=s,hits=out[-1]['hits'],pose_mm=out[-1]['pose_mm'],qs=[o['q'] for o in out])
 finally:c.permissions=perm
 rm=[o['reserve_mm'] for o in out if o['reserve_mm'] is not None]
 return dict(ok=True,kf=k,object_in_world=inw,window=bool(win),min_food_gap_mm=round(min(pen)*1000,1) if pen else None,min_reserve_mm=min(rm) if rm else None,time_s=round(APPROACH_M/VW,1),qs=[o['q'] for o in out])
def load(q,k):
 mass=K19.MASS[OBJ];com=KF[k]['p']
 d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d);bid=m.site_bodyid[sid];jp=np.zeros((3,m.nv));jr=jp.copy();mujoco.mj_jac(m,d,jp,jr,com,bid)
 tau=d.qfrc_bias-jp.T@np.array([0,0,-mass*9.81]);ratios={n:float(abs(tau[ch.da[n]])/v) for n,v in ch.env.items()}
 return dict(kf=KF[k]['label'],held_kg=mass,max_joint_ratio=round(max(ratios.values()),3),pgc_moment_Nm=round(float(np.linalg.norm(np.cross(com-d.site_xpos[sid],[0,0,-mass*9.81]))),2))
def push_capacity(q,hi=400.):
 """Largest downward push (N) on the knob the arm can hold at q (as chain.push_capacity): joint torque
 envelope, keyed grip (150 N / 15 N.m key, SF 1.5), PGC moment, cart tipping."""
 from mobile import stability
 lo_=0.
 for _ in range(18):
  f=(lo_+hi)/2;F=[0,0,f];ok=ch.loads(np.array(q),F,K19.MASS['pusher'],0)['ok'] and stability(ch,np.array(q),F,K19.MASS['pusher'],0)['ok']
  lo_,hi=(f,hi) if ok else (lo_,f)
 return round(lo_,1)
# ---- anchors, pieces, DP over the anchor candidates (as r17chain.py) ----
A=[i for i,k_ in enumerate(KF) if k_['anchor']];M=[i for i,k_ in enumerate(KF) if k_['meet']]
def sides(a):
 before=[x for x in M if x<a];after=[x for x in M if x>a]
 prev_a=max([x for x in A if x<a],default=None);next_a=min([x for x in A if x>a],default=None);t=[]
 if prev_a is None:
  if a>0:t.append(0)
 else:assert before and before[-1]>prev_a,('no meet between anchors',prev_a,a);t.append(before[-1])
 if next_a is None:
  if a<len(KF)-1:t.append(len(KF)-1)
 else:assert after and after[0]<next_a,('no meet between anchors',a,next_a);t.append(after[0])
 return t
_cands={}
def candidates(k):
 key=(tuple(np.round(KF[k]['p'],4)),tuple(np.round(KF[k]['R'].ravel(),4)))
 if key in _cands:return _cands[key]
 pt_,Rt_=K.tcp_pose(OBJ,KF[k]['R'],KF[k]['p'],SIGN);out=[];stat={}
 for seed in SEEDS:
  t=dict(name=f'{ACT}_{k}',points=[list(pt_)]*2,held=None,kind='transfer',force=None,approach=list(Rt_[:,0]),jaws=[tuple(SIGN*(KF[k]['R']@K.OBJ[OBJ]['j']))],jaw_q=JAW_HELD)
  if isinstance(KF[k]['c'],float):t['cart_x']=KF[k]['c']
  r=solve(ch,pt_,list(Rt_[:,0]),target=t,seed=seed)
  for k_,v in r['status_counts'].items():stat[k_]=stat.get(k_,0)+v
  out+=[dict(q=c_['q'],reserve_mm=c_['reserve_mm']) for c_ in r['candidates']]
 out=sorted(out,key=lambda c_:-c_['reserve_mm']);_cands[key]=(out,stat);return _cands[key]
t0=time.monotonic();pieces={};anchors={};log=[];good={};KEEP=int(KV.get('KEEP',6))
for a in A:
 cs,stat=candidates(a);print(KF[a]['label'],'start candidates',len(cs),stat,flush=True);good[a]=[]
 for i,c_ in enumerate(cs[:TRIES]):
  got={};bad=None
  for b in sides(a):
   out,f=follow(a,b,c_['q']);got[b]=out
   if f:bad=f;break
  log.append(dict(anchor=KF[a]['label'],cand=i,start_reserve_mm=round(c_['reserve_mm'],1),cart=round(c_['q'][0],3),ok=bad is None,fail=bad))
  print(' cand',i,'cart',round(c_['q'][0],2),'ok' if bad is None else bad,flush=True)
  if bad is None:
   good[a].append((c_,got))
   if len(good[a])>=KEEP:break
 if not good[a]:anchors[a]=dict(ok=False,n_candidates=len(cs),start_status=stat)
segs=[(a,b,[mm for mm in M if a<mm<b][0]) for a,b in zip(A,A[1:])];pairs={}
for a,b,x in segs:
 for i,(ca,ga) in enumerate(good[a]):
  for j,(cb,gb) in enumerate(good[b]):pairs[(a,b,i,j)]=meet_join(ga[x][-1]['q'],gb[x][-1]['q'],x,plan=False)
 print('joins at',KF[x]['label'],sorted([(round(v['arm_deg']),v['ok']) for v in [pairs[(a,b,i,j)] for i in range(len(good[a])) for j in range(len(good[b]))]])[:6],flush=True)
def dp():
 cost={A[0]:{i:0. for i in range(len(good[A[0]]))}};back={}
 for a,b,x in segs:
  cost[b]={}
  for j in range(len(good[b])):
   opts=[(cv+pairs[(a,b,i,j)]['arm_deg'],i) for i,cv in cost[a].items() if pairs[(a,b,i,j)]['ok']]
   if opts:cost[b][j],back[(b,j)]=min(opts)
 if not cost[A[-1]]:return None
 j=min(cost[A[-1]],key=cost[A[-1]].get);sel={A[-1]:j}
 for a,b,x in reversed(segs):j=back[(b,j)];sel[a]=j
 return sel
sel=dp() if all(good[a] for a in A) else None
if sel is None and KV.get('PLAN') and all(good[a] for a in A):
 for a,b,x in segs:
  blocked=sorted([k_ for k_ in pairs if k_[:2]==(a,b) and not pairs[k_]['ok']],key=lambda k_:pairs[k_]['arm_deg'])
  if any(pairs[k_]['ok'] for k_ in pairs if k_[:2]==(a,b)):continue
  for k_ in blocked[:int(KV.get('PLAN_N',2))]:
   r_=meet_join(good[a][k_[2]][1][x][-1]['q'],good[b][k_[3]][1][x][-1]['q'],x,plan=True);print('planned',KF[x]['label'],k_[2:],r_['ok'],r_.get('method'),flush=True)
   if r_['ok']:pairs[k_]=r_;break
 sel=dp()
if sel is None:sel={a:0 for a in A if good[a]}
for a in A:
 if a in sel:
  c_,got=good[a][sel[a]];anchors[a]=dict(ok=True,cand=sel[a],q=c_['q'],cart=round(c_['q'][0],3),start_reserve_mm=round(c_['reserve_mm'],1))
  for b,out in got.items():pieces[(a,b)]=out
joins={}
for a,b,x in segs:
 if a in sel and b in sel:j=dict(pairs[(a,b,sel[a],sel[b])]);j['at']=KF[x]['label'];j['best_pair_deg']=min(v['arm_deg'] for k_,v in pairs.items() if k_[:2]==(a,b));joins[x]=j
apps=[]
def q_at(k):
 if k in anchors:return anchors[k]['q'] if anchors[k]['ok'] else None
 return next((s_['q'] for out in pieces.values() for s_ in out if s_['kf']==k),None)
for k,world,inw in GR:
 q=q_at(k)
 if q is None:apps.append(dict(ok=False,kf=k,reason='no arm state at this keyframe'));continue
 apps.append(approach(k,world,inw,q))
ok=all(v['ok'] for v in anchors.values()) and len(joins)==len([x for x in M if x>min(A) and x<max(A)]) and all(j['ok'] for j in joins.values()) and all(p_['ok'] for p_ in apps)
play=[];tsum=0.;loads=[];push=None
if ok:
 order=[]
 if A[0]>0:order+=list(reversed(pieces[(A[0],0)]))+[dict(q=anchors[A[0]]['q'],dt=0.)]
 else:order.append(dict(q=anchors[A[0]]['q'],dt=0.))
 for a,b in zip(A,A[1:]):
  x=[mm for mm in M if a<mm<b][0];order+=pieces[(a,x)]
  j=joins[x];order+=[dict(q=qq,dt=j['s']/max(1,len(j['qs']))) for qq in j['qs']]
  back=pieces[(b,x)];order+=[dict(q=s_['q'],dt=s_['dt']) for s_ in reversed(back[:-1])]+[dict(q=anchors[b]['q'],dt=back[0]['dt'])]
 if A[-1]<len(KF)-1:order+=pieces[(A[-1],len(KF)-1)]
 tsum=sum(s_['dt'] for out in pieces.values() for s_ in out)+sum(j['s'] for j in joins.values())+2*.8+sum(p_['time_s'] for p_ in apps)
 play=[s_['q'] for s_ in order]
 for (a,b),out in pieces.items():
  for s_ in out:
   if s_['kf'] is not None:loads.append(load(np.array(s_['q']),s_['kf']))
 for a in A:loads.append(load(np.array(anchors[a]['q']),a))
 if ACT=='press':
  st_=[s_['q'] for out in pieces.values() for s_ in out];st_=st_[::max(1,len(st_)//12)]
  cap=[push_capacity(q) for q in st_];push=dict(min_N=min(cap),per_state_N=cap,note='max downward push the arm can hold on the keyed knob (joint torque envelope, keyed grip 150 N / SF 1.5, PGC moment, cart tip); the tomato wedging force is NOT sourced (R11 open item)')
def summ(out):
 rs=[s_['reserve_mm'] for s_ in out if s_['reserve_mm'] is not None]
 return dict(steps=len(out),time_s=round(sum(s_['dt'] for s_ in out),1),min_reserve_mm=min(rs) if rs else None,max_step_deg=max(s_['step_deg'] for s_ in out),cart=[out[0]['cart'],out[-1]['cart']])
res=dict(act=ACT,obj=OBJ,arm=ARM,grasp_sense=SIGN,layout=J(L),argv=sys.argv[1:],scene=SCENE,ok=ok,time_s=round(tsum,1),elapsed_s=round(time.monotonic()-t0),rinse_dwell_s_est=RINSE,
 method='r17chain.py method (r19prepchain.py docstring); unchanged checker',
 keyframes=[dict(i=i,label=k_['label'],p=np.round(k_['p'],3).tolist(),R=np.round(k_['R'],4).tolist(),c=k_['c'],anchor=k_['anchor'],meet=k_['meet'],dwell_s=k_['dw']) for i,k_ in enumerate(KF)],
 anchors={KF[a]['label']+f'#{a}':{k_:v for k_,v in an.items() if k_!='q'} for a,an in anchors.items()},
 pieces=[dict(frm=KF[a]['label']+f'#{a}',to=KF[b]['label']+f'#{b}',**summ(out)) for (a,b),out in pieces.items()],
 joins=[{k_:v for k_,v in j.items() if k_!='qs'} for j in joins.values()],approaches=[{k_:v for k_,v in p_.items() if k_!='qs'} for p_ in apps],
 min_reserve_mm=min([summ(o)['min_reserve_mm'] for o in pieces.values() if summ(o)['min_reserve_mm'] is not None],default=None),
 max_pgc_moment_Nm=max([l_['pgc_moment_Nm'] for l_ in loads],default=None),max_joint_ratio=max([l_['max_joint_ratio'] for l_ in loads],default=None),
 push=push,loads=loads,tries=log,play=play,approach_qs=[p_.get('qs') for p_ in apps],grasps=[dict(kf=k,world=w,object_in_world=inw) for k,w,inw in GR])
os.makedirs('results/r19/prep',exist_ok=True);fn=f'results/r19/prep/chain_{ACT}'+('_'+KV['TAG'] if 'TAG' in KV else '')+arms.tag(ARM)+'.json';save(fn,res)
print(fn);print(json.dumps({k_:v for k_,v in res.items() if k_ not in ('play','approach_qs','loads','keyframes','tries','layout','scene','grasps')},default=str,ensure_ascii=False))
