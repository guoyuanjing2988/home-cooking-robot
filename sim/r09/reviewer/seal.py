"""Read and seal reviewer evidence; never writes producer artifacts."""
import ast,json,hashlib,re
from pathlib import Path
H=Path(__file__).resolve().parent;IN=H.parent/'integrator';ROOT=H.parents[2]
def read(n):return json.loads((H/'results'/n).read_text())
def save(n,v):(H/'results'/n).write_text(json.dumps(v,indent=2),encoding='utf-8')
inventory=[]
for p in sorted(IN.rglob('*')):
 if not p.is_file():continue
 b=p.read_bytes();parsed=None
 if p.suffix=='.py':ast.parse(b.decode('utf-8-sig'));parsed='Python AST'
 if p.suffix=='.json':json.loads(b.decode('utf-8-sig'));parsed='JSON'
 inventory.append(dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),parsed=parsed))
save('input_inventory.json',inventory)
rules=read('rules.json');probes=read('negative_probes.json');stat=read('statics.json');ad=read('admissions.json');eng=read('engineering.json');paths=read('paths.json')
assert rules['empty_source_diff'] and rules['arm_subtree_equal'] and rules['process_contract_equal']
assert all(x['match'] for x in rules['historical_regression'])
assert all(x['match'] for r in stat['rows'] for x in r['endpoints'])
assert ad['all_pass'] and len(ad['rows'])==397
assert len(probes['rows'])==26 and len(probes['failures'])==3
assert sum(r['all_pass'] for r in paths['locals'])==2
dense=[]
for f in ['path_6.json','path_7.json','idle_fold_prefix.json','idle_unfold_prefix.json']:
 r=read(f);assert r['all_pass'] and r['maximum_global_bound_m']<=.004
 dense.extend(r['rows'])
stages=[s for c in paths['connections'] for s in c['stages']]
assert len(stages)==30 and all(s['budget_s']>=60 and not s['ok'] for s in stages)
resources=[json.loads(p.read_text()) for p in (H/'audit').glob('*.resource.json')]
post=ROOT/'posts/r09/reviewer.md';body=post.read_text(encoding='utf-8');broken=[]
for link in re.findall(r'\]\(([^)]+)\)',body):
 if link.startswith('http'):continue
 target=Path(link) if re.match(r'^[A-Z]:',link) else post.parent/link
 if target.name=='summary.json':continue
 if not target.exists():broken.append(link)
assert not broken,broken
v=dict(carrot='fail',products_completed=0,products_total=4,strokes_pass=2,strokes_total=11,static_templates_pass=3,connections_pass=0,connections_total=10,idle='fail',parking_snapshot='conditional pass',minimum_tip_margin_mm=eng['stability']['minimum_any_horizontal_acceleration_mm'],submitted_discrete_tip_margin_mm=eng['stability']['minimum_mm'],prep_min=None,cost_cny=353165.00,proceed='no',findings=10,review=dict(reference_sha256=rules['reference_sha256'],reference_regression_pass=8,submitted_tests_pass=17,independent_probes=26,independent_probe_failures=[r['name'] for r in probes['failures']],static_endpoint_matches=22,admitted_records_rechecked=397,stability_records=398,dense_path_states=len(dense),dense_path_min_discrete_tip_mm=min(r['tip']['min_margin_m'] for r in dense)*1000,connection_stages_audited=len(stages),connection_stages_elapsed_s=sum(s['elapsed_s'] for s in stages),collision_rejections_reproduced=sum(s['rejected_state_reproduced'] is True for s in stages),max_process_tree_MiB=max(r['peak_MiB'] for r in resources),longest_run_s=max(r['elapsed_s'] for r in resources),output_bytes_before_seal=sum(p.stat().st_size for p in H.rglob('*') if p.is_file()),producer_files_inventoried=len(inventory),all_local_links_resolve=True),no_purchase=True,no_supplier_contact=True,no_physical_tests=True)
save('summary.json',v)
(H/'results/final_reply.txt').write_text('DONE r09_reviewer carrot=fail products=0/4 strokes=2/11 connections=0/10 idle=fail cost_cny=353165.00 proceed=no findings=10',encoding='utf-8')
print(json.dumps(v,indent=2))
