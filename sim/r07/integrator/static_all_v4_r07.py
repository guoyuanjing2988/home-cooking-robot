"""Full96-start per stroke, resumable one-worker foreground chunk."""
import sys,runpy,time,json
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];lo=int(sys.argv[2]);hi=int(sys.argv[3]);began=time.monotonic()
for index in range(lo,hi):
 remaining=1035-(time.monotonic()-began)
 if remaining<40:break
 sys.argv=['static_v4_r07.py',ID,str(index),str(index+1),str(remaining),'96','96']
 runpy.run_path(str(H/'static_v4_r07.py'),run_name='__main__')
