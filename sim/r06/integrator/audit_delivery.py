"""Final evidence audit. A valid report of FAIL is not a passing workstation."""
from jobs import *
from PIL import Image
import csv
checks=[]
def check(name,condition,detail=None):
 checks.append(dict(name=name,pass_=bool(condition),detail=detail))
def read(n):return json.loads((H/n).read_text(encoding='utf-8'))
prov=read('audit/provenance.json')
fast=dict(source='sim/r05/integrator/fast_bounds.py',copy='upstream_r05/fast_bounds.py')
if not any(p['copy'].replace('\\','/')==fast['copy'] for p in prov):
 fast['sha256']=hashlib.sha256((ROOT/fast['source']).read_bytes()).hexdigest();fast['identical']=(ROOT/fast['source']).read_bytes()==(H/fast['copy']).read_bytes();prov.append(fast)
if not any(p['copy'].replace('\\','/')=='sources/station_sources.json' for p in prov):
 a=ROOT/'sim/r06/stations/results/sources.json';b=H/'sources/station_sources.json';prov.append(dict(source=str(a.relative_to(ROOT)),copy=str(b.relative_to(H)),sha256=hashlib.sha256(a.read_bytes()).hexdigest(),identical=a.read_bytes()==b.read_bytes()))
for p in prov:
 a=ROOT/p['source'];b=H/p['copy'];check('immutable_copy:'+p['copy'],a.read_bytes()==b.read_bytes() and hashlib.sha256(b.read_bytes()).hexdigest()==p['sha256'])
write('audit/provenance.json',prov)
basis=['DECISIONS.md','posts/r06/stations.md','posts/r05/reviewer.md','posts/r04/reviewer.md','posts/r02/tools.md','inputs/cook_ref.md','inputs/keypose_cook.md','inputs/prep_checker.py']
write('audit/binding_inputs.json',[dict(file=n,sha256=hashlib.sha256((ROOT/n).read_bytes()).hexdigest()) for n in basis])
phase=read('results/phase_summary.json');motion=read('results/motion.json');schedule=read('results/schedule.json');clear=read('results/clearance.json');cost=read('results/cost_summary.json');prefix=read('results/executed_prefix.json')
check('all_enumerated_obligations_have_96_starts',len(phase['strokes'])==len(JOBS) and all(x['starts']>=96 for x in phase['strokes']),dict(total=len(JOBS),starts=phase['total_solver_starts']))
check('failed_meal_has_no_fabricated_time',not motion['meal_pass'] and schedule['prep_min'] is None)
check('budgets_distinguish_unsearched_edges',all(c['allocated_planner_budget_s']>=60 for c in motion['connections']) and motion['unsearched_required_connections']==sum(not c['actual_search_done'] for c in motion['connections']))
check('no_working_contact_on_retract',all(j['kind']!='working_stroke' for j in JOBS if any(x in j.get('substep','') for x in ('retract','park'))),[j['id'] for j in JOBS if j['kind']=='working_stroke' and any(x in j.get('substep','') for x in ('retract','park'))])
check('explicit_owned_window_schema',all(all(k in w for k in ('kind','object_id','support_id','face','normal','tcp_origin_m','tcp_rotation')) for j in JOBS if j['admission']=='full_robot_static' for w in load_cell(j).contact_windows))
probe=load_cell(next(j for j in JOBS if j['id']=='A02_grasp'));row=next(r for r in phase['selected_witnesses'] if r['stroke']=='A02_grasp');probe.pose(np.array(row['q']));old=copy.deepcopy(probe.contact_windows)
for w in probe.contact_windows:w['kind']='working_stroke'
probe.working_stroke=False;check('R05_finding1_work_window_removed_on_transit',not permitted(probe))
probe.contact_windows=old
for w in probe.contact_windows:w['object_id']='output_tomato'
check('another_objects_window_cannot_allow_contact',not permitted(probe))
ch=Cell(V);xml=E.fromstring(ch.xml);gxml={g.get('name'):g for g in xml.findall('.//worldbody//geom')};geom=[]
for body in SPEC['bodies']:
 for g in body['geometry']:
  name=('R_mount_'+g['id']) if body['id']=='robot_pedestal' else g['id'];actual=gxml.get(name)
  if actual is None:geom.append(dict(source=g['id'],pass_=False,reason='Missing solid'));continue
  wanted=np.array(g['size_m'])/2 if g['type']=='box' else np.array([g['radius_m'],g['height_m']/2]);size=np.fromstring(actual.get('size'),sep=' ')
  geom.append(dict(source=g['id'],actual=name,source_size_parameter_m=wanted.tolist(),actual_size_parameter_m=size.tolist(),pass_=bool(np.all(size>=wanted-1e-10)),geometry_shrunk=False if np.all(size>=wanted-1e-10) else True))
check('all_station_solids_present_and_not_shrunk',all(x['pass_'] for x in geom))
check('OEM_assets_unscaled',all(np.allclose(np.fromstring(a.get('scale','1 1 1'),sep=' '),[1,1,1]) for a in xml.findall('.//asset/mesh')))
check('actual_OEM_ranges',np.allclose([np.degrees(ch.m.jnt_range[ch.jid[n]]) for n in ARM],[[-360.,360.],[-360.,360.],[-160.,160.],[-360.,360.],[-360.,360.],[-360.,360.]]))
check('fixed_mount_has_no_rail',np.max(np.abs(ch.m.jnt_range[ch.jid['R_carriage_x']]))<=1e-12)
check('controller_full_public_envelope',np.all(np.fromstring(gxml['controller_box'].get('size'),sep=' ')*2>=[.460,.254,.449]))
write('results/geometry_inventory.json',dict(station_solids=geom,source_dimensions_retained=True,arm='UR5e',full_OEM_inertias=True,base_meshes_restored=True,OEM_collision_primitives_unchanged=True,visual_meshes_other_than_base_display_only_not_admission=True,added_fixed_members=['overhead_crossbeam','overhead_column_-1','overhead_column_1','R_mount_brace_left','R_mount_brace_right','controller_drip_shield','cold_water_coupler','drain_coupler','single_household_power_inlet'],fixed_frame_worktop_mount_is_one_bolted_weld_assembly=True,all_moving_arm_and_held_parts_keep_environment_gates=True,structural_stiffness_and_stop_load_qualification=False,module_closed_size_m=[1.45,.75,1.95],service_door_sweep_excluded_from_closed_footprint=True))
passing={x['id'] for x in phase['strokes'] if x['pass_']};check('static_numerator_only_real_geometry_strokes',passing<=set(j['id'] for j in JOBS if j['admission']=='full_robot_static'))
for x in phase['selected_witnesses']:
 job=next(j for j in JOBS if j['id']==x['stroke']);c=load_cell(job);hits,mins,pf=contacts(c,np.array(x['q']));tq,gr,cases=check_load(c,np.array(x['q']),hand(c,job['targets'][0],job['load']));check('final_static:'+x['stroke'],not hits and tq<=1 and gr>=1)
 if job['load']=='carry':
  # Independent virtual-work comparison: a force applied directly at R_mass
  # versus the force plus equivalent couple at R_work. This checks the actual
  # compiled site transforms/Jacobians, not just the adapter's cross product.
  jw=np.zeros((3,c.m.nv));jr=np.zeros_like(jw);jm=np.zeros_like(jw);jrm=np.zeros_like(jw)
  mujoco.mj_jacSite(c.m,c.d,jw,jr,c.m.site('R_work').id);mujoco.mj_jacSite(c.m,c.d,jm,jrm,c.m.site('R_mass').id)
  errors=[]
  for case in cases:
   force=np.array(case['force_N']);moment=np.array(case['moment_Nm']);equiv=np.array(case['equivalent_moment_at_R_work_Nm'])
   errors.append(float(np.max(np.abs(jw.T@force+jr.T@equiv-(jm.T@force+jr.T@moment)))))
  check('carry_CoM_virtual_work:'+x['stroke'],max(errors,default=0)<1e-8,dict(max_joint_wrench_error_Nm=max(errors,default=0)))
check('actual_prefix_food_conserved',all(abs(sum(f['mass_kg'] for f in state['food'].values())-.57)<1e-9 for state in prefix['states']) and all(abs(sum(s['food_mass_kg'].values())-.57)<1e-9 for s in prefix['physical_states']))
check('no_unverified_food_transform',all(s['food_quality']=='raw_unwashed' for s in prefix['physical_states']))
check('every_actual_joint_recorded',all(len(s['every_joint'])==mujoco.MjModel.from_xml_path(str(H/s['xml'])).njnt for s in prefix['physical_states']))
check('attachment_handoffs_no_teleport',all(s.get('attachment_invariant_m',0)<=1e-5 for s in prefix['states']))
path_audits=[]
for path in prefix['paths']:
 if not path['ok']:continue
 model=mujoco.MjModel.from_xml_path(str(H/path['xml']));held=next((n for n in ('output_carrot','output_potato','output_bok_choy','output_tomato','clean_leaf_basket') if any(model.body(b).name=='R_held_'+n for b in range(model.nbody))),None)
 c=Cell(V,held);pb=PointBound(c);largest=max((pb.segment_bound(np.array(a),np.array(b))/max(1,math.ceil(pb.segment_bound(np.array(a),np.array(b))/.004)) for a,b in zip(path['path'],path['path'][1:])),default=0)
 valid=largest<=.004000000001 and path['load_replay']['pass_'] and path['load_replay']['max_torque_ratio']<=1 and path['load_replay']['min_grip_margin']>=1
 path_audits.append(dict(id=path['id'],pass_=valid,xml_sha256=hashlib.sha256((H/path['xml']).read_bytes()).hexdigest(),maximum_point_step_mm=largest*1000,accepted_states=path['load_replay']['states']))
check('accepted_paths_have_full_4mm_load_replay',all(x['pass_'] for x in path_audits));write('audit/accepted_path_audit.json',path_audits)
check('all_isolated_connections_real_search_budget',all(d['allocated_budget_s']>=60 and d.get('planner_time_s',0)>=60 if not d['ok'] else d['allocated_budget_s']>=60 for d in motion['isolated_loaded_connection_diagnostics']))
with (H/'results/costs.csv').open(encoding='utf-8-sig',newline='') as f:lines=list(csv.DictReader(f))
check('one_safety_package_one_reserve',sum(x['id']=='A13' for x in lines)==1 and sum(x['id']=='RESERVE15' for x in lines)==1 and abs(sum(float(x['line_cny']) for x in lines)-cost['total_cny'])<.001 and abs(cost['reserve_cny']-.15*cost['subtotal_cny'])<.001)
images=[]
for f in (H/'renders').glob('*.png'):
 with Image.open(f) as im:images.append(dict(file=str(f.relative_to(H)),width=im.width,height=im.height,pass_=max(im.size)<=1600))
check('renders_within_1600px',bool(images) and all(x['pass_'] for x in images))
frames=read('renders/frame_manifest.json');check('24_honestly_labelled_prefix_frames',len(frames['frames'])==24 and not frames['complete_meal'])
resources=[read(str(f.relative_to(H))) for f in (H/'audit').glob('*_run.json')]
check('bounded_foreground_CPU_runs',all(r['cpu_only'] and r['timeout_s']<1200 and r['peak_process_MiB']<1900.1 and r['worker_processes']==1 for r in resources))
total=sum(p.stat().st_size for p in H.rglob('*') if p.is_file());check('output_below_3GB',total<3*1024**3,dict(bytes=total))
check('post_written', (ROOT/'posts/r06/integrator.md').exists())
write('audit/delivery.json',dict(report_integrity_pass=all(x['pass_'] for x in checks),workstation_acceptance_pass=False,checks=checks,images=images,output_bytes=total,unsearched_meal_connections=motion['unsearched_required_connections'],unqualified_meal=True))
print('AUDIT',sum(x['pass_'] for x in checks),'/',len(checks),'FAILED',[x['name'] for x in checks if not x['pass_']], 'MiB',round(total/1024**2,1))
