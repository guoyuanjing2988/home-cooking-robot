"""Sequential candidate study inside one bounded foreground worker slot."""
import sys,subprocess,time,json
from pathlib import Path
layout=sys.argv[1];begin=time.monotonic();rows=[]
for script,args in [('setup_stations_v2_r07.py',[layout]),('envelope_v2_r07.py',[layout]),('reach_v2_r07.py',[layout,'R']),('reach_v2_r07.py',[layout,'L']),('carriage_barrier_v2_r07.py',[layout]),('park_v2_r07.py',[layout])]:
 remaining=1040-(time.monotonic()-begin)
 if remaining<30:break
 started=time.monotonic()
 try:r=subprocess.run([sys.executable,script,*args],timeout=remaining);status='complete' if r.returncode==0 else 'error'
 except subprocess.TimeoutExpired:status='timeout'
 rows.append(dict(script=script,args=args,status=status,elapsed_s=time.monotonic()-started));Path('audit/'+layout+'_candidate_pipeline.json').write_text(json.dumps(rows,indent=2))
 print('STEP',rows[-1],flush=True)
 if status!='complete':break
