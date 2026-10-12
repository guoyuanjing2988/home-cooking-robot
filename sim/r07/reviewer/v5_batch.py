from pathlib import Path
import subprocess,sys,json
H=Path(__file__).resolve().parent;I=H.parent/'integrator'
rows=json.loads((I/'results/motion.json').read_text())['internal_paths'];ok=[r for r in rows if r['ok']]
rank=sorted(ok,key=lambda r:r['final_replay'].get('states_checked',0),reverse=True)
tight=sorted(ok,key=lambda r:min((v['min_mm'] for k,v in r['final_replay'].get('clearance_distribution',{}).items() if k!='self'),default=1e9))
ids=list(dict.fromkeys([rank[0]['index'],tight[0]['index'],1,2,5,7,11,20,39,50,51,56,57]))
ids=[i for i in ids if any(r['index']==i for r in ok)]
(H/'results_v5/internal_selection.json').write_text(json.dumps({'selected':ids,'longest_states':rank[0]['index'],'tightest_submitted':tight[0]['index']},indent=2))
for i in ids:
 if (H/f'results_v5/internal_{i}.json').exists():continue
 subprocess.run([sys.executable,'-B',str(H/'v5_internal.py'),str(i)],check=True,timeout=240)
