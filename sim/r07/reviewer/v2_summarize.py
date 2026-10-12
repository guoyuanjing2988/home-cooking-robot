from pathlib import Path
import json
H=Path(__file__).resolve().parent;O=H/'results_v2'
def read(n):return json.loads((O/n).read_text())
r=read('rules.json');s=read('reverify.json');c=read('connections.json')
print('STATIC',s['strokes_passed'],s['strokes_total'],s['poses_total'],'qsets',sum(bool(x['checks']) for x in s['rows']),'pass_ids',[x['index'] for x in s['rows'] if x['ok']],'modelmatch',all(x['model_matches_submission'] for x in s['rows']),'maxpose',max(x['max_position_error_delta_mm'] for x in s['rows']),'maxtq',max(x['max_torque_ratio_delta'] or 0 for x in s['rows']))
print('RULES',r['code_match'],len(r['code_hashes']),r['source_files'],r['source_mismatches'],r['parsed_groups_equal'],r['ledger_exact_match'],r['contact_kinds'],r['installed_dimension_changes'],r['meal'],r['cost'])
print('CONNECTIONS',c['checked_connections'],c['states_checked'],c['two_arm_candidates'],'long',c['longest_candidate_index'],'tight',c['closest_gate_candidate_index'],'maxstep',max(x['maximum_grid_bound_mm'] for x in c['rows']),'missing',len(c['missing_candidate_pairs']),'terminal',sum(x['source_terminal_available'] for x in c['rows']))
for i in (c['longest_candidate_index'],c['closest_gate_candidate_index'],14,54,90):
    x=next(x for x in c['rows'] if x['index']==i);print('CON',i,next(x for x in c['rank'] if x['index']==i),x['first_rejection'])
for n in ('L13','L18','L19'):
    x=read(f'idle_{n}.json');print('IDLE',n,x['populated_geometry_pass'],len(x['snapshot_hits']),x['door_sweep_min_gap_mm'],x['front_strip_pass'],x['corridor_pass'],'tq',x['holding_torque']['ratio'],x['public_ranges_ok'],x['folded_envelopes'])
    print('IDLEHITS',n,x['snapshot_hits'][:3]);print('FOLDS',n,[(z['index'],z['direction'],z['states_checked'],z['max_point_step_mm'],z['first_rejection']) for z in x['fold_replays']][:2])
for i in (14,18,24):
    p=O/f'internal_{i}.json'
    if p.exists():
        x=read(p.name);print('INTERNAL',i,{k:x[k] for k in ('pass_','states_checked','max_point_step_mm','max_actual_sphere_step_mm','max_bound_delta_m','max_check_torque_ratio','min_grip_margin','minimum_clearance_reserve_mm','point_arc_bound_m','duration_s','simultaneous_moving_segments')})
