import sys,time,subprocess,json
from pathlib import Path
H=Path(__file__).resolve().parent;start=time.monotonic()
for ID in sys.argv[1:]:
 for i in (35,47,52,54):
  remain=1040-(time.monotonic()-start)
  if remain<40:raise SystemExit('Chunk complete; queue resumable')
  subprocess.run([sys.executable,'-B','static_v7_r07.py',ID,str(i),str(i+1),str(remain),'96','96'],check=True,timeout=remain+10)
