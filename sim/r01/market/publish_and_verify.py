"""Publish the requested post and verify the market handoff, within 60 seconds."""
from pathlib import Path
import csv,json,re,hashlib,time,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[2]
OUT=ROOT/'results'
POST=WORKSPACE/'posts'/'r01'/'market.md'
start=time.monotonic()
read=lambda name:json.loads((OUT/name).read_text(encoding='utf-8'))
sources=read('sources.json');costs=read('costs.json');arms=read('catalog.json')
text=(ROOT/'market_post_template.md').read_text(encoding='utf-8')
for tag,file in [('CATALOG_TABLE','catalog_table.md'),('COST_TABLE','cost_table.md'),('MOUNT_TABLE','mount_table.md'),('ALTERNATIVE_COST_TABLE','alternative_cost_table.md')]:
 text=text.replace('{{'+tag+'}}',(OUT/file).read_text(encoding='utf-8').strip())
text=text.replace('{{SOURCE_COUNT}}',str(len(sources)))
assert '{{' not in text
POST.parent.mkdir(parents=True,exist_ok=True)
POST.write_text(text,encoding='utf-8')

# Explicit cabinet and faucet primitives for the installation-obstacle handoff.
# This is a conservative proxy subset, not a full checker scene or IK witness.
scene=read('scene_assumptions.json')
xml=ET.Element('mujoco',model='market_installation_obstacle_proxies')
ET.SubElement(xml,'compiler',angle='degree')
ET.SubElement(xml,'option',gravity='0 0 -9.81')
world=ET.SubElement(xml,'worldbody')
def box(name,lo,hi,color):
 center=[(x+y)/2 for x,y in zip(lo,hi)];half=[(y-x)/2 for x,y in zip(lo,hi)]
 ET.SubElement(world,'geom',name=name,type='box',pos=' '.join(map(str,center)),size=' '.join(map(str,half)),rgba=color,contype='1',conaffinity='2')
cab=scene['upper_cabinets']
box('upper_cabinet_closed_proxy',[-1.8,0,1.35],[1.47,.37,2.15],'.65 .65 .65 1')
box('cabinet_door_full_sweep_proxy',[-1.8,.37,1.35],[1.47,.97,2.15],'.8 .5 .2 .25')
for i,p in enumerate(scene['faucet']['obstacle_primitives']):
 ET.SubElement(world,'geom',name='faucet_'+p['type']+'_proxy',type='cylinder',
  pos=' '.join(map(str,p['center'])),size=f"{p['radius']} {p['height']/2}",rgba='.3 .5 .7 .6',contype='1',conaffinity='2')
# Counter slabs are only visual/reference boxes; station models remain in inputs.
box('counter_left_reference',[-1.80,0,.81],[-.70,.60,.85],'.6 .45 .3 1')
box('counter_right_reference',[-.11,0,.81],[.69,.60,.85],'.6 .45 .3 1')
box('stove_protected_reference',[.69,0,.81],[1.47,.60,.85],'.7 .2 .2 1')
modeldir=ROOT/'models';modeldir.mkdir(exist_ok=True)
ET.indent(xml,space='  ')
ET.ElementTree(xml).write(modeldir/'installation_obstacles.xml',encoding='utf-8',xml_declaration=True)
(modeldir/'README.md').write_text('Cabinet/faucet obstacle proxy subset for the market installation handoff.\n\nAll placement/dimension assumptions are in ../results/scene_assumptions.json. The faucet placement is inferred, not the authoritative task water-outlet coordinate. The door box is a conservative full-sweep envelope. This file contains no arm, carriage or tool and is not a P01-P16 checker model. Do not claim clearance or feasibility from compiling it. Restore the original scene metadata and exact surveyed geometry in the real robot model.\n',encoding='utf-8')

rows=list(csv.DictReader((OUT/'catalog.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==len(arms)==15
assert len({r['arm_id'] for r in rows})==15
required={'dof','reach_mm','rated_payload_kg','arm_mass_kg','mounting_allowed','joint_brakes','spring_applied_brakes_verified','safety_certification','force_sensing','ip_rating','washdown_food_contact','controller_dimensions_mm','mains_and_power','public_china_price_cny','price_evidence_kind','model_url','model_commit','continuous_joint_output_torques_nm'}
assert required.issubset(rows[0])
for a in arms:
 assert len(a['model_commit'])==40 and re.fullmatch('[0-9a-f]{40}',a['model_commit'])
 assert not a['all_binding_requirements_verified'] and not a['torque_limit_usable']
 assert a['continuous_joint_output_torques_nm'] is None
 assert all(i in sources for i in a['spec_source_ids']+a['price_source_ids'])
for n in (2,3):
 total=costs['totals'][str(n)];subtotal=sum(i[f'{"two" if n==2 else "three"}_arm_cny'] for i in costs['items'])
 assert subtotal==total['subtotal_cny']
 assert round(subtotal*(1+total['contingency_rate']),2)==total['installed_estimate_cny']==costs[f'cost{n}_cny']
assert costs['cost2_cny']==464600 and costs['cost3_cny']==599150
assert costs['incremental_third_arm_cny']==134550
assert sum(t['budget_installed_cny'] for t in read('prep_tools.json'))==8000
for p in OUT.glob('*.json'):json.loads(p.read_text(encoding='utf-8'))
for p in OUT.glob('*.csv'):
 with p.open(encoding='utf-8-sig',newline='') as f:
  for row in csv.DictReader(f):assert None not in row, 'CSV column-count mismatch'
assert re.search('[\u4e00-\u9fff]',text[:100]) and text.index('English details follow.')>text.index('464,600')
missing=[]
for target in re.findall(r'\]\(([^)]+)\)',text):
 if target.startswith(('http://','https://')):continue
 resolved=(POST.parent/target).resolve()
 if resolved==(OUT/'handoff_validation.json').resolve():continue # This audit writes its own linked result below.
 if not resolved.is_file():missing.append(target)
assert not missing,missing
for a in read('model_sources.json')['models']:assert a['model_commit'] in text
baseline=read('supplement_manifest.json')['input_sha256']
now={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (WORKSPACE/'inputs').iterdir() if p.is_file()}
assert baseline==now
bytes_total=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())+POST.stat().st_size
assert bytes_total<2_000_000_000
assert time.monotonic()-start<60
ET.parse(modeldir/'installation_obstacles.xml')
compiled=read('obstacle_model_validation.json') if (OUT/'obstacle_model_validation.json').exists() else None
if compiled:
 assert compiled['compiled'] and compiled['mujoco_version']=='3.2.5'
 assert compiled['model_sha256']==hashlib.sha256((modeldir/'installation_obstacles.xml').read_bytes()).hexdigest()
validation=dict(date='2026-10-07',catalog_arm_count=len(rows),source_count=len(sources),required_outputs_present=True,
 post_path=str(POST.relative_to(WORKSPACE)),post_bytes=POST.stat().st_size,
 cost2_cny=costs['cost2_cny'],cost3_cny=costs['cost3_cny'],cost_arithmetic_verified=True,
 csv_json_parse_verified=True,local_post_links_verified=True,model_commits_match_post=True,
 input_sha256=now,input_hashes_unchanged_since_research_snapshot=True,output_bytes=bytes_total,output_under_2gb=True,
 obstacle_xml_parses=True,obstacle_compiled_mujoco_version=compiled['mujoco_version'] if compiled else None,
 obstacle_model_scope='Conservative cabinet/faucet proxy subset only;not a checker scene or clearance witness',
 all_binding_requirements_verified_count=0,checker_executed=False,ik_executed=False,
 no_purchase_or_supplier_contact=True,no_robot_v5_modifications=True,elapsed_s=round(time.monotonic()-start,4))
(OUT/'handoff_validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:validation[k] for k in ('catalog_arm_count','source_count','post_bytes','cost2_cny','cost3_cny','output_bytes','input_hashes_unchanged_since_research_snapshot')},indent=2))
