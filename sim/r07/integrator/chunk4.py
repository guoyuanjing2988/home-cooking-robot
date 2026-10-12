"""Up to four CPU workers, foreground, per-worker 1900MiB/1040s bounds."""
import os,sys,time,subprocess,json
from pathlib import Path
from bounded import rss,tree
H=Path(__file__).resolve().parent
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
jobs=[(arg.split(':')[0],int(arg.split(':')[1]),int(arg.split(':')[2])) for arg in sys.argv[1:]];assert len(jobs)<=4
workers=[];start=time.monotonic()
for mode,lo,hi in jobs:
 name=f'{mode}_{lo}_{hi}';fp=(H/'audit'/('chunk_'+name+'.log')).open('w',encoding='utf-8')
 cmd=[sys.executable,'-B','-u',str(H/'motion_r05.py'),str(lo),str(hi),mode]
 p=subprocess.Popen(cmd,stdout=fp,stderr=subprocess.STDOUT);workers.append(dict(name=name,p=p,file=fp,start=time.monotonic(),peak=0,cmd=cmd,status='running'))
try:
 while any(w['status']=='running' for w in workers):
  for w in workers:
   if w['status']!='running':continue
   p=w['p'];w['peak']=max(w['peak'],sum(rss(pid) for pid in tree(p.pid)));elapsed=time.monotonic()-w['start']
   if elapsed>1040 or w['peak']>1900:p.kill();w['status']='timeout' if elapsed>1040 else 'memory_limit'
   elif p.poll() is not None:w['status']='complete' if p.returncode==0 else 'error'
   if w['status']!='running':
    w['file'].flush();rec=dict(command=w['cmd'],status=w['status'],exit_code=p.poll(),elapsed_s=elapsed,peak_MiB=w['peak'],timeout_s=1040,worker_processes=1,cpu_only=True)
    (H/'audit'/('chunk_'+w['name']+'.resource.json')).write_text(json.dumps(rec,indent=2));print(w['name'],w['status'],round(elapsed,1),flush=True)
  if time.monotonic()-start>1080:raise TimeoutError('foreground chunk >1080s')
  time.sleep(.25)
finally:
 for w in workers:
  if w['p'].poll() is None:w['p'].kill()
  w['p'].wait(timeout=10);w['file'].close()
print('CHUNK_COMPLETE',round(time.monotonic()-start,1),flush=True)
