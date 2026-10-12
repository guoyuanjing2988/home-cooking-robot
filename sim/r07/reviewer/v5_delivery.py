from pathlib import Path
import json,hashlib,ast,re
H=Path(__file__).resolve().parent;O=H/'results_v5';root=H.parents[2];I=H.parent/'integrator';post=root/'posts/r07/reviewer.md'
resources=[]
for p in (H/'audit').glob('v5_*.resource.json'):
 r=json.loads(p.read_text());resources.append(dict(file=str(p.relative_to(root)),**r))
parsed=[]
for p in O.rglob('*.json'):
 if p.name=='delivery.json':continue
 json.loads(p.read_text());parsed.append(str(p.relative_to(root)))
scripts=[]
for p in H.glob('*v5*.py'):ast.parse(p.read_text(encoding='utf-8-sig'));scripts.append(str(p.relative_to(root)))
text=post.read_text();links=[];missing=[]
for link in re.findall(r'\]\(([^)]+)\)',text):
 if link.startswith(('https://','http://')):continue
 p=Path(link) if re.match(r'^[A-Za-z]:/',link) else post.parent/link
 if p.name=='delivery.json':continue
 links.append(link)
 if not p.exists():missing.append(link)
summary=json.loads((O/'summary.json').read_text());motion=json.loads((O/'connections.json').read_text());fold=json.loads((O/'fold.json').read_text());idle=json.loads((I/'results/idle.json').read_text())
assert summary['strokes_pass']==47 and summary['strokes_total']==59
assert summary['internal_replayed']>=8 and summary['internal_pass']==summary['internal_replayed']
assert summary['connection_attempts_replayed']==110 and summary['saved_legs']==19 and summary['saved_pass']==19
assert len(fold['routes'])==2*sum(len(idle[k]['attempts']) for k in ('task_fold','meal_end_return_diagnostic'))
assert not missing,missing
assert all(r['max_point_step_mm']<=4+1e-8 for r in fold['routes'])
assert summary['connection_maxstep']<=4 and summary['internal_maxstep']<=4
finding_text=text.split('## Findings')[1].split('## Next steps')[0];findings=re.findall(r'^\d+\. \*\*(?:BLOCKING|HIGH|MEDIUM)',finding_text,re.M)
assert len(findings)==11
assert text.startswith('中文摘要：')
inputfiles=[root/'DECISIONS.md',I/'reference.py',I/'runtime_v5_r07.py',I/'persistent_v5_r07.py',I/'binding_v5_r07.py',I/'results/motion.json',I/'results/idle.json',I/'results/state_sequence.json',root/'posts/r07/integrator.md']
input_hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputfiles}
v5bytes=sum(p.stat().st_size for p in O.rglob('*') if p.is_file())+sum(p.stat().st_size for p in H.glob('*v5*.py'))+sum(p.stat().st_size for p in (H/'audit_v5').rglob('*') if p.is_file())+post.stat().st_size
reviewerbytes=sum(p.stat().st_size for p in H.rglob('*') if p.is_file())
assert v5bytes<3_000_000_000
result=dict(artifact_checks_pass=True,json_files=len(parsed),scripts=len(scripts),local_links=len(links),missing_links=missing,findings=11,independent_internal_paths=summary['internal_replayed'],connection_attempts=110,saved_connection_legs=19,fold_directional_replays=len(fold['routes']),v5_output_bytes=v5bytes,whole_reviewer_tree_bytes=reviewerbytes,max_resource_MiB=max(r['peak_MiB'] for r in resources),longest_successful_chunk_s=max(r['elapsed_s'] for r in resources if r['exit_code']==0),resources=resources,input_hashes=input_hashes,post_sha256=hashlib.sha256(post.read_bytes()).hexdigest(),upstream_edited=False,physical_tests=False,purchasing=False,supplier_contact=False,reviewer_max_concurrent_numerical_workers=3,resource_scope='Numerical workers exclude foreground supervisor/venv launchers; at most three numerical jobs. All runs use timeout and1900MiB tree ceiling.',verdict='DONE r07_reviewer strokes=47/59 connections=0/110 meal=fail idle=fail prep_min=null cost_cny=343734.95 proceed=no findings=11')
(O/'delivery.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ('resources','input_hashes')},indent=2))
