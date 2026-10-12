"""Fresh scope/transaction checks and layout-specific negative certificates."""
import subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;began=time.monotonic();ID=sys.argv[1]
jobs=[['door_scope_check_v7_r07.py',ID],['check_state_v7_r07.py',ID],['safety_v7_r07.py'],['certificates_batch_v7_r07.py']+sys.argv[1:]]
for args in jobs:
 remain=1040-(time.monotonic()-began)
 result=subprocess.run([sys.executable,'-B']+args,timeout=max(1,remain),cwd=H)
 if result.returncode:raise SystemExit(result.returncode)
