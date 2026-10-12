"""Refresh completed-run counts without repeating unchanged path measurements."""
import sys,subprocess,json
from pathlib import Path
ID=sys.argv[1];O=Path('results');schedule=json.loads((O/'schedule.json').read_text());assert schedule['selected_layout']==ID
for script,args in [('fresh_admission_v2_r07.py',[ID]),('deliver_v2_r07.py',[ID])]:
 if script=='fresh_admission_v2_r07.py' and '--no-replay' in sys.argv:continue
 p=subprocess.run([sys.executable,script,*args],timeout=400)
 if p.returncode:raise RuntimeError(script)
out=json.loads((O/'schedule.json').read_text())
for key in ('accepted_internal_paths','isolated_internal_duration_sum_s','timing_method'):out[key]=schedule[key]
(O/'schedule.json').write_text(json.dumps(out,indent=2))
subprocess.run([sys.executable,'write_post_v2_r07.py'],check=True,timeout=30)
