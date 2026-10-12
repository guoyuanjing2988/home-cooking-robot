import subprocess,sys,time,json
from pathlib import Path
ID=sys.argv[1];start=time.monotonic();rows=[]
for script,args in [('evidence_v4_r07.py',[ID]),('reach_v4_r07.py',[ID,'R']),('single_aux_v4_r07.py',[ID])]:
 remain=1060-(time.monotonic()-start)
 if remain<30:break
 try:r=subprocess.run([sys.executable,'-B',script]+args,timeout=remain);code=r.returncode
 except subprocess.TimeoutExpired:code='timeout'
 rows.append(dict(script=script,code=code,elapsed_s=time.monotonic()-start));Path('audit/'+ID+'_study_aux_v4.json').write_text(json.dumps(rows,indent=2))
 if code!=0:break
