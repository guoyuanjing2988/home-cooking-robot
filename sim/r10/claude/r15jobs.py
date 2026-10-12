"""Run r15reach.py job lines in parallel (one job = one line: <probe> KEY=VAL ...).
Usage: <venv python> r15jobs.py jobs.txt [workers=12]; logs in logs/r15/."""
import sys,os,subprocess,time
from concurrent.futures import ThreadPoolExecutor
jobs=[l.split() for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')];W=int(sys.argv[2]) if len(sys.argv)>2 else 12
os.makedirs('logs/r15',exist_ok=True)
def run(j):
 name='_'.join(a.split('=')[-1].replace('/','-') for a in j)[:120];t=time.time()
 with open(f'logs/r15/reach_{name}.log','w') as f:r=subprocess.run([sys.executable,'r15reach.py']+j,stdout=f,stderr=subprocess.STDOUT)
 print(f'{r.returncode} {time.time()-t:.0f}s {" ".join(j)}',flush=True)
with ThreadPoolExecutor(W) as ex:list(ex.map(run,jobs))
print('ALL DONE',flush=True)
