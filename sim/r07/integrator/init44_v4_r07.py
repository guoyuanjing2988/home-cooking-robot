import json,sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';c=json.loads((O/'layouts/L43.json').read_text())
c.update(id='L44',orientation='R07_v4_L44',beam_y=.55,tie_y=.546,bracket_thickness=.020,chain_centres_z=[1.2855,1.3255],reason='L43 first admitted static exposes fixed wall-tie1mm reserve and base/chain7.475mm reserve. Translate whole beam5mm forward, whole ties9mm forward, grow bracket18->20mm to mate tie rear face without a structural gap, raise single full chain5mm. No part shrunk; same named wall mating faces. One full principal and no helper.')
(O/'layouts/L44.json').write_text(json.dumps(c,indent=2))
for s in ('setup_stations_v2_r07.py','process_v4_r07.py'):subprocess.run([sys.executable,'-B',s,'L44'],check=True,timeout=30)
for suffix in ('envelope','park_full'):
 d=json.loads((O/'layouts'/f'L43_{suffix}.json').read_text());d['config']=c;(O/'layouts'/f'L44_{suffix}.json').write_text(json.dumps(d,indent=2))
print('L44 fixed hardware reserves improved with whole-solid translations and thicker brackets')
