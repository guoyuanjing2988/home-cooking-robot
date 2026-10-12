import json,sys,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];start=time.monotonic()
for p in sorted((H/'results/static_v4'/ID).glob('*.json'),key=lambda p:int(p.stem)):
 d=json.loads(p.read_text());target=H/'results/motion_v4'/ID/('internal_'+p.stem+'.json')
 if not(d.get('witness') and d.get('complete')) or target.exists():continue
 remain=1060-(time.monotonic()-start)
 if remain<80:break
 try:r=subprocess.run([sys.executable,'-B','motion_v4_r07.py',ID,'internal',p.stem],timeout=remain)
 except subprocess.TimeoutExpired:break
 if r.returncode:break
