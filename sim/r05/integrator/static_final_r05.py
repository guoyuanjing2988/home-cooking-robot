import sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent
for seconds,name,script in [(300,'static_final','statics_r05.py'),(120,'validation_final','validate_r05.py')]:
 code=subprocess.call([sys.executable,'-B',str(H/'bounded.py'),str(seconds),name,sys.executable,'-B',str(H/script)])
 if code:raise SystemExit(code)
