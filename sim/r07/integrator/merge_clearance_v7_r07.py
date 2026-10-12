"""Merge disjoint full-state clearance refinements without changing any bound."""
import sys,json,hashlib
from pathlib import Path
import numpy as np
H=Path(__file__).resolve().parent;O=H/'results';ID=sys.argv[1];parts=[json.loads((O/f'clearance_refinement_v7_lane{i}.json').read_text()) for i in range(4)]
assert all(d['layout']==ID and d['complete'] and d['stride']==4 and d['lane']==i for i,d in enumerate(parts))
sources={}
for d in parts:
 for name,digest in d['source_hashes'].items():
  assert name not in sources or sources[name]==digest
  assert hashlib.sha256((H/name).read_bytes()).hexdigest()==digest
  sources[name]=digest
rows=[r for d in parts for r in d['rows']];rows.sort(key=lambda r:(r['kind'],r['index'],r['state']));assert len(rows)==len({(r['kind'],r['index'],r['state']) for r in rows})
counts={kind:sum(r['kind']==kind for r in rows) for kind in ('static','path')};fresh=json.loads((O/'fresh_admission.json').read_text());motion=[json.loads(f.read_text()) for f in (O/'motion_v7'/ID).glob('internal_*.json')]
expected=dict(static=sum(len(r['reference']['poses']) for r in fresh['rows'] if r['ok']),path=sum(r['final_replay']['states_checked'] for r in motion if r['ok']));assert counts==expected
stats={}
for r in rows:
 for category,value in r['minima'].items():stats.setdefault(r['kind'],{}).setdefault(category,[]).append(value['reserve_mm'])
distribution={kind:{cat:dict(samples=len(x),min_mm=min(x),p05_mm=float(np.percentile(x,5)),median_mm=float(np.median(x)),p95_mm=float(np.percentile(x,95)),max_mm=max(x),fraction_at_least10mm=float(np.mean(np.round(np.array(x),9)>=10))) for cat,x in categories.items()} for kind,categories in stats.items()}
out=dict(layout=ID,complete=True,counts=counts,distribution=distribution,rows=rows,method=parts[0]['method'],source_hashes=sources,expected_counts=expected,total_elapsed_s=sum(d['total_elapsed_s'] for d in parts),parallel_lanes=[dict(lane=d['lane'],counts=d['counts'],chunks_s=d['chunks_s']) for d in parts],scope='Four disjoint template-index lanes; every original eligible state is included exactly once. Parallelization changes no geometry, gate, distance method or reporting population.')
(O/'clearance_refinement_v7.json').write_text(json.dumps(out,indent=2,allow_nan=False));print('MERGED_CLEARANCE',counts,distribution,flush=True)
