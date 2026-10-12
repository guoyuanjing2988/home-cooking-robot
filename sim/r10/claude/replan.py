"""Re-plan one chain end to end: SEQ (groups) -> N (normalize) -> C1..C3 in
parallel -> A (assemble). Logs: logs/r12/chain_<preset>_<step>.log.
Usage: python replan.py <preset>"""
import sys,os,subprocess,time
from concurrent.futures import ThreadPoolExecutor
P=sys.argv[1];os.makedirs('logs/r12',exist_ok=True)
def run(step):
 t=time.time()
 with open(f'logs/r12/chain_{P}_{step}.log','w') as f:r=subprocess.run([sys.executable,'chain.py',P,step],stdout=f,stderr=subprocess.STDOUT)
 print(P,step,'exit',r.returncode,round(time.time()-t),'s',flush=True);return r.returncode
if run('SEQ')==0 and run('N')==0:
 with ThreadPoolExecutor(3) as ex:codes=list(ex.map(run,['C1','C2','C3']))
 if all(c==0 for c in codes):run('A')
