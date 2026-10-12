import numpy as np,collections,sys,json
from chain import checker,target
from solver import solve
preset=sys.argv[1];k=int(sys.argv[2])
t=target(preset,'peel_load');ch,_=checker(preset,'carrot');ch.active=ch.arm_ids
p=[t['points'][0],t['points'][-1]][k]
r=solve(ch,np.array(p),t['approach'],seed=300+k,target=t,starts=288)
print(preset,k,r['status_counts'],[round(c['reserve_mm'],1) for c in r['candidates']],flush=True)
json.dump(dict(cands=r['candidates']),open(f'results/peel_{preset}_{k}.json','w'),default=lambda x:x.tolist() if hasattr(x,'tolist') else str(x))
