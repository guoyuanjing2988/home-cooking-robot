"""Cross-file, ownership, immutable-source, resource and delivery audit."""
from station_spec import *
import csv,re
from PIL import Image
def read(n):return json.loads((H/n).read_text())
checks=[]
def check(name,condition,detail=None):checks.append(dict(name=name,pass_=bool(condition),detail=detail))
phase=read('results/phase_summary.json');motion=read('results/motion.json');prefix=read('results/executed_prefix.json');cost=read('results/cost_summary.json');clear=read('results/clearance.json');rows=[]
check('counts_consistent',phase['passed']==sum(r['pass_'] for r in phase['obligations'])==16 and motion['passed']==sum(p['ok'] for p in prefix['paths'])==14 and motion['total']==188)
check('handling96_starts',all(r['solver_starts']==96 for r in phase['obligations'] if r['kind']=='whole_pan_handling'))
check('handling96_distinct_initial_configs',all(r['unique_initial_configurations']==96 for r in read('results/start_coverage.json')['rows']))
check('loads_pass',read('audit/revision3_load_validation.json')['pass_'])
check('processing_honestly_unqualified',all(not r['pass_'] for r in phase['obligations'] if r['kind']!='whole_pan_handling') and not motion['meal_pass'] and read('results/schedule.json')['prep_min'] is None)
check('six_further_layouts',read('results/exit_condition.json')['further_layout_iterations']>=6)
for st in prefix['states']:
 m=mujoco.MjModel.from_xml_path(str(H/st['xml']));d=mujoco.MjData(m);d.qpos[:]=st['q'];mujoco.mj_forward(m,d);foods={};joints_ok=len(st['every_joint'])==m.njnt
 for joint in range(m.njnt):
  name=m.joint(joint).name;start=m.jnt_qposadr[joint];nn=7 if m.jnt_type[joint]==0 else 1;joints_ok &= np.max(abs(d.qpos[start:start+nn]-st['every_joint'][name]))<1e-10
 for product,mass in [('carrot',.12),('potato',.20),('bok_choy',.10),('tomato',.15)]:
  matches=[i for i in range(m.nbody) if m.body(i).name in ('food_'+product,'R_held_food_'+product)];okay=len(matches)==1
  if not okay:raise AssertionError(matches)
  bid=matches[0];gid=int(m.body_geomadr[bid]);parents=[];b=bid
  while b:parents.append(m.body(b).name);b=int(m.body_parentid[b])
  owner='output_'+product;okay &= any(n in parents for n in (owner,'R_held_'+owner));okay &= abs(st['food'][product]['mass_kg']-mass)<1e-12 and st['food'][product]['quality']=='raw_unwashed'
  foods[product]=dict(body=m.body(bid).name,owner=owner,mass_kg=mass,world_position_m=d.xpos[bid].tolist(),world_rotation=d.xmat[bid].tolist(),shape_size_parameters_m=m.geom_size[gid].tolist(),pass_=bool(okay),mass_accounting='Held surrogate tiny inertias plus external combined payload counted once; physical food ledger unchanged')
  st['food'][product]['world_position_m']=d.xpos[bid].tolist()
 if isinstance(st['appliance'],str):st['appliance']=dict(mode=st['appliance'])
 st['appliance'].update(water_inlet='closed',water_L=0,drain_volume_L=0,root_retained=False,finished_outputs=0,mechanism_positions={m.joint(i).name:float(d.qpos[m.jnt_qposadr[i]]) for i in range(m.njnt) if m.jnt_type[i] in (2,3) and not m.joint(i).name.startswith('R_')},force_transmission_qualified=False)
 rows.append(dict(event=st['event'],food=foods,mass_kg=sum(x['mass_kg'] for x in foods.values()),every_joint_recorded=bool(joints_ok),pass_=bool(joints_ok and all(x['pass_'] for x in foods.values()))))
check('every_state_food_and_joint_ledger',all(r['pass_'] and abs(r['mass_kg']-.57)<1e-10 for r in rows))
check('ownership_recompile_continuity',all(st.get('ownership_position_invariant_m',0)<=1e-5 and st.get('ownership_rotation_invariant',0)<=1e-5 for st in prefix['states']))
write('results/conservation.json',dict(states=rows,pass_=all(r['pass_'] for r in rows),initial_mass_kg=.57,final_mass_kg=.57,food_transforms_executed=0,finished_product_conservation_verified=False))
write('results/executed_prefix.json',prefix);write('results/state_sequence.json',dict(states=prefix['states'],food_transforms_executed=0,food_mass_kg=.57,complete=False))
check('all_admitted_robot_point_steps4mm',all(p['load_replay']['max_point_step_mm']<=4.00000001 for p in prefix['paths'] if p['ok']))
check('all_admitted_appliance_point_steps4mm',all(p.get('max_appliance_point_step_mm',0)<=4.00000001 for p in prefix['paths'] if p['ok']))
check('all_path_load_replays',all(r['pass_'] for r in read('results/final_path_loads.json')))
check('no_working_window_on_nonworking_path',all(w['kind']=='grasp_release_support' and w.get('object_id') and w.get('support_id') and w.get('face') for p in prefix['paths'] for w in p.get('contact_windows',[])))
check('last_failure_not_committed',not prefix['paths'][-1]['ok'] and prefix['states'][-1]['event']=='P01_drain_open')
for item in read('audit/provenance.json'):
 aa=ROOT/item['source'];bb=H/item['copy'];check('immutable:'+item['copy'],aa.read_bytes()==bb.read_bytes() and hashlib.sha256(bb.read_bytes()).hexdigest()==item['sha256'])
manifest=read('history/v2/snapshot_manifest.json');history_bad=[n for n,digest in manifest.items() if not (H/'history/v2'/n).exists() or hashlib.sha256((H/'history/v2'/n).read_bytes()).hexdigest()!=digest];check('v2_history_unchanged',not history_bad,history_bad)
lines=list(csv.DictReader((H/'results/costs.csv').open(encoding='utf-8-sig')));check('one_reserve_one_safety',sum(x['id']=='SAFETY' for x in lines)==1 and sum(x['id']=='RESERVE15' for x in lines)==1 and abs(sum(float(x['line_cny']) for x in lines)-cost['total_cny'])<1e-6 and abs(cost['reserve_cny']-.15*cost['subtotal_cny'])<1e-6)
runs=[json.loads(f.read_text()) for f in (H/'audit').glob('*_run.json') if f.name.startswith(('station_','rescue_'))];edges=[]
for r in runs:
 if 'start_monotonic_s' in r:edges.extend([(r['start_monotonic_s'],1),(r['end_monotonic_s'],-1)])
active=0;peak=0
for t,delta in sorted(edges):active+=delta;peak=max(peak,active)
check('bounded_resources',peak<=4 and all(r['timeout_s']<1200 and r['peak_process_MiB']<1900.1 and r['cpu_only'] for r in runs),dict(max_concurrent_workers=peak,runs=len(runs),max_worker_MiB=max(r['peak_process_MiB'] for r in runs)))
size=sum(f.stat().st_size for f in H.rglob('*') if f.is_file());check('output_under3GB',size<3*1024**3,dict(bytes=size))
render_files=list((H/'renders').glob('*.png'));check('renders_within1600px',all(max(Image.open(f).size)<=1600 for f in render_files),len(render_files));frames=read('renders/frame_manifest.json');check('24_honest_frames',len(frames['frames'])==24 and not frames['complete_meal'] and all(any(p['id']==f['path'] and p['ok'] for p in prefix['paths']) for f in frames['frames']))
check('food_transition_guards',all(read('results/food_transformation.json')['guards_tested']['additional_rejections'].values()))
original=rc.Workcell(17);current=StationCell(32);geometry=[]
for name in original.gnames:
 if not name.startswith(('R_geom_','R_eoat_','R_jaw_')):continue
 ga=original.gnames.index(name);gb=current.gnames.index(name);geometry.append(dict(name=name,pass_=bool(original.m.geom_type[ga]==current.m.geom_type[gb] and np.max(abs(original.m.geom_size[ga]-current.m.geom_size[gb]))<1e-12)))
check('original_arm_eoat_dimensions_preserved',bool(geometry) and all(x['pass_'] for x in geometry),geometry)
check('xarm_mass_CoM_preserved',all(x['mass_CoM_preserved'] for x in read('results/arm_evaluation.json')['conversion']['mass_CoM_audit']))
iface=read('results/interfaces.json');iface.update(known_unqualified_mismatches=['Basket joint XML range155mm exceeds150mm selected drive; all executed travel141mm or less','Cradle Y command230mm exceeds size16-200 selected nominal travel; first motion already collides','Pusher350mm model travel is not supplied by100mm L16 envelope; no matching drive selected','Generic index and blade motors lack matched torque-speed curve/brake selection','IP30 SMC drives need complete splash isolation and wet cleaning access','Pan clamp cam links, drain valve drive and lid gearbox are not force-qualified; modeled geometry is not a complete fabrication interface'],appliance_contact_policy='No working-contact exception enabled. All tested moving-versus-fixed and moving-versus-moving non-welded solids are checked for nonpenetration; rigid welded manufacturing joints excluded. Robot/held gaps use unchanged reference gates.',force_basis=dict(arm_carry='8 force corners +/-1.89N at assembly CoM, SF1.5*4.2kg*0.3m/s2',blade_carrot_N=152.6,blade_potato_N=183.2,blade_basis='Width-scaled primary compression-cut paper maxima with factor2, conditional slow0.5mm/s; full station reaction chain not qualified',peeling_N=63,eyes_N=52,tomato_wedging_N=636,process_load_status='Retained conservative design loads from stations; no appliance capacity pass claimed'),lift_stroke_executed_m=.141,quality_assumption_is_not_a_blocker=True);write('results/interfaces.json',iface)
check('door_sweep_robot_gates',read('results/service_door.json')['pass_'])
post_missing=[]
for file in ['integrator.md','integrator_v1.md','integrator_v2.md']:
 post=ROOT/'posts/r06'/file
 for target in re.findall(r'\]\(([^)]+)\)',post.read_text(encoding='utf-8')):
  if target.startswith(('http','C:','#')):continue
  if not (post.parent/target.split('#')[0]).exists():post_missing.append(dict(file=file,target=target))
check('current_and_history_post_links',not post_missing,post_missing)
write('results/revision_manifest.json',dict(revision=3,selected_layout=32,authoritative_results=[f.name for f in (H/'results').iterdir() if f.is_file()],histories=['history/v1/','history/v2/'],posts=['posts/r06/integrator_v1.md','posts/r06/integrator_v2.md'],diagnostics='v3/',complete_product_count=0,stopping_condition='b:15 further evidenced layouts; not workstation acceptance'))
write('audit/revision3_integrity.json',dict(checks=checks,report_integrity_pass=all(x['pass_'] for x in checks),workstation_acceptance_pass=False,scope='Self-audit, not independent review',source_hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in H.glob('station_*.py')}));print('AUDIT',sum(x['pass_'] for x in checks),'/',len(checks),'FAILED',[x['name'] for x in checks if not x['pass_']])
