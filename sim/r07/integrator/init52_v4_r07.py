import json,sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';c=json.loads((O/'layouts/L51.json').read_text())
c.update(id='L52',orientation='R07_v4_L52',height=1.170,reason='L51 admitted poses are capped at6mm extra by a complete stored bowl16mm from wall bracket; carriage has17.5mm cabinet/door gap. Move all full bowls8mm forward toY.452m and lower complete principal mount5mm toZ1.170m, targeting24mm bowl/bracket and22.5mm carriage/cabinet gaps. Full dimensions retained; new map,96-start admission, parking and motion replay required.')
for prod in ('carrot','potato','leafy_greens','tomato'):
 c['station_overrides']['output_'+prod]['new_center'][1]=.452
(O/'layouts/L52.json').write_text(json.dumps(c,indent=2))
for s in ('setup_stations_v2_r07.py','process_v4_r07.py'):subprocess.run([sys.executable,'-B',s,'L52'],check=True,timeout=30)
for suffix in ('envelope','park_full'):
 d=json.loads((O/'layouts'/f'L51_{suffix}.json').read_text());d['config']=c;d['reuse_basis']='Envelope retains identical OEM inertias, payload/CoM and90deg gravity orientation; mount translation alone leaves gravity joint torque unchanged. Parkq is proposal only.';(O/'layouts'/f'L52_{suffix}.json').write_text(json.dumps(d,indent=2))
positive=[]
for f in (O/'static_v4/L51').glob('*.json'):
 d=json.loads(f.read_text())
 if d.get('complete') and d.get('witness'):positive.append(int(f.stem))
(H/'audit/L52_prior_positive.json').write_text(json.dumps(sorted(positive)))
