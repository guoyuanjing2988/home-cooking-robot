"""R18 spatula rest screening: for each candidate rest (x, y, handle elevation), put the spatula there
and replay the checked R17 whole actions (their saved arm paths, every step) in that scene; a candidate
is kept only if no step of any action hits it (unchanged checker, robot / held object vs environment).
Then the kept candidates are tried for pickability (solver.solve at the rest grasp, both senses).
Actions replayed (results/r17/chain_*_final.json): wok (plate + sink rinse), lever (faucet), lid, spider.
python r18spatscan.py -> results/r18/spatscan.json"""
import json,itertools,numpy as np
import chain
from scene import build,save
from checker import Checker
from solver import solve
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
CH={n:json.load(open(f'results/r17/chain_{n}.json')) for n in ('wok_s-1_final','lever_s+1_final','lid_s-1_final','spider_s+1_final')}
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)
def setup(r):
 if r.get('wok_tilt'):K17.set_wok_tilt(r['wok_tilt'])
 for k,v in r.get('tool_xy',{}).items():
  if k!='spatula':K.TOOL_XY[k]=tuple(v)
def replay(name,step=2):
 r=CH[name];setup(r);cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),**K17.held_cfg(r['obj'],r['grasp_sense']),'r16_tools':{'ladle':None}})   # the spatula on its candidate rest in every replay
 tree,meta=build(cfg,None);ch=Checker(tree,meta);hits=[]
 for i,q in enumerate(r['play'][::step]):
  c=ch.check(np.array(q),full=False,mass=0.)
  sp=[h['pair'] for h in c['hits'] if any('spatula' in g for g in h['pair'])]
  if sp:hits.append((i*step,sp[0]));break
 return hits
cands=[]
for x,y,e in itertools.product([-1.30,-1.15,-1.00,-.85,.0,.10,.20,1.50,1.60,1.68],[.30,.42,.50],[50.,25.,8.]):
 if .05<x<.56 and y<.30:continue   # plating spots
 cands.append((x,y,e))
out=[]
for x,y,e in cands:
 K.TOOL_XY['spatula']=(x,y);K.SPAT_ELEV=e;row=dict(x=x,y=y,elev=e,blocks={})
 for n in CH:
  h=replay(n)
  if h:row['blocks'][n]=h[0];break
 row['clear']=not row['blocks'];out.append(row);print(row,flush=True)
keep=[r for r in out if r['clear']]
for row in keep:   # pickability at the rest grasp (blade-frame object), both senses
 K.TOOL_XY['spatula']=(row['x'],row['y']);K.SPAT_ELEV=row['elev'];Rb,pb=K17.spatula_rest_blade();row['starts']={}
 for s in (1,-1):
  cfg=chain.chain_cfg('SD',**{**BASE,'r16_tools':{'ladle':None},**K17.held_cfg('spatula_b',s)});tree,meta=build(cfg,None);ch=Checker(tree,meta)
  pt,Rt=K.tcp_pose('spatula_b',Rb,pb+[0,0,.008],s);t=dict(name='spat',points=[list(pt)]*2,held=None,kind='transfer',force=None,approach=list(Rt[:,0]),jaws=[tuple(s*(Rb@K.OBJ['spatula_b']['j']))],jaw_q=.015)
  r=solve(ch,pt,list(Rt[:,0]),target=t,seed=14);row['starts'][s]=len(r['candidates'])
 print('pick',row,flush=True)
save('results/r18/spatscan.json',dict(rows=out,kept=keep))
print('kept',[(r['x'],r['y'],r['elev'],r.get('starts')) for r in keep])
