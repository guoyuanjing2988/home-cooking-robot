"""Freeze final static and expanded-pose evidence after all source workers exit."""
import sys,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];began=time.monotonic()
for args in [['failed_refresh_v6_r07.py',ID],['fresh_v6_r07.py',ID],['meal_poses_v6_r07.py',ID]]:
 result=subprocess.run([sys.executable,'-B']+args,timeout=max(1,1040-(time.monotonic()-began)))
 if result.returncode:raise SystemExit(result.returncode)
