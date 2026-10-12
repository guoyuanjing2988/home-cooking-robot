"""Disjoint resumable lanes, with deployment/return witnesses first."""
import json,sys,time,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];lane=int(sys.argv[2]);stride=int(sys.argv[3]);began=time.monotonic()
order=[0,58,49,12,13,30,31,10,15,28,34,43,46,53,33]+[i for i in range(59) if i not in (0,58,49,12,13,30,31,10,15,28,34,43,46,53,33)]
for i in order[lane::stride]:
 file=H/'results/static_v7'/ID/f'{i}.json';d=json.loads(file.read_text()) if file.exists() else dict(starts=0,complete=False)
 if d.get('complete') and d['starts']>=96:continue
 remain=1040-(time.monotonic()-began)
 if remain<45:break
 r=subprocess.run([sys.executable,'-B','static_v7_r07.py',ID,str(i),str(i+1),str(remain),'96','96'],cwd=H)
 if r.returncode==75:continue
 if r.returncode:raise SystemExit(r.returncode)
print('STATIC_LANE_CHUNK',lane,round(time.monotonic()-began,2))
