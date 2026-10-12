import sys,json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';c=json.loads((O/'layouts/L44.json').read_text())
c.update(id='L45',orientation='R07_v4_L45',staged_food_matches_lands=True,reason='L44 wall/chain clearance improvement retained. Reconcile every inactive raw vegetable center to its actual relocated named land; previous exploratory fixtures had stale staged-food XY. Source solids unchanged, fresh exact-scene statics required; no inherited pass credit.')
(O/'layouts/L45.json').write_text(json.dumps(c,indent=2))
for s in ('setup_stations_v2_r07.py','process_v4_r07.py'):subprocess.run([sys.executable,'-B',s,'L45'],check=True,timeout=30)
for suffix in ('envelope','park_full'):
 d=json.loads((O/'layouts'/f'L44_{suffix}.json').read_text());d['config']=c;(O/'layouts'/f'L45_{suffix}.json').write_text(json.dumps(d,indent=2))
print('L45 full food/support coordinates reconciled')
