"""R19 pot zone (GitHub #37, #8): re-screen a MOVED pot-zone fixture against every stored path. New file.

A fixture move only changes the pairs that involve that fixture; every other pair of every stored state keeps the
distance it was checked with. So for each candidate the stored states are replayed with the fixture at its new
place and ONLY its pairs are measured, exactly: per state the enclosing-AABB separation of every robot geom vs
every moved-fixture geom, refined by the checker's own GJK lower bound (distance.Bounds.pair) wherever the AABB
bound is within 30 mm of the gap; gate = distance - the checker's gap (10 mm robot-environment, 5 mm gripper /
held-environment). The old place of the fixture is gone from the scene (it can only have helped).
Moved fixtures:
 SPOTS=x,y;x,y;...   spider rest (kitchen16 cradle pad + the spider lying on it): r16_rest_spider, r16_spider_*
 RACK=keyed          the keyed lid rack of kitchen19pot.py: r19pot_rack_* (with the declared lid window: in window
                     states the held lid vs the rack is the intended contact, not a hit; reported separately)
Paths (ARM=ur5e_enc2_pgc, PY=.15, the checking standard; stored states 2pi-unwrapped, joint-linear between
stored states, cut to <= 4 mm point bound as r19smooth.sample_poly):
 - the adopted chains results/r17/chain_*_ur5e_enc2_pgc.json (wok and plate 2 at py.15, lever, lid, spatula; the
   spider chain only in RACK mode or with EXTRA=) + their grasp approaches / release retreats (empty gripper);
 - the 22 hub edges results/r19/hub_py.15_ur5e_enc2_pgc/edge_*.json (stored <= 4 mm states, r19hub union scene);
 - the prep sets results/r19/prep/chain_*_full_ur5e_enc2_pgc.json and the checked cup chains (R19_CUPS.md table:
   s10a/b/d/f, s11S, s11enc), replayed in the union scene WITHOUT their own held object: the held object is
   bounded by a sphere of HELD_R = 0.20 m around the TCP (point-to-AABB lower bound), so their numbers are
   conservative lower bounds; they need an exact replay only if that bound comes near the gap.
EXTRA=<chain json>,...  more r17chain-format chains (e.g. a re-planned spider) with their r17chain approach worlds.
python r19pot_screen.py SPOTS=1.60,.26 [RACK=keyed] [EXTRA=..] ARM=ur5e_enc2_pgc PY=.15 [WORKERS=12] [TAG=..]
 -> results/r19/pot/screen_<spot|rack>[_<TAG>].json"""
import sys,os,json,math,time,glob
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
OUT='results/r19/pot'
HELD_R=.20;CAP=.030
ADOPTED=dict(wok=('results/r17/chain_wok_s-1_final_py.15_ur5e_enc2_pgc.json',False),wok_plate2b=('results/r17/chain_wok_s-1_r18plate2b_py.15_ur5e_enc2_pgc.json',True),
 lever=('results/r17/chain_lever_s+1_final_ur5e_enc2_pgc.json',False),lid=('results/r17/chain_lid_s-1_final_ur5e_enc2_pgc.json',False),
 spatula=('results/r17/chain_spatula_s-1_r18roll-1.15_.30_ur5e_enc2_pgc.json',False),spider=('results/r17/chain_spider_s+1_final_ur5e_enc2_pgc.json',False))
APP_WORLDS=dict(wok=lambda n:{0:{'r17_lever':30.},n-1:{'r17_lever':30.}},lever=lambda n:{0:{'r17_lever':0.},1:{'r17_lever':30.}},
 lid=lambda n:{0:{'r16_lid':'on'},n-1:{'r16_lid':'rack'}},spider=lambda n:{0:{},n-1:{}},spatula_b=lambda n:{0:{'r16_tools':{'ladle':None}}})
CUPS=['results/r19/cups/chain_cup_T2R_b1_L_s+1_s10'+s+'.json' for s in 'abdf']+['results/r19/cups/chain_cup_T2R_b1_S_s+1_s11S.json','results/r19/cups/chain_cup_T2R_b1_L_s+1_s11enc_ur5e_enc.json']
HUBDIR='results/r19/hub_py.15_ur5e_enc2_pgc'
def J(f):return json.load(open(f,encoding='utf-8'))
def layer(mode):
 import kitchen19pot as P
 if mode[0]=='spot':P.install(spider=mode[1])
 else:P.install(rack='keyed')
 return P
def moved_prefix(mode):return ('r16_rest_spider','r16_spider_') if mode[0]=='spot' else ('r19pot_rack_',)
def kitchen(r):
 import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
 K15.PLATE['c'][1]=.15;K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K17.set_wok_tilt(float(r.get('wok_tilt') or 0.))
 sp=K.TOOL_XY['spider']
 for k,v in r.get('tool_xy',{}).items():K.TOOL_XY[k]=tuple(v)
 K.TOOL_XY['spider']=sp;K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV=8.;K.SPAT_YAW=0.;K.SPAT_ROLL=180.
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)
def scene(r,held,world,plate2):
 import chain,kitchen15 as K15,kitchen17 as K17
 from scene import build
 from checker import Checker
 from r19enc_check import meshheld
 ex={'r17_plate2':[.43,.15,K15.PLATE['c'][2]]} if plate2 else {}
 cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),**ex,'r16_tools':{'ladle':None},**world,**(K17.held_cfg(r['obj'],r['grasp_sense']) if held else {})})
 tree,meta=build(cfg,None);meshheld(tree);return Checker(tree,meta)
def union():
 sys.argv=[sys.argv[0],'commands']+[a for a in sys.argv[1:] if a.startswith(('ARM=','PY='))]
 import r19hub
 from checker import Checker
 tree,meta=r19hub.union_tree();return Checker(tree,meta)
class Meas:
 """Exact min gate of the moved-fixture pairs per state (see the module doc)."""
 def __init__(s,ch,prefix,window=None,held_sphere=False):
  import mujoco
  s.ch=ch;m=ch.m;s.m=m;s.mj=mujoco;nm=ch.gnames
  s.env=[g for g in range(m.ngeom) if not ch.robot[g] and nm[g].startswith(prefix)]
  rob=[g for g in range(m.ngeom) if ch.robot[g] and m.geom_type[g]!=0];pr=[]
  for a in rob:
   for b in s.env:
    q=ch.required(ch,a,b)
    if q is not None and q[1]!='self':pr.append((a,b,q[0]))
  s.A=np.array([p[0] for p in pr],int);s.B=np.array([p[1] for p in pr],int);s.N=np.array([p[2] for p in pr]);s.rob=sorted(set(s.A.tolist()))
  s.win=window;s.sid=m.site('R_prep').id;s.held_sphere=held_sphere
  if window is not None:
   wp=set(window['parts']);wf=set(window['faces']);s.wmask=np.array([nm[a] in wp and nm[b] in wf for a,b in zip(s.A,s.B)])
  mujoco.mj_kinematics(m,ch.d);s.elo={};s.ehi={}
  for g in s.env:
   R=ch.d.geom_xmat[g].reshape(3,3);c=ch.d.geom_xpos[g]+R@m.geom_aabb[g,:3];e=np.abs(R)@m.geom_aabb[g,3:];s.elo[g]=c-e;s.ehi[g]=c+e
 def __call__(s,q):
  m,d=s.m,s.ch.d;d.qpos[:]=q;s.mj.mj_kinematics(m,d);lo=np.zeros((m.ngeom,3));hi=np.zeros((m.ngeom,3))
  for g in s.rob:
   R=d.geom_xmat[g].reshape(3,3);c=d.geom_xpos[g]+R@m.geom_aabb[g,:3];e=np.abs(R)@m.geom_aabb[g,3:];lo[g]=c-e;hi[g]=c+e
  for g in s.env:lo[g]=s.elo[g];hi[g]=s.ehi[g]
  inwin=False;mask=np.ones(len(s.A),bool)
  if s.win is not None:
   import kitchen19pot as P
   inwin=P.in_window(s.win,d.site_xpos[s.sid],d.site_xmat[s.sid].reshape(3,3))
   if inwin:mask=~s.wmask
  best=(1e9,None,1e9)
  if len(s.A):
   dl=np.maximum(np.maximum(lo[s.A]-hi[s.B],lo[s.B]-hi[s.A]),0.);ab=np.sqrt((dl*dl).sum(1));key=np.where(mask,ab-s.N,1e9)
   for i in np.argsort(key):
    if key[i]>=min(best[0],CAP):break
    dist=max(ab[i],s.ch.bounds.pair(int(s.A[i]),int(s.B[i]))['lower_m']);v=dist-s.N[i]
    if v<best[0]:best=(float(v),[s.ch.gnames[s.A[i]],s.ch.gnames[s.B[i]]],float(dist))
  if s.held_sphere:   # an unmodelled held object within HELD_R of the TCP (gap 5 mm): point-to-AABB lower bound
   p=d.site_xpos[s.sid]
   for g in s.env:
    dd=float(np.linalg.norm(np.maximum(np.maximum(s.elo[g]-p,p-s.ehi[g]),0.)))-HELD_R-.005
    if dd<best[0]:best=(dd,['held object within %.2f m of the TCP'%HELD_R,s.ch.gnames[g]],dd+.005)
  return best,inwin
def sample(ch,Q):
 import r19smooth as S
 Q=S.unwrap(np.array(Q,float));X,src,sp=S.sample_poly(Q,S.FastBound(ch));return X,sp
def run_path(task):
 mode,kind,name,arg=task;t0=time.monotonic()
 try:
  P=layer(mode);pre=moved_prefix(mode);held_sphere=False;W=None
  if kind in ('play','app'):
   f,plate2=arg[0],arg[1];r=J(f);kitchen(r)
   if kind=='play':ch=scene(r,True,{},plate2);Q=r['play']
   else:
    k=arg[2];ap=r['approaches'][k];n=len(r['keyframes']);wd=APP_WORLDS.get(r['obj'],lambda n:{})(n).get(ap['kf'],{})
    ch=scene(r,False,wd,plate2);Q=r['approach_qs'][k]
   if mode[0]=='rack' and r['obj']=='lid' and kind=='play':W=P.window(sign=r['grasp_sense'])
   X,sp=sample(ch,Q)
  else:
   import kitchen16 as K
   K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);ch=union()
   if kind=='edge':X=np.array(J(arg)['qs'],float);sp=None
   else:r=J(arg);X,sp=sample(ch,r['play']);X=np.concatenate([X]+[np.array(a,float) for a in r.get('approach_qs',[]) if a]);held_sphere=True
  me=Meas(ch,pre,W,held_sphere);best=(1e9,None,1e9);arg_i=None;nh=0;nwin=0;wmin=1e9
  for i,q in enumerate(X):
   (v,pr,dist),inwin=me(q);nwin+=inwin
   if v<0:nh+=1
   if v<best[0]:best=(v,pr,dist);arg_i=i
  if W is not None and nwin:   # the intended contact in the window: its distance (for the record; not gated)
   me2=Meas(ch,pre,None)
   for q in X:
    me2.ch.d.qpos[:]=q;me2.mj.mj_kinematics(me2.m,me2.ch.d)
    if P.in_window(W,me2.ch.d.site_xpos[me2.sid],me2.ch.d.site_xmat[me2.sid].reshape(3,3)):wmin=min(wmin,me2(q)[0][2])
  return dict(mode=list(mode[:1])+[list(mode[1]) if mode[0]=='spot' else mode[1]],kind=kind,name=name,states=len(X),max_step_bound_mm=None if sp is None else round(sp*1e3,3),
   moved_geoms=len(me.env),min_gate_mm=round(best[0]*1e3,2) if best[1] else None,min_dist_mm=round(best[2]*1e3,2) if best[1] else None,pair=best[1],state=arg_i,
   hit_states=nh,window_states=nwin,window_min_dist_mm=None if wmin>=1e8 else round(wmin*1e3,2),bounded_by_held_sphere=held_sphere,elapsed_s=round(time.monotonic()-t0,1))
 except Exception:
  import traceback;return dict(kind=kind,name=name,error=traceback.format_exc()[-800:])
def tasks(mode):
 T=[];extra=[e for e in KV.get('EXTRA','').split(',') if e]
 for key,(f,p2) in ADOPTED.items():
  if key=='spider' and mode[0]=='spot':continue
  T.append((mode,'play',key,(f,p2)))
  for k,a in enumerate(J(f)['approach_qs']):
   if a:T.append((mode,'app',f'{key}@app{k}',(f,p2,k)))
 for f in extra:
  T.append((mode,'play',os.path.basename(f),(f,False)))
  for k,a in enumerate(J(f)['approach_qs']):
   if a:T.append((mode,'app',os.path.basename(f)+f'@app{k}',(f,False,k)))
 for f in sorted(glob.glob(f'{HUBDIR}/edge_*.json')):
  if J(f).get('ok'):T.append((mode,'edge',os.path.basename(f)[5:-5],f))
 for f in sorted(glob.glob('results/r19/prep/chain_*_full_ur5e_enc2_pgc.json'))+[c for c in CUPS if os.path.exists(c)]:T.append((mode,'other',os.path.basename(f)[6:-5],f))
 return T
def main():
 import multiprocessing as mp
 modes=[('spot',tuple(float(v) for v in s.split(','))) for s in KV.get('SPOTS','').split(';') if s]+([('rack','keyed')] if KV.get('RACK')=='keyed' else [])
 T=[t for md in modes for t in tasks(md)];t0=time.monotonic();print('tasks',len(T),flush=True)
 with mp.Pool(min(int(KV.get('WORKERS',12)),len(T)),maxtasksperchild=1) as pool:res=pool.map(run_path,T,chunksize=1)
 os.makedirs(OUT,exist_ok=True)
 for md in modes:
  rows=[r for r,t in zip(res,T) if t[0]==md];tag=f"spot_{md[1][0]:.2f}_{md[1][1]:.2f}" if md[0]=='spot' else 'rack_keyed'
  ok=[r for r in rows if 'error' not in r];bad=[r for r in rows if 'error' in r]
  worst=min(ok,key=lambda r:r['min_gate_mm'] if r['min_gate_mm'] is not None else 1e9) if ok else None
  summ=dict(mode=tag,paths=len(rows),errors=len(bad),states=sum(r['states'] for r in ok),hit_paths=[r['name'] for r in ok if r['hit_states']],
   worst=None if worst is None else {k:worst[k] for k in ('kind','name','min_gate_mm','min_dist_mm','pair')},
   by_kind={k:min([r['min_gate_mm'] for r in ok if r['kind']==k and r['min_gate_mm'] is not None],default=None) for k in ('play','app','edge','other')})
  fn=f"{OUT}/screen_{tag}{('_'+KV['TAG']) if 'TAG' in KV else ''}.json";json.dump(dict(summary=summ,method=__doc__,rows=rows),open(fn,'w'),indent=1,default=float)
  print(fn,json.dumps(summ,default=float),flush=True)
  for r in sorted(ok,key=lambda r:r['min_gate_mm'] if r['min_gate_mm'] is not None else 1e9)[:8]:print('  ',r['kind'],r['name'],r['states'],'min gate',r['min_gate_mm'],r['pair'],'hits',r['hit_states'],'win',r['window_states'],r['window_min_dist_mm'],flush=True)
  for r in bad:print('  ERROR',r['name'],r['error'][-300:],flush=True)
 print('done',round(time.monotonic()-t0),'s')
if __name__=='__main__':main()
