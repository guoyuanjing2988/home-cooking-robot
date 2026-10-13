"""Companion of hub_recheck.py (Mac, 2026-10-13; new file): how close each R19 hub edge comes to TODAY'S new places only
(the cup pad r19_scale_pad, its post r19_scale_post, the cup r19_cup_body, the holding bowl r19_bowl_body / r19_bowl_tab).
Lower bounds from the checker's convex machinery (near_util: AABB, refined by Bounds.pair GJK) minus the checker's required
gap for that pair (10 mm arm, 5 mm gripper), every EVERY-th state (default 2: states are <= 4 mm apart, so <= 8 mm
between samples) and the last. Slack above MARGIN (0.10 m) is not reported. For the record; the check is hub_recheck.py.
python hub_recheck_near.py  -> results/mac/hub_recheck/near_new_places.json"""
import sys,os,json,time
sys.argv=[sys.argv[0],'none']+sys.argv[1:]
import numpy as np,mujoco
import bowlobj   # noqa: F401
import r19hub_cup as H
import kitchen16 as K
from scene import save
KV=H.KV;OUT='results/mac/hub_recheck';MARGIN=float(KV.get('MARGIN',.10))
SRC='/Users/yg736648/Documents/gyj_work/kitchen_robot/home-cooking-robot/sim/r10/claude/results/r19/hub'
_ut=H.union_tree
def union_tree_bowl():
 tree,meta=_ut();K._add(tree.find('worldbody'),'',K.OBJ['bowl']['parts'],np.eye(3),bowlobj.SPOT2,rgba='.78 .8 .83 1');return tree,meta
H.union_tree=union_tree_bowl
ch=H.union_checker();m,d=ch.m,ch.d
NEW={g:m.geom(g).name for g in range(m.ngeom) if m.geom(g).name in ('r19_scale_pad','r19_scale_post','r19_cup_body','r19_bowl_body','r19_bowl_tab')}
assert len(NEW)==5,NEW
import near_util;NR=near_util.Near(ch,list(NEW),cut=MARGIN);TG=[NEW[g] for g in NR.t]
S=H.J(f'{OUT}/summary.json');out={};T0=time.monotonic();STEP=int(KV.get('EVERY',2))
for key in S:
 src=f'{SRC}/edge_{key}.json' if os.path.exists(f'{SRC}/edge_{key}.json') else f'results/mac/hub_cup/edge_{key}.json'
 Q=np.array(H.J(src)['qs'],float);best={}
 for k in list(range(0,len(Q),STEP))+[len(Q)-1]:
  for n,v in zip(TG,NR.slack(Q[k])):
   if v is not None and (n not in best or v[0]<best[n][0]):best[n]=(v[0],k,v[1])
 out[key]={n:dict(slack_mm=round(v[0]*1000,1),state=v[1],robot_geom=v[2]) for n,v in best.items()}
 mn=min([v[0] for v in best.values()]) if best else None
 out[key]['closest_new_place_slack_mm']=None if mn is None else round(mn*1000,1)
 print(key,'closest slack to new places',out[key]['closest_new_place_slack_mm'],{n:v['slack_mm'] for n,v in out[key].items() if isinstance(v,dict)},round(time.monotonic()-T0),flush=True)
save(f'{OUT}/near_new_places.json',dict(margin_m=MARGIN,note=f'None = slack > {MARGIN*1000:.0f} mm to every new place on this edge; slack = convex lower bound - required gap, every {STEP}th state',edges=out))
