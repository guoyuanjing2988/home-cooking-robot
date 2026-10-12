import time,json
import checker as ck
from model import CONFIG
from run import delta
began=time.monotonic();ck.configure(dict(CONFIG,arm='xArm7',height=.30,orientation='horizontal',standoff=.15,count=2))
for pid in ('P02','P04','P06','P13'):
    if time.monotonic()-began>180:raise TimeoutError('smoke 180sec')
    r=ck.run_phase(pid,2,delta(pid))
    print(pid,r['feasible_seeds'],r['blocker_counts'],r['dominant_blocker'],flush=True)
    ck.json_write(ck.HERE/'results/smoke'/f'{pid}.json',r)
