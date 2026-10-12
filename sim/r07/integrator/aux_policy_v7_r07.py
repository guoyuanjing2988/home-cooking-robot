import subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];began=time.monotonic()
for script,args in [('archive_render_history_v7_r07.py',['v1']),('grasp_identity_v7_r07.py',[ID]),('check_state_v7_r07.py',[ID]),('safety_v7_r07.py',[]),('aux_v7_r07.py',[ID]),('counter_v7_r07.py',[ID]),('plot_maps_v7_r07.py',[ID])]:
 subprocess.run([sys.executable,'-B',script]+args,cwd=H,timeout=max(1,1060-(time.monotonic()-began)),check=True)
