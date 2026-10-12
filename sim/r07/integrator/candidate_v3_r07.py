"""Six faucet-enabled studies, each in a bounded single-worker foreground chunk."""
import sys,subprocess,time,json,os
from pathlib import Path
layout=sys.argv[1];begin=time.monotonic();rows=[]
for script,args in [('setup_stations_v2_r07.py',[layout]),('envelope_v3_r07.py',[layout]),('reach_v2_r07.py',[layout,'R']),('reach_v2_r07.py',[layout,'L']),('carriage_barrier_v2_r07.py',[layout]),('park_v2_r07.py',[layout]),('idle_v2_r07.py',[layout,'--snapshot-only'])]:
 remaining=1080-(time.monotonic()-begin)
 if remaining<30:break
 started=time.monotonic()
 try:
  env=dict(os.environ,R07_PARK_SECONDS=str(min(500,max(30,remaining-30))))
  r=subprocess.run([sys.executable,script,*args],timeout=remaining,env=env);status='complete' if r.returncode==0 else 'error'
 except subprocess.TimeoutExpired:status='timeout'
 rows.append(dict(script=script,args=args,status=status,elapsed_s=time.monotonic()-started));Path('audit/'+layout+'_candidate_pipeline.json').write_text(json.dumps(rows,indent=2));print('STEP',rows[-1],flush=True)
 if status!='complete':break
