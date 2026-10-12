import subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;began=time.monotonic()
for script,args in [('layout_L101_v7_r07.py',[]),('band_pair_certificate_v7_r07.py',['L99']),('band_pair_certificate_v7_r07.py',['L101']),('screen_v7_r07.py',['L101']),('dock_packing_v7_r07.py',['L101']),('headroom_v7_r07.py',['L101']),('bail_geometry_v7_r07.py',['L101']),('study_v7_r07.py',['L101'])]:
 subprocess.run([sys.executable,'-B',script]+args,cwd=H,timeout=max(1,1060-(time.monotonic()-began)),check=True)
