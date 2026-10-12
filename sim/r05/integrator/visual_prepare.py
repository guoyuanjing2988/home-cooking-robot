import subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
for script,args,seconds in [('idle_r05.py',['--repair'],240),('renders_r05.py',[],120)]:
 p=subprocess.run([sys.executable,'-B','-u',str(H/script)]+args,timeout=seconds)
 if p.returncode:raise SystemExit(p.returncode)
