"""R19 seasoning cups (#5): screen the staging candidates (kitchen19seas.py sites T1, T2R/T2L/T2RC/T2LC, T3).
New file; nothing else is changed.

MODE=replay  every stored state of every saved checked path is replayed in today's (R18b) kitchen with the
             staged cups (all slots filled; L cups unless the site takes S only) and their caddy / rack /
             bracket added, as r18spatreplay.py / r19prep_spotreplay.py do (fast checker, full=False: MuJoCo
             contacts with the 10 / 5 mm gaps). Reported per path: states, states with a hit on a staging
             geom (first one named), and the least distance (mujoco.mj_geomDistance) from any robot / held
             geom to any staging geom over all its states. Paths:
               - the 6 checked whole actions (results/r17/chain_*: wok plate + sink rinse at plating spot 1
                 and 2, faucet lever, lid, spider, spatula fetch) with their grasp approaches,
               - the 22 checked hub-roadmap edges (results/r19/hub/edge_*.json, every state),
               - the checked R15 stir cycle in the R17 kitchen (results/r19/stir/stirwalk2_h_scrape_dice_r17.json).
             A SCREEN of stored states (not a <= 4 mm re-check of the paths between them).
MODE=ik      pickability of every slot: 96-start collision-aware IK (solver.solve, SEED) for the cup held at
             its slot, lifted 8 mm (r18spatscan.py convention; T2: 12 mm, since the cart-mounted caddy is a
             robot part and needs 10 mm), every other slot filled; both grasp senses (-1: gripper body above
             the lug, +1: below). Counts of collision-free starts and the best reserve.
             T2 (cart-mounted): the cart is fixed at CARTS (default 0.172 = hub station H_WOK).
Design options: Z=<m> riser under the T1 caddy / T3 rack (0 = on the counter, the plan); APITCH=<deg> grasp
approach pitched down from horizontal (kitchen19seas.set_approach).
python r19cup_screen.py SITE=T1|T2R|T2L|T2RC|T2LC|T3 MODE=replay|ik [Z=0] [APITCH=0] [SIZE=L|S] [SEED=14] [SLOTS=f0,b1] [SENSES=-1,1] [CARTS=.172]
 -> results/r19/cups/screen_<SITE>_<MODE>[_<SIZE>].json"""
import sys,os,json,glob,time,collections
sys.path.insert(0,'.')
import numpy as np,mujoco
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17,kitchen19seas as S
from scene import save
from checker import Checker
KV=dict(a.split('=',1) for a in sys.argv[1:]);SITE=KV['SITE'];MODE=KV.get('MODE','replay');SIZE=KV.get('SIZE','L' if SITE!='T3' else 'S')
OUT='results/r19/cups';os.makedirs(OUT,exist_ok=True)
S.setup_kitchen();Z=float(KV.get('Z',0.));S.set_approach(float(KV.get('APITCH',0.)))
LAYER=dict(r19seas=dict(site=SITE,cups=SIZE,taken=None,z=Z))
CHAINS=dict(wok_plate_rinse='wok_s-1_final',wok_plate2_rinse='wok_s-1_r18plate2b',faucet_open='lever_s+1_final',lid_off_to_rack='lid_s-1_final',spider_pot_to_plate='spider_s+1_final',spatula_fetch='spatula_s-1_r18roll-1.15_.30')
def stage_ids(ch):return [g for g,n in enumerate(ch.gnames) if n.startswith(('r19s_','R_cart_r19s_'))]
def mover_ids(ch,stage):return [g for g,n in enumerate(ch.gnames) if (ch.robot[g] or ch.held[g]) and g not in stage and ch.m.geom_type[g]!=mujoco.mjtGeom.mjGEOM_PLANE]
def replay_states(ch,qs,labels=None):
 """fast check + least distance robot -> staging geoms (distance computed only for pairs whose bounding
 spheres come within 0.10 m)."""
 m,d=ch.m,ch.d;st=stage_ids(ch);mv=mover_ids(ch,st);hits=collections.Counter();first=None;best=(1e9,None,None);ft=np.zeros(6)
 for i,q in enumerate(qs):
  c=ch.check(np.asarray(q,float),full=False,mass=0.)
  hs=[h for h in c['hits'] if any(n.startswith(('r19s_','R_cart_r19s_')) for n in h['pair'])]
  if hs:
   hits[labels[i] if labels else 'all']+=1
   if first is None:first=dict(state=i,label=labels[i] if labels else None,pair=hs[0]['pair'],gap_mm=hs[0].get('real_gap_mm'))
  # distances (kinematics were set by check)
  P=d.geom_xpos;rb=m.geom_rbound
  for a in mv:
   for b in st:
    if np.linalg.norm(P[a]-P[b])-rb[a]-rb[b]>.10:continue
    dist=mujoco.mj_geomDistance(m,d,a,b,.10,ft)
    if dist<best[0]:best=(dist,ch.gnames[a],ch.gnames[b],i)
 return dict(states=len(qs),hit_states=sum(hits.values()),hit_by_label=dict(hits),first_hit=first,min_dist_mm=round(best[0]*1000,1) if best[0]<1e8 else '>100',min_pair=best[1:3] if best[0]<1e8 else None,min_state=best[3] if best[0]<1e8 else None)
def run_replay():
 res={};t0=time.monotonic();seglab=json.load(open('results/r19/prim/segments.json'))['labels'] if os.path.exists('results/r19/prim/segments.json') else {}
 for n,f in CHAINS.items():
  r=json.load(open(f'results/r17/chain_{f}.json'));S.setup_kitchen()
  for k,v in r.get('tool_xy',{}).items():
   if k!='spatula':K.TOOL_XY[k]=tuple(v)
  if r['obj']=='wok':K17.set_wok_tilt(r.get('wok_tilt',0.))
  ex={'r17_plate2':[.43,K15.PLATE['c'][1],K15.PLATE['c'][2]]} if 'plate2' in n else {}
  ch,_=S.checker({**r.get('scene',{}),**ex,'r16_tools':{'ladle':None},**K17.held_cfg(r['obj'],r['grasp_sense']),**LAYER})
  lab=seglab.get(n);labels=[(lab[i] if lab and lab[i] else 'play') for i in range(len(r['play']))] if lab else None
  res[n]=replay_states(ch,r['play'],labels)
  # grasp approaches: empty gripper, object in the world (the scene of each approach's keyframe)
  aq=[q for a in r.get('approach_qs') or [] if a for q in a]
  if aq:
   world=dict(r.get('scene',{}));world.update(ex)
   if r['obj']=='lever':world['r17_lever']=0.   # both lever approaches are near the closed / open lever; the staging geoms are far from it
   che,_=S.checker({**world,'r16_tools':{'ladle':None},**LAYER});res[n+'__approaches']=replay_states(che,aq)
  print(n,res[n],flush=True)
 S.setup_kitchen()
 ch,_=S.checker({'r16_tools':{'ladle':None},'r17_lever':0.,'r16_lid':'on','r17_plate2':[.17,K15.PLATE['c'][1],K15.PLATE['c'][2]],**LAYER})   # the hub union scene of r19prep_spotreplay.py
 for f in sorted(glob.glob('results/r19/hub/edge_*.json')):
  e=json.load(open(f))
  if not e.get('ok') or not e.get('qs'):continue
  k='hub_'+os.path.basename(f)[5:-5];res[k]=replay_states(ch,e['qs']);print(k,res[k],flush=True)
 st=json.load(open('results/r19/stir/stirwalk2_h_scrape_dice_r17.json'));sign=next((a['jaw_sign'] for a in st['attempts'] if a.get('ok')),-1)
 S.setup_kitchen();K.TOOL_XY['spatula']=(-1.15,.30)
 ch,_=S.checker({'r15_spatula':st['grip_m'],'r15_spatula_jaw':sign,'r16_tools':{'ladle':None,'spatula':None},**LAYER})
 res['stir_cycle']=replay_states(ch,st['states']['q'],st['states']['kinds']);print('stir_cycle',res['stir_cycle'],flush=True)
 tot=dict(paths=len(res),states=sum(v['states'] for v in res.values()),paths_hit=[k for k,v in res.items() if v['hit_states']],
  min_dist_mm=min((v['min_dist_mm'] for v in res.values() if isinstance(v['min_dist_mm'],float)),default='>100'))
 return dict(results=res,total=tot,elapsed_s=round(time.monotonic()-t0,1))
def run_ik():
 from solver import solve
 import chain
 seed=int(KV.get('SEED',14));lift=.012 if SITE.startswith('T2') else .008
 sl=S.slots(SITE,Z);names=KV['SLOTS'].split(',') if 'SLOTS' in KV else list(sl);senses=[int(s) for s in KV.get('SENSES','-1,1').split(',')]
 out={};t0=time.monotonic()
 cart=S.site_def(SITE)[0]=='cart'
 for name in names:
  size=S.slot_size(SITE,SIZE,name);obj='cup'+size;R,p=sl[name];out[name]={}
  for s in senses:
   ch,_=S.checker({**K17.held_cfg(obj,s),'r19seas':dict(site=SITE,cups=SIZE,taken=name,z=Z)})
   if cart:   # cart-frame slot: the target moves with the cart; solve with the cart fixed at a few stations
    rows=[]
    for cx in [float(v) for v in KV.get('CARTS','.172').split(',')]:   # default: hub station H_WOK; the caddy moves with the cart, so only the environment differs between stations
     q0=[cx,-.21,0.];Rw,pw=S.cart_to_world(q0,R,p);pt,Rt=K.tcp_pose(obj,Rw,pw+[0,0,lift],s)
     t=dict(name='cup',points=[list(pt)]*2,held=None,kind='transfer',force=None,approach=list(Rt[:,0]),jaws=[tuple(s*(Rw@K.OBJ[obj]['j']))],jaw_q=.015,cart_x=cx)
     r=solve(ch,pt,list(Rt[:,0]),target=t,seed=seed);rows.append(dict(cart_x=cx,n=len(r['candidates']),best=max([c['reserve_mm'] for c in r['candidates']],default=None),status=r['status_counts']))
    out[name][s]=dict(by_cart=rows,n=sum(rr['n'] for rr in rows),best=max([rr['best'] for rr in rows if rr['best'] is not None],default=None))
   else:
    pt,Rt=K.tcp_pose(obj,R,p+[0,0,lift],s)
    t=dict(name='cup',points=[list(pt)]*2,held=None,kind='transfer',force=None,approach=list(Rt[:,0]),jaws=[tuple(s*(R@K.OBJ[obj]['j']))],jaw_q=.015)
    r=solve(ch,pt,list(Rt[:,0]),target=t,seed=seed)
    out[name][s]=dict(n=len(r['candidates']),best=max([c['reserve_mm'] for c in r['candidates']],default=None),status=r['status_counts'],
     carts=sorted(round(c['q'][0],2) for c in r['candidates'])[:12],
     blockers=sorted({tuple(h['pair']) for row in r['rows'] if row.get('check') for h in row['check'].get('hits',[])},key=str)[:8] if not r['candidates'] else None)
   print(name,size,'sense',s,{k:v for k,v in out[name][s].items() if k!='by_cart'},flush=True)
 return dict(slots={k:dict(size=S.slot_size(SITE,SIZE,k),**{str(s):v for s,v in d.items()}) for k,d in out.items()},lift_m=lift,seed=seed,elapsed_s=round(time.monotonic()-t0,1))
r=run_replay() if MODE=='replay' else run_ik()
fn=f'{OUT}/screen_{SITE}'+(f'_z{Z:g}' if Z else '')+f'_{MODE}'+(f'_{SIZE}' if MODE=='ik' else '')+(f"_p{S.APITCH:g}" if MODE=='ik' and S.APITCH else '')+('_'+KV['TAG'] if 'TAG' in KV else '')+'.json'
import arms;fn=fn[:-5]+arms.tag()+'.json'
save(fn,dict(site=SITE,mode=MODE,size=SIZE,z=Z,approach_pitch_deg=S.APITCH,doc=__doc__,**r));print(fn,'elapsed',r['elapsed_s'])
if MODE=='replay':print('TOTAL',r['total'])
