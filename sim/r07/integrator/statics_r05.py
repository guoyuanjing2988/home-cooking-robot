import json,time,copy,hashlib
import final_check as f
s=f.s;H=s.HERE;O=H/'results';begin=time.monotonic()
old=json.loads((H/'upstream_r04/results/best.json').read_text());witnesses={};rows=[]
for ph in s.P['phases']:
 for sg in ph['segments']:
  key=ph['id']+'__'+sg['label'].replace(' ','_');ch=s.Checker(ph,sg)
  result=f.replay(ch,old['witnesses'][key]);row=dict(id=key,phase=ph['id'],logical=ph['id'].split('.')[0],ok=result['ok'],replayed_candidates=1)
  if result['ok']:witnesses[key]=dict(phase=ph['id'],label=sg['label'],**result)
  else:row['blockers']=[p['forbidden'] for p in result['poses']]
  rows.append(row);print(key,result['ok'],round(time.monotonic()-begin,1),flush=True)
logical=[dict(id=f'Q{i:02}',ok=all(r['ok'] for r in rows if r['logical']==f'Q{i:02}')) for i in range(1,28)]
out=dict(schema='r05.reference_static_replay',logical_passed=sum(r['ok'] for r in logical),logical_total=27,strokes_passed=len(witnesses),strokes_total=len(rows),poses_verified=sum(len(w['poses']) for w in witnesses.values()),logical_phases=logical,rows=rows,seeds_tried=0,archived_starts=10272,archived_solver_solutions=2324,verified_witnesses=len(witnesses),wall_rule='Only named rear +Y mating faces of wall_mount_-1.84 and wall_mount_0.18. Connector and power tabs moved 12mm forward, full sizes retained.',acceptance=s.P['acceptance'],elapsed_s=time.monotonic()-begin)
f.write('phase_summary.json',out);f.write('static_all.json',dict(rows=rows,witnesses=witnesses));f.write('best.json',dict(old,witnesses=witnesses,stage='R05',phases_passed=out['logical_passed'],overall_pass=False))
print('STATIC',out['logical_passed'],len(witnesses),flush=True)
