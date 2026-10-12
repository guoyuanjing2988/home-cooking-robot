"""Final cross-file, conservation, geometry, render and history audit."""
from rescue_spec import *
from PIL import Image
import re,csv
def read(n):return json.loads((H/n).read_text())
checks=[]
def check(name,condition,detail=None):checks.append(dict(name=name,pass_=bool(condition),detail=detail))
phase=read('results/phase_summary.json');motion=read('results/motion.json');prefix=read('results/executed_prefix.json');cfg=prefix['config'];V=cfg['id'];baseline={};physical=[]
for state in prefix['states']:
 model=mujoco.MjModel.from_xml_path(str(H/state['xml']));data=mujoco.MjData(model);data.qpos[:]=state['q'];mujoco.mj_forward(model,data);row=dict(event=state['event'],food={},containers={},pass_=True)
 for product in PRODUCTS:
  names=['food_'+product,'R_held_food_'+product];ids=[b for b in range(model.nbody) if model.body(b).name in names];okay=len(ids)==1
  if ids:
   b=ids[0];ancestor=b;owner=None
   while ancestor:
    canonical=model.body(ancestor).name.removeprefix('R_held_')
    if canonical.startswith('output_'):owner=canonical;break
    ancestor=int(model.body_parentid[ancestor])
   geoms=[g for g in range(model.ngeom) if model.geom(g).name in names];okay &= len(geoms)==1 and owner==state['food'][product]['owner']
   if geoms:
    size=model.geom_size[geoms[0]].copy()
    if product not in baseline:baseline[product]=size
    okay &= np.array_equal(size,baseline[product]);row['food'][product]=dict(body=model.body(b).name,owner=owner,mass_kg=state['food'][product]['mass_kg'],world_position_m=data.xpos[b].tolist(),shape_size_parameters_m=size.tolist(),pass_=bool(okay),mass_accounting='Held tiny inertias plus external combined payload counted once; physical food identity/mass ledger unchanged')
  row['pass_'] &= bool(okay)
 for obj,record in state['containers'].items():
  names=[obj,'R_held_'+obj];ids=[b for b in range(model.nbody) if model.body(b).name in names];okay=len(ids)==1
  if ids:okay &= np.linalg.norm(data.xpos[ids[0]]-record['position_m'])<1e-8 and np.max(abs(data.xmat[ids[0]]-record['rotation']))<1e-8
  row['containers'][obj]=bool(okay);row['pass_'] &= bool(okay)
 physical.append(row)
write('results/conservation.json',dict(states=physical,pass_=all(x['pass_'] for x in physical),food_total_kg=.57,complete_product=False,cut_children_or_scraps_created=0,food_quality='raw_unwashed'))
check('compiled_food_identity_ownership_size_and_pan_pose',all(x['pass_'] for x in physical))
coverage=[]
for j in phase['strokes']:
 if 'action' not in j:continue
 chunks=[read(f) for f in j['evidence']];rows=[r for ch in chunks for r in ch['rows']];seeds={r['seed'] for r in rows};initial=[hashlib.sha256(np.array(r['actual_initial_q'],dtype=float).tobytes()).hexdigest() for r in rows if 'actual_initial_q' in r]
 good=len(rows)==96 and seeds==set(range(96)) and len(initial)==96 and len(set(initial))==96
 for ch in chunks:
  good &= ch['every_start_budget_s']>=20
  for row in ch['rows']:good &= row['solve']['collision_aware'] and row['solve']['allocated_per_start_s']>=20 and row['lift_solve']['allocated_per_start_s']>=20
  if ch.get('reused_identical_problem'):
   source=read(ch['reused_identical_problem']);good &= source['problem_sha256']==ch['problem_sha256'] and source['empty_model_sha256']==ch['empty_model_sha256'] and source['held_model_sha256']==ch['held_model_sha256']
 coverage.append(dict(id=j['id'],starts=len(rows),unique_independent_seeds=len(set(initial)),pass_=bool(good)))
write('results/start_coverage.json',coverage);check('all30_handling_obligations96_distinct_collision_aware_starts',all(x['pass_'] for x in coverage))
check('counts_match_explicit_ledger',phase['static_strokes_passed']==sum(s['pass_'] for s in phase['strokes']) and phase['static_strokes_total']==len(phase['strokes']) and motion['connections_passed']==sum(c['pass_'] for c in motion['connections']) and motion['connections_total']==len(motion['connections']))
mech=read('results/mechanism_motion.json');check('carrier_not_promoted_to_actual_lift',any(r['joint']=='carrier_carrot_joint' and not r['drive_interface_qualified'] for r in mech['wash']['rows']) and not any(s['event']=='P01_lift_insert' for s in prefix['states']))
image_rows=[]
for file in sorted((H/'renders').glob('*.png')):
 with Image.open(file) as im:image_rows.append(dict(file=str(file.relative_to(H)),size=list(im.size),pass_=max(im.size)<=1600))
frames=read('renders/frame_manifest.json');check('32_renders_within1600px',len(image_rows)==32 and all(x['pass_'] for x in image_rows));check('24_executed_prefix_frames_only',len(frames['frames'])==24 and not frames['complete_meal'] and all(f['path'] in {p['id'] for p in prefix['paths'] if p['ok']} for f in frames['frames']))
post=(ROOT/'posts/r06/integrator.md').read_text(encoding='utf-8');check('Chinese_summary_and_explicit_failure_post',post.startswith('中文摘要') and 'FAIL' in post and 'Condition(a) is not met' in post)
broken=[]
for link in re.findall(r'\]\(([^)]+)\)',post):
 if '://' in link:continue
 if not (ROOT/'posts/r06'/link).resolve().exists():broken.append(link)
check('all_post_artifact_links_resolve',not broken,broken)
history=H/'history/v1';check('v1_post_and_results_history_preserved',(ROOT/'posts/r06/integrator_v1.md').exists() and read('history/v1/results/phase_summary.json')['static_strokes_passed']==22 and read('history/v1/results/motion.json')['meal_pass'] is False)
check('stronger_final_force_box_passes',read('audit/revision2_validation.json')['report_integrity_pass'])
runs=[json.loads(f.read_text()) for f in (H/'audit').glob('rescue*_run.json')];events=[]
for run in runs:events += [(run['start_monotonic_s'],1),(run['end_monotonic_s'],-1)]
count=0;peak=0
for moment,delta in sorted(events):count+=delta;peak=max(peak,count)
check('max4_bounded_CPU_workers',peak<=4 and all(r['peak_process_MiB']<1900.1 and r['timeout_s']==1100 and r['cpu_only'] for r in runs),dict(peak_workers=peak,peak_memory_MiB=max(r['peak_process_MiB'] for r in runs)))
total=sum(f.stat().st_size for f in H.rglob('*') if f.is_file());check('under3GB',total<3*1024**3,dict(bytes=total));check('allowed_stop_condition_b',read('results/exit_condition.json')['condition_b'])
basis=['DECISIONS.md','posts/r06/stations.md','posts/r06/reviewer.md','posts/r05/reviewer.md','posts/r04/reviewer.md','posts/r02/tools.md','inputs/cook_ref.md','inputs/keypose_cook.md','inputs/prep_checker.py']
write('audit/binding_inputs.json',[dict(file=n,sha256=hashlib.sha256((ROOT/n).read_bytes()).hexdigest()) for n in basis])
report=dict(revision=2,selected_layout=V,report_integrity_pass=all(x['pass_'] for x in checks),workstation_acceptance_pass=False,checks=checks,images=image_rows,output_bytes=total,mechanical_checks='audit/revision2_validation.json',static_strokes=[phase['static_strokes_passed'],phase['static_strokes_total']],connections=[motion['connections_passed'],motion['connections_total']],finished_products=0)
write('audit/delivery.json',report);write('audit/revision2_delivery.json',report);print('INTEGRITY',sum(x['pass_'] for x in checks),'/',len(checks),'FAIL',[x['name'] for x in checks if not x['pass_']], 'MiB',round(total/1024**2,1))
