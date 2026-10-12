from v3_common import *
import hashlib,csv
from planner_r05 import Planner
saved=read('motion_v2/L34/passing.json');ch=v.scene(104);ch.xml=(I/saved['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
pl=Planner(ch,{},seconds=65);cross=np.array(saved['q_crossing']);clear=pl.state(cross,{})
old=saved['planner'].get('last_rejection');replay=None
if old:
    ok=pl.state(np.array(old['q']),{});replay=dict(rejected=not ok,blockers=pl.last)
dump('passing.json',dict(pass_=False,equal_x_crossing_clear=clear,crossing_hits=f.contacts(ch,cross)[0],saved_rejection=replay,actual_planner_s=saved['planner']['planner_time_s'],allocated_s=saved['planner']['allocated_budget_s'],reason='Same shared lane; continuous order reversal must cross equal carriageX, with fixed overlapping carriage blocks. No passing or overlap execution path exists.'))
models=[]
for side in ('R','L'):
    bodies=[b for b in range(ch.m.nbody) if (mujoco.mj_id2name(ch.m,mujoco.mjtObj.mjOBJ_BODY,b) or '').startswith(side+'_') and not any(x in (mujoco.mj_id2name(ch.m,mujoco.mjtObj.mjOBJ_BODY,b) or '') for x in ('carriage','mount','tool','jaw','held'))]
    models.append(dict(side=side,body_mass_sum_kg=float(sum(ch.m.body_mass[b] for b in bodies)),bodies=[mujoco.mj_id2name(ch.m,mujoco.mjtObj.mjOBJ_BODY,b) for b in bodies]))
paths=[json.loads(p.read_text()) for p in O.glob('internal_*.json')];static=json.loads((O/'reverify.json').read_text());conn=json.loads((O/'connections.json').read_text());fold=json.loads((O/'fold_prefix.json').read_text());idle=json.loads((O/'idle_L34.json').read_text());rules=json.loads((O/'rules.json').read_text())
times={r['index']:r['duration_s'] for r in read('schedule.json')['accepted_internal_paths']}
mins={cat:min((p['minimum_clearance_reserve_mm'][cat],p['index']) for p in paths if cat in p['minimum_clearance_reserve_mm']) for cat in paths[0]['minimum_clearance_reserve_mm']}
logics={p['id'].split('.')[0]:[] for p in v.P['phases']}
for r in static['rows']:logics[r['stroke'].split('__')[0].split('.')[0]].append(r['ok'])
result=dict(strokes_passed=static['strokes_passed'],strokes_total=105,static_poses=static['poses_total'],logical_phases_passed=sum(all(a) for a in logics.values()),static_models_match=all(r['model_matches_submission'] for r in static['rows']),internal_passed=sum(p['pass_'] for p in paths),internal_states=sum(p['states_checked'] for p in paths),max_point_step_mm=max(p['max_point_step_mm'] for p in paths),max_actual_sphere_step_mm=max(p['max_actual_sphere_step_mm'] for p in paths),bound_delta_m=max(p['max_bound_delta_m'] for p in paths),longest_internal=max(paths,key=lambda p:p['point_arc_bound_m'])['index'],clearance_minimum_reserve_and_path=mins,internal_duration_sum_s=sum(p['duration_s'] for p in paths),max_duration_delta_s=max(abs(times[p['index']]-p['duration_s']) for p in paths),accepted_two_arm_moving_segments=sum(p['simultaneous_moving_segments'] for p in paths),max_internal_torque_ratio=max(p['max_check_torque_ratio'] for p in paths),min_internal_grip=min(p['min_grip_margin'] for p in paths),connection_diagnostics=conn['checked_connections'],connection_scene_states=conn['states_checked'],connection_diagnostic_passed=sum(p['diagnostic_pass'] for p in conn['rows']),longest_connection_candidate=conn['longest_candidate_index'],tightest_connection_candidate=conn['closest_gate_candidate_index'],connection_max_point_step_mm=max(p['maximum_grid_bound_mm'] for p in conn['rows']),connection_source_terminal_missing=sum(not p['source_terminal_available'] for p in conn['rows']),fold_prefixes=len(fold['rows'])//2,fold_prefix_states=sum(p['states_checked'] for p in fold['rows']),fold_prefix_max_point_step_mm=max(p['max_point_step_mm'] for p in fold['rows']),fold_prefix_all_pass=all(p['prefix_pass'] for p in fold['rows']),full_fold_diagnostic_states=sum(p['states_checked'] for p in idle['fold_replays']),idle_snapshot_pass=all(idle[k] for k in ('populated_geometry_pass','door_sweep_pass','front_strip_pass','corridor_pass','public_ranges_ok')),full_idle_pass=False,meal_pass=False,meal_connections_passed=0,meal_connections_total=156,prep_min=None,cost_cny=rules['cost']['total_cny'],proceed=False,OEM_body_mass_inventory=models)
dump('summary.json',result)
W=H.parents[2];manifest=read('manifest_v3.json');bad=[x['path'] for x in manifest['entries'] if hashlib.sha256((W/x['path']).read_bytes()).hexdigest()!=x['sha256']]
dump('manifest_audit.json',dict(entries=len(manifest['entries']),mismatches=bad))
print(json.dumps(result,indent=2))
