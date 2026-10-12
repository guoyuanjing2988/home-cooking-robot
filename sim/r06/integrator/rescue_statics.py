"""96 independent collision-aware starts for every physical handling obligation.

Four disjoint seed ranges may run concurrently. Each worker checkpoints every
seed and returns after1000s, below the enclosing1100s foreground timeout.
"""
from rescue_spec import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--variant',type=int,default=14);p.add_argument('--lo',type=int,default=0);p.add_argument('--hi',type=int,default=1000);p.add_argument('--seed-lo',type=int,default=0);p.add_argument('--seed-hi',type=int,default=24);p.add_argument('--warm-layout',type=int);a=p.parse_args();assert 0<=a.seed_lo<a.seed_hi<=96
cfg=config(a.variant);jobs=recipe(a.variant)['statics'];beg=time.monotonic();deadline=beg+1000
def exact(ch,target,q):
 z=np.array(q).copy();ix=ch.ix;lim=np.array([ch.m.jnt_range[ch.jid[n]] for n in ch.variables]).T
 def fun(x):
  z[ix]=x;pp,rr=ch.pose(z);return np.r_[(pp-target)*20,Rotation.from_matrix(ch.rot.T@rr).as_rotvec()*3]
 ls=least_squares(fun,np.clip(z[ix],lim[0]+1e-9,lim[1]-1e-9),bounds=lim,max_nfev=100,ftol=1e-9,xtol=1e-9,gtol=1e-9);z[ix]=ls.x;return z
def evaluate(ch,q,target,label):
 pp,rr=ch.pose(q);hits,mins,pf=contacts(ch,q);hs=hand(ch,target);tq,gr,cases=check_load(ch,q,hs);pe=float(np.linalg.norm(pp-target)*1000);oe=float(np.linalg.norm(Rotation.from_matrix(ch.rot.T@rr).as_rotvec())*180/math.pi);mass=1.2+hs['R']['held_kg'];chart=mass<=5 and np.linalg.norm(ch.com)+.09<=.35
 return dict(label=label,q=q.tolist(),errors=dict(position_mm=pe,orientation_deg=oe),hits=hits[:5],clearance=mins,reserve_mm=min((v['reserve_mm'] for cat,v in mins.items() if cat!='self'),default=0),torque_ratio=tq,grip_margin=gr,force_cases=cases,total_flange_kg=mass,payload_chart_ok=chart,pass_=not hits and pe<=5 and oe<=3 and tq<=1 and gr>=1 and chart,attachment_precision_ok=pe<=.001 and oe<=.001)
for ji,job in enumerate(jobs[a.lo:a.hi],a.lo):
 name=f'v2/statics/L{a.variant}_{ji:02d}_{a.seed_lo}_{a.seed_hi}.json';f=H/name;rows=json.loads(f.read_text())['rows'] if f.exists() else [];done={r['seed'] for r in rows}
 loc=copy.deepcopy(job['locations']);loc[job['object_id']]=job['origin'];empty=Workcell(a.variant,None,loc);loaded=Workcell(a.variant,job['object_id'],loc);empty.capture(job['object_id'],job['origin']);loaded.contact_windows=loaded.window(job['object_id'],job['station'],job['origin']);target=key_position(job['origin'],cfg)
 # Adjacent release/reacquisition obligations sometimes have byte-identical
 # complete scenes, targets and policies. The exact same96 independent starts
 # certify both physical problems; record the full hash equality and source,
 # rather than calling them additional solver executions.
 problem=hashlib.sha256((empty.xml+loaded.xml+json.dumps(dict(target=target.tolist(),capture=empty.capture_window,windows=loaded.contact_windows),sort_keys=True)).encode()).hexdigest()
 cached=None
 for cf in sorted((H/'v2/statics').glob(f'L{a.variant}_*_{a.seed_lo}_{a.seed_hi}.json')):
  if cf==f:continue
  cc=json.loads(cf.read_text())
  if cc.get('index',10000)<ji and cc.get('problem_sha256')==problem and len(cc['rows'])==a.seed_hi-a.seed_lo:cached=(cf,cc);break
 if cached:
  cf,cc=cached
  if f.exists() and not json.loads(f.read_text()).get('reused_identical_problem'):write(f'v2/audit/pre_reuse_{f.name}',json.loads(f.read_text()))
  write(name,dict(cc,job=job,index=ji,reused_identical_problem=str(cf.relative_to(H)),source_file_sha256=hashlib.sha256(cf.read_bytes()).hexdigest(),additional_solver_executions=0));print('EXACT_PROBLEM_REUSE',ji,str(cf.relative_to(H)),flush=True);continue
 for ch,label in ((empty,'empty'),(loaded,'held')):
  model=f'v2/models/L{a.variant}_{job["id"]}_{label}.xml';(H/model).parent.mkdir(parents=True,exist_ok=True);(H/model).write_text(ch.xml)
 if f.exists():
  existing=json.loads(f.read_text());existing['problem_sha256']=problem;write(name,existing)
 warm=[];warm_cell=None
 if a.warm_layout:
  for wf in sorted((H/'v2/statics').glob(f'L{a.warm_layout}_{ji:02d}_*.json')):
   prior=json.loads(wf.read_text());warm.extend(prior['rows'])
  if warm:
   okay=[r for r in warm if r['pass_']];warm=okay or warm;warm_cell=Workcell(a.warm_layout,None,loc)
  # A different ingredient at the same TCP target can supply a seed, never a
  # geometry certificate. Re-solve and check the full new scene after perturbing.
  family=[]
  for wf in sorted((H/'v2/statics').glob(f'L{a.variant}_*.json')):
   prior=json.loads(wf.read_text())
   if prior['index']>=ji or prior['job']['station']!=job['station'] or not np.allclose(prior['job']['origin'],job['origin']):continue
   family.extend(r for r in prior['rows'] if r['pass_'])
  if family:warm=family;warm_cell=empty
 for k in range(a.seed_lo,a.seed_hi):
  if k in done:continue
  rng=np.random.default_rng(614000+ji*100+k)
  if time.monotonic()>deadline-45:print('CHECKPOINT',ji,k,flush=True);raise SystemExit(0)
  q=empty.q0.copy()
  for n in empty.variables:
   lo,hi=empty.m.jnt_range[empty.jid[n]];q[empty.qa[n]]=rng.uniform(max(-math.pi,lo),min(math.pi,hi))
  local_good=[r for r in rows if r['pass_']]
  if warm or local_good:
   pool=local_good or warm;oldq=np.array(pool[rng.integers(len(pool))]['poses'][0]['q']);seed_cell=empty if local_good else warm_cell
   for n in ARM:
    lo,hi=empty.m.jnt_range[empty.jid[n]];q[empty.qa[n]]=np.clip(oldq[seed_cell.qa[n]]+rng.normal(0,.15),lo+1e-8,hi-1e-8)
  seed_q=q.copy();solve=empty.collision_solve(target,empty.rot,q,seconds=20);q=exact(empty,target,solve['q']);poses=[evaluate(empty,q,target,'open_key_endpoint')]
  z=q.copy()
  for n in ('R_jaw_minus','R_jaw_plus'):z[empty.qa[n]]=.005
  poses.append(evaluate(empty,z,target,'closed_key_before_ownership'))
  heldq=names_to_q(loaded,empty,z);poses.append(evaluate(loaded,heldq,target,'retained_on_own_support'))
  up=loaded.collision_solve(target+[0,0,.08],loaded.rot,heldq,seconds=20);lift=exact(loaded,target+[0,0,.08],up['q']);poses.append(evaluate(loaded,lift,target+[0,0,.08],'retained_above_support'))
  retreat=names_to_q(empty,loaded,lift)
  for n in ('R_jaw_minus','R_jaw_plus'):retreat[empty.qa[n]]=-.02
  poses.append(evaluate(empty,retreat,target+[0,0,.08],'released_above_support'))
  good=all(x['pass_'] and x['attachment_precision_ok'] for x in poses);row=dict(seed=k,pass_=good,poses=poses,solve=solve,lift_solve=up,min_reserve_mm=min(x['reserve_mm'] for x in poses),starts_independent=True,seed_strategy=f'Independent0.15rad perturbations of validated branches from L{a.warm_layout}/current/same-target family; new scene fully re-solved' if warm or local_good else 'Independent uniform joint starts',actual_initial_q=seed_q.tolist())
  rows.append(row);write(name,dict(job=job,index=ji,config=cfg,problem_sha256=problem,seed_range=[a.seed_lo,a.seed_hi],rows=rows,starts_completed=len(rows),every_start_budget_s=20,algorithm='Collision-aware exact-shape checked IK; full20s per-start branch rescue where needed; fixed-shape impossibility witnesses stop early',elapsed_s=time.monotonic()-beg,empty_model_sha256=hashlib.sha256(empty.xml.encode()).hexdigest(),held_model_sha256=hashlib.sha256(loaded.xml.encode()).hexdigest()))
 print('STATIC',ji,job['id'],sum(r['pass_'] for r in rows),'/',len(rows),'time',round(time.monotonic()-beg,1),flush=True)
print('CHUNK_COMPLETE',a.seed_lo,a.seed_hi,flush=True)
