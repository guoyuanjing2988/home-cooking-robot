"""R19 prep step 3 (#38) reach probes (new file): 96-start collision-aware IK (solver.solve, unchanged checker,
as r14reach.py / r19prep_layout.py reach) with a step-3 object held at one pose, in the r19prepchain.py union
scene (today's kitchen, kitchen19.LAYOUT, faucet lever closed AND open). A probe is a single pose, not a path.
python r19prep3_probe.py PROBES=a,b,.. [NPAR=8] [SEEDS=14,15] [ARM=..]   (no PROBES: list them)
 -> results/r19/prep3/probe_<name>[_arm].json"""
import sys,os,json,subprocess,collections
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:])
OUT='results/r19/prep3';os.makedirs(OUT,exist_ok=True)
def probes():
 import kitchen16 as K,kitchen19 as K19,kitchen19p3 as P3
 I=np.eye(3);P={};W=P3.WORK;FO=K19.FAUCET_OUT;L=K19.LAYOUT;car=('carrot',I.tolist(),K19.tray('carrot').tolist());tom=('tomato',I.tolist(),K19.tray('tomato').tolist())
 def add(nm,obj,R,p,objs=(),st=(),desc='',lever=False):
  P[nm]=dict(obj=obj,R=np.asarray(R).tolist(),p=np.asarray(p,float).tolist(),objs=[list(o) for o in objs],stations=list(st),desc=desc)
 for yaw in (0,-90,180,-45,45):
  Rz=K.Rz(yaw)
  for cy in (.30,.32):
   for fz in (.92,.94,.96):
    add(f'bas_tap_y{yaw}_c{cy:.2f}_f{fz:.2f}','basket',Rz,[FO[0],cy,fz],[car,tom],desc=f'basket held under the outlet, handle yaw {yaw}, centre y {cy}, floor {fz}')
  add(f'bas_work_y{yaw}','basket',Rz,W+[0,0,.008],[car,tom],desc=f'basket held 8 mm over the work spot, handle yaw {yaw}')
  add(f'tub_tap_y{yaw}','tub',Rz,[FO[0],.31,.95],[car,tom],desc=f'tub held under the outlet (floor .95), handle yaw {yaw}')
  add(f'tub_work_y{yaw}','tub',Rz,W+[0,0,.008],[car,tom],desc=f'tub held 8 mm over the work spot, handle yaw {yaw}')
  add(f'bas_intub_y{yaw}','basket',Rz,W+[0,0,P3.TUB['t']+.008],[car,tom,('tub',Rz.tolist(),W.tolist())],desc=f'basket held 8 mm over the tub floor, tub at the work spot, yaw {yaw}')
  for deg in (90,130):
   for s in (1,-1):
    R2,p2=P3.rolled_about_knob('basket',Rz,np.array([FO[0],.30,.98]),s*deg)
    add(f'bas_sinkroll_y{yaw}_{s*deg}','basket',R2,p2,[car,tom],desc=f'basket rolled {s*deg} about the handle over the sink, yaw {yaw}')
 # catch tray under the lever blade plate (tray centre at the lever origin; the lug toward the robot)
 lx,ly,_=L['lever'];add('ctray_seat','ctray',I,[lx,ly,.862+.008],[car,tom],['lever'],desc='catch tray held 8 mm over its seat under the blade plate')
 add('ctray_out','ctray',I,[lx,ly-.14,.862+.03],[car,tom],['lever'],desc='catch tray pulled 14 cm out toward the robot, 3 cm up')
 # round 2 probes: a second (back) spot B2 by the sink, pours over a bowl, the basket in the low-knob tub, the tub emptied
 for bx,by in ((-0.84,.45),(-0.80,.46),(-0.86,.44),(-0.78,.44)):
  for yaw in (0,-30,30):
   add(f'b2_bas_{bx:.2f}_{by:.2f}_y{yaw}','basket',K.Rz(yaw),[bx,by,.858],[car,tom],desc=f'basket held 8 mm over the back spot ({bx},{by}), handle yaw {yaw}')
 for yaw in (0,-30):
  Rz=K.Rz(yaw)
  add(f'tub2_intub_y{yaw}','basket',Rz,W+[0,0,P3.TUB['t']+.008],[car,tom,('tub',Rz.tolist(),W.tolist())],desc=f'basket held 8 mm over the tub floor (low tub knob, same yaw {yaw}), tub at the work spot')
  add(f'tub2_above_y{yaw}','basket',Rz,W+[0,0,P3.TUB['H']+.03],[car,tom,('tub',Rz.tolist(),W.tolist())],desc=f'basket held 3 cm over the tub rim, yaw {yaw}')
  add(f'tub2_work_y{yaw}','tub',Rz,W+[0,0,.008],[car,tom],desc=f'low-knob tub held 8 mm over the work spot, yaw {yaw}')
  add(f'tub2_tap_y{yaw}','tub',Rz,[FO[0],.31,.95],[car,tom],desc=f'low-knob tub held under the outlet, yaw {yaw}')
  for deg in (90,-90,120,-120):
   R2,p2=P3.rolled_about_knob('tub',Rz,np.array([FO[0]-.02,.27,.95]),deg)
   add(f'tub2_empty_y{yaw}_{deg}','tub',R2,p2,[car,tom],desc=f'low-knob tub rolled {deg} over the sink (emptying), yaw {yaw}')
 # pours: the basket rolled about its handle with its mouth over a bowl (bowl rim 0.94); mouth centre ~ knob - 0.17 along the handle
 for nm,bc in (('B1',W[:2]),('B2',np.array([-0.84,.45]))):
  for deg in (130,-130):
   for dy in (0.,.05,-.05):
    for yaw in (0,-30):
     Rz=K.Rz(yaw);hx=Rz@np.array([.17,0,0])
     kn=np.array([bc[0],bc[1]+dy,.85+.09+.10])+hx   # knob over (bowl centre + dy) shifted out along the handle, 10 cm over the bowl rim
     R0,p0=P3.at_knob('basket',Rz,kn);R2,p2=P3.rolled_about_knob('basket',R0,p0,deg)
     add(f'pour_{nm}_{deg}_dy{dy:+.2f}_y{yaw}','basket',R2,p2,[car,tom,('bowl',K.Rz(180).tolist(),[bc[0],bc[1],.85])],desc=f'basket rolled {deg} with its mouth over a bowl at {nm} (+{dy} in y), yaw {yaw}')
 # round 3: a cooking-side staging bowl (T1 back strip behind the plating spots; plating spot 2 in the prep block), pours over it
 import kitchen15 as K15
 PL=np.array(K15.PLATE['c'],float)
 for nm,bc in (('T1a',np.array([.30,.40])),('T1b',np.array([.25,.36])),('P2',np.array([.17,.15])),('P1',np.array([.43,.15])),('SR',np.array([-.02,.30]))):
  for yaw in (180,-90,-135,135):
   Rz=K.Rz(yaw)
   add(f'stg_{nm}_bowl_y{yaw}','bowl',Rz,[bc[0],bc[1],.858],[car,tom],desc=f'staging bowl held 8 mm over {nm} {bc}, knob yaw {yaw}')
  for yaw in (180,-90):
   Rz=K.Rz(yaw);hx=Rz@np.array([.17,0,0])
   for deg in (130,-130):
    kn=np.array([bc[0],bc[1],.85+.09+.10])+hx;R0,p0=P3.at_knob('basket',Rz,kn);R2,p2=P3.rolled_about_knob('basket',R0,p0,deg)
    add(f'stg_{nm}_pour_y{yaw}_{deg}','basket',R2,p2,[car,tom,('bowl',K.Rz(0).tolist(),[bc[0],bc[1],.85])],desc=f'basket (knob yaw {yaw}) rolled {deg} over a bowl at {nm}')
  for deg in (90,-90,120,-120):
   kn=np.array([bc[0],bc[1],.85+.09+.08]);ct=K.OBJ['ctray']
   R0,p0=P3.at_knob('ctray',np.eye(3),kn+[0,-.0,0]);R0,p0=P3.at_knob('ctray',np.eye(3),np.array([bc[0],bc[1]-.10,.85+.09+.06]))
   R2,p2=P3.rolled_about_knob('ctray',R0,p0,deg)
   add(f'stg_{nm}_ctray_{deg}','ctray',R2,p2,[car,tom,('bowl',K.Rz(0).tolist(),[bc[0],bc[1],.85])],['lever'],desc=f'catch tray rolled {deg} over a bowl at {nm}')
 # round 4: basket pour over a T1 bowl, more knob yaws / roll angles
 for nm,bc in (('T1a',np.array([.30,.40])),('T1c',np.array([.30,.38])),('T1d',np.array([.22,.40]))):
  for yaw in (0,-45,-90,-135):
   Rz=K.Rz(yaw);hx=Rz@np.array([.17,0,0])
   for deg in (130,-130,110,-110):
    for dz in (.10,.14):
     kn=np.array([bc[0],bc[1],.85+.09+dz])+hx;R0,p0=P3.at_knob('basket',Rz,kn);R2,p2=P3.rolled_about_knob('basket',R0,p0,deg)
     add(f'tp_{nm}_y{yaw}_{deg}_z{dz:.2f}','basket',R2,p2,[car,tom,('bowl',K.Rz(180).tolist(),[bc[0],bc[1],.85])],desc=f'basket (knob yaw {yaw}) rolled {deg} over a T1 bowl {bc}, knob {dz} over the rim')
 # round 5: basket front / tub back near the sink (prep-time spots), and both at the work spot
 for bx,by in ((-0.86,.12),(-0.84,.13),(-0.82,.12)):
  for yaw in (0,-20,20):
   add(f'fr_bas_{bx:.2f}_{by:.2f}_y{yaw}','basket',K.Rz(yaw),[bx,by,.858],[car,tom],desc=f'basket held 8 mm over a front spot ({bx},{by}), yaw {yaw}')
 for tx,ty in ((-0.86,.40),(-0.84,.41),(-0.82,.42),(-0.86,.38)):
  for yaw in (0,-20,20):
   add(f'bk_tub_{tx:.2f}_{ty:.2f}_y{yaw}','tub',K.Rz(yaw),[tx,ty,.858],[car,tom],desc=f'tub held 8 mm over a back spot ({tx},{ty}), yaw {yaw}')
   add(f'bk_bin_{tx:.2f}_{ty:.2f}_y{yaw}','basket',K.Rz(yaw),[tx,ty,.85+P3.TUB['t']+.008],[car,tom,('tub',K.Rz(yaw).tolist(),[tx,ty,.85])],desc=f'basket held 8 mm over the tub floor, tub at the back spot ({tx},{ty}), yaw {yaw}')
 # slicer out bowl with a strut + knob toward +x (under the cabinet)
 sx,sy,_=L['slicer'];ob=K19.chute_top(*L['slicer']);bcen=np.array(K19.place('slicer',*L['slicer'])[1])+K19.Rz(L['slicer'][2])@K19.SLICER_BOWL
 add('sbowl_seat','sbowl',I,[bcen[0],bcen[1],.851+.008],[car,tom],desc='slicer out bowl (with a knob toward +x) held 8 mm over its seat under the spout')
 add('sbowl_slid','sbowl',I,[bcen[0]+.10,bcen[1],.851+.008],[car,tom],desc='slicer out bowl slid 10 cm right (out from under the spout)')
 return P
def run(name):
 import chain
 from scene import build,save
 from checker import Checker
 from solver import solve
 import kitchen15 as K15,kitchen16 as K,kitchen17 as K17,kitchen19 as K19,kitchen19p3 as P3,arms
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=8.,0.,180.
 Pr=probes()[name];sign=int(KV.get('SIGN',1))
 BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},r14_fridge=True,r17_lever=0.,**K19.base_cfg())
 sc=K19.layout_scene(*Pr['stations'],objs=Pr['objs']);sc['stations']['slicer']=K19.LAYOUT['slicer']
 cfg=chain.chain_cfg('SD',**{**BASE,'r19':sc,**K17.held_cfg(Pr['obj'],sign)})
 tree,meta=build(cfg,None);K19.add(tree,cfg)
 if Pr['obj']=='sbowl' or any(o[0]=='sbowl' for o in Pr['objs']):P3.drop_out_bowl(tree)   # the plain R11 out bowl is replaced by the knob version
 Rl,pl=K17.lever_pose(K17.LEVER_OPEN);K._add(tree.find('worldbody'),'u_open_',K.OBJ['lever']['parts'],Rl,pl,rgba='.75 .77 .8 1')
 ch=Checker(tree,meta);R=np.array(Pr['R']);p=np.array(Pr['p']);pt,Rt=K.tcp_pose(Pr['obj'],R,p,sign)
 t=dict(name=name,points=[list(pt)]*2,held=None,kind='transfer',force=None,approach=list(Rt[:,0]),jaws=[tuple(sign*(R@K.OBJ[Pr['obj']]['j']))],jaw_q=K19.JAW[Pr['obj']])
 stat=collections.Counter();cands=[]
 for seed in [int(s) for s in KV.get('SEEDS','14,15').split(',')]:
  r=solve(ch,pt,list(Rt[:,0]),target=t,seed=seed);stat.update(r['status_counts']);cands+=r['candidates']
 cands=sorted(cands,key=lambda c:-c['reserve_mm']);bl=collections.Counter()
 if not cands:
  r=solve(ch,pt,list(Rt[:,0]),target=t,seed=99)
  for row in r['rows']:
   for h in (row.get('check') or {}).get('hits',[]):bl[' | '.join(sorted(h['pair']))]+=1
 out=dict(probe=name,desc=Pr['desc'],obj=Pr['obj'],R=Pr['R'],p=Pr['p'],tcp=pt.tolist(),approach=Rt[:,0].tolist(),ok=bool(cands),n_ok=len(cands),status=dict(stat),
  best_reserve_mm=round(cands[0]['reserve_mm'],1) if cands else None,carts=sorted({round(c['q'][0],2) for c in cands}),best_q=cands[0]['q'] if cands else None,blockers=bl.most_common(6),arm=arms.current())
 save(f"{OUT}/probe_{name}{arms.tag()}.json",out)
 print(f"{name:34s} ok {len(cands):3d} res {out['best_reserve_mm']} carts {out['carts'][:5]} {dict(stat)} {out['blockers'][:2]}",flush=True)
if __name__=='__main__':
 if 'ONE' in KV:run(KV['ONE']);sys.exit()
 names=[n for pat in KV.get('PROBES','').split(',') if pat for n in probes() if n==pat or (pat.endswith('*') and n.startswith(pat[:-1]))]
 if not names:print('\n'.join(probes()));sys.exit()
 from concurrent.futures import ThreadPoolExecutor
 def one(n):
  r=subprocess.run([sys.executable,__file__,f'ONE={n}']+[a for a in sys.argv[1:] if a.startswith(('ARM=','SEEDS=','SIGN='))],capture_output=True,text=True)
  return (r.stdout.strip().splitlines() or [n+' ERR '+r.stderr[-400:]])[-1]
 with ThreadPoolExecutor(int(KV.get('NPAR',8))) as ex:
  for o in ex.map(one,names):print(o,flush=True)
