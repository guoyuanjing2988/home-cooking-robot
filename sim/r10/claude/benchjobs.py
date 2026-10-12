"""Run foodbench.py jobs in parallel. Job file lines: <item> [KEY=VALUE ...].
Usage: python benchjobs.py jobs.txt [workers=8]; logs in logs/r13/."""
import sys,os,subprocess,time
from concurrent.futures import ThreadPoolExecutor
jobs=[l.split() for l in open(sys.argv[1],encoding='utf-8') if l.strip() and not l.startswith('#')]
W=int(sys.argv[2]) if len(sys.argv)>2 else 8;os.makedirs('logs/r13',exist_ok=True)
def run(j):
 name='_'.join(x.replace('=','').replace(':','').replace(',','_') for x in j);t=time.time()
 with open(f'logs/r13/{name}.log','w') as f:r=subprocess.run([sys.executable,'foodbench.py']+j,stdout=f,stderr=subprocess.STDOUT)
 print(name,'exit',r.returncode,round(time.time()-t),'s',flush=True)
with ThreadPoolExecutor(W) as ex:list(ex.map(run,jobs))
