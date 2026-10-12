from pathlib import Path
import json,math,hashlib,xml.etree.ElementTree as E
H=Path(__file__).resolve().parent;O=H/'results_v4';I=H.parent/'integrator'
def read(p):return json.loads(p.read_text())
rr=read(O/'reverify.json');rules=read(O/'rules.json');idle=read(O/'idle_L53.json');paths=[read(p) for p in O.glob('internal_*.json') if 'rebased' not in p.name];meta=read(O/'metadata.json');env=read(O/'envelopes.json');schedule=read(I/'results/schedule.json')
good=[p for r in rr['rows'] if r['ok'] for p in r['checks']]
mins={c:min(p['min_clearance'][c]['reserve_mm'] for p in good if c in p['min_clearance']) for c in good[0]['min_clearance']}
out=dict(static_strokes=rr['strokes_passed'],static_total=rr['strokes_total'],poses_replayed=rr['poses_total'],admitted_poses=len(good),static_model_hash_mismatches=[r['index'] for r in rr['rows'] if r['submitted_ok'] and not r['model_matches_submission']],internal_pass=sum(r['pass_'] for r in paths),internal_total=59,internal_states=sum(r['states_checked'] for r in paths),internal_max_step_mm=max(r['max_point_step_mm'] for r in paths),internal_bound_max_delta_m=max(r['max_bound_delta_m'] for r in paths),internal_actual_sphere_step_mm=max(r['max_actual_sphere_step_mm'] for r in paths),max_torque_ratio=max(r['max_check_torque_ratio'] for r in paths),min_grip=min(r['min_grip_margin'] for r in paths),isolated_duration_s=sum(r['duration_s'] for r in paths),duration_max_delta_s=max(abs(r['duration_s']-next(z['duration_s'] for z in schedule['accepted_internal_paths'] if z['index']==r['index'])) for r in paths),longest_internal=max(paths,key=lambda r:r['point_arc_bound_m'])['index'],tightest_internal=min(paths,key=lambda r:min(r['minimum_clearance_reserve_mm'].values()))['index'],static_min_reserves_mm=mins,path_min_reserves_mm={c:min(p['minimum_clearance_reserve_mm'].get(c,math.inf) for p in paths) for c in paths[0]['minimum_clearance_reserve_mm']},cost=rules['cost'],meal=rules['meal'],door_min_vertical_gap_mm=idle['door_sweep_min_gap_mm'],folded_envelopes=idle['folded_envelopes'],envelope_witnesses=env['rated_witnesses'],compiled_arm_mass_kg=sum(b['mass_kg'] for b in meta['compiled_bodies'] if b['name'] in ('R_base','R_shoulder_link','R_upper_arm_link','R_forearm_link','R_wrist_1_link','R_wrist_2_link','R_wrist_3_link')),helper_body_count=len(meta['helper_bodies']),connections_pass=0,connections_total=110,prep_min=None,idle_pass=False,meal_pass=False,proceed=False)
out['compiled_arm_mass_kg']=sum(b['mass_kg'] for b in meta['compiled_bodies'] if b['name'].startswith('R_arm_'))
out['compiled_body_masses']=meta['compiled_bodies']
out['bfp_geometry']=[g.attrib for g in E.parse(I/'models/L53_idle.xml').findall('.//geom') if g.get('name')=='bfp610_complete_envelope']
out['failed_internal_41']=read(I/'results/motion_v4/L53/internal_41.json')['final_replay']
for name in ('connections','fold'):
    if (O/(name+'.json')).exists():out[name]=read(O/(name+'.json'))
resources=[read(p) for p in (H/'audit').glob('v4*.resource.json')];out['resources']=resources
out['reviewer_v4_bytes']=sum(p.stat().st_size for folder in (O,H/'audit_v4') for p in folder.rglob('*') if p.is_file())
(O/'summary.json').write_text(json.dumps(out,indent=2,allow_nan=False),encoding='utf-8')
print({k:out[k] for k in ('static_strokes','static_total','internal_pass','internal_states','compiled_arm_mass_kg','isolated_duration_s','helper_body_count','reviewer_v4_bytes')})
print('BFP',out['bfp_geometry']);print('FAIL41',out['failed_internal_41'].get('reason'),out['failed_internal_41'].get('blocker'))
print('MASSES',[(b['name'],b['mass_kg']) for b in meta['compiled_bodies'] if b['name'].startswith('R_')])
