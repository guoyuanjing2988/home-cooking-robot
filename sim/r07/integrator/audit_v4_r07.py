import json,csv,hashlib,xml.etree.ElementTree as E
from pathlib import Path
from PIL import Image
H=Path(__file__).resolve().parent;O=H/'results';root=H.parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={};hashes=read(H/'audit/copied_code_hashes.json');changed=[]
for name,digest in hashes.items():
 for base in (H,H/'upstream',root/'sim/r05/integrator'):
  p=base/name
  if not p.exists() or sha(p)!=digest:changed.append(str(p))
checks['all90_copied_modules_unchanged']=not changed
source_changes=[];source_count=0
for p in (root/'sim/r05/integrator/sources').rglob('*'):
 if not p.is_file():continue
 source_count+=1;q=H/'sources'/p.relative_to(root/'sim/r05/integrator/sources')
 if not q.exists() or sha(q)!=sha(p):source_changes.append(str(q))
checks['inherited_source_assets_unchanged']=not source_changes
s=read(O/'phase_summary.json');ID=s['selected_layout'];m=read(O/'motion.json');idle=read(O/'idle.json');sched=read(O/'schedule.json');fresh=read(O/'fresh_admission.json');P=read(O/'process_v4.json');base=read(O/'inherited_process_v3.json');seq=read(O/'state_sequence.json')
for key in ('finished_products','force_models','tools','acceptance'):checks[key+'_unchanged']=P[key]==base[key]
checks['all59_strokes_enumerated']=len(s['stroke_results'])==len(fresh['rows'])==59
checks['count_matches_fresh_admission']=s['strokes_passed']==sum(r['ok'] for r in fresh['rows'])
checks['positive_count_completed96']=all(r['starts']>=96 for r in fresh['rows'] if r['ok'])
checks['same_compiled_geometry']=all(r['same_compiled_geometry'] for r in fresh['rows'])
checks['all_positive_internal_attempted']=all(any(p['index']==r['index'] for p in m['internal_paths']) for r in fresh['rows'] if r['ok'])
checks['internal_step_bound']=all(p['final_replay']['max_point_step_mm']<=4.000001 for p in m['internal_paths'] if p['ok'])
checks['internal_witness_hashes_match']=all(p['source_static_sha256']==sha(O/'static_v4'/ID/f'{p["index"]}.json') for p in m['internal_paths'])
checks['branch_binding']=all('jaw_axis_branch' in p and 'endpoint_witness' in p for p in m['internal_paths'])
import mujoco
range_failures=[]
for p in m['internal_paths']:
 if not p['ok']:continue
 model=mujoco.MjModel.from_xml_path(str(H/'models'/f'{ID}_internal_{p["index"]}.xml'))
 for edge in p['edges']:
  for q in edge['path']:
   for j in range(model.njnt):
    if model.jnt_limited[j] and not model.jnt_range[j,0]-1e-8<=q[model.jnt_qposadr[j]]<=model.jnt_range[j,1]+1e-8:range_failures.append([p['index'],j])
checks['all_internal_vertices_in_joint_ranges']=not range_failures
# Each saved edge is sampled by linear joint interpolation; a convex interval
# containing both vertices contains every replay sample and the whole segment.
checks['local_connection_continuity']=all(not row.get('pass_') or row.get('raw_joint_continuity') or row.get('rebased_joint_continuity') and row.get('rebased_downstream_sha256')==sha(H/row['rebased_downstream_bundle']) and read(H/row['rebased_downstream_bundle'])['pass_'] for row in m['local_connection_diagnostics'])
checks['stop_condition_b']=s['new_documented_layout_iterations']>=6
checks['contact_transit_regression']=read(O/'contact_policy_regression.json')['pass_']
checks['door10mm_regression']=read(O/'door_gate_regression_v4.json')['pass_']
checks['rotated_face_regression']=read(O/'rotated_contact_regression_v4.json')['pass_']
contacts=read(O/'intended_contacts.json')['contacts'];checks['contact_kinds_and_identities']=all(c['kind'] in ('working_stroke','grasp_release_support') and c.get('object_id') and c.get('support_id')==c['face'] for c in contacts)
checks['conserved_symbolic_ledger']=not seq['discrete_state_chain_errors'] and seq['executed_state']==seq['initial_state'] and abs(seq['mass_input_kg']-.57)<1e-12
checks['all_four_initial_foods']=read(O/'persistent_model.json')['unique_food_bodies']==4
checks['all_connections_and_events_enumerated']=len(m['connections'])==m['connections_total'] and len(m['event_paths'])==m['event_paths_total']
event_names=[e['name'] for e in seq['events']]
checks['recipe_event_expansion']=event_names.count('carrot_guarded_prehalve_for_140mm_holder_limit')==1 and sum(n.startswith('carrot_two_half_') for n in event_names)==4 and sum(n.startswith('potato_fresh_starch_rinse_') for n in event_names)==3 and event_names.count('potato_drain')==event_names.count('bok_choy_soak')==1
checks['wash_valve_ordering']=all(s['state']['water']=='on' for s in seq['expanded_strokes'] if s['index'] in (2,8,17,26,33,35,39,41,47))
checks['no_unexecuted_meal_credit']=m['connections_pass']==0 and not m['meal_pass'] and sched['prep_min'] is None and not idle['meal_end_to_park_verified']
checks['correct_idle_semantics']=idle['doors_checked_against_corridor'] is False and 'task_fold' in idle and ('staged_fold' in idle or 'alternative_fold_goals' in idle)
required=['phase_summary.json','motion.json','idle.json','schedule.json','costs.csv','clearance.json','iterations.csv'];checks['required_deliverables']=all((O/n).exists() for n in required)
checks['histories_v1_v2_v3_preserved']=all((root/'posts/r07'/f'integrator_v{k}.md').exists() for k in (1,2,3)) and (H/'history/v3/results/phase_summary.json').exists()
cost=list(csv.DictReader((O/'costs.csv').open(encoding='utf-8-sig')));reserve=[x for x in cost if x['item']=='One15percent project reserve'];total=[x for x in cost if x['item']=='TOTAL'];amount=sum(float(x['total_cny']) for x in cost if x['item'] not in ('TOTAL','One15percent project reserve'))
checks['one_safety_one_reserve']=len(reserve)==len(total)==1 and sum('Inclusive home-safety' in x['item'] for x in cost)==1 and abs(float(reserve[0]['total_cny'])-round(amount*.15,2))<.001 and abs(float(total[0]['total_cny'])-round(amount+float(reserve[0]['total_cny']),2))<.001
models=[H/idle['model_xml'],H/idle['doors_model_xml'],H/'models/persistent_meal.xml']+[H/'models'/f'{ID}_internal_{p["index"]}.xml' for p in m['internal_paths'] if p['ok']]
checks['no_portal_elevator_pallet_extension']=all(not any(any(word in g.get('name','') for word in ('elevator','pallet','storage_recess','recess_header','front_post','portal')) for g in E.parse(p).findall('.//geom')) for p in models)
checks['no_ghost_helper']=all(not any(g.get('name','').startswith('L_') for g in E.parse(p).findall('.//geom')) for p in models)
walls=[E.parse(p).find(".//geom[@name='north_wall']") for p in models];checks['original_wall']=all(g is not None and abs(float(g.get('size').split()[0])-1.85)<1e-9 and abs(float(g.get('size').split()[2])-1.2)<1e-9 for g in walls)
images=[]
for name in ('overview.png','parked_doors_open.png','under_cabinet_band.png','passing.png','executed_local_strip.png','reachability_study.png'):
 p=H/'renders'/name
 if not p.exists():continue
 with Image.open(p) as im:images.append(dict(file=name,size=list(im.size)));im.verify()
checks['requested_images_all_under1600']=len(images)==6 and all(max(i['size'])<=1600 for i in images)
frame=read(O/'frame_manifest.json');record=read(H/frame['path_file']);manifest=read(H/'renders/manifest_v4.json');views={a['name']:a for a in manifest['views']}
checks['fresh_render_files_match_layout']=all((H/'renders'/a['image']).exists() and (H/'renders'/(a['name']+'.png')).exists() and sha(H/'renders'/a['image'])==sha(H/'renders'/(a['name']+'.png')) for a in manifest['views'])
render_resource=H/'audit'/f'v4_{ID}_export.resource.json'
checks['render_batch_completed']=render_resource.exists() and read(render_resource)['exit_code']==0
checks['24_real_checked_frames']=len(frame['frames'])==24 and record['ok'] and not frame['executed_meal'] and frame['layout']==ID and frame['model_sha256']==record['model_sha256']==hashlib.sha256((H/frame['model_xml']).read_text().encode('utf-8')).hexdigest() and frame.get('model_file_sha256')==record.get('model_file_sha256')==sha(H/frame['model_xml']) and all(views[f'frame_{f["frame"]:02}']['q']==f['q'] and record['states'][f['state_index']]['q']==f['q'] for f in frame['frames'])
resources=[dict(file=p.name,**read(p)) for p in (H/'audit').glob('v4_*.resource.json')];checks['bounded_resource_limits']=all(r['timeout_s']<1200 and r['elapsed_s']<1200 and r['peak_MiB']<1900 and r['cpu_only'] for r in resources)
size=sum(p.stat().st_size for p in H.rglob('*') if p.is_file());checks['under3GB']=size<3_000_000_000
post=root/'posts/r07/integrator.md';checks['chinese_first_post']=post.read_text(encoding='utf-8').startswith('本轮') and ID in post.read_text(encoding='utf-8')
invalid=[]
for p in O.glob('*.json'):
 try:json.loads(p.read_text(encoding='utf-8-sig'),parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
 except Exception as e:invalid.append(dict(file=p.name,error=str(e)))
checks['finite_json']=not invalid
paths=[O/n for n in required]+[O/'fresh_admission.json',O/'state_sequence.json',O/'persistent_model.json',O/'frame_manifest.json',O/'layout_iterations_v4.json',H/frame['path_file'],post]+models+list((O/'static_v4'/ID).glob('*.json'))+list((O/'motion_v4'/ID).glob('*.json'))+list(H.glob('*v4*r07.py'))+list((H/'renders/v4').glob('*.png'))
paths +=[H/'renders'/view['image'] for view in manifest['views']]
paths +=[H/'renders'/i['file'] for i in images]+[O/'clearance_refinement_v4.json',O/'sequence_revision_v4.json']
manifest_data=[dict(file=str(p.relative_to(root)),sha256=sha(p),bytes=p.stat().st_size) for p in dict.fromkeys(paths)];(O/'manifest_v4.json').write_text(json.dumps(manifest_data,indent=2))
out=dict(schema='r07.v4.delivery-audit',artifact_fidelity_pass=all(checks.values()),task_pass=False,checks=checks,changed_reference_files=changed,inherited_source_count=source_count,changed_source_assets=source_changes,resource_runs=resources,output_bytes=size,images=images,invalid_json=invalid,scope='Artifact fidelity is not meal or physical qualification. Numerical workers at most4; bounded foreground chunks, CPU only; helper process launchers/supervisors are not additional numerical workers.')
(O/'delivery_audit.json').write_text(json.dumps(out,indent=2));print('AUDIT',out['artifact_fidelity_pass'],[(k,x) for k,x in checks.items() if not x],size)
