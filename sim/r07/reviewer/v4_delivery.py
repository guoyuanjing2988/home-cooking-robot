from pathlib import Path
import json,hashlib,ast,re
H=Path(__file__).resolve().parent;O=H/'results_v4';I=H.parent/'integrator';root=I.parents[2];post=root/'posts/r07/reviewer.md'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=read(O/'summary.json');rules=read(O/'rules.json');con=read(O/'connections.json');fold=read(O/'fold.json');idle=read(O/'idle_L53.json')
assert (s['static_strokes'],s['static_total'],s['internal_pass'],s['internal_states'])==(42,59,41,2564)
assert con['checked_connections']==38 and con['states_checked']==12071
assert sum(r['saved_path_available'] and r['diagnostic_pass'] for r in con['rows'])==3
assert all(r['max_point_step_mm']<=4+1e-8 for r in con['rows'])
assert all(not r['working_permission_leaks'] for r in con['rows'])
assert fold['states_checked']==5588 and len(fold['routes'])==22 and not any(r['pass_'] for r in fold['routes'])
assert all(r['max_point_step_mm']<=4+1e-8 for r in fold['routes'])
assert idle['populated_geometry_pass'] and idle['door_sweep_pass'] and idle['front_strip_pass'] and idle['corridor_pass']
assert not idle['doors_checked_against_corridor'] and not idle['full_idle_pass']
assert rules['code_match'] and not rules['source_mismatches'] and rules['ledger_exact_match'] and not rules['contact_errors']
assert rules['meal']['events']==206 and rules['meal']['motion_events']==204
assert s['compiled_arm_mass_kg']==20.9949 and s['helper_body_count']==0
assert rules['cost']['total_cny']==339249.95
assert all(r['pass_'] for r in rules['work_probes'])
code=[]
for p in sorted(H.glob('v4*.py')):
    ast.parse(p.read_text(encoding='utf-8-sig'));code.append(dict(path=str(p.relative_to(root)),sha256=digest(p)))
parsed=[]
for p in sorted(O.glob('*.json')):
    read(p);parsed.append(dict(path=str(p.relative_to(root)),sha256=digest(p)))
unchanged=[]
R05=I.parents[1]/'r05/integrator'
for p in (I/'upstream').glob('*.py'):
    hs=[digest(q) for q in (p,I/p.name,R05/p.name)];assert len(set(hs))==1;unchanged.append(p.name)
t=post.read_text(encoding='utf-8');assert t.startswith('中文摘要：')
links=re.findall(r'\]\(([^)]+)\)',t);missing=[]
for link in links:
    if link.startswith(('https://','http://')):continue
    target=(post.parent/link.split('#')[0]).resolve()
    if target!=(O/'delivery.json').resolve() and not target.exists():missing.append(link)
assert not missing,missing
findings=re.findall(r'^\d+\. \*\*(?:BLOCKING|HIGH|MEDIUM)',t,re.M);assert len(findings)==10
for word in ('## Verdict','## Findings','## Next steps','42/59','0/110','339,249.95'):assert word in t
resources=[read(p) for p in (H/'audit').glob('v4*.resource.json')]
assert max(r['timeout_s'] for r in resources)<1200
assert max(r['peak_MiB'] for r in resources)<1900
size=sum(p.stat().st_size for p in H.rglob('*') if p.is_file());assert size<3_000_000_000
out=dict(delivery_pass=True,review_scope='fourth R07 delivery L53',verdict=dict(strokes='42/59',connections='0/110',meal='fail',idle='fail',prep_min=None,cost_cny=339249.95,proceed='no',findings=10),local_saved_replays=3,connection_candidates_checked=38,connection_scene_states=12071,fold_directions_checked=22,fold_states=5588,internal_paths_replayed=41,internal_states=2564,rebased_downstream_states=59,post_sha256=digest(post),post_bytes=post.stat().st_size,reviewer_directory_bytes=size,reference_copies_unchanged=len(unchanged),missing_links=missing,script_hashes=code,result_hashes=parsed,resource_records=resources,maximum_observed_worker_MiB=max(r['peak_MiB'] for r in resources),maximum_successful_elapsed_s=max(r['elapsed_s'] for r in resources if r['exit_code']==0),maximum_concurrent_numerical_workers=3,cpu_only=True,physical_tests=False,purchases=False,supplier_contact=False,upstream_modified=False,limitations=['Only three saved local connection paths exist; other connection checks are bounded rejection diagnostics. No saved complete meal or complete fold path exists.','Finite searches do not prove architectural impossibility.','Scores retain the archived arm model/ranges; newer OEM specification differences remain unresolved.'])
(O/'delivery.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:out[k] for k in ('delivery_pass','verdict','reviewer_directory_bytes','maximum_observed_worker_MiB','maximum_successful_elapsed_s')}))
