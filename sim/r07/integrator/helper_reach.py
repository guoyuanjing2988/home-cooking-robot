"""Kinematic-only diagnosis. No result here is an accepted witness."""
import copy,numpy as np
from collections import Counter
import solver as s
ph=next(p for p in s.P['phases'] if p['id']=='Q05.carrot');sg=copy.deepcopy(ph['segments'][1]);sg['poses']=sg['poses'][:1]
ch=s.Checker(ph,sg);reference=ch.forbidden;ch.forbidden=lambda q:[];rng=np.random.default_rng(772)
rows=[];counts=Counter()
for k in range(96):
 r=ch.run_seed(k,rng);r['ok']=False;r['diagnostic_only']=True
 q=np.array(r['poses'][0]['q']);hits=reference(q);r['actual_hits']=hits;rows.append(r)
 if all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in r['poses'][0]['errors']):counts.update(tuple(h['pair']) for h in hits)
best=min(rows,key=lambda r:sum(e['position_mm']+e['orientation_deg'] for p in r['poses'] for e in p['errors']))
s.ck.json_write(s.HERE/'results/helper_kinematic_diagnosis.json',dict(best=best,rows=rows,blockers=[dict(pair=p,count=n) for p,n in counts.most_common(20)],status='No collision optimisation; never admitted'))
print(best['poses'][0]['errors'],counts.most_common(15))
