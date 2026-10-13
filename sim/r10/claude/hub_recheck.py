"""R19 rule 1 pass (Mac, 2026-10-13; new file, edits nothing): re-check the R19 hub edges in a union scene that also has
today's new places: the seasoning-cup pad + post + cup at (.45,.30,1.085) (cupobj, already in r19hub_cup's union scene)
and the holding bowl (bowlobj, 190 x 70 mm, grip tab toward the aisle) standing at plating spot 2 (.17,.13,.85), added
next to the R19 dish at spot 2 (union: either may stand there; clearance is pairwise).
Method (equivalent to re-running `r19hub.py edge` once): the scene only gains objects, so every try that failed in R19
still fails and the command would reach the same first passing path. So each edge's stored path (results/r19/hub/
edge_<A>__<B>.json 'qs', already cut to the <=4 mm point bound by r19hub check_path) gets the full unchanged checker on
EVERY state here. If any state fails, the edge is re-run with the r19hub_cup cmd_edge search (straight, vias, planner)
in this scene and written to results/mac/hub_recheck/edge_<A>__<B>.json.
python hub_recheck.py [EDGES=A:B,...] [EXTRA=1]   -> results/mac/hub_recheck/recheck_<A>__<B>.json, summary.json"""
import sys,os,json,time,shutil
sys.argv=[sys.argv[0],'none']+sys.argv[1:]
import numpy as np
import bowlobj   # noqa: F401  (OBJ['bowl'])
import r19hub_cup as H
import kitchen16 as K
from scene import save
KV=H.KV;OUT='results/mac/hub_recheck';os.makedirs(OUT,exist_ok=True)
SRC='sim/r10/claude/results/r19/hub'   # read only
LANES=[('SPAT','LEV_C'),('SPAT','H_SPAT'),('LID_RACK','H_WOK'),('WOK','H_SINK'),('SPAT','H_SINK'),
 ('LEV_O','WOK'),('LEV_O','H_SINK'),('SPIDER','H_WOK'),('WOK','H_POT'),('LEV_O','H_SPAT'),
 ('LID_RACK','H_POT'),('LEV_C','H_SINK'),('LID_POT','H_WOK'),('LEV_C','H_SPAT'),
 ('SPIDER','H_POT'),('LID_POT','H_POT'),('LEV_C','H_WOK'),('LEV_O','H_WOK')]   # the 18 edges of R19_HUB.md section 6
EXTRA=[('H_SPAT','H_SINK',SRC),('H_SINK','H_WOK',SRC),('H_WOK','H_POT',SRC),('WOK','H_WOK',SRC)]+[('CUP',b,'results/mac/hub_cup') for b in ('H_WOK','WOK','H_SINK','SPAT')]
EDGES=[(a,b,SRC) for a,b in LANES]+(EXTRA if KV.get('EXTRA','1')=='1' else [])
if 'EDGES' in KV:EDGES=[(a,b,s) for a,b,s in EDGES if f'{a}:{b}' in KV['EDGES'].split(',')]
_ut=H.union_tree
def union_tree_bowl():
 tree,meta=_ut();K._add(tree.find('worldbody'),'',K.OBJ['bowl']['parts'],np.eye(3),bowlobj.SPOT2,rgba='.78 .8 .83 1');return tree,meta
H.union_tree=union_tree_bowl
ch=H.union_checker();Hh=H.J('results/mac/hub_cup/hubs.json')
assert any(ch.m.geom(g).name=='r19_bowl_body' for g in range(ch.m.ngeom)) and any(ch.m.geom(g).name=='r19_scale_pad' for g in range(ch.m.ngeom))
SUMF=f'{OUT}/summary.json';SUM=H.J(SUMF) if os.path.exists(SUMF) else {}
T0=time.monotonic()
for a,b,src in EDGES:
 r=H.J(f'{src}/edge_{a}__{b}.json');Q=np.array(r['qs'],float);t1=time.monotonic()
 ends_ok=bool(np.allclose(Q[0],H.node_q(a,Hh)) and np.allclose(Q[-1],H.node_q(b,Hh)))
 worst={};fails=[]
 for i,q in enumerate(Q):
  c=ch.check(q,full=True,mass=0.)
  if not c['ok']:fails.append(dict(i=i,at=round(i/(len(Q)-1),3),hits=[h['pair'] for h in c['hits']][:3],ranges=c['ranges'],mobile=c['mobile']['ok'],stability=c['stability']['ok']))
  for cat,v in c['clearance'].items():
   if cat not in worst or v['reserve_mm']<worst[cat][0]:worst[cat]=(v['reserve_mm'],i)
 env=min([v[0] for k,v in worst.items() if k!='self'] or [None]);slf=worst['self'][0] if 'self' in worst else None
 near={}   # closest distance of any robot state to the new objects, for the record
 rec=dict(a=a,b=b,source=f'{src}/edge_{a}__{b}.json',method=r.get('method'),time_s=r.get('time_s'),states=len(Q),path_ends_match_nodes=ends_ok,
  ok=not fails,states_failed=len(fails),fails=fails[:10],min_reserve_mm=None if env is None else round(env,1),min_self_mm=None if slf is None else round(slf,1),
  min_reserve_by_cat={k:dict(mm=round(v[0],1),i=v[1]) for k,v in worst.items()},stored_min_reserve_mm=r.get('min_reserve_mm'),stored_min_self_mm=r.get('min_self_mm'),
  elapsed_s=round(time.monotonic()-t1),scene='r19hub_cup union (lever closed+open, lid pot+rack, dishes at x .43 and .17, cup pad+post+cup) + holding bowl at spot 2')
 if fails:   # re-run the r19hub edge search in this scene
  if not os.path.exists(f'{OUT}/hubs.json'):shutil.copy('results/mac/hub_cup/hubs.json',f'{OUT}/hubs.json')
  H.OUT=OUT;H.KV.clear();H.KV.update(dict(A=a,B=b,PLAN_S=KV.get('PLAN_S','120')));H.cmd_edge();e=H.J(f'{OUT}/edge_{a}__{b}.json')
  rec['rerun']={k:v for k,v in e.items() if k not in ('qs','segments','tries')};rec['rerun_tries']=[dict(method=t['method'],ok=t['ok']) for t in e.get('tries',[])]
 save(f'{OUT}/recheck_{a}__{b}.json',rec)
 SUM[f'{a}__{b}']={k:rec[k] for k in ('ok','states','states_failed','min_reserve_mm','min_self_mm','stored_min_reserve_mm','stored_min_self_mm','time_s','method','path_ends_match_nodes')}
 if fails:SUM[f'{a}__{b}']['rerun_ok']=rec['rerun'].get('ok');SUM[f'{a}__{b}']['rerun_method']=rec['rerun'].get('method');SUM[f'{a}__{b}']['rerun_time_s']=rec['rerun'].get('time_s');SUM[f'{a}__{b}']['first_fail']=fails[0]
 save(SUMF,SUM)
 print(f'{a}__{b}',rec['ok'],'states',len(Q),'failed',len(fails),'res',rec['min_reserve_mm'],'self',rec['min_self_mm'],'(stored',r.get('min_reserve_mm'),r.get('min_self_mm'),') ends',ends_ok,fails[:1],'t',round(time.monotonic()-T0),flush=True)
print('done',sum(v['ok'] for v in SUM.values()),'/',len(SUM),round(time.monotonic()-T0),flush=True)
