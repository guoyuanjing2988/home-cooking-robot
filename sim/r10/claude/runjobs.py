"""Run dyn.py jobs in parallel. Each job line: <preset> <mu> <grip_N> [KEY=VALUE ...]
(environment settings for dyn.py, e.g. FINGER=V ITEM_D=.08 GRIP=pos:.006).
Usage: python runjobs.py jobs.txt [workers=5]; logs go to logs/r12/."""
import sys,os,subprocess,shlex,time
from concurrent.futures import ThreadPoolExecutor
jobs=[l.split() for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
W=int(sys.argv[2]) if len(sys.argv)>2 else 5;os.makedirs('logs/r12',exist_ok=True)
def run(j):
 P,mu,F,*kv=j;env=dict(os.environ,**dict(x.split('=',1) for x in kv));name='_'.join([P,mu,F]+[x.replace('=','').replace(':','').replace('/','') for x in kv])
 t=time.time()
 with open(f'logs/r12/dyn_{name}.log','w') as f:r=subprocess.run([sys.executable,'dyn.py',P,mu,F],env=env,stdout=f,stderr=subprocess.STDOUT)
 print(name,'exit',r.returncode,round(time.time()-t),'s',flush=True)
with ThreadPoolExecutor(W) as ex:list(ex.map(run,jobs))
