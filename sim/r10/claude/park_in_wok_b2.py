"""Park in wok, piece (b) second attempt (Mac, 2026-10-13; new file, edits nothing).
From the stroke-<k> park retreat state (results/mac/park_in_wok_a_<KEY>.json 'retreated_q', jaws open 25 mm, spatula left
in the wok as world geoms exactly as park_in_wok.py) to the CUP endpoint (results/mac/hub_cup/hubs.json) in 3 pieces:
 b1 arm-only at the retreat cart: retreat state -> a low posture P (cart fixed). Straight first, then planner.plan
    (RRT-Connect + staging + shortcuts + full <=4 mm replay, as r19hub.py cmd_edge for cart-fixed edges).
 b2 cart-only: P at the retreat cart -> P at the cart XC (the arm frozen in P).
 b3 P at XC -> CUP: straight, then the r19hub via poses, then planner.plan if XC == CUP cart.
Every state of every piece passes the unchanged checker (r19hub check_path: <=4 mm point bound, fast screen + full
check on every state; planner: its own full <=4 mm replay). Scene = r19hub_cup union scene + the spatula in the wok.
Candidate low postures P: POSES=tuck,ik1,ik2,... ('tuck' = the R19 hub tuck, labels nearest the retreat state;
'ik*' = hand-designed TCP targets solved on the retreat state's IK branch, see LOWS).
(d) = (b) reversed + (a) reversed: the same checked states in reverse order, ending at the stroke-start q.
python park_in_wok_b2.py [KEY=work1] [POSES=tuck] [XC=.172] [PLAN_S=120] [SEED=8]  -> results/mac/park_in_wok_b2_<KEY>.json"""
import sys,os,json,math,time
sys.argv=[sys.argv[0],'none']+sys.argv[1:]
import numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
import r19hub_cup as H
import chain,planner
from scene import build,save,fmt
import kitchen16 as K16
KV=H.KV;KEY=KV.get('KEY','work1');OUTD='results/mac'
ST=json.load(open('results/r19/stir/stirwalk2_h_scrape_dice_r17.json'));SIGN=-1
Q0=np.array(ST['states']['q'][ST['states']['kinds'].index(KEY)],float)
A=json.load(open(f'{OUTD}/park_in_wok_a_{KEY}.json'));QR=np.array(A['retreated_q'],float)
assert A['ok'] and np.allclose(A['stroke_start_q'],Q0)
def spatula_geoms():   # as park_in_wok.py
 sv=dict(K16.TOOL_XY);K16.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K16.TOOL_XY['spider']=(1.52,.36)
 SCN=dict(r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None,'spatula':None})
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_spatula=.45,r15_spatula_jaw=SIGN,**SCN);tree,meta=build(cfg,None)
 m=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));d=mujoco.MjData(m);d.qpos[:]=Q0;mujoco.mj_kinematics(m,d)
 K16.TOOL_XY.clear();K16.TOOL_XY.update(sv)
 tn={mujoco.mjtGeom.mjGEOM_BOX:('box',3),mujoco.mjtGeom.mjGEOM_CYLINDER:('cylinder',2),mujoco.mjtGeom.mjGEOM_CAPSULE:('capsule',2),mujoco.mjtGeom.mjGEOM_SPHERE:('sphere',1),mujoco.mjtGeom.mjGEOM_ELLIPSOID:('ellipsoid',3)}
 out=[]
 for g in range(m.ngeom):
  n=m.geom(g).name
  if not n.startswith('R_gripper_spatula'):continue
  t,ns=tn[m.geom_type[g]];qq=np.zeros(4);mujoco.mju_mat2Quat(qq,d.geom_xmat[g])
  out.append(dict(name='park_'+n[2:],type=t,size=m.geom_size[g][:ns].tolist(),pos=d.geom_xpos[g].tolist(),quat=qq.tolist()))
 return out
SG=spatula_geoms()
def add_spat(world):
 for g in SG:E.SubElement(world,'geom',name=g['name'],type=g['type'],size=fmt(g['size']),pos=fmt(g['pos']),quat=fmt(g['quat']),rgba='.8 .8 .82 1',contype='1',conaffinity='2',mass='.000001')
_ut=H.union_tree
def union_tree_park():
 tree,meta=_ut();add_spat(tree.find('worldbody'));return tree,meta
H.union_tree=union_tree_park
ch=H.union_checker();m,d=ch.m,ch.d;ids=ch.arm_ids;lo=m.jnt_range[:,0];hi=m.jnt_range[:,1];sid=m.site('R_prep').id
def st(q):
 r=ch.check(np.asarray(q,float),full=True,mass=0.);e,s=H.reserve(r);return dict(ok=r['ok'],reserve_mm=None if e is None else round(e,1),self_mm=None if s is None else round(s,1),hits=[h['pair'] for h in r['hits']][:4])
def fk(q):d.qpos[:]=q;mujoco.mj_kinematics(m,d);return d.site_xpos[sid].copy(),d.site_xmat[sid].reshape(3,3).copy()
def near_label(q,ref,joints=None,allowed=None):
 """q relabelled per arm joint by 2pi*k (k in allowed[j] or any k keeping the joint in range) nearest ref."""
 q=np.array(q,float)
 for j in (joints or ids):
  if j==5:continue
  ks=allowed[j] if allowed else [k for k in (-2,-1,0,1,2) if lo[j]-1e-9<=q[j]+H.TWO_PI*k<=hi[j]+1e-9]
  q[j]+=H.TWO_PI*min(ks,key=lambda k:abs(q[j]+H.TWO_PI*k-ref[j]))
 return q
def diag(q,lab):
 d.qpos[:]=q;mujoco.mj_kinematics(m,d);out={}
 for g in range(m.ngeom):
  n=m.geom(g).name
  if n.startswith('R_geom_'):out[n]=np.round(d.geom_xpos[g],3).tolist()
 print('diag',lab,'tcp',np.round(fk(q)[0],3).tolist(),out,flush=True)
T0=time.monotonic()
Hh=H.J('results/mac/hub_cup/hubs.json');TK=np.array(Hh['tuck']['q'],float);ASC=H.allowed_shifts('cup',ch)
CUPRAW=np.array(Hh['endpoints']['CUP']['q_raw'],float)
print('stroke start',np.round(Q0,3).tolist(),'\nretreat',np.round(QR,3).tolist(),st(QR),flush=True)
if KV.get('DIAG'):
 for g in range(m.ngeom):
  n=m.geom(g).name
  if n.startswith(('r07_closed_door','upper_cabinet')):
   print('cab',n,np.round(d.geom_xpos[g],3).tolist(),np.round(m.geom_size[g],3).tolist(),flush=True)
 diag(QR,'QR');diag(np.r_[QR[0],-.21,0.,TK,H.JAW,H.JAW],'tuck@QR')
# ---- candidate low postures (joints 3..8) ----
LOWS={   # hand-designed TCP targets (relative to the cart x; world y, z) with the approach axis (R_prep x) pointing down
 'ik1':((0.10,-.05,1.00),(0,0,-1)),'ik2':((0.0,-.10,.95),(0,0,-1)),'ik3':((0.15,0.0,1.05),(0,0,-1)),'ik4':((0.25,-.05,0.98),(0,0,-1))}
def ik_low(dx,y,z,ax):
 pt=np.array([QR[0]+dx,y,z]);x=np.array(ax,float);_,R0=fk(QR)
 # keep the jaw axis (R_prep y) as close as possible to the retreat's, orthogonalised
 yv=R0[:,1]-x*(R0[:,1]@x);yv/=np.linalg.norm(yv);Rt=np.c_[x,yv,np.cross(x,yv)]
 q=QR.copy();il=ids;l_=lo[il]+1e-6;h_=hi[il]-1e-6
 def res(v):
  q[il]=v;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
  return np.r_[(d.site_xpos[sid]-pt)*10,Rotation.from_matrix(Rt@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
 sol=least_squares(res,np.clip(QR[il],l_,h_),bounds=(l_,h_),max_nfev=400,xtol=1e-10,ftol=1e-10);q[il]=sol.x
 pe,re=ch.pose_error(q,pt,Rt);return q,pe,re
POSES=KV.get('POSES','tuck').split(',');XC=float(KV.get('XC',.172));PLAN_S=float(KV.get('PLAN_S',120));SEED=int(KV.get('SEED',8))
OUT=dict(key=KEY,stroke_start_q=Q0.tolist(),retreated_q=QR.tolist(),xc=XC,scene='r19hub_cup union + spatula in the wok at the stroke start',tries=[])
def piece(lab,qa,qb,plan_ok):
 p=H.check_path(ch,[qa,qb]);tr=dict(piece=lab,method='straight',ok=p['ok'],fail=(p.get('fail') or {}));OUT['tries'].append(tr)
 print(lab,'straight',p['ok'],tr['fail'].get('at'),tr['fail'].get('hits'),round(time.monotonic()-T0),flush=True)
 if p['ok']:mt=H.metrics(ch,p['qs']);return dict(method='straight',qs=p['qs'],min_reserve_mm=min(s['min_reserve_mm'] for s in p['segments']),min_self_mm=min(s['min_self_mm'] for s in p['segments']),states=sum(s['n'] for s in p['segments']),**mt)
 if plan_ok and abs(qa[0]-qb[0])<1e-9:
  stages=[np.r_[qa[:3],TK if True else qa[3:9],qa[9:]]]
  r=planner.plan(ch,qa,qb,budget_s=max(60.,PLAN_S),stages=stages,seed=SEED)
  OUT['tries'].append(dict(piece=lab,method='planner.plan',ok=r['ok'],reason=r.get('reason'),elapsed_s=round(r.get('elapsed_s',0),1),restarts=r.get('restarts'),nodes=r.get('nodes')))
  print(lab,'planner',r['ok'],r.get('reason'),round(r.get('elapsed_s',0)),flush=True)
  if r['ok']:
   rs=[H.reserve(dict(clearance=c)) for c in r['clearance'] if c];mt=H.metrics(ch,r['path'])
   return dict(method='planner.plan (RRT-Connect, staging, shortcuts, full <=4 mm replay)',qs=r['path'],min_reserve_mm=round(min(x for x,_ in rs if x is not None),1),min_self_mm=round(min(s for _,s in rs if s is not None),1),states=len(r['path']),max_step_bound_mm=round(r['step_bound_m']*1000,2),**mt)
 return None
res=None
for pn in POSES:
 if pn=='tuck':P=near_label(np.r_[QR[0],-.21,0.,TK,H.JAW,H.JAW],QR)
 else:
  (dx,y,z),ax=LOWS[pn];P,pe,re=ik_low(dx,y,z,ax);print(pn,'ik pose err mm',round(pe*1000,2),'deg',round(np.degrees(re),2),flush=True)
  if pe>.002:OUT['tries'].append(dict(piece='P',pose=pn,ok=False,fail='ik')) ;continue
 sP=st(P);print('pose',pn,np.round(P,3).tolist(),sP,flush=True);OUT['tries'].append(dict(piece='P',pose=pn,q=P.tolist(),state=sP))
 if not sP['ok']:continue
 b1=piece(f'b1 {pn}',QR,P,True)
 if b1 is None:continue
 PX=P.copy();PX[0]=XC
 b2=piece(f'b2 {pn} cart {QR[0]:.3f}->{XC}',P,PX,False)
 if b2 is None:continue
 qc=near_label(CUPRAW,PX,allowed=ASC);print('CUP labelled',np.round(qc,3).tolist(),st(qc),flush=True)
 b3=piece(f'b3 {pn} -> CUP',PX,qc,True)
 if b3 is None:continue
 res=dict(pose=pn,P=P.tolist(),cup_q=qc.tolist(),pieces=dict(b1=b1,b2=b2,b3=b3));break
if res:
 pcs=res['pieces'];t=round(sum(p['time_s'] for p in pcs.values()),2)   # each piece = one edge (its 0.6 s join included by metrics)
 qs=[list(map(float,q)) for p in ('b1','b2','b3') for q in (pcs[p]['qs'] if p=='b1' else pcs[p]['qs'][1:])]
 for p in pcs.values():p['qs']=[list(map(float,q)) for q in p['qs']]
 a_t=A['jaw_time_s']+A['retreat_time_s'];c_t=20.6
 OUT.update(ok=True,**res,time_b_s=t,min_reserve_mm=min(p['min_reserve_mm'] for p in pcs.values()),min_self_mm=min(p['min_self_mm'] for p in pcs.values()),
  states_checked=sum(p['states'] for p in pcs.values()),qs=qs,
  sequence=dict(a_s=a_t,b_s=t,cup_chain_s=c_t,d_s=round(a_t+t,2),total_s=round(2*(a_t+t)+c_t,2),baseline_s=75.4,
   note='(d) = (b) and (a) in reverse: identical checked states, same time; ends at the stroke-start q (jaws close .025 -> .015 at the end)'))
 print('PASS b',json.dumps({k:v for k,v in OUT.items() if k not in ('qs','tries','pieces','stroke_start_q','retreated_q','P','cup_q')},default=str),{k:{kk:vv for kk,vv in v.items() if kk!='qs'} for k,v in pcs.items()},flush=True)
else:OUT['ok']=False
OUT['elapsed_s']=round(time.monotonic()-T0)
save(f"{OUTD}/park_in_wok_b2_{KEY}{KV.get('TAG','')}.json",OUT);print('elapsed',OUT['elapsed_s'],'ok',OUT['ok'],flush=True)
