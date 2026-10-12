import json,re
from pathlib import Path
h=Path(__file__).resolve().parent;root=h.parents[2];post=root/'posts/r06/reviewer.md';text=post.read_text(encoding='utf-8');broken=[]
for target in re.findall(r'\]\(([^)]+)\)',text):
    if target.startswith(('http://','https://')):continue
    path=Path(target) if re.match(r'^[A-Za-z]:/',target) else post.parent/target
    if not path.exists():broken.append(target)
metrics=json.loads((h/'v2/metrics.json').read_text());coverage=json.loads((h/'v2/replay_coverage.json').read_text())
checks=dict(Chinese_first=text.startswith('中文摘要'),findings=len(re.findall(r'^\d+\. \*\*(?:INFORMATIONAL|BLOCKING|HIGH|MEDIUM)',text,re.M))==9,links_resolve=not broken,static_score=metrics['static_score']==[30,150],meal_connections=metrics['prefix_connections']==[10,240],at_least8_strokes=metrics['stroke_replays']==[8,8],at_least20_nonstationary_connections=coverage['nonstationary_trajectories']>=20,point_step=metrics['max_point_step_mm']<=4.00000001,upstream_unchanged=not metrics['upstream_files_changed'],conservation=json.loads((h/'v2/conservation.json').read_text())['pass_'],cost=metrics['cost_total_cny']==274850,prep_time_unknown=metrics['prep_min'] is None)
out=dict(pass_=all(checks.values()),checks=checks,broken_links=broken,coverage=coverage,post_bytes=post.stat().st_size,scope='Report integrity, not workstation acceptance')
(h/'v2/delivery.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out));assert out['pass_']
