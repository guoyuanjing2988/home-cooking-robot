"""R19 #39 dock design re-run on the adopted m2 mount (#42), both arms. New file; r19dock_budget.py / kitchen19dock.py
are imported and not changed; no r19*_m2* / r19m2* file is touched. Writes only to results/r19/dock/m2/<arm>/.

The inputs are a MANIFEST (json) per arm: the adopted m2 files (R19_MOUNT.md section 4, R19_M2FIX.md, R19_M2JOIN.md).
DEFAULT below is the state of 2026-10-14; the lane (scratchpad/lanes/m2_dock.sh) writes its own manifests from the
paths at its top, so a changed file is edited in one place there.
python r19dock_m2.py manifest ARM=<arm> OUT=<json> [wok=.. lever=.. prep.carrot=.. hubdir=.. stir=.. ...]   (overrides)
python r19dock_m2.py stations MANIFEST=<json>     the m2 station list (kitchen19dock.STATIONS for that arm)
python r19dock_m2.py lean MANIFEST=<json> [K_TYRE= K_TRUCK= K_CASTOR= TAG=]   load lean along the m2 paths
python r19dock_m2.py budget MANIFEST=<json>       r19dock_budget.budget() on that lean -> the arm's budget boxes
python r19dock_m2.py report MANIFEST=<json>       summary.json + the tables
Station rule (R19_DOCK.md section 10): one V-groove per action endpoint of the m2 hub graph and per anchor where the cart
dwells for a seat / closed chain / forceful or static work (lever play, press, wok pick and set-down, fold, lid lift-off,
lid into the rack, spider pick / rest, stgwok, stir), plus parking. Values within 0.5 mm merge. Two grooves closer than
MIN_SPACING share one twin-V insert (machined at their exact spacing; the 10 mm V mouth leaves a land >= 2 mm down to
12 mm spacing). Transit hubs get a groove only if it is >= MIN_SPACING from every other one. A seat during which the
cart moves (more than 0.5 mm) is marked pin=False: it is a scale-only station (the pin would block the motion)."""
import sys,os,json,glob,math
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
PART=next((a for a in sys.argv[1:] if '=' not in a),KV.get('PART','stations'))
def argv_from_manifest(kv=KV):
 """put the manifest's ARM= / PY= into sys.argv (arms.current() and r19tol_core read them there at import)."""
 if 'MANIFEST' in kv:
  m=json.load(open(kv['MANIFEST']))
  for k,v in (('ARM',m['arm']),('PY',m['py'])):
   if k not in kv:sys.argv.append(f'{k}={v}');kv[k]=v
argv_from_manifest()
OUT_ROOT='results/r19/dock/m2'
MIN_SPACING=.035   # [D] 30 mm insert + 5 mm
PARK=2.40
M_='results/r19/mount';S_='results/r19/stir';H_='results/r19/fr5'
def _f(b,a):return f'{M_}/{b}_{a}.json'
DEFAULT={
 'ur5e_enc2_pgc_m2':dict(chains=dict(wok='chain_wok_s-1_rt',wok_plate2='chain_wok_s-1_rtplate2',lever='chain_lever_s+1_mnt',lid='chain_lid_s-1_rt',spider='chain_spider_s+1_mnt',spatula='chain_spatula_s-1_rt'),
  prep=dict(carrot='chain_carrot_mnt2t8',press='chain_press_rt',tomato='chain_tomato_rt',ctray='chain_ctray_rt',tubfill='chain_tubfill_rt',soak='chain_soak_mnt',stgwok='chain_stgwok_rt',fold='chain_fold_rt',unfold='chain_unfold_rt',
   basket='chain_basket_fix',tubempty='chain_tubempty_fix',ct2s='chain_ct2s_fixs2',bascarrot='chain_bascarrot_full')),
 'fr5_j6_pgc_m2':dict(chains=dict(wok='chain_wok_s-1_rt',wok_plate2='chain_wok_s-1_rtplate2',lever='chain_lever_s+1_mnt',lid='chain_lid_s-1_rt',spider='chain_spider_s+1_rt',spatula='chain_spatula_s-1_mnt'),
  prep=dict(carrot='chain_carrot_mnt5v3',press='chain_press_rt',ctray='chain_ctray_rt',soak='chain_soak_rt',tubempty='chain_tubempty_rt',tubfill='chain_tubfill_rt',fold='chain_fold_rt',unfold='chain_unfold_rt',bascarrot='chain_bascarrot_mnt',
   basket='chain_basket_fix',ct2s='chain_ct2s_fix',tomato='chain_tomato_fix'))}
def default_manifest(arm):
 d=DEFAULT[arm]
 return dict(arm=arm,py='.15',pot=dict(RACK='keyed',SPX='1.56',SPY='.20'),hubdir=f'{H_}/hub_py.15_{arm}',
  stir=f'{S_}/lib_stir_cycle_{arm}_short01_u06_j8000.json',stir_base=f'{S_}/lib_stir_cycle_{arm}.json',stirjoin=f'{S_}/lib_stir_join_{arm}.json',
  chains={k:_f(b,arm) for k,b in d['chains'].items()},prep={k:_f(b,arm) for k,b in d['prep'].items()},park=PARK)
def manifest():
 if 'MANIFEST' in KV:return json.load(open(KV['MANIFEST']))
 return default_manifest(KV.get('ARM','ur5e_enc2_pgc_m2'))
def outdir(M):
 d=f"{OUT_ROOT}/{M['arm']}";os.makedirs(d,exist_ok=True);return d
def J(f):return json.load(open(f,encoding='utf-8'))
# ---------------------------------------------------------------- manifest from argv
def write_manifest():
 M=default_manifest(KV['ARM'])
 if any(k.startswith('prep.') for k in KV):M['prep']={}   # an explicit prep list (the lane's) replaces the default one
 for k,v in KV.items():
  if k in ('ARM','OUT','PART'):continue
  if k.startswith('prep.'):M['prep'][k[5:]]=v
  elif k in M['chains']:M['chains'][k]=v
  elif k.startswith('drop.prep.'):M['prep'].pop(k[10:],None)
  else:M[k]=v
 miss=[f for f in list(M['chains'].values())+list(M['prep'].values())+[M['stir'],M['stirjoin']] if not os.path.exists(f)]
 if miss:raise SystemExit(f'missing files: {miss}')
 bad=[f for f in list(M['chains'].values())+list(M['prep'].values()) if not J(f).get('ok')]
 if bad:raise SystemExit(f'files not ok: {bad}')
 os.makedirs(os.path.dirname(KV['OUT']) or '.',exist_ok=True);json.dump(M,open(KV['OUT'],'w'),indent=1);print(KV['OUT'],json.dumps(M)[:400])
# ---------------------------------------------------------------- stations
def stations():
 M=manifest();out=outdir(M);g=J(f"{M['hubdir']}/graph.json");cand=[]   # (name, x, kind, pin, note)
 for n,v in g['nodes'].items():
  x=float(v['cart']);kind='work' if v.get('kind')=='endpoint' else 'hub'
  cand.append(('LEV' if n in ('LEV_C','LEV_O') else n,x,kind,True,f"hub graph {v.get('kind')} {n}"))
 c=M['chains'];p=M['prep']
 def play(f):return np.array(J(f)['play'],float)
 Q=play(c['lever']);cand.append(('LEVER',float(Q[0,0]),'work',True,'lever play (closed chain), cart fixed'))
 Q=play(c['wok']);cand.append(('WOK_SET',float(Q[-1,0]),'work',True,'wok set-down into the cooker (last state)'))
 Q=play(c['lid']);dw=int(np.argmax(abs(Q[::-1,0]-Q[-1,0])>5e-5)) or len(Q)   # trailing states with the cart parked (within 0.05 mm)
 cand.append(('LID_RACK_SEAT',float(Q[-1,0]),'work',dw>=5,f"lid into the rack: the cart is parked for the last {dw} states (the straight drop)"))
 for k,lab in (('press','PRESS'),('stgwok','STGWOK'),('fold','FOLD')):
  if k in p:Q=play(p[k]);cand.append((lab,float(Q[0,0]),'work',bool(np.ptp(Q[:,0])<5e-4),f'{k} set: cart range {1e3*float(np.ptp(Q[:,0])):.1f} mm'))
 L=J(M['stir']);Q=np.array(L['states']['q'],float);cand.append(('STIR',float(Q[0,0]),'work',bool(np.ptp(Q[:,0])<5e-4),'stir cycle (parked)'))
 cand.append(('PARK',float(M.get('park',PARK)),'park',True,'parking / charging'))
 # merge values within 0.5 mm (work names win over hub names)
 cand.sort(key=lambda t:(t[1],t[2]!='work'));groups=[]
 for t in cand:
  if groups and abs(t[1]-groups[-1][0][1])<=5e-4:groups[-1].append(t)
  else:groups.append([t])
 st=[]
 for gr in groups:
  w=[t for t in gr if t[2] in ('work','park')] or gr;h=w[0]
  st.append(dict(name=h[0],x=round(h[1],4),kind=h[2],pin=all(t[3] for t in w),aliases=sorted({t[0] for t in gr}-{h[0]}),notes=[t[4] for t in gr]))
 # transit hubs: keep only if >= MIN_SPACING from every work / park groove
 work=[s for s in st if s['kind']!='hub']
 for s in st:
  if s['kind']=='hub':s['groove']=all(abs(s['x']-o['x'])>=MIN_SPACING for o in work)
  else:s['groove']=s['pin']
 grooves=sorted([s for s in st if s['groove']],key=lambda s:s['x'])
 # inserts: grooves closer than MIN_SPACING share one twin-V insert
 ins=[];
 for s in grooves:
  if ins and s['x']-ins[-1][-1]['x']<MIN_SPACING:ins[-1].append(s)
  else:ins.append([s])
 for k,i in enumerate(ins):
  for s in i:s['insert']=k;s['insert_kind']='twin-V' if len(i)>1 else 'single V'
 res=dict(arm=M['arm'],min_spacing_m=MIN_SPACING,stations={s['name']:s['x'] for s in grooves},detail=st,inserts=[[s['name'] for s in i] for i in ins],
  scale_only=[s['name'] for s in st if not s['groove']],rule=__doc__.split('Station rule')[1].strip())
 json.dump(res,open(f'{out}/stations.json','w'),indent=1)
 print(M['arm'],'grooves',len(grooves),'inserts',len(ins))
 for s in st:print(f"  {s['name']:14s} x {s['x']:+.4f} {s['kind']:5s} groove={s['groove']!s:5s} pin={s['pin']!s:5s} insert={s.get('insert','-')} {s.get('insert_kind','')} aliases={s['aliases']} | {'; '.join(s['notes'])}")
 return res
def load_stations(M):
 f=f"{OUT_ROOT}/{M['arm']}/stations.json"
 return J(f)['stations'] if os.path.exists(f) else stations()['stations']
# ---------------------------------------------------------------- load lean (as r19dock_budget.lean, on the manifest's paths)
PAY=dict(wok=1.8+1.15,wok_plate2=1.8+1.15,spatula=.3,lever=0.,lid=.8,spider=.45+.3)   # kg at the TCP (r19dock_budget.PATHS values)
def lean():
 import mujoco,chain,r19dock_budget as B
 import r19tol_core as C
 from scene import build
 from checker import Checker
 M=manifest();out=outdir(M)
 cfg=chain.chain_cfg('SD',**C.BASE);tree,meta=build(cfg,None);ch=Checker(tree,meta);m,d=ch.m,ch.d
 cart=m.body('rail_structure').id;sid=m.site('R_prep').id
 def sub(b):
  while b and b!=cart:b=m.body_parentid[b]
  return b==cart
 mov=[b for b in range(1,m.nbody) if b!=cart and sub(b)];marm=float(m.body_mass[mov].sum())
 sets=[(k,f,PAY[k]) for k,f in M['chains'].items()]+[('stir',M['stir'],.3)]+[('prep:'+k,f,1.0) for k,f in M['prep'].items()]
 rows={};allc=[]
 for name,f,pay in sets:
  r=J(f);Q=r.get('play') or (r.get('states') or {}).get('q')
  Q=C.unwrap(Q);cs=[]
  for q in Q:
   d.qpos[:]=q;mujoco.mj_kinematics(m,d);x0=d.xpos[cart];mm=m.body_mass[mov];P=d.xipos[mov]-x0
   mc=(mm[:,None]*P).sum(0)+pay*(d.site_xpos[sid]-x0);Mt=marm+pay;cs.append(np.r_[mc/Mt,Mt])
  cs=np.array(cs);rows[name]=cs;allc.append(cs)
 res=dict(method='r19dock_budget.lean on the m2 manifest paths',manifest=M,k=dict(K_TYRE=B.K_TYRE,K_TRUCK=B.K_TRUCK,K_CASTOR=B.K_CASTOR),moving_mass_kg=round(marm,2),cart=B.CART_BOM,configs={})
 A=np.vstack(allc)
 for kind in ('rail','castors'):
  sup=B.supports(kind)
  def state(c):
   Wm=c[3]*B.G;Wc=B.CART_BOM['m']*B.G;W=Wm+Wc;cx=(Wm*c[0]+Wc*B.CART_BOM['c'][0])/W;cy=(Wm*c[1]+Wc*B.CART_BOM['c'][1])/W
   u,R=B.solve(sup,W,cx,cy);return dict(tx=float(np.degrees(u[1])),ty=float(np.degrees(-u[2])),zb=float((u[0]+u[1]*.08)*1e3),R=R,cy=cy)
  S=[state(c) for c in A];tx=np.array([s['tx'] for s in S]);ty=np.array([s['ty'] for s in S]);zb=np.array([s['zb'] for s in S])
  ref=float(np.median(tx));per={};i0=0
  for name,cs in rows.items():
   n=len(cs);per[name]=dict(states=n,tilt_x_deg=[round(float(tx[i0:i0+n].min()),4),round(float(tx[i0:i0+n].max()),4)],min_support_N=round(min(float(s['R'].min()) for s in S[i0:i0+n]),1));i0+=n
  res['configs'][kind]=dict(supports=[list(s) for s in sup],reference_median=dict(tilt_x=ref,tilt_y=float(np.median(ty)),z=float(np.median(zb))),
   tilt_x_halfrange_deg=round(float(np.ptp(tx)/2),4),tilt_x_max_dev_from_median_deg=round(float(np.max(abs(tx-ref))),4),tilt_y_halfrange_deg=round(float(np.ptp(ty)/2),4),
   z_base_halfrange_mm=round(float(np.ptp(zb)/2),3),min_front_support_N=round(float(min(s['R'][:2].min() for s in S)),1),min_front_pair_total_N=round(float(min(s['R'][:2].sum() for s in S)),1),
   min_rear_support_N=round(float(min(s['R'][2:].min() for s in S)),1),cop_y_range_m=[round(min(s['cy'] for s in S),4),round(max(s['cy'] for s in S),4)],per_path=per)
  print(M['arm'],kind,json.dumps({k:v for k,v in res['configs'][kind].items() if k not in ('per_path','supports')}),flush=True)
 tag=KV.get('TAG','');fn=f'{out}/lean{("_"+tag) if tag else ""}.json';json.dump(res,open(fn,'w'),indent=1,default=float);print(fn,'states',len(A))
def budget():
 import r19dock_budget as B
 M=manifest();B.OUT=outdir(M);B.budget()
# ---------------------------------------------------------------- report
def report():
 M=manifest();out=outdir(M);arm=M['arm']
 def scen(f,box):
  try:s=J(f)['scenarios'].get(box)
  except Exception:return None
  return None if s is None else s['gate']['min_mm']
 def merged(key,box):
  f=f"{out}/tol/pot/merged_{key.replace(':','_')}__{box}.json"
  if os.path.exists(f):
   m=J(f);return m['gate']['min_mm'] if m.get('complete') else None
  return scen(f"{out}/tol/pot/scene_{key.replace(':','_')}__scen-{box}.json",box)
 boxes=('dock_stops','dock_rail','dock_rail_map');rows=[]
 for key in ('play:wok','app:wok:0','app:wok:1','play:spatula','app:spatula:0','play:lever','app:lever:0','app:lever:1'):
  rows.append(dict(key=key,**{b:scen(f"{out}/tol/main/scene_{key.replace(':','_')}__scen-{b}.json",b) for b in boxes}))
 for key in ('play:lid19','app:lid19:0','app:lid19:1','play:spider19','app:spider19:0','app:spider19:1'):
  rows.append(dict(key=key,**{b:merged(key,b) for b in boxes}))
 ed=[]
 for f in sorted(glob.glob(f'{out}/tol/main/scene_edge_*__scen-dock_rail.json')):
  key=J(f)['scene'];ed.append(dict(key=key,**{b:scen(f.replace('scen-dock_rail.json',f'scen-{b}.json'),b) for b in boxes}))
 num=lambda v:v if isinstance(v,(int,float)) else 1e9
 emin={b:min((e[b] for e in ed),key=num,default=None) for b in boxes}
 res=dict(arm=arm,replays=rows,edges=ed,edges_min=emin)
 for k,f in (('stations','stations.json'),('budget','budget.json'),('travel','screen_travel.json'),('arm_screen','screen_dock.json'),('lean','lean.json')):
  try:
   v=J(f'{out}/{f}')
   res[k]=v['summary'] if k=='arm_screen' else {kk:v[kk] for kk in ('stations','inserts','scale_only')} if k=='stations' else v.get('boxes',v) if k=='budget' else \
    {p:dict(min=v[p]['min_by_category'],ok=v[p]['clearance_ok']) for p in ('pin_up','pin_down')} if k=='travel' else {c:{kk:v['configs'][c][kk] for kk in ('tilt_x_halfrange_deg','tilt_x_max_dev_from_median_deg','min_front_support_N','min_front_pair_total_N')} for c in v['configs']}
  except Exception as e:res[k]=f'missing ({e})'
 json.dump(res,open(f'{out}/summary.json','w'),indent=1,default=float)
 fm=lambda v:'-' if v is None else (v if isinstance(v,str) else f'{v:+.2f}')
 print(f'### {arm}\n| Path | target box (dock_stops) | dock_rail (tier 1) | dock_rail_map (tier 2) |\n|---|---|---|---|')
 for r in rows:print(f"| {r['key']} | {fm(r['dock_stops'])} | {fm(r['dock_rail'])} | {fm(r['dock_rail_map'])} |")
 print(f"| {len(ed)} hub edges (min) | {fm(emin['dock_stops'])} | {fm(emin['dock_rail'])} | {fm(emin['dock_rail_map'])} |")
 for k in ('stations','budget','travel','lean'):print(k,json.dumps(res.get(k),default=float)[:700])
 a=res.get('arm_screen');print('arm_screen',json.dumps({k:a[k] for k in ('paths','states','errors','hit_paths','worst','by_kind')} if isinstance(a,dict) else a,default=float))
if __name__=='__main__':
 {'manifest':write_manifest,'stations':stations,'lean':lean,'budget':budget,'report':report}[PART]()
