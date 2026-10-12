"""Complete96 independent local starts on already-admitted branches."""
import sys,json,time,runpy
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];lo,hi=map(int,sys.argv[2:4]);budget=float(sys.argv[4]) if len(sys.argv)>4 else 1020;skip=set(map(int,sys.argv[5:]));begin=time.monotonic()
for i in range(lo,hi):
 if i in skip:continue
 f=H/'results/static_v2'/ID/f'{i}.json'
 if not f.exists():continue
 r=json.loads(f.read_text())
 if not r.get('witness') or r['starts']>=96:continue
 remaining=budget-(time.monotonic()-begin)
 if remaining<30:break
 sys.argv=['static_v2_r07.py',ID,str(i),str(i+1),str(remaining),'96','96'];runpy.run_path(str(H/'static_v2_r07.py'))
print('POSITIVE_BUDGET_CHUNK',ID,lo,hi,time.monotonic()-begin,flush=True)
