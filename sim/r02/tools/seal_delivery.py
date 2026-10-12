"""Ensure report targets exist and seal the reviewable exported artifacts."""
from pathlib import Path
import hashlib, json, re
R=Path(__file__).resolve().parent
W=R.parents[2]
post=W/'posts/r02/tools.md'
body=post.read_text(encoding='utf-8')
missing=[]
for target in re.findall(r'\]\(([^)]+)\)',body):
    if target.startswith('../../'):
        path=(post.parent/target).resolve()
        if path==R/'audit/delivery_manifest.json':continue
        if not path.exists():missing.append(target)
assert not missing,missing
assert body.startswith('建议') and all((R/x).exists() for x in ['results/process_v2.json','results/tools_bom.csv','cad/custom_parts.FCStd','cad/custom_parts.step','renders/layout_plan.png','renders/layout_perspective.png'])
files=[post]+[x for directory in ['results','research','cad/step'] for x in (R/directory).rglob('*') if x.is_file()]
files += [R/x for x in ['cad/custom_parts.FCStd','cad/custom_parts.step','cad/counter_layout.FCStd','cad/counter_layout.step','cad/cad_manifest.json','renders/layout_perspective.png','renders/layout_plan.png','renders/layout.blend','audit/delivery_validation.json','audit/step_roundtrip.json']]
rows={str(x.relative_to(W)).replace('\\','/'):dict(bytes=x.stat().st_size,sha256=hashlib.sha256(x.read_bytes()).hexdigest()) for x in sorted(set(files))}
out=dict(status='delivered_concept',logical_phases=27,expanded_instances=36,powered_appliances=1,custom_part_designs=18,bom_tools_cny=14149.96,files=rows,report_links='all local targets exist',qualification='IK, measured food trials, matched hardware and safety remain explicitly unvalidated')
(R/'audit/delivery_manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(files=len(rows),post_bytes=post.stat().st_size,local_links='pass',phases=27,powered_appliances=1,custom_parts=18,bom_cny=14149.96)))
