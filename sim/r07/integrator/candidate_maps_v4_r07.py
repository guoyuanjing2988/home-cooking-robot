import sys,subprocess,time,json,os
from pathlib import Path
ID=sys.argv[1];start=time.monotonic();rows=[]
for script,args in [('reach_v4_r07.py',[ID,'R']),('reach_v4_r07.py',[ID,'L']),('carriage_barrier_v2_r07.py',[ID]),('run_v4_r07.py',['park_v2_r07.py',ID]),('run_v4_r07.py',['idle_v2_r07.py',ID,'--snapshot-only'])]:
 remaining=1080-(time.monotonic()-start)
 if remaining<30:break
 try:r=subprocess.run([sys.executable,'-B',script,*args],timeout=remaining,env=dict(os.environ,R07_PARK_SECONDS=str(min(200,remaining-30))));code=r.returncode
 except subprocess.TimeoutExpired:code='timeout'
 rows.append(dict(script=script,args=args,code=code,elapsed_s=time.monotonic()-start));Path('audit/'+ID+'_candidate_v4.json').write_text(json.dumps(rows,indent=2))
 if code!=0:break
