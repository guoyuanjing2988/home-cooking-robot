import subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;began=time.monotonic()
for script,args in [('layout_L99_v7_r07.py',[]),('screen_v7_r07.py',['L99']),('dock_packing_v7_r07.py',['L99']),('headroom_v7_r07.py',['L99']),('study_v7_r07.py',['L99'])]:
 subprocess.run([sys.executable,'-B',script]+args,cwd=H,timeout=max(1,1060-(time.monotonic()-began)),check=True)
