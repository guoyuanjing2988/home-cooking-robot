"""R19 #2 (FR5): the hub roadmap (r19hub.py, imported unchanged) for the cheap-arm candidate in the pot-zone layout.
New file. As r19pot_hub.py: the kitchen19pot layer (RACK=keyed, SPX / SPY spider rest) is installed before r19hub
builds its union scene; r19hub's action chain files are replaced by the six FR5 chains below (each re-checked at
<= 4 mm in this layout with PY=.15, R19_FR5.md section 2), and everything is written to results/r19/fr5/hub_<HUBTAG>/
(no R19 hub folder is touched). Nothing in r19hub.py is changed: its union scene, tuck search, 2pi relabels, edge
checks (<= 4 mm, full checker, unchanged gates), via poses, planner and graph are used as they are.
 python r19fr5_hub.py endpoints|tuck|hubs|screen|edge|graph  RACK=keyed SPX=1.56 SPY=.20 ARM=fr5_j6_pgc_sp20 PY=.15
        [HUBTAG=py.15_fr5_j6_pgc_sp20] [WOK= WOK2= LEVER= LID= SPIDER= SPAT=  chain files, defaults below]
        + the r19hub.py options of each command (TUCK= / ELBOW= / A= B= PLAN_S= ...)"""
import sys,os
sys.path.insert(0,'.')
CMD=sys.argv[1];KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
import kitchen19pot as P
P.install(rack=KV.get('RACK'),spider=(KV['SPX'],KV['SPY']) if 'SPX' in KV else None)
OWN=('RACK','SPX','SPY','HUBTAG','WOK','WOK2','LEVER','LID','SPIDER','SPAT')
sys.argv=[sys.argv[0],CMD]+[a for a in sys.argv[2:] if a.split('=',1)[0] not in OWN]
import r19hub as H
DEF=dict(WOK='results/r17/chain_wok_s-1_final_py.17_fr5_j6_pgc_sp20.json',             # planned with the plate at y .17; re-checked at .15 (WOKPY=1)
 WOK2='results/r17/chain_wok_s-1_r18plate2b_py.17_fr5_j6_pgc_sp20.json',                 # the same, 2nd plating spot
 LEVER='results/r17/chain_lever_s+1_final_fr5_j6_pgc_sp20.json',
 LID='results/r19/pot/chain_lid_s-1_pot_keyed_nospider_fr5_j6_pgc_sp20.json',
 SPIDER='results/r19/fr5/chain_spider_s+1_rt_1.56_.20_fr5_j6_pgc_sp20.json',
 SPAT='results/r17/chain_spatula_s-1_r18roll-1.15_.30_fr5_j6_pgc_sp20.json')
F={k:KV.get(k,v) for k,v in DEF.items()}
for f in F.values():assert os.path.exists(f),f
H.ACT={'wok':[F['WOK'],F['WOK2']],'lever':[F['LEVER']],'lid':[F['LID']],'spider':[F['SPIDER']],'spatula':[F['SPAT']]}
H.OUT='results/r19/fr5/hub_'+KV.get('HUBTAG','py.15_fr5_j6_pgc_sp20');os.makedirs(H.OUT,exist_ok=True)
if __name__=='__main__':
 print('arm',H.ARM,'PY',H.K15.PLATE['c'][1],'spider rest',H.K.TOOL_XY['spider'],'rack',P.ACTIVE['rack'],'out',H.OUT,flush=True)
 {'endpoints':H.cmd_endpoints,'tuck':H.tuck_search,'hubs':H.cmd_hubs,'screen':H.cmd_screen,'edge':H.cmd_edge,'graph':H.cmd_graph}[CMD]()
