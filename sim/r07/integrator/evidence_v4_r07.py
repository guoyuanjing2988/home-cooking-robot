import sys,subprocess,time,json
from pathlib import Path
start=time.monotonic();rows=[]
for ID in sys.argv[1:]:
 for script in ('fixed_hardware_v2_r07.py','target_certificate_v2_r07.py'):
  remaining=1060-(time.monotonic()-start)
  if remaining<30:break
  try:r=subprocess.run([sys.executable,'-B','run_v4_r07.py',script,ID],timeout=remaining);code=r.returncode
  except subprocess.TimeoutExpired:code='timeout'
  rows.append(dict(layout=ID,script=script,code=code,elapsed_s=time.monotonic()-start))
  Path('audit/evidence_v4_'+sys.argv[1]+'.json').write_text(json.dumps(rows,indent=2))
  if code!=0:break
