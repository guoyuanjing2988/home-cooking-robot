"""Issue #34 (Mac 2026-10-13, new file): confirmation of a rim tipper holder with the UNCHANGED checker (Checker.check,
full=True, every state): the holder (r34holder.py) is added to each scene, with the cup upright (loaded) and, separately,
tipped 120 deg (poured); then
 (ii)  every state of the stored stir cycle results/r19/stir/stirwalk2_h_scrape_dice_r17.json (its own scene, as
       r19stir_save.py SCENE=r17, spatula held at .45 m, jaw -1),
 (iii) every playback state of results/mac/chain_cup_final.json and chain_bowl_final.json (their scenes, as r19cup_recheck.py),
 and the same states WITHOUT the holder (baseline), so a hit can be attributed.
python rim_tipper_confirm.py HOLDER=az,gap,dz [TAG=..] -> results/mac/rim_tipper_confirm_<TAG>.json"""
import sys,json,time,numpy as np
import r34holder   # noqa: F401  (cupobj, bowlobj, holder wrappers)
import chain
from scene import build,save
from checker import Checker
import kitchen16 as K,kitchen17 as K17
KV=dict(a.split('=',1) for a in sys.argv[1:]);HD=[float(v) for v in KV['HOLDER'].split(',')];T0=time.monotonic()
def run(label,cfg,Q,extra):
 tree,meta=build({**cfg,**extra},None);ch=Checker(tree,meta);worst={};hits=[]
 for i,q in enumerate(Q):
  c=ch.check(np.asarray(q,float),full=True,mass=0.)
  if c['hits']:hits.append((i,[h['pair'] for h in c['hits']][:3]))
  for cat,v in c['clearance'].items():
   if cat not in worst or v['reserve_mm']<worst[cat][0]:worst[cat]=(round(v['reserve_mm'],1),i,v.get('pair'))
 hold=[h for h in hits if any(any(str(n).startswith('r34_') for n in p) for p in h[1])]
 print(label,len(Q),'states; steps with hits',len(hits),'(holder involved:',len(hold),')',sorted(worst.items(),key=lambda t:t[1][0])[:3],round(time.monotonic()-T0),flush=True)
 return dict(states=len(Q),steps_with_hits=len(hits),holder_hits=len(hold),first_hits=hits[:5],worst=worst)
OUT={}
# (ii) stir
ST=json.load(open('results/r19/stir/stirwalk2_h_scrape_dice_r17.json'));QS=ST['states']['q']
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);sv=dict(K.TOOL_XY);K.TOOL_XY['spider']=(1.52,.36)
cs=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_spatula=.45,r15_spatula_jaw=-1,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None,'spatula':None})
for lab,ex in (('stir_base',{}),('stir_up',dict(r34_holder=HD,r34_cup=True)),('stir_tipped',dict(r34_holder=HD,r34_tipped=True))):OUT[lab]=run(lab,cs,QS,ex)
K.TOOL_XY.clear();K.TOOL_XY.update(sv)
# (iii) pour paths
for nm,f in (('cup_pour','results/mac/chain_cup_final.json'),('bowl_pour','results/mac/chain_bowl_final.json')):
 r=json.load(open(f));K.set_design(**r['design'])
 for k_,v in r.get('tool_xy',{}).items():K.TOOL_XY[k_]=tuple(v)
 cfg=chain.chain_cfg('SD',**{**dict(r19_station=True,r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools=dict(K17.R17_TOOLS_OFF)),**r['scene'],**K17.held_cfg(r['obj'],r['grasp_sense'])})
 for lab,ex in ((nm+'_base',{}),(nm+'_up',dict(r34_holder=HD,r34_cup=True)),(nm+'_tipped',dict(r34_holder=HD,r34_tipped=True))):OUT[lab]=run(lab,cfg,r['play'],ex)
ok=all(OUT[k]['holder_hits']==0 and OUT[k]['steps_with_hits']<=OUT[k.rsplit('_',1)[0]+'_base']['steps_with_hits'] for k in OUT if not k.endswith('_base'))
save('results/mac/rim_tipper_confirm_'+KV.get('TAG','x')+'.json',dict(holder=HD,ok=ok,results=OUT,elapsed_s=round(time.monotonic()-T0)))
print('OK' if ok else 'FAIL',round(time.monotonic()-T0))
