"""Sequential, timeout-bounded preparation of reviewable final artifacts."""
import subprocess,sys,time,json
from pathlib import Path
ID=sys.argv[1];begin=time.monotonic();rows=[]
jobs=[('motion_v2_r07.py',[ID,'internal','18','20','24','26']),('motion_v2_r07.py',[ID,'passing','2']),('persistent_v2_r07.py',[ID]),('fresh_admission_v2_r07.py',[ID]),('mount_invariants_v2_r07.py',[]),('fixed_hardware_v2_r07.py',['L16']),('fixed_hardware_v2_r07.py',['L17']),('deliver_v2_r07.py',[ID]),('measure_export_v2_r07.py',[ID]),('counter_and_arm_r07.py',[ID]),('map_figure_v2_r07.py',[]),('write_post_v2_r07.py',[])]
pending=[str(i) for i in (18,20,24,26) if not (Path('results/motion_v2')/ID/f'internal_{i}.json').exists()]
if '--artifacts-only' in sys.argv:pending=[]
jobs[0]=('motion_v2_r07.py',[ID,'internal',*pending])
if (Path('results/motion_v2')/ID/'passing.json').exists():jobs.pop(1)
for script,args in jobs:
 start=time.monotonic();remaining=1020-(start-begin)
 if remaining<30:raise RuntimeError('Resume finalization in a new foreground chunk')
 p=subprocess.run([sys.executable,script,*args],timeout=remaining)
 rows.append(dict(script=script,args=args,exit_code=p.returncode,elapsed_s=time.monotonic()-start))
 Path('audit/finalization_pipeline.json').write_text(json.dumps(rows,indent=2))
 print('FINALIZE_STEP',rows[-1],flush=True)
 if p.returncode:raise RuntimeError(script+' failed')
