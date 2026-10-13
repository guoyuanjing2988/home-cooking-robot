"""R19 prep audit (read-only replay; new file, nothing else changed).

Replays the stored R12 prep chains state by state in today's kitchen and lists what they hit:
 - chain_SD (carrot: rib tray -> wash under the R07 wall spout -> peeler -> slicer chute)
 - chain_WD (tomato: pad -> rinse under the R07 wall spout -> lever cutter, pusher press)
Scene 'r18' = the R19 hub union scene (r19hub.union_tree): the R18b kitchen with the spatula flat
on its rest at (-1.15, .30), flipped; the faucet lever closed AND open; the lid on the pot AND in
the rack; a dish on both plating spots. Each chain's own prep stations and held items are added
per stored segment, exactly as chain.py checked them (held item, tomato on the plate / gone).
Scene 'orig' = the chain's own R12 scene (control): its hits are the declared contact windows.

The fast checker (full=False, as r18spatreplay.py) is a SCREEN, not a check: a hit means a robot
or held geom is inside the 10 / 5 mm gap of that geom at a stored state.
python r19prep_replay.py SD|WD [STRIDE=1] [SCENE=r18|orig]  -> results/r19/prep/replay_<P>_<SCENE>.json"""
import sys,time,json
sys.path.insert(0,'.')
import numpy as np,chain
from scene import build,save
from checker import Checker
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
P=sys.argv[1];KV=dict(a.split('=',1) for a in sys.argv[2:]);STRIDE=int(KV.get('STRIDE',1));SCENE=KV.get('SCENE','r18')
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)            # as r17chain.py / r19hub.py
K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV=8.;K.SPAT_ROLL=180.             # R18b spatula rest
BASE=dict(r14=True,r15=True,r16=True,r17=True,r15_drum_taken=True,r16_tools={'ladle':None},
 r17_lever=0.,r16_lid='on',r17_plate2=[.17,K15.PLATE['c'][1],K15.PLATE['c'][2]])
NEW=('r14_','r15_','r16_','r17_','u_')   # fixtures added after R12 (R14 stove/hood/ports, R15 cooker/plate, R16 zone 2/tools, R17 faucet, union copies)
def seg_state(label):
 """(held, scene extras) of a stored segment, as chain.py group()/connection() checked it."""
 if P=='SD':return (None,{}) if label=='G4S:chute_retreat' else ('carrot',{})
 if label in ('GT3:tomato_release_retreat',):
  seat=chain.target(P,'wedge_load@tomato')['points'][-1];from scene import tomato_dz
  return None,dict(tomato_at=(np.array(seat)-[0,0,tomato_dz(chain.chain_cfg(P))]).tolist())
 if label in ('C3','GT4:pusher_grasp'):return None,chain.tstate(P,'pusher_grasp')
 if label in ('GT4:pusher_press','GT4:pusher_return'):return 'pusher',dict(tomato_gone=True)
 if label=='GT4:pusher_release_lift':return None,dict(tomato_gone=True)
 return 'tomato',{}
def checker_for(label):
 held,ex=seg_state(label)
 if SCENE=='orig':cfg=chain.chain_cfg(P,**ex)
 else:
  c0=chain.chain_cfg(P);cfg=chain.chain_cfg(P,**{**BASE,'present':c0['present'],**ex})   # keep the chain's own stations present
 tree,meta=build(cfg,held)
 if SCENE!='orig':
  world=tree.find('worldbody')
  R,p=K17.lever_pose(K17.LEVER_OPEN);K._add(world,'u_open_',K.OBJ['lever']['parts'],R,p,rgba='.75 .77 .8 1')
  R,p=K.pose('lid','rack');K._add(world,'u_rack_',K.OBJ['lid']['parts'],R,p)
 return Checker(tree,meta),held
r=json.load(open(f'results/chain_{P}/full.json'));Q=r['path'];L=r['labels']
t0=time.monotonic();segs=[];i=0
while i<len(Q):
 j=i
 while j<len(Q) and L[j]==L[i]:j+=1
 ch,held=checker_for(L[i]);new={};other={};first=None;n=0;newstates=0
 for k in list(range(i,j,STRIDE))+([j-1] if (j-1-i)%STRIDE else []):
  c=ch.check(np.array(Q[k]),full=False,mass=chain.MASS[held]);n+=1;hitnew=False
  for h in c['hits']:
   key=' | '.join(sorted(h['pair']))
   if any(g.startswith(NEW) for g in h['pair']):
    new[key]=new.get(key,0)+1;hitnew=True
    if first is None:first=dict(state=k,pair=h['pair'],gap_mm=h.get('real_gap_mm'),required_mm=h.get('required_gap_mm'),cart_x=Q[k][0])
   else:other[key]=other.get(key,0)+1
  newstates+=hitnew
 segs.append(dict(label=L[i],states=[i,j-1],cart_x=[round(Q[i][0],3),round(Q[j-1][0],3)],held=held,checked=n,states_hitting_new=newstates,new_fixture_pairs=new,first_new_hit=first,other_pairs=other))
 print(f'{L[i]:32s} {i:5d}-{j-1:5d} cart {Q[i][0]:+.3f}..{Q[j-1][0]:+.3f} checked {n:4d}  new-fixture states {newstates:4d}  {sorted(new,key=new.get,reverse=True)[:3]}  other {len(other)}',flush=True)
 i=j
out=dict(preset=P,scene=SCENE,stride=STRIDE,method='fast checker (full=False) on every STRIDE-th stored state + each segment end: a SCREEN, not a check',
 scene_note=__doc__.split('\n\n')[0],elapsed_s=round(time.monotonic()-t0,1),segments=segs,
 total_states_hitting_new=sum(s['states_hitting_new'] for s in segs),total_checked=sum(s['checked'] for s in segs))
save(f'results/r19/prep/replay_{P}_{SCENE}.json',out)
print('total checked',out['total_checked'],'states hitting R14+ fixtures',out['total_states_hitting_new'],'elapsed',out['elapsed_s'],'s')
