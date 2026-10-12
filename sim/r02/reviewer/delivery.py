"""Delivery integrity: source hashes, links, reruns, force/cost arithmetic, resources."""
import ast,hashlib,json,re,math
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2];A=H/'audit'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 report=ROOT/'posts/r02/reviewer.md';txt=report.read_text(encoding='utf-8')
 findings=re.findall(r'^([0-9]+)\. \*\*(BLOCKING|HIGH|MEDIUM|INFORMATIONAL)',txt,re.M)
 assert [int(x[0]) for x in findings]==list(range(1,14))
 assert len([x for x in findings if x[1]=='BLOCKING'])==3
 assert '\u4e00'<=txt[0]<='\u9fff'
 for label in ('## Verdict','## Findings','## Next steps'):assert label in txt
 links=[]
 for url in re.findall(r'\]\(([^\n]+?)\)',txt):
  if url.startswith(('http:','https:')):continue
  path=(report.parent/url).resolve();links.append(dict(url=url,exists=path.is_file() or path==(A/'delivery.json').resolve()))
 assert all(x['exists'] for x in links),[x for x in links if not x['exists']]
 immutable=read(A/'readonly_hashes.json')
 mismatches=[s for s,sha in immutable.items() if digest(ROOT/s)!=sha]
 inventory=read(A/'inventory.json')
 source_changes=[r['path'] for r in inventory if digest(ROOT/r['path'])!=r['sha256']]
 model_sources=read(ROOT/'sim/r02/concept2/audit/source_models.json')
 model_changes=[s for s,sha in model_sources.items() if digest(ROOT/s)!=sha]
 assert not mismatches and not source_changes and not model_changes
 rule=read(A/'rule_ast.json');assert rule['r01_r02_byte_identical']
 assert (A/'r01_to_r02.diff').stat().st_size==0
 reruns=[read(p) for p in sorted((H/'reruns').glob('*.comparison.json'))]
 assert len(reruns)>=5 and all(x['counts_equal'] for x in reruns)
 assert {'Q05.carrot','Q09.potato','Q16','Q22','Q24','Q27'}<={x['id'] for x in reruns}
 replay=read(A/'replay.json')
 assert replay['instances']==36 and replay['strokes']==77
 assert not any(replay[k] for k in ('invalid_admitted_pose_count','contact_record_mismatches','max_frozen_drift','max_torque_ratio_difference','max_grip_margin_difference'))
 forces=read(H/'results/force_arithmetic.json');assert len(forces)==17
 assert max(abs(x['difference_N']) for x in forces)<1e-3
 cost=read(H/'results/cost_reconciliation.json');assert round(cost['corrected_total'])==360640
 resources=[read(p) for p in sorted(A.glob('*.resource.json')) if p.name!='delivery.resource.json']
 assert all(r['exit_code']==0 and r['peak_MiB']<1900 and r['elapsed_s']<r['timeout_s']<1200 and r['cpu_only'] for r in resources)
 for p in H.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
 best=read(ROOT/'sim/r02/concept2/results/best.json');assert best['logical_phases_total']==27 and best['logical_phases_passed']==0
 details=[]
 for p in sorted((ROOT/'sim/r02/concept2/results/final_v4/c0684').glob('Q*.json')):
  r=read(p)
  details.append(dict(id=r['id'],strokes=len(r['parts']),poses_per_seed=sum(len(s['poses']) for s in r['definition']['segments']),elapsed_s=r['elapsed_s'],max_nominal_force_N=max(math.sqrt(sum(a*a for a in f)) for s in r['definition']['segments'] for hands in s['poses'] for h in hands.values() for f in h['nominal_forces_N']),max_saved_nominal_torque_ratio=max((row['nominal']['torque']['ratio'] for part in r['parts'] for row in part['rows'] if row['nominal']),default=0)))
 (A/'difficulty.json').write_text(json.dumps(details,indent=2),encoding='utf-8')
 out=dict(status='PASS',review_date='2026-10-08',report=str(report.relative_to(ROOT)),report_sha256=digest(report),findings=len(findings),blocking_findings=3,best='dual_fixed_lane_xArm6',phases_passed=0,phases_total=27,cost_cny=360640,proceed=False,reruns=[dict(id=x['id'],counts_equal=x['counts_equal']) for x in reruns],replay={k:replay[k] for k in ('instances','strokes','seed_strokes','saved_poses','replayed_endpoints')},immutable_source_count=len(immutable),submitted_files_verified=len(inventory),source_model_count=len(model_sources),changed_readonly_files=mismatches,changed_submitted_files=source_changes,changed_source_models=model_changes,local_links=len(links),missing_local_links=[],force_models_checked=17,distinct_literature_force_spotchecks=6,resource_records=len(resources),max_peak_MiB=max(r['peak_MiB'] for r in resources),max_run_s=max(r['elapsed_s'] for r in resources),max_concurrent_numerical_workers=2,cpu_only=True,output_bytes=sum(p.stat().st_size for p in H.rglob('*') if p.is_file())+report.stat().st_size)
 assert out['output_bytes']<2_000_000_000
 (A/'delivery.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 print(json.dumps(out))
 print('HARDEST_FORCE',sorted(details,key=lambda x:x['max_nominal_force_N'],reverse=True)[:5])
 print('HARDEST_SEED_POSES',sorted(details,key=lambda x:x['poses_per_seed'],reverse=True)[:5])
if __name__=='__main__':main()
