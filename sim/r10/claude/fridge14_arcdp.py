"""R14 fridge: continuity of the handle arc from the docked cart (x = -1.48). Phase 1 (CAND=a):
96-start solver.solve at door angle a (fixed grasp: pad centre on the bar at z 1.10, jaws along
the door normal, approach along the door face), two seeds, all collision-free candidates kept.
Phase 2 (no args): pick one candidate per angle minimising first the number of breaks (a joint
step > 20° between neighbouring angles = release and re-grasp the handle there), then the
largest joint step. python fridge14_arcdp.py CAND=<deg> | python fridge14_arcdp.py
-> results/r14/fridge_arc_cand_<deg>.json, results/r14/fridge_arc_path.json"""
import sys,json,glob,numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:]);ANG=np.arange(0,55.01,2.5);BREAK=20.
if 'CAND' in KV:
 import chain,kitchen14 as K
 from scene import build,save
 from checker import Checker
 from solver import solve
 F=K.FRIDGE;H=np.array([F['x'][0],F['y_face']+F['door_t']]);BAR=np.array([F['bar_x'],F['bar_y']])
 rz=lambda th,v:np.array([v[0]*np.cos(th)+v[1]*np.sin(th),-v[0]*np.sin(th)+v[1]*np.cos(th)])
 a=float(KV['CAND']);th=np.radians(a);p=np.r_[H+rz(th,BAR-H),1.10];ap=np.r_[rz(th,(-1,0)),0];jw=np.r_[rz(th,(0,1)),0]
 cfg=chain.chain_cfg('SD',r14=True,present=[],r14_fridge=True,r14_fridge_door_deg=a,r14_held_handle=True)
 tree,meta=build(cfg,None);ch=Checker(tree,meta);out=[]
 for seed in (14,15):
  for sign in (1,-1):  # the jaw axis sign picks the wrist-3 half turn
   t=dict(name='arc',points=[list(p)]*2,held=None,kind='transfer',force=None,approach=list(ap),jaws=[tuple(sign*jw)],jaw_q=0.,cart_x=-1.48)
   r=solve(ch,p,list(ap),target=t,seed=seed)
   out+=[dict(q=c['q'],reserve_mm=c['reserve_mm']) for c in r['candidates']]
 save(f'results/r14/fridge_arc_cand_{a:g}.json',dict(deg=a,n=len(out),cands=out));print(a,len(out));sys.exit()
C=[json.load(open(f'results/r14/fridge_arc_cand_{a:g}.json'))['cands'] for a in ANG]
import chain
from scene import build
from checker import Checker
ids=Checker(*build(chain.chain_cfg('SD',r14=True,present=[]),None)).arm_ids
step=lambda q1,q2:float(np.degrees(np.max(abs((np.array(q1)[ids]-np.array(q2)[ids]+np.pi)%(2*np.pi)-np.pi))))
# DP over (breaks, max step); state = candidate index at each angle
best=[[(0,0.,None)]*len(C[0])]
for i in range(1,len(ANG)):
 row=[]
 for j,c in enumerate(C[i]):
  opts=[]
  for k,c0 in enumerate(C[i-1]):
   b,mx,_=best[i-1][k];s=step(c0['q'],c['q']);opts.append(((b+(s>BREAK),max(mx,s if s<=BREAK else 0)),k,s))
  if not opts:row.append((99,0.,None));continue
  (b,mx),k,s=min(opts);row.append((b,mx,k))
 best.append(row)
if any(len(c)==0 for c in C):print('angles with no collision-free solution:',[float(a) for a,c in zip(ANG,C) if not c])
j=int(np.argmin([b*1000+mx for b,mx,_ in best[-1]]));path=[]
for i in range(len(ANG)-1,-1,-1):path.append(j);j=best[i][j][2] if i else None
path=path[::-1];steps=[step(C[i-1][path[i-1]]['q'],C[i][path[i]]['q']) for i in range(1,len(ANG))]
breaks=[float(ANG[i]) for i,s in enumerate(steps,1) if s>BREAK]
res=dict(angles=ANG.tolist(),n_candidates=[len(c) for c in C],break_threshold_deg=BREAK,regrasp_at_deg=breaks,max_step_within_segments_deg=round(max([s for s in steps if s<=BREAK],default=0),1),
 steps_deg=[round(s,1) for s in steps],reserve_mm=[round(C[i][path[i]]['reserve_mm'],1) for i in range(len(ANG))],q_path=[C[i][path[i]]['q'] for i in range(len(ANG))])
from scene import save;save('results/r14/fridge_arc_path.json',res);print(json.dumps({k:v for k,v in res.items() if k!='q_path'}))
