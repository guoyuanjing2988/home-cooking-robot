from pathlib import Path
import json,hashlib,re,ast
H=Path(__file__).resolve().parent;I=H.parent/'integrator';O=H/'results_v2';root=H.parents[2];post=root/'posts/r07/reviewer.md'
def read(n):return json.loads((O/n).read_text())
def dump(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
s=read('reverify.json');c=read('connections.json');rr=read('rules.json');p=[read(f'internal_{i}.json') for i in (14,18,24)];idle=[read(f'idle_{i}.json') for i in ('L13','L18','L19')]
summary=dict(delivery=2,selected_layout='L13',static_strokes_passed=s['strokes_passed'],static_strokes_total=s['strokes_total'],logical_passed=0,logical_total=27,internal_paths_passed=sum(x['pass_'] for x in p),internal_paths_total=105,connections_passed=0,connections_total=156,event_paths_passed=0,event_paths_total=557,meal='fail',idle='fail',prep_min=None,cost_cny=rr['cost']['total_cny'],proceed='no',findings=11,independent_static_candidates=sum(bool(x['checks']) for x in s['rows']),independent_static_poses=s['poses_total'],independent_internal_states=sum(x['states_checked'] for x in p),connection_diagnostics=c['checked_connections'],connection_scene_states=c['states_checked'],saved_meal_connection_trajectories_replayed=0,requested_20_saved_connection_replays_fulfilled=False,connection_evidence_limitation='No saved meal paths exist. 33 rejection diagnostics do not replace 20 complete saved trajectory replays.',idle_fold_directions_checked=sum(len(x['fold_replays']) for x in idle),saved_fold_trajectories_replayed=0,comparison_snapshots={x['layout']:bool(x['populated_geometry_pass'] and x['door_sweep_pass'] and x['front_strip_pass'] and x['corridor_pass']) for x in idle},max_internal_point_step_mm=max(x['max_point_step_mm'] for x in p),max_connection_diagnostic_grid_mm=max(x['maximum_grid_bound_mm'] for x in c['rows']),max_fold_diagnostic_grid_mm=max(y['max_point_step_mm'] for x in idle for y in x['fold_replays']),numerical_bound_disagreement_m=max([x['max_bound_delta_m'] for x in p]+[x['bound_delta_m'] for x in c['rank']]),corrected_idle_gripper_door_gate_mm=10,submitted_idle_gripper_door_gate_mm=5,stale_contact_ledger_rows=2,reviewer_new_IK_starts=0)
dump('review_summary.json',summary)
hashes=[]
for r in rr['code_hashes']:
    a=I/r['name'];b=I.parents[1]/'r05/integrator'/r['name'];current=hashlib.sha256(a.read_bytes()).hexdigest();hashes.append(dict(name=r['name'],unchanged=current==r['sha256'][1]==hashlib.sha256(b.read_bytes()).hexdigest()))
resources=[json.loads(x.read_text()) for x in (H/'audit').glob('v2_*.resource.json')]
text=post.read_text(encoding='utf-8');missing=[];links=[]
for link in re.findall(r'\]\(([^)]+)\)',text):
    if link.startswith(('http://','https://')):continue
    target=(post.parent/link).resolve();links.append(str(target))
    if target.name=='delivery_audit.json':continue
    if not target.exists():missing.append(link)
parses=[]
for file in list(O.glob('*.json')):
    json.loads(file.read_text());parses.append(file.name)
for file in H.glob('v2_*.py'):ast.parse(file.read_text())
names=re.findall(r'^([0-9]+)\. \*\*(BLOCKING|HIGH|MEDIUM)',text,re.M)
assert s['strokes_passed']==6 and all(x['pass_'] for x in p)
assert len(names)==11 and [int(x[0]) for x in names]==list(range(1,12))
assert not missing and all(x['unchanged'] for x in hashes)
assert all(x['peak_MiB']<1900 and x['elapsed_s']<1200 and x['timeout_s']<1200 for x in resources)
assert all(x['model_matches_submission'] for x in s['rows'])
assert max(summary['max_internal_point_step_mm'],summary['max_connection_diagnostic_grid_mm'],summary['max_fold_diagnostic_grid_mm'])<=4
assert text.startswith('中文摘要') and '## Verdict' in text and '## Findings' in text and '## Next steps' in text
files=list(H.rglob('*'));size=sum(x.stat().st_size for x in files if x.is_file());assert size<3*1024**3
manifest={str(x.relative_to(I)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [I/'results/process_v3.json',I/'results/motion.json',I/'results/phase_summary.json',I/'results/idle.json',I/'results/state_sequence.json',I/'results/torque_envelope.json',I/'results/intended_contacts.json']}
dump('delivery_audit.json',dict(pass_=True,findings=len(names),post=str(post),post_sha256=hashlib.sha256(post.read_bytes()).hexdigest(),checked_local_links=len(links),missing_links=missing,parsed_result_files=parses,copied_upstream_hashes=hashes,reviewed_input_hashes=manifest,resources=resources,peak_worker_MiB=max(x['peak_MiB'] for x in resources),longest_job_s=max(x['elapsed_s'] for x in resources),maximum_reviewer_workers=3,worker_cap_MiB=1900,reviewer_output_bytes=size,scope='Artifact validation only. Engineering verdict remains meal/idle FAIL; saved connection/fold replay requirements remain evidence-limited.'))
print(json.dumps(summary));print('DELIVERY PASS',size,'bytes',len(links),'local links','peak',max(x['peak_MiB'] for x in resources),'MiB')
