import subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;began=time.monotonic()
for script,args in [('layout_L98_v7_r07.py',[]),('dock_packing_v7_r07.py',['L98']),('headroom_v7_r07.py',['L98']),('screen_v7_r07.py',['L98']),('bail_geometry_v7_r07.py',['L98']),('study_v7_r07.py',['L98'])]:
 subprocess.run([sys.executable,'-B',script]+args,cwd=H,timeout=max(1,1060-(time.monotonic()-began)),check=True)
