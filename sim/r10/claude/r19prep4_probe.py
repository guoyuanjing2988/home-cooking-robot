"""R19 prep step 4 (#38) reach probes (new file): 96-start collision-aware IK (solver.solve, unchanged checker,
as r19prep3_probe.py) with an object held at one pose, in the r19prepchain.py union scene (today's kitchen,
kitchen19.LAYOUT, faucet lever closed AND open) plus the kitchen19p4.py layer. A probe is a single pose, not a path.
Probes with a fixed cart (CART) solve with the cart there (the T2L pan rides on the cart: its world pose depends on it).
MODE=chute: option (b) geometry from the scene model (no IK): spout outlet, free counter, the drop a chute would need.
python r19prep4_probe.py PROBES=a,b*,.. [NPAR=8] [SEEDS=14,15] [ARM=..] [SIGN=1]   (no PROBES: list them)
 -> results/r19/prep4/probe_<name>[_arm].json"""
import sys,os,json,subprocess,collections
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:])
OUT='results/r19/prep4';os.makedirs(OUT,exist_ok=True)
def mouth_pose(name,Rlevel,mouth,deg):
 """level pose (R, p) and rolled pose of container `name` such that, rolled deg about its handle axis, the centre
 of its mouth (object (0, 0, H)) is at the world point `mouth`."""
 import kitchen16 as K,kitchen19p3 as P3
 from scipy.spatial.transform import Rotation
 o=K.OBJ[name];import kitchen19p4 as P4;H=P4.DBOWL['H'] if name.startswith(('dbowl','dbh')) else P4.STG_H if name.startswith('stg') else P3.CTRAY['H'] if name=='ctray' else P3.BOWL['H']
 g=np.asarray(o['grip'],float);ax=np.asarray(Rlevel)@np.asarray(o.get('hax',o['a']),float);Rr=Rotation.from_rotvec(ax*np.radians(deg)).as_matrix()
 p=np.asarray(mouth,float)-Rlevel@g-Rr@(Rlevel@(np.array([0,0,H])-g))
 R2,p2=P3.rolled_about_knob(name,Rlevel,p,deg);return (np.asarray(Rlevel,float),p),(R2,p2)
def probes():
 import kitchen15 as K15,kitchen16 as K,kitchen19 as K19,kitchen19p3 as P3,kitchen19p4 as P4
 I=np.eye(3);P={};L=K19.LAYOUT;car=('carrot',I.tolist(),K19.tray('carrot').tolist());tom=('tomato',I.tolist(),K19.tray('tomato').tolist())
 def add(nm,obj,R,p,objs=(car,tom),st=(),p4=None,cart=None,desc=''):
  P[nm]=dict(obj=obj,R=np.asarray(R).tolist(),p=np.asarray(p,float).tolist(),objs=[list(o) for o in objs],stations=list(st),p4=p4 or {},cart=cart,desc=desc)
 # ---- (a) drawer bowl: held 8 mm over the guide plate, at the seat and slid out to x; knob pitched down pd ----
 for pd in (0,15,30,45):
  B=P3.pitched(f'dbowl_p{pd}') if pd else 'dbowl'
  for x in (-1.69,-1.60,-1.55,-1.50,-1.45,-1.40):
   R,p=P4.drawer_seat(x);add(f'dw_x{x:.2f}_p{pd}',B,R,p+[0,0,.008],p4=dict(drawer=dict(xo=max(x,-1.60)),drop_potato=True),desc=f'drawer bowl held 8 mm over the guide plate at x {x}, knob +x pitched {pd}')
  for x in (-1.50,-1.45):
   R,p=P4.drawer_seat(x);add(f'dwup_x{x:.2f}_p{pd}',B,R,p+[0,0,.10],p4=dict(drawer=dict(xo=x),drop_potato=True),desc=f'drawer bowl lifted 10 cm over its out spot x {x}, knob pitched {pd}')
 # ---- (a) round 2: drawer bowl with the cranked handle (knob facing the robot, beside the slicer), seat / slid / lifted ----
 for dxk in (.15,.17):
  for ky in (.30,.25):
   for kz in (1.06,1.10):
    for pd in (0,30):
     B=P4.dbh(dxk,round(.495-ky,3),round(kz-.863,3),pd)
     for tag,x,up in (('seat',-1.69,0.),('d15',-1.54,0.),('d20',-1.49,0.),('d20up',-1.49,.10)):
      R,p=P4.drawer_seat(x);add(f'dbh_{tag}_x{dxk:.2f}_ky{ky:.2f}_kz{kz:.2f}_p{pd}',B,R,p+[0,0,.008+up],p4=dict(drawer=dict(xo=max(x,-1.54)),drop_potato=True),desc=f'drawer bowl with cranked handle (knob x +{dxk}, y {ky}, z {kz}, pitch {pd}) held at {tag} (bowl x {x})')
 # ---- (a) round 4 (#38, m2): the cranked handle with the knob turned toward +x by kyaw, so the arm can back off it
 for ky in (.30,.25):
  for kyaw in (30,45,60):
   B=P4.dbh(.17,round(.495-ky,3),round(1.10-.863,3),0,kyaw)
   for tag,x,up in (('seat',-1.69,0.),('d15',-1.54,0.),('d20',-1.49,0.),('d20up',-1.49,.10)):
    R,p=P4.drawer_seat(x);add(f'dbk_{tag}_ky{ky:.2f}_k{kyaw}',B,R,p+[0,0,.008+up],p4=dict(drawer=dict(xo=max(x,-1.54)),drop_potato=True),desc=f'drawer bowl, cranked handle (knob x +0.17, y {ky}, z 1.10) turned {kyaw} deg toward +x, held at {tag} (bowl x {x})')
 # ---- (a) round 3: the cranked-handle bowl rolled over the T2L pan (mouth 6 cm over the pan rim), cart fixed ----
 B=P4.dbh(.17,.195,.237,0)
 for cx in (-1.25,-1.10):
  t2=dict(present=True);R0,p0=P4.t2l_world(cx,t2)
  for yaw in (0,90,-90,180):
   for deg in (100,-100,130,-130):
    _,(R2,p2)=mouth_pose(B,K.Rz(yaw),p0+[0,0,P4.STG_H+.06],deg);add(f'dbp_c{cx:+.2f}_k{yaw}_{deg}',B,R2,p2,p4=dict(t2l=t2,drawer=dict(xo=-1.49),drop_potato=True),cart=cx,desc=f'cranked-handle bowl (yaw {yaw}) rolled {deg}, mouth 6 cm over the T2L pan rim, cart {cx}')
 for cx in (-1.25,):
  t2=dict(present=True);R0,p0=P4.t2l_world(cx,t2)
  for dz in (.12,.18):
   for yaw in (0,90,-90,-45,45):
    for deg in (100,-100,130,-130):
     _,(R2,p2)=mouth_pose(B,K.Rz(yaw),p0+[0,0,P4.STG_H+dz],deg);add(f'dbq_c{cx:+.2f}_dz{dz:.2f}_k{yaw}_{deg}',B,R2,p2,p4=dict(t2l=t2,drawer=dict(xo=-1.49),drop_potato=True),cart=cx,desc=f'cranked-handle bowl (yaw {yaw}) rolled {deg}, mouth {dz} over the T2L pan rim, cart {cx}')
 # ---- cooking time: the pan held at swing waypoints in front of the arm base (cart frame, cart 0.45) ----
 for lx in (-.25,-.05,.15):
  for ly in (.22,.32,.42):
   for lz in (1.00,1.12,1.25):
    for yaw in (0,45):
     t2=dict(present=False);add(f'stgsw_x{lx:+.2f}_y{ly:.2f}_z{lz:.2f}_k{yaw}','stg',K.Rz(yaw),np.array([lx,ly,lz])+[.45,-.21,0],p4=dict(t2l=t2),cart=.45,desc=f'pan held at cart-frame ({lx},{ly},{lz}), yaw {yaw}, cart 0.45')
 # ---- cooking time, mirrored (the cups' T2R pour mirrored): the cart RIGHT of the wok, the pan on the arm's left ----
 for cx in (1.10,1.21,1.30):
  t2=dict(present=False);g=K.OBJ['stg']['grip']
  for gz in (1.38,1.33):
   for yaw in (0,90):
    RL=K.Rz(yaw);pw=np.array([K15.WOK0[0],.07,gz-g[2]]);R2,p2=P3.rolled_about_knob('stg',RL,pw,135);R3,p3=P3.rolled_about_knob('stg',RL,pw,-135)
    add(f'stgm_c{cx:.2f}_g{gz:.2f}_y{yaw}_lvl','stg',RL,pw,p4=dict(t2l=t2),cart=cx,desc=f'pan level over the wok, cart {cx} (pan on the arm left), grip {gz}, lug yaw {yaw}')
    add(f'stgm_c{cx:.2f}_g{gz:.2f}_y{yaw}_t135','stg',R2,p2,p4=dict(t2l=t2),cart=cx,desc=f'pan tipped 135 over the wok, cart {cx}, grip {gz}, lug yaw {yaw}')
    add(f'stgm_c{cx:.2f}_g{gz:.2f}_y{yaw}_t-135','stg',R3,p3,p4=dict(t2l=t2),cart=cx,desc=f'pan tipped -135 over the wok, cart {cx}, grip {gz}, lug yaw {yaw}')
  R,p=P4.t2l_world(cx,t2);add(f'stgm_c{cx:.2f}_pick','stg',R,p+[0,0,.012],p4=dict(t2l=t2),cart=cx,desc=f'pan held 12 mm over its T2L cradle, cart {cx}')
 # ---- tray crossing high in front of / over the arm base (cart -1.19, cart-frame positions of the tray centre) ----
 for lx in (-.15,0.,.15):
  for ly in (.20,.30):
   for lz in (1.40,1.50):
    add(f'cthi_x{lx:+.2f}_y{ly:.2f}_z{lz:.2f}','ctray',np.eye(3),np.array([lx,ly,lz])+[-1.19,-.21,0],st=('lever',),p4=dict(t2l=dict(present=True)),cart=-1.19,desc=f'catch tray held at cart-frame ({lx},{ly},{lz}), cart -1.19')
 # ---- the step-3 prep bowl at plating spot 2 (knob -x) poured into the T2L pan, cart such that the pan is in front of the spot ----
 for cx in (.49,.40,.60):
  t2=dict(present=True);R0,p0=P4.t2l_world(cx,t2)
  add(f'p2b_c{cx:.2f}_pick','bowl',K.Rz(180),[.17,.15,.858],p4=dict(t2l=t2),cart=cx,desc=f'step-3 prep bowl held 8 mm over plating spot 2 (knob -x), cart {cx}')
  for yaw in (180,-90,90):
   for deg in (110,-110,130,-130):
    _,(R2,p2)=mouth_pose('bowl',K.Rz(yaw),p0+[0,0,P4.STG_H+.10],deg);add(f'p2b_c{cx:.2f}_k{yaw}_{deg}','bowl',R2,p2,p4=dict(t2l=t2),cart=cx,desc=f'prep bowl (knob yaw {yaw}) rolled {deg}, mouth 10 cm over the T2L pan rim, cart {cx}')
 # ---- catch tray at the lever with the cart fixed close right of it (pan beside the lever, no crossing) ----
 lx,ly,_=L['lever']
 for cx in (-.65,-.70,-.75,-.80,-.85):
  t2=dict(present=True)
  add(f'ctc_c{cx:+.2f}_seat','ctray',I,[lx,ly,.862+.008],st=('lever',),p4=dict(t2l=t2),cart=cx,desc=f'catch tray 8 mm over its seat, cart {cx}')
  add(f'ctc_c{cx:+.2f}_out','ctray',I,[lx,ly-.15,.862+.018],st=('lever',),p4=dict(t2l=t2),cart=cx,desc=f'catch tray pulled out 15 cm (18 mm up), cart {cx}')
  add(f'ctc_c{cx:+.2f}_hi','ctray',I,[lx,ly-.15,.972],st=('lever',),p4=dict(t2l=t2),cart=cx,desc=f'catch tray lifted in front of the lever, cart {cx}')
 # ---- (a) round 4: the cranked-handle bowl poured into a COUNTER bowl (front spot by the sink / plating spot 2), free cart ----
 B=P4.dbh(.17,.195,.237,0)
 for nm,bc in (('FS',np.array([-.86,.15])),('P2',np.array([.17,.15]))):
  for yaw in (0,45,90,-45,-90,180):
   for deg in (110,-110,130,-130):
    tgt=np.array([bc[0],bc[1],K19.COUNTER_TOP+P3.BOWL['H']+.14])
    _,(R2,p2)=mouth_pose(B,K.Rz(yaw),tgt,deg);add(f'dbc_{nm}_k{yaw}_{deg}',B,R2,p2,objs=(car,tom,('bowl',K.Rz(180).tolist(),[bc[0],bc[1],K19.COUNTER_TOP])),p4=dict(drawer=dict(xo=-1.49),drop_potato=True),desc=f'cranked-handle bowl (yaw {yaw}) rolled {deg}, mouth 14 cm over a prep bowl at {nm}')
 # ---- T2L staging pan on the cart (pick 12 mm over the cradle), cart fixed ----
 for cy,zb in ((.05,.93),(.03,.93),(.05,.98),(.08,.93),(.02,.98)):
  t2=dict(cy=cy,zb=zb,present=False)
  for pd in (0,30):
   S_=P4.stg_pitched(pd) if pd else 'stg'
   for cx in (-.90,-.45,.172):
    R,p=P4.t2l_world(cx,t2);add(f'stg_pick_y{cy:.2f}_z{zb:.2f}_p{pd}_c{cx:+.2f}',S_,R,p+[0,0,.012],p4=dict(t2l=t2),cart=cx,desc=f'staging pan held 12 mm over its T2L cradle (cart y {cy}, bottom {zb}), approach pitched {pd}, cart {cx}')
 # ---- pours INTO the T2L pan (it stands on its cradle): catch tray (lever out) and drawer bowl ----
 for cy,zb in ((.05,.93),(.05,.98)):
  t2=dict(cy=cy,zb=zb,present=True);rim=zb+P4.STG_H
  for cx in (-.60,-.45,-1.20):
   R0,p0=P4.t2l_world(cx,t2)
   for deg in (-120,-90,120):
    for dz in (.06,.10):
     _,(R2,p2)=mouth_pose('ctray',I,p0+[0,0,P4.STG_H+dz],deg);add(f'ct2_y{cy:.2f}_z{zb:.2f}_c{cx:+.2f}_{deg}_dz{dz:.2f}','ctray',R2,p2,st=('lever',),p4=dict(t2l=t2),cart=cx,desc=f'catch tray rolled {deg}, mouth {dz} over the T2L pan rim, cart {cx}')
   for deg in (-110,110):
    for yaw in (0,-90,90):
     for pd in (0,30):
      B=P3.pitched(f'dbowl_p{pd}') if pd else 'dbowl'
      _,(R2,p2)=mouth_pose(B,K.Rz(yaw),p0+[0,0,P4.STG_H+.06],deg);add(f'db2_y{cy:.2f}_z{zb:.2f}_c{cx:+.2f}_{deg}_k{yaw}_p{pd}',B,R2,p2,p4=dict(t2l=t2,drawer=dict(xo=-1.45),drop_potato=True),cart=cx,desc=f'drawer bowl (knob yaw {yaw}, pitch {pd}) rolled {deg} with its mouth 6 cm over the T2L pan rim, cart {cx}')
 # ---- the pan over the wok (cups pour pose: axis (0.83, 0.09), grip at 1.38 m), level and tipped 135 ----
 for cy,zb in ((.05,.93),):
  t2=dict(cy=cy,zb=zb,present=False)
  for gz in (1.38,1.33):
   for yaw in (0,-90):
    for tip in (135,-135):
     g=K.OBJ['stg']['grip'];RL=K.Rz(yaw);pw=np.array([K15.WOK0[0],.07,gz-g[2]])   # axis y 0.07: the pan (r 70 mm) stays 10 mm in front of the hood front (y 0.15); at the cups' 0.09 it hit the hood
     R2,p2=P3.rolled_about_knob('stg',RL,pw,tip)
     for cx in (.45,):
      add(f'stgwok_g{gz:.2f}_y{yaw}_lvl_c{cx:.2f}','stg',RL,pw,p4=dict(t2l=t2),cart=cx,desc=f'pan level over the wok, grip {gz}, lug yaw {yaw}')
      add(f'stgwok_g{gz:.2f}_y{yaw}_t{tip}_c{cx:.2f}','stg',R2,p2,p4=dict(t2l=t2),cart=cx,desc=f'pan tipped {tip} over the wok, grip {gz}, lug yaw {yaw}')
 return P
def run(name):
 import chain
 from scene import build,save
 from checker import Checker
 from solver import solve
 import kitchen15 as K15,kitchen16 as K,kitchen17 as K17,kitchen19 as K19,kitchen19p3 as P3,kitchen19p4 as P4,arms
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=8.,0.,180.
 Pr=probes()[name];sign=int(KV.get('SIGN',1))
 BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},r14_fridge=True,r17_lever=0.,**K19.base_cfg())
 sc=K19.layout_scene(*Pr['stations'],objs=Pr['objs']);sc['stations']['slicer']=K19.LAYOUT['slicer']
 cfg=chain.chain_cfg('SD',**{**BASE,'r19':sc,'r19p4':Pr['p4'],**K17.held_cfg(Pr['obj'],sign)})
 tree,meta=build(cfg,None);K19.add(tree,cfg);P4.add(tree,cfg);P3.mesh_held(tree);P4.mesh(tree)
 Rl,pl=K17.lever_pose(K17.LEVER_OPEN);K._add(tree.find('worldbody'),'u_open_',K.OBJ['lever']['parts'],Rl,pl,rgba='.75 .77 .8 1')
 ch=Checker(tree,meta);R=np.array(Pr['R']);p=np.array(Pr['p']);pt,Rt=K.tcp_pose(Pr['obj'],R,p,sign)
 t=dict(name=name,points=[list(pt)]*2,held=None,kind='transfer',force=None,approach=list(Rt[:,0]),jaws=[tuple(sign*(R@K.OBJ[Pr['obj']]['j']))],jaw_q=K19.JAW[Pr['obj']])
 if Pr.get('cart') is not None:t['cart_x']=float(Pr['cart'])
 stat=collections.Counter();cands=[]
 for seed in [int(s) for s in KV.get('SEEDS','14,15').split(',')]:
  r=solve(ch,pt,list(Rt[:,0]),target=t,seed=seed);stat.update(r['status_counts']);cands+=r['candidates']
 cands=sorted(cands,key=lambda c:-c['reserve_mm']);bl=collections.Counter()
 if not cands:
  r=solve(ch,pt,list(Rt[:,0]),target=t,seed=99)
  for row in r['rows']:
   for h in (row.get('check') or {}).get('hits',[]):bl[' | '.join(sorted(h['pair']))]+=1
 out=dict(probe=name,desc=Pr['desc'],obj=Pr['obj'],R=Pr['R'],p=Pr['p'],cart_fixed=Pr.get('cart'),p4=Pr['p4'],tcp=pt.tolist(),approach=Rt[:,0].tolist(),sign=sign,ok=bool(cands),n_ok=len(cands),status=dict(stat),
  best_reserve_mm=round(cands[0]['reserve_mm'],1) if cands else None,carts=sorted({round(c['q'][0],2) for c in cands}),best_q=cands[0]['q'] if cands else None,blockers=bl.most_common(6),arm=arms.current())
 save(f"{OUT}/probe_{name}{'_s'+str(sign) if sign!=1 else ''}{arms.tag()}.json",out)
 print(f"{name:44s} ok {len(cands):3d} res {out['best_reserve_mm']} carts {out['carts'][:5]} {dict(stat)} {out['blockers'][:2]}",flush=True)
def chute():
 """Option (b) geometry, read from the built scene (no IK): where the spout is, what stands on the counter around the
 slicer, and the drop a chute from the spout outlet to each candidate bowl spot needs at a given slope."""
 import kitchen19 as K19,kitchen16 as K,kitchen17 as K17,kitchen19p3 as P3,chain,mujoco,xml.etree.ElementTree as E
 from scene import build,save
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=8.,0.,180.
 BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},r14_fridge=True,r17_lever=0.,**K19.base_cfg())
 cfg=chain.chain_cfg('SD',**{**BASE,'r19':K19.layout_scene()});tree,meta=build(cfg,None);K19.add(tree,cfg)
 m=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));d=mujoco.MjData(m);mujoco.mj_forward(m,d)
 def aabb(n):
  g=m.geom(n).id;ab=m.geom_aabb[g];Rg=d.geom_xmat[g].reshape(3,3);c=d.geom_xpos[g]+Rg@ab[:3];e=np.abs(Rg)@ab[3:];return (c-e).round(4).tolist(),(c+e).round(4).tolist()
 names=['r19_slicer_station_slicer_spout' if 'r19_slicer_station_slicer_spout' in [m.geom(i).name for i in range(m.ngeom)] else 'slicer_spout']
 gs={m.geom(i).name for i in range(m.ngeom)}
 sp=[n for n in gs if n.endswith('slicer_spout')][0];base=[n for n in gs if n.endswith('slicer_base')][0]
 items={n:aabb(n) for n in [sp,base,'raw_tray','raw_greens','r19_raw_potato','counter_left','upper_cabinet_0','r07_closed_door_0_0','north_wall','stored_bowl_potato_bowl_outer_bottom','r16_rest_spatula']}
 lo,hi=items[sp];z_out=lo[2]
 rows=[]
 for slope in (20,25,30,35,40):
  for nm,(bx,by,brim) in dict(front_gap=(-1.55,.15,.85+.06),open_strip_right=(-1.40,.15,.85+.06),back_strip_potato_spot=(-1.40,.46,.85+.06)).items():
   run=float(np.hypot(bx-(lo[0]+hi[0])/2,by-hi[1])) if by<lo[1] else float(abs(bx-(lo[0]+hi[0])/2))
   need=run*np.tan(np.radians(slope));rows.append(dict(slope_deg=slope,target=nm,bowl_rim_z=brim,horizontal_run_m=round(run,3),drop_needed_m=round(need,3),drop_available_m=round(z_out-brim,3),feasible=bool(z_out-brim>=need)))
 out=dict(items=items,spout_outlet_bottom_z=z_out,rows=rows,note='option (b): a chute from the spout outlet (bottom z, back face of the turned slicer) to a bowl; drop needed = run x tan(slope); slope is an ESTIMATE (no sourced sliding angle for wet cut vegetables on a printed chute)')
 save(f'{OUT}/chute_geometry.json',out);print(json.dumps(out,indent=1)[:3000])
if __name__=='__main__':
 if KV.get('MODE')=='chute':chute();sys.exit()
 if 'ONE' in KV:run(KV['ONE']);sys.exit()
 names=[n for pat in KV.get('PROBES','').split(',') if pat for n in probes() if n==pat or (pat.endswith('*') and n.startswith(pat[:-1]))]
 if not names:print('\n'.join(probes()));sys.exit()
 from concurrent.futures import ThreadPoolExecutor
 def one(n):
  r=subprocess.run([sys.executable,__file__,f'ONE={n}']+[a for a in sys.argv[1:] if a.startswith(('ARM=','SEEDS=','SIGN='))],capture_output=True,text=True)
  return (r.stdout.strip().splitlines() or [n+' ERR '+r.stderr[-600:]])[-1]
 with ThreadPoolExecutor(int(KV.get('NPAR',8))) as ex:
  for o in ex.map(one,names):print(o,flush=True)
