import subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;began=time.monotonic()
for script,args in [('layout_L97_v7_r07.py',[]),('dock_packing_v7_r07.py',['L97']),('headroom_v7_r07.py',['L97']),('screen_v7_r07.py',['L97']),('static_v7_r07.py',['L97','0','1','100','96','96']),('static_v7_r07.py',['L97','58','59','100','96','96']),('study_v7_r07.py',['L97'])]:
 subprocess.run([sys.executable,'-B',script]+args,cwd=H,timeout=max(1,1060-(time.monotonic()-began)),check=True)
