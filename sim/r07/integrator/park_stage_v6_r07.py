"""Refresh current regressions, search alternative parks, refresh a passing goal."""
import subprocess,sys,time,json
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];began=time.monotonic()
for args in [['door_scope_check_v6_r07.py',ID],['check_state_v6_r07.py',ID],['fold_alternatives_v6_r07.py',ID]]:
 result=subprocess.run([sys.executable,'-B']+args,cwd=H,timeout=max(1,1060-(time.monotonic()-began)))
 if result.returncode:raise SystemExit(result.returncode)
result=json.loads((H/'results/layouts'/f'{ID}_fold_alternatives_v6.json').read_text())
if result['pass_']:
 subprocess.run([sys.executable,'-B','aux_v6_r07.py',ID,'--reuse-park'],cwd=H,check=True,timeout=max(1,1060-(time.monotonic()-began)))
