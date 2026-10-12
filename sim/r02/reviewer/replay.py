"""Independent stored-pose replay; diagnostic AABBs never replace contact gates."""
import os,sys,json,collections,math
from pathlib import Path
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path.insert(0,str(ROOT/'sim/r02/concept2'))
import adapter
import numpy as np,mujoco
def main():
 report=[];geom=[];allparts=0;allrows=0;allposes=0;max_tq=0.;max_gr=0.;max_frozen=0.;bad=0;anomalies=[];maps=[]
 for f in sorted((ROOT/'sim/r02/concept2/results/final_v4/c0684').glob('Q*.json')):
  r=json.loads(f.read_text());items=[]
  for si,part in enumerate(r['parts']):
   ch=adapter.Checker(r['definition'],r['definition']['segments'][si],r['config']);allparts+=1
   frozen=adapter.ck.BASE+adapter.ck.JAWS+sum([v for s,v in adapter.ck.ARMS.items() if s not in ch.seg['poses'][0]],[])
   maps.append(dict(id=r['id'],stroke=part['label'],intended=[ch.gnames[i] for i in sorted(ch.intended)],requested={s:h['intended'] for s,h in ch.seg['poses'][0].items()}))
   # Every saved seed is checked for frozen axes and declared pose/acceptance.
   for row in part['rows']:
    allrows+=1;q0=np.array(row['poses'][0]['q'])
    for pi,po in enumerate(row['poses']):
     allposes+=1;q=np.array(po['q']);max_frozen=max(max_frozen,max(abs(q[ch.qa[n]]-q0[ch.qa[n]]) for n in frozen))
     if row['ok'] and (row['hits'] or any(e['position_mm']>5 or e['orientation_deg']>3 for e in po['errors'])):bad+=1
   # Replay all IK-complete seed endpoints, including rejected poses.
   replayed=0;changed=0
   for row in part['rows']:
    if row.get('blocker',{}).get('kind')=='IK':continue
    hits=[];nom=None;check=None
    for pi,po in enumerate(row['poses']):
     q=np.array(po['q']);hands=ch.seg['poses'][pi];ch.environment_pose(pi)
     observed=ch.forbidden(q);hits += [dict(pose=pi,**v) for v in observed];replayed+=1
     for level in ('nominal','check'):
      for forces,moments in adapter.wrench_cases(hands,level):
       tq=ch.torque_multi(q,hands,forces,moments=moments)
       gr=min(ch.grip_side(q,h,forces[s],s,moments[s])['margin'] for s,h in hands.items())
       value=(tq['ratio'],gr)
       if level=='nominal':nom=value if nom is None else (max(nom[0],value[0]),min(nom[1],value[1]))
       else:check=value if check is None else (max(check[0],value[0]),min(check[1],value[1]))
     for hit in observed:
      if hit['real_gap_mm']>-10:continue
      a,b=[ch.m.geom(n).id for n in hit['pair']]
      # Boxes only, for a valid OBB -> AABB separated lower bound.
      if any(int(ch.m.geom_type[g])!=6 for g in (a,b)):continue
      ext=[np.abs(ch.d.geom_xmat[g].reshape(3,3))@ch.m.geom_size[g] for g in (a,b)]
      gap=float(np.linalg.norm(np.maximum(np.abs(ch.d.geom_xpos[a]-ch.d.geom_xpos[b])-ext[0]-ext[1],0)))
      if gap>=.01 and len(anomalies)<40:anomalies.append(dict(id=r['id'],stroke=part['label'],seed=row['k'],pose=pi,pair=hit['pair'],literal_gap_mm=hit['real_gap_mm'],AABB_separation_lower_bound_mm=gap*1000,acceptance_changed=False))
    changed+=hits!=row['hits']
    for lv,val in (('nominal',nom),('check',check)):
     max_tq=max(max_tq,abs(val[0]-row[lv]['torque']['ratio']));max_gr=max(max_gr,abs(val[1]-row[lv]['grip']['margin']))
   items.append(dict(stroke=part['label'],replayed_endpoints=replayed,contact_record_mismatches=changed))
  report.append(dict(instance=r['id'],parts=items))
  print('REPLAY',r['id'],sum(a['replayed_endpoints'] for a in items),flush=True)
 output=dict(instances=len(report),strokes=allparts,seed_strokes=allrows,saved_poses=allposes,max_frozen_drift=max_frozen,max_torque_ratio_difference=max_tq,max_grip_margin_difference=max_gr,invalid_admitted_pose_count=bad,contact_record_mismatches=sum(p['contact_record_mismatches'] for i in report for p in i['parts']),replayed_endpoints=sum(p['replayed_endpoints'] for i in report for p in i['parts']),details=report,numerical_anomalies=anomalies)
 (H/'audit/replay.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
 (H/'audit/resolved_contacts.json').write_text(json.dumps(maps,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in output.items() if k not in ('details','numerical_anomalies')}) )
if __name__=='__main__':main()
