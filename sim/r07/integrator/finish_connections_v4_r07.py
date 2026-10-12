import sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1]
commands=[['motion_batch_v4_r07.py',ID],['connections_v4_r07.py',ID,*map(str,[15,16,17,18,19,35,36,37,38,39,55,56,57])],['rebase_connections_v4_r07.py',ID]]
for args in commands:subprocess.run([sys.executable,'-B',*args],cwd=H,check=True,timeout=1000)
