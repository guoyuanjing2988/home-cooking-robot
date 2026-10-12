import copy,json,numpy as np
from collections import Counter
import solver as s
ph=next(p for p in s.P['phases'] if p['id']=='Q05.carrot')
out=[]
for pos in ([ -.65,-.12,1.10],[-1.45,-.15,1.05],[-.45,-.30,1.04]):
    sg=copy.deepcopy(ph['segments'][1])
    for po in sg['poses']:po['R']['pos']=pos
    ch=s.Checker(ph,sg);rng=np.random.default_rng(744);rows=[ch.run_seed(k,rng) for k in range(96)]
    good=[r for r in rows if r['ok']];counts=Counter(tuple(h['pair']) for r in rows for h in r['hits'])
    best=min(good or rows,key=lambda r:sum(e['position_mm']+e['orientation_deg'] for p in r['poses'] for e in p['errors']))
    out.append(dict(pos=pos,solutions=len(good),best=best,rows=rows,blockers=[dict(pair=a,count=n) for a,n in counts.most_common(10)]))
    print(pos,len(good),best.get('blocker'),counts.most_common(3),flush=True)
s.ck.json_write(s.HERE/'results/helper_trials.json',out)
