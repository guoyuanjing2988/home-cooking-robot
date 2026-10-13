"""R19 tolerance (#13): merge the r19tol_replay.py results, apply the error budget, write the tables.

python r19tol_report.py [ARM=<id>]  -> results/r19/tol<tag>/summary.json + tables.md (pasted into R19_TOLERANCE.md)
Per action (its stored play + its grasp approaches) and per hub edge:
  - the exact nominal minimum (gate / contact) vs the reserve the checker reported;
  - the measured tolerance per perturbation axis (worst sign), binding segment and pair;
  - the error budget (BUDGET below; S = sourced, E = estimated, M = measured in the sim) per scenario, and the
    utilization U = sum e_i / tol_i (worst-case linear) and sqrt(sum (e_i / tol_i)^2) (RSS), against the gate
    tolerance (keeps the 10 / 5 mm planning gaps) and the contact tolerance (keeps any clearance in the model).
    U <= 1 means the budget fits. Linear superposition per pair: tol_i is the minimum over all states and pairs,
    so U_lin <= 1 is sufficient (to first order); a single pair involves at most one fixture group, so only the
    worst fixture term enters.
  - the worst corner of each cart-only budget box (r19tol_replay.py PARTS=scen-*), measured."""
import sys,os,json,glob,math,collections
sys.path.insert(0,'.')
import r19tol_core as C
CAP=dict(mm=15.,deg=1.5)   # search caps of r19tol_replay.py: 'no violation up to' -> the cap is used (conservative)
SCEN=['as_designed','R09_requirement','dock_stops','touch_off']
# ---- the error budget: half-ranges (mm or deg) per scenario; axis = which measured tolerance it uses
# 'any' = a translation in an unknown direction (worst of x, y, z); 'fixture' / 'grasp*' handled separately
BUDGET=[
 # name, axis, unit, as_designed, R09_requirement, dock_stops, touch_off, label, basis
 ('dock_x','x','mm',2.0,2.0,0.3,0.2,'E','x registration at set start. As designed there is no x datum (mobile.py: the bumper fixes y only): homing at the counter-end stop + encoder counts. Indexed stop / pin per station; touch-off.'),
 ('odometry_x','x','mm',5.0,0.0,1.0,1.0,'E','in-set cart travel up to ~1 m (the wok carry 0.66 m, spatula 1.05 m, hub edges up to 1.15 m): 0.5 % (effective tyre radius not calibrated, slip) / 0.1 % calibrated. Encoder: ZLTECH ZLLG65ASM500 4096 lines (S), resolution 0.03-0.13 mm, not the limit. R09 counts it inside its +-2 mm.'),
 ('dock_y','y','mm',1.5,2.0,0.5,0.3,'E','bumper on the cabinet fronts: door flushness +-1 mm + bumper compression +-0.5 mm; datum rail / stop on the plinth; touch-off.'),
 ('dock_yaw','yaw','deg',0.3,0.2,0.05,0.03,'E','bumper over 0.56 m on fronts that are flush to +-1.5 mm -> +-0.3 deg; V-block + flat; touch-off. Pivot: the arm J1 axis.'),
 ('floor_z','z','mm',1.0,1.0,0.5,0.3,'E','floor height under the 4 contacts + tyre radius (R09 requirement +-1 mm height).'),
 ('floor_tilt_x','tilt_x','deg',0.15,0.0,0.15,0.03,'E','tile floor unevenness ~0.5 mm across the 0.21 m caster-to-drive-wheel base (flatness spec of tiled floors is commonly 2 mm / 2 m; not verified in the standard text). Toward the counter = tilt_x -. Touch-off / inclinometer measures and compensates it.'),
 ('floor_tilt_y','tilt_y','deg',0.07,0.0,0.07,0.03,'E','as above across the 0.44 m track.'),
 ('load_tilt_x','tilt_x','deg',0.25,0.0,0.10,0.10,'E','tyre / caster / bumper / cabinet-front compliance under the arm moment (~60 N m with the wok at reach, #13): lean toward the counter. Posture-dependent, so a set-start touch-off does not remove it; stiffer bumper datum + measured pre-compensation. Mast bending: 0.003 deg (120x120x4 steel tube est.), negligible.'),
 ('mount_xy','any','mm',0.5,0.5,0.05,0.05,'E','arm base on the mast plate: four M8 bolts (S, UR manual) in clearance holes; dowel-pinned + calibrated plate.'),
 ('mount_yaw','yaw','deg',0.2,0.2,0.02,0.02,'E','base rotation in the bolt clearance; pinned.'),
 ('arm_accuracy','any','mm',2.0,0.3,0.3,0.3,'S/E','UR5e absolute accuracy with the sim\'s nominal kinematics: >= 2 mm (S, ROS answers 324883); with the robot\'s own factory calibration exported into the checker: ~0.3 mm (E).'),
 ('arm_repeatability','any','mm',0.03,0.03,0.03,0.03,'S','UR5e pose repeatability +-0.03 mm, ISO 9283 (S, datasheet).'),
 ('tracking_sync','any','mm',1.5,0.5,0.5,0.5,'E','servoj path following + cart / arm clock skew (4-10 ms x 0.25 m/s); #6. Hardware-synchronized cart axis / slower near tight spots.'),
 ('thermal','any','mm',0.3,0.3,0.3,0.3,'E','aluminium arm 0.85 m x 23e-6/K x 15 K = 0.3 mm; steel cart 0.2 mm; hot wok rim +0.4 mm radius.'),
 ('grasp_offset','grasp_t','mm',1.0,0.5,0.5,0.5,'E','held part in the jaws: keyed block, form-fit pads (R11) +-0.5 mm; +-1 mm with wear / debris.'),
 ('grasp_turn','grasp_rot','deg',2.0,1.0,1.0,1.0,'E','turn about the jaw axis under the moment (wok 6.47 of 7 N m PGC limit).')]
FIXTURE={   # half-range (mm, any direction) per fixture group: as_designed, R09_requirement, dock_stops, touch_off; label E
 'cooker':(5,1,1,.5),'drum':(2,1,1,.5),'faucet_body':(2,.5,.5,.3),'lever_clip':(2,.5,.5,.3),'plate1':(10,2,2,2),'plate2':(10,2,2,2),
 'spatula_pad':(3,1,1,.5),'lid_rack':(2,.5,.5,.3),'pot':(3,1,1,.5),'spider_rest':(3,1,1,.5),'sink':(2,.5,.5,.3),'raw':(15,15,15,15),
 'bowls':(5,2,2,2),'cups':(3,1,1,1),'upper':(3,1,1,.5),'counter':(2,.5,.5,.3),'wall':(2,.5,.5,.3)}
FIXTURE_BASIS=('cooker: freestanding induction cooker (moved for cleaning) vs a counter-fixed locator; lid rack / spider rest / spatula pad: '
 'screwed to the counter, positions from a tape survey vs robot touch-off; faucet body / sink / upper cabinets / hood / counter: kitchen survey '
 '(tape +-2-3 mm vs touch-off +-0.3-0.5 mm); lever clip: hand-fitted clip vs keyed clip; plates: by hand vs a guarded stand; raw food '
 'on the prep tray: not a fixture (+-15 mm whatever the registration); all E.')
def load():
 R=collections.defaultdict(dict)
 for f in glob.glob(f'{C.OUT}/scene_*__*.json'):
  r=C.J(f);R[r['scene']][r['part']]=r
 return R
def merged(R,sc):
 out=dict(directions=[],validation=[],grid=[],scenarios={},nominal=None,checker_reported=None,groups={},states=None)
 for p,r in R[sc].items():
  out['directions']+=r.get('directions',[]);out['validation']+=r.get('validation',[]);out['grid']+=r.get('grid',[])
  out['scenarios'].update(r.get('scenarios',{}));out['states']=r['states']
  if r.get('nominal'):out['nominal']=r['nominal']
  if r.get('checker_reported'):out['checker_reported']=r['checker_reported']
  for g,v in r.get('groups',{}).items():
   if v.get('searched') or g not in out['groups']:out['groups'][g]=v
 return out
def lab(b):
 if not b:return ''
 l=b.get('label') or ''
 if not l:l='start (kf 0)' if b.get('src_index',0)<1 else ''
 return l
def tolmap(M):
 """(kind, axis, group) -> worst-sign tolerance for gate / contact with its binding."""
 T={}
 for d in M['directions']:
  k=(d['kind'],d['axis'],d['group'])
  for meas in ('gate','contact'):
   t=d[meas];v=t['tol'] if t.get('bounded') else max(t['tol'],CAP[d['unit']])
   cur=T.setdefault(k,{}).get(meas)
   if cur is None or v<cur['tol']:T[k][meas]=dict(tol=v,bounded=bool(t.get('bounded')),sign=d['sign'],unit=d['unit'],pair=(t.get('binding') or {}).get('pair'),label=lab(t.get('binding')))
 return T
def combine(Ms):
 """Union of several scenes (an action's play + approaches): min per key."""
 T={}
 for name,M in Ms:
  for k,v in tolmap(M).items():
   for meas,x in v.items():
    cur=T.setdefault(k,{}).get(meas)
    if cur is None or x['tol']<cur['tol']:T[k][meas]=dict(x,scene=name)
 return T
def axis_tol(T,ax,meas):
 if ax=='any':return min((axis_tol(T,a,meas) for a in ('x','y','z')),key=lambda x:x['tol'])
 if ax=='grasp_t':
  c=[T[k][meas] for k in T if k[0]=='grasp' and k[1] in ('x','y','z')]
  return min(c,key=lambda x:x['tol']) if c else None
 if ax=='grasp_rot':
  c=[T[k][meas] for k in T if k[0]=='grasp' and k[1]=='rot'];return c[0] if c else None
 return T[('cart',ax,None)][meas]
def utilization(T,si,meas,groups):
 terms=[]
 for name,ax,unit,*vals,lbl,basis in BUDGET:
  e=vals[si]
  if e<=0:continue
  t=axis_tol(T,ax,meas)
  if t is None:continue
  terms.append((name,e,t['tol'],e/t['tol']))
 fx=[]
 for g in groups:
  c=[T[k][meas] for k in T if k[0]=='fix' and k[2]==g]
  if not c:continue
  t=min(c,key=lambda x:x['tol']);e=FIXTURE.get(g,(2,1,1,.5))[si];fx.append((f'fixture:{g}',e,t['tol'],e/t['tol']))
 if fx:terms.append(max(fx,key=lambda x:x[3]))
 lin=sum(x[3] for x in terms);rss=math.sqrt(sum(x[3]**2 for x in terms))
 top=sorted(terms,key=lambda x:-x[3])[:3]
 return dict(lin=round(lin,2),rss=round(rss,2),top=[(n,e,round(t,3),round(u,2)) for n,e,t,u in top],fixture_term=max(fx,key=lambda x:x[3])[0] if fx else None)
ACTIONS=['wok','spatula','lever','lid','spider']
def main():
 R=load();out=dict(arm=C.ARM,actions={},edges={},budget=dict(items=[dict(name=b[0],axis=b[1],unit=b[2],**dict(zip(SCEN,b[3:7])),label=b[7],basis=b[8]) for b in BUDGET],fixture=FIXTURE,fixture_basis=FIXTURE_BASIS,scenarios=SCEN))
 units={('cart',a):('mm' if a in ('x','y','z') else 'deg') for a in C.CART_AXES}
 lines=[]
 def block(name,scenes):
  Ms=[(s,merged(R,s)) for s in scenes if s in R]
  if not Ms:return None
  T=combine(Ms);groups=sorted({g for _,M in Ms for g,v in M['groups'].items() if v.get('searched')})
  nom=[(s,M['nominal'],M['checker_reported']) for s,M in Ms if M['nominal']]
  rec=dict(scenes=[s for s,_ in Ms],nominal={s:dict(exact_min_gate_mm=n['min_gate_mm'],exact_min_contact_mm=n['min_contact_mm'],pair=n['gate_pair'],label=n['gate_label'],
   checker_reported_mm=(c or {}).get('min_reserve_mm'),checker_reported_exact_there_mm=(c or {}).get('exact_gate_there_mm')) for s,n,c in nom},
   tolerance={f"{k[0]}:{k[1]}"+(f":{k[2]}" if k[2] else ''):v for k,v in sorted(T.items(),key=lambda kv:str(kv[0]))},
   utilization={sc:{meas:utilization(T,i,meas,groups) for meas in ('gate','contact')} for i,sc in enumerate(SCEN)},
   corners={s:M['scenarios'] for s,M in Ms if M['scenarios']},
   validation=[v for _,M in Ms for v in M['validation']])
  return rec
 for a in ACTIONS:
  r=C.J(C.tagged(C.CHAINS[a]['file']));sc=[f'play:{a}']+[f'app:{a}:{k}' for k,q in enumerate(r['approach_qs']) if q]
  out['actions'][a]=block(a,sc)
 for s in sorted(k for k in R if k.startswith('edge:')):out['edges'][s[5:]]=block(s,[s])
 json.dump(out,open(f'{C.OUT}/summary.json','w'),indent=1,default=float)
 # ---------------- tables
 L=[]
 L.append('### Nominal: exact minimum vs the reserve the checker reported\n\n| Scene | States | Exact gate reserve (mm) | Exact gap (mm) | Binding pair, where | Checker-reported reserve (mm) |\n|---|---|---|---|---|---|')
 for grp in ('actions','edges'):
  for a,rec in out[grp].items():
   if not rec:continue
   for s,n in rec['nominal'].items():
    st=merged(R,s)['states']
    L.append(f"| {s} | {st} | {n['exact_min_gate_mm']:.2f}{' (>=)' if n['pair'] is None else ''} | {n['exact_min_contact_mm']:.2f} | {' / '.join(n['pair']) if n['pair'] else '-'}, {n['label'] or 'start'} | {n['checker_reported_mm']} |")
 axes=['x','y','z','yaw','tilt_x','tilt_y']
 L.append('\n### Cart pose tolerance per axis (worst sign): gate / contact; binding pair at the gate\n\n| Action / edge | '+' | '.join(f"{a} ({'mm' if a in 'xyz' else 'deg'})" for a in axes)+' | First to bind (gate) |\n|---|'+'---|'*len(axes)+'---|')
 for grp in ('actions','edges'):
  for a,rec in out[grp].items():
   if not rec:continue
   T=rec['tolerance'];cells=[]
   for ax in axes:
    g=T[f'cart:{ax}']['gate'];c=T[f'cart:{ax}']['contact']
    f=lambda x:(f"{x['tol']:.3g}{'-' if x['sign']<0 else '+'}" if x['bounded'] else f">{x['tol']:.3g}")
    cells.append(f"{f(g)} / {f(c)}")
   first=min(axes,key=lambda ax:T[f'cart:{ax}']['gate']['tol']/(1. if ax in 'xyz' else 10.))   # rank: 1 deg ~ 10 mm at ~0.6 m lever
   b=T[f'cart:{first}']['gate'];L.append(f"| {a} | "+' | '.join(cells)+f" | {first}: {' / '.join(b['pair'] or [])}, {b['label']} ({b.get('scene','')}) |")
 L.append('\n### Fixture and grasp tolerance (worst axis and sign; gate / contact, mm or deg)\n\n| Action | Fixture group: tolerance, binding pair | Grasp offset (tool x/y/z) | Grasp turn about the jaw axis |\n|---|---|---|---|')
 for a,rec in out['actions'].items():
  T=rec['tolerance'];fx=collections.defaultdict(list)
  for k,v in T.items():
   p=k.split(':')
   if p[0]=='fix':fx[p[2]].append(v)
  fs=[]
  for g,vs in fx.items():
   gg=min(vs,key=lambda v:v['gate']['tol']);cc=min(vs,key=lambda v:v['contact']['tol'])
   if gg['gate']['tol']>=CAP['mm']:continue
   fs.append((gg['gate']['tol'],f"{g} {gg['gate']['tol']:.3g} / {cc['contact']['tol']:.3g} ({' / '.join(gg['gate']['pair'] or [])})"))
  gt=[T[k] for k in T if k.startswith('grasp:') and not k.startswith('grasp:rot')];gr=T.get('grasp:rot')
  gts=f"{min(v['gate']['tol'] for v in gt):.3g} / {min(v['contact']['tol'] for v in gt):.3g}" if gt else '-'
  grs=f"{gr['gate']['tol']:.3g} / {gr['contact']['tol']:.3g}" if gr else '-'
  L.append(f"| {a} | {'; '.join(x for _,x in sorted(fs)) or 'none within 15 mm'} | {gts} | {grs} |")
 L.append('\n### Budget utilization U (worst-case linear / RSS); U <= 1 fits. Gate = keeps the 10/5 mm gaps; contact = keeps any clearance\n\n| Action / edge | '+' | '.join(SCEN)+' | Largest terms (as designed, contact) |\n|---|'+'---|'*len(SCEN)+'---|')
 for grp in ('actions','edges'):
  for a,rec in out[grp].items():
   if not rec:continue
   U=rec['utilization'];cells=[f"gate {U[s]['gate']['lin']}/{U[s]['gate']['rss']}, contact {U[s]['contact']['lin']}/{U[s]['contact']['rss']}" for s in SCEN]
   top=', '.join(f"{n} {e}/{t} = {u}" for n,e,t,u in U['as_designed']['contact']['top'])
   L.append(f"| {a} | "+' | '.join(cells)+f" | {top} |")
 L.append('\n### Cart-only budget boxes, worst sign corner replayed (measured): min gate reserve / min gap (mm)\n\n| Action / edge | '+' | '.join(SCEN)+' |\n|---|'+'---|'*len(SCEN))
 for grp in ('actions','edges'):
  for a,rec in out[grp].items():
   if not rec:continue
   cells=[]
   for s in SCEN:
    vals=[(sc_[s]['gate']['min_mm'],sc_[s]['contact']['min_mm'],sn) for sn,sc_ in rec['corners'].items() if s in sc_]
    missing=[x for x in rec['scenes'] if s not in rec['corners'].get(x,{})]
    if not vals:cells.append('not run');continue
    num=lambda v:v if isinstance(v,(int,float)) else float(str(v).lstrip('>='))
    g=min(vals,key=lambda v:num(v[0]));c=min(vals,key=lambda v:num(v[1]))
    cells.append(f"{g[0]} / {c[1]}"+(' (play not run)' if missing else ''))
   L.append(f"| {a} | "+' | '.join(cells)+' |')
 open(f'{C.OUT}/tables.md','w',encoding='utf-8').write('\n'.join(L)+'\n')
 print('\n'.join(L))
if __name__=='__main__':main()
