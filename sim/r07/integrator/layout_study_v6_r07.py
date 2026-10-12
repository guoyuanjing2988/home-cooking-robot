import sys,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];start=time.monotonic()
for script,args in [('screen_v6_r07.py',[]),('aux_v6_r07.py',['--reuse-park']),('fold_v6_r07.py',['--short-study'])]:
 subprocess.run([sys.executable,'-B',script,ID]+args,cwd=H,timeout=max(30,1060-(time.monotonic()-start)),check=True)
