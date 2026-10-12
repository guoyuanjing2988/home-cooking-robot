"""Literal search blockers, without turning finite numerical failures into proofs."""
import sys,json,collections
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';ID=sys.argv[1];rows=[]
for file in sorted((O/'static_v2'/ID).glob('*.json'),key=lambda p:int(p.stem)):
 r=json.loads(file.read_text());pairs=collections.Counter()
 for start in r['rows']:
  pairs.update(tuple(b['pair']) for b in start.get('blockers',[]))
 b=r.get('best_failed') or {}
 rows.append(dict(index=r['index'],stroke=r['stroke'],pass_=bool(r.get('witness')),starts=r['starts'],budget_complete=r['starts']>=96,allocated_s_per_unresolved_start=20,actual_recorded_search_s=sum(x['elapsed_s'] for x in r['rows']),best_failed_errors=b.get('errors'),best_failed_hits=b.get('hits'),most_frequent_pairs=[dict(pair=list(p),starts_with_pair=n) for p,n in pairs.most_common(8)],source=str(file.relative_to(H)).replace('\\','/'),claim='A finite search record, not a geometric impossibility certificate.'))
out=dict(layout=ID,rows=rows,critical_cases=[r for r in rows if r['index'] in (2,14)],scope='All105 selected-layout records. Exact target/fixed obstruction certificates are separate files. A passing row does not imply an internal path or conserved meal.')
(O/'failure_evidence_v3.json').write_text(json.dumps(out,indent=2));print('FAILURE_EVIDENCE',ID,len(rows),sum(r['budget_complete'] for r in rows))
