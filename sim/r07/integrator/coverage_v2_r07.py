"""Resume bounded broad layout diagnosis; literal starts, never96-start credit."""
import sys,subprocess,time,json
from pathlib import Path
ID=sys.argv[1];lo=int(sys.argv[2]);hi=int(sys.argv[3]);begin=time.monotonic()
for i in range(lo,hi):
 file=Path('results/static_v2')/ID/f'{i}.json'
 if file.exists():continue
 left=990-(time.monotonic()-begin)
 if left<95:break
 r=subprocess.run([sys.executable,'static_v2_r07.py',ID,str(i),str(i+1),str(min(90,left)),'96','4'],timeout=min(110,left+15))
 if r.returncode:raise RuntimeError('static diagnostic failed')
print('COVERAGE_CHUNK',ID,lo,hi,'elapsed',time.monotonic()-begin,flush=True)
