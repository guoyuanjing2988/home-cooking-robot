import subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent
for script,args in [('solver_prepare_v7_r07.py',[]),('safety_v7_r07.py',[]),('layout_L80_v7_r07.py',[]),('layout_L81_v7_r07.py',[]),('check_state_v7_r07.py',['L74']),('door_scope_check_v7_r07.py',['L74'])]:
 subprocess.run([sys.executable,'-B',script]+args,cwd=H,timeout=120,check=True)
