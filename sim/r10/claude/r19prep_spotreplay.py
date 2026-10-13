"""R19 prep audit: ground truth for a candidate appliance spot (read-only replay; new file).
Adds one envelope box (r19prep_screen.py sizes) to today's kitchen and replays, with the fast checker
(full=False, as r18spatreplay.py), every stored state of the 6 checked cooking chains (wok plate + sink
rinse at both spots, faucet, lid, spider, spatula fetch; same scene and held objects as r19prim_swept.py)
and every 4th state of the hub edges the screen flagged. Prints the states where any robot / held geom
comes within the gaps of the box. A SCREEN-LEVEL replay, not a full check.
python r19prep_spotreplay.py NAME X Y SX SY SZ -> results/r19/prep/spot_<NAME>.json"""
import sys,json,os,time,collections
sys.path.insert(0,'.')
import numpy as np
import xml.etree.ElementTree as E
import chain
from scene import build,save,box
from checker import Checker
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
NAME=sys.argv[1];X,Y,SX,SY,SZ=map(float,sys.argv[2:7])
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)   # as r19prim_swept.py
CHAINS=dict(wok_plate_rinse='wok_s-1_final',wok_plate2_rinse='wok_s-1_r18plate2b',faucet_open='lever_s+1_final',lid_off_to_rack='lid_s-1_final',spider_pot_to_plate='spider_s+1_final',spatula_fetch='spatula_s-1_r18roll-1.15_.30')
def with_box(tree):
 box(tree.find('worldbody'),'cand_box',[X,Y,.85+SZ/2],[SX,SY,SZ],(.9,.6,.1,1));return tree
seglab=json.load(open('results/r19/prim/segments.json'))['labels'];screen=json.load(open('results/r19/prep/screen.json'))
row=next((r for r in screen['rows'] if abs(r['center'][0]-X)<1e-3 and abs(r['center'][1]-Y)<1e-3 and r['size_m']==[SX,SY,SZ]),None)
t0=time.monotonic();res={};n_states=0
for n,f in CHAINS.items():
 r=json.load(open(f'results/r17/chain_{f}.json'))
 K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=8.,0.,180.
 for k,v in r.get('tool_xy',{}).items():
  if k!='spatula':K.TOOL_XY[k]=tuple(v)
 if r['obj']=='wok':K17.set_wok_tilt(r.get('wok_tilt',0.))
 ex={'r17_plate2':[.43,K15.PLATE['c'][1],K15.PLATE['c'][2]]} if 'plate2' in n else {}
 cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),**ex,'r16_tools':{'ladle':None},**K17.held_cfg(r['obj'],r['grasp_sense'])})
 tree,meta=build(cfg,None);ch=Checker(with_box(tree),meta);hit=collections.Counter();first=None
 qs=[(seglab[n][i] or seglab[n][1],q) for i,q in enumerate(r['play'])]+[(f"approach@{a['kf']}",q) for a,aq in zip(r['approaches'],r['approach_qs']) for q in aq]
 for lab,q in qs:
  c=ch.check(np.array(q),full=False,mass=0.);n_states+=1
  hs=[h for h in c['hits'] if 'cand_box' in h['pair']]
  if hs:
   hit[lab]+=1
   if first is None:first=dict(segment=lab,pair=hs[0]['pair'],gap_mm=hs[0].get('real_gap_mm'))
 res[n]=dict(states=len(qs),hit_segments=dict(hit),first=first)
 print(n,len(qs),'states; hit segments',dict(hit),first,flush=True)
hub=[k for k in (row['flagged_segments'] if row else []) if k.startswith('hub_edge__')]
cfg=chain.chain_cfg('SD',**{**BASE,'r16_tools':{'ladle':None},'r17_lever':0.,'r16_lid':'on','r17_plate2':[.17,K15.PLATE['c'][1],K15.PLATE['c'][2]]})
tree,meta=build(cfg,None);ch=Checker(with_box(tree),meta)
for k in hub:
 e=json.load(open(f"results/r19/hub/edge_{k[10:]}.json"));qs=e["qs"][::4]+[e['qs'][-1]];h=0;g=None
 for q in qs:
  c=ch.check(np.array(q),full=False,mass=0.);n_states+=1;hs=[x for x in c['hits'] if 'cand_box' in x['pair']]
  if hs:
   h+=1
   if g is None:g=dict(pair=hs[0]['pair'],gap_mm=hs[0].get('real_gap_mm'))
 res[k]=dict(states=len(qs),hit_states=h,first=g);print(k,len(qs),'states; hit states',h,g,flush=True)
out=dict(name=NAME,box=dict(center=[X,Y,.85+SZ/2],size=[SX,SY,SZ]),screen_flagged=row['flagged'] if row else None,states=n_states,elapsed_s=round(time.monotonic()-t0,1),results=res,
 any_hit=any((v.get('hit_segments') or v.get('hit_states')) for v in res.values()))
save(f'results/r19/prep/spot_{NAME}.json',out);print(NAME,'any hit',out['any_hit'],'states',n_states,'elapsed',out['elapsed_s'])
