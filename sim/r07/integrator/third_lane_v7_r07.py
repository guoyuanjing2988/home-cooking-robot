import subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
for args in [['band_pair_certificate_v7_r07.py','L99'],['band_pair_certificate_v7_r07.py','L101'],['static_lane_v7_r07.py','L101','2','3']]:
 subprocess.run([sys.executable,'-B']+args,cwd=H,check=True,timeout=1060)
