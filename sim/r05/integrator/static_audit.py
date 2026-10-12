"""Re-score archived starts on current geometry; fresh searches stay separate."""
import json,copy,sys,time
import final_check as f
s=f.s;H=s.HERE;O=H/'results';beg=time.monotonic();rows=[];witnesses={};fresh=O/'repair/strokes'
ids=sys.argv[1:]
for ph in s.P['phases']:
 if ids and ph['id'] not in ids:continue
 for sg in ph['segments']:
  key=ph['id']+'__'+sg['label'].replace(' ','_');path=fresh/(key+'.json')
  for stage in ['repair3','repair4','repair5','repair6']:
   candidate=O/stage/'strokes'/(key+'.json')
   if candidate.exists():path=candidate
  if not path.exists():path=H/'baseline/strokes'/(key+'.json')
  raw=json.loads(path.read_text());ch=s.Checker(ph,sg);pool=[raw['best']]+[r for r in raw['rows'] if r.get('ok') and r['k']!=raw['best']['k']]
  checked=[];accepted=None
  # Reverify alternatives if geometry invalidates the selected archived start.
  for r0 in pool[:16]:
   r=copy.deepcopy(r0)
   if 'L' not in sg['poses'][0]:
    for po in r['poses']:
     if po['q'][ch.qa['L_carriage_x']]>.045:po['q'][ch.qa['L_carriage_x']]=.045
   replay=f.replay(ch,r);checked.append(replay)
   if replay['ok']:
    accepted=replay;accepted.update(phase=ph['id'],label=sg['label']);witnesses[key]=accepted;break
  row=dict(stroke=key,phase=ph['id'],logical=ph['id'].split('.')[0],source=str(path.relative_to(H)),archived_starts=raw['starts'],solver_solutions_found=raw['solutions_found'],replayed_candidates=len(checked),verified_witnesses=int(accepted is not None),ok=accepted is not None,candidates=checked)
  rows.append(row);print(key,'PASS' if accepted else 'FAIL',len(checked),round(time.monotonic()-beg,1),flush=True)
  (O/'static_partial.json').write_text(json.dumps(dict(rows=rows,witnesses=witnesses),indent=2))
(O/('static_'+('_'.join(ids) if ids else 'all')+'.json')).write_text(json.dumps(dict(rows=rows,witnesses=witnesses),indent=2));print('done',len(rows),sum(r['ok'] for r in rows))
