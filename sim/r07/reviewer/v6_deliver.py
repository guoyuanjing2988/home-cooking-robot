from pathlib import Path
import json,hashlib,ast,re,time
H=Path(__file__).resolve().parent;O=H/'results_v6';R=H.parents[2];I=H.parent/'integrator';post=R/'posts/r07/reviewer.md'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
s=load(O/'summary.json');template=(H/'report_v6_template.md').read_text(encoding='utf-8-sig')
foldtext=(f"The reviewer replayed **{s['fold_saved_edges']}/{s['fold_saved_edges']} saved successful edge prefixes in both directions**, "
 f"covering **{s['fold_saved_edge_states']:,} states**, and reproduced **{s['fold_rejections_reproduced']}/{s['fold_saved_rejections']} saved rejection states** "
 f"across **{s['fold_attempts']} distinct fold/return/unfold attempts**. These are prefixes of rejected complete routes. "
 f"Additional direct, jaw-opening and staging diagnostics cover **{s['fold_directions']} directions / {s['fold_states']:,} states**, with **zero complete passes** "
 f"and a maximum independent point step of **{s['fold_maxstep']:.6f} mm**. "
 "The initial raw-food unfolding model and prospective completed-food folding/return models are kept separate and hash matched. "
 "No open-sweep obstacles are used during these motions. No failed randomized search is treated as proof of architectural impossibility. "
 "[Saved-edge/rejection audit](../../sim/r07/reviewer/results_v6/fold_saved_edges.json), "
 "[directional diagnostics](../../sim/r07/reviewer/results_v6/fold.json), "
 "[initial-scene deployment](../../sim/r07/reviewer/results_v6/unfold_initial.json).")
resource_note=('The optional extended direct/staging fold-diagnostic sweep reached its 900 s supervisor limit; its worker tree was terminated and completed attempt checkpoints retained. '
 'No partial route was accepted. The separate audit of all saved fold prefixes and rejection states completed independently. '
 'The initial connection geometry audit used gravity-only independent load arithmetic; its separate complete inertial-load replay includes all six signed acceleration alternatives. '
 'The inherited idle-method description was corrected to describe the snapshot-only sweep scope; numerical values were unchanged.')
for a,b in {'connection_states':f"{s['connection_states']:,}",'connection_maxstep':f"{s['connection_maxstep']:.6f}",'fold_evidence':foldtext,'resource_note':resource_note}.items():template=template.replace('{{'+a+'}}',b)
assert '{{' not in template
post.write_text(template,encoding='utf-8')
# Validate delivered evidence and links after writing the review.
assert template.startswith('中文摘要：')
assert s['strokes_pass']==47 and s['strokes_total']==59
assert s['internal_replayed']>=8 and s['internal_pass']==s['internal_replayed']
assert s['connection_attempts_replayed']==110 and s['saved_pass']==s['saved_legs']==s['source_saved_legs']==30
assert s['inertial_load_pass']==s['inertial_load_legs']==30
assert s['fold_saved_edges']==s['fold_saved_edges_pass'] and s['fold_rejections_reproduced']==s['fold_saved_rejections']
assert s['fold_saved_edges']==13 and s['fold_saved_rejections']==51
assert load(O/'fold_ranges.json')['all_pass']
assert all(r['max_point_step_mm']<=4 for r in load(O/'fold_saved_edges.json')['saved_edges'])
assert max(s['internal_maxstep'],s['connection_maxstep'],s['fold_maxstep'])<=4
assert s['meal_mass_ownership'] and s['meal_FK'] and s['meal_prefix']==0
assert load(O/'door_scope.json')['all_corrected_scope'] and load(O/'meal.json')['all_probes_pass']
assert load(O/'metadata.json')['integrator_worker_peak_reconstructed']<=4
findings=re.findall(r'^\d+\. \*\*(?:BLOCKING|HIGH|MEDIUM)',template.split('## Findings')[1].split('## Next steps')[0],re.M);assert len(findings)==11
missing=[];links=[]
for link in re.findall(r'\]\(([^)]+)\)',template):
 if link.startswith(('http://','https://')):continue
 p=Path(link) if re.match(r'^[A-Za-z]:/',link) else post.parent/link
 if p.resolve()==(O/'delivery.json').resolve():continue
 if not p.exists():missing.append(link)
 links.append(link)
assert not missing,missing
scripts=[]
for p in H.glob('v6_*.py'):ast.parse(p.read_text(encoding='utf-8-sig'));scripts.append(p.name)
parsed=[]
for p in O.rglob('*.json'):
 if p.name=='delivery.json':continue
 load(p);parsed.append(str(p.relative_to(O)))
resources=[]
for p in (H/'audit').glob('v6_*.resource.json'):
 row=load(p);resources.append(dict(file=str(p.relative_to(R)),**row))
assert all(x['timeout_s']<1200 and x['peak_MiB']<=1900 for x in resources)
metadata=load(O/'metadata.json');source_matches=[]
for row in metadata['source_hashes']:
 p=R/row['file'];source_matches.append(dict(file=row['file'],unchanged=hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']))
assert all(x['unchanged'] for x in source_matches)
size=sum(p.stat().st_size for p in O.rglob('*') if p.is_file())+sum(p.stat().st_size for p in H.glob('v6_*.py'))+sum(p.stat().st_size for p in (H/'audit_v6').rglob('*') if p.is_file())+post.stat().st_size
assert size<3_000_000_000
verdict='DONE r07_reviewer strokes=47/59 connections=0/110 meal=fail idle=fail prep_min=null cost_cny=343734.95 proceed=no findings=11'
delivery=dict(artifact_checks_pass=True,task_acceptance_pass=False,scripts=len(scripts),json_files=len(parsed),local_links=len(links),missing_links=missing,findings=len(findings),new_output_bytes=size,whole_reviewer_tree_bytes=sum(p.stat().st_size for p in H.rglob('*') if p.is_file()),resources=resources,peak_logged_MiB=max(x['peak_MiB'] for x in resources),reviewer_max_numerical_workers=4,fold_diagnostic_timeout=dict(limit_s=900,status='supervisor terminated worker tree; optional proposal diagnostics incomplete; no acceptance credit',log='sim/r07/reviewer/audit/v6_fold.log',resource_record_note='Legacy supervisor raises before writing resource JSON on timeout; exception is retained in tool transcript. Peak not independently recorded after abort; live1900MiB monitor was active.'),source_unchanged=source_matches,post_sha256=hashlib.sha256(post.read_bytes()).hexdigest(),no_upstream_writes=True,no_purchases=True,no_supplier_contact=True,no_physical_tests=True,verdict=verdict)
(O/'delivery.json').write_text(json.dumps(delivery,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in delivery.items() if k not in ('resources','source_unchanged')},indent=2))
