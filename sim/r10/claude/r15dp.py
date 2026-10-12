"""R15 continuity: pick one IK candidate per pose (from r15reach.py results) so that the arm
can move between consecutive poses without changing IK branch and within the UR5e joint
speed limit (180 °/s per joint, UR5e datasheet).
 python r15dp.py stir <keys.json> [GRIP=.4] [N=80] [SUF=_cx.55]  closed stroke cycle: keyframes 0..N-1 then back
                                                      to 0 (the stroke pattern repeats every N keys)
 python r15dp.py seq <reach json> <reach json> ...   an open sequence (e.g. lift, carry, tip 15..90)
Cost: the largest joint step / allowed step over the path, where allowed = dt x 180 °/s for the
stir cycle (dt from the keyframe times) and BREAK (default 30°) for a sequence (slow moves).
Uses only collision-free candidates that also clear the plume rule (stir).
-> results/r15/dp_<name>.json"""
import sys,json,glob,os,numpy as np
import chain
from scene import build,save
from checker import Checker
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a);args=[a for a in sys.argv[2:] if '=' not in a]
VMAX=180.;ids=None
def joint_ids():
 global ids
 if ids is None:ids=Checker(*build(chain.chain_cfg('SD',r14=True,present=[],r15=True),None)).arm_ids
 return ids
def step(q1,q2):
 i=joint_ids();d=np.degrees(np.abs((np.array(q1)[i]-np.array(q2)[i]+np.pi)%(2*np.pi)-np.pi));return d
def cart(q1,q2):return abs(q1[0]-q2[0])   # the cart stays put while stirring (its x is part of q)
def dp(C,allowed,closed):
 """C: list of candidate lists; allowed[i]: allowed max joint step from pose i to i+1
 (len = len(C) if closed else len(C)-1). Returns (cost, path, steps)."""
 n=len(C);best=None
 starts=range(len(C[0])) if closed else [None]
 for s in starts:
  # cost-so-far per candidate at pose i (max ratio), back pointers
  if closed:cost=[np.inf]*len(C[0]);cost[s]=0.
  else:cost=[0.]*len(C[0])
  back=[[None]*len(C[0])]
  for i in range(1,n):
   nc=[];bk=[]
   for c in C[i]:
    o=[(max(cost[k],step(C[i-1][k]['q'],c['q']).max()/allowed[i-1]+(1e3 if cart(C[i-1][k]['q'],c['q'])>1e-3 else 0)),k) for k in range(len(C[i-1])) if np.isfinite(cost[k])]
    v,k=min(o) if o else (np.inf,None);nc.append(v);bk.append(k)
   cost=nc;back.append(bk)
  if closed:fin=[(max(cost[k],step(C[-1][k]['q'],C[0][s]['q']).max()/allowed[-1]+(1e3 if cart(C[-1][k]['q'],C[0][s]['q'])>1e-3 else 0)),k) for k in range(len(C[-1])) if np.isfinite(cost[k])]
  else:fin=[(cost[k],k) for k in range(len(C[-1]))]
  if not fin:continue
  v,k=min(fin)
  if best is None or v<best[0]:
   path=[k]
   for i in range(n-1,0,-1):path.append(back[i][path[-1]])
   best=(v,path[::-1])
 v,path=best;qs=[C[i][path[i]]['q'] for i in range(n)]
 steps=[step(qs[i],qs[i+1]) for i in range(n-1)]+([step(qs[-1],qs[0])] if closed else [])
 return v,path,qs,steps
mode=sys.argv[1]
if mode=='stir':
 keys=json.load(open(args[0]))['keys'];N=int(KV.get('N',80));G=float(KV.get('GRIP',.4));tag=os.path.basename(args[0])[5:-10]
 R=[json.load(open(f'results/r15/reach_stir_{tag}_i{i:03d}_g{G:g}{KV.get("SUF","")}.json')) for i in range(N)]
 C=[[c for c in r['cands'] if c['plume_mm'] is not None and c['plume_mm']>=0] for r in R]
 missing=[i for i,c in enumerate(C) if not c]
 if missing:print('poses with no usable candidate:',missing);save(f'results/r15/dp_stir_{tag}.json',dict(ok=False,missing=missing,n=N));sys.exit()
 t=[k['t'] for k in keys[:N+1]];dt=np.diff(t);allowed=dt*VMAX
 v,path,qs,steps=dp(C,allowed,True)
 sp=np.array([s/d for s,d in zip(steps,dt)])   # mean joint speed over each key interval, deg/s
 res=dict(ok=bool(v<=1),cost_max_step_over_allowed=round(float(v),3),n=N,period_cycle_s=round(t[N]-t[0],2),joint_speed_max_degps=[round(float(x)) for x in sp.max(0)],
  worst_interval=dict(i=int(np.argmax(sp.max(1))),t=round(t[int(np.argmax(sp.max(1)))],2),speed_degps=round(float(sp.max())),dt_s=round(float(dt[int(np.argmax(sp.max(1)))]),3)),
  reserve_mm_min=round(min(C[i][path[i]]['reserve_mm'] for i in range(N)),1),plume_mm_min=round(min(C[i][path[i]]['plume_mm'] for i in range(N)),1),
  cart_x=round(qs[0][0],3),q_path=qs,jaw_path=[C[i][path[i]].get('jaw_sign') for i in range(N)],n_candidates=[len(c) for c in C])
 save(f'results/r15/dp_stir_{tag}.json',res);print(json.dumps({k:v_ for k,v_ in res.items() if k not in ('q_path','jaw_path')}))
else:
 R=[json.load(open(f)) for f in args];BREAK=float(KV.get('BREAK',30))
 C=[r['cands'] for r in R];missing=[i for i,c in enumerate(C) if not c]
 if missing:print('poses with no candidate:',[args[i] for i in missing]);sys.exit()
 v,path,qs,steps=dp(C,[BREAK]*(len(C)-1),False)
 res=dict(files=args,ok=bool(v<=1),cost=round(float(v),3),break_deg=BREAK,max_step_deg=[round(float(s.max()),1) for s in steps],reserve_mm=[round(C[i][path[i]]['reserve_mm'],1) for i in range(len(C))],
  cart_x=[round(q[0],3) for q in qs],q_path=qs,jaw_path=[C[i][path[i]].get('jaw_sign') for i in range(len(C))])
 name=KV.get('NAME','seq');save(f'results/r15/dp_{name}.json',res);print(json.dumps({k:v_ for k,v_ in res.items() if k not in ('q_path','files')}))
