"""Workspace-only archival and delivery audit; engineering failure stays failure."""
import json,csv,hashlib,collections,xml.etree.ElementTree as E
from pathlib import Path
from PIL import Image
H=Path(__file__).resolve().parent;root=H.parents[2];O=H/'results'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
archive=H/'upstream/models';archive.mkdir(exist_ok=True)
for name in ('idle.xml','idle_before_transfer.xml','idle_r05.xml','idle_variant.xml','installed_cell.xml','passing.xml','passing_full.xml','witnesses'):
 src=(H/'models'/name).resolve();dst=(archive/name).resolve()
 # Verify both absolute move targets before any recursive directory move.
 assert src.is_relative_to(H.resolve()) and dst.is_relative_to(H.resolve())
 if src.exists():
  assert not dst.exists();src.rename(dst)
# Legacy metadata flag did not control R07 builds (r07_model removes it).
c=read(O/'config.json');c.pop('transport_only',None);write(O/'config.json',c)
summary=read(O/'phase_summary.json');summary['config']=c;write(O/'phase_summary.json',summary)
best=read(O/'best.json');best['config']=c;write(O/'best.json',best)
env=read(O/'torque_envelope.json');env['application_to_final_mount']=dict(config=c,change='Only helper base translated by -14.92464384mm in Y; same rotation, body gravity, rated payload and relative OEM self-collision geometry. Pure translation leaves every joint gravity moment and envelope unchanged.');write(O/'torque_envelope.json',env)
checks={};hashes=read(H/'audit/copied_code_hashes.json');changed=[]
for name,digest in hashes.items():
 for base in (H,H/'upstream',root/'sim/r05/integrator'):
  p=base/name
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(str(p))
checks['all_90_copied_and_original_python_files_unchanged']=not changed
assert not changed,changed
required=['phase_summary.json','motion.json','idle.json','schedule.json','costs.csv','clearance.json','iterations.csv']
checks['required_files_present']=all((O/n).exists() for n in required)
invalid=[]
for f in list(O.rglob('*.json'))+list((H/'audit').glob('*.json')):
 try:json.loads(f.read_text(encoding='utf-8-sig'),parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
 except Exception as e:invalid.append([str(f),str(e)])
checks['json_parses_without_nonfinite']=not invalid
P=read(O/'process_v3.json');old=read(O/'inherited_process_v3.json')
for name in ('force_models','finished_products','tools','acceptance'):checks[name+'_unchanged']=P[name]==old[name]
cs=[contact for p in P['phases'] for s in p['segments'] for pose in s['poses'] for h in pose.values() for contact in h.get('contacts',[])]
checks['every_contact_has_kind_and_object_support']=all(c.get('kind') in ('grasp_release_support','working_stroke') and c.get('object_id') and c.get('support_id')==c['face'] for c in cs)
checks['contact_policy_regression_pass']=read(O/'contact_policy_regression.json')['pass_']
motion=read(O/'motion.json');idle=read(O/'idle.json');schedule=read(O/'schedule.json')
checks['all_static_strokes_and_poses_enumerated']=summary['strokes_total']==105 and summary['poses_replayed']==256 and len(list((O/'final_static').glob('*.json')))==105
checks['all_connections_enumerated']=len(motion['connections'])==156
checks['all_event_paths_enumerated']=len(motion['event_paths'])==557
checks['no_failed_motion_claimed_executed']=not motion['meal_pass'] and motion['connections_passed']==0 and motion['event_paths_passed']==0 and schedule['prep_min'] is None
checks['idle_corrected_doors_not_corridor']=idle['doors_checked_against_corridor'] is False and not idle['pass_'] and len(idle['fold_paths'])==3
with (O/'costs.csv').open(newline='',encoding='utf-8') as f:cost=list(csv.DictReader(f))
base=sum(float(r['total_cny']) for r in cost if r['item'] not in ('TOTAL','One15percent project reserve'))
reserve=[r for r in cost if r['item']=='One15percent project reserve'];total=[r for r in cost if r['item']=='TOTAL']
checks['cost_one_reserve_one_safety_correct']=len(reserve)==len(total)==1 and sum('Inclusive home-safety' in r['item'] for r in cost)==1 and abs(float(reserve[0]['total_cny'])-round(base*.15,2))<.001 and abs(float(total[0]['total_cny'])-round(base*1.15,2))<.011
active_geometry=[]
for f in (H/'models').glob('*.xml'):
 if f.name.startswith(('xarm','jaka')):continue
 names=[g.get('name','') for g in E.parse(f).findall('.//geom')]
 assert not any(any(t in n for t in ('elevator','pallet','storage_recess','recess_header','front_post','portal')) for n in names),(f,names)
 active_geometry.append(dict(file=f.name,geoms=len(names),slicer_geoms=[n for n in names if n.startswith('slicer_')]))
checks['no_removed_r05_hardware_in_active_models']=True
resources=[dict(file=f.name,**read(f)) for f in (H/'audit').glob('*.resource.json')]
checks['bounded_cpu_resources']=all(r['timeout_s']<1200 and r['elapsed_s']<1200 and r['peak_MiB']<1900 and r['cpu_only'] for r in resources)
images=[]
for f in (H/'renders').glob('*.png'):
 with Image.open(f) as im:images.append(dict(file=f.name,size=list(im.size)))
checks['all_renders_max_1600px']=bool(images) and all(max(i['size'])<=1600 for i in images)
checks['all_requested_renders_and_24_frames']=all((H/'renders'/n).exists() for n in ('overview.png','parked_doors_open.png','under_cabinet_band.png','passing.png','executed_local_strip.png')) and len(list((H/'renders').glob('frame_*.png')))==24
bytes_n=sum(p.stat().st_size for p in H.rglob('*') if p.is_file())
checks['output_under_3GB']=bytes_n<3_000_000_000
post=root/'posts/r07/integrator.md';checks['post_exists_starts_chinese']=post.exists() and '本轮' in post.read_text(encoding='utf-8')[:100]
inputs={str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'DECISIONS.md',root/'posts/r05/integrator.md',root/'posts/r05/reviewer.md',root/'posts/r04/reviewer.md']}
output=dict(delivery_pass=all(checks.values()),engineering_pass=False,checks=checks,changed_upstream=changed,invalid_json=invalid,input_sha256=inputs,copied_python_count=len(hashes),active_geometry=active_geometry,resource_records=resources,max_elapsed_s=max(r['elapsed_s'] for r in resources),max_worker_tree_MiB=max(r['peak_MiB'] for r in resources),numerical_worker_concurrency_max=3,concurrency_basis='First static chunks deliberately used three bounded jobs. Subsequent jobs used at most three numerical workers; render controller runs one CPU Blender at a time. Launchers/monitors are not additional numerical workers.',output_bytes=bytes_n,images=images,limitations=['Full-meal planner execution coverage not achieved: missing accepted endpoints and persistent interface executor.','Delivery verification does not constitute a connected meal, folded populated idle, food quality or hardware qualification.'])
write(O/'delivery_audit.json',output)
print(json.dumps(dict(delivery_pass=output['delivery_pass'],failed_checks=[k for k,v in checks.items() if not v],MiB=bytes_n/1048576,max_elapsed_s=output['max_elapsed_s'],max_tree_MiB=output['max_worker_tree_MiB'])))
assert output['delivery_pass']
