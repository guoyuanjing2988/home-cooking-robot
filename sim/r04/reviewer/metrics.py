from pathlib import Path
import json,collections
H=Path(__file__).resolve().parent;I=H.parent/'integrator';R=H/'results'
def read(p):return json.loads(p.read_text())
v=read(R/'reverify_all.json');g=read(R/'geometry_independent.json');e=read(R/'envelope_independent.json')
strokes=[r for p in v['instances'] for r in p['strokes']];poses=[x for r in strokes for x in r['checks']]
out=dict(static={k:v[k] for k in ['logical_passed','logical_total','instances_passed','strokes_passed','strokes_total','poses_total']},max_pose_mm=max(x['position_mm'] for p in poses for x in p['errors']),max_pose_deg=max(x['orientation_deg'] for p in poses for x in p['errors']),max_check_ratio=max(p['torque']['check'] for p in poses),min_grip=min(p['grip']['check'] for p in poses),max_torque_delta=max(p['max_torque_delta'] for p in strokes),max_grip_delta=max(p['max_grip_delta'] for p in strokes),max_envelope_delta=max(abs(r['delta_Nm']) for r in e['rows']),doors=dict(count=len(g['door_violations']),categories=g['door_counts'],unresolved=len(g['door_unresolved'])),torso_components=len(g['human_corridor_intersections']),static_geometry_checks=len(g['static_crosschecks']),all_static_geometry_consistent=g['all_static_bounds_consistent'],max_geometry_radius=max(r['all_angle_radius_upper_m'] for r in g['motion_radius_bounds']),all_planner_motion_weights_conservative=g['all_2m_weights_conservative'],passing=g['passing'])
if (R/'motion_independent.json').exists():
 m=read(R/'motion_independent.json');out['motion']=dict(replayed=m['connections_replayed'],states=m['states_checked'],sections=[dict(stroke=x['stroke'],pass_=x['pass_'],reason=[e.get('reason') for e in x['edges']]) for x in m['sections']],connections=[dict(index=x['index'],sampled_clear=x['sampled_clear'],certificate=x['direct_certificate']) for x in m['connections']])
(R/'metrics.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
