"""Resumable foreground chunks;96 independent starts/stroke,20s per unresolved start."""
import os,sys,json,time,hashlib,collections
import msvcrt,atexit
from pathlib import Path
# Serialize source-file mutations across resumable queues. OS locks release
# even when the bounded supervisor terminates a worker.
_locks=[];_lockdir=Path(__file__).resolve().parent/'audit/static_source_locks';_lockdir.mkdir(exist_ok=True)
for _index in range(int(sys.argv[2]),int(sys.argv[3])):
 _handle=(_lockdir/f'{sys.argv[1]}_{_index}.lock').open('a+b')
 if _handle.tell()==0:_handle.write(b'0');_handle.flush()
 _handle.seek(0)
 try:msvcrt.locking(_handle.fileno(),msvcrt.LK_NBLCK,1)
 except OSError:
  _handle.close()
  for _held in _locks:_held.close()
  raise SystemExit(75)
 _locks.append(_handle)
atexit.register(lambda:[f.close() for f in _locks])
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v6_r07 as v
from collision_ik_v6_r07 import solve
from ik_v2_r07 import fast_ik
from least_analytic_v6_r07 import solve as least_solve
from mink_v6_r07 import solve as mink_solve
from least_fixed_v6_r07 import solve as fixed_solve
lo,hi=map(int,sys.argv[2:4]);run_budget=float(sys.argv[4]) if len(sys.argv)>4 else 990
seed_goal=int(sys.argv[5]) if len(sys.argv)>5 else 96
visit_goal=int(sys.argv[6]) if len(sys.argv)>6 else seed_goal
out=v.O/'static_v6'/v.ID;out.mkdir(parents=True,exist_ok=True);began=time.monotonic();old=json.loads((v.O/'inherited_best.json').read_text())['witnesses'];maps={}
for side in v.s.model.SIDES:
 path=v.O/'reachability'/('L09' if v.ID in ('L10','L11') else 'L08' if v.ID in ('L12','L13') else v.ID)/(side+'.json')
 if not path.exists() and int(v.ID[1:])>=60:path=v.O/'reachability'/'L59'/(side+'.json')
 if path.exists():maps[side]=json.loads(path.read_text())['rows']
def initial(ch,sg,index,seed,witness):
 if witness is None and seed%4==0:
  for donor_id,donor_index in ([('L73',index)] if int(v.ID[1:])>=74 else [])+([('L71',index)] if int(v.ID[1:])>=73 else [])+([('L59',2 if index in (35,47) else 0 if index==54 else index)] if int(v.ID[1:])>=60 else [])+([('L53',index)] if int(v.ID[1:])>=54 else [])+([('L52',index)] if int(v.ID[1:])>=53 else [])+([('L51',index)] if int(v.ID[1:])>=52 else [])+[('L45',index),('L34',sg.get('source_stroke_index',index))]:
   donor=v.O/('static_v5' if donor_id in ('L59','L71','L73') else 'static_v4' if donor_id in ('L45','L51','L52','L53') else 'static_v2')/donor_id/f'{donor_index}.json'
   if not donor.exists():continue
   candidate=json.loads(donor.read_text()).get('witness')
   if not candidate:continue
   import copy
   witness=copy.deepcopy(candidate)
   for pose in witness['poses']:pose['q']=pose['q'][:ch.m.nq]
   if donor_id=='L34':
    pp=json.loads((v.O/'layouts/L34_process.json').read_text());ss=[z for p in pp['phases'] for z in p['segments']][donor_index]
    if 'R' in ss['poses'][0] and 'R' in sg['poses'][0]:witness['poses'][0]['q'][ch.qa['R_carriage_x']]+=sg['poses'][0]['R']['pos'][0]-ss['poses'][0]['R']['pos'][0]
   break
 rng=np.random.default_rng(970000+index*1000+seed);q=ch.m.qpos0.copy()
 ch.lock_initial_carriage=not witness and seed%3==1
 if witness:
  q=np.array(witness['poses'][0]['q']);k=witness['k']
  for n in v.s.ck.JOINTS+[s+'_carriage_x' for s in v.s.model.SIDES]:q[ch.qa[n]]+=rng.normal(0,.010 if 'carriage' in n else .035)
 else:
  k=seed%2
  for side in v.s.model.SIDES:
   hands=sg['poses'][0];x=np.mean([h['pos'][0] for h in hands.values()]);side_names=v.s.ck.ARMS[side]+[side+'_carriage_x']
   for n in side_names:q[ch.qa[n]]=rng.uniform(*ch.m.jnt_range[ch.jid[n]])
   valid=[r for r in maps.get(side,[]) if r['pass_']]
   if valid:
    if side in hands:
     axes={'down':[0,0,-1],'front':[0,1,0],'side':[1,0,0]}
     rank=sorted(valid,key=lambda r:np.linalg.norm(np.array(r['pos'])-hands[side]['pos'])+.25*(1-np.dot(axes[r['orientation']],hands[side]['approach'])))[:30]
    else:rank=sorted(valid,key=lambda r:-abs(r['pos'][0]-x)+(.5 if r['pos'][2]<1.15 else 0))[:30]
    src=np.array(rank[seed%len(rank)]['witness']['q']);
    for n in side_names:q[ch.qa[n]]=src[ch.qa[n]]+rng.normal(0,.04)
   if seed%24==23 and index in range(len(v.items)) and v.items[index][2] in old and side in hands:
    src=np.array(old[v.items[index][2]]['poses'][0]['q'])
    for n in side_names:q[ch.qa[n]]=src[ch.qa[n]]+rng.normal(0,.03)
 for side,h in sg['poses'][0].items():
  for label in ('minus','plus'):q[ch.qa[side+'_jaw_'+label]]=h['jaw_opening_m']/2
 if not witness and seed%4==0:
  warm=[]
  for label in ('L14','L18','L13','L12'):
   file=v.O/'static_v2'/label/f'{index}.json'
   if file.exists():
    candidate=json.loads(file.read_text()).get('witness')
    if candidate:warm.append(candidate)
  if warm:
   candidate=warm[(seed//4)%len(warm)];k=candidate['k'];src=np.array(candidate['poses'][0]['q'])
   for side in sg['poses'][0]:
    for name in v.s.ck.ARMS[side]+[side+'_carriage_x']:q[ch.qa[name]]=src[ch.qa[name]]
 if not witness:
  pool=[]
  for directory in dict.fromkeys((v.O/'static_v6'/v.ID,v.O/'static_v2'/'L13',v.O/'static_v2'/'L12')):
   for saved in directory.glob('*.json'):
    try:
     candidate=json.loads(saved.read_text()).get('witness')
     if candidate:pool.append(candidate)
    except (ValueError,OSError):pass
  for side in v.s.model.SIDES:
   if side in sg['poses'][0]:
    if pool and seed%4==2:
     staged=pool[seed%len(pool)];src=np.array(staged['poses'][0]['q'])
     for n in v.s.ck.ARMS[side]+[side+'_carriage_x']:q[ch.qa[n]]=src[ch.qa[n]]
     k=staged['k']
    continue
   x=np.mean([h['pos'][0] for h in sg['poses'][0].values()])
   choices=[.30,.0,-.65,-1.15,-1.45]
   choices.sort(key=lambda xx:-abs(xx-x))
   stage=v.s.ck.hand([choices[seed%5],-.16 if seed%2 else -.25,1.13],held='empty',approach=[0,-1,0],jaw_axis=[1,0,0])
   q,_,_=fast_ik(ch,q,{side:stage},0,max_iter=180)
   if pool and seed%3:
    staged=np.array(pool[seed%len(pool)]['poses'][0]['q'])
    for n in v.s.ck.ARMS[side]+[side+'_carriage_x']:q[ch.qa[n]]=staged[ch.qa[n]]
   parkfile=v.O/'layouts'/f'{v.ID}_park_full.json'
   if parkfile.exists() and seed%2==0:
    parked=np.array(json.loads(parkfile.read_text())['q'])
    for n in v.s.ck.ARMS[side]+[side+'_carriage_x']:q[ch.qa[n]]=parked[ch.qa[n]]
  if ch.lock_initial_carriage:
   for side in sg['poses'][0]:q[ch.qa[side+'_carriage_x']]=rng.uniform(*ch.m.jnt_range[ch.jid[side+'_carriage_x']])
 if not witness and int(v.ID[1:])>=31 and seed%6==0 and sg['station']=='peel' and sg.get('action')=='process' and sg['poses'][0].get('R',{}).get('held')=='peeler':
  source=v.O/'static_v2/L29/5.json'
  if source.exists():
   candidate=json.loads(source.read_text()).get('witness')
   if candidate:
    src=np.array(candidate['poses'][0]['q']);source_process=json.loads((v.O/'layouts/L29_process.json').read_text());source_segments=[a for p in source_process['phases'] for a in p['segments']];dx=sg['poses'][0]['R']['pos'][0]-source_segments[5]['poses'][0]['R']['pos'][0]
    for name in v.s.ck.ARMS['R']+['R_carriage_x']:q[ch.qa[name]]=src[ch.qa[name]]
    q[ch.qa['R_carriage_x']]+=dx;k=candidate['k']
    # This is only a translated proposal, clipped to public carriage travel.
    # Full new fixture/other-arm/pose/load admission remains mandatory.
 for n in ch.qa:
  j=ch.jid[n]
  if ch.m.jnt_limited[j]:
   lower,upper=ch.m.jnt_range[j];margin=min(1e-8,(upper-lower)/4)
   q[ch.qa[n]]=np.clip(q[ch.qa[n]],lower+margin,upper-margin)
 return q,k,rng
for index in range(lo,min(hi,len(v.items))):
 file=out/(str(index)+'.json');ph,sg,key=v.items[index]
 record=json.loads(file.read_text()) if file.exists() else dict(index=index,stroke=key,layout=v.ID,rows=[],starts=0,solutions_found=0,verified_witnesses=0,witness=None,best_failed=None,complete=False,allocated_seconds_per_unresolved_start=20,required_starts=seed_goal)
 if record['starts']>=seed_goal:continue
 if time.monotonic()-began>run_budget-30:break
 ch=v.scene(index);ch.search_carriage=True
 for seed in range(record['starts'],min(seed_goal,record['starts']+visit_goal)):
  if time.monotonic()-began>run_budget-25:break
  start=time.monotonic();deadline=start+20;ch.night_robust=48<=seed<56;q,k,rng=initial(ch,sg,index,seed,record['witness']);best=None;tries=0;raw=None;termination=None;methods=[]
  if int(v.ID[1:])>=20 and not record['witness'] and seed%4==3 and record.get('best_failed'):
   failed=record['best_failed']['raw'];q=np.array(failed['poses'][0]['q']);k=failed['k']
   for name in v.s.ck.JOINTS+[side+'_carriage_x' for side in v.s.model.SIDES]:q[ch.qa[name]]=np.clip(q[ch.qa[name]]+rng.normal(0,.045),*ch.m.jnt_range[ch.jid[name]])
  while time.monotonic()<deadline:
   poses=[];hits=[];err=[]
   for pi,hands in enumerate(sg['poses']):
    for side,h in hands.items():
     for label in ('minus','plus'):q[ch.qa[side+'_jaw_'+label]]=h['jaw_opening_m']/2
    ch.hands=hands;ch.set_contacts(hands);ch.search_termination=None
    # Full collision least-squares continuation retains the admitted branch;
    # projected DLS repeatedly lost the helper-index branch on warm starts.
    method=least_solve if record['witness'] is not None else (mink_solve,least_solve,solve,fixed_solve)[(seed+tries)%4] if int(v.ID[1:])>=20 else least_solve if (seed+tries)%2 else solve
    if method is fixed_solve and pi==0:
     for side in hands:
      name=side+'_carriage_x';lower,upper=ch.m.jnt_range[ch.jid[name]]
      q[ch.qa[name]]=np.linspace(lower+.005,upper-.005,13)[(seed+tries)%13]
    methods.append(method.__module__)
    q,errors,hh,evals=method(ch,q,hands,k,deadline);poses.append(dict(q=q.tolist(),errors=errors));hits.extend(hh);err.extend(errors)
    if hh or any(e['position_mm']>5 or e['orientation_deg']>3 for e in errors):break
   raw=dict(k=k,poses=poses);score=sum(e['position_mm']+3*e['orientation_deg'] for e in err)+sum(max(0,h['required_gap_mm']-h['real_gap_mm']) for h in hits)+1000*(len(sg['poses'])-len(poses))
   proposal=dict(raw=raw,score=score,hits=hits[:6],errors=err)
   if best is None or score<best['score']:best=proposal
   checked=v.f.replay(ch,raw) if len(poses)==len(sg['poses']) and not hits and all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in err) else None
   if checked and not checked['ok']:
    proposal['failed_check']=checked
    if best is proposal:best['failed_check']=checked
   tries+=1
   if checked and checked['ok']:
    record['solutions_found']+=1;record['verified_witnesses']+=1
    reserve=min((a['reserve_mm'] for po in checked['poses'] for cat,a in po['min_clearance'].items() if cat!='self'),default=0.)
    checked['minimum_nonself_reserve_mm']=reserve
    if record['witness'] is None or (reserve,-checked['max_envelope_ratios']['check'])>(record['witness'].get('minimum_nonself_reserve_mm',-1e9),-record['witness']['max_envelope_ratios']['check']):record['witness']=checked
    best=proposal;best['check']=checked;break
   if checked and not checked['ok']:
    termination=dict(kind='collision_free_pose_solution_rejected_by_full_reference',reference=checked.get('failure'))
    break
   if getattr(ch,'search_termination',None):
    termination=ch.search_termination
    break
   # Unresolved starts really use20s, with new branches and carriage choices.
   q,k,rng=initial(ch,sg,index,seed*100+tries,None)
  good=bool(best.get('check',{}).get('ok',False))
  compact=dict(seed=seed,orientation_key=best['raw']['k'],allocated_s=20,elapsed_s=time.monotonic()-start,restarts=tries,ok=good,poses_attempted=len(best['raw']['poses']),errors=best['errors'],blockers=best['hits'],score=best['score'],termination=termination or dict(kind='accepted' if good else '20s_budget_exhausted'))
  compact['proposal_methods']=sorted(set(methods));compact['extra_clearance_objective_policy']='v6 certified bounds; unresponsive pairs reported for layout changes';compact['unresponsive_extra_pairs']=getattr(ch,'immobile_extra_objective',{});compact['seed_policy']='Unresolved: map/global/staging restarts; after a reference-admitted witness: independent local perturbations0.035rad and0.010m, each with20s available. A positive witness removes the need for global infeasibility exploration.';record['rows'].append(compact);record['starts']=len(record['rows']);record['ok']=record['witness'] is not None
  if not good and (record['best_failed'] is None or best['score']<record['best_failed']['score']):record['best_failed']=best
  record['complete']=record['starts']>=seed_goal;record['model_sha256']=hashlib.sha256(ch.xml.encode()).hexdigest();record['process_sha256']=hashlib.sha256(json.dumps(v.P,sort_keys=True).encode()).hexdigest()
  temporary=file.with_suffix('.json.tmp');temporary.write_text(json.dumps(record,indent=2),encoding='utf-8')
  for _retry in range(100):
   try:temporary.replace(file);break
   except PermissionError:
    if _retry==99:raise
    time.sleep(.02) # Windows readers can briefly deny replacement.
  if (seed+1)%8==0:print(v.ID,index,key,seed+1,'good',record['verified_witnesses'],'elapsed',round(time.monotonic()-began),flush=True)
 if record['complete'] and record['witness']:(v.H/'models'/f'{v.ID}_stroke_{index}.xml').write_text(ch.xml,encoding='utf-8')
 print(v.ID,index,'chunk',record['starts'],'PASS' if record['ok'] else 'FAIL',flush=True)
print('FOREGROUND_CHUNK_END',v.ID,lo,hi,round(time.monotonic()-began),flush=True)
