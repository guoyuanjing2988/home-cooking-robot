import subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];began=time.monotonic()
for args in [['aux_v7_r07.py',ID],['fold_v7_r07.py',ID,'--short-study'],['fold_v7_r07.py',ID,'--unfold','--short-study']]:
 subprocess.run([sys.executable,'-B']+args,cwd=H,timeout=max(1,1060-(time.monotonic()-began)),check=True)
