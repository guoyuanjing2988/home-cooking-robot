"""Readable per-edge failures; full nested witnesses remain in motion.json."""
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';m=json.loads((O/'motion.json').read_text());rows=[]
for r in m['internal']:
 if r['ok']:continue
 edges=r.get('edges',[]) or [{}]
 for j,e in enumerate(edges):
  if e.get('ok'):continue
  hits=list(e.get('blockers',[]));extra=e.get('lift_failures',[])
  if not e:
   for attempt in r.get('source_ik_attempts',[]):
    for po in attempt.get('reference',{}).get('poses',[]):hits+=po.get('forbidden',[])
  for item in extra:
   hits+=item.get('blocker',{}).get('blockers',[]) if isinstance(item.get('blocker'),dict) else []
  line=e.get('working_line_blocker',{})
  if isinstance(line,dict):hits+=line.get('blockers',[])
  pairs=list(dict.fromkeys(' / '.join(x['pair']) for x in hits if x.get('pair')))
  reasons=[e.get('reason'),r.get('reason')]+[x.get('reason') for x in extra]
  rows.append(dict(index=r['index'],stroke=r['stroke'],edge=j,status=r.get('status','FAIL'),blocker_pairs='; '.join(pairs),reason='; '.join(x for x in reasons if x),planner_s=e.get('planner_time_s',0),allocated_s=e.get('allocated_budget_s',0),starts=e.get('seeds_tried',len(r.get('source_ik_attempts',[]))),states=e.get('states_checked',len(r.get('source_ik_attempts',[]))),tried='Full-size two-arm/carriage RRT-Connect,65s search/restarts,folded via bias,shortcutting,straight<=50mm support windows,Cartesian continuation where required; recorded exact endpoint/grasp retries where applicable' if e else 'Offset-grasp source IK with final-reference rejection before path search; original template65s search also retained',source=r['source_file']))
with (O/'internal_failures.csv').open('w',newline='',encoding='utf-8') as fp:
 w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('Internal failed edges',len(rows),'failed templates',sum(not r['ok'] for r in m['internal']))
