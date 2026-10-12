import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results_v3';I=H.parent/'integrator';W=H.parents[2]
def get(n):return json.loads((O/n).read_text())
s=get('reverify.json');print('STATIC',s['strokes_passed'],s['poses_total'],'models',all(x['model_matches_submission'] for x in s['rows']))
r=get('rules.json');print('RULES',{k:r[k] for k in ('code_match','source_files','source_mismatches','parsed_groups_equal','ledger_exact_match','contact_kinds','installed_dimension_changes','active_forbidden_storage_geoms','meal','cost')})
print('WALL',[x for x in r['wall_robot_pairs'] if x['mating_permission']]);print('SOURCE_GEOM',len(r['compiled_source_body_geoms']),all(x['all_unchanged'] for x in r['compiled_source_body_geoms']))
i=get('idle_L34.json');print('IDLE',{k:i[k] for k in ('populated_geometry_pass','door_sweep_pass','door_sweep_min_gap_mm','front_strip_pass','corridor_pass','folded_envelopes','public_ranges_ok','saved_fold_paths')})
print('IDLE_FAILURES',[(x['index'],x['direction'],x['states_checked'],x['first_rejection']) for x in i['fold_replays']])
if (O/'connections.json').exists():
 c=get('connections.json');print('CONNECTIONS',{k:c[k] for k in ('checked_connections','states_checked','longest_candidate_index','closest_gate_candidate_index','two_arm_candidates')})
paths=[json.loads(p.read_text()) for p in O.glob('internal_*.json')]
print('INTERNAL',[(p['index'],p['pass_'],p['states_checked'],p['duration_s'],p['point_arc_bound_m'],p['simultaneous_moving_segments']) for p in paths])
if paths:print('MINIMA',{cat:min(p['minimum_clearance_reserve_mm'].get(cat,1e9) for p in paths) for cat in paths[0]['minimum_clearance_reserve_mm']})
m=json.loads((I/'results/manifest_v3.json').read_text());bad=[x['path'] for x in m['entries'] if not (W/x['path']).exists() or hashlib.sha256((W/x['path']).read_bytes()).hexdigest()!=x['sha256']]
(O/'manifest_audit.json').write_text(json.dumps(dict(entries=len(m['entries']),mismatches=bad),indent=2));print('MANIFEST',len(m['entries']),bad)
