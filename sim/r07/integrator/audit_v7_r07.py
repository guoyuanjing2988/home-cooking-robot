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
s=read(O/'phase_summary.json');ID=s['selected_layout'];m=read(O/'motion.json');idle=read(O/'idle.json');schedule=read(O/'schedule.json');fresh=read(O/'fresh_admission.json');P=read(O/'process_v7.json');base=read(O/'inherited_process_v3.json');seq=read(O/'state_sequence.json')
for key in ('finished_products','force_models','acceptance'):checks[key+'_unchanged']=P[key]==base[key]
import copy
adjusted=copy.deepcopy(P['tools']);bail=adjusted['carried_bowl'].pop('r07_bail_adaptation',None)
if bail:adjusted['carried_bowl']['mass_kg']-=bail['added_mass_kg']
checks['original_tools_unchanged_except_declared_added_bail_mass']=all(adjusted[k]==val if k!='carried_bowl' else all((abs(adjusted[k][a]-b)<1e-9 if a=='mass_kg' else adjusted[k][a]==b) for a,b in val.items()) for k,val in base['tools'].items())
checks['grasp_window_real_identity_regression']=read(O/'grasp_identity_regression_v7.json')['pass_']
checks['functional_wash_failure_disclosed']=read(O/'wash_alignment_v7.json')['layout']==ID and s['functional_process_checks']['wash_alignment']==read(O/'wash_alignment_v7.json')
checks['all59_strokes_enumerated']=len(s['stroke_results'])==len(fresh['rows'])==59
checks['static_count_matches_fresh']=s['strokes_passed']==sum(r['ok'] for r in fresh['rows'])
checks['all_final_strokes_completed96']=all(r['starts']>=96 and r['complete'] for r in fresh['rows'])
frozen=read(O/f'frozen_v7_{ID}.json');static_records=[read(O/'static_v7'/ID/f'{i}.json') for i in range(59)]
checks['frozen_static_sources_unchanged']=all(digest==sha(O/'static_v7'/ID/name) for name,digest in frozen['static_sources'].items()) and len(frozen['static_sources'])==59
checks['frozen_expanded_joint_proposals_unchanged']=frozen['meal_proposals_sha256']==sha(O/'meal_pose_proposals_v7'/f'{ID}.json')
checks['96_distinct_recorded_starts_each']=all(len(d['rows'])>=96 and len({r['seed'] for r in d['rows']})>=96 and all(r['allocated_s']>=20 for r in d['rows']) for d in static_records)
checks['all_same_compiled_geometry']=all(r['same_compiled_geometry'] for r in fresh['rows'])
checks['all_positive_internal_attempted']=all(any(x['index']==r['index'] for x in m['internal_paths']) for r in fresh['rows'] if r['ok'])
checks['all59_internal_attempted']=set(x['index'] for x in m['internal_paths'])==set(range(59))
checks['all_internal_edge_budgets_at_least60']=all(e.get('allocated_budget_s',0)>=60 for x in m['internal_paths'] for e in x['edges'])
checks['internal_step_bound']=all(x['final_replay']['max_point_step_mm']<=4.000001 for x in m['internal_paths'] if x['ok'])
checks['internal_static_source_hashes_match']=all(x['source_static_sha256']==sha(O/'static_v7'/ID/f'{x["index"]}.json') for x in m['internal_paths'])
segments=[sg for ph in P['phases'] for sg in ph['segments']]
def internal_grip_valid(x):
 margin=x['final_replay']['min_grip_margin']
 return all(h.get('held')=='empty' for po in segments[x['index']]['poses'] for h in po.values()) if margin is None else margin>=1
checks['internal_load_grip']=all(x['final_replay']['max_envelope_ratio']<=1 and internal_grip_valid(x) for x in m['internal_paths'] if x['ok'])
rolled=[read(f) for f in (O/'rolled_internal_v7'/ID).glob('*.json')]
checks['all20_changed_roll_internals_attempted']=len(rolled)==20 and len({x['expanded_stroke']['id'] for x in rolled})==20 and len(m['expanded_internal_coverage']['rows'])==111
checks['rolled_internal_sources_models_budgets']=all(x['source_static_sha256']==sha(O/'static_v7'/ID/f'{x["expanded_stroke"]["index"]}.json') and x['model_sha256']==hashlib.sha256((H/x['model_xml']).read_text().encode()).hexdigest() and all(e['allocated_budget_s']>=60 for e in x['edges']) for x in rolled)
checks['rolled_internal_acceptance_no_meal_credit']=all(not x['meal_state_verified'] and (not x['ok'] or (x['endpoint_reference']['ok'] and x['final_replay']['pass_'] and x['final_replay']['max_point_step_mm']<=4.000001 and x['final_replay']['max_envelope_ratio']<=1 and x['final_replay']['min_grip_margin']>=1)) for x in rolled)
checks['expanded_internals_not_execution']=not any(x['executed_in_meal'] for x in m['expanded_internal_coverage']['rows'])
connections=[read(O/'connections_v7'/ID/f'{i}.json') for i in range(m['connections_total'])]
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
checks['conditional_before_and_after_masses_conserved']=all(abs(state['total_food_kg']-.57)<1e-12 for x in connections for state in [x['state_before'],x['conditional_state_after_attempt']]+[state for leg in x['legs'] for state in (leg['state'],leg['state_after_checked_leg'])])
checks['state_model_negative_regression']=read(O/'state_model_regression_v7.json')['pass_']
checks['actual_roll_joint_proposals']=read(O/'meal_pose_proposals_v7'/f'{ID}.json')['complete']
checks['six_further_evidenced_iterations']=s['new_documented_layout_iterations']>=6
checks['park_full_door10mm']=idle['doors_checked_against_corridor'] is False and idle['task_fold'].get('idle_all_robot_sweep_gap_mm')==10 and read(O/'door_scope_regression_v7.json')['pass_']
checks['door_pause_safety_logic']=read(O/'safety_v7.json')['pass_']
checks['all_connection_models_exclude_every_open_sweep_family']=all(not any(g.get('name','').startswith(('cabinet_door_sweep_','idle_full_sweep_cover_')) for g in E.parse(H/l['model_xml']).findall('.//geom')) for x in connections for l in x['legs'])
checks['fold_and_final_return_attempted']=bool(idle['task_fold'].get('attempts')) and bool(idle['meal_end_return_diagnostic'].get('attempts')) and bool(idle['alternative_fold_goals'].get('attempts'))
front=[idle[k] for k in ('front_fold','front_unfold','front_return','high_front_fold','high_front_unfold','high_front_return')]
checks['cartesian_front_stages_attempted']=all(d.get('complete',False) and d.get('attempts') for d in front)
checks['front_stage_source_geometry_and_budgets']=all(d.get('model_sha256')==hashlib.sha256((H/d['model_xml']).read_text().encode()).hexdigest() and all(e['allocated_budget_s']>=60 for a in d.get('attempts',[]) for e in a['edges']) for d in front)
checks['front_stage_accepted_replays']=all(a['max_point_step_mm']<=4.000001 and a['max_envelope_ratio']<=1 and all(e.get('endpoint_joint_continuity',False) and e.get('fresh_replay',{}).get('pass_',False) for e in a['edges']) for d in front for a in d.get('attempts',[]) if a.get('pass_',False))
checks['no_unexecuted_prep_time']=schedule['prep_min'] is None and not idle['meal_end_to_park_verified']
checks['rotato_removed']=read(O/'config.json')['peeler_model']=='custom_guarded_linear'
import mujoco
import numpy as np
carried_pose_errors=[]
for connection in connections:
 for leg in connection['legs']:
  name=leg['state']['attached']
  if not leg['pass_'] or name is None:continue
  model=mujoco.MjModel.from_xml_path(str(H/leg['model_xml']));data=mujoco.MjData(model);data.qpos[:]=leg['planner']['path'][-1];mujoco.mj_kinematics(model,data);site=model.site('R_prep').id
  frame=np.eye(4);frame[:3,3]=data.site_xpos[site];frame[:3,:3]=data.site_xmat[site].reshape(3,3)
  carried_pose_errors.append(float(np.max(abs(frame-np.array(leg['state_after_checked_leg']['objects'][name]['pose'])))))
checks['checked_carried_object_pose_matches_endpoint_FK']=all(error<1e-7 for error in carried_pose_errors)
checks['failed_legs_do_not_update_recorded_object_pose']=all(leg['state']==leg['state_after_checked_leg'] for connection in connections for leg in connection['legs'] if not leg['pass_'])
range_errors=[];models=[H/idle['model_xml'],H/idle['doors_model_xml'],H/'models/persistent_meal.xml']+[H/'models'/f'{ID}_internal_{x["index"]}.xml' for x in m['internal_paths'] if x['ok']]
for x in m['internal_paths']:
 if not x['ok']:continue
 model=mujoco.MjModel.from_xml_path(str(H/'models'/f'{ID}_internal_{x["index"]}.xml'))
 for edge in x['edges']:
  for q in edge['path']:
   for j in range(model.njnt):
    if model.jnt_limited[j] and not model.jnt_range[j,0]-1e-8<=q[model.jnt_qposadr[j]]<=model.jnt_range[j,1]+1e-8:range_errors.append([x['index'],j])
checks['all_internal_joint_ranges']=not range_errors
rolled_range_errors=[]
for x in rolled:
 if not x['ok']:continue
 model=mujoco.MjModel.from_xml_path(str(H/x['model_xml']))
 for edge in x['edges']:
  for q in edge['path']:
   for j in range(model.njnt):
    if model.jnt_limited[j] and not model.jnt_range[j,0]-1e-8<=q[model.jnt_qposadr[j]]<=model.jnt_range[j,1]+1e-8:rolled_range_errors.append([x['ordinal'],j])
checks['all_rolled_joint_ranges']=not rolled_range_errors
checks['accepted_rolled_paths_timed_separately']=len(schedule['accepted_rolled_paths'])==sum(x['ok'] for x in rolled) and abs(schedule['isolated_changed_roll_sum_s']-sum(x['duration_s'] for x in schedule['accepted_rolled_paths']))<1e-9
checks['no_forbidden_structures_or_retired_peeler']=all(not any(any(word in g.get('name','') for word in ('elevator','pallet','storage_recess','recess_header','front_post','portal','rotato_','sammic_m5_')) for g in E.parse(f).findall('.//geom')) for f in models)
checks['no_ghost_helper']=all(not any(g.get('name','').startswith('L_') for g in E.parse(f).findall('.//geom')) for f in models)
walls=[E.parse(f).find(".//geom[@name='north_wall']") for f in models];checks['original_wall_dimensions']=all(g is not None and abs(float(g.get('size').split()[0])-1.85)<1e-9 and abs(float(g.get('size').split()[2])-1.2)<1e-9 for g in walls)
checks['full151mm_base_and160elbow']=all(E.parse(f).find(".//geom[@name='R_current151mm_base_cover']") is not None and abs(float(E.parse(f).find(".//joint[@name='R_elbow_joint']").get('range').split()[1])-2.7925268)<1e-6 for f in models)
required=['phase_summary.json','motion.json','idle.json','schedule.json','costs.csv','clearance.json','iterations.csv'];checks['required_artifacts']=all((O/n).exists() for n in required)
clear=read(O/'clearance.json');refined=read(O/'clearance_refinement_v7.json')
checks['full_clearance_refinement_current']=refined['layout']==ID and refined['complete'] and clear['refined_reserve_assessment']['complete'] and refined['counts']['path']==sum(x['final_replay']['states_checked'] for x in m['internal_paths'] if x['ok'])
checks['connection_summary_counts_match']=read(O/'connection_summary_v7.json')['attempted']==len(connections) and read(O/'connection_summary_v7.json')['conditional_pass']==sum(x['pass_'] for x in connections)
checks['six_history_posts_preserved']=all((root/'posts/r07'/f'integrator_v{k}.md').exists() for k in (1,2,3,4,5,6)) and (H/'history/v6/delivery_snapshot.zip').exists()
checks['full_bowl_geometry_preserved']=read(O/'bail_geometry_validation_v7.json')['pass_']
checks['selected_stored_bowl_packing_clear']=read(O/'layouts'/f'{ID}_dock_packing_v7.json')['pass_']
cost=list(csv.DictReader((O/'costs.csv').open(encoding='utf-8-sig')));reserve=[x for x in cost if x['item']=='One15percent project reserve'];totals=[x for x in cost if x['item']=='TOTAL'];amount=sum(float(x['total_cny']) for x in cost if x['item'] not in ('TOTAL','One15percent project reserve'))
checks['one_safety_one_reserve']=len(reserve)==len(totals)==1 and sum('Inclusive home-safety' in x['item'] for x in cost)==1 and abs(float(reserve[0]['total_cny'])-round(amount*.15,2))<.001 and abs(float(totals[0]['total_cny'])-round(amount+float(reserve[0]['total_cny']),2))<.001
images=[]
for name in ('overview.png','parked_doors_open.png','under_cabinet_band.png','passing.png','executed_local_strip.png','reachability_study.png'):
 f=H/'renders'/name
 if f.exists():
  with Image.open(f) as im:images.append(dict(file=name,size=list(im.size)));im.verify()
checks['all_requested_images_under1600']=len(images)==6 and all(max(i['size'])<=1600 for i in images)
frame=read(O/'frame_manifest.json');record=read(H/frame['path_file']);manifest=read(H/'renders/manifest_v7.json');views={x['name']:x for x in manifest['views']}
checks['24_actual_checked_simulation_frames']=len(frame['frames'])==24 and record['ok'] and frame['layout']==ID and not frame['executed_meal'] and frame['model_sha256']==record['model_sha256']==hashlib.sha256((H/frame['model_xml']).read_text().encode()).hexdigest() and all(record['states'][f['state_index']]['q']==f['q']==views[f'frame_{f["frame"]:02}']['q'] for f in frame['frames'])
checks['renders_match_manifest']=all((H/'renders'/v['image']).exists() and (H/'renders'/(v['name']+'.png')).exists() and sha(H/'renders'/v['image'])==sha(H/'renders'/(v['name']+'.png')) for v in manifest['views'])
checks['shared_render_meshes_intact']=all(sha((H/'renders'/v['scene']).parent/read(H/'renders'/v['scene'])['meshes_file'])==read(H/'renders'/v['scene'])['meshes_sha256'] for v in manifest['views'])
checks['rendered_scenes_unchanged_at_final_export']=read(O/'render_scene_reexport_v7.json')['pass_']
resources=[dict(file=f.name,**read(f)) for f in (H/'audit').glob('v7_*.resource.json')]
checks['bounded_cpu_resource_limits']=all(x['timeout_s']<1200 and x['elapsed_s']<1200 and x['peak_MiB']<2000 and x['cpu_only'] for x in resources)
size=sum(f.stat().st_size for f in H.rglob('*') if f.is_file());checks['under3GB']=size<3_000_000_000
post=root/'posts/r07/integrator.md';checks['post_current_and_chinese_first']=post.read_text(encoding='utf-8').startswith('本轮') and ID in post.read_text(encoding='utf-8')
paths=[O/n for n in required]+[O/'fresh_admission.json',O/'state_sequence.json',O/'persistent_model.json',O/'frame_manifest.json',O/'layout_iterations_v7.json',O/'state_model_regression_v7.json',H/'source_review_v7.json',post]+models+list((O/'static_v7'/ID).glob('*.json'))+list((O/'connections_v7'/ID).glob('*.json'))+list((O/'motion_v7'/ID).glob('*.json'))+list(H.glob('*v7*r07.py'))+[H/'renders'/x['image'] for x in manifest['views']]
paths += [O/'connection_summary_v7.json',O/'clearance_refinement_v7.json',O/'reachability_map_v7.csv',O/'door_scope_regression_v7.json',O/'safety_v7.json',O/'counter_area_v7.json',H/'renders/reachability_study.png',H/'renders/executed_local_strip.png',H/'renders/counter_free_area.png']
paths += [f for f in (H/'audit').glob('v7_*recovery.json')]
paths += list((O/'rolled_internal_v7'/ID).glob('*.json'))+[H/x['model_xml'] for x in rolled]+[O/f'normalized_park_v7_{ID}.json']
paths += list(O.glob('clearance_refinement_v7_lane*.json'))+[O/f'frozen_v7_{ID}.json']
paths += [O/'render_scene_reexport_v7.json']
continuation=read(O/'front_replay_continuation_summary_v7.json')
checks['timed_front_replay_proposals_resumed']=len(continuation['attempts'])==4 and all(a['completed_replays']>=1 or a['rejected_replay_reasons'] for a in continuation['attempts'])
paths += [O/'front_replay_continuation_summary_v7.json']+list((O/'front_replay_continuations_v7').glob('*.json'))
entries=[dict(file=str(f.relative_to(root)),sha256=sha(f),bytes=f.stat().st_size) for f in dict.fromkeys(paths)];(O/'manifest_v7.json').write_text(json.dumps(entries,indent=2))
slots=[dict(file=f.name,**read(f)) for f in (H/'audit').glob('v7_*.slot.json')];events=sorted([(x['acquired_unix'],1) for x in slots]+[(x['released_unix'],-1) for x in slots]);active=0;peak=0
for _,delta in events:active+=delta;peak=max(peak,active)
checks['maximum_four_workers_v7']=peak<=4 and all(0<=x['slot']<4 and x['limit']==4 for x in slots)
checks['all_finished_numeric_runs_have_slot_record']=all(x['file']=='v7_bootstrap.resource.json' or (H/'audit'/x['file'].replace('.resource.json','.slot.json')).exists() for x in resources)
out=dict(schema='r07.v7.delivery-audit',artifact_fidelity_pass=all(checks.values()),task_pass=False,resource_compliance_pass=checks['maximum_four_workers_v7'] and checks['bounded_cpu_resource_limits'],worker_peak=peak,slot_intervals=slots,checks=checks,changed_reference_files=changed,inherited_source_count=source_count,changed_source_assets=source_changes,resource_runs=resources,output_bytes=size,images=images,scope='Artifact fidelity is not a completed meal or hardware/food-quality qualification. V7 uses four OS-held worker slots and bounded foreground CPU chunks. V5 resource incident remains in preserved history. Supervisors and Windows venv launchers are not additional numerical workers.')
(O/'delivery_audit.json').write_text(json.dumps(out,indent=2));print('AUDIT',out['artifact_fidelity_pass'],[k for k,x in checks.items() if not x],size)
