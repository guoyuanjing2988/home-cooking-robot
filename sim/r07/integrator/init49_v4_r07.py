import json,sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';c=json.loads((O/'layouts/L47.json').read_text())
c.update(id='L49',orientation='R07_v4_L49',power_z=1.20,reason='L48 terminal certificates show full horizontal tool handles intersect staged raw food. Move full docks back toY.400m, raise entire full power track94mm relative toL47 toZ1.200m; original full track/connectors and all station sizes remain. Full fixed-scene, map and pose checks decide admission.')
for typ in ('wash_pad','eye_core_spoon'):c['station_overrides']['dock_'+typ]['new_center'][1]=.40
(O/'layouts/L49.json').write_text(json.dumps(c,indent=2))
for s in ('setup_stations_v2_r07.py','process_v4_r07.py'):subprocess.run([sys.executable,'-B',s,'L49'],check=True,timeout=30)
for suffix in ('envelope','park_full'):
 d=json.loads((O/'layouts'/f'L45_{suffix}.json').read_text());d['config']=c;(O/'layouts'/f'L49_{suffix}.json').write_text(json.dumps(d,indent=2))
log=dict(cancelled_workers=[32312,34616],reason='L47 immutable fixed-solid power/dock intersections; L48 exact terminal-food obstruction certificates. Partial search starts retained, not claimed96.',certificates=['results/layouts/L47_fixed_obstructions.json','results/layouts/L48_target_certificates.json'])
(H/'audit/v4_L47_L48_certified_cancellation.json').write_text(json.dumps(log,indent=2))
