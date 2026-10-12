"""Artifact fidelity and task outcome are deliberately separate."""
import json,csv,hashlib,xml.etree.ElementTree as E
from pathlib import Path
from PIL import Image
H=Path(__file__).resolve().parent;O=H/'results';root=H.parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={};copied=read(H/'audit/copied_code_hashes.json');changed=[]
for name,digest in copied.items():
 for base in (H,H/'upstream',root/'sim/r05/integrator'):
  f=base/name
  if not f.exists() or sha(f)!=digest:changed.append(str(f))
checks['all90_copied_modules_unchanged']=not changed
source_changes=[];source_count=0
for f in (root/'sim/r05/integrator/sources').rglob('*'):
 if not f.is_file():continue
 source_count+=1;g=H/'sources'/f.relative_to(root/'sim/r05/integrator/sources')
 if not g.exists() or sha(f)!=sha(g):source_changes.append(str(g))
checks['all_inherited_source_assets_unchanged']=not source_changes
s=read(O/'phase_summary.json');ID=s['selected_layout'];m=read(O/'motion.json');idle=read(O/'idle.json');schedule=read(O/'schedule.json');fresh=read(O/'fresh_admission.json');P=read(O/'process_v5.json');base=read(O/'inherited_process_v3.json');seq=read(O/'state_sequence.json')
for key in ('finished_products','force_models','tools','acceptance'):checks[key+'_unchanged']=P[key]==base[key]
checks['all59_strokes_enumerated']=len(s['stroke_results'])==len(fresh['rows'])==59
checks['static_count_matches_fresh']=s['strokes_passed']==sum(r['ok'] for r in fresh['rows'])
checks['all_final_strokes_completed96']=all(r['starts']>=96 and r['complete'] for r in fresh['rows'])
checks['all_same_compiled_geometry']=all(r['same_compiled_geometry'] for r in fresh['rows'])
checks['all_positive_internal_attempted']=all(any(x['index']==r['index'] for x in m['internal_paths']) for r in fresh['rows'] if r['ok'])
checks['all59_internal_attempted']=set(x['index'] for x in m['internal_paths'])==set(range(59))
checks['all_internal_edge_budgets_at_least60']=all(e.get('allocated_budget_s',0)>=60 for x in m['internal_paths'] for e in x['edges'])
checks['internal_step_bound']=all(x['final_replay']['max_point_step_mm']<=4.000001 for x in m['internal_paths'] if x['ok'])
checks['internal_static_source_hashes_match']=all(x['source_static_sha256']==sha(O/'static_v5'/ID/f'{x["index"]}.json') for x in m['internal_paths'])
checks['internal_load_grip']=all(x['final_replay']['max_envelope_ratio']<=1 and x['final_replay']['min_grip_margin']>=1 for x in m['internal_paths'] if x['ok'])
connections=[read(O/'connections_v5'/ID/f'{i}.json') for i in range(m['connections_total'])]
checks['all110_connections_actual_planner']=len(connections)==110 and all(x['planner_ran'] and x['legs'] for x in connections)
checks['all_connection_leg_budgets_at_least60']=all(l['allocated_budget_s']>=60 and l['planner']['allocated_budget_s']>=60 for x in connections for l in x['legs'])
def grip_valid(leg):
 margin=leg['replay']['min_grip_margin']
 return (leg['state']['attached'] is None) if margin is None else margin>=1
checks['accepted_connection_replay_bound_and_load']=all(l['replay']['max_point_step_mm']<=4.000001 and l['replay']['max_envelope_ratio']<=1 and grip_valid(l) for x in connections for l in x['legs'] if l['pass_'])
checks['no_working_permission_on_connection']=all(x['working_permissions_on_connection']==0 and all(w.get('kind')!='working_stroke' for l in x['legs'] for w in l['planner'].get('contact_windows',[])) for x in connections)
checks['all_connection_model_hashes_match']=all(l['model_sha256']==hashlib.sha256((H/l['model_xml']).read_text().encode()).hexdigest() for x in connections for l in x['legs'])
checks['all_connection_source_hashes_match']=all(q['sha256']==sha(H/q['file']) for x in connections for q in x['source_proposals'])
checks['later_conditional_paths_not_execution']=all(not x['executed'] and not x.get('committed',True) for x in connections) and m['connections_pass']==0 and m['executed_prefix_connections']==0 and not m['meal_pass']
checks['conserved_food_ledger']=all(x['mass_conserved'] and abs(x['state_before']['total_food_kg']-.57)<1e-12 for x in connections) and seq['executed_state']==seq['initial_state'] and abs(seq['mass_input_kg']-.57)<1e-12
checks['state_model_negative_regression']=read(O/'state_model_regression_v5.json')['pass_']
checks['actual_roll_joint_proposals']=read(O/'meal_pose_proposals_v5'/f'{ID}.json')['complete']
checks['six_further_evidenced_iterations']=s['new_documented_layout_iterations']>=6
checks['park_full_door10mm']=idle['doors_checked_against_corridor'] is False and idle['task_fold'].get('all_robot_door_gap_mm')==10 and 'alternative_fold_goals' in idle
checks['fold_and_final_return_attempted']=bool(idle['task_fold'].get('attempts')) and bool(idle['meal_end_return_diagnostic'].get('attempts')) and bool(idle['alternative_fold_goals'].get('attempts'))
checks['no_unexecuted_prep_time']=schedule['prep_min'] is None and not idle['meal_end_to_park_verified']
checks['rotato_removed']=read(O/'config.json')['peeler_model']=='custom_guarded_linear'
import mujoco
range_errors=[];models=[H/idle['model_xml'],H/idle['doors_model_xml'],H/'models/persistent_meal.xml']+[H/'models'/f'{ID}_internal_{x["index"]}.xml' for x in m['internal_paths'] if x['ok']]
for x in m['internal_paths']:
 if not x['ok']:continue
 model=mujoco.MjModel.from_xml_path(str(H/'models'/f'{ID}_internal_{x["index"]}.xml'))
 for edge in x['edges']:
  for q in edge['path']:
   for j in range(model.njnt):
    if model.jnt_limited[j] and not model.jnt_range[j,0]-1e-8<=q[model.jnt_qposadr[j]]<=model.jnt_range[j,1]+1e-8:range_errors.append([x['index'],j])
checks['all_internal_joint_ranges']=not range_errors
checks['no_forbidden_structures_or_retired_peeler']=all(not any(any(word in g.get('name','') for word in ('elevator','pallet','storage_recess','recess_header','front_post','portal','rotato_','sammic_m5_')) for g in E.parse(f).findall('.//geom')) for f in models)
checks['no_ghost_helper']=all(not any(g.get('name','').startswith('L_') for g in E.parse(f).findall('.//geom')) for f in models)
walls=[E.parse(f).find(".//geom[@name='north_wall']") for f in models];checks['original_wall_dimensions']=all(g is not None and abs(float(g.get('size').split()[0])-1.85)<1e-9 and abs(float(g.get('size').split()[2])-1.2)<1e-9 for g in walls)
checks['full151mm_base_and160elbow']=all(E.parse(f).find(".//geom[@name='R_current151mm_base_cover']") is not None and abs(float(E.parse(f).find(".//joint[@name='R_elbow_joint']").get('range').split()[1])-2.7925268)<1e-6 for f in models)
required=['phase_summary.json','motion.json','idle.json','schedule.json','costs.csv','clearance.json','iterations.csv'];checks['required_artifacts']=all((O/n).exists() for n in required)
clear=read(O/'clearance.json');refined=read(O/'clearance_refinement_v5.json')
checks['full_clearance_refinement_current']=refined['layout']==ID and refined['complete'] and clear['refined_reserve_assessment']['complete'] and refined['counts']['path']==sum(x['final_replay']['states_checked'] for x in m['internal_paths'] if x['ok'])
checks['connection_summary_counts_match']=read(O/'connection_summary_v5.json')['attempted']==len(connections) and read(O/'connection_summary_v5.json')['conditional_pass']==sum(x['pass_'] for x in connections)
checks['four_history_posts_preserved']=all((root/'posts/r07'/f'integrator_v{k}.md').exists() for k in (1,2,3,4)) and (H/'history/v4/delivery_snapshot.zip').exists()
cost=list(csv.DictReader((O/'costs.csv').open(encoding='utf-8-sig')));reserve=[x for x in cost if x['item']=='One15percent project reserve'];totals=[x for x in cost if x['item']=='TOTAL'];amount=sum(float(x['total_cny']) for x in cost if x['item'] not in ('TOTAL','One15percent project reserve'))
checks['one_safety_one_reserve']=len(reserve)==len(totals)==1 and sum('Inclusive home-safety' in x['item'] for x in cost)==1 and abs(float(reserve[0]['total_cny'])-round(amount*.15,2))<.001 and abs(float(totals[0]['total_cny'])-round(amount+float(reserve[0]['total_cny']),2))<.001
images=[]
for name in ('overview.png','parked_doors_open.png','under_cabinet_band.png','passing.png','executed_local_strip.png','reachability_study.png'):
 f=H/'renders'/name
 if f.exists():
  with Image.open(f) as im:images.append(dict(file=name,size=list(im.size)));im.verify()
checks['all_requested_images_under1600']=len(images)==6 and all(max(i['size'])<=1600 for i in images)
frame=read(O/'frame_manifest.json');record=read(H/frame['path_file']);manifest=read(H/'renders/manifest_v5.json');views={x['name']:x for x in manifest['views']}
checks['24_actual_checked_simulation_frames']=len(frame['frames'])==24 and record['ok'] and frame['layout']==ID and not frame['executed_meal'] and frame['model_sha256']==record['model_sha256']==hashlib.sha256((H/frame['model_xml']).read_text().encode()).hexdigest() and all(record['states'][f['state_index']]['q']==f['q']==views[f'frame_{f["frame"]:02}']['q'] for f in frame['frames'])
checks['renders_match_manifest']=all((H/'renders'/v['image']).exists() and (H/'renders'/(v['name']+'.png')).exists() and sha(H/'renders'/v['image'])==sha(H/'renders'/(v['name']+'.png')) for v in manifest['views'])
resources=[dict(file=f.name,**read(f)) for f in (H/'audit').glob('v5_*.resource.json')]
checks['bounded_cpu_resource_limits']=all(x['timeout_s']<1200 and x['elapsed_s']<1200 and x['peak_MiB']<2000 and x['cpu_only'] for x in resources)
size=sum(f.stat().st_size for f in H.rglob('*') if f.is_file());checks['under3GB']=size<3_000_000_000
post=root/'posts/r07/integrator.md';checks['post_current_and_chinese_first']=post.read_text(encoding='utf-8').startswith('本轮') and ID in post.read_text(encoding='utf-8')
paths=[O/n for n in required]+[O/'fresh_admission.json',O/'state_sequence.json',O/'persistent_model.json',O/'frame_manifest.json',O/'layout_iterations_v5.json',O/'state_model_regression_v5.json',O/'research_v5.json',post]+models+list((O/'static_v5'/ID).glob('*.json'))+list((O/'connections_v5'/ID).glob('*.json'))+list((O/'motion_v5'/ID).glob('*.json'))+list(H.glob('*v5*r07.py'))+[H/'renders'/x['image'] for x in manifest['views']]
paths += [O/'connection_summary_v5.json',O/'clearance_refinement_v5.json',O/'reachability_map_v5.csv',H/'audit/v5_worker_overlap_incident.json',H/'renders/reachability_study.png',H/'renders/executed_local_strip.png']
entries=[dict(file=str(f.relative_to(root)),sha256=sha(f),bytes=f.stat().st_size) for f in dict.fromkeys(paths)];(O/'manifest_v5.json').write_text(json.dumps(entries,indent=2))
incident=read(H/'audit/v5_worker_overlap_incident.json')
out=dict(schema='r07.v5.delivery-audit',artifact_fidelity_pass=all(checks.values()),task_pass=False,resource_compliance_pass=False,resource_incident=incident,checks=checks,changed_reference_files=changed,inherited_source_count=source_count,changed_source_assets=source_changes,resource_runs=resources,output_bytes=size,images=images,scope='Artifact fidelity is not a completed meal, resource compliance or hardware/food-quality qualification. One brief five-worker overlap violated the four-worker cap and is recorded. Runs otherwise use bounded foreground CPU chunks. Supervisors and Windows venv launchers are not additional numerical workers.')
(O/'delivery_audit.json').write_text(json.dumps(out,indent=2));print('AUDIT',out['artifact_fidelity_pass'],[k for k,x in checks.items() if not x],size)
