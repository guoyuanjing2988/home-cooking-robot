import sys,time,subprocess,json
from pathlib import Path
begin=time.monotonic();layout=sys.argv[1];rows=[]
for script in ('fold_continuation_v3_r07.py','passing_v3_r07.py','target_certificate_v2_r07.py','fixed_hardware_v2_r07.py','rules_v3_r07.py'):
 remaining=1050-(time.monotonic()-begin)
 if remaining<30:break
 started=time.monotonic()
 try:r=subprocess.run([sys.executable,'-B',script,layout],timeout=remaining);status='complete' if r.returncode==0 else 'error'
 except subprocess.TimeoutExpired:status='timeout'
 rows.append(dict(script=script,status=status,elapsed_s=time.monotonic()-started));Path(f'audit/{layout}_auxiliary_pipeline.json').write_text(json.dumps(rows,indent=2));print('AUXILIARY',rows[-1],flush=True)
 if status!='complete':break
