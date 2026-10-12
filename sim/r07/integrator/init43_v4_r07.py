"""Correct fixed bowl/dock to bracket gaps found by fresh full-scene statics."""
import sys,json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results'
c=json.loads((O/'layouts/L42.json').read_text());c.update(id='L43',orientation='R07_v4_L43',reason='L42 static water standby exposes fixed output-land/bracket8mm gaps and eye-tool-post/bracket overlap. Move full bowls27mm forward and full tool docks85mm forward; keep all full sizes. One full UR5e and guarded small-peeler reservation; no helper/regrasp indexing.')
for prod in ('carrot','potato','leafy_greens','tomato'):c['station_overrides']['output_'+prod]['new_center'][1]=.46
c['station_overrides']['dock_wash_pad']['new_center'][1]=.40;c['station_overrides']['dock_eye_core_spoon']['new_center'][1]=.40
(O/'layouts/L43.json').write_text(json.dumps(c,indent=2))
for s in ('setup_stations_v2_r07.py','process_v4_r07.py'):subprocess.run([sys.executable,'-B',s,'L43'],check=True,timeout=30)
for suffix in ('envelope','park_full'):
 d=json.loads((O/'layouts'/f'L42_{suffix}.json').read_text());d['config']=c;(O/'layouts'/f'L43_{suffix}.json').write_text(json.dumps(d,indent=2))
print('L43 fixture correction created')
