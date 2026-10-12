"""Resumable real96-start critical stroke budget in <20-minute chunks."""
import sys,runpy,time,json
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];indices=list(map(int,sys.argv[2:])) or [0,3,4]
begin=time.monotonic()
for index in indices:
 left=1040-(time.monotonic()-begin)
 if left<35:break
 sys.argv=['static_v4_r07.py',ID,str(index),str(index+1),str(left),'96','96']
 runpy.run_path(str(H/'static_v4_r07.py'),run_name='__main__')
