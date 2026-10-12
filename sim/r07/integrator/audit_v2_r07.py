"""Artifact/rule audit, explicitly separate from engineering and budget success."""
import json,csv,hashlib,xml.etree.ElementTree as E
from pathlib import Path
from PIL import Image
H=Path(__file__).resolve().parent;root=H.parents[2];O=H/'results'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
checks={};hashes=read(H/'audit/copied_code_hashes.json');changed=[]
for name,digest in hashes.items():
 for base in (H,H/'upstream',root/'sim/r05/integrator'):
  p=base/name
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(str(p))
checks['copied90_and_upstream_unchanged']=not changed
P=read(O/'process_v3.json');old=read(O/'inherited_process_v3.json')
for key in ('force_models','finished_products','tools','acceptance'):checks[key+'_unchanged']=P[key]==old[key]
contacts=[c for p in P['phases'] for sg in p['segments'] for pose in sg['poses'] for h in pose.values() for c in h.get('contacts',[])]
checks['explicit_contact_kinds_identities']=all(c.get('kind') in ('grasp_release_support','working_stroke') and c.get('object_id') and c.get('support_id')==c['face'] for c in contacts)
checks['nonworking_contact_regression']=read(O/'contact_policy_regression.json')['pass_']
required=['phase_summary.json','motion.json','idle.json','schedule.json','costs.csv','clearance.json','iterations.csv'];checks['required_outputs_present']=all((O/n).exists() for n in required)
s=read(O/'phase_summary.json');m=read(O/'motion.json');idle=read(O/'idle.json');t=read(O/'schedule.json');ID=s['selected_layout'];fresh=read(O/'fresh_admission.json')
checks['all105_strokes_256_poses_enumerated']=len(s['stroke_results'])==105 and s['required_poses']==256
checks['fresh_static_count_matches']=fresh['layout']==ID and fresh['strokes_passed']==s['strokes_passed'] and len(fresh['rows'])==105
checks['fresh_models_match_search_geometry']=all(r['same_compiled_geometry'] for r in fresh['rows'] if r['starts'])
checks['at_least6_complete_paired_maps']=s['complete_paired_layout_maps']>=6
checks['connections_events_all_enumerated']=len(m['connections'])==156 and len(m['event_paths'])==557
checks['no_fictitious_meal_time']=not m['meal_pass'] and t['prep_min'] is None
checks['corrected_idle_with_fold_attempts']=idle['doors_checked_against_corridor'] is False and len(idle['fold_paths'])==3
checks['v1_history_retained']=(root/'posts/r07/integrator_v1.md').exists() and (H/'history/v1/results/phase_summary.json').exists()
with (O/'costs.csv').open(newline='',encoding='utf-8') as file:rows=list(csv.DictReader(file))
base=sum(float(r['total_cny']) for r in rows if r['item'] not in ('TOTAL','One15percent project reserve'));reserve=[r for r in rows if r['item']=='One15percent project reserve'];total=[r for r in rows if r['item']=='TOTAL']
checks['one_reserve_one_safety_correct']=len(reserve)==len(total)==1 and sum('Inclusive home-safety' in r['item'] for r in rows)==1 and abs(float(reserve[0]['total_cny'])-round(base*.15,2))<.001 and abs(float(total[0]['total_cny'])-round(base*1.15,2))<.011
active=[H/idle['model_xml'],H/idle['doors_model_xml'],H/'models/persistent_meal.xml']+[H/'models'/f'{ID}_internal_{r["index"]}.xml' for r in m['internal_paths'] if r.get('ok')]
checks['no_elevator_pallet_portal_extension']=all(not any(any(k in g.get('name','') for k in ('elevator','pallet','storage_recess','recess_header','front_post','portal')) for g in E.parse(p).findall('.//geom')) for p in active)
images=[]
for path in (H/'renders').glob('*.png'):
 with Image.open(path) as im:images.append(dict(file=path.name,size=list(im.size)))
checks['renders_max1600']=all(max(r['size'])<=1600 for r in images)
checks['requested_renders_and24_frames']=all((H/'renders'/n).exists() for n in ('overview.png','parked_doors_open.png','under_cabinet_band.png','passing.png','executed_local_strip.png','reachability_study.png')) and len(list((H/'renders').glob('frame_*.png')))==24
frame=read(O/'frame_manifest.json');checks['strip_has24_executed_local_samples']=len(frame['frames'])==24 and frame['executed_meal'] is False and read(H/frame['path_file'])['ok']
resources=[dict(file=p.name,**read(p)) for p in (H/'audit').glob('*.resource.json')];checks['bounded_cpu_jobs']=all(r['timeout_s']<1200 and r['elapsed_s']<1200 and r['peak_MiB']<1900 and r['cpu_only'] for r in resources)
bytes_n=sum(p.stat().st_size for p in H.rglob('*') if p.is_file());checks['under3GB']=bytes_n<3_000_000_000
post=root/'posts/r07/integrator.md';checks['chinese_first_post']=post.exists() and post.read_text(encoding='utf-8').startswith('本轮')
invalid=[]
for p in O.glob('*.json'):
 try:json.loads(p.read_text(encoding='utf-8-sig'),parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
 except Exception as exc:invalid.append(dict(file=p.name,error=str(exc)))
checks['required_json_finite']=not invalid
out=dict(artifact_checks_pass=all(checks.values()),engineering_pass=False,checks=checks,changed_upstream=changed,invalid_json=invalid,selected_layout=ID,copied_python_count=len(hashes),static_search_budget_coverage=dict(strokes_96_or_more=s['strokes_with_96_starts'],total=105,complete=s['all_strokes_full_search_budget']),complete_paired_layout_maps=s['complete_paired_layout_maps'],meal_planner_execution_coverage=False,output_bytes=bytes_n,max_elapsed_s=max(r['elapsed_s'] for r in resources),max_worker_tree_MiB=max(r['peak_MiB'] for r in resources),numerical_worker_concurrency_max=3,concurrency_basis='No more than three simultaneous foreground numerical worker slots; launcher/monitor processes do not do numerical work. Unrelated R06/user services untouched.',resources=resources,images=images,limitations=['Artifact fidelity does not establish task completion, a passing meal or folded park.','Per-stroke allocated budget and actual time are distinct.','Missing persistent interfaces/attachments reject meal roots before RRT; no zero-time search is represented as65s.'])
(O/'delivery_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(artifact_checks_pass=out['artifact_checks_pass'],failed_checks=[k for k,x in checks.items() if not x],MiB=bytes_n/1048576,budget_coverage=out['static_search_budget_coverage'])));assert out['artifact_checks_pass']
