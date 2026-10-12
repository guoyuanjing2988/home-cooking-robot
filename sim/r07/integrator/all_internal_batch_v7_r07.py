"""Disjoint resumable current-layout internal diagnostics, including failed statics."""
import json,sys,time,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];lane=int(sys.argv[2]);stride=int(sys.argv[3]) if len(sys.argv)>3 else 4;began=time.monotonic()
for i in range(lane,59,stride):
 target=H/'results/motion_v7'/ID/f'internal_{i}.json'
 if target.exists():continue
 d=json.loads((H/'results/static_v7'/ID/f'{i}.json').read_text());assert d['complete'] and d['starts']>=96
 if time.monotonic()-began>770:break
 args=['motion_v7_r07.py',ID,'internal',str(i)] if d.get('witness') else ['failed_internal_v7_r07.py',ID,str(i)]
 # The outer 1120s process-tree supervisor bounds this single numerical child.
 result=subprocess.run([sys.executable,'-B']+args,cwd=H)
 if result.returncode:raise SystemExit(result.returncode)
print('INTERNAL_BATCH_CHUNK',lane,round(time.monotonic()-began,2),flush=True)
