import json,csv,copy
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results'
jobs=[]
def job(id,label,seconds,resources,deps,basis):jobs.append(dict(id=id,label=label,duration_s=seconds,resources=resources,depends=deps,basis=basis))
job('stage','Stage/inspect four inputs',60,['R','L'],[],'R03 handling allowance')
job('greens_wash','Coarse wash bok choy',60,['R','sink'],['stage'],'R03230s composite separated:60wash+170cut')
job('greens_trim','Guarded5-10mm root trim',170,['aux'],['greens_wash'],'Retained slow greens proxy at0.5mm/s')
job('greens_separate','Separate six stalks and expose every crease',90,['R'],['greens_trim'],'R03 allowance; six-stalk count explicit, inspect and extend if needed')
job('fill','Fill50.16L sink',501.6,['sink'],['greens_separate'],'50.16/6L/min; same R03 water requirement')
job('soak','Soak bok choy',600,['sink'],['fill'],'Binding600s; cannot shorten')
job('carrot_wash','Wash carrot/load nest/acquire peeler',120,['R','sink'],['stage'],'R03 allowance')
job('carrot_peel','12 peel/index cycles',270,['R','L','peel'],['carrot_wash'],'R03 retained time and two-arm support/index')
job('carrot_rinse','Rinse/clean peel land/install bowl',120,['R','sink','peel'],['carrot_peel'],'R03 allowance')
job('carrot_trim','End trims and terminal two5mm slices',280,['aux'],['carrot_rinse'],'R03 low-speed bounds unchanged')
job('carrot_disc','OEM disc feed/output/delivery',90,['R','slicer'],['carrot_trim'],'R03 handling estimate; pusher wrench unknown; detach arms before run')
job('potato_wash','Wash potato/load nest/acquire peeler',120,['R','sink','peel'],['carrot_rinse'],'R03 allowance')
job('potato_peel','10 peel/index cycles',190,['R','L','peel'],['potato_wash'],'R03 retained time')
job('potato_eyes','Eyes/rinse/clean/bowl install',180,['R','sink','peel'],['potato_peel'],'R03 allowance; three planning eyes, inspect and extend')
job('potato_trim','End trims/longitudinal split/terminal slices',1020,['aux'],['potato_eyes'],'R03 low-speed bounds unchanged')
job('potato_disc','OEM disc feed/collection',90,['R','slicer'],['potato_trim'],'R03 handling estimate')
job('potato_rinse','Three fresh changes and30s drain',120,['R','sink'],['potato_disc','soak'],'Shared sink unavailable during soak; retain all edible pieces')
job('greens_rub','Rub/inspect every crease/rinse/drain',150,['R','L','sink'],['soak'],'R03120s+30s; physical inspection still required')
job('greens_split','Split two stalks wider than15mm',680,['aux'],['greens_rub'],'R03two340s low-speed cycles; each extra wide stalk adds340s+handling')
job('greens_sections','Five40mm cycles and transfer',360,['aux'],['greens_split'],'R03 full allowance retained; conservative resource lock includes transfer')
job('tomato_wash','Wash/core/load tomato',150,['R','sink','peel'],['potato_eyes'],'R03 allowance')
job('tomato_cut','Eight-wedge cycle and transfer',180,['aux'],['tomato_wash'],'R03 low-speed proxy unchanged')
job('inspection','Inspect ten distributed root slices/all wedges/all creases/yield',90,['R','L'],['carrot_disc','potato_rinse','greens_sections','tomato_cut'],'R03 allowance; >=98percent yield required')
job('clean','Disassemble/rinse/drain/wipe/return/park',300,['R','L','sink','aux','slicer'],['inspection'],'R03 full cleaning allowance; no dirty tool reused as clean')
for j in jobs:
 if 'aux' in j['resources'] and j['id']!='clean':
  j['resources'].append('L');j['basis']+='; L charged for guarded-cell loading/handling in desired dual-arm plan, required helper poses not yet admitted'
cal={};done={};pending=jobs.copy()
def slot(j):
 start=max([done[x]['end_s'] for x in j['depends']] or [0.])
 while True:
  collisions=[end for res in j['resources'] for lo,end in cal.get(res,[]) if lo<start+j['duration_s']-1e-8 and end>start+1e-8]
  if not collisions:return start
  start=min(collisions)
while pending:
 ready=[j for j in pending if all(x in done for x in j['depends'])];j=min(ready,key=lambda x:(slot(x),jobs.index(x)));start=slot(j)
 row=dict(j,start_s=start,end_s=start+j['duration_s']);done[j['id']]=row;pending.remove(j)
 for res in j['resources']:cal.setdefault(res,[]).append((row['start_s'],row['end_s']))
rows=sorted(done.values(),key=lambda r:(r['start_s'],r['id']));makespan=max(r['end_s'] for r in rows)
schedule=dict(schema='r04.resource-schedule.v1',rows=rows,prep_min=makespan/60,planned_prep_min=makespan/60,verified_prep_min=None,serial_R03_min=99.86,target_min=45,target_met=makespan<=2700,executability='FAIL: persistent ownership, paths, paired concurrency and food quality not admitted',overlap=[dict(wash=w['id'],cut=c['id'],start_s=max(w['start_s'],c['start_s']),end_s=min(w['end_s'],c['end_s'])) for w in rows if 'wash' in w['id'] or w['id']=='greens_rub' for c in rows if 'aux' in c['resources'] and c['id']!='clean' and max(w['start_s'],c['start_s'])<min(w['end_s'],c['end_s'])],lower_bound_min=(sum(j['duration_s'] for j in jobs if 'aux' in j['resources'] and j['id']!='clean')+390)/60,scheduling_method='Greedy earliest feasible calendar insertion on R/L/sink/peel/aux/slicer resources; shared soak blocks sink. Conservative exclusive machine locks retain all R03 durations.',conditional_counts=dict(eyes=3,basal_stalks=6,wide_stalks=2),paired_pose_verified=False)
schedule.update(machine_only_optimistic_min=83.86,two_arm_overlap_achieved=False,actor_policy='R washing/processing, L assigned auxiliary cut-cell handling with its resource charged for the whole conservative composite; helper replacement poses and both-arm concurrent trajectories unverified',guarded_aux_feed_mm_s=.5,faster_feed='1-2mm/s is not admitted without source/qualification covering force versus rate, cutting quality, actuator and guarded pusher motion. Proxy forces were not lowered for a time target.')
(O/'schedule.json').write_text(json.dumps(schedule,indent=2))
base=list(csv.DictReader((H/'baseline/costs.csv').open(encoding='utf-8-sig')))[:-2]
costs=[]
for name,main,helper,rail,slicer in [('best_candidate',150000,76900,61000,18000),('wall_candidate',150000,76900,43000,18000),('household_wall_candidate',150000,76900,43000,4000),('xarm_wall_household_candidate',76900,76900,43000,4000),('jaka_zu7_wall_household_candidate',75000,76900,43000,4000)]:
 total=0
 for i,r in enumerate(base):
  qty=float(r['quantity']);val=float(r['total_cny'])
  if i==0:val=main
  if i==1:val=helper
  if i==2:val=rail
  if i==5:val=slicer
  basis=r['basis']
  if i==2:basis='R04 allowance: full61k geometry repair/fallback, or43k strong-wall design scenario requiring site verification; no building qualification'
  if i==5 and slicer==4000:basis='BFP610 household appliance+keyed bowl/pusher adapter allowance, not matched230V China quote; OEM AU429AUD out-of-stock observed'
  costs.append(dict(configuration=name,item=r['item'],quantity=qty,total_cny=round(val,2),basis=basis,status='PLANNING_ONLY_NOT_PASSING'));total+=val
 costs.append(dict(configuration=name,item='One15percent project reserve',quantity=1,total_cny=round(total*.15,2),basis='one reserve applied once',status='PLANNING_ONLY_NOT_PASSING'))
 costs.append(dict(configuration=name,item='TOTAL',quantity=1,total_cny=round(total*1.15,2),basis='home safety18k once; rail brakes once in rail line; no duplicated tools reserve',status='PLANNING_ONLY_NOT_PASSING'))
with (O/'costs.csv').open('w',newline='',encoding='utf-8') as fp:w=csv.DictWriter(fp,fieldnames=list(costs[0]));w.writeheader();w.writerows(costs)
(O/'cost_summary.json').write_text(json.dumps(dict(totals={r['configuration']:r['total_cny'] for r in costs if r['item']=='TOTAL'},cheapest_passing_cny=None,reason='No complete meal passes unchanged contact/motion/product requirements; low-cost candidates are not promoted to passing configurations.'),indent=2))
print('planned prep',makespan/60,'min; lower bound',schedule['lower_bound_min'],'min; totals',json.loads((O/'cost_summary.json').read_text())['totals'])
