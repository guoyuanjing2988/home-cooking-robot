import json,sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';c=json.loads((O/'layouts/L50.json').read_text())
c.update(id='L51',orientation='R07_v4_L51',reason='L50 exact full post bounds reachY.550m andZ1.180m:1mm from power track frontY.551, below10mm gate. Move each complete raised horizontal assembly40mm forward toY.360m; post rearY.510 gives41mm power clearance. Food-overlap repair80mm lift retained; gates and full geometries unchanged.')
for typ in ('wash_pad','eye_core_spoon'):c['station_overrides']['dock_'+typ]['new_center'][1]=.36
(O/'layouts/L51.json').write_text(json.dumps(c,indent=2))
for s in ('setup_stations_v2_r07.py','process_v4_r07.py'):subprocess.run([sys.executable,'-B',s,'L51'],check=True,timeout=30)
for suffix in ('envelope','park_full'):
 d=json.loads((O/'layouts'/f'L45_{suffix}.json').read_text());d['config']=c;(O/'layouts'/f'L51_{suffix}.json').write_text(json.dumps(d,indent=2))
