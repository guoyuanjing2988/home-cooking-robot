"""Late candidate fold and96-start completion in one foreground worker slot."""
import sys,subprocess,time,json
from pathlib import Path
start=time.monotonic();rows=[]
jobs=[('idle_v2_r07.py',['L19','--snapshot-only']),('idle_working_v2_r07.py',['L19','0','--refine']),('static_v2_r07.py',['L18','0','1','250','96']),('static_v2_r07.py',['L13','14','15','200','96'])]
for script,args in jobs:
 left=1040-(time.monotonic()-start)
 if left<45:break
 t=time.monotonic();p=subprocess.run([sys.executable,script,*args],timeout=left)
 rows.append(dict(script=script,args=args,exit_code=p.returncode,elapsed_s=time.monotonic()-t));Path('audit/late_validation_pipeline.json').write_text(json.dumps(rows,indent=2));print('LATE_STEP',rows[-1],flush=True)
 if p.returncode:raise RuntimeError(script)
