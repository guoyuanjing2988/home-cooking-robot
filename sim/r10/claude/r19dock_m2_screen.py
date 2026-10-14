"""R19 #39 dock screens on the adopted m2 mount (#42): r19dock_screen.py (unchanged) with the inputs of a MANIFEST
(r19dock_m2.py). New file; nothing else is changed. Writes only to results/r19/dock/m2/<arm>/.
PART=travel  the cart travel / docked screen with the arm's m2 station list (results/r19/dock/m2/<arm>/stations.json,
             from r19dock_m2.py stations) -> screen_travel.json
PART=arm     every m2 path of the manifest replayed with the dock parts (r19dock_screen PART=arm = r19prep5_screen's
             method): the six cooking chains + their approaches, the ok edges of the m2 hub, the prep sets (+ approaches),
             the #41 stir library (short01) and the two stir-join sets (STIR_ENTRY / STIR_EXIT, wrapped as stir-scene
             libraries in the output folder). The old UR5e-base cup chains are not part of the m2 set -> screen_dock[_TAG].json
python r19dock_m2_screen.py PART=travel|arm MANIFEST=<json> [WORKERS=8] [TLIM=280] [KINDS=..] [ONLY=k1,k2] [TAG=..] [PIN=up|down]
ONLY= limits the prep sets (keys of the manifest's prep) and EDGES=a:b the ok edges (smoke runs)."""
import sys,os,json
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
import r19dock_m2 as M2   # puts the manifest's ARM= / PY= into sys.argv before anything imports arms
MF=M2.manifest();OUT=M2.outdir(MF)
PART=KV.get('PART','travel')
def _stir_tasks():
 """the #41 library and the two join sets as stir-scene libraries ({'params': {'grip_m'}, 'states': {'q'}})."""
 L=M2.J(MF['stir']);out=[('stir','stir_short01',MF['stir'])]
 for s in M2.J(MF['stirjoin'])['sets']:
  f=f"{OUT}/stirjoin_{s['id']}.json"
  if not os.path.exists(f):json.dump(dict(params=dict(grip_m=L['params']['grip_m']),states=dict(q=s['states']['q']),source=MF['stirjoin'],id=s['id']),open(f,'w'))
  out.append(('stir','join_'+s['id'],f))
 return out
if PART=='arm':
 sys.argv=[a for a in sys.argv if not a.startswith('PART=')]+['PART=arm']
 import r19dock_screen as S
 P5S=S.P5S;S4=P5S.S4;PS=S4.PS
 P5S.OUT=OUT
 prep=MF['prep'];only=[k for k in KV.get('ONLY','').split(',') if k]
 P5S.SETS=[f for k,f in prep.items() if not only or k in only]
 c=MF['chains']
 PS.ADOPTED=dict(wok=(c['wok'],False),wok_plate2b=(c['wok_plate2'],True),lever=(c['lever'],False),lid=(c['lid'],False),spatula=(c['spatula'],False),spider=(c['spider'],False))
 S4.SPIDER=c['spider'];PS.HUBDIR=MF['hubdir'];PS.CUPS=[]
 _tasks=P5S.tasks
 def tasks():
  T=[t for t in _tasks() if t[0]!='stir']
  if 'EDGES' in KV:
   a,b=map(int,KV['EDGES'].split(':'));E=[t for t in T if t[0]=='edge'];keep=set(t[1] for t in E[a:b]);T=[t for t in T if t[0]!='edge' or t[1] in keep]
  if 'stir' in KV.get('KINDS','prep,play,app,edge,stir'):T+=_stir_tasks()
  return T
 P5S.tasks=tasks
 P5S.KV.setdefault('KINDS','prep,play,app,edge,stir')
if __name__=='__main__':
 if PART=='travel':
  import kitchen19dock as D,r19dock_screen as S
  D.STATIONS=dict(M2.load_stations(MF));S.OUT=OUT
  print('stations',D.STATIONS,flush=True);S.travel()
 else:
  print('m2 screen',MF['arm'],'sets',len(P5S.SETS),'hub',MF['hubdir'],flush=True);P5S.main()
