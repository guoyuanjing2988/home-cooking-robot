"""Sequential admitted internal paths, each retains actual planner evidence."""
import sys,json,time,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];lo,hi=map(int,sys.argv[2:4]);begin=time.monotonic();rows=[]
for i in range(lo,hi):
 file=H/'results/static_v2'/ID/f'{i}.json'
 if not file.exists() or not json.loads(file.read_text()).get('witness'):continue
 destination=H/'results/motion_v2'/ID/f'internal_{i}.json'
 if destination.exists():continue
 remaining=1020-(time.monotonic()-begin)
 if remaining<90:break
 start=time.monotonic()
 try:r=subprocess.run([sys.executable,'-B','motion_v2_r07.py',ID,'internal',str(i)],timeout=remaining);status='complete' if r.returncode==0 else 'error'
 except subprocess.TimeoutExpired:status='timeout'
 rows.append(dict(index=i,status=status,elapsed_s=time.monotonic()-start));(H/'audit'/f'{ID}_motion_batch_{lo}_{hi}.json').write_text(json.dumps(rows,indent=2));print('MOTION_BATCH',rows[-1],flush=True)
 if status!='complete':break
