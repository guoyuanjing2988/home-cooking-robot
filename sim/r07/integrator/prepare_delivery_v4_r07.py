import json,csv,sys,hashlib,statistics,copy
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';ID=sys.argv[1]
def read(p):return json.loads((p if isinstance(p,Path) else O/p).read_text(encoding='utf-8-sig'))
def write(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False))
cfg=read('layouts/'+ID+'.json');P=read('layouts/'+ID+'_process_v4.json');fresh=read('fresh_admission.json');seq=read('state_sequence.json');assert fresh['layout']==ID and seq['layout']==ID
P['night_process_change']['appliance']=cfg.get('peeler_model','Sammic M-5')
P['night_process_change']['essential_unqualified'][0]='Rotato holder, spike extraction, cutter adjustment, prehalving and guarded cycle' if cfg.get('peeler_model')=='Rotato Express' else 'M5 lid opening, load, motor cycle and stopped unload'
write('config.json',cfg);write('process_v4.json',P);write('process_v3.json',P);write('torque_envelope.json',read('layouts/'+ID+'_envelope.json'))
write('best.json',dict(layout=ID,witnesses={r['stroke']:r['reference'] for r in fresh['rows'] if r['ok']},scope='New59-template witnesses only; source hashes in fresh_admission.json'))
write('process_metadata_errata.json',dict(layout=ID,searched_process='results/layouts/'+ID+'_process_v4.json',actual_peeler=cfg.get('peeler_model'),erratum='The archived searched process retains two inert M5 summary labels. Final process_v4.json/process_v3.json correct only these labels to Rotato. Active config, full geometry and four actual phase labels always specified Rotato Express. Search evidence/hash preserved; no geometry, force or quality credit changes.',correct_essential_interfaces=['Rotato upper holder, cutter height, spike extraction and closed guard cycle','Carrot prehalving and retained pieces','BFP610 exact batch interfaces']))
layouts=[]
for n in range(36,int(ID[1:])+1):
 label='L'+str(n);file=O/'layouts'/f'{label}.json'
 if not file.exists():continue
 c=read(file);maps=[]
 for side in ('R','L'):
  mp=O/'reachability'/label/(side+'.json')
  if mp.exists():
   d=read(mp);maps.append(dict(side=side,clear=sum(bool(r['pass_']) for r in d['rows']),total=len(d['rows']),complete=d.get('complete'),proposal_reuse=d.get('reuse_note'),evidence=str(mp.relative_to(H))))
 fixed=O/'layouts'/f'{label}_fixed_obstructions.json';cert=O/'layouts'/f'{label}_target_certificates.json';park=O/'layouts'/f'{label}_idle.json';statics=[read(f) for f in (O/'static_v4'/label).glob('*.json')]
 layouts.append(dict(layout=label,reason=c['reason'],main_mount_deg=c['mount_deg'],height_m=c['height'],stand_off_y_m=c['front_mount_y'],arms=c.get('count'),maps=maps,fixed_obstructions=read(fixed).get('global_fixed_obstructions',[]) if fixed.exists() else None,target_certified_blocked=sum(r['impossible_at_declared_targets'] for r in read(cert)['rows']) if cert.exists() else None,park_snapshot=read(park)['snapshot_pass'] if park.exists() else None,complete96=sum(s.get('complete',False) for s in statics),static_pass=sum(s.get('complete',False) and bool(s.get('witness')) for s in statics),starts=sum(s['starts'] for s in statics),evidence=[str(p.relative_to(H)) for p in (file,fixed,cert,park) if p.exists()]))
write('layout_iterations_v4.json',dict(layouts=layouts,new_layouts_with_evidence=len(layouts),scope='Exact-layout failures and numerical searches only; no architecture-wide impossibility conclusion. Maps exclude movable stations/other arm and are seed proposals, never full-scene admission.'))
rows=fresh['rows'];passed=sum(r['ok'] for r in rows)
summary=dict(schema='r07.v4.static-summary',selected_layout=ID,strokes_passed=passed,strokes_total=len(rows),poses_passed=sum(len(r.get('reference',{}).get('poses',[])) for r in rows if r['ok']),static_fraction=passed/len(rows),stroke_results=rows,stop_condition='b',new_documented_layout_iterations=len(layouts),stop_condition_a=False,full_meal_pass=False,quality_qualified=False,required_starts=96,seconds_per_unresolved_start=20,complete96=sum(r['complete'] for r in rows),unresolved_or_unattempted=[r['index'] for r in rows if not r['ok']],budget_scope='96 completed starts required for positive count;20s available per unresolved start, local convergence and positive termination recorded. Unattempted/partial failed items are unresolved, never an impossibility proof.',count_scope='59 simplified robot template diagnostics; appliance approach witnesses are not appliance operation or finished-product credit. Explicit interface and conserved-event obligations remain in state_sequence.json.',acceptance=P['acceptance'],historical_L34='32/105 statics,18/105 internal,0/156 meal connections; preserved separately, never added to new59 count')
write('phase_summary.json',summary)
internal=[read(p) for p in sorted((O/'motion_v4'/ID).glob('internal_*.json'),key=lambda p:int(p.stem.split('_')[-1]))]
local=[read(p) for p in (O/'motion_v4'/ID).glob('connection_*.json')]
motion=dict(schema='r07.v4.motion',layout=ID,meal_pass=False,internal_pass=sum(r['ok'] for r in internal),internal_total=len(rows),internal_paths=internal,connections_pass=0,connections_total=len(seq['expanded_connections']),connections=seq['expanded_connections'],local_connection_diagnostics=local,event_paths=seq['events'],event_paths_total=len(seq['events']),event_paths_pass=0,persistent_model_executable=False,planner_budget_s=65,point_step_limit_mm=4,scope='Accepted isolated template motions do not alter the persistent meal state. Connection records explicitly identify missing physical binding/events; no planner budget is claimed spent on an unmodeled event.')
write('motion.json',motion)
idle=read('layouts/'+ID+'_idle.json')
for suffix,key in [('task_fold_periodic','task_fold'),('fold_continuation','continued_deployment'),('fold_staged','staged_fold'),('fold_alternatives','alternative_fold_goals')]:
 p=O/'layouts'/f'{ID}_{suffix}.json'
 if p.exists():idle[key]=read(p)
idle.update(pass_=False,fold_unfold_pass=any(idle.get(k,{}).get('pass_',False) for k in ('task_fold','staged_fold','alternative_fold_goals')),meal_end_to_park_verified=False,status='MEAL_NOT_EXECUTED; snapshot/auxiliary fold separately stated')
write('idle.json',idle);write('passing.json',dict(layout=ID,applicable=False,pass_=None,reason='One full UR5e and one carriage on one wall lane. No second arm exists or passing event is scheduled.',model_xml=idle['model_xml'],q_crossing=idle['q']))
schedule=dict(schema='r07.v4.executed-timing',layout=ID,prep_min=None,meal_executed=False,home_speed_limits={'rail_m_s':.1,'joint_rad_s':.35,'all_geometry_point_m_s':.05,'rail_point_acceleration_m_s2':.3,'joint_acceleration_rad_s2':.35},mandatory_process_times={'bok_choy_soak_s':600,'potato_drain_s':[20,30],'potato_fresh_rinses':3,'peeler_cycle_s':None,'BFP610_feed_cycle_and_stop_s':None,'sink_fill_and_drain_s':None},accepted_internal_paths=[],reason='No connected conserved meal; no invented prep clock. Local path timings are simulation under home-tier rest-to-rest limits. Appliance timings and water draining require qualified interfaces/measurements.')
write('schedule.json',schedule)
values={}
for r in rows:
 if not r['ok']:continue
 for pose in r['reference']['poses']:
  for cat,d in pose['min_clearance'].items():values.setdefault(cat,[]).append(d['reserve_mm'])
dist={k:dict(samples=len(a),min_mm=min(a),median_mm=statistics.median(a),fraction_at_least10mm=sum(round(x,9)>=10 for x in a)/len(a),all_values_mm=a,comparison='Round only for percentage to1e-9mm to avoid binary20mm becoming19.9999999999998mm; raw values retained; admission gates unchanged.') for k,a in values.items()}
write('clearance.json',dict(schema='r07.v4.clearance',layout=ID,static_pose_category_minimum_reserves=dist,idle_snapshot_minima=idle.get('min_clearance'),meal_distribution=None,scope='Each sample is the minimum eligible conservative pair reserve in that category at one admitted static pose, not all distant pairs. Self-contact gate is separate. Path-state distribution added after fresh replay.',robustness_pass=False,robustness_reason='All accepted poses meet original gates;10mm additional reserve is reported, not inferred. No connected robust meal is established.'))
old=list(csv.DictReader((H/'history/v3/results/costs.csv').open(encoding='utf-8-sig')));cost=[]
for r in old:
 if r['item'] in ('TOTAL','One15percent project reserve') or r['item'].startswith('xArm6'):continue
 if r['item'].startswith('Electric grippers'):r.update(quantity='1',total_cny='12000')
 if r['item'].startswith('One compact wall'):r.update(item='One compact wall rail, one carriage, home brake, chain and brackets',basis='Retain43000CNY conservative system allowance despite helper/carriage removal; no unsupported rail quote.')
 if r['item'].startswith('GROHE Eurosmart'):r.update(item='GROHE Eurocube13303000 fixed wall spout',basis='Public dimensional drawing and buyable listing;1500CNY design allowance, not a China quote.')
 cost.append(r)
for item,amount,basis in [('Starfrit Rotato Express commodity peeler',500,'Allowance, not a quote; OEM automation/food-quality suitability unqualified'),('Complete peeler mechanical guard and holder retrofit',2000,'Mechanical parts allowance; interlocks/control already in single safety package'),('Two complete horizontal tool dock stands and feet',400,'Mechanical fabrication allowance; full existing tool solids retained')]:cost.append(dict(configuration='r07_under_cabinet_candidate',item=item,quantity=1,total_cny=amount,basis=basis,status='PLANNING_ALLOWANCE_UNQUALIFIED_NOT_PASSING'))
base=round(sum(float(r['total_cny']) for r in cost),2);reserve=round(base*.15,2);total=round(base+reserve,2)
for item,value,basis in [('One15percent project reserve',reserve,'15% of entire base, applied once'),('TOTAL',total,'One18000CNY home safety package; one15% reserve')]:cost.append(dict(configuration='r07_under_cabinet_candidate',item=item,quantity=1,total_cny=value,basis=basis,status='PLANNING_ALLOWANCE_UNQUALIFIED_NOT_PASSING'))
with (O/'costs.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=old[0].keys());w.writeheader();w.writerows(cost)
write('cost_summary.json',dict(base_cny=base,reserve_cny=reserve,total_cny=total,cheapest_passing_cny=None,safety_package_count=1,reserve_count=1,qualified_quote=False))
historical=list(csv.DictReader((H/'history/v3/results/iterations.csv').open(encoding='utf-8-sig')));fields=list(historical[0]);iterations=historical.copy()
def add(**kw):iterations.append({k:kw.get(k,'') for k in fields})
for lay in layouts:
 label=lay['layout'];add(kind='night_layout',id=label,layout=label,starts=lay['starts'],pass_=False,status=lay['reason'],evidence='results/layouts/'+label+'.json')
 for mp in lay['maps']:add(kind='night_reach_map',id=mp['side'],layout=label,pass_=mp['clear'],status=f"{mp['clear']}/{mp['total']} exploratory targets; not full scene",evidence=mp['evidence'])
 for file in (O/'static_v4'/label).glob('*.json'):
  d=read(file)
  for r in d['rows']:add(kind='night_static_start',id=d['index'],layout=label,seed=r['seed'],starts=1,pass_=r['ok'],budget_s=r['allocated_s'],actual_s=r['elapsed_s'],status=r['termination']['kind'],evidence=str(file.relative_to(H)))
 for suffix in ('fixed_obstructions','target_certificates','idle','fold_continuation','task_fold','task_fold_periodic','fold_staged','fold_alternatives'):
  file=O/'layouts'/f'{label}_{suffix}.json'
  if file.exists():add(kind='night_'+suffix,id=label,layout=label,pass_=read(file).get('pass_',False),status='Exact layout evidence; see artifact, no global infeasibility claim',evidence=str(file.relative_to(H)))
for r in internal:add(kind='night_internal',id=r['index'],layout=ID,pass_=r['ok'],budget_s=65,status='Full reference replay; isolated template',evidence=f'results/motion_v4/{ID}/internal_{r["index"]}.json')
for r in local:add(kind='night_connection',id=r['index'],layout=ID,pass_=r.get('pass_',False),budget_s=r.get('allocated_budget_s',''),status=r.get('status','Local transition only; persistent ownership separately required'),evidence=f'results/motion_v4/{ID}/connection_{r["index"]}.json')
with (O/'iterations.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(iterations)
print('PREPARED',ID,passed,'/',len(rows),'internal',motion['internal_pass'],'connections',motion['connections_total'],'CNY',total)
