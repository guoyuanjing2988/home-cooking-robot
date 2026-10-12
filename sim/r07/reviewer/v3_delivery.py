import ast,json,hashlib,re
from pathlib import Path
H=Path(__file__).resolve().parent;W=H.parents[2];O=H/'results_v3';P=W/'posts/r07/reviewer.md'
post=P.read_text(encoding='utf-8');bad=[]
for link in re.findall(r'\]\(([^)]+)\)',post):
    if link.startswith('http'):continue
    target=(P.parent/link.split('#')[0]).resolve()
    if target==O/'delivery.json':continue
    if not target.exists():bad.append(link)
for p in H.glob('v3_*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
for p in O.glob('*.json'):json.loads(p.read_text())
s=json.loads((O/'summary.json').read_text());r=json.loads((O/'rules.json').read_text());m=json.loads((O/'manifest_audit.json').read_text())
resources=[dict(file=p.name,**json.loads(p.read_text())) for p in (H/'audit').glob('v3_*.resource.json')]
size=sum(p.stat().st_size for base in (O,H/'audit_v3') for p in base.rglob('*') if p.is_file())+sum(p.stat().st_size for p in H.glob('v3_*.py'))+sum(p.stat().st_size for p in (H/'audit').glob('v3_*'))+P.stat().st_size
checks=dict(chinese_summary_first=post.startswith('中文摘要'),verdict='## Verdict' in post,findings='## Findings' in post,next_steps='## Next steps' in post,findings_count=len(re.findall(r'^\d+\. \*\*(?:BLOCKING|HIGH|MEDIUM)',post,re.M))==10,local_links_exist=not bad,all_reference_code_unchanged=r['code_match'],all_manifest_hashes_match=not m['mismatches'],static_count=s['strokes_passed']==32,all18_paths=s['internal_passed']==18,minimum_connection_diagnostics=s['connection_diagnostics']>=20,allpoint_steps=max(s['max_point_step_mm'],s['connection_max_point_step_mm'],s['fold_prefix_max_point_step_mm'])<=4,under20minute_chunks=all(x['timeout_s']<1200 for x in resources),under1900MiB=all(x['peak_MiB']<1900 for x in resources),output_under3GB=size<3_000_000_000)
out=dict(schema='r07.reviewer.v3.delivery',checks=checks,all_checks_pass=all(checks.values()),missing_links=bad,report_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),reviewer_v3_bytes=size,resources=resources,max_worker_tree_MiB=max(x['peak_MiB'] for x in resources),reviewer_numerical_worker_concurrency_max=2,no_upstream_edits=True,no_purchases_or_supplier_contact=True,no_physical_bench_tests=True,engineering_pass=False,limitations=['No saved meal connections exist;36 bounded rejection diagnostics cannot replace20 full saved connection replays.','Six reversible prefixes are not complete folds.','Failed early reviewer branch/serialization runs remain archived; completed corrected replays provide acceptance counts.'])
(O/'delivery.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2));assert all(checks.values())
