"""R14 reach + clearance probes for the storage / dispensing / cooking stations
(kitchen14.py) with the docked cart, UR5e, PGC and R12 dual-zone fingers: 96-start
collision-aware IK (solver.solve) with the unchanged checker (10 mm robot-environment,
5 mm gripper-environment). Usage: python r14reach.py <probe> [CARTX=..]
Results: results/r14/reach_<probe>[_cx..].json"""
import sys,os,json,numpy as np
import chain
from scene import build,save
from checker import Checker
from solver import solve
import kitchen14 as K
probe=sys.argv[1];KV=dict(a.split('=',1) for a in sys.argv[2:])
th=lambda deg:[0,np.cos(np.radians(deg)),np.sin(np.radians(deg))]
P={  # name: (point, approach, jaws, scene extras, held-cup)
 'cup_fill':((.55,.38,1.24),(0,1,0),[(1,0,0),(-1,0,0)],dict(),True),
 'cup_pick':((.57,K.CUP_Y,K.CUP_RAIL['z'][0]+.005),(0,1,0),[(1,0,0),(-1,0,0)],dict(r14_cup_taken=1),True),
 'cup_pour100':((.83,.17,1.13),th(-100),[(1,0,0),(-1,0,0)],dict(),True),
 'cup_pour120':((.83,.17,1.13),th(-120),[(1,0,0),(-1,0,0)],dict(),True),
 'cup_staple':((-1.0,.38,1.24),(0,1,0),[(1,0,0),(-1,0,0)],dict(),True),
 'drawer_handle_closed':((-1.5,-.035,.68),(0,1,0),[(0,0,1),(0,0,-1)],dict(r14_drawer=True),False),
 'drawer_handle_open':((-1.5,-.035-K.DRAWER['open'],.68),(0,1,0),[(0,0,1),(0,0,-1)],dict(r14_drawer=True,r14_drawer_open=True),False),
 'drawer_tray':((-1.5,-.25,.53),(0,0,-1),[(1,0,0),(-1,0,0)],dict(r14_drawer=True,r14_drawer_open=True),False),
 'wok_stir':((.83,.17,1.06),th(-60),[(1,0,0),(-1,0,0)],dict(),False),
}
if probe.startswith('pt'):  # generic point: pt X Y Z AX AY AZ [CUP=1]
 v=[float(x) for x in probe[2:].split('_')];P[probe]=(tuple(v[:3]),tuple(v[3:6]),[tuple(v[6:9])] if len(v)>=9 else None,dict(r14_drawer_open=KV.get('OPEN')=='1',**(dict(r14_fridge=True,r14_fridge_door_deg=float(KV['FRIDGE']),r14_held_handle=KV.get('HELD')=='1',r14_held_box=KV.get('BOX')=='1',r14_box_taken=KV.get('BOX')=='taken',**(dict(r14_rbin_z=float(KV['RBINZ'])) if 'RBINZ' in KV else {})) if 'FRIDGE' in KV else {})),KV.get('CUP')=='1')
p,approach,jaws,extra,cup=P[probe]
cfg=chain.chain_cfg('SD',r14=True,present=[],r14_cup=cup and KV.get('DRUM')!='1',r14_drum=KV.get('DRUM')=='1',**extra)
tree,meta=build(cfg,None);ch=Checker(tree,meta)
target=dict(name=probe,points=[list(p),list(p)],held=None,kind='transfer',force=None,approach=list(approach),**(dict(jaws=jaws) if jaws else {}),jaw_q=float(KV['JAWQ']) if 'JAWQ' in KV else .014 if cup else .02)
if 'CARTX' in KV:target['cart_x']=float(KV['CARTX'])
if 'CARTY' in KV:target['cart_y']=float(KV['CARTY'])
r=solve(ch,np.array(p,float),list(approach),target=target,seed=int(KV.get('SEED',14)))
os.makedirs('results/r14',exist_ok=True)
best=r['best'];out=dict(probe=probe,point=p,approach=approach,cart_x=target.get('cart_x'),ok=r['ok'],status_counts=r['status_counts'],elapsed_s=round(r['elapsed_s'],1),
 best_q=best.get('q'),reserve_mm=best.get('reserve_mm'),best_pos_mm=best.get('position_mm'),
 blockers=sorted({tuple(h[:2]) if isinstance(h,(list,tuple)) else str(h) for row in r['rows'] if row.get('check') for h in row['check'].get('hits',[])},key=str)[:12] if not r['ok'] else [])
save(f"results/r14/reach_{probe}{'_cx'+KV['CARTX'] if 'CARTX' in KV else ''}{'_cy'+KV['CARTY'] if 'CARTY' in KV else ''}{'_fr'+KV['FRIDGE'] if 'FRIDGE' in KV else ''}{'_'+KV['TAG'] if 'TAG' in KV else ''}.json",out)
print(json.dumps({k:v for k,v in out.items() if k!='best_q'},default=str))
