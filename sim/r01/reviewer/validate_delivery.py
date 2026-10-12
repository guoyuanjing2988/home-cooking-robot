"""Final bounded reviewer delivery validation, without re-running simulations."""
import json,hashlib,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];POST=ROOT/'posts/r01/reviewer.md'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
hashes=read(HERE/'audit/input_artifact_hashes.json')
unchanged={}
for path,digest in hashes.items():
    if path.startswith('inputs/') or path.startswith('inputs\\'):
        actual=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        assert actual==digest,path
        unchanged[path]=actual
report=POST.read_text(encoding='utf-8')
assert report.startswith('本轮审查结论')
findings=re.findall(r'^\d+\. \*\*(BLOCKING|HIGH|MEDIUM)',report,flags=re.M)
assert len(findings)==12 and findings.count('BLOCKING')==3
resources={}
for p in (HERE/'audit').glob('*.resource.json'):
    if p.name=='validate_delivery.resource.json':continue # wrapper writes this run's final record after exit
    r=read(p);assert r['exit_code']==0 and r['timeout_s']<1200 and r['peak_MiB']<1900
    resources[p.name]=r
comparisons={}
for pid in ['P01','P02','P06','P13','P14']:
    r=read(HERE/'reruns'/f'{pid}.json');a=read(HERE/'reruns'/f'{pid}.comparison.json')
    assert r['seeds']==96 and len(r['rows'])==96
    assert all(v.get('equal',True) for v in a.values() if isinstance(v,dict))
    assert a['nominal_ratio_abs_difference']==0
    comparisons[pid]=dict(seeds=96,feasible_seeds=r['feasible_seeds'],blocker_counts=r['blocker_counts'],ratio=r['best_nominal']['torque']['ratio'])
g=read(HERE/'results/golden/xArm6x2.json');prior=read(HERE.parent/'concept/results/golden/xArm6x2.json')
for key in ['seeds','ik_seeds','collision_free_seeds','rated_admission_by_force','rows']:
    assert g[key]==prior[key],key
replay=read(HERE/'audit/witness_replay.json');assert replay['forbidden_hits']==[] and replay['nominal_ratio_max_recompute_error']==0
limits=read(HERE/'audit/datasheet_limit_audit.json');assert limits['max_frozen_drift_rad_or_m']==0
cost=read(HERE/'audit/cost_reconciliation.json');assert cost['totals']['2']['installed_estimate_cny']==488175 and cost['totals']['3']['installed_estimate_cny']==625025
links=[]
for target in re.findall(r'!?\[[^\]]+\]\(([^)]+)\)',report):
    if target.startswith(('https:','http:')):continue
    p=Path(target) if re.match(r'^[A-Za-z]:/',target) else (POST.parent/target).resolve()
    assert p.exists() or p==HERE/'audit/delivery.json',target # this validated manifest is written below
    if 'SKILL.md' not in target:assert p.is_relative_to(ROOT),target
    links.append(target)
output_bytes=POST.stat().st_size+sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
assert output_bytes<2_000_000_000
result=dict(status='REVIEW_COMPLETE_WITH_BLOCKERS',best='xArm6x2',conditional_phases=10,binding_verified_phases=0,
    cost_cny=488175,proceed=False,findings=12,blocking_findings=3,input_hashes=unchanged,resources=resources,
    comparisons=comparisons,golden=dict(seeds=96,ik=16,collision_free=1,conditional_counts=g['rated_admission_by_force'],raw_rows_identical=True),
    replay=replay,local_links=links,output_bytes=output_bytes,report_sha256=hashlib.sha256(POST.read_bytes()).hexdigest(),
    final_reply='DONE r01_reviewer best=xArm6x2 phases=0/16 cost_cny=488175 proceed=no findings=12')
(HERE/'audit/delivery.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','best','conditional_phases','binding_verified_phases','cost_cny','findings','output_bytes','comparisons']},indent=2))
