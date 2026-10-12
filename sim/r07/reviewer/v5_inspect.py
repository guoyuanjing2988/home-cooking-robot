from pathlib import Path
import json
I=Path(__file__).resolve().parent.parent/'integrator'
def read(n):return json.loads((I/'results'/n).read_text())
for n in ('idle.json','state_sequence.json','connection_summary_v5.json','state_model_regression_v5.json'):
 d=read(n);print(n)
 for k,v in d.items():
  if k in ('task_fold','alternative_fold_goals','meal_end_return_diagnostic'):print(k,str(v)[:400])
  elif k in ('events','expanded_strokes','expanded_connections'):print(k,len(v),str(v[0])[:500] if v else '')
  elif k not in ('q','robot_parts','initial_state','executed_state'):print(k,str(v)[:120])
for i in (0,1,2,40,70):
 d=read(f'connections_v5/L73/{i}.json');print('CONNECTION',i,d['status'])
 for l in d['legs']:
  print('LEG',l['name'],list(l), 'attached',l['state']['attached'],'planner keys',list(l['planner']))
  print('path',len(l['planner'].get('path',[])), 'last',str(l['planner'].get('last_rejection'))[:100])
print('INTERNAL RANK')
d=read('motion.json')
for r in d['internal_paths']:
 if r['ok']:print(r['index'],r['final_replay'].get('states_checked'),r['final_replay'].get('clearance_distribution',{}))
