"""Bind current evidence and distinguish artifact fidelity from task acceptance."""
import json,csv,hashlib,xml.etree.ElementTree as E,datetime
from pathlib import Path
from PIL import Image
H=Path(__file__).resolve().parent;root=H.parents[2];O=H/'results'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={};hashes=read(H/'audit/copied_code_hashes.json');changed=[]
for name,digest in hashes.items():
 for base in (H,H/'upstream',root/'sim/r05/integrator'):
  p=base/name
  if not p.exists() or sha(p)!=digest:changed.append(str(p))
checks['all_copied_reference_modules_unchanged']=not changed
source_changes=[];source_count=0;source_root=root/'sim/r05/integrator/sources'
for p in source_root.rglob('*'):
 if not p.is_file():continue
 source_count+=1;q=H/'sources'/p.relative_to(source_root)
 if not q.exists() or sha(q)!=sha(p):source_changes.append(str(q))
checks['all_inherited_source_assets_unchanged']=not source_changes
s=read(O/'phase_summary.json');ID=s['selected_layout'];m=read(O/'motion.json');idle=read(O/'idle.json');sched=read(O/'schedule.json');fresh=read(O/'fresh_admission.json');P=read(O/'process_v3.json');base=read(O/'inherited_process_v3.json')
for key in ('force_models','finished_products','tools','acceptance'):checks[key+'_unchanged']=P[key]==base[key]
contacts=[c for p in P['phases'] for sg in p['segments'] for pose in sg['poses'] for h in pose.values() for c in h.get('contacts',[])]
checks['explicit_contact_kinds_and_identities']=all(c.get('kind') in ('grasp_release_support','working_stroke') and c.get('object_id') and c.get('support_id')==c['face'] for c in contacts)
checks['contact_policy_regression']=read(O/'contact_policy_regression.json')['pass_']
door=read(O/'door_gate_regression_v3.json');checks['ten_mm_door_regression']=door['pass_']
checks['new_stop_condition_b']=s['faucet_enabled_complete_paired_layout_maps']>=6
checks['all105_enumerated']=len(s['stroke_results'])==105 and len(fresh['rows'])==105
checks['fresh_static_count']=fresh['layout']==ID and fresh['strokes_passed']==s['strokes_passed']
checks['admitted_branches_completed96_starts']=all(r['starts']>=96 for r in s['stroke_results'] if r['ok'])
checks['every_admitted_stroke_has_motion_attempt']=all(any(p['index']==r['index'] and p.get('edges') for p in m['internal_paths']) for r in s['stroke_results'] if r['ok'])
checks['fresh_models_match_saved_search']=all(r['same_compiled_geometry'] for r in fresh['rows'] if r['starts'])
checks['all_connections_and_events_enumerated']=len(m['connections'])==m['connections_total'] and len(m['event_paths'])==m['event_paths_total']
checks['no_invented_meal_clock']=not m['meal_pass'] and sched['prep_min'] is None
checks['doors_not_checked_against_corridor']=idle['doors_checked_against_corridor'] is False
checks['fold_path_work_present']=bool(idle.get('continued_deployment',{}).get('attempts') or idle.get('fold_paths') or idle.get('auxiliary_map_folds',{}).get('routes'))
required=['phase_summary.json','motion.json','idle.json','schedule.json','costs.csv','clearance.json','iterations.csv'];checks['required_outputs']=all((O/n).exists() for n in required)
checks['histories_preserved']=(root/'posts/r07/integrator_v1.md').exists() and sha(root/'posts/r07/integrator_v2.md')=='42dd10c7da1ca73284326ad636b9b72183370ba4b281e413efa2ee94089c41e0' and (H/'history/v2/results/phase_summary.json').exists()
with (O/'costs.csv').open(newline='',encoding='utf-8') as file:cost=list(csv.DictReader(file))
amount=sum(float(r['total_cny']) for r in cost if r['item'] not in ('TOTAL','One15percent project reserve'));reserve=[r for r in cost if r['item']=='One15percent project reserve'];total=[r for r in cost if r['item']=='TOTAL']
checks['single15percent_reserve_and_safety']=len(reserve)==len(total)==1 and sum('Inclusive home-safety' in r['item'] for r in cost)==1 and abs(float(reserve[0]['total_cny'])-round(amount*.15,2))<.001 and abs(float(total[0]['total_cny'])-round(amount+float(reserve[0]['total_cny']),2))<.001
active_models=[H/idle['model_xml'],H/idle['doors_model_xml'],H/'models/persistent_meal.xml']+[H/'models'/f'{ID}_internal_{r["index"]}.xml' for r in m['internal_paths'] if r.get('ok')]
checks['no_removed_R05_additions']=all(not any(any(word in g.get('name','') for word in ('elevator','pallet','storage_recess','recess_header','front_post','portal')) for g in E.parse(p).findall('.//geom')) for p in active_models)
walls=[E.parse(p).find(".//geom[@name='north_wall']") for p in active_models]
checks['original_wall_dimensions_restored']=all(g is not None and abs(float(g.get('size').split()[0])-1.85)<1e-9 and abs(float(g.get('size').split()[2])-1.2)<1e-9 and abs(float(g.get('pos').split()[1])-.62)<1e-9 for g in walls)
checks['only_replacement_faucet_active']=all(all(E.parse(p).find(f".//geom[@name='{n}']") is None for n in ('faucet_riser','sensor_faucet_stem','sensor_faucet_spout')) for p in active_models)
images=[]
for p in (H/'renders').glob('*.png'):
 with Image.open(p) as im:images.append(dict(file=p.name,size=list(im.size)));im.verify()
checks['images_max1600']=all(max(r['size'])<=1600 for r in images)
checks['requested_render_files']=all((H/'renders'/n).exists() for n in ('overview.png','parked_doors_open.png','under_cabinet_band.png','passing.png','executed_local_strip.png','reachability_study.png'))
frame=read(O/'frame_manifest.json');path_record=read(H/frame['path_file']);checks['honest24_checked_samples']=len(frame['frames'])==24 and frame['executed_meal'] is False and path_record['ok'] and frame['layout']==ID
render=read(H/'renders/manifest_v3.json');views={v['name']:v for v in render['views']};checks['render_poses_match_executed_samples']=all(views[f'frame_{r["frame"]:02}']['q']==r['q'] for r in frame['frames'])
if frame.get('prefix_only'):checks['prefix_not_claimed_complete']=path_record['complete_fold_unfold_pass'] is False and 'PREFIX' in path_record['scope']
resources=[dict(file=p.name,**read(p)) for p in (H/'audit').glob('*.resource.json')];checks['bounded_cpu_resource_limits']=all(r['timeout_s']<1200 and r['elapsed_s']<1200 and r['peak_MiB']<1900 and r['cpu_only'] for r in resources)
size=sum(p.stat().st_size for p in H.rglob('*') if p.is_file());checks['output_under3GB']=size<3_000_000_000
post=root/'posts/r07/integrator.md';checks['chinese_first_final_post']=post.read_text(encoding='utf-8').startswith('本轮') and 'This is a checkpoint' not in post.read_text(encoding='utf-8')
invalid=[]
for p in O.glob('*.json'):
 try:json.loads(p.read_text(encoding='utf-8-sig'),parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
 except Exception as exc:invalid.append(dict(file=p.name,error=str(exc)))
checks['top_level_json_finite']=not invalid
paths=[O/n for n in required]+[O/n for n in ('config.json','process_v3.json','intended_contacts.json','torque_envelope.json','fresh_admission.json','frame_manifest.json','faucet_v3.json','door_gate_regression_v3.json','state_sequence.json','persistent_model.json','passing.json')]+active_models+[post,H/frame['path_file']]
paths+=list((O/'static_v2'/ID).glob('*.json'))+list((O/'final_static_v2'/ID).glob('*.json'))+list((O/'motion_v2'/ID).glob('*.json'))+list((H/'renders/v3').glob('*.png'))+list((H/'renders').glob('*.png'))
paths +=[O/'layouts'/f'{ID}.json',O/'layouts'/f'{ID}_process.json',O/'layouts'/f'{ID}_envelope.json',O/'layouts'/f'{ID}_idle.json']
paths += [O/'failure_evidence_v3.json',O/'faucet_wall_v3.json',O/'arm_reconsideration_v3.json',O/'reachability_map_v3.csv']
paths += list(H.glob('*v3*r07.py'))
for study in s['faucet_enabled_paired_maps']:
 label=study['layout'];paths += [O/'layouts'/f'{label}.json',O/'reachability'/label/'R.json',O/'reachability'/label/'L.json']
 for suffix in ('_carriage_barriers.json','_fixed_obstructions.json','_target_certificates.json','_idle.json','_fold_continuation.json'):
  p=O/'layouts'/f'{label}{suffix}'
  if p.exists():paths.append(p)
paths += [p for directory in ('sources/faucet_v3','sources/faucet_wall_v3') for p in (H/directory).rglob('*') if p.is_file()]
entries=[dict(path=str(p.relative_to(root)).replace('\\','/'),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(set(paths))]
manifest=dict(schema='r07.v3.bound-delivery',created_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),selected_layout=ID,entries=entries,active_static_directory=f'sim/r07/integrator/results/static_v2/{ID}',active_fresh_replay_directory=f'sim/r07/integrator/results/final_static_v2/{ID}',active_paths_directory=f'sim/r07/integrator/results/motion_v2/{ID}',history=['posts/r07/integrator_v1.md','posts/r07/integrator_v2.md','sim/r07/integrator/history/v1','sim/r07/integrator/history/v2'],nonselected_result_policy='All other layout/static/path directories are exploration or superseded history. Counts never merge witnesses from different geometries.',engineering_pass=False)
(O/'manifest_v3.json').write_text(json.dumps(manifest,indent=2))
out=dict(schema='r07.v3.delivery-audit',artifact_checks_pass=all(checks.values()),engineering_pass=False,checks=checks,changed_copied_code=changed,invalid_json=invalid,selected_layout=ID,static_budget_coverage=dict(strokes_with96=s['strokes_with_96_starts'],total=105,complete=s['all_strokes_full_search_budget']),new_paired_maps=s['faucet_enabled_complete_paired_layout_maps'],copied_python_count=len(hashes),output_bytes=size,max_worker_tree_MiB=max(r['peak_MiB'] for r in resources),max_elapsed_s=max(r['elapsed_s'] for r in resources),numerical_worker_concurrency_max=3,concurrency_basis='At most three monitored foreground numerical worker slots. Launcher/monitor processes are not numerical workers; no other-round processes were touched.',resources=resources,images=images,limitations=['Artifact fidelity is separate from engineering success and complete search-budget coverage.','The stop condition is six further documented layout iterations, not a global architecture impossibility proof.','A checked deployment prefix is not a complete fold; disconnected paths are not a meal.'])
(O/'delivery_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(artifact_checks_pass=out['artifact_checks_pass'],failed=[k for k,x in checks.items() if not x],MiB=size/1048576,budget=out['static_budget_coverage'])));assert out['artifact_checks_pass']
