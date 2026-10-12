from jobs import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--lo',type=int,default=0);p.add_argument('--hi',type=int,default=10000);p.add_argument('--starts',type=int,default=96);a=p.parse_args();assert a.starts>=96
rows=[];beg=time.monotonic();rng=np.random.default_rng(6006+a.lo)
for ji,job in enumerate(JOBS[a.lo:a.hi],a.lo):
 ch=load_cell(job);best=None;valid=[];attempts=[];counters={};start=time.monotonic()
 for k in range(a.starts):
  q=ch.q0.copy()
  for n in ARM:q[ch.qa[n]]=rng.uniform(max(-math.pi,ch.m.jnt_range[ch.jid[n],0]),min(math.pi,ch.m.jnt_range[ch.jid[n],1]))
  poses=[];score=0;okay=True
  for target in job['targets']:
   q,err=ch.solve(np.array(target),ch.rot,q);hs=hand(ch,target,job['load']);ch.set_contacts(hs);hits,mins,ca=contacts(ch,q);tq,gr,cases=check_load(ch,q,hs)
   # Every actual flange mass includes exactly 1.2kg EOAT and held assembly.
   total=1.2+hs['R']['held_kg'];payload_ok=total<=5 and np.linalg.norm(ch.com)+.09<=.35
   good=err['position_mm']<=5 and err['orientation_deg']<=3 and not hits and tq<=1 and gr>=1 and payload_ok
   reserve=min((x['reserve_mm'] for cat,x in mins.items() if cat!='self'),default=min(x['reserve_mm'] for x in mins.values()));score+=len(hits)*100+err['position_mm']+err['orientation_deg']+max(0,tq-1)*100;okay &= good
   poses.append(dict(q=q.tolist(),errors=err,clearance=mins,blockers=hits[:5],torque_ratio=tq,grip_margin=gr,force_cases=cases,total_flange_kg=total,payload_chart_ok=payload_ok,reserve_mm=reserve))
   for h in hits:counters[' / '.join(h['pair'])]=counters.get(' / '.join(h['pair']),0)+1
  row=dict(seed=k,static_robot_ok=okay,score=score,poses=poses)
  attempts.append(dict(seed=k,static_robot_ok=okay,score=score,max_pose_mm=max(x['errors']['position_mm'] for x in poses),max_pose_deg=max(x['errors']['orientation_deg'] for x in poses),first_blocker=next((x['blockers'][0] for x in poses if x['blockers']),None)))
  if best is None or score<best['score']:best=row
  if okay:valid.append(row)
 if valid:best=max(valid,key=lambda r:min(x['reserve_mm'] for x in r['poses']))
 admitted=bool(valid) and job['admission']=='full_robot_static'
 result=dict(index=ji,id=job['id'],macro=job['macro'],kind=job['kind'],pass_=admitted,static_robot_ok=bool(valid),starts=a.starts,solutions=len(valid),selected=best,attempts=attempts,job=job,blocker_counts=counters,elapsed_s=time.monotonic()-start,model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),limitation=job.get('unresolved'))
 rows.append(result);write(f'results/static_chunk_{a.lo}_{a.hi}.json',dict(rows=rows,elapsed_s=time.monotonic()-beg,total_jobs=len(JOBS)))
 if job['held']:(H/f'models/{job["id"]}.xml').write_text(ch.xml)
 print(ji,job['id'],'static robot',bool(valid),'admitted',admitted,'solutions',len(valid),'seconds',round(result['elapsed_s'],2),flush=True)
print('STROKES',len(rows),'ADMITTED',sum(r['pass_'] for r in rows),'elapsed',round(time.monotonic()-beg,1))
