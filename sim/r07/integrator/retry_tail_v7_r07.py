"""Sequential final internal-path retries inside one bounded worker slot."""
import sys,json,time,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];began=time.monotonic()
subprocess.run([sys.executable,'-B','preflight_v7_r07.py'],cwd=H,timeout=30,check=True)
for index in (21,29):
 row=json.loads((H/'results/motion_v7'/ID/f'internal_{index}.json').read_text())
 if row['ok'] or row.get('retry_policy'):continue
 remaining=1040-(time.monotonic()-began)
 if remaining<400:print('RETRY_TAIL_DEFERRED',index,flush=True);break
 subprocess.run([sys.executable,'-B','retry_internal_v7_r07.py',ID,str(index)],cwd=H,timeout=remaining,check=True)
print('RETRY_TAIL_CHUNK',round(time.monotonic()-began,2),flush=True)
