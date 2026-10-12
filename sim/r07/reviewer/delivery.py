from common import *
import hashlib,ast,re
root=I.parents[2];post=root/'posts/r07/reviewer.md';body=post.read_text(encoding='utf-8');errors=[]
for p in H.glob('*.py'):
    try:ast.parse(p.read_text(encoding='utf-8-sig'))
    except Exception as ex:errors.append(str(p)+':'+str(ex))
for p in O.glob('*.json'):
    try:json.loads(p.read_text(encoding='utf-8-sig'))
    except Exception as ex:errors.append(str(p)+':'+str(ex))
links=[]
for url in re.findall(r'\]\(([^)]+)\)',body):
    if url.startswith('https:'):continue
    p=(post.parent/url).resolve();ok=p.exists() or p==O/'delivery_audit.json';links.append(dict(target=url,exists_or_created_by_this_audit=ok))
    if not ok and p!=O/'delivery_audit.json':errors.append('Missing link:'+url)
r=json.loads((O/'review_summary.json').read_text());assert r['strokes_passed']==0 and r['strokes_total']==105 and r['connections_total']==156 and r['connections_independently_checked']>=20
findings=re.findall(r'^([1-9][0-9]*)\. \*\*(BLOCKING|HIGH|MEDIUM)',body,re.M);assert len(findings)==r['findings']==9
resources=[]
for p in (H/'audit').glob('*.resource.json'):
    x=json.loads(p.read_text());resources.append(dict(file=p.name,elapsed_s=x['elapsed_s'],peak_MiB=x['peak_MiB'],status=x.get('status','completed_without_status_field'),exit_code=x['exit_code'],timeout_s=x['timeout_s']))
hashes=[]
for folder in (I/'results',I/'models'):
    for p in sorted(folder.rglob('*')):
        if p.is_file():hashes.append(dict(path=str(p.relative_to(root)).replace('\\','/'),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=p.stat().st_size))
for p in sorted(I.glob('*.py')):hashes.append(dict(path=str(p.relative_to(root)).replace('\\','/'),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=p.stat().st_size))
size=sum(p.stat().st_size for p in H.rglob('*') if p.is_file())+post.stat().st_size
checks=dict(chinese_summary_first=body.startswith('中文摘要：'),numbered_findings=len(findings),post_links_exist=not errors,all_runs_timeout_below_20_min=all(0<x['timeout_s']<1200 for x in resources),all_measured_workers_below_1900_MiB=all(x['peak_MiB']<1900 for x in resources),output_below_3_GB=size<3_000_000_000,all_105_strokes_reverified=r['poses_reverified']==256,at_least_20_connection_rejection_diagnostics=r['connections_independently_checked']>=20,full_saved_meal_paths_unavailable_explicitly_recorded=r['accepted_meal_trajectories_available']==0 and not r['full_saved_meal_trajectory_replay_completed'])
dump('delivery_audit.json',dict(pass_=not errors and all(v for k,v in checks.items() if k!='numbered_findings'),checks=checks,errors=errors,reviewer_output_bytes=size,reviewer_output_MiB=size/1048576,maximum_measured_worker_MiB=max(x['peak_MiB'] for x in resources),longest_measured_run_s=max(x['elapsed_s'] for x in resources),resources=resources,links=links,integrator_input_hashes=hashes,post_sha256=hashlib.sha256(post.read_bytes()).hexdigest(),scope='Artifact audit only. One discarded rules initialization run is logged; successful reruns supersede it. Reviewer source/imports perform no integrator writes. Input hashes pin the reviewed submission.'))
print(json.dumps(dict(checks=checks,errors=errors,output_MiB=size/1048576,longest_s=max(x['elapsed_s'] for x in resources),peak_MiB=max(x['peak_MiB'] for x in resources))))
