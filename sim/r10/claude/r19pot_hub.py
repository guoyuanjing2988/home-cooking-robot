"""R19 pot zone (GitHub #37, #8): the hub roadmap (r19hub.py, run unchanged) in the pot-zone layout. New file.

r19hub.py is imported as it is; this wrapper only installs the kitchen19pot layer (RACK=keyed, SPX / SPY spider rest)
before its union scene is built, points its 'spider' (and optionally 'lid') action at the new chain, and writes to
results/r19/pot/hub_<HUBTAG>/ (the R19 hub folder is not touched).
 python r19pot_hub.py hubs  SPIDER=<chain> RACK=keyed SPX= SPY= HUBTAG=<t> ARM=ur5e_enc2_pgc PY=.15
     endpoints, 2pi relabels and hubs.json with the SAME tuck as FROM (default results/r19/hub_py.15_ur5e_enc2_pgc);
     prints, per endpoint, whether it is identical to FROM's (only the moved action's endpoint may differ)
 python r19pot_hub.py edge A=SPIDER B=H_POT [PLAN_S=120] SPIDER=... (same options)   -> edge_<A>__<B>.json, as r19hub.py edge
 python r19pot_hub.py graph ... : copies FROM's edge files whose two endpoints are unchanged (their states are valid in
     the new layout only together with the moved-fixture re-screen, r19pot_screen.py: pairwise clearance), then
     r19hub.py graph on the folder."""
import sys,os,json,shutil
sys.path.insert(0,'.')
CMD=sys.argv[1];KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
import kitchen19pot as P
P.install(rack=KV.get('RACK'),spider=(KV['SPX'],KV['SPY']) if 'SPX' in KV else None)
sys.argv=[sys.argv[0],CMD]+[a for a in sys.argv[2:] if a.split('=',1)[0] not in ('RACK','SPX','SPY','SPIDER','LID','HUBTAG','FROM')]
import r19hub as H
FROM=KV.get('FROM','results/r19/hub_py.15_ur5e_enc2_pgc')
H.OUT='results/r19/pot/hub_'+KV.get('HUBTAG','final');os.makedirs(H.OUT,exist_ok=True)
if 'SPIDER' in KV:H.ACT['spider']=[KV['SPIDER']]
if 'LID' in KV:H.ACT['lid']=[KV['LID']]
def changed():
 a=json.load(open(f'{FROM}/hubs.json'))['endpoints'];b=json.load(open(f'{H.OUT}/hubs.json'))['endpoints']
 import numpy as np
 return {e:bool(np.max(abs(np.array(a[e]['q_shifted'])-np.array(b[e]['q_shifted'])))>1e-9) for e in a}
if CMD=='hubs':
 H.KV.setdefault('TUCKFILE',f'{FROM}/tuck_neg.json');H.cmd_hubs();print('endpoint changed vs',FROM,changed())
elif CMD=='edge':H.cmd_edge()
elif CMD=='graph':
 ch=changed();n=0
 for f in sorted(os.listdir(FROM)):
  if not(f.startswith('edge_') and f.endswith('.json')):continue
  a,b=f[5:-5].split('__')
  if ch.get(a) or ch.get(b) or os.path.exists(f'{H.OUT}/{f}'):continue
  shutil.copyfile(f'{FROM}/{f}',f'{H.OUT}/{f}');n+=1
 print('copied',n,'unchanged edges from',FROM);H.cmd_graph()
