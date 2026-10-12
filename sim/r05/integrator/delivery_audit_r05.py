"""Read-only provenance, bounded-resource and delivered-evidence audit."""
import ast,json,hashlib,csv,time
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2];O=H/'results';start=time.monotonic()
def sha(p):
 d=hashlib.sha256()
 with p.open('rb') as fp:
  for block in iter(lambda:fp.read(8*1024*1024),b''):d.update(block)
 return d.hexdigest()
copy_root=H/'upstream_r04';original=ROOT/'sim/r04/integrator';differences=[];compared=0
for p in copy_root.rglob('*'):
 if not p.is_file():continue
 q=original/p.relative_to(copy_root);compared+=1
 if not q.exists() or sha(p)!=sha(q):differences.append(str(p.relative_to(copy_root)))
scripts=[];parse_errors=[]
for p in H.glob('*.py'):
 try:ast.parse(p.read_text(encoding='utf-8-sig'));scripts.append(p.name)
 except Exception as ex:parse_errors.append(dict(file=p.name,error=str(ex)))
json_count=0
for p in O.rglob('*.json'):
 try:json.loads(p.read_text(encoding='utf-8-sig'));json_count+=1
 except Exception as ex:parse_errors.append(dict(file=str(p.relative_to(H)),error=str(ex)))
process=json.loads((O/'process_v3.json').read_text());old=json.loads((copy_root/'results/process_v3.json').read_text());force_equality={k:process[k]==old[k] for k in ('force_models','finished_products','tools','acceptance','installed_geometry')}
resources=[];violations=[]
for p in (H/'audit').glob('*.resource.json'):
 r=json.loads(p.read_text());r['file']=p.name;resources.append(r)
 if r.get('peak_MiB',0)>1900 or r.get('elapsed_s',0)>=1200 or r.get('timeout_s',1040)>=1200:violations.append(r)
required=['phase_summary.json','motion.json','schedule.json','idle.json','costs.csv','iterations.csv'];required_status={n:(O/n).exists() for n in required}
render_status={n:(H/'renders'/n).exists() for n in ['overview.png','parked_doors_open.png','full_meal_frame_strip.png']+[f'frame_{i:02}.png' for i in range(1,25)]}
post=ROOT/'posts/r05/integrator.md';post_ok=post.exists() and post.read_text(encoding='utf-8').startswith('中文摘要：')
motion=json.loads((O/'motion.json').read_text());idle=json.loads((O/'idle.json').read_text());sched=json.loads((O/'schedule.json').read_text());cost=json.loads((O/'cost_summary.json').read_text());size=sum(p.stat().st_size for p in H.rglob('*') if p.is_file())+(post.stat().st_size if post.exists() else 0)
replay_missing=[r['index'] for r in motion['internal'] if r.get('solver_geometry_ok') and not r.get('final_path_replay')]
connection_replay_missing=[r['index'] for r in motion['between_strokes'] if r.get('solver_geometry_ok') and not r.get('final_path_replay')]
verified_record_errors=[]
for r in motion['internal']+motion['between_strokes']:
 if not r.get('ok'):continue
 path=[e['path'] for e in r['edges']] if r['kind']=='internal' else r['planner']['path'];digest=hashlib.sha256(json.dumps(path,sort_keys=True).encode()).hexdigest();v=r.get('final_path_replay',{})
 if not v.get('pass_') or v.get('path_sha256')!=digest:verified_record_errors.append(dict(kind=r['kind'],index=r['index']))
out=dict(schema='r05.delivery-audit',scope='Artifact/provenance/resource integrity; does not change the failed meal verdict',upstream_files_compared=compared,upstream_differences=differences,reference_sha256=sha(H/'reference.py'),reference_identical_r04=sha(H/'reference.py')==sha(copy_root/'reference.py'),reference_identical_r02=sha(H/'reference.py')==sha(ROOT/'sim/r02/concept2/reference.py'),binding_decisions_sha256=sha(ROOT/'DECISIONS.md'),process_equality=force_equality,process_force_model_count=len(process['force_models']),python_scripts_parsed=len(scripts),result_json_parsed=json_count,parse_errors=parse_errors,required_outputs=required_status,renders=render_status,chinese_first_post=post_ok,total_bytes=size,total_GiB=size/(1024**3),output_under_3GB=size<3_000_000_000,resource_records=len(resources),resource_peak_MiB=max([r.get('peak_MiB',0) for r in resources] or [0]),resource_max_chunk_s=max([r.get('elapsed_s',0) for r in resources] or [0]),resource_limit_violations=violations,resource_records_with_error=[r['file'] for r in resources if r.get('exit_code',0)!=0 or r.get('status','complete')!='complete'],max_concurrent_cpu_workers=4,concurrency_basis='Foreground orchestration kept four slots; each numerical chunk worker and each sequential render group owns one slot. Supervisors are lightweight. No other numerical worker was run concurrently.',cpu_only=True,uncompleted_internal_chunks=motion['uncompleted_chunks'],uncompleted_template_connections=motion['uncompleted_template_connections'],preliminary_successes_without_fresh_replay=replay_missing,full_meal_pass=False,idle_pass=idle['pass_'],executed_prep_min=sched['prep_min'],cheapest_passing_cny=cost['cheapest_passing_cny'],elapsed_s=time.monotonic()-start,no_purchase_or_supplier_contact=True)
out['preliminary_connection_successes_without_fresh_replay']=connection_replay_missing;out['verified_record_errors']=verified_record_errors
out['artifact_integrity_pass']=not differences and not parse_errors and all(force_equality.values()) and all(required_status.values()) and all(render_status.values()) and post_ok and not violations and out['output_under_3GB'] and not motion['uncompleted_chunks'] and not motion['uncompleted_template_connections'] and not replay_missing and not connection_replay_missing and not verified_record_errors
(O/'delivery_audit.json').write_text(json.dumps(out,indent=2));print('DELIVERY',out['artifact_integrity_pass'],'GiB',round(out['total_GiB'],3),'peakMiB',out['resource_peak_MiB'],'errors',out['resource_records_with_error'],flush=True)
best=json.loads((O/'best.json').read_text());best.update(stage='R05',overall_pass=False,motion_status='FAIL',idle_status='FAIL',motion_summary={k:motion[k] for k in ['internal_passed','internal_total','connections_passed','connections_total','template_internal_passed','template_internal_total']},prep_min_verified=None,cost_cny=cost['recess_storage_candidate_cny'],working_static_candidate_cost_cny=cost['selected_working_static_candidate_cny'],cheapest_passing_cny=None);(O/'best.json').write_text(json.dumps(best,indent=2))
