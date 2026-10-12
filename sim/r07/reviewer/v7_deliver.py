from pathlib import Path
import json,hashlib,re,ast
H=Path(__file__).resolve().parent;R=H.parents[2];O=H/'results_v7';I=H.parent/'integrator'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
s=load(O/'summary.json');eng=load(O/'engineering.json')
assert s['connection_records']==110 and s['saved_legs']==30 and s['passed_saved_legs']==30
assert s['internal_replays']>=8 and s['internal_passed']==s['internal_replays']
assert s['front_saved_edges']==8 and s['front_saved_passes']==8
assert s['front_reproduced']==s['front_rejections']
assert s['connection_max_step_mm']<=4.000000001 and s['internal_max_step_mm']<=4.000000001 and s['fold_max_step_mm']<=4.000000001
assert s['working_permission_leaks']==0 and s['all_model_hashes_match']
assert load(O/'grasp_identity_probe.json')['pass_']
assert load(O/'door_scope.json')['all_corrected_scope']
assert load(O/'auxiliary_idle.json')['pass_']
assert load(O/'front_ranges.json')['pass_']
assert load(O/'meal.json')['all_probes_pass'] and load(O/'meal.json')['all_snapshot_invariants']
input_hashes=[dict(**row,current_sha256=hashlib.sha256((R/row['file']).read_bytes()).hexdigest()) for row in eng['source_hashes']]
assert all(x['sha256']==x['current_sha256'] for x in input_hashes)
post=(H/'report_v7_template.md').read_text(encoding='utf-8')
values={k:str(s[k]) for k in ('connection_states','front_saved_edges','front_states','front_reproduced','front_rejections')}
values['connection_step']=f"{s['connection_max_step_mm']:.6f}"
values['resource_note']=f"Completed reviewer runs peak at {s['peak_worker_tree_MiB']:.1f} MiB per monitored worker tree. The first front-staging batch reached its 900 s supervisor limit after four complete edge checkpoints; the unfinished edge received no credit and the remaining original paths were resumed in a second bounded chunk. The inherited supervisor omits its normal resource record on timeout, so [the timeout record](../../sim/r07/reviewer/results_v7/front_timeout.json) explicitly records that missing peak measurement. No failed or interrupted check receives a pass."
for k,v in values.items():post=post.replace('{{'+k+'}}',v)
assert '{{' not in post
assert len(re.findall(r'^\d+\. \*\*(?:BLOCKING|HIGH|MEDIUM)',post,re.M))==11
dest=R/'posts/r07/reviewer.md';dest.write_text(post,encoding='utf-8')
links=[]
for target in re.findall(r'\]\(([^)]+)\)',post):
    if target.startswith(('http://','https://','C:')):continue
    q=(dest.parent/target).resolve();links.append(dict(target=target,exists=q.exists()))
assert all(x['exists'] or x['target'].endswith('/delivery.json') for x in links)
scripts=list(H.glob('v7_*.py'))
for p in scripts:ast.parse(p.read_text(encoding='utf-8'))
resources=[load(p) for p in (H/'audit').glob('v7*.resource.json')]
assert all(0<x['timeout_s']<1200 and x['peak_MiB']<1900 and x['cpu_only'] for x in resources)
files=[p for p in (R/'sim/r07').rglob('*') if p.is_file()];total=sum(p.stat().st_size for p in files)
assert total<3_000_000_000
newfiles=list(O.rglob('*'))+list((H/'audit_v7').rglob('*'))+scripts+[H/'report_v7_template.md',dest]+list((H/'audit').glob('v7*'))
newfiles=[p for p in newfiles if p.is_file()]
manifest=[dict(file=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in newfiles if p.name!='delivery.json']
out=dict(pass_=True,review='R07 seventh delivery',input_hashes_unchanged=True,input_hashes=input_hashes,post_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),post_links=links,python_syntax_files=len(scripts),resource_records=len(resources),max_worker_tree_MiB=max(x['peak_MiB'] for x in resources),max_numerical_workers=4,max_run_timeout_s=max(x['timeout_s'] for x in resources),resource_failures=[x for x in resources if x['exit_code']],whole_r07_bytes=total,new_delivery_bytes=sum(x['bytes'] for x in manifest),manifest=manifest,verdict=dict(strokes='45/59',connections='0/110',meal='fail',idle='fail',prep_min=None,cost_cny=344884.95,proceed=False,findings=11),scope='Read-only integrator/reference audit. Changes confined to sim/r07/reviewer and posts/r07/reviewer.md. No purchasing, supplier contact, physical tests or subagents.')
(O/'delivery.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ('input_hashes','manifest','resource_failures','post_links')},indent=2))
