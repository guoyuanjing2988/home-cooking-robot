"""Assemble current evidence without turning conditional paths into a meal."""
import os,sys,json,csv,hashlib,statistics,copy,shutil,collections
from pathlib import Path
os.environ['R07_LAYOUT']=sys.argv[1]
import persistent_v5_r07 as p
v=p.v;H=v.H;O=v.O;ID=v.ID
def read(n):return json.loads((n if isinstance(n,Path) else O/n).read_text(encoding='utf-8-sig'))
def write(n,d):(O/n).write_text(json.dumps(d,indent=2,allow_nan=False))
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
cfg=read('layouts/'+ID+'.json');P=read('layouts/'+ID+'_process_v4.json');fresh=read('fresh_admission.json');assert fresh['layout']==ID
write('config.json',cfg);write('process_v5.json',P);write('process_v4.json',P);write('process_v3.json',P);write('torque_envelope.json',read('layouts/'+ID+'_envelope.json'))
contacts=[]
for _,sg,_ in v.items:
 for hands in sg['poses']:
  for h in hands.values():
   for contact in h.get('contacts',[]):
    if contact not in contacts:contacts.append(contact)
write('intended_contacts.json',dict(layout=ID,contacts=contacts,additional_binding_policy='Named finger/object grasp faces are instantiated per persistent object; see binding_v5_r07.py and each connection file. No working permission on free transfers.'))
layouts=[]
for number in range(54,max(72,int(ID[1:]))+1):
 label='L'+str(number);file=O/'layouts'/f'{label}.json'
 if not file.exists():continue
 c=read(file);mp=O/'reachability'/label/'R.json';stats=[read(f) for f in (O/'static_v5'/label).glob('*.json')]
 if not mp.exists() and not stats:continue
 maps=[]
 if mp.exists():
  d=read(mp);maps=[dict(side='R',clear=sum(bool(x['pass_']) for x in d['rows']),total=len(d['rows']),complete=d['complete'],evidence=str(mp.relative_to(H)),current_cover_and_targets=(H/'audit'/f'{label}_map_v5_refreshed.json').exists())]
 layouts.append(dict(layout=label,reason=c['reason'],mount_deg=c['mount_deg'],height_m=c['height'],stand_off_y_m=c['front_mount_y'],maps=maps,static_attempted=len(stats),complete96=sum(x.get('complete',False) for x in stats),static_pass=sum(x.get('complete',False) and bool(x.get('witness')) for x in stats),starts=sum(x['starts'] for x in stats),evidence=str(file.relative_to(H))))
write('layout_iterations_v5.json',dict(layouts=layouts,new_layouts_with_evidence=len(layouts),scope='Finite layout-specific searches, not a proof against the under-cabinet architecture. Maps omit movable stations and give proposals only. Unexecuted configurations L62/L63/L66 are not counted.'))
rows=fresh['rows'];passed=sum(r['ok'] for r in rows)
summary=dict(schema='r07.v5.static-summary',selected_layout=ID,strokes_passed=passed,strokes_total=len(rows),static_fraction=passed/len(rows),poses_passed=sum(len(r.get('reference',{}).get('poses',[])) for r in rows if r['ok']),stroke_results=rows,required_starts=96,seconds_per_unresolved_start=20,complete96=sum(r['complete'] for r in rows),unresolved_or_unattempted=[r['index'] for r in rows if not r['ok']],acceptance=P['acceptance'],stop_condition='b',new_documented_layout_iterations=len(layouts),stop_condition_a=False,full_meal_pass=False,quality_qualified=False,budget_scope='96 completed starts required for positive count. Unresolved starts have20s available; accepted, converged local minimum, full-reference rejection and exhausted budget are recorded separately.',count_scope='59 full-geometry robot templates; static admission does not certify appliance operation or a persistent connected meal.')
write('phase_summary.json',summary);write('best.json',dict(layout=ID,witnesses={r['stroke']:r['reference'] for r in rows if r['ok']}))
internal=[read(f) for f in sorted((O/'motion_v5'/ID).glob('internal_*.json'),key=lambda f:int(f.stem.split('_')[-1]))]
conn=[read(O/'connections_v5'/ID/f'{i}.json') for i in range(len(p.expanded())-1)]
assert all(r['planner_ran'] and r['allocated_budget_s']>=60 for r in conn)
w=p.World();initial=w.snapshot();ch,_=w.build(0,None);(H/'models/persistent_meal.xml').write_text(ch.xml)
events=[]
for prod in ('carrot','potato','leafy_greens','tomato'):
 if prod in ('carrot','potato'):events.append(dict(product=prod,kind='declared_transformation',operation='peel',station='linear_peeler_holder',duration_s=6*2*.160/.0034/.20,source='https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf',timing_basis='Six160mm outward/return strokes at3.4mm/s and20percent duty, derived design allowance, not measured peeling time',quality_assumed=True,executed=False))
 events.append(dict(product=prod,kind='declared_transformation',operation='slices' if prod in ('carrot','potato') else 'sections' if prod=='leafy_greens' else 'wedges',station='BFP610_processing_bowl' if prod in ('carrot','potato') else 'secondary_work_face',duration_s=None,timing_status='Exact batch timing not published/qualified; not replaced by zero',quality_assumed=True,executed=False))
for name,sec in [('bok_choy_soak',600),('potato_drain',30)]:events.append(dict(name=name,kind='timed_process',duration_s=sec,executed=False))
for i in range(3):events.append(dict(name='potato_fresh_starch_rinse_'+str(i+1),kind='water_change',duration_s=None,executed=False))
physical=['Full food loading/release into guarded holder','Peeler lid/holder full sweep, close/interlock, actuator cycle, stop/open','BFP610 full pusher, lid, disc and batch bowl handling with ordinary controls and unplugging','Secondary guard and full cassette transfers','Separate leaf/basal-crease handling without shrinking robot-touched geometry','Bulk food transfer in full containers to each output bowl','Return all tools/containers and final water shutoff']
for name in physical:events.append(dict(name=name,kind='robot_or_interface_obligation',executed=False,geometry_may_not_be_abstracted=True))
cond=sum(r['pass_'] for r in conn);geometric=sum(r.get('geometric_connection_pass',r['pass_']) for r in conn)
compact=[]
for r in conn:
 compact.append({k:r.get(k) for k in ('connection','from_stroke','to_stroke','planner_ran','allocated_budget_s','actual_planner_s','status','pass_','geometric_connection_pass','executed','blockers','required_events','mass_conserved')})
 compact[-1].update(evidence=f'results/connections_v5/{ID}/{r["connection"]}.json',sha256=digest(O/'connections_v5'/ID/f'{r["connection"]}.json'))
seq=dict(schema='r07.v5.persistent-meal',layout=ID,mass_input_kg=.57,initial_state=initial,executed_state=initial,expanded_strokes=p.expanded(),expanded_connections=compact,events=events,discrete_state_chain_errors=[],executed_prefix_connections=0,executed_products=[],status='No completed connected product; later attempts are conditional scenarios after failed prefix, not committed motion.',transformation_policy='Food-only mass-conserving station changes with density/packing-derived bulk beds. Full robot-touched solids retained; unqualified direct bulk grasps retain full original geometry and receive no pass.',conditional_state_limit='Intermediate food loading and physical appliance controls are explicit unexecuted prerequisites. A conditional diagnostic can expose geometric blockers but cannot establish those actions.',duration_limit='P16 cycle derived from published actuator data; exact BFP610 and secondary per-batch times remain unknown.')
write('state_sequence.json',seq);write('persistent_model.json',dict(layout=ID,model_xml='models/persistent_meal.xml',model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),unique_food_bodies=4,full_initial_objects=len(w.objects),food_mass_kg=.57,transaction_checks='results/state_model_regression_v5.json',executable_connection_scenarios=True,full_recipe_executed=False,conditional_state_limit=seq['conditional_state_limit']))
motion=dict(schema='r07.v5.motion',layout=ID,meal_pass=False,internal_pass=sum(r['ok'] for r in internal),internal_total=len(rows),internal_paths=internal,connections_pass=0,connections_total=len(conn),connections=compact,all_connections_planner_ran=all(r['planner_ran'] for r in conn),conditional_connection_pass=cond,geometric_connection_pass=geometric,executed_prefix_connections=0,event_paths=events,event_paths_total=len(events),event_paths_pass=0,persistent_model_executable=True,full_recipe_executable=False,planner_budget_s=65,point_step_limit_mm=4,scope='All connections actually planned in a persistent populated conditional state. Individual geometric passes are separate from executable state transitions. None is credited as an executed meal after a failed prefix.')
write('motion.json',motion)
pair_counts=collections.Counter();status_counts=collections.Counter(r['status'] for r in conn)
for r in conn:
 for leg in r['legs']:
  for end in leg.get('endpoint_geometry',[]):
   blocker=end.get('blocker') or {}
   for hit in blocker.get('blockers',[]):
    if hit.get('pair'):pair_counts[' / '.join(sorted(hit['pair']))]+=1
write('connection_summary_v5.json',dict(layout=ID,attempted=len(conn),actual_planner_seconds=sum(r['actual_planner_s'] for r in conn),allocated_leg_seconds=sum(r['allocated_budget_s'] for r in conn),status_counts=dict(status_counts),geometric_pass=geometric,conditional_pass=cond,executed_prefix=0,endpoint_blocker_counts=dict(pair_counts.most_common()),scope='Endpoint pair frequency across attempted legs; counts are diagnostics, not an infeasibility certificate. Full per-connection data remain authoritative.'))
idle=read('layouts/'+ID+'_idle.json')
for suffix,key in [('fold_v5','task_fold'),('fold_alternatives_v5','alternative_fold_goals'),('return_v5','meal_end_return_diagnostic')]:
 f=O/'layouts'/f'{ID}_{suffix}.json';idle[key]=read(f) if f.exists() else dict(pass_=False,status='NOT_ATTEMPTED')
fold=any(idle[k].get('pass_',False) for k in ('task_fold','alternative_fold_goals'))
idle.update(pass_=False,fold_unfold_pass=fold,meal_end_to_park_verified=False,status='Prospective populated park checked separately; connected meal and meal-end return not executed.')
write('idle.json',idle);write('passing.json',dict(layout=ID,applicable=False,pass_=None,reason='One full UR5e, one carriage, one wall lane; no crossing event.',model_xml=idle['model_xml'],q_crossing=idle['q']))
schedule=dict(schema='r07.v5.executed-timing',layout=ID,prep_min=None,meal_executed=False,home_speed_limits={'rail_m_s':.1,'joint_rad_s':.35,'all_geometry_point_m_s':.05,'rail_point_acceleration_m_s2':.3,'joint_acceleration_rad_s2':.35},mandatory_process_times={'bok_choy_soak_s':600,'potato_drain_s':30,'potato_fresh_rinses':3,'peeler_design_cycle_per_root_s':6*2*.160/.0034/.20,'BFP610_feed_cycle_and_stop_s':None,'secondary_cut_s':None,'sink_fill_and_drain_s':None},accepted_internal_paths=[],reason='No executed connected meal. Isolated checked paths are timed separately. Unknown appliance batch times stay unknown; declared food quality does not provide a cycle time.')
write('schedule.json',schedule)
values={}
for r in rows:
 if not r['ok']:continue
 for po in r['reference']['poses']:
  for cat,d in po['min_clearance'].items():values.setdefault(cat,[]).append(d['reserve_mm'])
dist={k:dict(samples=len(a),min_mm=min(a),median_mm=statistics.median(a),fraction_at_least10mm=sum(round(x,9)>=10 for x in a)/len(a),all_values_mm=a) for k,a in values.items()}
write('clearance.json',dict(schema='r07.v5.clearance',layout=ID,static_pose_category_minimum_reserves=dist,idle_snapshot_minima=idle.get('min_clearance'),meal_distribution=None,robustness_pass=False,scope='Worst eligible pair in each category per pose/state, not diluted by distant pairs. Gates unchanged;10mm extra is a design objective, not established by a tiny positive numerical reserve.'))
refined_file=O/'clearance_refinement_v5.json'
if refined_file.exists():
 refined=read(refined_file)
 if refined.get('layout')==ID:
  clear=read('clearance.json');clear['refined_reserve_assessment']={key:refined[key] for key in ('complete','counts','distribution','method')};clear['refined_reserve_assessment']['source']='results/clearance_refinement_v5.json';write('clearance.json',clear)
archive=H/'history/v5_delivery_inputs';archive.mkdir(exist_ok=True)
for name in ('costs.csv','iterations.csv'):
 if not (archive/name).exists():shutil.copy2(O/name,archive/name)
old=list(csv.DictReader((archive/'costs.csv').open(encoding='utf-8-sig')));cost=[x for x in old if x['item'] not in ('TOTAL','One15percent project reserve','Starfrit Rotato Express commodity peeler','Complete peeler mechanical guard and holder retrofit')]
for item,amount,basis in [('P16-200-256-12-P actuator, LAC and12V supply',1600,'CNY planning allowance; OEM supports relay/H-bridge/LAC operation; no FX quote or purchase'),('Full linear bearing guide and root holder',2300,'Custom mechanical allowance; guide takes radial load above actuator4N lateral allowance'),('Full custom peeler mechanical guards and hinge',2500,'Mechanical allowance only; interlock/control already in single home-safety package')]:cost.append(dict(configuration='r07_under_cabinet_candidate',item=item,quantity=1,total_cny=amount,basis=basis,status='PLANNING_ALLOWANCE_NOT_PASSING'))
base=round(sum(float(x['total_cny']) for x in cost),2);reserve=round(base*.15,2);total=round(base+reserve,2)
for item,value in [('One15percent project reserve',reserve),('TOTAL',total)]:cost.append(dict(configuration='r07_under_cabinet_candidate',item=item,quantity=1,total_cny=value,basis='One15% project reserve; one18000CNY home-safety package',status='PLANNING_ALLOWANCE_NOT_PASSING'))
with (O/'costs.csv').open('w',newline='',encoding='utf-8') as f:writer=csv.DictWriter(f,fieldnames=old[0].keys());writer.writeheader();writer.writerows(cost)
write('cost_summary.json',dict(base_cny=base,reserve_cny=reserve,total_cny=total,cheapest_passing_cny=None,safety_package_count=1,reserve_count=1,qualified_quote=False))
history=list(csv.DictReader((archive/'iterations.csv').open(encoding='utf-8-sig')));fields=list(history[0]);iterations=history.copy()
def add(**kw):iterations.append({k:kw.get(k,'') for k in fields})
for lay in layouts:
 label=lay['layout'];add(kind='v5_layout',id=label,layout=label,starts=lay['starts'],pass_=False,status=lay['reason'],evidence=lay['evidence'])
 for mp in lay['maps']:add(kind='v5_reach_map',id='R',layout=label,pass_=mp['clear'],status=f"{mp['clear']}/{mp['total']} targets; map proposals only",evidence=mp['evidence'])
 for f in (O/'static_v5'/label).glob('*.json'):
  d=read(f)
  inherited=d.get('inheritance',{}).get('source_starts',0)
  for r in d['rows']:
   reused=r['seed']<inherited
   add(kind='v5_same_problem_reuse' if reused else 'v5_static_start',id=d['index'],layout=label,seed=r['seed'],starts=0 if reused else 1,pass_=r['ok'],budget_s=r['allocated_s'],actual_s=0 if reused else r['elapsed_s'],status=('Exact geometry/target reuse from '+d['inheritance']['source']+'; original termination: ' if reused else '')+r['termination']['kind'],evidence=str(f.relative_to(H)))
 for suffix in ('idle','fold_v5','fold_alternatives_v5','return_v5'):
  f=O/'layouts'/f'{label}_{suffix}.json'
  if f.exists():add(kind='v5_'+suffix,id=label,layout=label,pass_=read(f).get('pass_',False),status='Full physical scene; no executed meal credit',evidence=str(f.relative_to(H)))
 if label!=ID:
  for f in (O/'connections_v5'/label).glob('*.json'):
   d=read(f);add(kind='v5_prior_connection_diagnostic',id=d.get('connection',f.stem),layout=label,pass_=False,budget_s=d.get('allocated_budget_s'),actual_s=d.get('actual_planner_s'),status='Historical model/method only; no current admission. '+d.get('status','See prior record'),evidence=str(f.relative_to(H)))
for r in internal:add(kind='v5_internal',id=r['index'],layout=ID,pass_=r['ok'],budget_s=65,status='Independent<=4mm full-load replay; isolated template',evidence=f'results/motion_v5/{ID}/internal_{r["index"]}.json')
for r in conn:add(kind='v5_connection',id=r['connection'],layout=ID,pass_=r['pass_'],budget_s=r['allocated_budget_s'],actual_s=r['actual_planner_s'],status=r['status'],evidence=f'results/connections_v5/{ID}/{r["connection"]}.json')
for f in sorted((H/'audit').glob('v5_*.resource.json')):
 d=read(f);add(kind='v5_bounded_run',id=f.stem,starts=0,pass_=d.get('exit_code')==0,budget_s=d['timeout_s'],actual_s=d['elapsed_s'],status=f"Process result only, not task admission; exit={d.get('exit_code')}, peak_MiB={d['peak_MiB']}",evidence=str(f.relative_to(H)))
add(kind='v5_resource_incident',id='worker_overlap',pass_=False,status='At most5 numerical workers briefly overlapped; allowed4; overlap upper bound21s. Extra job stopped.',evidence='audit/v5_worker_overlap_incident.json')
with (O/'iterations.csv').open('w',newline='',encoding='utf-8') as f:writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(iterations)
print('PREPARED',ID,passed,'/',len(rows),'internal',motion['internal_pass'],'connection attempts',len(conn),'conditional',cond,'CNY',total)
