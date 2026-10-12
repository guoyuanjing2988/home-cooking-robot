"""Fair resumable starts: collect staging seeds before repeatedly hard targets.
All admitted strokes still require96 real starts and full reference replay.
"""
import sys,time,json,runpy
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];queue=list(map(int,sys.argv[2:]));start=time.monotonic()
while time.monotonic()-start<1005:
 pending=[]
 for i in queue:
  file=H/'results/static_v6'/ID/f'{i}.json';d=json.loads(file.read_text()) if file.exists() else {}
  if d.get('starts',0)<96:pending.append((i,d))
 if not pending:break
 for i,d in pending:
  remain=1040-(time.monotonic()-start)
  if remain<40:raise SystemExit('Resumable fair chunk ended')
  sys.argv=['static_v6_r07.py',ID,str(i),str(i+1),str(remain),'96','96' if d.get('witness') else '8'];runpy.run_path(str(H/'static_v6_r07.py'),run_name='__main__')
