"""Seal reviewer evidence and check local report links; no upstream writes."""
import json,hashlib,re
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2];IN=H.parent/'integrator'
def read(n):return json.loads((H/'results'/n).read_text())
reg=read('submitted_regression.json');st=read('statics.json');paths=read('paths.json');eng=read('engineering.json');pr=read('negative_probes.json');supp=read('supplemental.json')
resources=[json.loads(p.read_text()) for p in (H/'audit').glob('*.resource.json')]
reference=ROOT/'sim/r05/integrator/reference.py';hash_reference=hashlib.sha256(reference.read_bytes()).hexdigest()
post=ROOT/'posts/r08/reviewer.md';body=post.read_text(encoding='utf-8');missing=[]
for target in re.findall(r'\]\(([^)]+)\)',body):
 if target.startswith(('http:','https:')):continue
 p=Path(target) if ':' in target[:3] else post.parent/target
 if p.name=='summary.json':continue
 if not p.exists():missing.append(str(p))
upstream=json.loads((IN/'results/delivery_audit.json').read_text());mismatch=[]
for name,digest in upstream['hashes'].items():
 p=IN/name
 if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()!=digest:mismatch.append(name)
summary=dict(carrot='fail',products_completed=0,products_total=4,strokes_passed=sum(r['static_ok'] for r in st['rows']),strokes_total=11,internal_paths_passed=0,connections_executed=0,connections_total=10,idle='fail',park_snapshot=eng['park_snapshot']['pass_'],prep_min=None,cost_cny=eng['cost']['total_cny'],proceed='no',findings=11,static_endpoints=22,all_static_verdicts_match=all(e.get('match',False) for r in st['rows'] for e in r['endpoints']),regression_pass=reg['pass_'],regression_geometry_cases=len(reg['r07_unchanged_inputs']),regression_capability_checks=len(reg['negative_probes']),independent_contact_probe_failures=[r['name'] for r in pr['contact'] if not r['pass_']],independent_transform_probe_failures=[r['name'] for r in pr['transform'] if not r['pass_']],forged_commit_accepted=pr['forged_commit']['accepted'],accepted_prefix_distinct_states=supp['accepted_prefix_distribution']['self']['states'],reference_sha256=hash_reference,upstream_delivered_source_hash_mismatches=mismatch,broken_local_report_links=missing,max_recorded_worker_tree_MiB=max(r['peak_MiB'] for r in resources),reviewer_bytes=sum(p.stat().st_size for p in H.rglob('*') if p.is_file()),interpretation='No end-to-end witness exists; partial paths, synthetic probes and prospective idle are not execution. Reference rejection retained despite diagnosed distance discrepancy.')
assert not missing,missing
assert summary['strokes_passed']==1 and summary['all_static_verdicts_match'] and summary['regression_pass']
assert hash_reference=='46e9002b222cf92970cfc5b30c10fbe23eed06470b8714fc946ffdd44d0f5681'
(H/'results/summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
