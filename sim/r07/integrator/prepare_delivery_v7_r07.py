"""Assemble current evidence without turning conditional paths into a meal."""
import os,sys,json,csv,hashlib,statistics,copy,shutil,collections
from pathlib import Path
os.environ['R07_LAYOUT']=sys.argv[1]
import persistent_v7_r07 as p
v=p.v;H=v.H;O=v.O;ID=v.ID
def read(n):return json.loads((n if isinstance(n,Path) else O/n).read_text(encoding='utf-8-sig'))
def write(n,d):(O/n).write_text(json.dumps(d,indent=2,allow_nan=False))
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
cfg=read('layouts/'+ID+'.json');P=read('layouts/'+ID+'_process_v4.json');fresh=read('fresh_admission.json');assert fresh['layout']==ID
write('config.json',cfg);write('process_v7.json',P);write('process_v4.json',P);write('process_v3.json',P);write('torque_envelope.json',read('layouts/'+ID+'_envelope.json'))
contacts=[]
for _,sg,_ in v.items:
 for hands in sg['poses']:
  for h in hands.values():
   for contact in h.get('contacts',[]):
    if contact not in contacts:contacts.append(contact)
write('intended_contacts.json',dict(layout=ID,contacts=contacts,additional_binding_policy='Named finger/object grasp faces are instantiated per persistent object; see binding_v7_r07.py and each connection file. No working permission on free transfers.'))
layouts=[]
for number in range(90,102):
 label='L'+str(number);file=O/'layouts'/f'{label}.json'
 if not file.exists():continue
 c=read(file);mp=O/'reachability'/label/'R.json';stats=[read(f) for f in (O/'static_v7'/label).glob('*.json')]
 screenfile=O/'layouts'/f'{label}_screen_v7.json';foldfile=O/'layouts'/f'{label}_fold_v7.json'
 if not mp.exists() and not stats and not screenfile.exists():continue
 maps=[]
 if mp.exists():
  d=read(mp);maps=[dict(side='R',clear=sum(bool(x['pass_']) for x in d['rows']),total=len(d['rows']),complete=d['complete'],evidence=str(mp.relative_to(H)),current_cover_and_targets=(H/'audit'/f'{label}_map_v7_refreshed.json').exists())]
 layouts.append(dict(layout=label,reason=c['reason'],mount_deg=c['mount_deg'],height_m=c['height'],stand_off_y_m=c['front_mount_y'],maps=maps,static_attempted=len(stats),complete96=sum(x.get('complete',False) for x in stats),static_pass=sum(x.get('complete',False) and bool(x.get('witness')) for x in stats),starts=sum(x['starts'] for x in stats),evidence=str(file.relative_to(H))))
 layouts[-1]['screen']=read(screenfile) if screenfile.exists() else None
 layouts[-1]['fold_attempts']=len(read(foldfile)['attempts']) if foldfile.exists() else 0
 layouts[-1]['screen_evidence']=str(screenfile.relative_to(H)) if screenfile.exists() else None
 certificate=O/'layouts'/f'{label}_target_certificates.json'
 if certificate.exists():
  cd=read(certificate);layouts[-1]['target_obstruction_certificates']=dict(complete=cd['complete'],blocked_targets=sum(x['impossible_at_declared_targets'] for x in cd['rows']),evidence=str(certificate.relative_to(H)),scope=cd['scope'])
for lay in layouts:
 for suffix,key in [('headroom_v7','headroom'),('dock_packing_v7','stored_bowl_packing'),('band_pair_v7','band_pair')]:
  file=O/'layouts'/f'{lay["layout"]}_{suffix}.json'
  if file.exists():lay[key]=dict(evidence=str(file.relative_to(H)),data=read(file))
write('layout_iterations_v7.json',dict(layouts=layouts,new_layouts_with_evidence=len(layouts),scope='New L90-L101 closed-door front-feed/bowl/peeler/mount layout studies. Empty-EOAT maps omit movable fixtures; full-target obstruction and stored-bowl packing probes expose those separately. L99/L100 stopped after a full-carriage base/beam obstruction certificate. L101 restores the gap with full geometry. Finite evidence is not an architectural impossibility proof.'))
assert len(layouts)>=6, 'Do not deliver before the documented-iteration stop condition is met'
rows=fresh['rows'];passed=sum(r['ok'] for r in rows)
summary=dict(schema='r07.v7.static-summary',selected_layout=ID,strokes_passed=passed,strokes_total=len(rows),static_fraction=passed/len(rows),poses_passed=sum(len(r.get('reference',{}).get('poses',[])) for r in rows if r['ok']),stroke_results=rows,required_starts=96,seconds_per_unresolved_start=20,complete96=sum(r['complete'] for r in rows),unresolved_or_unattempted=[r['index'] for r in rows if not r['ok']],acceptance=P['acceptance'],stop_condition='b',new_documented_layout_iterations=len(layouts),stop_condition_a=False,full_meal_pass=False,quality_qualified=False,budget_scope='96 completed starts required for positive count. Unresolved starts have20s available; accepted, converged local minimum, full-reference rejection and exhausted budget are recorded separately.',count_scope='59 full-geometry robot templates; static admission does not certify appliance operation or a persistent connected meal.')
write('phase_summary.json',summary);write('best.json',dict(layout=ID,witnesses={r['stroke']:r['reference'] for r in rows if r['ok']}))
summary['functional_process_checks']=dict(wash_alignment=read('wash_alignment_v7.json'),scope='Geometric static counts do not imply process success. Failed jet alignment remains a functional blocker.')
write('phase_summary.json',summary)
internal=[read(f) for f in sorted((O/'motion_v7'/ID).glob('internal_*.json'),key=lambda f:int(f.stem.split('_')[-1]))]
assert len(internal)==len(rows) and {r['index'] for r in internal}==set(range(len(rows)))
conn=[read(O/'connections_v7'/ID/f'{i}.json') for i in range(len(p.expanded())-1)]
assert all(r['planner_ran'] and r['allocated_budget_s']>=60 for r in conn)
assert not conn[0]['pass_'], 'Recompute the actual committed prefix if the first transition succeeds'
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
 compact[-1].update(evidence=f'results/connections_v7/{ID}/{r["connection"]}.json',sha256=digest(O/'connections_v7'/ID/f'{r["connection"]}.json'))
seq=dict(schema='r07.v7.persistent-meal',layout=ID,mass_input_kg=.57,initial_state=initial,executed_state=initial,expanded_strokes=p.expanded(),expanded_connections=compact,events=events,discrete_state_chain_errors=[],executed_prefix_connections=0,executed_products=[],status='No completed connected product; later attempts are conditional scenarios after failed prefix, not committed motion.',transformation_policy='Food-only mass-conserving station changes with density/packing-derived bulk beds. Full robot-touched solids retained; unqualified direct bulk grasps retain full original geometry and receive no pass.',conditional_state_limit='Intermediate food loading and physical appliance controls are explicit unexecuted prerequisites. A conditional diagnostic can expose geometric blockers but cannot establish those actions.',duration_limit='P16 cycle derived from published actuator data; exact BFP610 and secondary per-batch times remain unknown.')
seq['discrete_state_chain_checked']=False;seq['discrete_state_chain_scope']='The committed prefix is empty. Conditional connection scenarios are individually checked, not certified as a continuous recipe-state chain.'
write('state_sequence.json',seq);write('persistent_model.json',dict(layout=ID,model_xml='models/persistent_meal.xml',model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),unique_food_bodies=4,full_initial_objects=len(w.objects),food_mass_kg=.57,transaction_checks='results/state_model_regression_v7.json',executable_connection_scenarios=True,full_recipe_executed=False,conditional_state_limit=seq['conditional_state_limit']))
motion=dict(schema='r07.v7.motion',layout=ID,meal_pass=False,internal_pass=sum(r['ok'] for r in internal),internal_total=len(rows),internal_paths=internal,connections_pass=0,connections_total=len(conn),connections=compact,all_connections_planner_ran=all(r['planner_ran'] for r in conn),conditional_connection_pass=cond,geometric_connection_pass=geometric,executed_prefix_connections=0,event_paths=events,event_paths_total=len(events),event_paths_pass=0,persistent_model_executable=True,full_recipe_executable=False,planner_budget_s=65,point_step_limit_mm=4,scope='All connections actually planned in a persistent populated conditional state. Individual geometric passes are separate from executable state transitions. None is credited as an executed meal after a failed prefix.')
write('motion.json',motion)
motion['free_transfer_load_policy']=dict(payload_acceleration_m_s2=.3,SF=1.5,signed_axes=6,working_wrench_N=[0,0,0],source='persistent_v7_r07.zero and connections_v7_r07.replay; actual attached mass retained')
rolled=[read(f) for f in sorted((O/'rolled_internal_v7'/ID).glob('*.json'),key=lambda f:int(f.stem))]
variants=[r for r in p.expanded() if r['roll_deg']]
assert len(rolled)==len(variants)==20 and {r['expanded_stroke']['id'] for r in rolled}=={r['id'] for r in variants}
roll_by_id={r['expanded_stroke']['id']:r for r in rolled};internal_by_index={r['index']:r for r in internal};expanded_internal=[]
for r in p.expanded():
 diagnostic=roll_by_id[r['id']] if r['roll_deg'] else internal_by_index[r['index']]
 evidence=f'results/rolled_internal_v7/{ID}/{diagnostic["ordinal"]}.json' if r['roll_deg'] else f'results/motion_v7/{ID}/internal_{r["index"]}.json'
 expanded_internal.append(dict(**r,isolated_path_pass=diagnostic['ok'],evidence=evidence,executed_in_meal=False,same_template_reuse=not bool(r['roll_deg'])))
motion['expanded_internal_coverage']=dict(total=len(expanded_internal),distinct_extra_rolls=len(rolled),extra_rolls_pass=sum(r['ok'] for r in rolled),rows=expanded_internal,scope='All111 stroke instances map to checked internal diagnostics. Identical zero-roll commands reuse their template path; each of20 changed wash rolls gets a separate full-budget path attempt. Isolated scene checks do not establish persistent meal execution.')
write('motion.json',motion)
pair_counts=collections.Counter();status_counts=collections.Counter(r['status'] for r in conn)
for r in conn:
 for leg in r['legs']:
  for end in leg.get('endpoint_geometry',[]):
   blocker=end.get('blocker') or {}
   for hit in blocker.get('blockers',[]):
    if hit.get('pair'):pair_counts[' / '.join(sorted(hit['pair']))]+=1
write('connection_summary_v7.json',dict(layout=ID,attempted=len(conn),actual_planner_seconds=sum(r['actual_planner_s'] for r in conn),allocated_leg_seconds=sum(r['allocated_budget_s'] for r in conn),status_counts=dict(status_counts),geometric_pass=geometric,conditional_pass=cond,executed_prefix=0,connections_with_rejected_containment=sum(any(event.startswith('Rejected containment transaction:') for event in r['required_events']) for r in conn),endpoint_blocker_counts=dict(pair_counts.most_common()),scope='Endpoint pair frequency across attempted legs; counts are diagnostics, not an infeasibility certificate. Full per-connection data remain authoritative.'))
idle=read('layouts/'+ID+'_idle.json')
for suffix,key in [('fold_v7','task_fold'),('unfold_v7','explicit_unfold'),('fold_alternatives_v7','alternative_fold_goals'),('return_v7','meal_end_return_diagnostic'),('fold_bridge_v7','fold_bridge_diagnostic'),('return_bridge_v7','return_bridge_diagnostic'),('fold_front_v7','front_fold'),('unfold_front_v7','front_unfold'),('return_front_v7','front_return'),('fold_high_front_v7','high_front_fold'),('unfold_high_front_v7','high_front_unfold'),('return_high_front_v7','high_front_return')]:
 f=O/'layouts'/f'{ID}_{suffix}.json';idle[key]=read(f) if f.exists() else dict(pass_=False,status='NOT_ATTEMPTED')
def at_final_park(q):
 if q is None or len(q)!=len(idle['q']):return False
 # Require the same recorded joint state, not an implicit branch reset between
 # independently successful fold/unfold attempts.
 return max(abs(float(a)-float(b)) for a,b in zip(q,idle['q']))<=1e-7
fold_completed=any(a.get('pass_',False) and at_final_park(a.get('goal_q',a.get('park_q'))) for key in ('task_fold','alternative_fold_goals','front_fold','high_front_fold') for a in idle[key].get('attempts',[])) or bool(idle['fold_bridge_diagnostic'].get('pass_',False) and at_final_park(idle['fold_bridge_diagnostic'].get('park_q')))
unfold_initial=any(a.get('pass_',False) and at_final_park(a.get('start_q')) for key in ('explicit_unfold','front_unfold','high_front_unfold') for a in idle[key].get('attempts',[]))
fold=fold_completed and unfold_initial
return_pass=any(a.get('pass_',False) and at_final_park(a.get('goal_q')) for key in ('meal_end_return_diagnostic','front_return','high_front_return') for a in idle[key].get('attempts',[])) or bool(idle['return_bridge_diagnostic'].get('pass_',False) and at_final_park(idle['return_bridge_diagnostic'].get('park_q')));idle_pass=bool(idle['snapshot_pass'] and fold and return_pass)
idle['park_endpoint_consistency']=dict(fold_to_final_snapshot=fold_completed,unfold_from_final_snapshot=unfold_initial,return_to_final_snapshot=return_pass,scope='Exact stored joint state; no unplanned wrap or alternate-pose reset.')
idle.update(pass_=idle_pass,fold_unfold_pass=fold,prospective_final_return_pass=return_pass,meal_end_to_park_verified=False,status='Populated snapshot, reversible fold and prospective final return are geometrically checked; actual meal-end return remains unexecuted.' if idle_pass else 'Prospective populated park checked separately; at least one required fold/unfold/final-return path failed. Connected meal and actual meal-end return not executed.')
write('idle.json',idle);write('passing.json',dict(layout=ID,applicable=False,pass_=None,reason='One full UR5e, one carriage, one wall lane; no crossing event.',model_xml=idle['model_xml'],q_crossing=idle['q']))
schedule=dict(schema='r07.v7.executed-timing',layout=ID,prep_min=None,meal_executed=False,home_speed_limits={'rail_m_s':.1,'joint_rad_s':.35,'all_geometry_point_m_s':.05,'rail_point_acceleration_m_s2':.3,'joint_acceleration_rad_s2':.35},mandatory_process_times={'bok_choy_soak_s':600,'potato_drain_s':30,'potato_fresh_rinses':3,'peeler_design_cycle_per_root_s':6*2*.160/.0034/.20,'BFP610_feed_cycle_and_stop_s':None,'secondary_cut_s':None,'sink_fill_and_drain_s':None},accepted_internal_paths=[],reason='No executed connected meal. Isolated checked paths are timed separately. Unknown appliance batch times stay unknown; declared food quality does not provide a cycle time.')
write('schedule.json',schedule)
values={}
for r in rows:
 if not r['ok']:continue
 for po in r['reference']['poses']:
  for cat,d in po['min_clearance'].items():values.setdefault(cat,[]).append(d['reserve_mm'])
dist={k:dict(samples=len(a),min_mm=min(a),median_mm=statistics.median(a),fraction_at_least10mm=sum(round(x,9)>=10 for x in a)/len(a),all_values_mm=a) for k,a in values.items()}
write('clearance.json',dict(schema='r07.v7.clearance',layout=ID,static_pose_category_minimum_reserves=dist,idle_snapshot_minima=idle.get('min_clearance'),meal_distribution=None,robustness_pass=False,scope='Worst eligible pair in each category per pose/state, not diluted by distant pairs. Gates unchanged;10mm extra is a design objective, not established by a tiny positive numerical reserve.'))
refined_file=O/'clearance_refinement_v7.json'
if refined_file.exists():
 refined=read(refined_file)
 if refined.get('layout')==ID:
  clear=read('clearance.json');clear['refined_reserve_assessment']={key:refined[key] for key in ('complete','counts','distribution','method')};clear['refined_reserve_assessment']['source']='results/clearance_refinement_v7.json';write('clearance.json',clear)
archive=H/'history/v7_delivery_inputs';archive.mkdir(exist_ok=True)
for name in ('costs.csv','iterations.csv'):
 if not (archive/name).exists():shutil.copy2(O/name,archive/name)
old=list(csv.DictReader((archive/'costs.csv').open(encoding='utf-8-sig')));cost=[x for x in old if x['item'] not in ('TOTAL','One15percent project reserve','Starfrit Rotato Express commodity peeler','Complete peeler mechanical guard and holder retrofit','P16-200-256-12-P actuator, LAC and12V supply','Full linear bearing guide and root holder','Full custom peeler mechanical guards and hinge')]
for item,amount,basis in [('P16-200-256-12-P actuator, LAC and12V supply',1600,'CNY planning allowance; OEM supports relay/H-bridge/LAC operation; no FX quote or purchase'),('Full linear bearing guide and root holder',2300,'Custom mechanical allowance; guide takes radial load above actuator4N lateral allowance'),('Full custom peeler mechanical guards and hinge',2500,'Mechanical allowance only; interlock/control already in single home-safety package')]:cost.append(dict(configuration='r07_under_cabinet_candidate',item=item,quantity=1,total_cny=amount,basis=basis,status='PLANNING_ALLOWANCE_NOT_PASSING'))
for row in cost:
 if 'Inclusive home-safety' in row['item']:row['basis']+='; includes600CNY allocation for five door-open pause sensors and presence/door logic within the existing package'
if cfg.get('bail_adaptation_allowance_cny'):
 cost=[r for r in cost if r['item']!='Four full bowl-bail locks and pins']
 cost.append(dict(configuration='r07_under_cabinet_candidate',item='Four full bowl-bail locks and pins',quantity=4,total_cny=cfg['bail_adaptation_allowance_cny'],basis='Four full articulated existing bails, full pins/stops,40g added mass each; mechanical proof remains unqualified',status='PLANNING_ALLOWANCE_NOT_PASSING'))
base=round(sum(float(x['total_cny']) for x in cost),2);reserve=round(base*.15,2);total=round(base+reserve,2)
for item,value in [('One15percent project reserve',reserve),('TOTAL',total)]:cost.append(dict(configuration='r07_under_cabinet_candidate',item=item,quantity=1,total_cny=value,basis='One15% project reserve; one18000CNY home-safety package',status='PLANNING_ALLOWANCE_NOT_PASSING'))
with (O/'costs.csv').open('w',newline='',encoding='utf-8') as f:writer=csv.DictWriter(f,fieldnames=old[0].keys());writer.writeheader();writer.writerows(cost)
write('cost_summary.json',dict(base_cny=base,reserve_cny=reserve,total_cny=total,cheapest_passing_cny=None,safety_package_count=1,reserve_count=1,qualified_quote=False))
history=list(csv.DictReader((archive/'iterations.csv').open(encoding='utf-8-sig')));fields=list(history[0]);iterations=[r for r in history if not r['kind'].startswith('v7_')]
def add(**kw):iterations.append({k:kw.get(k,'') for k in fields})
for number in range(74,84):
 label='L'+str(number);screen=O/'layouts'/f'{label}_screen_v7.json'
 if not screen.exists():continue
 add(kind='v7_superseded_scope_layout',id=label,layout=label,pass_=False,status='Historical over-constrained scene retained legacy open-sweep masks in operation; excluded from corrected-scope count',evidence=str(screen.relative_to(H)))
 for file in (O/'static_v7'/label).glob('*.json'):
  d=read(file)
  for row in d['rows']:add(kind='v7_superseded_scope_static_start',id=d['index'],layout=label,seed=row['seed'],starts=1,pass_=False,budget_s=row['allocated_s'],actual_s=row['elapsed_s'],status='Historical scope error; original search: '+row['termination']['kind'],evidence=str(file.relative_to(H)))
 for file in (O/'connections_v7'/label).glob('*.json'):
  d=read(file);add(kind='v7_superseded_scope_connection',id=d['connection'],layout=label,pass_=False,budget_s=d['allocated_budget_s'],actual_s=d['actual_planner_s'],status='Historical scope error; '+d['status'],evidence=str(file.relative_to(H)))
 for suffix in ('fold_v7','unfold_v7','return_v7','fold_alternatives_v7','fold_bridge_v7'):
  file=O/'layouts'/f'{label}_{suffix}.json'
  if file.exists():add(kind='v7_superseded_scope_'+suffix,id=label,layout=label,pass_=False,status='Historical over-constrained motion scene; no corrected-scope admission',evidence=str(file.relative_to(H)))
for lay in layouts:
 label=lay['layout'];add(kind='v7_layout',id=label,layout=label,starts=lay['starts'],pass_=False,status=lay['reason'],evidence=lay['evidence'])
 for mp in lay['maps']:add(kind='v7_reach_map',id='R',layout=label,pass_=mp['clear'],status=f"{mp['clear']}/{mp['total']} targets; map proposals only",evidence=mp['evidence'])
 for f in (O/'static_v7'/label).glob('*.json'):
  d=read(f)
  inherited=d.get('inheritance',{}).get('source_starts',0)
  for r in d['rows']:
   reused=r['seed']<inherited
   add(kind='v7_same_problem_reuse' if reused else 'v7_static_start',id=d['index'],layout=label,seed=r['seed'],starts=0 if reused else 1,pass_=r['ok'],budget_s=r['allocated_s'],actual_s=0 if reused else r['elapsed_s'],status=('Exact geometry/target reuse from '+d['inheritance']['source']+'; original termination: ' if reused else '')+r['termination']['kind'],evidence=str(f.relative_to(H)))
 if lay.get('screen_evidence'):add(kind='v7_layout_screen',id=label,layout=label,starts=0,pass_=False,status='Fresh full59-template old-branch replay; no inherited96-start credit',evidence=lay['screen_evidence'])
 if lay.get('target_obstruction_certificates'):add(kind='v7_target_obstruction_probe',id=label,layout=label,pass_=False,status=str(lay['target_obstruction_certificates']['blocked_targets'])+' targets certified obstructed across5mm/3degree tolerance; zero is no impossibility proof',evidence=lay['target_obstruction_certificates']['evidence'])
 for suffix in ('idle','fold_v7','unfold_v7','fold_alternatives_v7','return_v7','fold_bridge_v7','return_bridge_v7','fold_front_v7','unfold_front_v7','return_front_v7','fold_high_front_v7','unfold_high_front_v7','return_high_front_v7'):
  f=O/'layouts'/f'{label}_{suffix}.json'
  if f.exists():
   detail=read(f);add(kind='v7_'+suffix,id=label,layout=label,pass_=detail.get('pass_',False),status='Full physical scene; no executed meal credit',evidence=str(f.relative_to(H)))
   for number,attempt in enumerate(detail.get('attempts',[])):
    edges=attempt.get('edges',([attempt['planner']] if 'planner' in attempt else []));route=str(attempt.get('name',attempt.get('candidate',attempt.get('seed',number))))
    add(kind='v7_fold_route',id=suffix+':'+route,layout=label,pass_=attempt.get('pass_',False),budget_s=sum(e.get('allocated_budget_s',0) for e in edges),actual_s=sum(e.get('planner_time_s',0) for e in edges),status=f'{len(edges)} actual planner legs; zero means no clear staging/park joint goal. Full per-leg and snapshot evidence retained; no meal credit.',evidence=str(f.relative_to(H)))
    for ik in attempt.get('ik',[]):add(kind='v7_fold_staging_ik',id=suffix+':'+route+':'+str(ik['seed']),layout=label,seed=ik['seed'],starts=1,pass_=ik['pass_'],budget_s=ik['allocated_s'],actual_s=ik['elapsed_s'],status='Cartesian staging IK; not a source-template96-start solve or a path pass',evidence=str(f.relative_to(H)))
 if label!=ID:
  for f in (O/'connections_v7'/label).glob('*.json'):
   d=read(f);add(kind='v7_prior_connection_diagnostic',id=d.get('connection',f.stem),layout=label,pass_=False,budget_s=d.get('allocated_budget_s'),actual_s=d.get('actual_planner_s'),status='Historical model/method only; no current admission. '+d.get('status','See prior record'),evidence=str(f.relative_to(H)))
for r in internal:add(kind='v7_internal',id=r['index'],layout=ID,pass_=r['ok'],budget_s=65,status='Independent<=4mm full-load replay; isolated template',evidence=f'results/motion_v7/{ID}/internal_{r["index"]}.json')
for r in internal:
 if r.get('retry_policy'):add(kind='v7_internal_clearance_retry',id=r['index'],layout=ID,pass_=r['ok'],budget_s=65,status=str(r['retry_policy']),evidence=f'results/motion_v7/{ID}/internal_{r["index"]}.json')
for r in rolled:add(kind='v7_rolled_internal',id=r['expanded_stroke']['id'],layout=ID,pass_=r['ok'],budget_s=sum(e['allocated_budget_s'] for e in r['edges']),actual_s=sum(e['planner_time_s'] for e in r['edges']),status='Full geometry and changed roll; isolated path only, no repeated96-start static or connected-meal credit',evidence=f'results/rolled_internal_v7/{ID}/{r["ordinal"]}.json')
branch=read(f'normalized_park_v7_{ID}.json')
add(kind='v7_park_joint_branch',id=ID,layout=ID,pass_=branch['same_full_geometry'] and branch['within_joint_limits'],status='Equivalent allowed joint branch selected before deployment; full physical geometry compared, no motion or encoder-reset credit',evidence=f'results/normalized_park_v7_{ID}.json')
for r in conn:add(kind='v7_connection',id=r['connection'],layout=ID,pass_=r['pass_'],budget_s=r['allocated_budget_s'],actual_s=r['actual_planner_s'],status=r['status'],evidence=f'results/connections_v7/{ID}/{r["connection"]}.json')
for f in sorted((H/'audit').glob('v7_*.resource.json')):
 d=read(f);add(kind='v7_bounded_run',id=f.stem,starts=0,pass_=d.get('exit_code')==0,budget_s=d['timeout_s'],actual_s=d['elapsed_s'],status=f"Process result only, not task admission; exit={d.get('exit_code')}, peak_MiB={d['peak_MiB']}",evidence=str(f.relative_to(H)))
add(kind='v7_resource_policy',id='four_OS_locked_slots',pass_=True,status='Four OS-held file locks; fail-fast if all slots occupied. V5 resource incident remains historical and is not repeated or relabelled.',evidence='bounded_v7_r07.py')
add(kind='v7_grasp_identity_regression',id='live_registered_faces',layout=ID,pass_=read('grasp_identity_regression_v7.json')['pass_'],status='Genuine grasp admitted; wrong object/support, forged frame/parts/normal/fingers, stale registry and working kind rejected',evidence='results/grasp_identity_regression_v7.json')
add(kind='v7_wash_alignment',id='full_colander_opening',layout=ID,pass_=read('wash_alignment_v7.json')['pass_'],status='Independent functional jet/opening geometry; no collision-only washing credit',evidence='results/wash_alignment_v7.json')
for lay in layouts:
 for key in ('headroom','stored_bowl_packing','band_pair'):
  if key in lay:
   data=lay[key]['data'];admitted=data.get('full_swept_convex_distance',{}).get('full_carriage_range_clear',False) if key=='band_pair' else data.get('pass_',False)
   add(kind='v7_'+key,id=lay['layout'],layout=lay['layout'],pass_=admitted,status='Full geometry screening; actual IK/path gates unchanged',evidence=lay[key]['evidence'])
with (O/'iterations.csv').open('w',newline='',encoding='utf-8') as f:writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(iterations)
print('PREPARED',ID,passed,'/',len(rows),'internal',motion['internal_pass'],'connection attempts',len(conn),'conditional',cond,'CNY',total)



