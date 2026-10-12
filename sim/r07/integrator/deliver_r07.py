"""Assemble negative results without inheriting R05 successes or invented paths."""
import json,csv,hashlib,math,collections
from pathlib import Path
H=Path(__file__).resolve().parent; O=H/'results'
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
def write(n,x):
 if n=='schedule.json' and (O/n).exists():
  before=read(n)
  for key in ('auxiliary_executed_path_time_s','auxiliary_segment_times_s','auxiliary_scope','timing_method'):
   if key in before and before[key] is not None:x[key]=before[key]
 (O/n).write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
P=read('process_v3.json');config=read('config.json');seq=read('state_sequence.json')
rows=[read('final_static/'+str(i)+'.json') for i in range(105)]
assert len(rows)==105 and len({r['stroke'] for r in rows})==105
logical=[dict(id=f'Q{i:02d}',ok=all(r['ok'] for r in rows if r['logical']==f'Q{i:02d}'),failed_strokes=[r['stroke'] for r in rows if r['logical']==f'Q{i:02d}' and not r['ok']]) for i in range(1,28)]
pose_n=sum(len(r['poses']) for r in rows)
summary=dict(schema='r07.full-fresh-static-replay',config=config,strokes_passed=sum(r['ok'] for r in rows),strokes_total=105,logical_passed=sum(r['ok'] for r in logical),logical_total=27,logical_phases=logical,poses_replayed=pose_n,starts_total=sum(r['search_starts'] for r in rows),fresh_continuation_solves=sum(r['fresh_continuation_solves'] for r in rows),verified_witnesses=sum(r['ok'] for r in rows),acceptance=P['acceptance'],process_sha256=hashlib.sha256((O/'process_v3.json').read_bytes()).hexdigest(),stroke_results=[dict(id=r['stroke'],ok=r['ok'],file='results/final_static/'+str(i)+'.json',starts=r['search_starts'],poses=len(r['poses']),model_sha256=r['model_sha256']) for i,r in enumerate(rows)],scope='All canonical poses freshly re-solved and replayed on R07 geometry, including rated-envelope statics, payload, grip and all-pair gaps. Failed candidates are diagnostics, not witnesses. No R05 accepted pose is inherited.')
write('phase_summary.json',summary)
write('best.json',dict(config=config,witnesses={r['stroke']:r['witness'] for r in rows if r['ok']},overall_pass=False,manufacturing_and_food_quality_qualified=False))
lookup={r['stroke']:r for r in rows}
seq['ownership_pass']=read('persistent_model.json')['ownership_pass'] and not read('persistent_model.json')['ownership_invariant_errors'] and not seq['discrete_state_chain_errors']
def endpoint_reason(key):
 r=lookup.get(key)
 return 'Template not present in canonical replay' if r is None else None if r['ok'] else 'No accepted R07 pose/load/grip/clearance stroke witness: results/final_static/'+str(r['index'])+'.json'
def blocked(kind,**kw):return dict(kind=kind,pass_=False,allocated_planner_budget_s=65,actual_rrt_time_s=0,restarts=0,solutions_found=0,verified_witnesses=0,status='REJECTED_PRECONDITIONS_NO_SEARCH',**kw)
internals=[blocked('internal',id=r['stroke'],from_pose=0,to_pose=len(r['poses'])-1,reason=endpoint_reason(r['stroke'])) for r in rows]
connections=[blocked('expanded_connection',**{k:v for k,v in c.items() if k not in ('pass_','status')},reason=dict(from_endpoint=endpoint_reason(c['from_template']),to_endpoint=endpoint_reason(c['to_template']),persistent_binding='No complete continuous attachment/actuator/partition executor; BFP610 OEM interfaces absent')) for c in seq['expanded_connections']]
events=[blocked('event',id=e['id'],name=e['name'],stage=e.get('stage'),reason=e.get('reason','Unverified geometry, continuous handoff, jaws/support/latch or working path'),state_chain_present=bool(e.get('state_before') is not None)) for e in seq['events'] if e.get('motion_required')]
canonical=[blocked('canonical_connection',index=i,from_stroke=a['stroke'],to_stroke=b['stroke'],reason=[endpoint_reason(a['stroke']),endpoint_reason(b['stroke'])]) for i,(a,b) in enumerate(zip(rows,rows[1:]))]
aux=read('aux_paths.json');passing=read('passing.json');idle=read('idle.json')
motion=dict(schema='r07.motion-admission-ledger',meal_pass=False,continuous_meal_execution=False,canonical_internal_passed=0,canonical_internal_total=len(internals),connections_passed=0,connections_total=len(connections),event_paths_passed=0,event_paths_total=len(events),ledger_events_total=len(seq['events']),internal_paths=internals,connections=connections,event_paths=events,canonical_connection_diagnostics=canonical,persistent_scene='models/persistent_meal.xml',persistent_model=read('persistent_model.json'),discrete_state_chain_errors=seq['discrete_state_chain_errors'],ownership_state_ledger_pass=seq['ownership_pass'],point_displacement_gate_mm=4,planner_policy=dict(budget_s=65,method='Copied RRT-Connect, 12s restarts, folded staging proposals, 16 shortcut trials, full <=4mm acceptance replay',missing_endpoint_policy='Reject invalid endpoint roots before RRT. Allocation is not time spent; no zero-time rejection is represented as a 60s search.',coverage_limit='Every obligation is enumerated and its preconditions audited. Meal RRT searches were not run because no accepted R07 canonical endpoint and no complete persistent interface executor exist. This round does not satisfy full-meal planner execution coverage.'),auxiliary_executed_path=aux,passing=passing,parking=idle)
write('motion.json',motion)
# Historical engineering allowances; one reserve, one safety package.
with (O/'inherited_costs.csv').open(newline='',encoding='utf-8') as f:cost=[r for r in csv.DictReader(f) if r['configuration']=='household_wall_candidate' and r['item'] not in ('TOTAL','One15percent project reserve')]
for r in cost:
 r['configuration']='r07_under_cabinet_candidate';r['status']='PLANNING_ALLOWANCE_UNQUALIFIED_NOT_PASSING'
 if 'Two independent lanes' in r['item']:r.update(item='Two compact wall rails, guides, carriages, home brakes, chains and brackets',basis='Retained 43000 CNY strong-wall planning allowance; no portal, legs, storage elevator or pallet. Wall/site and actual brake qualification outstanding.')
 if 'processor' in r['item'].lower() or 'slicer' in r['item'].lower() or 'BFP' in r['item'] or 'Robot-Coupe' in r['item']:r.update(item='Breville BFP610 batch processor and interfaces',basis='Inherited household candidate 4000 CNY allowance, not a quote; exact automation interfaces unqualified.')
base=round(sum(float(r['total_cny']) for r in cost),2);reserve=round(base*.15,2);total=round(base+reserve,2)
cost += [dict(configuration='r07_under_cabinet_candidate',item='One15percent project reserve',quantity=1,total_cny=reserve,basis='15% of all base items applied exactly once',status='PLANNING_ALLOWANCE_UNQUALIFIED_NOT_PASSING'),dict(configuration='r07_under_cabinet_candidate',item='TOTAL',quantity=1,total_cny=total,basis='Includes one safety package and one reserve',status='PLANNING_ALLOWANCE_UNQUALIFIED_NOT_PASSING')]
with (O/'costs.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(cost[0]));w.writeheader();w.writerows(cost)
write('cost_summary.json',dict(base_cny=base,reserve_cny=reserve,total_cny=total,reserve_rate=.15,safety_package_count=1,cheapest_passing_configuration=None,current_supplier_quote=False))
# Do not add disconnected work strokes to manufacture a meal duration.
write('schedule.json',dict(schema='r07.executed-path-schedule',meal_pass=False,prep_min=None,verified_prep_min=None,estimated_meal_prep_min=None,executed_meal_segments=0,auxiliary_executed_path_time_s=None,speed_policy=dict(joint_rad_s=.35,joint_accel_rad_s2=.35,empty_rail_m_s=.2,loaded_rail_m_s=.1,rail_accel_m_s2=.3,max_geometry_point_m_s=.05,geometry_point_accel_m_s2=.3,waypoint_rest_to_rest=True),required_process_timers=dict(bok_choy_soak_s=600,sink_fill_s=501.6,sink_volume_L=50.16,flow_L_min=6,potato_fresh_water_rinses=3,colander_drain_s=30,inspection_s=90,end_cleaning_s=300),appliance_times=dict(BFP610_start_stop_and_batch_disassembly_s=None,reason='No executed or experimentally sourced automated batch cycle; R211 continuous-discharge time cannot be reused'),reason='No connected executed meal. Null is unavailable, not zero minutes. Process timers alone do not establish a schedule.'))
iterations=[]
for directory in ('static_iteration_1','static'):
 for file in sorted((O/directory).glob('*.json'),key=lambda p:int(p.stem)):
  x=json.loads(file.read_text());
  for r in x.get('rows',[]):iterations.append(dict(kind=directory,id=str(x.get('index',file.stem)),seed=r.get('seed',r.get('k',r.get('raw',{}).get('k'))),starts=1,pass_=bool(r.get('ok',False)),budget_s='',actual_s='',status='fresh_search_diagnostic',evidence=str(file.relative_to(H)).replace('\\','/')))
for r in rows:iterations.append(dict(kind='all_pose_continuation',id=r['stroke'],seed='',starts=r['fresh_continuation_solves'],pass_=r['ok'],budget_s='',actual_s='',status='full_static_reference_replay',evidence='results/final_static/'+str(r['index'])+'.json'))
for typ,arr in [('internal',internals),('expanded_connection',connections),('event',events),('canonical_connection',canonical)]:
 for i,r in enumerate(arr):iterations.append(dict(kind=typ,id=r.get('id',r.get('index',i)),seed='',starts=0,pass_=False,budget_s=65,actual_s=0,status=r['status'],evidence='results/motion.json'))
for file in sorted((H/'audit').glob('*.resource.json')):
 x=json.loads(file.read_text());iterations.append(dict(kind='bounded_run',id=file.stem,seed='',starts='',pass_=x['exit_code']==0,budget_s=x['timeout_s'],actual_s=x['elapsed_s'],status=x['status'],evidence=str(file.relative_to(H)).replace('\\','/')))
for name,x in [('passing',passing['planner']),('aux_local',aux['planner'])]:iterations.append(dict(kind='rrt',id=name,seed=x['seed'],starts=x['seeds_tried'],pass_=x['ok'],budget_s=x['allocated_budget_s'],actual_s=x['planner_time_s'],status=x.get('route',x.get('reason')),evidence='results/'+('passing.json' if name=='passing' else 'aux_paths.json')))
with (O/'iterations.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(iterations[0]));w.writeheader();w.writerows(iterations)
print(json.dumps(dict(strokes=summary['strokes_passed'],poses=pose_n,starts=summary['starts_total'],connections=len(connections),events=len(events),cost=total,sequence_keys=list(seq),iteration_rows=len(iterations))))
