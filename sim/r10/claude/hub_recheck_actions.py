"""Addendum to hub_recheck.py (Mac, 2026-10-13; new file): rule 1 also concerns the checked ACTIONS the hub edges join
(a movement set = spur + the action's play + spur). Each action's stored play and grasp-approach states are re-checked
with the full unchanged checker in the action's own scene (as r17video.py / r19cup_recheck.py rebuild it) plus today's
new places: the seasoning-cup pad + post + cup at (.45,.30,1.085) and the holding bowl at plating spot 2 (.17,.13,.85).
The approach states are checked in the empty-gripper scene of their keyframe (r17chain: object in the world).
python hub_recheck_actions.py  -> results/mac/hub_recheck/actions.json"""
import sys,os,json,time
import numpy as np
import cupobj,bowlobj   # noqa: F401
import chain
from scene import build,save
from checker import Checker
import kitchen16 as K,kitchen17 as K17
KV=dict(a.split('=',1) for a in sys.argv[1:]);OUT='results/mac/hub_recheck';T0=time.monotonic()
K.SPAT_ELEV=8.;K.SPAT_ROLL=180.   # R18b spatula rest pose (as r19hub.py), used where the spatula is on its rest
FILES=dict(wok_spot1='results/r17/chain_wok_s-1_final.json',wok_spot2='results/r17/chain_wok_s-1_r18plate2b.json',lever='results/r17/chain_lever_s+1_final.json',
 lid='results/r17/chain_lid_s-1_final.json',spider='results/r17/chain_spider_s+1_final.json',spatula='results/r17/chain_spatula_s-1_r18roll-1.15_.30.json',cup='results/mac/chain_cup_final.json')
NEWP=dict(r19_station=True,r19_port=[.45,.30,1.085],r19_cup='port',r19_bowl='spot',r19_bowl_at=list(bowlobj.SPOT2))
NEWN=('r19_scale_pad','r19_scale_post','r19_cup_body','r19_bowl_body','r19_bowl_tab')
def tree_for(r,held,extra):
 K.set_design(**r['design'])
 for k_,v in r.get('tool_xy',{}).items():K.TOOL_XY[k_]=tuple(v)
 K17.set_wok_tilt(r.get('wok_tilt') or 0.)
 if r.get('wok_grasp')=='end':K17.set_wok_end_grasp()
 cfg=chain.chain_cfg('SD',**{**dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools=dict(K17.R17_TOOLS_OFF)),**r['scene'],**(K17.held_cfg(r['obj'],r['grasp_sense']) if held else {}),**NEWP,**extra})
 return build(cfg,None)
def run(ch,Q,lab):
 nf=0;hits={};first=None;worst=1e9
 for i,q in enumerate(Q):
  c=ch.check(np.asarray(q,float),full=True,mass=0.)
  env=[v['reserve_mm'] for k,v in c['clearance'].items() if k!='self'];worst=min([worst]+env)
  if not c['ok']:
   nf+=1;first=first if first is not None else i
   for h in c['hits']:
    p=tuple(h['pair'])
    if any(n in NEWN for n in p):hits[str(p)]=hits.get(str(p),0)+1
    else:hits['other '+str(p)]=hits.get('other '+str(p),0)+1
 return dict(states=len(Q),failed=nf,first_fail=first,hit_pairs=dict(sorted(hits.items(),key=lambda t:-t[1])[:8]),min_env_mm=round(worst,1))
RES={}
for a,f in FILES.items():
 r=json.load(open(f));tree,meta=tree_for(r,True,dict(r19_cup=None) if a=='cup' else {});ch=Checker(tree,meta);P=run(ch,r['play'],a)   # the cup action holds the pad's cup
 apps=[]
 for k,qs in enumerate(r.get('approach_qs') or []):
  if not qs:continue
  kf=r['approaches'][k]['kf'];w={}
  if a.startswith('wok'):w={}
  elif a=='lever':w=dict(r17_lever=0. if kf==0 else K17.LEVER_OPEN)
  elif a=='lid':w=dict(r16_lid='on' if kf==0 else 'rack')
  elif a=='spatula':w={'r16_tools':{'ladle':None}}
  elif a=='spider':w={}
  elif a=='cup':w=dict(r19_cup='port')
  te,me=tree_for(r,False,w);ce=Checker(te,me);apps.append(dict(kf=kf,**run(ce,qs,f'{a} approach {k}')))
 RES[a]=dict(file=f,play=P,approaches=apps,ok=P['failed']==0 and all(x['failed']==0 for x in apps))
 print(a,RES[a]['ok'],'play',P,'apps',[(x['failed'],x['hit_pairs']) for x in apps],round(time.monotonic()-T0),flush=True)
save(f'{OUT}/actions.json',dict(new_places=NEWP,note='play + grasp-approach states, full checker, action scene + new places; approach scenes: the object in the world at that keyframe (lever closed/open, lid on pot/in rack, the cup on its pad)',actions=RES))
print('done',{a:v['ok'] for a,v in RES.items()},round(time.monotonic()-T0),flush=True)
