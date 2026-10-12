"""R16 whole actions as continuous checked paths (the straight joint-space joins of r16seq.py
collide: lid rim / pot wall, spider / upper cabinet, ladle / pour drum, ...). Each action is a list
of object keyframes (pose + cart x); between them the object moves in a straight line (rotation
slerp) every <= 1 cm / 2° while the cart moves linearly between its keyframe values; the arm
follows by IK continuation from the previous joint vector (as r16walk.py), and the unchanged
checker runs at every step (full Bounds check every 5th step and at every keyframe).
ANCHORS: every station (pot, rest, rack, plate spot) starts from its own r16walk result (same
design, same grasp sense), because one continuation through all stations arrives at the next
station on the wrong arm branch (runs 1-2: lid / upper arm, carrier / hood, ladle / cart mast).
From each anchor the path is followed to the MEET keyframes in the open travel lane on either
side; there the two arm states are joined by a straight joint-space move (cart fixed), checked
every <= 1° of the largest joint. Two anchors without a meet between them are joined at the
second anchor (continuation state -> that anchor's walk state).
Lane: the object 0-0.13 m behind the counter edge, below the hood where it is under it; in the
lane the cart stays CART_OFF = 0.30 m left of the object (crossing over the arm's own base hit
it: spider / base plate, ladle / cart mast). The cart moves WITH the arm working (every step
checked); the R10 dock carry envelope (chain.dock_carry: everything within 0.40 m of the cart
along x and <= 0.10 m over the counter edge while the cart moves) is reported, not enforced.
Timing: TCP <= 0.10 m/s, rotation <= 45°/s, every joint <= 60°/s, cart <= 0.25 m/s (the slowest
governs each step), joins at 60°/s + 0.6 s, + grasp / release 0.8 s each, + dwells (ASSUMPTIONS
as in r16seq.py).
python r16chain.py ACT=lid|plate_in|spider|ladle [MEETSP=x,y,z: spider branch-change point] [PLAN=1 PLAN_S=120: plan blocked joins] [TAG=..] -> results/r16/chain_<ACT>[_TAG].json"""
import sys,os,json,numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation,Slerp
import chain
from scene import build,save
from checker import Checker
import kitchen15 as K15,kitchen16 as K
KV=dict(a.split('=',1) for a in sys.argv[1:]);ACT=KV['ACT']
DESIGN=dict(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.set_design(**DESIGN)
VW,WW,QW,CW,CART_OFF=.10,45.,60.,.25,.30
def W(n):return json.load(open(f'results/r16/walk_{n}.json'))
def rolled(name,R,p,deg):
 o=K.OBJ[name];g=p+R@o['grip'];ax=R@o['a'];Rr=Rotation.from_rotvec(ax*np.radians(deg)).as_matrix();return Rr@R,g+Rr@(p-g)
I=np.eye(3);PC=np.array(K15.PLATE['c'],float);PX,PY=K.POT['c'][0],K.POT['c'][1]
def kf(R,p,c=None,dw=0.,label='',anchor=None,meet=False):
 """Keyframe: pose, cart x (None: lane rule, CART_OFF left of the object), dwell, label,
 anchor (walk result name and path index whose pose is this keyframe), meet point."""
 p=np.asarray(p,float);return dict(R=R,p=p,c=float(np.clip(p[0]-CART_OFF,-1.48,1.46)) if c is None else c,dw=dw,label=label,anchor=anchor,meet=meet)
def action():
 fl=K.POT['c'][2]+.002+K.POT['rack']
 if ACT=='lid':   # off the pot, slid out of the hood, up in front of the hood, rolled upright, carried high to the rack
  R2,p2=K.lid_on({});Rk,pk=K.pose('lid','rack');hi=p2+[0,-.23,.27];Rr,pr=rolled('lid',R2,hi,90);c0=W('lid_off_pot_f')['cart_x'];ck=W('lid_park_f90')['cart_x']
  return 'lid',{},[kf(R2,p2+[0,0,.008],c0,0,'lift off',('lid_off_pot_f',0)),kf(R2,p2+[0,0,.02],c0),kf(R2,p2+[0,-.23,.02],c0,0,'slide out'),kf(R2,hi,c0,0,'up'),kf(Rr,pr,c0,0,'roll 90 deg'),
   kf(Rr,[pr[0]+.12,-.10,1.36],None,0,'carry',meet=True),kf(Rk,[pk[0],-.10,1.36],ck),kf(Rk,pk+[0,0,.08],ck,0,'over the rack',('lid_park_f90',0)),kf(Rk,pk+[0,0,.004],ck,0,'in the rack')],'lid_off_pot_f'
 if ACT=='plate_in':   # plate spot -> lane -> in over the pot front rim -> onto the rack in the pot
  Rs,ps=K.pose('carrier','stage');Rp,pp=K.pose('carrier','pot');cs=W('carrier_stage_f')['cart_x'];cp=W('carrier_pot_f')['cart_x'];zr=K.POT_TOP+.01
  return 'carrier',dict(r15_plate=False,r16_lid='rack'),[kf(Rs,ps+[0,0,.008],cs,0,'pick'),kf(Rs,ps+[0,0,.08],cs),kf(Rs,[ps[0],0,1.16],cs,0,'lane'),
   kf(Rs,[(ps[0]+PX)/2,0,1.16],(cs+cp)/2,0,'lane middle'),kf(Rs,[PX,0,1.16],cp,0,'lane at the pot'),kf(Rs,[PX,0,zr],cp),kf(Rp,[PX,PY,zr],cp,0,'in over the pot',('carrier_pot_f',0)),
   kf(Rp,pp+[0,0,.008],cp,0,'on the rack')],'carrier_pot_f'
 if ACT=='spider':   # rest -> up -> forward -> lane -> pot (scoop, drain) -> lane -> plate (tip) -> lane -> back
  Rt,pt=K.pose('spider','rest');bs=np.array([PX,PY+.02,fl+.035]);ds=PC+[0,0,K15.PLATE['h']+.16];Rd,pd=rolled('spider',I,ds,-110)
  ct=W('rest_spider_f3')['cart_x'];cl=W('spider_lift_f')['cart_x'];cd=W('spider_dump_fL')['cart_x'];MS=np.array([float(v) for v in KV.get('MEETSP','1.40,0,1.30').split(',')])   # where the arm changes branch between the rest and the pot
  return 'spider',dict(r16_lid='rack'),[kf(Rt,pt+[0,0,.008],ct,0,'pick',('rest_spider_f3',0)),kf(Rt,pt+[0,0,.03],ct),kf(Rt,[pt[0],.40,1.0],ct,0,'out'),kf(Rt,[pt[0],.25,1.22],ct,0,'up and forward'),kf(I,[pt[0],0,1.22],ct,0,'forward'),kf(I,[pt[0],0,1.30],ct),
   kf(I,MS,None,0,'branch change',meet=True),kf(I,[1.30,0,1.12],cl,0,'lane'),kf(I,bs+[0,0,.12],cl,0,'over the pot'),kf(I,bs,cl,0,'scoop',('spider_lift_f',0)),kf(I,bs+[0,0,.12],cl,5.,'drain'),
   kf(I,[PX,0,1.12],cl,0,'lane'),kf(I,[(PX+ds[0])/2,0,1.12],None,0,'lane middle',meet=True),kf(I,[ds[0],0,1.12],cd),kf(I,ds,cd,0,'over the plate',('spider_dump_fL',0)),kf(Rd,pd,cd,0,'tip 110 deg'),
   kf(I,ds,cd,0,'level again'),kf(I,[ds[0],0,1.12],cd,0,'lane'),kf(I,[(PX+ds[0])/2,0,1.12],None,0,'lane middle'),kf(I,[1.30,0,1.12],None),kf(I,MS,None,0,'branch change',meet=True),
   kf(I,[pt[0],0,1.30],ct,0,''),kf(I,[pt[0],0,1.22],ct),kf(Rt,[pt[0],.25,1.22],ct,0,'back'),kf(Rt,[pt[0],.40,1.0],ct),kf(Rt,pt+[0,0,.03],ct),kf(Rt,pt+[0,0,.008],ct,0,'on the rest',('rest_spider_f3',0))],'spider_lift_f'
 if ACT=='ladle':   # rest -> lane -> pot (scoop) -> lane -> soup bowl (pour) -> lane -> pot -> ... -> back
  Rl,pl=K.pose('ladle','rest');bl=np.array([PX,PY,fl+.035]);dl=PC+[0,0,K.BOWL['h']+.085];Rq,pq=rolled('ladle',I,dl,-100)
  ctl=W('rest_ladle_f3')['cart_x'];cll=W('ladle_lift_f3')['cart_x'];cdl=W('ladle_pour_f3m')['cart_x']
  pot=[kf(I,[PX,0,1.10],cll,0,'lane'),kf(I,bl+[0,0,.10],cll,0,'over the pot'),kf(I,bl,cll,0,'scoop',('ladle_lift_f3',0)),kf(I,bl+[0,0,.10],cll),kf(I,[PX,0,1.10],cll,0,'lane')]
  bowl=[kf(I,[(PX+dl[0])/2,0,1.10],None,0,'lane middle',meet=True),kf(I,[dl[0],0,1.10],cdl),kf(I,dl,cdl,0,'over the bowl',('ladle_pour_f3m',0)),kf(Rq,pq,cdl,1.5,'pour'),kf(I,dl,cdl),
   kf(I,[dl[0],0,1.10],cdl,0,'lane'),kf(I,[(PX+dl[0])/2,0,1.10],None,0,'lane middle',meet=True)]
  head=[kf(Rl,pl+[0,0,.008],ctl,0,'pick',('rest_ladle_f3',0)),kf(Rl,pl+[0,0,.06],ctl),kf(I,[pl[0],0,pl[2]+.06],ctl,0,'forward low'),kf(I,[pl[0],0,1.30],ctl,0,'up'),kf(I,[1.40,0,1.30],None,0,'',meet=True)]
  tail=[kf(I,[1.40,0,1.30],None,0,'',meet=True),kf(I,[pl[0],0,1.30],ctl),kf(I,[pl[0],0,pl[2]+.06],ctl),kf(Rl,pl+[0,0,.06],ctl),kf(Rl,pl+[0,0,.008],ctl,0,'on the rest',('rest_ladle_f3',0))]
  return 'ladle',dict(r16_lid='rack',r15_plate=False,r16_bowl=True),head+pot+bowl+pot+tail,'ladle_lift_f3'
OBJ,SCENE,KF,SIGNW=action()
sign=W(SIGNW)['jaw_sign']
for k_ in KF:
 if k_['anchor'] and W(k_['anchor'][0])['jaw_sign']!=sign:raise SystemExit(f"grasp sense of {k_['anchor'][0]} differs from {SIGNW}")
cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,r16_held=dict(obj=OBJ,T_tool_obj=K.T_tool_obj(OBJ,sign).tolist()),**SCENE)
tree,meta=build(cfg,None);ch=Checker(tree,meta);m,d=ch.m,ch.d;ids=ch.arm_ids;sid=m.site('R_prep').id
lo=np.array([m.jnt_range[j,0] for j in range(m.njnt)])[ids];hi_=np.array([m.jnt_range[j,1] for j in range(m.njnt)])[ids]
def solve_to(q,R,p):
 pt_,Rt_=K.tcp_pose(OBJ,R,p,sign)
 def res(x):
  q[ids]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
  return np.r_[(d.site_xpos[sid]-pt_)*10,Rotation.from_matrix(Rt_@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
 x0=np.clip(q[ids],lo+1e-8,hi_-1e-8);sol=least_squares(res,x0,bounds=(lo+1e-9,hi_-1e-9),max_nfev=200,xtol=1e-10,ftol=1e-10)
 q[ids]=sol.x;pe,re=ch.pose_error(q,pt_,Rt_);return q,pe,re,float(np.degrees(np.max(abs(sol.x-x0))))
def state(q,full):
 c=ch.check(q,full=full,mass=0.);rmin=min((v['reserve_mm'] for cat,v in c['clearance'].items() if cat!='self'),default=None) if full else None
 return c['hits'],rmin
def follow(a,b,q):
 """Keyframes a -> b (indices, either direction) from joint vector q at KF[a]."""
 q=np.array(q,float);out=[];st=1 if b>a else -1
 for i in range(a,b,st):
  A_,B_=KF[i],KF[i+st];ang=np.degrees(np.linalg.norm(Rotation.from_matrix(B_['R']@A_['R'].T).as_rotvec()));dist=np.linalg.norm(B_['p']-A_['p'])
  n=max(1,int(np.ceil(max(dist/.01,ang/2,abs(B_['c']-A_['c'])/.01))));sl=Slerp([0,1],Rotation.from_matrix([A_['R'],B_['R']]))
  for k in range(1,n+1):
   q[0]=A_['c']+(B_['c']-A_['c'])*k/n;q,pe,re,dq=solve_to(q,sl(k/n).as_matrix(),A_['p']+(B_['p']-A_['p'])*k/n)
   hits,rmin=state(q,k%5==0 or k==n);env=None if abs(B_['c']-A_['c'])<1e-9 else bool(chain.dock_carry(ch,q))
   dt=max(dist/n/VW,ang/n/WW,dq/QW,abs(B_['c']-A_['c'])/n/CW)+(KF[i+st]['dw'] if k==n and st>0 else 0.)+(KF[i]['dw'] if k==1 and st<0 else 0.)
   out.append(dict(seg=f"{A_['label']}->{B_['label']}",cart=round(q[0],3),step_deg=round(dq,2),pose_mm=round(pe*1000,2),reserve_mm=None if rmin is None else round(rmin,1),carry_env=env,dt=dt,hits=[h['pair'] for h in hits][:3],q=q.tolist()))
   if pe>.005 or re>np.radians(3) or hits or dq>10:return out,out[-1]
 return out,None
def join(qa,qb):
 """Straight joint-space move qa -> qb (cart fixed), checked every <= 1° of the largest joint. The
 UR5e joints turn +-360°: a target a full turn away is the same pose, so each joint takes the
 nearest equivalent angle that stays in its range."""
 qa,qb=np.array(qa),np.array(qb)
 for j in range(6):
  c=[qb[3+j]+k*2*np.pi for k in (-2,-1,0,1,2) if lo[j]-1e-9<=qb[3+j]+k*2*np.pi<=hi_[j]+1e-9];qb[3+j]=min(c,key=lambda v:abs(v-qa[3+j]))
 dq=np.degrees(np.max(abs(qb[3:9]-qa[3:9])));n=max(1,int(np.ceil(dq)))
 for k in range(1,n):
  hits,_=state(qa+(qb-qa)*k/n,False)
  if hits:
   if KV.get('PLAN'):   # straight swing blocked: RRT-Connect (planner.py, full bounded replay), arm only, cart fixed
    import planner;ch.active=ch.arm_ids;r=planner.plan(ch,qa,qb,budget_s=float(KV.get('PLAN_S',120)),seed=8)
    if r['ok']:
     P=np.array(r['path']);sweep=float(np.degrees(np.sum(np.max(abs(np.diff(P[:,3:9],axis=0)),axis=1))))
     return dict(ok=True,method='planned',arm_deg=round(float(dq),1),path_joint_deg=round(sweep,1),s=round(sweep/QW+.6,2),plan_s=round(r['elapsed_s'],1))
    return dict(ok=False,method='planner failed',arm_deg=round(float(dq),1),reason=r.get('reason'))
   return dict(ok=False,arm_deg=round(float(dq),1),at=round(k/n,2),hits=[h['pair'] for h in hits][:3])
 return dict(ok=True,arm_deg=round(float(dq),1),s=round(dq/QW+.6,2))
A=[i for i,k_ in enumerate(KF) if k_['anchor']];M=[i for i,k_ in enumerate(KF) if k_['meet']]
def aq(i):n,j=KF[i]['anchor'];return W(n)['path'][j]['q']
pieces=[];joins=[];arrive={}
def run(a,b):
 out,f=follow(a,b,aq(a));pieces.append(dict(frm=KF[a]['label'],to=KF[b]['label'],steps=len(out),time_s=round(sum(s_['dt'] for s_ in out),1),
  min_reserve_mm=min([s_['reserve_mm'] for s_ in out if s_['reserve_mm'] is not None],default=None),max_step_deg=max([s_['step_deg'] for s_ in out],default=0),
  cart_moving_steps=sum(1 for s_ in out if s_['carry_env'] is not None),carry_env_violations=sum(1 for s_ in out if s_['carry_env'] is False),fail=None if f is None else {k:v for k,v in f.items() if k!='q'}))
 if f is None:arrive.setdefault(b,[]).append(out[-1]['q'])
if A[0]>0:run(A[0],0)
for a,b in zip(A,A[1:]):
 mt=[x for x in M if a<x<b]
 if mt:run(a,mt[0]);run(b,mt[-1])
 else:
  run(a,b)
  if b in arrive:arrive[b].append(aq(b))
if A[-1]<len(KF)-1:run(A[-1],len(KF)-1)
for key,qs in arrive.items():
 if len(qs)==2:j=join(*qs);j['at']=KF[key]['label'];joins.append(j)
ok=all(p_['fail'] is None for p_ in pieces) and all(j['ok'] for j in joins)
t=sum(p_['time_s'] for p_ in pieces)+sum(j.get('s',0) for j in joins)+2*.8
res=dict(act=ACT,obj=OBJ,design=DESIGN,grasp_sense=sign,ok=ok,time_s=round(t,1),pieces=pieces,joins=joins,
 min_reserve_mm=min([p_['min_reserve_mm'] for p_ in pieces if p_['min_reserve_mm'] is not None],default=None),
 carry_env_violations=sum(p_['carry_env_violations'] for p_ in pieces),cart_moving_steps=sum(p_['cart_moving_steps'] for p_ in pieces))
os.makedirs('results/r16',exist_ok=True);save(f'results/r16/chain_{ACT}'+('_'+KV['TAG'] if 'TAG' in KV else '')+'.json',res)
print(json.dumps(res,default=str,ensure_ascii=False))
