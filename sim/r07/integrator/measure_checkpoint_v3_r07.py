"""Measure immutable completed path records while independent IK budgets finish."""
import sys,json,runpy,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';ID=sys.argv[1]
(O/'passing.json').write_bytes((O/f'motion_v2/{ID}/passing.json').read_bytes())
runpy.run_path(str(H/'measure_export_v3_r07.py'))
# The internal export exits after executing its derivative. This script is
# invoked with a SystemExit catch by the driver below when needed.
