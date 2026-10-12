"""Freeze final static and expanded-pose evidence after all source workers exit."""
import sys,subprocess,time,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];O=H/'results';began=time.monotonic()
def run(args):
 result=subprocess.run([sys.executable,'-B']+args,timeout=max(1,1040-(time.monotonic()-began)))
 if result.returncode:raise SystemExit(result.returncode)
files=list((H/'results/static_v7'/ID).glob('*.json'))
assert len(files)==59 and all(json.loads(f.read_text())['complete'] for f in files)
for args in [['archive_render_history_v7_r07.py','v2'],['normalize_park_v7_r07.py',ID],['aux_v7_r07.py',ID,'--reuse-park'],['counter_v7_r07.py',ID]]:run(args)
checkpoint=O/f'static_freeze_v7_{ID}.json'
if not checkpoint.exists():
 run(['failed_refresh_v7_r07.py',ID]);run(['fresh_v7_r07.py',ID])
 checkpoint.write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2))
sources=json.loads(checkpoint.read_text());assert sources=={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
bundle=O/'meal_pose_proposals_v7'/f'{ID}.json'
if not bundle.exists() or not json.loads(bundle.read_text()).get('complete'):run(['meal_poses_v7_r07.py',ID])
if not json.loads(bundle.read_text()).get('complete'):
 print('FREEZE_PARTIAL',ID,'resume expanded proposals without mutating static sources');raise SystemExit(0)
(O/f'frozen_v7_{ID}.json').write_text(json.dumps(dict(layout=ID,static_sources=sources,meal_proposals_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),scope='No static mutations after this freeze; downstream path sources must match.'),indent=2));print('FROZEN',ID,len(sources))
