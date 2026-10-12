"""Aggregate auditable revision2 evidence, preserving unresolved obligations."""
from rescue_spec import *
import csv,itertools,argparse
p=argparse.ArgumentParser();p.add_argument('--variant',type=int,default=15);a=p.parse_args();V=a.variant;cfg=config(V);spec=recipe(V)
def read(n):return json.loads((H/n).read_text())
def distribution(values):
 return dict(n=len(values),minimum=min(values) if values else None,percentiles={str(p):float(np.percentile(values,p)) for p in (5,25,50,75,95)} if values else {},fraction_at_least10mm=sum(x>=10-1e-5 for x in values)/len(values) if values else None)
strokes=[];selected=[];static_reserves=[];raw_count=0;coverage_count=0
for i,j in enumerate(spec['statics']):
 files=sorted((H/'v2/statics').glob(f'L{V}_{i:02d}_*.json'));chunks=[json.loads(f.read_text()) for f in files];rows=[r for ch in chunks for r in ch['rows']];seeds={r['seed'] for r in rows};coverage_count+=len(rows);raw_count+=sum(len(ch['rows']) for ch in chunks if not ch.get('reused_identical_problem'));good=[r for r in rows if r['pass_']];win=max(good,key=lambda r:r['min_reserve_mm']) if good else None
 st=dict(**j,starts=len(seeds),required_starts=96,collision_aware=True,per_start_budget_s=20,pass_=win is not None and len(seeds)>=96,passing_starts=len(good),evidence=[str(f.relative_to(H)) for f in files],scope='Full pan acquisition/release geometry; downstream raw-pan models are conditional on unverified processing')
 if win:st.update(selected_seed=win['seed'],min_reserve_mm=win['min_reserve_mm'],poses=win['poses']);selected.append(dict(stroke=j['id'],job=j,**win));static_reserves.extend(p['reserve_mm'] for p in win['poses'])
 strokes.append(st)
# Preserve every named operation inside a merged cycle. Unknown food geometry
# is a failed obligation, never a successful parked-arm substitute.
process=[]
for e in spec['events']:
 if e['kind']!='appliance_cycle':continue
 for k,op in enumerate(e['internal_paths']):
  process.append(dict(id=e['id']+f'_{k:02d}_'+op,event=e['id'],operation=op,product=e['product'],station=e['station'],pass_=False,starts=0,reason='Required complete appliance/food state not solved; no parked-arm IK credit',status='unqualified'))
prefix=read(f'v2/motion/L{V}_persistent.json');mechfile=H/f'v2/mechanisms/L{V}_carrot_wash.json';mech=read(str(mechfile.relative_to(H))) if mechfile.exists() else {}
if mech.get('actual_prefix_reached') and prefix['completed_transfers']==1:
 last=copy.deepcopy(prefix['states'][-1]);previous_q=np.array(last['q'])
 for r in mech['rows']:
  if not r['pass_'] or not r.get('drive_interface_qualified',True) or 'start_q' not in r or np.max(abs(np.array(r['start_q'])-previous_q))>1e-8:break
  op='retain_pan' if 'retention' in r['joint'] else 'open_pan_lid';ident='P01_'+op;path=[r['start_q'],r['endpoint_q']];steps=r['planned_states']-1
  # Mechanism diagnostic already checked every state including physical
  # non-robot solids. Store that exact interpolation for frame provenance.
  trace=[dict(q=(np.array(path[0])+(np.array(path[1])-path[0])*k/max(1,steps)).tolist(),reserve_mm=r['robot_min_reserve_mm']) for k in range(steps+1)]
  speed=.20 if 'lid' in r['joint'] else .02;acc=.25 if 'lid' in r['joint'] else .04;travel=abs(r['end']-r['start']);dur=2*math.sqrt(travel/acc) if travel<=speed*speed/acc else travel/speed+speed/acc
  prefix['paths'].append(dict(id=ident,ok=True,path=path,xml=mech['xml'],contact_windows=[] if r['contact_window'] is None else [r['contact_window']],capture_window=None,method='Physical appliance joint sweep including all moving solids',duration_s=dur,allocated_budget_s=65,load_replay=dict(pass_=True,states=r['states_checked'],min_reserve_mm=r['robot_min_reserve_mm'],reserve_samples_mm=[r['robot_min_reserve_mm']]*r['states_checked'],ordinary_reserve_samples_mm=[r['robot_min_reserve_mm']]*r['states_checked'],max_point_step_mm=r['max_point_step_mm'],max_torque_ratio=None,min_grip_margin=None,trace=trace),mechanism_evidence=str(mechfile.relative_to(H))))
  last=copy.deepcopy(last);last.update(event=ident,q=r['endpoint_q'],xml=mech['xml'],appliance='retained_lid_open' if 'lid' in r['joint'] else 'pan_retained');last['every_joint'][r['joint']]=[r['end']]
  if 'lid' in r['joint']:last['containers']['output_carrot']['lid']='open'
  prefix['states'].append(last);previous_q=np.array(last['q'])
  # Endpoints are physically checked, but the required96 collision-aware
  # parking starts have not been run: keep them out of the static numerator.
  target=next(x for x in process if x['event']=='P01' and x['operation']==op);target.update(status='Connected physical sweep passed;96-start static obligation incomplete',physical_sweep_pass=True,evidence=str(mechfile.relative_to(H)))
 prefix['blocked']=dict(event='P01_lift_insert',reason='Source120mm carrier slide exists, but its complete drive/latch/guide interface and turn/brush/drain/wash transitions are not qualified; food remains raw',qualified_prefix_mechanisms=sum('mechanism_evidence' in x for x in prefix['paths']))
write('results/executed_prefix.json',prefix);write('results/state_sequence.json',dict(proposed_recipe=spec,actual_states=prefix['states'],actual_food_total_kg=.57,finished_products=0))
passed=sum(x['pass_'] for x in strokes);phase=dict(static_strokes_passed=passed,static_strokes_total=len(strokes)+len(process),handling_strokes_passed=passed,handling_strokes_total=len(strokes),processing_obligations_total=len(process),processing_obligations_passed=0,solver_starts_per_handling_obligation=96,total_solver_starts=raw_count,obligation_start_coverage_including_exact_aliases=coverage_count,all_required_obligations_verified=False,meal_pass=False,strokes=strokes+process,selected_witnesses=selected,missing_geometry_is_not_an_IK_failure=True)
write('results/phase_summary.json',phase)
rehearsal=read(f'v2/motion/L{V}_rehearsal.json') if (H/f'v2/motion/L{V}_rehearsal.json').exists() else None
connections=[]
for e in spec['events']:
 names=[e['id']+'_'+x for x in e['required_paths']] if e['kind']=='whole_pan_transfer' else [e['id']+'_'+x for x in e['internal_paths']] if e['kind']=='appliance_cycle' else []
 for name in names:
  actual=next((x for x in prefix['paths'] if x['id']==name),None);diagnostic=next((x for x in (rehearsal or {}).get('paths',[]) if x['id']==name),None)
  connections.append(dict(id=name,pass_=bool(actual and actual['ok']),actual_search_done=actual is not None,allocated_planner_budget_s=65,actual_evidence='results/executed_prefix.json' if actual else None,raw_pan_rehearsal_pass=bool(diagnostic and diagnostic['ok']),processing_bypass_never_meal_credit=True))
motion=dict(connections_passed=sum(x['pass_'] for x in connections),connections_total=len(connections),connections=connections,meal_pass=False,finished_products=0,blocked=prefix['blocked'],unsearched_required_connections=sum(not x['actual_search_done'] for x in connections),raw_pan_rehearsal=dict(completed_transfers=(rehearsal or {}).get('completed_transfers',0),accepted_paths=sum(x['ok'] for x in (rehearsal or {}).get('paths',[])),attempted_paths=len((rehearsal or {}).get('paths',[])),evidence=f'v2/motion/L{V}_rehearsal.json',meal_credit=False,blocker=(rehearsal or {}).get('blocked')),path_point_step_limit_mm=4,planner_budget_s=65,one_arm_no_overlap_schedule=True)
write('results/motion.json',motion)
res=[z for p in prefix['paths'] if p['ok'] for z in p['load_replay']['reserve_samples_mm']];ordinary=[z for p in prefix['paths'] if p['ok'] for z in p['load_replay']['ordinary_reserve_samples_mm']]
clear=dict(gates_mm=dict(robot_environment=10,arm_arm=10,held_gripper_environment=5),PAD=0,static_selected_endpoint_reserve_mm=distribution(static_reserves),executed_all_reserve_mm=distribution(res),executed_outside_contact_windows_reserve_mm=distribution(ordinary),min_reserve_mm=min(res) if res else None,interpretation='Extra distance above binding gap; own support/capture windows excluded only for their exact pairs. Transition through5mm inevitably has small extra reserve.',paths=[dict(id=p['id'],min_reserve_mm=p['load_replay']['min_reserve_mm'],states=p['load_replay']['states']) for p in prefix['paths'] if p['ok']])
raw_res=[z for p in (rehearsal or {}).get('paths',[]) if p['ok'] for z in p['load_replay']['reserve_samples_mm']]
clear['raw_pan_rehearsal_reserve_mm']=distribution(raw_res);clear['minimum_including_conditional_rehearsal_mm']=min(res+raw_res+static_reserves) if res else None
clear['persistent_prefix_min_reserve_mm']=clear['min_reserve_mm'];clear['min_reserve_mm']=clear['minimum_including_conditional_rehearsal_mm']
write('results/clearance.json',clear)
time=20.;timeline=[]
for p in prefix['paths']:
 if not p['ok']:break
 timeline.append(dict(id=p['id'],start_s=time,duration_s=p['duration_s'],end_s=time+p['duration_s'],executed=True));time+=p['duration_s']
schedule=dict(prep_min=None,meal_complete=False,executed_prefix_s=time,startup_allowance_s=20,executed_path_timeline=timeline,home_limits=dict(point_speed_m_s=.10,point_tangential_accel_m_s2=.15,joint_speed_rad_s=.20,joint_accel_rad_s2=.25,jaw_speed_m_s=.01,jaw_accel_m_s2=.02),parallelism_executed=False,unexecuted_process_constraints=dict(cold_soak_s=600,greens_drain_s=30,potato_changes=3,water_charge_L=2,inlet_L_min=6,potato_min_fill_only_s=60,root_cut_proxy_rate_mm_s=.5,minimum_carrot_engagement_s=2100,minimum_potato_wholewidth_engagement_s=2520),quality_feedback_requires_repeats=True,conditional_times_are_not_executed_meal_estimates=True)
write('results/schedule.json',schedule)
old=list(csv.DictReader((H/'history/v1/results/costs.csv').open(encoding='utf-8-sig')));lines=[x for x in old if x['id'].startswith('A')]
for x in lines:
 if x['id']=='A03':x.update(item='1600x900 frame/worktop and fixed side pedestal',unit_cny='8000',line_cny='8000')
 if x['id']=='A07':x.update(item='Open process dock, supported feed and cartridge mechanisms (incomplete custom design)',unit_cny='9000',line_cny='9000')
 if x['id']=='A06':x.update(item='Press/feed/rotary/core and lateral-park actuators; gravity brakes/catches',basis='Design allowance includes the new lateral parking slide/drive; complete actuator specification remains unqualified')
lines += [dict(id='R2_01',item='Four outboard keys and complete geared lid drives',quantity='1',unit_cny='3600',line_cny='3600',basis='One-off design allowance; no supplier quote; guards covered once in A13')]
subtotal=sum(float(x['line_cny']) for x in lines);reserve=.15*subtotal;total=subtotal+reserve;lines.append(dict(id='RESERVE15',item='ONE15% reserve',quantity='1',unit_cny=str(reserve),line_cny=str(reserve),basis='15% of complete subtotal applied once'))
with (H/'results/costs.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['id','item','quantity','unit_cny','line_cny','basis']);w.writeheader();w.writerows(lines)
write('results/cost_summary.json',dict(subtotal_cny=subtotal,reserve_cny=reserve,total_cny=total,safety_package_cny=16000,safety_package_count=1,reserve_count=1,prices='Engineering allowances, not quotations',cheapest_passing_configuration=None))
iteration_rows=list(csv.DictReader((H/'history/v1/results/iterations.csv').open(encoding='utf-8-sig')))
why={8:'Translate complete cup140mm to fix4.1mm key/backer conflict; closed front door becomes blocker',9:'Replace shared cage by open pan lands; mount plate blocks shoulder; early discarded blade prototype dimensions not used for admission',10:'Enlarge module to1600x900; restore/enlarge full blade/pusher; actual base-plane plate still leaves shoulder3mm gap',11:'Side-mount arm and recess full plate30mm with actual base fasteners; open overhead corridor',12:'Try500mm rear rail as reach alternative; fixed side mount already works and avoids rail qualification',13:'Connected raised keys and rear blade parking; first real eight-path transfer passes; lid hits handle bolts',14:'Outboard key/low bridge and integral lid drive; eight-path transfer passes; original drive shaft intersects closed lid',15:'Retain full shaft but move rearward; enlarge gearbox; clamp and lid sweep pass; food cradle/processing still blocks'}
why[16]='L15 cross-cell/vertical process approach obstructed; add250mm lateral parking with full rail and motor, plus lower front staging poses'
why[17]='Returned carrot lid shaft leaves0.5mm to cup during potato wash pickup; translate complete cup80mm upward and update tool CoM'
for v in range(8,V+1):
 files=sorted((H/'v2/probes').glob(f'L{v}_carrot_pickup_*.json'));rr=[r for f in files for r in json.loads(f.read_text())['rows']]
 if not files:
  files+=sorted((H/'v2/statics').glob(f'L{v}_00_*.json'));rr=[r for f in files for r in json.loads(f.read_text())['rows']]
 files+=sorted((H/'v2/motion').glob(f'L{v}_persistent.json'))+sorted((H/'v2/motion').glob(f'L{v}_rehearsal.json'))+sorted((H/'v2/mechanisms').glob(f'L{v}_*.json'))
 iteration_rows.append(dict(iteration=f'R2-L{v}',variant_or_issue=config(v)['name'],failure=why[v].split(';')[-1],change=why[v],reason='Physical layout/pose change; same acceptance thresholds',evidence=';'.join(str(f.relative_to(H)) for f in files),result=f'{sum(bool(r.get("pass_")) for r in rr)}/{len(rr)} independent pickup starts; see full witnesses'))
with (H/'results/iterations.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['iteration','variant_or_issue','failure','change','reason','evidence','result']);w.writeheader();w.writerows(iteration_rows)
valid_layouts=[v for v in (8,10,11,12,13,14) if sum(json.loads(f.read_text())['starts_completed'] for f in (H/'v2/probes').glob(f'L{v}_carrot_pickup_*.json'))>=96]
write('results/exit_condition.json',dict(condition_a=False,condition_b=len(valid_layouts)>=6,documented_new_layouts=valid_layouts,minimum_required=6,not_a_working_meal=True,unfinished_work_explicit=True))
write('results/interfaces.json',interface_spec(V));write('results/recipe.json',spec)
write('results/mechanism_motion.json',dict(wash=mech,process=read(f'v2/mechanisms/L{V}_carrot_process.json'),scope='Only first clamp/lid have connected meal credit. Carrier and processing sweeps are conditional diagnostics; a passed later axis does not bypass a failed predecessor.',complete_appliance_acceptance=False))
write('results/utilities.json',dict(own_basin=True,water_inlet='G3/4 household cold-water hookup,6L/min design assumption',drain='40mm screened trapped drain design assumption',water_charge_L=2,pan_nominal_capacity_L=2.8,household_feeds=1,supply_V=230,supply_A=13,connected_allowance_W=1320,current_at_PF08_A=1320/(230*.8),power_scope='Allowance; complete motors/inrush/leakage/ventilation and hose-routing qualification outstanding',transport_guard='Drain and verify pan+food+residual-water payload<=3kg before pickup; no2L wash-water carry is credited',actual_water_state='off',one_safety_package=True,blade_and_door_interlocks='Required, hardware qualification incomplete',brakes='OEM arm holding documentary criterion; custom gravity axes require normally-applied brake and catch'))
overview=Workcell(V);(H/'models/overview.xml').write_text(overview.xml);write('results/geometry_inventory.json',dict(selected_layout=V,closed_module_m=[cfg['width']+.006,cfg['depth']+.006,1.973],full_OEM_inertias=True,OEM_collision_primitives_unchanged=True,controller_envelope_m=[.460,.254,.449],main_scene='models/overview.xml',main_scene_sha256=hashlib.sha256(overview.xml.encode()).hexdigest(),source_pans_food_keys_palm_jaws_cup_full_size=True,old_appliance_cage_replaced_by_new_open_docks=True,discarded_L09_prototype_not_admitted=True,custom_interfaces_not_complete=True,manufacturing_and_structural_qualification=False))
rating=read(f'v2/ratings{cfg["angle"]}/results/torque_envelope.json');write('results/torque_envelope.json',rating)
write('results/revision_manifest.json',dict(revision=2,selected_layout=V,authoritative_results=['phase_summary.json','motion.json','executed_prefix.json','state_sequence.json','schedule.json','costs.csv','cost_summary.json','iterations.csv','clearance.json','interfaces.json','recipe.json','geometry_inventory.json','torque_envelope.json','exit_condition.json','final_force_witnesses.json','payload_capability.json','final_path_loads.json','service_door.json'],original_delivery_archive='history/v1/',original_post='posts/r06/integrator_v1.md',historical_experiments='v2/',complete_product_count=0))
print('AGGREGATE',passed,'/',phase['static_strokes_total'],'connections',motion['connections_passed'],'/',motion['connections_total'],'starts',raw_count,'cost',total,'reserve',clear['min_reserve_mm'])
