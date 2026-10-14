"""R19 cart docking (GitHub #39): the cart's load lean on the docking rail, the registration budget of the design and its
BOM. New file; reads stored paths only; writes only to results/r19/dock/.

PART=lean   Load lean of the cart, [M] gravity moments of the arm + held payload along every adopted stored path x [E]
            support stiffnesses. Static rigid-body cart on four vertical springs (small rotations): the support points
            (cart frame) and stiffnesses are those of
              rail    the design: two V-wheel trucks on the rail (+-0.27, +0.194, K_TRUCK each) + the two drive wheels
                      (+-0.22, -0.22, K_TYRE each); the front castors are off the floor;
              castors the R10 / #14 cart: front castors (+-0.22, +0.11, K_CASTOR) + drive wheels (as above), bumper off
                      (R19_CART: a bumper on the doors carries no lean with swivel or fixed castors, see R19_DOCK.md 3.2).
            For every state: the support reactions (all must stay > 0), the roll (tilt_x, deg: the slope dz/dy of the cart base,
            + = the counter side higher = the top leans toward the aisle; only its variation matters, the static part is
            levelled out at commissioning with the eccentric wheel bushings), the pitch (tilt_y) and the drop of the J1 base point, relative to the
            reference posture (the median of all states, i.e. the station tilt calibrated at a mid posture), and the
            half-range. Payload at the TCP site (kg): wok 1.8 + food 1.15 (R19_CART / r19smooth.load_parts), spider 0.45
            + 0.3 food [E], spatula 0.3, lid 0.8, lever 0 (closed chain), stir spatula 0.3, prep sets 1.0 [E].
            Masses: the sim arm (menagerie, 21.0 kg; R19_CART table: DH 20.6 kg) and the R19_CART BOM cart (51.3 kg,
            CoM (0.001, -0.102, 0.353) [D]); the gripper + fingers as modelled.
PART=budget the per-axis registration budget of the design (R19_DOCK.md section 3) -> the cart budget boxes
            (half-ranges) for the tolerance replays: dock_rail (mechanics, commissioning shims, no software map) and
            dock_rail_map (+ the commissioning pose map used by the path certification).
PART=bom    the BOM with rough prices.
python r19dock_budget.py PART=lean|budget|bom|report ARM=ur5e_enc2_pgc PY=.15 [K_TYRE=2e5] [K_TRUCK=5e6] [K_CASTOR=2e5]"""
import sys,os,json,glob,math
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a);PART=KV.get('PART','lean');OUT='results/r19/dock'
K_TYRE=float(KV.get('K_TYRE',2e5));K_TRUCK=float(KV.get('K_TRUCK',5e6));K_CASTOR=float(KV.get('K_CASTOR',2e5))
G=9.81;DOCK_Y=-.21
CART_BOM=dict(m=51.3,c=[.001,-.102,.353])   # R19_CART section 1 (BOM, steel mast) [D]
PATHS=[('wok','results/r17/chain_wok_s-1_final_py.15_ur5e_enc2_pgc.json',1.8+1.15),('wok_plate2b','results/r17/chain_wok_s-1_r18plate2b_py.15_ur5e_enc2_pgc.json',1.8+1.15),
 ('spatula','results/r17/chain_spatula_s-1_r18roll-1.15_.30_ur5e_enc2_pgc.json',.3),('lever','results/r17/chain_lever_s+1_final_ur5e_enc2_pgc.json',0.),
 ('lid','results/r17/chain_lid_s-1_final_ur5e_enc2_pgc.json',.8),('spider','results/r19/pot/chain_spider_s+1_pot_1.56_.20_ur5e_enc2_pgc.json',.45+.3)]
def supports(kind):
 import kitchen19dock as D
 yf=D.TRACK['yc']-DOCK_Y
 if kind=='rail':return [(-D.TRUCK_X,yf,K_TRUCK),(D.TRUCK_X,yf,K_TRUCK),(-.22,-.22,K_TYRE),(.22,-.22,K_TYRE)]
 return [(-.22,.11,K_CASTOR),(.22,.11,K_CASTOR),(-.22,-.22,K_TYRE),(.22,-.22,K_TYRE)]
def solve(sup,W,cx,cy):
 """rigid cart on vertical springs (x_i, y_i, k_i): the reactions and the displacement (z, slope along y a, slope along
 x b) of the cart under a total weight W (N) at (cx, cy) (cart frame); w_i = z + a y_i + b x_i (up +)."""
 K=np.zeros((3,3));F=np.array([-W,-W*cy,-W*cx])
 for x,y,k in sup:v=np.array([1.,y,x]);K+=k*np.outer(v,v)
 u=np.linalg.solve(K,F);R=[-k*(u[0]+u[1]*y+u[2]*x) for x,y,k in sup];return u,np.array(R)
def lean():
 import mujoco,chain
 import r19tol_core as C
 from scene import build
 from checker import Checker
 cfg=chain.chain_cfg('SD',**C.BASE);tree,meta=build(cfg,None);ch=Checker(tree,meta);m,d=ch.m,ch.d
 cart=m.body('rail_structure').id;mount=m.body('R_mount').id;sid=m.site('R_prep').id
 arm=[b for b in range(1,m.nbody) if b!=cart and m.body_rootid[b]==m.body_rootid[cart] and b!=cart]
 # bodies on the cart tree other than the cart body itself (mount, arm links, tool, jaws): the moving masses
 def subtree(b):
  while b and b!=cart:b=m.body_parentid[b]
  return b==cart
 mov=[b for b in range(1,m.nbody) if b!=cart and subtree(b)]
 marm=float(m.body_mass[mov].sum())
 sets=list(PATHS)
 sf=f"results/r19/stir/lib_stir_cycle_{__import__('arms').current()}.json"
 if os.path.exists(sf):sets.append(('stir',sf,.3))
 for f in sorted(glob.glob('results/r19/prep/chain_*_full_ur5e_enc2_pgc.json'))+['results/r19/prep4/chain_stgwok_m5_ur5e_enc2_pgc.json']:
  sets.append(('prep:'+os.path.basename(f)[6:-5],f,1.0))
 rows={};allc=[]
 for name,f,pay in sets:
  try:r=C.J(f)
  except Exception:continue
  Q=r.get('play') or (r.get('states') or {}).get('q')
  if not Q:continue
  Q=C.unwrap(Q);cs=[]
  for q in Q:
   d.qpos[:]=q;mujoco.mj_kinematics(m,d);x0=d.xpos[cart]
   mm=m.body_mass[mov];P=d.xipos[mov]-x0;mc=(mm[:,None]*P).sum(0)
   tcp=d.site_xpos[sid]-x0;M=marm+pay;mc=mc+pay*tcp
   cs.append(np.r_[mc/M,M])
  cs=np.array(cs);rows[name]=cs;allc.append(cs)
 out=dict(method=__doc__,k=dict(K_TYRE=K_TYRE,K_TRUCK=K_TRUCK,K_CASTOR=K_CASTOR),moving_mass_kg=round(marm,2),cart=CART_BOM,configs={})
 for kind in ('rail','castors'):
  sup=supports(kind);res={}
  A=np.vstack(allc)
  def state(c):
   Wm=c[3]*G;Wc=CART_BOM['m']*G;W=Wm+Wc;cx=(Wm*c[0]+Wc*CART_BOM['c'][0])/W;cy=(Wm*c[1]+Wc*CART_BOM['c'][1])/W
   u,R=solve(sup,W,cx,cy)
   import kitchen19dock as D
   ybase=.08   # J1 axis (mount_y) in the cart frame
   return dict(tilt_x_deg=float(np.degrees(u[1])),tilt_y_deg=float(np.degrees(-u[2])),z_base_mm=float((u[0]+u[1]*ybase)*1e3),Rmin=float(R.min()),R=R,cy=cy,cx=cx)
  S=[state(c) for c in A];tx=np.array([s['tilt_x_deg'] for s in S]);ty=np.array([s['tilt_y_deg'] for s in S]);zb=np.array([s['z_base_mm'] for s in S])
  ref=dict(tilt_x=float(np.median(tx)),tilt_y=float(np.median(ty)),z=float(np.median(zb)))
  per={}
  i0=0
  for name,cs in rows.items():
   n=len(cs);t=tx[i0:i0+n];y_=ty[i0:i0+n];z=zb[i0:i0+n];Rm=min(s['Rmin'] for s in S[i0:i0+n]);i0+=n
   per[name]=dict(states=n,tilt_x_deg=[round(float(t.min()),4),round(float(t.max()),4)],tilt_y_deg=[round(float(y_.min()),4),round(float(y_.max()),4)],
    z_base_mm=[round(float(z.min()),3),round(float(z.max()),3)],min_support_N=round(Rm,1))
  front=[s['R'][:2].min() for s in S];rear=[s['R'][2:].min() for s in S];front2=[s['R'][:2].sum() for s in S]
  res=dict(supports=[list(s) for s in sup],reference_median=ref,
   tilt_x_halfrange_deg=round(float((tx.max()-tx.min())/2),4),tilt_x_max_dev_from_median_deg=round(float(np.max(abs(tx-ref['tilt_x']))),4),
   tilt_y_halfrange_deg=round(float((ty.max()-ty.min())/2),4),z_base_halfrange_mm=round(float((zb.max()-zb.min())/2),3),
   min_front_support_N=round(float(min(front)),1),min_front_pair_total_N=round(float(min(front2)),1),min_rear_support_N=round(float(min(rear)),1),cop_y_range_m=[round(min(s['cy'] for s in S),4),round(max(s['cy'] for s in S),4)],per_path=per)
  out['configs'][kind]=res
  print(kind,json.dumps({k:v for k,v in res.items() if k!='per_path'}),flush=True)
  for n_,p_ in per.items():print('   ',n_,p_,flush=True)
 os.makedirs(OUT,exist_ok=True);tag=KV.get('TAG','');fn=f'{OUT}/lean{("_"+tag) if tag else ""}.json';json.dump(out,open(fn,'w'),indent=1,default=float);print(fn)
# ---------------------------------------------------------------- the budget (R19_DOCK.md section 3)
DYN=1.1   # [E] dynamic increment of the posture-dependent lean (R19_CART section 3: dynamic vs static CoP within a few mm in normal motion)
def budget_terms(L):
 """(axis, term, tier-1 half-range, tier-2 half-range, label, basis). Units: mm for x, y, z; deg for yaw / tilts.
 tier 1 'dock_rail'     = the hardware + the commissioning shims (the rail shimmed so the cart stays level along x);
 tier 2 'dock_rail_map' = + the commissioning pose map (z, tilt_x, tilt_y vs cart x, and the measured lean stiffness)
                          applied in the path certification (a checker hook, R19_DOCK.md section 7)."""
 r=L['configs']['rail'];lean=r['tilt_x_max_dev_from_median_deg']*DYN;pitch=r['tilt_y_halfrange_deg']*DYN;zl=r['z_base_halfrange_mm']*DYN
 return [
  ('x','station index: 12 mm ball-nose pin in a hardened 90 deg V-block (50 N preload, then held by the self-locking actuator)',.02,.02,'E','kinematic ball-in-V contact: couplings repeat to sub-micron when clean and preloaded (Slocum 2010) [S]; 0.02 mm for finish, debris, cart compliance'),
  ('x','magnetic scale over the in-set travel and between stations (re-zeroed at every docking)',.04,.04,'S','RLS LM10 accuracy grade +-40 um over the measured length (+-20 / +-10 um grades exist) [S]'),
  ('x','tape bonding / read head (hysteresis < 3 um at 0.3 mm ride height [S]) / head-to-arm-base calibration',.03,.03,'E',''),
  ('x','rail thermal growth vs the building (Al 23e-6/K vs ~10e-6/K, +-5 K, up to 2.4 m from the anchor)',.16,.16,'E','anchor at the centre plinth angle; a steel extrusion or a floating steel tape would halve it'),
  ('y','V track straightness after installation (laser line / taut line, shims, plinth angles)',.20,.20,'E','DualVee track needs no precision mounting surface [S]; +-0.2 mm over 4.6 m by alignment'),
  ('y','V wheel radial play / runout (double-row angular contact, eccentric preload)',.02,.02,'E','no runout figure published'),
  ('y','rail lateral deflection under the arm reactions (<= 50 N per truck)',.05,.05,'E','extrusion bonded to the floor + angles every 0.6 m'),
  ('y','creep / settling of the bonded rail between re-checks',.10,.10,'E','re-checked at service'),
  ('z','rail top level at the trucks (shims)',.10,.10,'E','shim resolution 0.05-0.1 mm'),
  ('z','rear drive wheels on the tile floor: tier 1 the rail follows it (cart kept level), tier 2 mapped',1.0,.15,'S/E','GB 50209: 2 mm under a 2 m straightedge [S] -> +-1 mm long-wave; mapped residual 0.15 mm'),
  ('z','load: tyre compression at the J1 base (PART=lean, rail, x1.1 dynamic)',zl,.3*zl,'M/E','tier 2: 30 % residual of the stiffness-predicted value'),
  ('yaw','V track local straightness over the 0.54 m truck base (+-0.05 mm at each truck)',.0106,.0106,'E','atan(0.1 / 540)'),
  ('yaw','V wheel runout at both trucks (+-0.02 mm)',.0042,.0042,'E','atan(0.04 / 540)'),
  ('tilt_x','load lean toward the counter (PART=lean, rail: max deviation from a mid-posture zero, x1.1 dynamic)',lean,.3*lean,'M/E','[M] arm + payload moments over every stored state x [E] tyre 2e5 N/m, truck 5e6 N/m'),
  ('tilt_x','rear floor under the drive wheels: tier 1 short-wave residual after the rail follows the floor (tile lippage), tier 2 mapped',.035,.015,'S/E','GB 50209 joint height difference 0.5 mm [S]: ~0.25 mm effective after 2-wheel averaging / 414 mm'),
  ('tilt_x','commissioning measurement (MEMS inclinometer, SCL3300 class: 0.001 deg/rtHz, offset +-0.005 deg/K [S], +-3 K)',.015,.015,'S/E','relative to the reference station at the same temperature'),
  ('tilt_x','tyre wear / temperature between re-maps (PU radius +-0.05 mm)',.007,.007,'E','0.05 / 414 mm'),
  ('tilt_y','rail top level between the trucks (+-0.05 mm over 0.54 m)',.011,.011,'E',''),
  ('tilt_y','load pitch (PART=lean, rail, x1.1 dynamic)',pitch,.3*pitch,'M/E',''),
  ('tilt_y','commissioning measurement',.015,.015,'S/E','as tilt_x')]
TARGET=dict(x=1.0,y=.5,z=.5,yaw=.05,tilt_x=.11,tilt_y=.03)   # #39 target = r19tol_replay SCENARIOS['dock_stops'] (x 1.04, y .5, z .5, yaw .054, tilt_x .11, tilt_y .03)
STEP=dict(x=.05,y=.05,z=.05,yaw=.005,tilt_x=.005,tilt_y=.005)
def budget():
 L=json.load(open(f'{OUT}/lean.json'));T=budget_terms(L);up=lambda v,s:math.ceil(v/s-1e-9)*s
 boxes={}
 for k,tier in (('dock_rail',2),('dock_rail_map',3)):
  rss={a:math.sqrt(sum(t[tier]**2 for t in T if t[0]==a)) for a in TARGET}
  boxes[k]=dict(rss={a:round(v,4) for a,v in rss.items()},box={a:round(up(v,STEP[a]),3) for a,v in rss.items()})
  boxes[k]['meets_target']={a:bool(boxes[k]['box'][a]<=TARGET[a]+1e-9) for a in TARGET}
 sens={}
 for tag in ('soft','stiff'):
  f=f'{OUT}/lean_{tag}.json'
  if os.path.exists(f):
   Ls=json.load(open(f));sens[tag]=dict(k=Ls['k'],rail_halfrange_deg=Ls['configs']['rail']['tilt_x_halfrange_deg'],rail_maxdev_deg=Ls['configs']['rail']['tilt_x_max_dev_from_median_deg'],
    castors_halfrange_deg=Ls['configs']['castors']['tilt_x_halfrange_deg'],castors_maxdev_deg=Ls['configs']['castors']['tilt_x_max_dev_from_median_deg'])
 rl=L['configs']['rail'];cs=L['configs']['castors']
 out=dict(terms=[dict(axis=a,term=t,tier1=round(v1,4),tier2=round(v2,4),label=l,basis=b) for a,t,v1,v2,l,b in T],target=TARGET,boxes=boxes,
  load_lean=dict(rail=dict(halfrange_deg=rl['tilt_x_halfrange_deg'],maxdev_deg=rl['tilt_x_max_dev_from_median_deg'],min_front_truck_N=rl['min_front_support_N'],min_front_pair_N=rl.get('min_front_pair_total_N')),
   castors=dict(halfrange_deg=cs['tilt_x_halfrange_deg'],maxdev_deg=cs['tilt_x_max_dev_from_median_deg']),sensitivity=sens,dynamic_factor=DYN),
  scenario_halfranges_m_rad={k:[v['box']['x']*1e-3,v['box']['y']*1e-3,v['box']['z']*1e-3,math.radians(v['box']['yaw']),math.radians(v['box']['tilt_x']),math.radians(v['box']['tilt_y'])] for k,v in boxes.items()})
 json.dump(out,open(f'{OUT}/budget.json','w'),indent=1);print(json.dumps({k:v for k,v in out.items() if k!='terms'},indent=1))
 for r in out['terms']:print(f"| {r['axis']} | {r['term']} | {r['tier1']:g} | {r['tier2']:g} | [{r['label']}] {r['basis']} |")
# ---------------------------------------------------------------- BOM (R19_DOCK.md section 6)
BOM=[ # (item, qty, unit, unit price CNY low (domestic generic), high (branded reference part), label, note)
 ('Aluminium extrusion 40x30 (or 40x40) 6063-T5, slot 8, 2 x 2.31 m + 2 joint plates / dowels','4.62','m',30,60,'E','industrial profile class'),
 ('V-edge track, hardened (DualVee T3 stainless AISI 420 [S] or a domestic 90 deg V guide), butt-joined','4.62','m',80,700,'E','low: domestic machine V guide; high: DualVee imported'),
 ('V-groove guide wheel, sealed double-row, + eccentric bushing (DualVee W3 [S] or domestic)','2','pc',30,400,'T/E','Taobao search 2026-10-14: machine-tool V rollers ~CNY 30-100 [T]; DualVee [E]'),
 ('Truck plates 6 mm steel, laser-cut + M8 fasteners','2','pc',40,80,'E',''),
 ('Anti-lift keeper: 4 mm steel arm + UHMW-PE T-head slider','2','pc',30,80,'E',''),
 ('Magnetic scale: 2 mm-pole tape 4.6 m + read head (incremental with reference marks, or absolute RS485/SSI)','1','set',400,4000,'T/E','Taobao search 2026-10-14: read heads CNY 20-750, absolute RS485/SSI heads ~CNY 365-400 [T]; tape ~CNY 50-150/m [E]; RLS LM10 [E] a few k'),
 ('Hardened V-block inserts (440C or 45# HRC 45), 30 x 16 x 8 mm, 90 deg V, + 2 T-nuts / screws each','11','pc',30,80,'E','machined; one per station'),
 ('Index pin actuator: 24 V mini linear actuator, 15-20 mm stroke, >= 150 N, self-locking, limit switches / encoder','1','pc',30,205,'T','Taobao search 2026-10-14: 150 N mini actuators CNY 30-115, with encoder CNY 205 [T]'),
 ('Hardened 12 mm ball-nosed pin, bronze bush, disc springs, housing','1','set',80,200,'E',''),
 ('Plinth angles 30x30x3 (6 pc, 2 screws each), MS-polymer adhesive (2 cartridges), VHB tape, shim set 0.05-1 mm','1','set',100,250,'E',''),
 ('Rubber end buffers','2','pc',10,30,'E',''),
 ('Commissioning + monitor: MEMS inclinometer (SCL3300 class) on the deck, 0.02 mm/m machinist level, laser line','1','set',300,900,'E','the inclinometer stays on the cart as a live lean monitor'),
 ('Front castors on 5 mm raised mounts (re-use the #14 fixed castors)','2','pc',0,50,'E','spacers only'),
]
def bom():
 lo=hi=0.;rows=[]
 for it,q,u,a,b,l,n in BOM:
  qq=float(q);lo+=qq*a;hi+=qq*b;rows.append(dict(item=it,qty=q,unit=u,unit_cny=[a,b],line_cny=[round(qq*a),round(qq*b)],label=l,note=n))
 out=dict(rows=rows,total_cny=[round(lo),round(hi)],note='rough prices, no purchase, no vendor contact. low = domestic generic parts, high = the branded reference parts (DualVee, RLS LM10). [T] = Taobao search-result listing prices seen 2026-10-14 (read-only, not quotes); [E] = estimate',
  not_included='the #14 hub-motor holding brakes (R19_CART: ~CNY 4k for two), labour, the kitchen survey')
 json.dump(out,open(f'{OUT}/bom.json','w'),indent=1)
 for r in rows:print(f"| {r['item']} | {r['qty']} {r['unit']} | {r['unit_cny'][0]}-{r['unit_cny'][1]} | {r['line_cny'][0]}-{r['line_cny'][1]} | [{r['label']}] {r['note']} |")
 print('total CNY',out['total_cny'])
if __name__=='__main__' and PART!='report':
 {'lean':lean,'budget':budget,'bom':bom}[PART]()
# ---------------------------------------------------------------- summary (R19_DOCK.md sections 4-5)
def _scen(f,box):
 try:r=json.load(open(f))
 except Exception:return None
 s=(r.get('scenarios') or {}).get(box)
 return None if s is None else s['gate']['min_mm']
def report():
 T='results/r19/tol/ur5e_enc2_pgc_py.15';P='results/r19/pot/tol';D=f'{OUT}/tol'
 rows=[]
 main=[('wok play','play:wok'),('wok approaches','app:wok:0'),('spatula play','play:spatula'),('spatula approach','app:spatula:0'),('lever play','play:lever'),('lever approaches','app:lever:0')]
 for lab,key in main:
  k=key.replace(':','_')
  rows.append(dict(scene=lab,key=key,as_designed=_scen(f'{T}/scene_{k}__scen-as_designed.json','as_designed'),dock_stops_target=_scen(f'{T}/scene_{k}__scen-dock_stops.json','dock_stops'),
   dock_rail=_scen(f'{D}/main/scene_{k}__scen-dock_rail.json','dock_rail'),dock_rail_map=_scen(f'{D}/main/scene_{k}__scen-dock_rail_map.json','dock_rail_map')))
 def merged(key,box):
  f=f"{D}/pot/merged_{key.replace(':','_')}__{box}.json"
  if os.path.exists(f):
   m=json.load(open(f));return m['gate']['min_mm'] if m.get('complete') else None
  return _scen(f"{D}/pot/scene_{key.replace(':','_')}__scen-{box}.json",box)
 pot=[('lid play (keyed rack + pot-lift window, #8)','play:lid19','lid_final_1.56_.20_potwin',None),('lid approaches','app:lid19:0','final_full',None),
  ('spider play (rest 1.56 / 0.20, #37)','play:spider19','spider_1.56_.20','spider_1.56_.20'),('spider approaches','app:spider19:0','spider_1.56_.20',None)]
 for lab,key,ref,refad in pot:
  k=key.replace(':','_')
  rows.append(dict(scene=lab,key=key,as_designed=_scen(f'{P}/{refad}/scene_{k}__scen-as_designed.json','as_designed') if refad else None,
   dock_stops_target=_scen(f'{P}/{ref}/scene_{k}__scen-dock_stops.json','dock_stops'),dock_rail=merged(key,'dock_rail'),dock_rail_map=merged(key,'dock_rail_map')))
 ed=[]
 for f in sorted(glob.glob(f'{D}/main/scene_edge_*__scen-dock_rail.json')):
  key=json.load(open(f))['scene'];k=key.replace(':','_')
  ed.append(dict(key=key,as_designed=_scen(f'{T}/scene_{k}__scen-as_designed.json','as_designed'),dock_stops_target=_scen(f'{T}/scene_{k}__scen-dock_stops.json','dock_stops'),
   dock_rail=_scen(f,'dock_rail'),dock_rail_map=_scen(f.replace('dock_rail.json','dock_rail_map.json'),'dock_rail_map')))
 num=lambda v:v if isinstance(v,(int,float)) else 1e9
 emin={c:min((e[c] for e in ed),key=num,default=None) for c in ('as_designed','dock_stops_target','dock_rail','dock_rail_map')}
 tr=json.load(open(f'{OUT}/screen_travel.json'));ar=json.load(open(f'{OUT}/screen_dock.json'))['summary'];B=json.load(open(f'{OUT}/budget.json'));bom_=json.load(open(f'{OUT}/bom.json'))
 out=dict(replays=rows,edges=ed,edges_min=emin,budget=B['boxes'],target=B['target'],load_lean=B['load_lean'],
  travel=dict(pin_up=tr['pin_up']['min_by_category'],pin_up_ok=tr['pin_up']['clearance_ok'],pin_down=tr['pin_down']['min_by_category'],pin_down_ok=tr['pin_down']['clearance_ok'],ends=tr['pin_up']['end_buffers_mm'],design=tr['design']),
  arm_screen={k:ar[k] for k in ('paths','states','errors','hit_paths','worst','by_kind')},bom_total_cny=bom_['total_cny'])
 json.dump(out,open(f'{OUT}/summary.json','w'),indent=1)
 f=lambda v:'-' if v is None else (v if isinstance(v,str) else f'{v:+.2f}')
 print('| Path | As designed | Target box (dock_stops) | dock_rail (tier 1) | dock_rail_map (tier 2) |')
 print('|---|---|---|---|---|')
 for r in rows:print(f"| {r['scene']} | {f(r['as_designed'])} | {f(r['dock_stops_target'])} | {f(r['dock_rail'])} | {f(r['dock_rail_map'])} |")
 print(f"| 22 hub edges (min) | {f(emin['as_designed'])} | {f(emin['dock_stops_target'])} | {f(emin['dock_rail'])} | {f(emin['dock_rail_map'])} |")
 for e in ed:
  if num(e['dock_rail'])<10:print('   edge',e['key'],f(e['as_designed']),f(e['dock_stops_target']),f(e['dock_rail']),f(e['dock_rail_map']))
if __name__=='__main__' and PART=='report':report()
