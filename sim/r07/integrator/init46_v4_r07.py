import json,sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';c=json.loads((O/'layouts/L45.json').read_text())
c.update(id='L46',orientation='R07_v4_L46',power_z=1.106,reason='L45 tool-pick searches reach exact targets only through BFP/upper-cabinet obstructions. Move full wash-pad and eye/core docks from behind tall processor to open left rear corridor above low raw/finishing supports. Move whole power track/adapter6mm upward to gain21mm from socket-access envelope. Preserve full fixtures and named contact frames.')
c['station_overrides']['dock_wash_pad']={'new_center':[-.99,.36,0]};c['station_overrides']['dock_eye_core_spoon']={'new_center':[-.78,.385,0]}
(O/'layouts/L46.json').write_text(json.dumps(c,indent=2))
for s in ('setup_stations_v2_r07.py','process_v4_r07.py'):subprocess.run([sys.executable,'-B',s,'L46'],check=True,timeout=30)
for suffix in ('envelope','park_full'):
 d=json.loads((O/'layouts'/f'L45_{suffix}.json').read_text());d['config']=c;(O/'layouts'/f'L46_{suffix}.json').write_text(json.dumps(d,indent=2))
print('L46 open tool corridor and power clearance')
