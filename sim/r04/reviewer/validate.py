"""Final read-only input integrity and reviewer deliverable verification."""
from pathlib import Path
import ast,json,hashlib,re,collections
H=Path(__file__).resolve().parent;ROOT=H.parents[2];I=H.parent/'integrator';A=H/'audit';O=H/'results';POST=ROOT/'posts/r04/reviewer.md'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(n,v):(O/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
before=read(A/'input_hashes.json');changed=[];missing=[]
for name,value in before.items():
 p=ROOT/name
 if not p.is_file():missing.append(name)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=value:changed.append(name)
parsed=[];errors=[]
for directory in [H,I]:
 for p in directory.glob('*.py'):
  try:ast.parse(p.read_text(encoding='utf-8-sig'));parsed.append(str(p.relative_to(ROOT)))
  except Exception as e:errors.append(dict(file=str(p),error=str(e)))
post=POST.read_text(encoding='utf-8');bad_links=[];local_links=[]
for target in re.findall(r'\]\(([^\n)]+)\)',post):
 if '://' in target:continue
 dest=target.split('#',1)[0];p=(POST.parent/dest).resolve()
 local_links.append(target)
 if not p.exists() and p!=O/'delivery_audit.json':bad_links.append(target)
findings=re.findall(r'^([0-9]+)\. \*\*(BLOCKING|HIGH|MEDIUM|LOW|INFORMATIONAL)',post,re.M)
resources=[read(p) for p in A.glob('*.resource.json')]
replay=read(O/'reverify_all.json');motion=read(O/'motion_independent.json');geometry=read(O/'geometry_independent.json');passing=read(O/'passing_complete_independent.json');wall=read(O/'wall_policy_probe.json');cost=read(A/'schedule_cost_audit.json')
state=read(I/'results/state_sequence.json');persistent=read(I/'results/persistent_model.json')
state_inventory=dict(keys=list(state),counts={k:len(v) for k,v in state.items() if isinstance(v,list)},unverified_required_events=state['unverified_required_events'],mass_input_kg=state['mass_input_kg'],mass_loss_measured_kg=state['mass_loss_measured_kg'],ownership_invariant=state['ownership_invariant'],persistent_keys=list(persistent),persistent_ownership_pass=persistent['ownership_pass'],persistent_executable=persistent['executable'])
summary=dict(schema='r04.reviewer.verdict.v1',phases_passed=replay['logical_passed'],phases_total=replay['logical_total'],phase_score_scope='Unchanged-reference STATIC count; broader inherited whole-wall name exclusion is BLOCKING under the binding contact rule.',instances_passed=replay['instances_passed'],strokes_passed=replay['strokes_passed'],poses=replay['poses_total'],connections_passed=motion['connections_passed'],connections_total=motion['connections_total'],connections_independently_replayed=motion['connections_replayed'],motion='fail',empty_passing_reference_policy=passing['pass_'],all_doors_open=geometry['all_doors_open_pass'],rule_fidelity='BLOCKED',wall_policy_name_exclusion_pairs=len(wall['rows']),best_static_candidate_cny=cost['totals']['best_candidate']['total'],lowest_unqualified_candidate_cny=cost['totals']['jaka_zu7_wall_household_candidate']['total'],cheapest_cny=None,prep_min_planning=cost['makespan_s']/60,prep_min_verified=None,proceed=False,findings=len(findings),severity_counts=dict(collections.Counter(v for _,v in findings)))
dump('review_summary.json',summary)
out=dict(input_hashes_checked=len(before),upstream_and_binding_files_unchanged=not changed and not missing,changed=changed,missing=missing,AST_parsed=parsed,parse_errors=errors,post_path=str(POST.relative_to(ROOT)),post_starts_with_chinese_summary=post.startswith('中文摘要'),findings=findings,local_links_checked=len(local_links),broken_local_links=bad_links,resources=resources,max_recorded_worker_MiB=max(x['peak_MiB'] for x in resources),max_recorded_worker_elapsed_s=max(x['elapsed_s'] for x in resources),all_recorded_timeouts_below_20min=all(x['timeout_s']<1200 for x in resources),all_recorded_workers_below_1900MiB=all(x['peak_MiB']<1900 for x in resources),reviewer_output_bytes=sum(p.stat().st_size for p in H.rglob('*') if p.is_file()),r04_total_bytes=sum(p.stat().st_size for p in H.parent.rglob('*') if p.is_file()),concurrency='At most two reviewer numerical workers overlapped; CPU only; process-tree cap1900MiB; foreground bounded runs',post_sha256=hashlib.sha256(POST.read_bytes()).hexdigest(),state_inventory=state_inventory,verdict=summary,no_purchasing_or_supplier_contact=True)
dump('delivery_audit.json',out)
assert not changed and not missing and not errors and not bad_links
assert len(findings)==12 and [int(n) for n,_ in findings]==list(range(1,13)) and post.startswith('中文摘要')
assert replay['logical_passed']==27 and motion['connections_replayed']>=10 and motion['connections_total']==104 and not geometry['all_doors_open_pass']
assert out['r04_total_bytes']<3*1024**3 and out['all_recorded_timeouts_below_20min'] and out['all_recorded_workers_below_1900MiB']
print(json.dumps(dict(hashes=len(before),changed=changed,broken_links=bad_links,findings=len(findings),peak_MiB=out['max_recorded_worker_MiB'],r04_GiB=out['r04_total_bytes']/1024**3,verdict=summary),ensure_ascii=False))
