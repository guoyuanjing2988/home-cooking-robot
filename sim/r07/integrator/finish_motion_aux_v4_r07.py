import sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1]
for script in ('rebase_connections_v4_r07.py','fold_staged_v4_r07.py','motion_batch_v4_r07.py'):
 subprocess.run([sys.executable,'-B',str(H/script),ID],check=True,timeout=1000)
