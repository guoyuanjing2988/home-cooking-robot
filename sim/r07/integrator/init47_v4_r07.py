import json,sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';c=json.loads((O/'layouts/L46.json').read_text())
c.update(id='L47',orientation='R07_v4_L47',horizontal_tool_docks=True,reason='L46 upright tool acquisition still needs wrist height in cabinet/chain. Rotate each COMPLETE dock and stored tool90deg aboutX, making face normal-Y and robot horizontal pickup; add full240mm upright stand/90mm foot to support the rotated assembly. All original solids, offsets and own contact identities retained. Proper local-face normal and straight insertion checks replace world-Z-only dock assumption; gates unchanged.')
for typ in ('wash_pad','eye_core_spoon'):c['station_overrides']['dock_'+typ]['new_center'][1]=.42
(O/'layouts/L47.json').write_text(json.dumps(c,indent=2))
for s in ('setup_stations_v2_r07.py','process_v4_r07.py'):subprocess.run([sys.executable,'-B',s,'L47'],check=True,timeout=30)
for suffix in ('envelope','park_full'):
 d=json.loads((O/'layouts'/f'L46_{suffix}.json').read_text());d['config']=c;(O/'layouts'/f'L47_{suffix}.json').write_text(json.dumps(d,indent=2))
print('L47 complete horizontal tool-dock assemblies')
