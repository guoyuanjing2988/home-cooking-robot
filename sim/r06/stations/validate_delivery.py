"""Focused final artifact consistency checks, no new mechanical acceptance."""
import csv,hashlib,json,re
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RESULTS=HERE/'results'
post=ROOT/'posts/r06/stations.md'
checks=[]
def check(name,condition):
    assert condition,name
    checks.append(name)
for name in ['survey.csv','stations.json','concepts.json','events_A.json','events_B.json','state_ledger_A.json','state_ledger_B.json','food_catalog.json']:
    check('required '+name,(RESULTS/name).is_file() and (RESULTS/name).stat().st_size>0)
text=post.read_text(encoding='utf-8')
check('post begins Chinese',any('\u4e00'<=ch<='\u9fff' for ch in text[:30]))
for label,target in re.findall(r'\[([^\]]*)\]\(([^)]+)\)',text):
    if target.startswith(('https:','http:')):continue
    check('local post link '+target,(post.parent/target).resolve().is_file())
survey=list(csv.DictReader((RESULTS/'survey.csv').open(encoding='utf-8-sig',newline='')))
check('28 complete survey rows',len(survey)==28 and all(r['dimensions_mm'] and r['loading_geometry'] and r['power_W'] and r['cleanability'] and r['weak_evidence'] and r['urls'] for r in survey))
spec=json.loads((RESULTS/'stations.json').read_text(encoding='utf-8'))
concepts=json.loads((RESULTS/'concepts.json').read_text(encoding='utf-8'))
a,b=concepts['concepts']
check('recommended summary',concepts['recommendation']=='cassette_fixed' and a['arms']==1 and a['event_count']==79 and a['estimated_minutes']==45 and a['estimated_cny']==268985)
check('B summary',b['event_count']==93 and b['estimated_minutes']==56 and b['estimated_cny']==294285)
check('mount transforms agree',a['arm_mount']['position_m']==spec['robot']['mount_world']['position_m'])
check('closed initial pan lids',all(next(x for x in spec['bodies'] if x['id']=='lid_'+p)['joint']['initial']==0 for p in spec['products']))
check('opening reserves correct',all(x['reserve_mm'] is None or abs(x['minimum_nominal_gap_mm']-x['gate_mm']-x['reserve_mm'])<1e-9 for x in spec['clearance_reserves']))
for concept in [a,b]:
    check('time '+concept['id'],sum(x['estimated_s'] for x in concept['events'])==concept['estimated_timing']['resource_scheduled_nominal_seconds'])
    check('price '+concept['id'],round(sum(x['line_cny'] for x in concept['bom'])*1.15)==concept['estimated_cny'])
check('one owned object per food token',all('owner' in food for name in ['A','B'] for s in json.loads((RESULTS/f'state_ledger_{name}.json').read_text(encoding='utf-8')) for food in s['food'].values()))
check('local OEM model exists',(ROOT/spec['robot']['OEM_model_ref']).is_file())
for name in ['cassette_fixed_plan.png','cassette_fixed_elevation.png','appliance_hybrid_plan.png']:
    with Image.open(HERE/'plans'/name) as im:check('plan size '+name,max(im.size)<=1600)
audit=json.loads((HERE/'audit/validation.json').read_text(encoding='utf-8'))
for rel,digest in audit['input_sha256'].items():
    check('earlier input unchanged '+rel,hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest)
check('zero accepted paths',spec['full_scene_checks']['accepted_paths']==0 and spec['status']['motion']=='not_simulated')
check('explicit expanded-count qualification',concepts['common']['expanded_named_substeps_minimum']=={'cassette_fixed':216,'appliance_hybrid':223} and 'atomic' in concepts['common']['expanded_count_limit'])
size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())+post.stat().st_size
check('total output under3GB',size<3_000_000_000)
(HERE/'audit/delivery.json').write_text(json.dumps(dict(checks=checks,passed=len(checks),role_plus_post_bytes=size,scope='Delivery/consistency only;no motion,quality or safety acceptance'),indent=2),encoding='utf-8')
print(json.dumps(dict(delivery_checks=len(checks),total_bytes=size,estimated_min=45,estimated_cny=268985,accepted_paths=0)))
