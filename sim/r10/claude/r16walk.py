"""R16 handling checks for the second heat zone (kitchen16.py): one held object moved along a
named path of object poses, docked cart fixed, UR5e + PGC + R12 fingers.
Start: 96-start collision-aware IK (solver.solve, SEEDS seeds x 2 jaw senses) at the first pose.
Then IK continuation as in r15tipwalk.py: every 1 cm / 2° step starts the pose-only least-squares
IK from the previous joint vector, so the arm stays on its branch, and the unchanged checker
(10 mm robot-environment, 5 mm gripper/held-environment, joint ranges, rated load) runs at
every step (full Bounds check every 5th step and at the last). Start candidates are tried best
reserve first until one walks to the end.
Held load (own model, as r15reach.py pour): object mass at its centre of mass -> joint torque
ratios vs the rated envelope and the moment about the TCP vs the PGC's 7 N.m, at the first and
last pose.
Paths (object, scene, poses):
 lid_off      lid 8 mm over the steamer tier (carrier inside) -> up 2 cm -> toward the robot 23 cm -> up 10 cm
 lid_off_pot  the same on the bare pot (soup / blanching)
 lid_park     lid upright 8 cm above the rack -> 4 mm over the rack
 lid_roll     lid_off's last pose -> up 18 cm more (clear of the pot) -> rolled 90° about the approach axis
 carrier_in   carrier 14 cm above the tier floor -> 8 mm over it (out = the same path reversed)
 carrier_pot  (RACK set: steaming rack in the pot, no tier) carrier ring 1 cm over the pot rim -> 8 mm over the rack
 carrier_stage carrier 8 cm above the plate spot -> 8 mm over the counter (staging / serving spot)
(the last / first 8 mm of a place / pick are a support contact phase, not checked here)
 spider_lift  spider bowl 15 mm off the pot bottom -> up 16 cm (drain over the pot)
 spider_dump  spider bowl 14 cm over a plate at the plate spot -> rolled ROLL (default 110°) about the handle
 ladle_lift   ladle bowl 10 mm off the pot bottom -> up 16 cm
 ladle_pour   ladle bowl 6 cm over the soup bowl at the plate spot -> rolled 100° about the handle
 rest_<tool>  tool 8 mm above its rest (the grasp is made with the tool on the rest; the first mm
              are a contact phase) -> lifted 6 cm (tool = spider | ladle | spatula)
python r16walk.py PATH=<name> [SEEDS=2] [TRIES=12] [CARTX=..] [ROLL=deg] [LROLL=ladle roll deg] [SIGN=1|-1: one grasp sense]
 [POT_Y=m] [LID_A=deg] [CAR_A=deg] [POT_H=m] [RACK=m] [RACK_RY=-90|90] (kitchen16.set_design sweep) [TAG=..] -> results/r16/walk_<PATH>[_TAG].json"""
import sys,os,json,numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation,Slerp
import chain
from scene import build,save
from checker import Checker
from solver import solve
import kitchen15 as K15,kitchen16 as K
KV=dict(a.split('=',1) for a in sys.argv[1:]);K.set_design(*(float(KV[k]) if k in KV else None for k in ('POT_Y','LID_A','CAR_A','POT_H','RACK','RACK_RY')));NAME=KV['PATH'];SEEDS=(14,15)[:int(KV.get('SEEDS',2))];TRIES=int(KV.get('TRIES',12))
MASS=dict(lid=(.8,[0,0,.025]),carrier=(1.7,[0,0,.036]),spider=(.45,[0,0,0]),ladle=(.35,[0,0,0]),spatula=(.3,None))   # kg, CoG in the object frame (estimates)
def up(R,p,dz):return R,p+[0,0,dz]
def rolled(name,R,p,deg,n=None):
 """Object pose rolled by deg about the tool's handle (approach) axis through the grip point."""
 o=K.OBJ[name];g=p+R@o['grip'];ax=R@o['a'];Rr=Rotation.from_rotvec(ax*np.radians(deg)).as_matrix();return Rr@R,g+Rr@(p-g)
PC=np.array(K15.PLATE['c'],float)
def paths():
 sc_steam=dict(r16_tier=True,r16_carrier='tier');sc_pot=dict(r16_lid='rack')
 R,p=K.lid_on(dict(r16_tier=True));R2,p2=K.lid_on({})
 Rk,pk=K.pose('lid','rack');Rc,pc=K.pose('carrier','tier');Rs,ps=K.pose('carrier','stage')
 Rp,pp=K.pose('carrier','pot') if K.POT['rack'] else (None,None);rim_up=K.POT_TOP+.01-pp[2] if K.POT['rack'] else None
 fl=K.POT['c'][2]+.002+(K.POT['rack'] or 0)   # pot floor, or the steaming rack's top when it stays in the pot
 # spider bowl further back in a deep pot so its 45° handle clears the front rim
 bs=np.array([K.POT['c'][0],K.POT['c'][1]+(.04 if K.POT['h']>.13 else .02),fl+.02+.015]);bl=np.array([K.POT['c'][0],K.POT['c'][1],fl+.025+.01])
 ds=PC+[0,0,K15.PLATE['h']+.02+.14];ROLL=float(KV.get('ROLL',110));LROLL=float(KV.get('LROLL',100));dl=PC+[0,0,K.BOWL['h']+.025+.06]
 P=dict(lid_off=('lid',sc_steam,[up(R,p,.008),up(R,p,.02),(R,p+[0,-.23,.02]),(R,p+[0,-.23,.12])]),
  lid_off_pot=('lid',{},[up(R2,p2,.008),up(R2,p2,.02),(R2,p2+[0,-.23,.02]),(R2,p2+[0,-.23,.12])]),
  lid_park=('lid',dict(r16_lid=None),[up(Rk,pk,.08),(Rk,pk+[0,0,.004])]),
  lid_roll=('lid',dict(r16_lid=None),[(R2,p2+[0,-.23,.12]),(R2,p2+[0,-.23,.30]),rolled('lid',R2,p2+[0,-.23,.30],-90 if K.RACK['ry']<0 else 90)]),
  carrier_in=('carrier',dict(r16_tier=True,r16_lid='rack'),[up(Rc,pc,.14),up(Rc,pc,.008)]),
  carrier_pot=('carrier',dict(r16_lid='rack'),[up(Rp,pp,rim_up),up(Rp,pp,.008)]) if K.POT['rack'] else None,
  carrier_stage=('carrier',dict(r15_plate=False,r16_lid='rack'),[up(Rs,ps,.08),up(Rs,ps,.008)]),
  spider_lift=('spider',sc_pot,[(np.eye(3),bs),(np.eye(3),bs+[0,0,.16])]),
  spider_dump=('spider',sc_pot,[(np.eye(3),ds),rolled('spider',np.eye(3),ds,ROLL/2),rolled('spider',np.eye(3),ds,ROLL)]),
  ladle_lift=('ladle',sc_pot,[(np.eye(3),bl),(np.eye(3),bl+[0,0,.16])]),
  ladle_pour=('ladle',dict(sc_pot,r15_plate=False,r16_bowl=True),[(np.eye(3),dl),rolled('ladle',np.eye(3),dl,LROLL/2),rolled('ladle',np.eye(3),dl,LROLL)]))
 for t in ('spider','ladle','spatula'):Rt,pt=K.pose(t,'rest');P['rest_'+t]=(t,sc_pot,[up(Rt,pt,.008),up(Rt,pt,.06)])
 return P
OBJ,SCENE,WPS=paths()[NAME]
def steps(wps):
 """Object poses every <= 1 cm / 2° along the waypoints."""
 out=[wps[0]]
 for (Ra,pa),(Rb,pb) in zip(wps,wps[1:]):
  ang=np.degrees(np.linalg.norm(Rotation.from_matrix(Rb@Ra.T).as_rotvec()));n=max(1,int(np.ceil(max(np.linalg.norm(pb-pa)/.01,ang/2))))
  sl=Slerp([0,1],Rotation.from_matrix([Ra,Rb]))
  out+=[(sl(k/n).as_matrix(),pa+(pb-pa)*k/n) for k in range(1,n+1)]
 return out
POSES=steps(WPS)
def model(sign):
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,r16_held=dict(obj=OBJ,T_tool_obj=K.T_tool_obj(OBJ,sign).tolist()),**SCENE)
 tree,meta=build(cfg,None);return Checker(tree,meta)
def load(ch,q,R,p):
 m_,c=MASS[OBJ]
 if c is None:return None
 m,d=ch.m,ch.d;d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d);com=p+R@np.array(c)
 sid=m.site('R_prep').id;bid=m.site_bodyid[sid];jp=np.zeros((3,m.nv));jr=jp.copy();mujoco.mj_jac(m,d,jp,jr,com,bid)
 tau=d.qfrc_bias-jp.T@np.array([0,0,-m_*9.81]);ratios={n:float(abs(tau[ch.da[n]])/v) for n,v in ch.env.items()}
 return dict(held_kg=m_,max_joint_ratio=round(max(ratios.values()),3),pgc_moment_Nm=round(float(np.linalg.norm(np.cross(com-d.site_xpos[sid],[0,0,-m_*9.81]))),2),pgc_limit_Nm=7)
def walk(ch,sign,q0):
 m,d=ch.m,ch.d;ids=ch.arm_ids;sid=m.site('R_prep').id
 lo=np.array([m.jnt_range[j,0] for j in range(m.njnt)])[ids];hi=np.array([m.jnt_range[j,1] for j in range(m.njnt)])[ids]
 q=np.array(q0,float);path=[];worst=0.;minres=1e9
 for k,(R,p) in enumerate(POSES):
  pt,Rt=K.tcp_pose(OBJ,R,p,sign)
  def res(x):
   q[ids]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
   return np.r_[(d.site_xpos[sid]-pt)*10,Rotation.from_matrix(Rt@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
  x0=np.clip(q[ids],lo+1e-8,hi-1e-8);sol=least_squares(res,x0,bounds=(lo+1e-9,hi-1e-9),max_nfev=200,xtol=1e-10,ftol=1e-10)
  q[ids]=sol.x;pe,re=ch.pose_error(q,pt,Rt);stepd=float(np.degrees(np.max(abs(sol.x-x0))));worst=max(worst,stepd)
  full=k%5==0 or k==len(POSES)-1;chk=ch.check(q,full=full,mass=0.)
  rmin=min((v['reserve_mm'] for cat,v in chk['clearance'].items() if cat!='self'),default=None) if full else None
  ok=pe<=.005 and re<=np.radians(3) and not chk['hits']
  path.append(dict(k=k,step_deg=round(stepd,2),pose_mm=round(pe*1000,2),ok=bool(ok),reserve_mm=None if rmin is None else round(rmin,1),hits=[h['pair'] for h in chk['hits']][:3],q=q.tolist()))
  if rmin is not None:minres=min(minres,rmin)
  if not ok:return False,path,worst,minres
 return True,path,worst,minres
cands=[];stat={};models={}
for sign in ((int(KV['SIGN']),) if 'SIGN' in KV else (1,-1)):
 ch=models[sign]=model(sign);pt,Rt=K.tcp_pose(OBJ,*POSES[0],sign)
 for seed in SEEDS:
  t=dict(name=NAME,points=[list(pt)]*2,held=None,kind='transfer',force=None,approach=list(Rt[:,0]),jaws=[tuple(sign*(POSES[0][0]@K.OBJ[OBJ]['j']))],jaw_q=.015)
  if 'CARTX' in KV:t['cart_x']=float(KV['CARTX'])
  r=solve(ch,pt,list(Rt[:,0]),target=t,seed=seed)
  for k_,v in r['status_counts'].items():stat[k_]=stat.get(k_,0)+v
  cands+=[dict(q=c['q'],reserve_mm=c['reserve_mm'],jaw_sign=sign) for c in r['candidates']]
  if not r['ok'] and not stat.get('blockers'):stat['blockers']=sorted({tuple(h['pair']) for row in r['rows'] if row.get('check') for h in row['check'].get('hits',[])},key=str)[:10]
print(NAME,'start candidates',len(cands),stat,flush=True)
best=None;tries=[]
for i,c in enumerate(sorted(cands,key=lambda c:-c['reserve_mm'])[:TRIES]):
 ok,path,worst,minres=walk(models[c['jaw_sign']],c['jaw_sign'],c['q'])
 tries.append(dict(start_reserve_mm=round(c['reserve_mm'],1),ok=ok,stop=None if ok else dict(k=path[-1]['k'],hits=path[-1]['hits'],pose_mm=path[-1]['pose_mm'])))
 print(i,'ok' if ok else f"stops at step {path[-1]['k']}/{len(POSES)-1} {path[-1]['hits'] or path[-1]['pose_mm']}",'max step/°',round(worst,2),flush=True)
 if ok and (best is None or worst<best[1]):best=(path,worst,minres,c)
 if ok and worst<3:break
res=dict(path_name=NAME,obj=OBJ,scene=SCENE,n_steps=len(POSES)-1,n_start_candidates=len(cands),start_status=stat,ok=best is not None,tries=tries)
if best:
 path,worst,minres,c=best;ch=models[c['jaw_sign']]
 dist=sum(np.linalg.norm(b_[1]-a_[1]) for a_,b_ in zip(POSES,POSES[1:]))
 res.update(jaw_sign=c['jaw_sign'],cart_x=round(path[0]['q'][0],3),max_joint_step_deg=round(worst,2),min_reserve_mm=round(minres,1),object_travel_m=round(float(dist),3),
  load_first=load(ch,np.array(path[0]['q']),*POSES[0]),load_last=load(ch,np.array(path[-1]['q']),*POSES[-1]),path=path)
os.makedirs('results/r16',exist_ok=True);save(f'results/r16/walk_{NAME}'+('_'+KV['TAG'] if 'TAG' in KV else '')+'.json',res)
print(json.dumps({k:v for k,v in res.items() if k not in ('path','tries')},default=str))
