"""R19 prep step 4 (#38): screen the NEW step-4 parts against every stored path. New file; r19pot_screen.py is imported
for its helpers (stored-path list, <= 4 mm sampling, scene builders) and is not changed; nothing is written outside
results/r19/prep4/.
Same method as r19pot_screen.py: a new part only adds pairs, so each stored state is replayed with the part in the
scene and ONLY the pairs that involve the part are measured, exactly: enclosing-AABB separation, refined by the
checker's own GJK lower bound (distance.Bounds.pair) wherever it is within 30 mm of the gap; gate = distance - the
checker's required gap for that pair (ch.required: 10 mm robot-environment, 5 mm gripper / held-environment, 10 mm
arm vs a CART part; pairs the checker does not check are skipped, as it does). Stored states 2pi-unwrapped,
joint-linear between them, cut to <= 4 mm point bound (r19smooth.sample_poly); hub edges as stored (<= 4 mm).
The current cooking layout (kitchen19pot: RACK=keyed, spider rest at SPX, SPY = 1.56, 0.20) is installed in every
scene, and the adopted spider chain is the re-planned one of R19_POTZONE.md.
MODE=t2l     the T2L cradle + bracket and the parked staging pan (kitchen19p4, CART geoms R_cart_p4_*): they move
             with the cart, so their bounds are recomputed at every state.
MODE=drawer  the slicer drawer (guide plate, rails, stop: p4_drawer_*) with the cranked-handle bowl parked under the
             spout (p4_dbh_*). The R07 potato staging bowl and the plain R11 out bowl are removed by the design; a
             removed obstacle cannot create a hit, so they are left in the replayed scenes.
Paths: the adopted cooking chains (results/r17/chain_*_ur5e_enc2_pgc.json, wok + plate 2 at py.15, lever, lid,
spatula; spider = results/r19/pot/chain_spider_s+1_pot_1.56_.20_ur5e_enc2_pgc.json) + their approaches; the 22 hub
edges (hub_py.15_ur5e_enc2_pgc); the stored stir cycle (results/r19/stir/lib_stir_cycle_<arm>.json, its own scene);
the checked cup chains (union scene, held cup bounded by a 0.20 m sphere about the
TCP as r19pot_screen); the stored prep sets (results/r19/prep/chain_*_{full,r2}_ur5e_enc2_pgc.json + the step-3 smoke
passes) and the step-4 passes (results/r19/prep4/chain_{ct2p_s1,stgwok_m5}_ur5e_enc2_pgc.json), replayed EXACTLY in
their own scenes (held object, stations, union faucet) with their approaches.
python r19prep4_screen.py MODE=t2l|drawer [WORKERS=16] [KINDS=play,app,edge,other,prep] -> results/r19/prep4/screen_<MODE>.json"""
import sys,os,json,time,glob
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a);MODE=KV.get('MODE','t2l')
_argv=sys.argv;sys.argv=[sys.argv[0]];import r19pot_screen as PS;sys.argv=_argv
OUT='results/r19/prep4';POT=dict(RACK='keyed',SPX='1.56',SPY='.20')
SPIDER='results/r19/pot/chain_spider_s+1_pot_1.56_.20_ur5e_enc2_pgc.json'
PREP=sorted(set(glob.glob('results/r19/prep/chain_*_full_ur5e_enc2_pgc.json')+glob.glob('results/r19/prep/chain_*_r2_ur5e_enc2_pgc.json')+
 [f'results/r19/prep/chain_{t}_ur5e_enc2_pgc.json' for t in ('basket_y20p30','tubfill_t15fin','soak_so1','tubempty_ex2','ctray_cq1','bascarrot_bc1')]+
 [f'results/r19/prep4/chain_{t}_ur5e_enc2_pgc.json' for t in ('ct2p_s1','stgwok_m5')]))
def potzone():
 import kitchen19pot;kitchen19pot.install_kv(POT)
def my_parts(tree):
 """add the MODE's new parts to a built tree; returns the name prefixes of the new geoms."""
 import kitchen16 as K,kitchen19p4 as P4
 if MODE=='t2l':P4.add(tree,{'r19p4':dict(t2l=dict(P4.T2L,present=KV.get('EMPTY')!='1'))});pre=('R_cart_p4_',)   # EMPTY=1: the cradle + bracket alone (pan not parked)
 else:
  P4.add(tree,{'r19p4':dict(drawer=dict(xo=-1.49))});B=P4.dbh(.17,.195,.237,0);R,p=P4.drawer_seat()
  K._add(tree.find('worldbody'),'',K.OBJ[B]['parts'],R,p,rgba='.55 .75 .55 1');pre=('p4_drawer_','p4_dbh_')
 P4.mesh(tree);return pre
class Meas:
 """exact min gate over the pairs (moving robot / held geom) x (new geom), new geoms possibly moving with the cart."""
 def __init__(s,ch,prefix,held_sphere=False):
  import mujoco
  s.ch=ch;m=ch.m;s.m=m;s.mj=mujoco;nm=ch.gnames;s.new=[g for g in range(m.ngeom) if nm[g].startswith(prefix)];w={int(ch.weld[g]) for g in s.new}
  mov=[g for g in range(m.ngeom) if (ch.robot[g] or ch.held[g]) and g not in s.new and int(ch.weld[g]) not in w and m.geom_type[g]!=0];pr=[]
  for a in mov:
   for b in s.new:
    q=ch.required(ch,a,b)
    if q is not None:pr.append((a,b,q[0],q[1]))
  s.A=np.array([p[0] for p in pr],int);s.B=np.array([p[1] for p in pr],int);s.N=np.array([p[2] for p in pr]);s.cat=[p[3] for p in pr]
  s.geoms=sorted(set(s.A.tolist())|set(s.new));s.sid=m.site('R_prep').id;s.held_sphere=held_sphere
 def __call__(s,q):
  m,d=s.m,s.ch.d;d.qpos[:]=q;s.mj.mj_kinematics(m,d);lo=np.zeros((m.ngeom,3));hi=np.zeros((m.ngeom,3))
  for g in s.geoms:
   R=d.geom_xmat[g].reshape(3,3);c=d.geom_xpos[g]+R@m.geom_aabb[g,:3];e=np.abs(R)@m.geom_aabb[g,3:];lo[g]=c-e;hi[g]=c+e
  best=(1e9,None,1e9,None)
  if len(s.A):
   dl=np.maximum(np.maximum(lo[s.A]-hi[s.B],lo[s.B]-hi[s.A]),0.);ab=np.sqrt((dl*dl).sum(1));key=ab-s.N
   for i in np.argsort(key):
    if key[i]>=min(best[0],PS.CAP):break
    dist=max(ab[i],s.ch.bounds.pair(int(s.A[i]),int(s.B[i]))['lower_m']);v=dist-s.N[i]
    if v<best[0]:best=(float(v),[s.ch.gnames[s.A[i]],s.ch.gnames[s.B[i]]],float(dist),s.cat[i])
   if best[1] is None:i=int(np.argmin(key));best=(float(key[i]),[s.ch.gnames[s.A[i]],s.ch.gnames[s.B[i]]],float(ab[i]),s.cat[i]+' (AABB lower bound, >= 30 mm)')
  if s.held_sphere:
   p=d.site_xpos[s.sid]
   for g in s.new:
    dd=float(np.linalg.norm(np.maximum(np.maximum(lo[g]-p,p-hi[g]),0.)))-PS.HELD_R-.005
    if dd<best[0]:best=(dd,['held object within %.2f m of the TCP'%PS.HELD_R,s.ch.gnames[g]],dd+.005,'held sphere')
  return best
def cook_scene(r,held,world,plate2):
 import chain,kitchen15 as K15,kitchen17 as K17
 from scene import build
 from checker import Checker
 from r19enc_check import meshheld
 ex={'r17_plate2':[.43,.15,K15.PLATE['c'][2]]} if plate2 else {}
 cfg=chain.chain_cfg('SD',**{**PS.BASE,**r.get('scene',{}),**ex,'r16_tools':{'ladle':None},**world,**(K17.held_cfg(r['obj'],r['grasp_sense']) if held else {})})
 tree,meta=build(cfg,None);meshheld(tree);pre=my_parts(tree);return Checker(tree,meta),pre
def union_scene():
 sys.argv=[sys.argv[0],'commands','ARM=ur5e_enc2_pgc','PY=.15']
 import r19hub
 from checker import Checker
 tree,meta=r19hub.union_tree();pre=my_parts(tree);return Checker(tree,meta),pre
def prep_scene(R,key):
 """a stored prep set's own scene (as r19prep4_verify.py) + the new parts."""
 import chain
 from scene import build
 from checker import Checker
 import kitchen16 as K,kitchen17 as K17,kitchen19 as K19,kitchen19p3 as P3,kitchen19p4 as P4
 names=[R['obj']]+[o[0] for o in (R['scene'].get('r19') or {}).get('objs',[])]+[o[0] for g in R.get('grasps',[]) for o in ((g['world'].get('r19') if 'r19' in g['world'] else g['world']) or {}).get('objs',[])]
 P3.ensure([n for n in names if not str(n).startswith(('dbh_','stg_p'))]);P4.ensure(names)
 if R['obj'].startswith('pusher_y'):K19.pusher_turned(float(R['obj'][8:]))
 K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=8.,0.,180.
 K19.LAYOUT.update({k:(tuple(v) if isinstance(v,list) and k!='drop_bowls' else v) for k,v in R['layout'].items()})
 BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},r14_fridge=True,r17_lever=0.,**K19.base_cfg())
 if key=='play':extra=K17.held_cfg(R['obj'],R['grasp_sense']);wo=None
 else:
  g=R['grasps'][key];kf=R['keyframes'][g['kf']];extra=g['world'] if 'r19' in g['world'] else dict(r19=g['world'])
  seat=kf.get('seat',.008 if R['obj'] in ('carrot','tomato') else 0.);wo=[R['obj'],kf['R'],(np.array(kf['p'])-[0,0,seat]).tolist()] if g['object_in_world'] is True else None
 cfg=chain.chain_cfg('SD',**{**BASE,**R['scene'],**extra})
 if wo is not None:cfg['r19']=dict(cfg['r19'],objs=list(cfg['r19'].get('objs',[]))+[wo])
 tree,meta=build(cfg,None);K19.add(tree,cfg);P4.add(tree,cfg);P3.mesh_held(tree)
 Rl,p=K17.lever_pose(K17.LEVER_OPEN);K._add(tree.find('worldbody'),'u_open_',K.OBJ['lever']['parts'],Rl,p,rgba='.75 .77 .8 1')
 if MODE=='t2l' and (cfg.get('r19p4') or {}).get('t2l'):   # the set has its own T2L state (pan held / parked): screen only the cradle + bracket
  pre=('R_cart_p4_cradle','R_cart_p4_bracket');P4.mesh(tree)
 elif MODE=='drawer' and (cfg.get('r19p4') or {}).get('drawer'):pre=('p4_drawer_',);P4.mesh(tree)
 else:pre=my_parts(tree)
 return Checker(tree,meta),pre
def run_path(task):
 kind,name,arg=task;t0=time.monotonic()
 try:
  potzone();held_sphere=False;sp=None
  if kind in ('play','app'):
   f,plate2=arg[0],arg[1];r=PS.J(f);PS.kitchen(r);potzone()
   if kind=='play':ch,pre=cook_scene(r,True,{},plate2);Q=r['play']
   else:
    k=arg[2];ap=r['approaches'][k];n=len(r['keyframes']);wd=PS.APP_WORLDS.get(r['obj'],lambda n:{})(n).get(ap['kf'],{})
    ch,pre=cook_scene(r,False,wd,plate2);Q=r['approach_qs'][k]
   X,sp=PS.sample(ch,Q)
  elif kind=='stir':   # the stored R19 stir cycle (lib_stir_cycle_<arm>.json certified states) in its own scene (as r19stir_cycle.model(-1)) + the new parts
   import chain,kitchen16 as K
   from scene import build
   from checker import Checker
   from r19enc_check import meshheld
   L=PS.J(arg);K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);potzone()
   cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_spatula=L['params']['grip_m'],r15_spatula_jaw=-1,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None,'spatula':None})
   tree,meta=build(cfg,None);meshheld(tree);pre=my_parts(tree);ch=Checker(tree,meta);X,sp=PS.sample(ch,L['states']['q'])
  elif kind=='prep':
   f,key=arg;R=PS.J(f);ch,pre=prep_scene(R,key);Q=R['play'] if key=='play' else R['approach_qs'][key];X,sp=PS.sample(ch,Q)
  else:
   import kitchen16 as K
   K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);potzone();ch,pre=union_scene()
   if kind=='edge':X=np.array(PS.J(arg)['qs'],float)
   else:r=PS.J(arg);X,sp=PS.sample(ch,r['play']);X=np.concatenate([X]+[np.array(a,float) for a in r.get('approach_qs',[]) if a]);held_sphere=True
  me=Meas(ch,pre,held_sphere);best=(1e9,None,1e9,None);arg_i=None;nh=0
  for i,q in enumerate(X):
   v=me(q)
   if v[0]<0:nh+=1
   if v[0]<best[0]:best=v;arg_i=i
  return dict(kind=kind,name=name,states=len(X),max_step_bound_mm=None if sp is None else round(sp*1e3,3),new_geoms=len(me.new),pairs=len(me.A),
   min_gate_mm=round(best[0]*1e3,2) if best[1] else None,min_dist_mm=round(best[2]*1e3,2) if best[1] else None,pair=best[1],category=best[3],state=arg_i,hit_states=nh,bounded_by_held_sphere=held_sphere,elapsed_s=round(time.monotonic()-t0,1))
 except Exception:
  import traceback;return dict(kind=kind,name=name,error=traceback.format_exc()[-900:])
def tasks():
 T=[];kinds=KV.get('KINDS','play,app,edge,other,stir,prep').split(',')
 ad=dict(PS.ADOPTED);ad['spider']=(SPIDER,False)
 for key,(f,p2) in ad.items():
  if 'play' in kinds:T.append(('play',key,(f,p2)))
  if 'app' in kinds:
   for k,a in enumerate(PS.J(f)['approach_qs']):
    if a:T.append(('app',f'{key}@app{k}',(f,p2,k)))
 if 'edge' in kinds:
  for f in sorted(glob.glob(f'{PS.HUBDIR}/edge_*.json')):
   if PS.J(f).get('ok'):T.append(('edge',os.path.basename(f)[5:-5],f))
 if 'other' in kinds:
  for c in PS.CUPS:
   if os.path.exists(c):T.append(('other',os.path.basename(c)[6:-5],c))
 if 'stir' in kinds:
  import arms;f=f"results/r19/stir/lib_stir_cycle_{arms.current()}.json"
  if os.path.exists(f):T.append(('stir','stir_cycle',f))
 if 'prep' in kinds:
  for f in PREP:
   try:R=PS.J(f)
   except Exception:continue   # (a file being rewritten by another job right now)
   if not R.get('ok'):continue
   nm=os.path.basename(f)[6:-5];T.append(('prep',nm,(f,'play')))
   for k,a in enumerate(R.get('approach_qs') or []):
    if a:T.append(('prep',f'{nm}@app{k}',(f,k)))
 return T
def main():
 import multiprocessing as mp
 T=tasks();t0=time.monotonic();print('tasks',len(T),flush=True)
 with mp.Pool(min(int(KV.get('WORKERS',16)),len(T)),maxtasksperchild=1) as pool:res=pool.map(run_path,T,chunksize=1)
 ok=[r for r in res if 'error' not in r];bad=[r for r in res if 'error' in r]
 worst=min(ok,key=lambda r:r['min_gate_mm'] if r['min_gate_mm'] is not None else 1e9) if ok else None
 summ=dict(mode=MODE,paths=len(res),errors=len(bad),states=sum(r['states'] for r in ok),hit_paths=[r['name'] for r in ok if r['hit_states']],
  worst=None if worst is None else {k:worst[k] for k in ('kind','name','min_gate_mm','min_dist_mm','pair','category')},
  by_kind={k:min([r['min_gate_mm'] for r in ok if r['kind']==k and r['min_gate_mm'] is not None],default=None) for k in ('play','app','edge','other','stir','prep')},potzone=POT)
 import arms;summ['arm']=arms.current();summ['empty_cradle']=KV.get('EMPTY')=='1'
 os.makedirs(OUT,exist_ok=True);fn=f"{OUT}/screen_{MODE}{'_empty' if KV.get('EMPTY')=='1' else ''}{('_'+KV['TAG']) if 'TAG' in KV else ''}.json";json.dump(dict(summary=summ,method=__doc__,rows=res),open(fn,'w'),indent=1,default=float)
 print(fn,json.dumps(summ,default=float),flush=True)
 for r in sorted(ok,key=lambda r:r['min_gate_mm'] if r['min_gate_mm'] is not None else 1e9)[:10]:print('  ',r['kind'],r['name'],r['states'],'min gate',r['min_gate_mm'],r['pair'],r['category'],'hits',r['hit_states'],flush=True)
 for r in bad:print('  ERROR',r['name'],r['error'][-400:],flush=True)
 print('done',round(time.monotonic()-t0),'s')
if __name__=='__main__':main()
