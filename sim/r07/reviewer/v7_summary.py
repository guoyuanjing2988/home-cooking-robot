from pathlib import Path
import json,hashlib,collections,math
H=Path(__file__).resolve().parent;O=H/'results_v7';I=H.parent/'integrator'
def read(n):return json.loads((O/n).read_text())
static=read('reverify.json');internals=[json.loads(p.read_text()) for p in O.glob('internal_*.json')]
rows={}
for folder in ('connection_rows_tail','connection_rows'):
    for p in (O/folder).glob('*.json'):rows[int(p.stem)]=json.loads(p.read_text())
rows=[rows[i] for i in sorted(rows)];legs=[dict(connection=r['index'],**l) for r in rows for l in r['legs']];saved=[l for l in legs if l['saved_path']]
rank=[]
for l in saved:
    for cat,margin in l['minimum_reserves_mm'].items():
        if cat!='self':rank.append(dict(connection=l['connection'],leg=l['name'],category=cat,reserve_mm=margin))
fold=read('fold_saved_edges.json');direct=read('fold.json');front=read('front_paths.json') if (O/'front_paths.json').exists() else {'rows':[],'rejections':[]}
passed=[c for r in static['rows'] if r['ok'] for c in r['checks']]
res=[dict(file=p.name,**json.loads(p.read_text())) for p in (H/'audit').glob('v7*.resource.json')]
result=dict(strokes_passed=static['strokes_passed'],strokes_total=static['strokes_total'],admitted_poses=len(passed),diagnostic_poses=static['poses_total'],static_failed=[r['index'] for r in static['rows'] if not r['ok']],max_static_torque=max(c['torque']['check'] for c in passed),min_static_grip=min(c['grip']['check'] for c in passed),internal_replays=len(internals),internal_passed=sum(r['pass_'] for r in internals),internal_indices=sorted(r['index'] for r in internals),internal_states=sum(r['states_checked'] for r in internals),internal_max_step_mm=max(r['max_point_step_mm'] for r in internals),internal_max_bound_delta_m=max(r['max_bound_delta_m'] for r in internals),connection_records=len(rows),connection_states=sum(r['states_checked'] for r in legs),saved_legs=len(saved),passed_saved_legs=sum(r['pass_'] for r in saved),all_model_hashes_match=all(l['model_hash_matches'] for l in legs),connection_max_step_mm=max(l['max_point_step_mm'] for l in legs),connection_max_bound_delta_m=max(l['max_bound_delta_m'] for l in legs),working_permission_leaks=sum(len(l['working_leaks']) for l in legs),longest_connection=max(saved,key=lambda l:l['point_arc_bound_m'])['connection'],longest_connection_arc_m=max(l['point_arc_bound_m'] for l in saved),tightest_connection=min(rank,key=lambda l:l['reserve_mm']),fold_saved_edges=len(fold['saved_edges']),fold_saved_passed=sum(r['pass_'] for r in fold['saved_edges']),fold_prefix_states=sum(r['states_checked'] for r in fold['saved_edges']),fold_attempts=fold['unique_attempts'],fold_rejections=len(fold['rejections']),fold_rejections_reproduced=sum(r['reproduced'] for r in fold['rejections']),direct_fold_directions=len(direct['routes']),direct_fold_states=direct['states_checked'],direct_fold_passes=sum(r['pass_'] for r in direct['routes']),front_saved_edges=len(front['rows']),front_saved_passes=sum(r['pass_'] for r in front['rows']),front_states=sum(r['states_checked'] for r in front['rows']),front_rejections=len(front['rejections']),front_reproduced=sum(r['reproduced'] for r in front['rejections']),fold_max_step_mm=max([r['max_point_step_mm'] for r in fold['saved_edges']+direct['routes']+front['rows']]),meal='fail',idle='fail',prep_min=None,cost_cny=read('rules.json')['cost']['total_cny'],proceed=False,findings=11,resource_records=res,peak_worker_tree_MiB=max(r['peak_MiB'] for r in res),max_numerical_worker_concurrency=4)
(O/'summary.json').write_text(json.dumps(result,indent=2))
(O/'connections_merged.json').write_text(json.dumps(dict(rows=rows,scope='Deduplicated completed source-model replays from sequential and priority-tail jobs.'),indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='resource_records'},indent=2))
