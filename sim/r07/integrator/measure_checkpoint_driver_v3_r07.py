"""Retain measured fields across the later final count aggregation."""
import sys,json,runpy,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';ID=sys.argv[1]
try:runpy.run_path(str(H/'measure_checkpoint_v3_r07.py'))
except SystemExit as e:
 if e.code not in (None,0):raise
s=json.loads((O/'schedule.json').read_text())
fields={k:s[k] for k in ('accepted_internal_paths','isolated_internal_duration_sum_s','timing_method')}
paths={str(p.relative_to(H)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/'motion_v2'/ID).glob('internal_*.json')}
(O/'measured_paths_v3.json').write_text(json.dumps(dict(layout=ID,schedule_fields=fields,path_hashes=paths),indent=2))
print('MEASURED_CHECKPOINT',ID,len(fields['accepted_internal_paths']),flush=True)
