import json,copy,numpy as np
import final_check as f
s=f.s;H=s.HERE;rows=[]
for pid in ['Q14','Q18','Q24']:
 ph=next(x for x in s.P['phases'] if x['id']==pid);sg=copy.deepcopy(ph['segments'][0])
 for po in sg['poses']:po['L']=po.pop('R')
 ch=s.Checker(ph,sg);rng=np.random.default_rng(6000);raw=[ch.run_seed(k,rng) for k in range(96)];good=[r for r in raw if r['ok']];ver=[f.replay(ch,r) for r in good[:8]]
 rows.append(dict(phase=pid,seeds_tried=96,solver_solutions_found=len(good),verified_witnesses=sum(x['ok'] for x in ver),independent_replays=ver,rows=raw));print('L cut screen',pid,len(good),sum(x['ok'] for x in ver),flush=True)
(H/'results/dual_arm_concurrency.json').write_text(json.dumps(dict(status='NOT_ADMITTED',rows=rows,paired_paths_verified=False,scope='Replace cut-cell holder R by L without shrinking geometry or changing original load/forces. Finite static screen only; simultaneous R washing/L cutting paths, lid operations and supports require additional conserved-scene proof.'),indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist()))
