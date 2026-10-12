"""R18: every step of the checked R17 actions (wok plate + rinse, the same at the second plating spot,
faucet lever, lid, spider) replayed with the spatula lying on the counter at X, Y (handle ELEV deg
above the counter, turned YAW deg, ROLL 180 = the other face up); prints the steps where any part hits it.
python r18spatreplay.py X Y YAW [ELEV=8] [ROLL=0]"""
import sys;sys.path.insert(0,'.')
import json,numpy as np,chain
from scene import build
from checker import Checker
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)
for n in ('wok_s-1_final','wok_s-1_r18plate2b','lever_s+1_final','lid_s-1_final','spider_s+1_final'):
 r=json.load(open(f'results/r17/chain_{n}.json'))
 if r.get('wok_tilt'):K17.set_wok_tilt(r['wok_tilt'])
 for k,v in r.get('tool_xy',{}).items():K.TOOL_XY[k]=tuple(v)
 X,Y,YAW=map(float,sys.argv[1:4]);K.TOOL_XY["spatula"]=(X,Y);K.SPAT_ELEV=float(sys.argv[4]) if len(sys.argv)>4 else 8.;K.SPAT_YAW=YAW;K.SPAT_ROLL=float(sys.argv[5]) if len(sys.argv)>5 else 0.
 ex={'r17_plate2':[.43,K15.PLATE['c'][1],K15.PLATE['c'][2]]} if 'plate2' in n else {}
 cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),**ex,**K17.held_cfg(r['obj'],r['grasp_sense']),'r16_tools':{'ladle':None}})
 tree,meta=build(cfg,None);ch=Checker(tree,meta);hits=[];mind=1e9
 for i,q in enumerate(r['play']):
  c=ch.check(np.array(q),full=False,mass=0.)
  sp=[h['pair'] for h in c['hits'] if any('spatula' in g for g in h['pair'])]
  if sp:hits.append((i,sp[0]))
 print(sys.argv[1:],n,len(r["play"]),"steps, spatula hits:",len(hits),hits[:1],flush=True)
