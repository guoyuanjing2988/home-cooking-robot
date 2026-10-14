"""R19 #39 dock: the #13 worst-corner replays on the adopted m2 mount (#42), through r19dock_tol.py (and with it
r19tol_replay.py / r19tol_core.py / r19pot_tol.py, all unchanged). New file. Writes only to
results/r19/dock/m2/<arm>/tol/<TOLTAG>/.
This wrapper, from the MANIFEST (r19dock_m2.py):
 - puts ARM= / PY= and the pot-zone layer of the m2 certification (POT=1 RACK=keyed POTWIN=1 SPX SPY, SPIDER= / LID=
   the manifest's m2 spider / lid chains -> scenes play:spider19 / play:lid19 and their approaches) into sys.argv before
   r19dock_tol imports r19pot_tol; installs the spider rest for the hub union scene too (kitchen19pot.install);
 - points r19tol_core.CHAINS wok / spatula / lever at the manifest's m2 chains (same keyframe indices as the R17 chains,
   so the approach worlds are unchanged) and r19tol_core.hubdir at the m2 hub (only edges whose file is ok are run);
 - replaces the dock boxes by the arm's own m2 budget (results/r19/dock/m2/<arm>/budget.json, r19dock_m2.py budget);
   the #13 'dock_stops' box (the #39 target) stays available for comparison;
 - SCENES=main expands to the wok / spatula / lever plays + approaches + every ok m2 hub edge; SCENES=pot to the lid19 /
   spider19 approaches + the spider19 play (the lid19 play is run in state chunks, as r19dock_tol: PARTS=scen-<box>+c<k>of<n>).
python r19dock_m2_tol.py MANIFEST=<json> SCENES=main|pot|<list> PARTS=scen-dock_stops,scen-dock_rail,scen-dock_rail_map TOLTAG=main [WORKERS=8] [DEADLINE=280]
python r19dock_m2_tol.py MANIFEST=<json> TOLTAG=pot MERGE=1"""
import sys,os,json
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
MF=json.load(open(KV['MANIFEST']))
_add=dict(ARM=MF['arm'],PY=MF['py'],POT='1',RACK=MF['pot']['RACK'],POTWIN='1',SPX=MF['pot']['SPX'],SPY=MF['pot']['SPY'],SPIDER=MF['chains']['spider'],LID=MF['chains']['lid'])
for k,v in _add.items():
 if k not in KV:sys.argv.append(f'{k}={v}');KV[k]=v
import kitchen19pot;kitchen19pot.install(rack='keyed',spider=(float(MF['pot']['SPX']),float(MF['pot']['SPY'])))
import r19dock_tol as T   # imports r19pot_tol (pot layer, lid19 / spider19, lid window), r19tol_core, r19tol_replay
C=T.C;R=T.R
OUT=f"results/r19/dock/m2/{MF['arm']}"
C.OUT=f"{OUT}/tol/{KV.get('TOLTAG','run')}"
_B=json.load(open(f'{OUT}/budget.json'))
for k,v in _B['scenario_halfranges_m_rad'].items():R.SCENARIOS[k]=list(v)
for a in ('wok','spatula','lever'):C.CHAINS[a]=dict(C.CHAINS[a],file=MF['chains'][a])
C.hubdir=lambda:MF['hubdir']
def _expand(s):
 if s=='main':
  import glob
  E=['edge:'+os.path.basename(f)[5:-5] for f in sorted(glob.glob(f"{MF['hubdir']}/edge_*.json")) if C.J(f).get('ok')]
  return ','.join(['play:wok','app:wok:0','app:wok:1','play:spatula','app:spatula:0','play:lever','app:lever:0','app:lever:1']+E)
 if s=='pot':return 'app:lid19:0,app:lid19:1,play:spider19,app:spider19:0,app:spider19:1'
 return s
if 'SCENES' in KV:R.KV['SCENES']=_expand(KV['SCENES'])
if __name__=='__main__':
 if KV.get('MERGE')=='1':T.merge();raise SystemExit
 print('m2 tol',MF['arm'],'chains',{a:C.CHAINS[a]['file'] for a in ('wok','spatula','lever','lid19','spider19')},'hub',MF['hubdir'],flush=True)
 print('boxes',{k:R.SCENARIOS[k] for k in ('dock_stops','dock_rail','dock_rail_map')},'out',C.OUT,flush=True)
 R.main()
