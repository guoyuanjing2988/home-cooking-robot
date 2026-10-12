"""One numerical worker consumes unclaimed incomplete source problems."""
import json,sys,time,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];excluded=set(map(int,sys.argv[2:]));began=time.monotonic();order=[]
for i in range(59):
 try:d=json.loads((H/'results/static_v6'/ID/f'{i}.json').read_text())
 except (json.JSONDecodeError,OSError):continue
 # Start the largest unresolved problems first to avoid one late straggler.
 order.append(((bool(d.get('witness')),-(96-d['starts']),-i),i))
for _,i in sorted(order):
 if i in excluded:continue
 f=H/'results/static_v6'/ID/f'{i}.json'
 try:d=json.loads(f.read_text())
 except (json.JSONDecodeError,OSError):continue # A pre-lock legacy worker may be writing; revisit next chunk.
 if d['complete'] and d['starts']>=96:continue
 remain=1040-(time.monotonic()-began)
 if remain<45:break
 result=subprocess.run([sys.executable,'-B','static_v6_r07.py',ID,str(i),str(i+1),str(remain),'96','96'],cwd=H)
 if result.returncode==75:continue
 if result.returncode:raise SystemExit(result.returncode)
print('STATIC_QUEUE_CHUNK',ID,round(time.monotonic()-began,2),'excluded pre-lock workers',sorted(excluded),flush=True)
