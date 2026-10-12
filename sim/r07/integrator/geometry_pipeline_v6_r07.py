import sys,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];start=time.monotonic()
jobs=[['maps_refresh_v6_r07.py',ID],['check_state_v6_r07.py',ID],['aux_v6_r07.py',ID],['fold_v6_r07.py',ID]]
for job in jobs:
 remain=1060-(time.monotonic()-start)
 if remain<80:break
 try:result=subprocess.run([sys.executable,'-B']+job,timeout=remain)
 except subprocess.TimeoutExpired:break
 if result.returncode:raise SystemExit(result.returncode)
