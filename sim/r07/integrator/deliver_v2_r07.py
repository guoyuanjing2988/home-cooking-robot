"""Evidence-based R07 v2 aggregation; incomplete searches never become passes."""
import sys,json,csv,hashlib,collections,math
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';ID=sys.argv[1]
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
def write(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
cfg=read(f'layouts/{ID}.json');P=read(f'layouts/{ID}_process.json');items=[(ph,sg,ph['id']+'__'+sg['label'].replace(' ','_')) for ph in P['phases'] for sg in ph['segments']]
records=[];witnesses={}
for i,(ph,sg,key) in enumerate(items):
 file=O/'static_v2'/ID/f'{i}.json';r=json.loads(file.read_text()) if file.exists() else dict(index=i,stroke=key,starts=0,rows=[],witness=None,ok=False,complete=False)
 if r.get('witness'):witnesses[key]=r['witness']
 records.append(dict(index=i,stroke=key,logical=ph['id'].split('.')[0],ok=bool(r.get('witness')),starts=r['starts'],required_starts=96,budget_complete=r['starts']>=96,allocated_seconds_per_unresolved_start=20,actual_search_s=sum(t['elapsed_s'] for t in r['rows']),required_poses=len(sg['poses']),verified_poses=len(r['witness']['poses']) if r.get('witness') else 0,status='PASS_REFERENCE_WITNESS' if r.get('witness') else 'UNRESOLVED_SEARCH' if r['starts'] else 'NOT_SEARCHED',source=str(file.relative_to(H)).replace('\\','/'),model_sha256=r.get('model_sha256'),best_failed=r.get('best_failed')))
logical=[dict(id=f'Q{i:02}',ok=bool([r for r in records if r['logical']==f'Q{i:02}']) and all(r['ok'] for r in records if r['logical']==f'Q{i:02}'),failed_strokes=[r['stroke'] for r in records if r['logical']==f'Q{i:02}' and not r['ok']]) for i in range(1,28)]
maps=[]
for directory in sorted((O/'reachability').iterdir()):
 if not directory.is_dir():continue
 sides={}
 for side in ('R','L'):
  path=directory/(side+'.json')
  if not path.exists():continue
  x=json.loads(path.read_text());rows=x['rows'];sides[side]=dict(targets=len(rows),passed=sum(r['pass_'] for r in rows),kinematic_passed=sum(r['kinematic_solutions']>0 for r in rows),actual_starts=sum(r['starts'] for r in rows),elapsed_s=x.get('elapsed_s'),complete=len(rows)==252,file=str(path.relative_to(H)).replace('\\','/'))
 maps.append(dict(layout=directory.name,sides=sides,paired_complete=all(sides.get(s,{}).get('complete') for s in ('R','L'))))
paired=sum(r['paired_complete'] for r in maps);assert paired>=6
summary=dict(schema='r07.v2.static-and-layout-evidence',selected_layout=ID,config=cfg,strokes_passed=len(witnesses),strokes_total=len(items),logical_passed=sum(r['ok'] for r in logical),logical_total=27,logical_phases=logical,required_poses=sum(r['required_poses'] for r in records),verified_poses=sum(r['verified_poses'] for r in records),starts_total=sum(r['starts'] for r in records),search_seconds=sum(r['actual_search_s'] for r in records),strokes_with_96_starts=sum(r['budget_complete'] for r in records),all_strokes_full_search_budget=all(r['budget_complete'] for r in records),acceptance=P['acceptance'],stroke_results=records,reachability_maps=maps,complete_paired_layout_maps=paired,stopping_basis='Alternative (b): more than six documented mount/layout iterations with complete paired-arm reachability evidence, exact mount exclusions and carriage-barrier audits. This is a negative engineering delivery, not recovery to R05 or a proof that every under-cabinet architecture is impossible.',search_limit='The saved count per stroke is literal. A witnessed pass can have fewer than96 starts; unresolved under-budget strokes remain unresolved, never certified impossible. Full96-start coverage of all105 strokes has not been claimed.',source_process=f'results/layouts/{ID}_process.json',process_sha256=hashlib.sha256(json.dumps(P,sort_keys=True).encode()).hexdigest())
if summary['all_strokes_full_search_budget']:summary['search_limit']='Every canonical stroke completed96 or more independent starts with20s available per unresolved start. Accepted branches, reference-rejected pose solutions and genuinely gradient-converged local minima may finish early. Time exhaustion and numerical stagnation are distinguished; failure is not global impossibility.'
write('phase_summary.json',summary);write('best.json',dict(config=cfg,witnesses=witnesses,overall_pass=False));write('config.json',cfg);write('process_v3.json',P);write('torque_envelope.json',read(f'layouts/{ID}_envelope.json'))
seq=read('state_sequence.json');persistent=read('persistent_model.json');lookup={r['stroke']:r for r in records};actual={}
for file in (O/'motion_v2'/ID).glob('internal_*.json'):
 r=json.loads(file.read_text());actual[r['index']]=r
internals=[]
for r in records:
 if r['index'] in actual:internals.append(actual[r['index']]);continue
 internals.append(dict(index=r['index'],stroke=r['stroke'],ok=False,edges=[],status='REJECTED_PRECONDITIONS' if not r['ok'] else 'NO_COMPLETED_PLANNER_RECORD',allocated_planner_budget_s=65,actual_rrt_time_s=0 if not r['ok'] else None,reason='No admitted full stroke endpoint' if not r['ok'] else 'Witness exists; no completed route record. Interrupted multi-stroke chunks retain command ranges and actual elapsed time in bounded logs, without inventing per-stroke attribution.',meal_state_verified=False))
def rejected(kind,**kw):return dict(kind=kind,pass_=False,status='REJECTED_PRECONDITIONS_NO_SEARCH',allocated_planner_budget_s=65,actual_rrt_time_s=0,restarts=0,**kw)
connections=[rejected('expanded_connection',**{k:v for k,v in r.items() if k not in ('pass_','status')},reason=dict(from_static=lookup[r['from_template']]['ok'],to_static=lookup[r['to_template']]['ok'],persistent='Conserved ledger is present; intervening object/jaw/support/actuator paths and source-matched BFP610 interfaces have no execution witnesses')) for r in seq['expanded_connections']]
events=[rejected('event',id=e['id'],name=e['name'],stage=e.get('stage'),reason=e.get('reason') or 'Continuous pose/ownership and working/support event route unverified') for e in seq['events'] if e.get('motion_required')]
idle=read(f'layouts/{ID}_idle.json');write('idle.json',idle)
passing=read(f'motion_v2/{ID}/passing.json') if (O/'motion_v2'/ID/'passing.json').exists() else dict(pass_=False,status='NOT_PLANNED')
write('passing.json',passing)
motion=dict(schema='r07.v2.motion-ledger',selected_layout=ID,meal_pass=False,continuous_meal_execution=False,canonical_internal_passed=sum(r.get('ok',False) for r in internals),canonical_internal_total=len(internals),connections_passed=0,connections_total=len(connections),event_paths_passed=0,event_paths_total=len(events),ledger_events_total=len(seq['events']),internal_paths=internals,connections=connections,event_paths=events,ownership_state_ledger_pass=persistent['ownership_pass'] and not seq['discrete_state_chain_errors'],discrete_state_chain_errors=seq['discrete_state_chain_errors'],persistent_model=persistent,point_displacement_gate_mm=4,planner_policy=dict(budget_s=65,restarts_s=12,shortcut_trials=16,full_compiled_carriage_ranges=True,staging='Admitted populated-scene poses plus randomized staging perturbations',coverage_limit='Actual accepted internal routes are distinct from a connected persistent meal. Rejected meal preconditions have zero search time;65s allocation is not represented as time spent.'),parking=idle,passing=passing)
write('motion.json',motion)
# Cost rows are the unchanged historical engineering allowance, with one reserve.
cost=read('cost_summary.json');assert abs(cost['base_cny']*.15-cost['reserve_cny'])<.011 and cost['safety_package_count']==1
with (H/'history/v1/results/costs.csv').open(newline='',encoding='utf-8') as file:costrows=list(csv.DictReader(file))
for row in costrows:
 if 'compact wall rails' in row['item'] and cfg['lane_count']==1:
  row['item']='One compact wall rail, two carriages, home brakes, chains and brackets';row['basis']='Retain43000CNY conservative integrated rail-system allowance for two braked carriages and revised mounts. Single lane preserves carriage order; no passing, portal or elevator credited.'
with (O/'costs.csv').open('w',newline='',encoding='utf-8') as file:w=csv.DictWriter(file,fieldnames=list(costrows[0]));w.writeheader();w.writerows(costrows)
schedule=read('schedule.json');schedule.update(schema='r07.v2.executed-path-schedule',selected_layout=ID,meal_pass=False,prep_min=None,verified_prep_min=None,estimated_meal_prep_min=None,executed_meal_segments=0,auxiliary_executed_path_time_s=None,accepted_internal_paths=[],reason='No connected executed meal. Only independently checked isolated internal paths receive local duration, never a meal makespan.')
for key in ('auxiliary_segment_times_s','auxiliary_scope'):schedule.pop(key,None)
write('schedule.json',schedule)
iterations=[]
def add(kind,id,**kw):iterations.append(dict(kind=kind,id=id,layout=kw.get('layout',''),seed=kw.get('seed',''),starts=kw.get('starts',0),pass_=kw.get('pass_',False),budget_s=kw.get('budget_s',''),actual_s=kw.get('actual_s',''),status=kw.get('status',''),evidence=kw.get('evidence','')))
with (H/'history/v1/results/iterations.csv').open(newline='',encoding='utf-8') as file:
 for old in csv.DictReader(file):add('v1_'+old['kind'],old['id'],layout='v1',seed=old.get('seed'),starts=old.get('starts'),pass_=old.get('pass_')=='True',budget_s=old.get('budget_s'),actual_s=old.get('actual_s'),status='HISTORICAL_SUPERSEDED: '+old.get('status',''),evidence='history/v1/'+old.get('evidence',''))
for file in sorted((O/'layouts').glob('L*.json')):
 if len(file.stem)==3:
  x=json.loads(file.read_text());add('layout',file.stem,layout=file.stem,status=x['reason'],evidence=str(file.relative_to(H)).replace('\\','/'))
for m in maps:
 for side,x in m['sides'].items():add('reachability',m['layout']+'_'+side,layout=m['layout'],starts=x['actual_starts'],actual_s=x['elapsed_s'],pass_=x['complete'],status=f"{x['passed']}/{x['targets']} independent empty-arm targets;12 allocated starts/target, early success; not static budget",evidence=x['file'])
for file in sorted((O/'static_v2').glob('*/*.json')):
 x=json.loads(file.read_text())
 for r in x['rows']:add('static_start',x['stroke'],layout=x['layout'],seed=r['seed'],starts=1,pass_=r['ok'],budget_s=r['allocated_s'],actual_s=r['elapsed_s'],status='full_reference_pass' if r['ok'] else 'unresolved_start',evidence=str(file.relative_to(H)).replace('\\','/'))
for file in sorted((O/'static_v2_numerical_stagnation').glob('*/*.json')):
 x=json.loads(file.read_text())
 for r in x['rows']:add('superseded_stagnation',x['stroke'],layout=x['layout'],seed=r['seed'],starts=1,pass_=False,budget_s=r['allocated_s'],actual_s=r['elapsed_s'],status='Small numerical step with non-small gradient: excluded from required96-start count; retained only as diagnostic',evidence=str(file.relative_to(H)).replace('\\','/'))
for file in sorted((H/'audit').glob('*.resource.json')):
 x=json.loads(file.read_text());add('bounded_run',file.stem,pass_=x['exit_code']==0,budget_s=x['timeout_s'],actual_s=x['elapsed_s'],status=x['status'],evidence=str(file.relative_to(H)).replace('\\','/'))
for file in sorted((O/'layouts').glob('*_park_iteration_*.json')):
 x=json.loads(file.read_text());add('populated_park_search',file.stem,layout=x['config']['id'],pass_=x['pass_'],budget_s=820,actual_s=x['elapsed_s'],status=f"{len(x['hits'])} forbidden records; full stored objects and completed food retained",evidence=str(file.relative_to(H)).replace('\\','/'))
for file in sorted((O/'layouts').glob('*_idle.json')):
 x=json.loads(file.read_text())
 for r in x['fold_paths']:
  p=r['planner'];add('fold_unfold',str(r['index']),layout=x['layout'],starts=p.get('seeds_tried',0),pass_=r['pass_'],budget_s=p.get('allocated_budget_s',65),actual_s=p.get('planner_time_s',0),status=r.get('reason') or 'Full populated fold and reverse unfold accepted',evidence=str(file.relative_to(H)).replace('\\','/'))
  for ti,trial in enumerate(r.get('staging_attempts',[])):
   if trial.get('via_hits'):add('fold_staging_precondition',f"{r['index']}.{ti}",layout=x['layout'],status='Intermediate full-scene configuration rejected before planning',actual_s=0,evidence=str(file.relative_to(H)).replace('\\','/'))
   for li,leg in enumerate(trial['legs']):add('fold_staging_leg',f"{r['index']}.{ti}.{li}",layout=x['layout'],starts=leg.get('seeds_tried',0),pass_=leg['ok'],budget_s=leg['allocated_budget_s'],actual_s=leg['planner_time_s'],status='One arm moves; other arm and full populated scene remain collision obstacles',evidence=str(file.relative_to(H)).replace('\\','/'))
for file in sorted((O/'layouts').glob('*_fixed_obstructions.json')):
 x=json.loads(file.read_text());add('joint_independent_layout_obstruction',file.stem,layout=x['layout'],pass_=not x['all_poses_rejected'],status=f"{len(x['global_fixed_obstructions'])} fixed obstruction records; candidate-specific proof only",evidence=str(file.relative_to(H)).replace('\\','/'))
for r in internals:
 for i,e in enumerate(r.get('edges',[])):add('internal_rrt',f"{r['index']}.{i}",layout=ID,seed=e.get('seed'),starts=e.get('seeds_tried',0),pass_=e['ok'],budget_s=e.get('allocated_budget_s',65),actual_s=e.get('planner_time_s',0),status=e.get('route',e.get('reason','')),evidence=f'results/motion_v2/{ID}/internal_{r["index"]}.json')
for r in connections+events:add(r['kind'],r.get('id',r.get('index')),layout=ID,budget_s=65,actual_s=0,status=r['status'],evidence='results/motion.json')
with (O/'iterations.csv').open('w',newline='',encoding='utf-8') as file:w=csv.DictWriter(file,fieldnames=list(iterations[0]));w.writeheader();w.writerows(iterations)
print('V2',ID,'strokes',len(witnesses),'internal',motion['canonical_internal_passed'],'maps',paired,'96-start strokes',summary['strokes_with_96_starts'],'iterations',len(iterations),flush=True)
