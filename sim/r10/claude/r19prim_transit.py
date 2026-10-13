"""R19 hub transits: the free moves of the empty arm between the checked actions of the plating sequence
(r17seq.py: spatula rest -> faucet -> wok -> faucet -> spatula rest) are only ESTIMATED today
(|dx|/0.25 + 1 + 1.6 s, never collision checked). Here they are checked as library transits between
hub states taken from the saved chains:
 H_spat_pre  spatula rest pre-grasp (chain_spatula ... approach end, jaws open, cart -1.48)
 H_fau_closed_pre / H_fau_open_post  faucet lever pre-grasp (closed) / post-release (open), chain_lever
 H_wok_pre   wok pre-grasp at the cooker (chain_wok_s-1_final approach end; the chain starts and ends there)
Candidate paths per transit (cart and the 6 joints linear, nearest equivalent angles): direct, joints
first then cart, cart first then joints, and via a raised travel posture (the target or source posture
with the shoulder lift and elbow moved toward a folded pose). Each candidate is checked with the
unchanged checker (empty gripper, jaws open, the scene of that moment: spatula on its R18b rest, faucet
lever closed or open, wok on the cooker) every <= 1 deg of the largest joint and <= 1 cm of cart (the
r17chain.py meet-join standard), full clearance every 10th state and at the ends. Time: joints <= 60 deg/s, cart
<= 0.25 m/s per step, + 0.6 s per straight piece (r17chain.py join timing).
python r19prim_transit.py [PLAN=1 PLAN_S=100] [ONLY=rest_to_faucet|faucet_to_wok|wok_to_faucet|faucet_to_rest] -> results/r19/prim/transit.json (entries updated in place)"""
import sys;sys.path.insert(0,'.')
import json,os,time,numpy as np
import chain
from scene import build
from checker import Checker
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
QW,CW=60.,.25
KV=dict(a.split('=',1) for a in sys.argv[1:])
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)
K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=8.,0.,180.   # the R18b rest
L=lambda f:json.load(open(f'results/r17/chain_{f}.json'))
spat,lev,wok=L('spatula_s-1_r18roll-1.15_.30'),L('lever_s+1_final'),L('wok_s-1_final')
H=dict(H_spat_pre=np.array(spat['approach_qs'][0][-1]),H_fau_closed_pre=np.array(lev['approach_qs'][0][-1]),H_fau_open_post=np.array(lev['approach_qs'][1][-1]),H_wok_pre=np.array(wok['approach_qs'][0][-1]))
for k,v in H.items():v[-2:]=.025
_m={}
def model(lever):
 if lever not in _m:
  cfg=chain.chain_cfg('SD',**{**BASE,'r16_tools':{'ladle':None},'r17_lever':lever});tree,meta=build(cfg,None);_m[lever]=Checker(tree,meta)
 return _m[lever]
def near(a,b):
 b=b.copy();b[3:9]=a[3:9]+(b[3:9]-a[3:9]+np.pi)%(2*np.pi)-np.pi;return b
def check_line(ch,a,b,out):
 d=b-a;k=max(1,int(np.ceil(max(abs(d[0])/.01,np.degrees(np.abs(d[3:9])).max()))));rmin=1e9;t=0.
 for s in range(1,k+1):
  q=a+d*s/k;full=(s%10==0 or s==k);c=ch.check(q,full=full,mass=0.)
  if full:rmin=min(rmin,min((v['reserve_mm'] for cat,v in c['clearance'].items() if cat!='self'),default=1e9))
  if c['hits']:return False,dict(at=round(s/k,3),hits=[h['pair'] for h in c['hits']][:3])
  out.append(q)
 t=max(np.degrees(np.abs(d[3:9])).max()/QW,abs(d[0])/CW)+.6
 return True,dict(states=k,time_s=round(t,2),min_reserve_mm=round(rmin,1))
def path(ch,pts):
 out=[];info=[];a=pts[0]
 for b in pts[1:]:
  ok,i=check_line(ch,a,b,out);info.append(i)
  if not ok:return False,info,out
  a=b
 return True,info,out
def candidates(a,b):
 b=near(a,b);c=[('direct',[a,b])]
 m1=b.copy();m1[0]=a[0];c.append(('joints then cart',[a,m1,b]))
 m2=a.copy();m2[0]=b[0];c.append(('cart then joints',[a,m2,b]))
 for nm,base in (('raised source posture',a),('raised target posture',b)):   # shoulder lift up 20 deg, elbow folded 20 deg more, then cart, then down
  for sl in (+1,-1):
   r=base.copy();r[4]+=sl*np.radians(20);r[5]-=np.sign(base[5])*np.radians(20)
   ra=r.copy();ra[0]=a[0];rb=r.copy();rb[0]=b[0];c.append((f'{nm} ({"+" if sl>0 else "-"}lift)',[a,ra,rb,b]))
 w1=a.copy();w1[6:9]=b[6:9];c.append(('wrist joints first',[a,w1,b]))   # the self-contact (wrist link vs finger) comes from interpolating all joints at once
 w2=b.copy();w2[6:9]=a[6:9];c.append(('wrist joints last',[a,w2,b]))
 for j in range(3,9):   # the other winding of one joint (UR5e joints span +-360 deg): e.g. wrist 2 through 0 instead of through 180 (gripper folded onto the wrist)
  for w in (2*np.pi,-2*np.pi):
   bj=b.copy();bj[j]+=w
   if -2*np.pi<=bj[j]<=2*np.pi:
    c.append((f'joint {j-2} other winding',[a,bj]))
    m1=bj.copy();m1[0]=a[0];c.append((f'joint {j-2} other winding, joints then cart',[a,m1,bj]))
    m2=a.copy();m2[0]=bj[0];c.append((f'joint {j-2} other winding, cart then joints',[a,m2,bj]))
 return c
T=[('rest_to_faucet','H_spat_pre','H_fau_closed_pre',0.),('faucet_to_wok','H_fau_open_post','H_wok_pre',30.),('wok_to_faucet','H_wok_pre','H_fau_open_post',30.),('faucet_to_rest','H_fau_closed_pre','H_spat_pre',0.)]
est=json.load(open('results/r18/arm18.json'))['free_moves_s'];res=[];t0=time.monotonic()
for name,fa,fb,lever in T:
 if 'ONLY' in KV and name!=KV['ONLY']:continue
 ch=model(lever);tries=[]
 prev=[t_ for t_ in (json.load(open('results/r19/prim/transit.json'))['transits'] if os.path.exists('results/r19/prim/transit.json') else []) if t_['transit']==name]
 if 'PLAN' in KV and prev:tries=[t_ for t_ in prev[0]['tries'] if 'planned' not in t_['candidate']]   # straight candidates already checked in an earlier run
 else:
  for cn,pts in candidates(H[fa],H[fb]):
   ok,info,_=path(ch,pts);tries.append(dict(candidate=cn,ok=ok,pieces=info))
   print(name,cn,ok,info[-1],flush=True)
   if ok:break
  if prev:tries+=[t_ for t_ in prev[0]['tries'] if 'planned' in t_['candidate']]   # keep an earlier planner result
 if 'PLAN' in KV and not any(t_['ok'] for t_ in tries):   # RRT-Connect (planner.py, <= 4 mm replay, full checks) for the joint part, the cart moved separately at a fixed posture
  import planner
  for cn,cart_first in (('cart then planned joints',True),('planned joints then cart',False)):
   a,b=H[fa],near(H[fa],H[fb]);m_=(a if cart_first else b).copy();m_[0]=(b if cart_first else a)[0]
   cart_piece=(a,m_) if cart_first else (m_,b);ok,ci,_=path(ch,list(cart_piece))
   if not ok:tries.append(dict(candidate=cn,ok=False,pieces=[ci]));print(name,cn,'cart piece blocked',ci,flush=True);continue
   qa,qb=(m_,b) if cart_first else (a,m_);ch.active=ch.arm_ids
   pr=planner.plan(ch,qa,qb,budget_s=float(KV.get('PLAN_S',100)),seed=8);ch.active=ch.base_ids+ch.arm_ids
   pi=dict(ok=pr['ok'],method=pr.get('method'),elapsed_s=round(pr['elapsed_s'],1),restarts=pr.get('restarts'),nodes=pr.get('nodes'),reason=pr.get('reason'))
   if pr['ok']:
    Pp=np.array(pr['path']);sweep=float(np.degrees(np.abs(np.diff(Pp[:,3:9],axis=0))).max(1).sum());cl=[min((v['reserve_mm'] for cat,v in c_.items() if cat!='self'),default=1e9) for c_ in pr['clearance']]
    pi.update(states=len(Pp),joint_sweep_deg=round(sweep,1),time_s=round(sweep/QW+.6,2),min_reserve_mm=round(min(cl),1),step_bound_m=pr.get('step_bound_m'))
   pieces=[ci,pi] if cart_first else [pi,ci];tries.append(dict(candidate=cn,ok=pr['ok'],pieces=pieces));print(name,cn,pi,flush=True)
   if pr['ok']:break
 good=[t_ for t_ in tries if t_['ok']]
 res.append(dict(transit=name,frm=fa,to=fb,lever_deg=lever,cart=[round(H[fa][0],3),round(H[fb][0],3)],estimate_s=est[name],
  ok=bool(good),path=good[0]['candidate'] if good else None,time_s=round(sum(p['time_s'] for p in good[0]['pieces']),2) if good else None,
  states=sum(p['states'] for p in good[0]['pieces']) if good else None,min_reserve_mm=min(p['min_reserve_mm'] for p in good[0]['pieces']) if good else None,tries=tries))
fn='results/r19/prim/transit.json';old=json.load(open(fn)) if os.path.exists(fn) else {}
keep=[t_ for t_ in old.get('transits',[]) if t_['transit'] not in {r_['transit'] for r_ in res}]
for r_ in res:r_['elapsed_s']=round(time.monotonic()-t0,1)
out=dict(source='r19prim_transit.py',hubs={k:np.round(v,4).tolist() for k,v in H.items()},step='<= 1 deg largest joint, <= 1 cm cart',transits=sorted(keep+res,key=lambda t_:[x[0] for x in T].index(t_['transit'])),elapsed_s=round(time.monotonic()-t0,1))
json.dump(out,open(fn,'w'),indent=1)
for r_ in res:print(r_['transit'],r_['ok'],r_['path'],r_['time_s'],'est',r_['estimate_s'],'states',r_['states'],'reserve',r_['min_reserve_mm'])
print('elapsed',out['elapsed_s'])
