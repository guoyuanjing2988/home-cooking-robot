import json,sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';c=json.loads((O/'layouts/L52.json').read_text())
c.update(id='L53',orientation='R07_v4_L53',rail_centres_z=[1.285,1.29],power_z=1.195,reason='L52 margin histogram identifies19/66 admitted poses limited by17.5mm carriage/cabinet gap: lowering arm mount alone did NOT lower the rail-fixed carriage top. Lower full active rail/carriage/ties5mm and full power track5mm; full wall anchor plates stay centeredZ1.100m. Keep arm mountZ1.170m, chain and station solids. Actual compiled carriage top1.3275m gives22.5mm cabinet gap. Recompute full map/static/park/path admissions; L52 successes remain proposals only.')
(O/'layouts/L53.json').write_text(json.dumps(c,indent=2))
for s in ('setup_stations_v2_r07.py','process_v4_r07.py'):subprocess.run([sys.executable,'-B',s,'L53'],check=True,timeout=30)
for suffix in ('envelope','park_full'):
 d=json.loads((O/'layouts'/f'L52_{suffix}.json').read_text());d['config']=c;d['reuse_basis']='Unchanged full principal arm, mounting rotation and3kg+EOAT payload gravity envelope; rail position does not change joint gravity envelope. Parkq is proposal only.';(O/'layouts'/f'L53_{suffix}.json').write_text(json.dumps(d,indent=2))
positive=[]
for f in (O/'static_v4/L52').glob('*.json'):
 d=json.loads(f.read_text())
 if d.get('complete') and d.get('witness'):positive.append(int(f.stem))
(H/'audit/L53_prior_positive.json').write_text(json.dumps(sorted(positive)))
