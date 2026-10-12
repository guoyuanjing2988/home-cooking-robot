import json,sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';c=json.loads((O/'layouts/L47.json').read_text())
c.update(id='L48',orientation='R07_v4_L48',reason='L47 full checker exposes fixed horizontal dock posts intersecting power track. Translate both COMPLETE rotated tool docks140mm toward counter front; preserve all original solids and stand dimensions. No clearance exemption. New full-scene certificates and96-start searches decide admission.')
for typ in ('wash_pad','eye_core_spoon'):c['station_overrides']['dock_'+typ]['new_center'][1]=.28
(O/'layouts/L48.json').write_text(json.dumps(c,indent=2))
for s in ('setup_stations_v2_r07.py','process_v4_r07.py'):subprocess.run([sys.executable,'-B',s,'L48'],check=True,timeout=30)
for suffix in ('envelope','park_full'):
 d=json.loads((O/'layouts'/f'L45_{suffix}.json').read_text());d['config']=c;(O/'layouts'/f'L48_{suffix}.json').write_text(json.dumps(d,indent=2))
