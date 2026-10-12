import numpy as np,collections,sys
from chain import checker,target
from solver import solve
preset=sys.argv[1]
t=target(preset,'peel_load');ch,_=checker(preset,'carrot');ch.active=ch.arm_ids
for k,p in enumerate([t['points'][0],t['points'][-1]]):
 r=solve(ch,np.array(p),t['approach'],seed=99+k,target=t)
 c=collections.Counter()
 for row in r['rows']:
  for h in (row.get('check') or {}).get('hits',[])[:3]:c[tuple(sorted(h['pair']))]+=1
 print(k,r['status_counts'],c.most_common(8),flush=True)
