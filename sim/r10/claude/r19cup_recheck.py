"""R19 cup: independent re-check of a chain's playback states (every 'play' q, full checker) -> hits and
the tightest clearance per category. python r19cup_recheck.py results/mac/chain_cup_<tag>.json"""
import sys,json,numpy as np
import cupobj   # noqa: F401
import chain
from scene import build
from checker import Checker
import kitchen16 as K,kitchen17 as K17
r=json.load(open(sys.argv[1]));K.set_design(**r['design'])
for k_,v in r.get('tool_xy',{}).items():K.TOOL_XY[k_]=tuple(v)
cfg=chain.chain_cfg('SD',**{**dict(r19_station=True,r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools=dict(K17.R17_TOOLS_OFF)),**r['scene'],**K17.held_cfg(r['obj'],r['grasp_sense'])})
tree,meta=build(cfg,None);ch=Checker(tree,meta)
worst={};nh=0
for i,q in enumerate(r['play']):
 c=ch.check(np.array(q),full=True,mass=0.)
 if c['hits']:nh+=1;print('HIT step',i,[h['pair'] for h in c['hits']][:3])
 for cat,v in c['clearance'].items():
  if cat not in worst or v['reserve_mm']<worst[cat][0]:worst[cat]=(v['reserve_mm'],i,{k:v[k] for k in v if k!='reserve_mm'})
print('steps',len(r['play']),'steps with hits',nh)
for cat,(rm,i,v) in sorted(worst.items(),key=lambda t:t[1][0]):print(f' {cat}: min reserve {rm:.1f} mm at play step {i}',v)
