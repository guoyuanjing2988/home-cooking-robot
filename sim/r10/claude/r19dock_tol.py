"""R19 cart docking (GitHub #39): the #13 worst-corner replays (r19tol_replay.py, unchanged) with the budget boxes the
docking-rail design achieves. New file; r19tol_replay.py / r19tol_core.py / r19pot_tol.py are imported and run as they are.
This wrapper only
 - adds the cart budget boxes of results/r19/dock/budget.json (r19dock_budget.py PART=budget) to
   r19tol_replay.SCENARIOS: 'dock_rail' (tier 1: the hardware + commissioning shims) and 'dock_rail_map' (tier 2: + the
   commissioning pose map in the certification);
 - with POT=1 imports r19pot_tol first (the pot-zone layer exactly as R19_POTZONE.md: RACK=keyed, POTWIN=1, the spider
   rest SPX / SPY, the re-planned spider chain SPIDER=..., the lid window), for the lid19 / spider19 scenes;
 - writes to results/r19/dock/tol/<TOLTAG>/ and re-uses (reads only) the nominal caches of the #13 / #37 runs
   (results/r19/tol/<arm>_py<y>/cache, results/r19/pot/tol/*/cache) when the scene hash matches; a missing cache is
   computed and written to the dock folder.
python r19dock_tol.py SCENES=play:wok,... PARTS=scen-dock_rail,scen-dock_rail_map TOLTAG=main ARM=ur5e_enc2_pgc PY=.15 [WORKERS=..] [DEADLINE=270]
python r19dock_tol.py POT=1 RACK=keyed POTWIN=1 SPIDER=<json> SPX=1.56 SPY=.20 SCENES=play:lid19,... PARTS=... TOLTAG=pot ARM=ur5e_enc2_pgc PY=.15"""
import sys,os,json,glob,math,pickle
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
if KV.get('POT')=='1':import r19pot_tol   # noqa: F401  (installs the pot-zone layer + lid window in this process, as R19_POTZONE.md)
import r19tol_core as C
import r19tol_replay as R
C.OUT='results/r19/dock/tol/'+KV.get('TOLTAG','run')
B=json.load(open('results/r19/dock/budget.json'))
for k,v in B['scenario_halfranges_m_rad'].items():R.SCENARIOS[k]=list(v)
_ln=R.load_nominal
def load_nominal(key,ch,Q,ev):
 """r19tol_replay.load_nominal, first looking for the same cache file (same scene key, states and model hash) in the
 #13 / #37 cache folders (read only)."""
 import hashlib,numpy as np
 h=hashlib.sha1(np.ascontiguousarray(Q).tobytes()+ch.xml.encode()).hexdigest()[:16];name=f"nom_{key.replace(':','_')}_{h}.pkl"
 for d in [f'{C.OUT}/cache']+sorted(glob.glob('results/r19/tol/*/cache'))+['results/r19/tol/cache']+sorted(glob.glob('results/r19/pot/tol/*/cache')):
  f=os.path.join(d,name)
  if os.path.exists(f):
   try:return pickle.load(open(f,'rb')),True
   except Exception:pass
 return _ln(key,ch,Q,ev)
R.load_nominal=load_nominal
_sc=R.scenarios
def scenarios(ev,Q,noms,info,src,key,names=None):
 """r19tol_replay.scenarios, optionally on a CHUNK of the states: a part name 'scen-<box>+c<k>of<n>' evaluates only the
 states with index % n == k (the others get a nominal bound of 1 m, so the branch and bound never opens them). The
 exact minimum of the box is the minimum over its n chunk files (r19dock_tol.py MERGE=1)."""
 import re
 ch=[re.fullmatch(r'c(\d+)of(\d+)',x) for x in (names or [])];ch=[m for m in ch if m]
 if ch:
  k,n=int(ch[0].group(1)),int(ch[0].group(2));noms=[x if i%n==k else dict(x,gate=1.,contact=1.) for i,x in enumerate(noms)]
  names=[x for x in names if not re.fullmatch(r'c\d+of\d+',x)]
 out=_sc(ev,Q,noms,info,src,key,names)
 if ch:
  for v in out.values():v['chunk']=[k,n]
 return out
R.scenarios=scenarios
def merge():
 """min over the chunk files of each (scene, box) in C.OUT -> merged_<scene>__<box>.json"""
 import re
 groups={}
 for f in glob.glob(f'{C.OUT}/scene_*__scen-*+c*of*.json'):
  r=json.load(open(f))
  for box,v in r['scenarios'].items():groups.setdefault((r['scene'],box),[]).append(v)
 for (scene,box),vs in groups.items():
  n=vs[0]['chunk'][1];got=sorted(v['chunk'][0] for v in vs);res=dict(scene=scene,box=box,chunks=got,of=n,complete=got==list(range(n)))
  for meas in ('gate','contact'):
   num=[v[meas] for v in vs if not isinstance(v[meas]['min_mm'],str)]
   best=min(num,key=lambda v:v['min_mm']) if num else vs[0][meas]
   res[meas]=best;res[meas+'_evals']=sum(v[meas].get('evals',0) for v in vs)
  fn=f"{C.OUT}/merged_{scene.replace(':','_')}__{box}.json";json.dump(res,open(fn,'w'),indent=1)
  print(scene,box,'chunks',got,'of',n,'gate',res['gate']['min_mm'],res['gate'].get('pair'),res['gate'].get('corner'),'contact',res['contact']['min_mm'],flush=True)
if __name__=='__main__' and KV.get('MERGE')=='1':
 merge();raise SystemExit
if __name__=='__main__':
 print('scenarios',{k:[round(x*1e3,3) if i<3 else round(math.degrees(x),3) for i,x in enumerate(v)] for k,v in R.SCENARIOS.items()},'out',C.OUT,flush=True)
 R.main()
