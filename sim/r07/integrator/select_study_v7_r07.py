import subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;start=time.monotonic()
tasks=[('layout_L96_v7_r07.py',[]),('screen_v7_r07.py',['L96'])]+[(s,['L'+str(i)]) for i in range(90,97) for s in ('headroom_v7_r07.py','dock_packing_v7_r07.py')]+[('study_v7_r07.py',['L96'])]
for script,args in tasks:
 subprocess.run([sys.executable,'-B',script]+args,cwd=H,timeout=max(1,1060-(time.monotonic()-start)),check=True)
