"""Plan only the frozen 96-start prefix while later static searches continue."""
import os,sys,json,subprocess,time
from pathlib import Path
ID=sys.argv[1];os.environ['R07_LAYOUT']=ID
H=Path(__file__).resolve().parent;O=H/'results';began=time.monotonic()
import persistent_v6_r07 as p
rows=p.expanded();limit=0
for i,entry in enumerate(rows):
 d=json.loads((O/'static_v6'/ID/f"{entry['index']}.json").read_text())
 if not d.get('complete'):break
 limit=i
bundle=O/'meal_pose_proposals_v6'/f'{ID}.json'
try:bundle_complete=json.loads(bundle.read_text()).get('complete',False)
except (OSError,ValueError):bundle_complete=False
if not bundle_complete:
 result=subprocess.run([sys.executable,'-B','meal_poses_v6_r07.py',ID],timeout=400)
 if result.returncode:raise SystemExit(result.returncode)
indices=[str(i) for i in range(limit) if not (O/'connections_v6'/ID/f'{i}.json').exists()]
print('FROZEN_PREFIX_CONNECTIONS',indices,flush=True)
if indices:
 subprocess.run([sys.executable,'-B','connections_v6_r07.py',ID]+indices,timeout=max(1,1060-(time.monotonic()-began)))
