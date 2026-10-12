import sys,time,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];start=time.monotonic()
if '--inherit' in sys.argv:
 subprocess.run([sys.executable,'-B','inherit_statics_v7_r07.py',ID],check=True,timeout=120)
for i in [int(x) for x in sys.argv[2:] if x!='--inherit']:
 remain=1040-(time.monotonic()-start)
 if remain<40:break
 subprocess.run([sys.executable,'-B','static_v7_r07.py',ID,str(i),str(i+1),str(remain),'96','96'],check=True,timeout=remain+10)
