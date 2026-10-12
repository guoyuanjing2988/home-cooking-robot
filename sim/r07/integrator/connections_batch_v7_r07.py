"""Resume a disjoint stride of actual connection searches in one bounded chunk."""
import sys,subprocess,json
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];lane=int(sys.argv[2]);stride=int(sys.argv[3]) if len(sys.argv)>3 else 4
bundle=json.loads((H/'results/meal_pose_proposals_v7'/f'{ID}.json').read_text());assert bundle['complete'];count=len(bundle['records'])-1
indices=[i for i in range(lane,count,stride) if not (H/'results/connections_v7'/ID/f'{i}.json').exists()]
if indices:
 print('CONNECTION_BATCH',lane,'pending',len(indices),flush=True)
 result=subprocess.run([sys.executable,'-B','connections_v7_r07.py',ID]+list(map(str,indices)),timeout=1060)
 raise SystemExit(result.returncode)
print('CONNECTION_BATCH_COMPLETE',lane)
