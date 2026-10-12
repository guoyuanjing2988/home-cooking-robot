from jobs import *
import csv
rows={}
for file in sorted((H/'results').glob('static_chunk_*.json'),key=lambda x:x.stat().st_mtime):
 for r in json.loads(file.read_text())['rows']:
  if r['index']<len(JOBS) and r['job']['targets']==JOBS[r['index']]['targets']:rows[r['index']]=r
missing=[i for i in range(len(JOBS)) if i not in rows];assert not missing,missing
selected=[];reserves=[];principal=[];force_witnesses=[];force_max=0;grip_min=1e30
for i,r in sorted(rows.items()):
 r['job']=JOBS[i]
 r['kind']=JOBS[i]['kind']
 if r['job']['admission']!='full_robot_static':r['pass_']=False
 ch=load_cell(r['job']);okay=True
 pending=[]
 for pi,pose in enumerate(r['selected']['poses']):
  q=np.array(pose['q']);hs=hand(ch,r['job']['targets'][0],r['job']['load']);hits,mins,ca=contacts(ch,q);tq,gr,cases=check_load(ch,q,hs)
  if hits or tq>1 or gr<1:okay=False
  force_witnesses.append(dict(stroke=r['id'],pose_index=pi,arm_geometry_pass=not hits,torque_ratio=tq,grip_margin=gr,cases=cases,scope='Final CoM-corrected replay of the selected solver witness; random-start archive preserved'))
  pending.append((q,tq,gr,mins,hs))
 if r['pass_'] and okay:
  for q,tq,gr,mins,hs in pending:
   selected.append(dict(stroke=r['id'],q=q.tolist(),torque_ratio=tq,grip_margin=gr,clearance=mins));force_max=max(force_max,tq);grip_min=min(grip_min,gr)
   for cat,v in mins.items():
    if cat!='self':reserves.append(dict(stroke=r['id'],category=cat,**v))
   challenge=copy.deepcopy(hs);challenge['R']['held_kg']=3.;rat,mar,cs=check_load(ch,q,challenge);principal.append(dict(stroke=r['id'],total_flange_kg=4.2,external_load_kg=3.,torque_ratio=rat,grip_margin=mar,CoM_derived_from_task_m=ch.com.tolist(),pass_=rat<=1 and mar>=1))
 r['final_active_scene_replay_ok']=okay
 if r['pass_'] and not okay:r['pass_']=False
phase=dict(static_strokes_passed=sum(r['pass_'] for r in rows.values()),static_strokes_total=len(JOBS),robot_manipulation_strokes_total=sum(j['admission']=='full_robot_static' for j in JOBS),robot_manipulation_strokes_passed=sum(r['pass_'] for r in rows.values()),robot_retracted_diagnostic_only=sum(r['static_robot_ok'] and r['job']['admission']!='full_robot_static' for r in rows.values()),solver_starts_per_obligation=96,total_solver_starts=sum(r['starts'] for r in rows.values()),expanded_reference_obligations_enumerated=True,conditional_quality_operations_fully_bound=False,all_required_obligations_verified=False,meal_pass=False,max_admitted_torque_ratio=force_max,min_admitted_grip_margin=None if not selected else grip_min,selected_witnesses=selected,strokes=[dict(index=i,id=r['id'],macro=r['macro'],kind=r['kind'],pass_=r['pass_'],static_robot_ok=r['static_robot_ok'],starts=r['starts'],solutions=r['solutions'],selected_seed=r['selected']['seed'],final_replay_ok=r['final_active_scene_replay_ok'],limitation=r['limitation'],blocker=r['selected']['poses'][0]['blockers'][:2]) for i,r in sorted(rows.items())],acceptance=SPEC['acceptance'])
write('results/phase_summary.json',phase);write('results/final_force_witnesses.json',dict(rows=force_witnesses,carry_application='Real held-assembly CoM; equivalent r x F couple at fixed R_work key site',immutable_reference_functions=True,selected_witness_replay_only=True));write('results/principal_payload.json',dict(rows=principal,nominal_external_capability_kg=3,EOAT_kg=1.2,all_admitted_poses_pass=all(x['pass_'] for x in principal),limitation='3kg capability at admitted positions only; no full-workspace or failed-station admission'))
phase['static_scope']='Conditional reference-static held-assembly poses, not an executed capture transaction. The reference rigid-weld exclusion can hide internal held-assembly interference; the persistent unheld-key approach is independently tested and fails.'
phase['actual_grasp_transactions_completed']=0
write('results/phase_summary.json',phase)
prefix=json.loads((H/'results/executed_prefix.json').read_text());mr={}
for f in sorted((H/'results').glob('mechanism_chunk_*.json'),key=lambda x:x.stat().st_mtime):
 for row in json.loads(f.read_text())['rows']:mr[row['index']]=row
assert set(mr)=={i for i,j in enumerate(JOBS) if j['admission']!='full_robot_static'},'Mechanism diagnostics incomplete'
mechs=dict(rows=[mr[i] for i in sorted(mr)],scope='Rejected/unqualified appliance diagnostics, not an executed conserved meal',no_food_spawn=True,no_work_contact_on_nonworking_paths=True)
write('results/mechanism_motion.json',mechs)
ordered=[]
for e in EVENTS:
 group=[j for j in JOBS if j['macro']==e['id']];ordered += [j for j in group if j.get('substep')=='pan_lid_open_after_seating']+[j for j in group if 'close_before_process' in j.get('substep','')]
 for j in [j for j in group if not j.get('substep','').startswith(('pan_lid_','cell_roof_','cell_front_header_')) and not j['id'].endswith('_separate_retract')]:
  ordered.append(j);ordered += [r for r in group if r['id']==j['id']+'_separate_retract']
 ordered += [j for j in group if 'open_after_process' in j.get('substep','')]+[j for j in group if j.get('substep')=='pan_lid_close_before_transport']
connections=[]
for x,y in zip(ordered,ordered[1:]):
 proof=None
 if x['macro']=='A01' and y['id']=='A02_grasp':proof=next((c for c in prefix['connections'] if c['id']=='initial_to_A02_pregrasp'),None)
 if x['id']=='A02_grasp' and y['id']=='A03_release':proof=next((c for c in prefix['connections'] if c['id']=='A02_to_A03_loaded'),None)
 connections.append(dict(from_=x['id'],to=y['id'],pass_=bool(proof and proof['ok']),proof=proof,reason=None if proof and proof['ok'] else 'Persistent execution has not reached this boundary; unqualified actuator/food/ownership states are retained as failures',allocated_planner_budget_s=65,actual_search_done=proof is not None))
diagnostics=[]
for f in (H/'results').glob('connection_diagnostics_*.json'):diagnostics += json.loads(f.read_text())['rows']
motion=dict(meal_pass=False,connections_passed=sum(r['pass_'] for r in connections),connections_total=len(connections),internal_paths_executed=sum(p['ok'] for p in prefix['paths']),internal_paths_attempted=len(prefix['paths']),full_meal_internal_obligations=len(JOBS),full_meal_internal_verified=False,connections=connections,executed_prefix=prefix,mechanism_diagnostics=mechs,isolated_loaded_connection_diagnostics=diagnostics,isolated_diagnostics_are_not_meal_connections=True,unsearched_required_connections=sum(not r['actual_search_done'] for r in connections),two_arm_simultaneity='not_applicable_one_arm',contact_kinds_explicit=True,food_total_kg=.57,food_duplicated_kg=0,food_lost_kg=0,quality_pass=False,terminal_cuts_explicit=True,all_geometry_full_scale=True,path_point_displacement_max_m=.004,coverage_limitation='Every unexecuted edge remains FAIL. Budget allocation is not an assertion of a search: actual_search_done records coverage. Missing physical endpoints cannot be repaired with RRT.')
write('results/motion.json',motion)
pathres=[p['load_replay']['min_reserve_mm'] for p in prefix['paths'] if p['ok'] and p.get('load_replay',{}).get('min_reserve_mm') is not None]
vals=[r['reserve_mm'] for r in reserves];minimum=min(vals+pathres) if vals or pathres else None
clear=dict(gates_mm={'robot_environment':10,'held_gripper_environment':5,'self_reference':0},scope='Admitted selected static poses and full replay of executed prefix paths; unexecuted meal has no global minimum',minimum_admitted_reserve_mm=minimum,static_distribution_mm={str(q):float(np.quantile(vals,q/100)) for q in (0,5,25,50,75,95,100)} if vals else {},fraction_static_category_checks_reserve_ge_10=float(np.mean(np.array(vals)>=10)) if vals else None,minimum_by_category={cat:min(r['reserve_mm'] for r in reserves if r['category']==cat) for cat in {r['category'] for r in reserves}},rows=reserves,failed_states_not_in_admitted_distribution=True,full_meal_minimum_reserve_mm=None,numerical_tolerance_m=1e-6,PAD=0)
write('results/clearance.json',clear)
posevals=[min(v['reserve_mm'] for c,v in x['clearance'].items() if c!='self') for x in selected]
pathvals=[v for p in prefix['paths'] if p['ok'] for v in p.get('load_replay',{}).get('reserve_samples_mm',[])]
clear['static_pose_minimum_reserve_distribution_mm']={str(q):float(np.quantile(posevals,q/100)) for q in (0,5,25,50,75,95,100)} if posevals else {}
clear['fraction_admitted_static_poses_reserve_ge_10']=float(np.mean(np.array(posevals)>=10)) if posevals else None
clear['executed_path_checked_state_reserve_distribution_mm']={str(q):float(np.quantile(pathvals,q/100)) for q in (0,5,25,50,75,95,100)} if pathvals else {}
clear['fraction_executed_path_states_reserve_ge_10']=float(np.mean(np.array(pathvals)>=10)) if pathvals else None
write('results/clearance.json',clear)
timeline=[];t=20
for p in prefix['paths']:
 if not p['ok']:break
 duration_s=p['duration_s'];timeline.append(dict(id=p['id'],start_s=t,end_s=t+duration_s,duration_s=duration_s,xml=p['xml'],status='executed_checked_simulation_prefix'));t+=duration_s
schedule=dict(prep_min=None,complete_meal=False,executed_prefix_s=t,executed_paths=timeline,blocked_event=prefix['blocked'],home_speeds=dict(point_m_s=.10,point_tangential_acceleration_m_s2=.15,point_total_acceleration_budget_m_s2=.30,joint_rad_s=.20,joint_acceleration_rad_s2=.25,jaw_m_s=.01,jaw_acceleration_m_s2=.02),time_parameterisation='One shared rest-to-rest trapezoid/triangle progress per retained joint segment, using the minimum normalized speed and acceleration limits across every-point/joint/jaw bounds. Stops at knots; no smoothing credit.',acceleration_reserve='Conservative curvature bound .10m/s x(6 x.20rad/s)=.12m/s2, plus jaw-rotation cross term2 x.01 x1.2=.024; total <=.15+.12+.024=.294m/s2 <.30 carry-force budget.',reference_meal_input_kg=.57,nominal_source_macro_seconds=sum(e['estimated_s'] for e in EVENTS),source_advertised_plan_min=45,source_plan_is_executed=False,appliance_cycles=[dict(event=e['id'],action=e['action'],source_estimate_s=e['estimated_s'],status='unexecuted/unqualified') for e in EVENTS if e['kind']=='appliance'],required_soak_s=600,required_greens_drain_s=30,required_potato_drain_s=30,required_potato_fresh_changes=3,fill6L_at6L_min_s=60,minimum_three_potato_fills_s=180,physical_time_conflict='A31 source100s is below180s for three6L fills alone; a complete timeline must include filling, lift/drain and inspection separately.',parallelism='No executed appliance overlap. A planned cell cleaning during600s soak remains unqualified.',literature_speed_root_cutting_m_s=.0005,carrot30cuts_min_engaged_s=30*.035/.0005,potato18whole_width_cuts_min_engaged_s=18*.070/.0005,quality_feedback_not_replaced_by_timers=True)
write('results/schedule.json',schedule)
schedule['volume_qualification_gap']='Source basin working volume6L differs from the published solid GN pan2.8L. A real overflow/exchange/freeboard water path and lowered-pan state must be qualified; no6L fill was executed.'
write('results/schedule.json',schedule)
costs=[]
with (H/'sources/bom.csv').open(encoding='utf-8-sig',newline='') as f:
 for r in csv.DictReader(f):
  if r['concept']=='cassette_fixed':costs.append(dict(id=r['id'],item=r['item'],quantity=float(r['quantity']),unit_cny=float(r['unit_cny']),line_cny=float(r['line_cny']),basis=r['basis']))
extra=[('I01','Overhead support bridge and mount fabrication allowance',1500),('I02','Two guarded cover retract actuators/retention allowance',1200),('I03','Brush and roller parking stages with retention allowance',1600),('I04','Longer guarded blade drive stroke and gravity brake/catch allowance',1800),('I05','Outward door hinge/monitoring installation allowance',400),('I06','Raised key backers and insert/support relocation allowance',700)]
for n,item,c in extra:costs.append(dict(id=n,item=item,quantity=1,unit_cny=c,line_cny=c,basis='Additional one-off engineering allowance, not a supplier quote; no safety-package duplication'))
subtotal=sum(x['line_cny'] for x in costs);reserve=.15*subtotal;total=subtotal+reserve;costs.append(dict(id='RESERVE15',item='ONE 15% reserve',quantity=1,unit_cny=reserve,line_cny=reserve,basis='15% of complete subtotal, applied once'))
with (H/'results/costs.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['id','item','quantity','unit_cny','line_cny','basis']);w.writeheader();w.writerows(costs)
write('results/cost_summary.json',dict(subtotal_cny=subtotal,reserve_fraction=.15,reserve_cny=reserve,total_cny=total,home_safety_packages=1,safety_package_cny=16000,status='Unqualified candidate engineering budget; cheapest passing system is null',cheapest_passing_cny=None,purchasing=False,supplier_contact=False))
write('results/state_sequence.json',dict(ordered_obligations=ordered,executed_states=prefix['states'],physical_states=prefix['physical_states'],initial_mass_kg=.57,conserved_actual_prefix=True,proposed_boundary_ledger=LEDGER,proposed_ledger_never_executed_beyond_blocker=True,blocked_at=prefix['blocked'],food_piece_catalog_status='Immutable nominal catalog only; no remote piece or waste spawning accepted',all_container_jaw_lid_appliance_states_tracked_in_actual_prefix=True,unresolved_intermediate_states=list(r['id'] for r in mechs['rows'] if not r['pass_'])))
print('FINAL',phase['static_strokes_passed'],len(JOBS),motion['connections_passed'],len(connections),'prep null','cost',total,'reserve',minimum)
