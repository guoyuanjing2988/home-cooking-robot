"""R19 prep step 5 (#38) reach probes for the fold-away T2L cradle (kitchen19p5.py). New file; as r19prep4_probe.py:
96-start collision-aware IK (solver.solve, unchanged checker) with the LEAF held by its knob at one fold angle, the cart
fixed (the leaf rides on the cart, so its world pose depends on the cart), in the r19prepchain.py union scene (today's
kitchen, kitchen19.LAYOUT, lever station, faucet lever closed AND open) + the kitchen19p5 fixed bar. A probe is one pose.
python r19prep5_probe.py PROBES=a,b*,.. [NPAR=8] [SEEDS=14,15] [ARM=..]   (no PROBES: list them)
 -> results/r19/prep5/probe_<name>[_arm].json"""
import sys,os,json,subprocess,collections
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
OUT='results/r19/prep5';os.makedirs(OUT,exist_ok=True)
def probes():
 import kitchen16 as K,kitchen19 as K19,kitchen19p4 as P4,kitchen19p5 as P5
 I=np.eye(3);P={};car=('carrot',I.tolist(),K19.tray('carrot').tolist());tom=('tomato',I.tolist(),K19.tray('tomato').tolist())
 for knob in ('top','side'):
  for kr in (.03,.10):
   for pan in (False,True):
    o=P5._reg('swing',knob,kr,pan)
    for deg in (0.,45.,90.):
     for cx in (-.45,.17,1.21):
      R,p=P5.leaf_pose_world('swing',deg,cx)
      P[f'sw_{knob}_r{kr:g}_{"pan" if pan else "nop"}_a{deg:g}_c{cx:+.2f}']=dict(obj=o,R=R.tolist(),p=p.tolist(),objs=[list(car),list(tom)],cart=cx,
       p5=dict(kind='swing',state='held',knob=knob,knob_r=kr),desc=f'swing leaf ({knob} knob at r {kr}, pan {pan}) held at fold angle {deg}, cart {cx}')
 # ---- complete-flow probes: the catch tray (lever, step 3) poured into the staging pan riding on the cradle at fold angle a ----
 import r19prep4_actions as A4,kitchen19p3 as P3
 lx,ly,_=K19.LAYOUT['lever']
 for a in (90.,60.,45.):
  for cx in (-.45,-.52,-.60,-.70):
   Rl_,pl_=P5.leaf_pose_world('swing',a,cx);Rt,pt=P4.t2l_local();pan=Rl_@(pt-P5.hinge_local())+pl_   # pan bottom centre (world)
   p5=dict(kind='swing',state='folded',angle=a,pan=True,knob='top')
   for deg in (-120.,120.,-90.):
    for dz in (.06,.10):
     _,(R2,p2)=A4.mouth_pose('ctray',I,pan+[0,0,P4.STG_H+dz],deg)
     P[f'ct2s_a{a:g}_c{cx:+.2f}_{deg:g}_dz{dz:g}']=dict(obj='ctray',R=np.asarray(R2).tolist(),p=np.asarray(p2).tolist(),objs=[list(car),list(tom)],cart=cx,p5=p5,desc=f'catch tray rolled {deg} with its mouth {dz} m over the rim of the pan riding on the swing cradle at {a} deg, cart {cx}')
   (Rl,pl),_=A4.mouth_pose('ctray',I,pan+[0,0,P4.STG_H+.10],-120.)
   P[f'ct2s_a{a:g}_c{cx:+.2f}_level']=dict(obj='ctray',R=np.asarray(Rl).tolist(),p=np.asarray(pl).tolist(),objs=[list(car),list(tom)],cart=cx,p5=p5,desc=f'catch tray level over the pan on the cradle at {a} deg (pre-pour), cart {cx}')
  for cx in (-.52,-.60):
   P[f'ct2s_a{a:g}_c{cx:+.2f}_seat']=dict(obj='ctray',R=I.tolist(),p=[lx,ly,.862+.008],objs=[list(car),list(tom)],cart=cx,p5=dict(kind='swing',state='folded',angle=a,pan=True,knob='top'),desc=f'catch tray 8 mm over its seat, cradle at {a} deg with the pan, cart {cx}')
 return P
def run(name):
 import chain,collections
 from scene import build,save
 from checker import Checker
 from solver import solve
 import kitchen16 as K,kitchen17 as K17,kitchen19 as K19,kitchen19p3 as P3,kitchen19p4 as P4,kitchen19p5 as P5,arms
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=8.,0.,180.
 Pr=probes()[name];sign=1
 BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},r14_fridge=True,r17_lever=0.,**K19.base_cfg())
 sc=K19.layout_scene('lever',objs=Pr['objs']);sc['stations']['slicer']=K19.LAYOUT['slicer']
 import kitchen19p3 as P3_;P3_.ensure([Pr['obj']])
 cfg=chain.chain_cfg('SD',**{**BASE,'r19':sc,'r19p5':Pr['p5'],**K17.held_cfg(Pr['obj'],sign)})
 tree,meta=build(cfg,None);K19.add(tree,cfg);P4.add(tree,cfg);P5.add(tree,cfg);P3.mesh_held(tree);P4.mesh(tree);P5.mesh(tree)
 Rl,pl=K17.lever_pose(K17.LEVER_OPEN);K._add(tree.find('worldbody'),'u_open_',K.OBJ['lever']['parts'],Rl,pl,rgba='.75 .77 .8 1')
 ch=Checker(tree,meta);R=np.array(Pr['R']);p=np.array(Pr['p']);pt,Rt=K.tcp_pose(Pr['obj'],R,p,sign)
 t=dict(name=name,points=[list(pt)]*2,held=None,kind='transfer',force=None,approach=list(Rt[:,0]),jaws=[tuple(sign*(R@K.OBJ[Pr['obj']]['j']))],jaw_q=K19.JAW[Pr['obj']],cart_x=float(Pr['cart']))
 stat=collections.Counter();cands=[]
 for seed in [int(s) for s in KV.get('SEEDS','14,15').split(',')]:
  r=solve(ch,pt,list(Rt[:,0]),target=t,seed=seed);stat.update(r['status_counts']);cands+=r['candidates']
 cands=sorted(cands,key=lambda c:-c['reserve_mm']);bl=collections.Counter()
 if not cands:
  r=solve(ch,pt,list(Rt[:,0]),target=t,seed=99)
  for row in r['rows']:
   for h in (row.get('check') or {}).get('hits',[]):bl[' | '.join(sorted(h['pair']))]+=1
 out=dict(probe=name,desc=Pr['desc'],obj=Pr['obj'],R=Pr['R'],p=Pr['p'],cart_fixed=Pr['cart'],p5=Pr['p5'],tcp=pt.tolist(),approach=Rt[:,0].tolist(),ok=bool(cands),n_ok=len(cands),status=dict(stat),
  best_reserve_mm=round(cands[0]['reserve_mm'],1) if cands else None,best_q=cands[0]['q'] if cands else None,blockers=bl.most_common(6),arm=arms.current())
 save(f"{OUT}/probe_{name}{arms.tag()}.json",out)
 print(f"{name:40s} ok {len(cands):3d} res {out['best_reserve_mm']} {dict(stat)} {out['blockers'][:2]}",flush=True)
if __name__=='__main__':
 if 'ONE' in KV:run(KV['ONE']);sys.exit()
 names=[n for pat in KV.get('PROBES','').split(',') if pat for n in probes() if n==pat or (pat.endswith('*') and n.startswith(pat[:-1]))]
 if not names:print('\n'.join(probes()));sys.exit()
 from concurrent.futures import ThreadPoolExecutor
 def one(n):
  try:r=subprocess.run([sys.executable,__file__,f'ONE={n}']+[a for a in sys.argv[1:] if a.startswith(('ARM=','SEEDS='))],capture_output=True,text=True,timeout=float(KV.get('TONE',240)))
  except subprocess.TimeoutExpired:return n+' TIMEOUT'
  return (r.stdout.strip().splitlines() or [n+' ERR '+r.stderr[-600:]])[-1]
 with ThreadPoolExecutor(int(KV.get('NPAR',8))) as ex:
  for o in ex.map(one,names):print(o,flush=True)
