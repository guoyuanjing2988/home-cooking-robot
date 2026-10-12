import json,sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';c=json.loads((O/'layouts/L49.json').read_text())
c.update(id='L50',orientation='R07_v4_L50',horizontal_dock_lift=.08,stand_forward=.04,reason='L49 certificates locate full wrist/palm against raw greens atZ1.00m. Raise both COMPLETE horizontal tool assemblies80mm toZ1.08m; grow support stands240to320mm and shift added stands/feet40mm forward to avoid power track. Original tools/docks and food dimensions unchanged. Full target and fixed-hardware checks required.')
(O/'layouts/L50.json').write_text(json.dumps(c,indent=2))
for s in ('setup_stations_v2_r07.py','process_v4_r07.py'):subprocess.run([sys.executable,'-B',s,'L50'],check=True,timeout=30)
for suffix in ('envelope','park_full'):
 d=json.loads((O/'layouts'/f'L45_{suffix}.json').read_text());d['config']=c;(O/'layouts'/f'L50_{suffix}.json').write_text(json.dumps(d,indent=2))
