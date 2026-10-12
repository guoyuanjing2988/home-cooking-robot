"""Retry brush withdrawal using clearance-aware Cartesian continuation."""
import sys,json,shutil,time
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];O=H/'results';history=H/'history/v6';history.mkdir(exist_ok=True)
record=O/'motion_v6'/ID/'internal_17.json';prior=history/f'{ID}_internal17_before_robust.json'
if not prior.exists():shutil.copy2(record,prior)
previous=json.loads(prior.read_text())
checkpoint=H/'audit'/f'{ID}_internal_17_partial.json';d=json.loads(checkpoint.read_text());d['edges']=d['edges'][:2];checkpoint.write_text(json.dumps(d,indent=2))
source=(H/'motion_v6_r07.py').read_text().replace('from least_analytic_v4_r07 import solve as avoid','from least_analytic_v6_r07 import solve as avoid').replace('ch.lock_initial_carriage=False;candidate,errors,hh,_=avoid','ch.lock_initial_carriage=False;ch.night_robust=True;candidate,errors,hh,_=avoid')
sys.argv=['motion_v6_r07.py',ID,'internal','17'];exec(compile(source,str(H/'motion_v6_r07.py'),'exec'),{'__name__':'__main__','__file__':str(H/'motion_v6_r07.py')})
row=json.loads(record.read_text());row['retry_policy']=dict(prior_result=str(prior.relative_to(H)),reason='Prior Cartesian continuation rejected the final withdrawal edge. Use v6 extra10mm responsive-pair objective in collision-aware working-line continuation; keep exact process, geometry, pose and final gates.',prior_last_rejection=previous['edges'][-1].get('last_rejection'),prior_final_ik=previous['edges'][-1].get('working_ik_diagnostics',[])[-1:],reused_accepted_edges=2,new_edge_budget_s=65);record.write_text(json.dumps(row,indent=2));print('ROBUST_WITHDRAWAL_RETRY',row['ok'])
