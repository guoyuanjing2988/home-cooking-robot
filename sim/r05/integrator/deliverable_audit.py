"""Check delivery consistency; this audit does not change numerical acceptance."""
import csv,hashlib,json,math
from pathlib import Path
from PIL import Image
H=Path(__file__).resolve().parent
ROOT=H.parents[2]
O=H/'results'
def read(n):return json.loads((O/n).read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p,b,ps,mo=map(read,['process_v3.json','best.json','phase_summary.json','motion.json'])
 issues=[];checks={}
 def check(name,ok):
  checks[name]=bool(ok)
  if not ok:issues.append(name)
 parts=[v for i in ps['instances'] for v in i['parts']]
 check('all105strokes_have_at_least96starts',len(parts)==105 and all(v['starts']>=96 for v in parts))
 check('start_total_matches',sum(v['starts'] for v in parts)==ps['starts_total'])
 check('verified_total_matches',sum(v['independent_verified_witnesses'] for v in parts)==ps['verified_witnesses'])
 check('best_and_summary_counts_match',b['phases_passed']==ps['logical_passed'] and len(b['witnesses'])==ps['strokes_passed'])
 check('process_hash_matches_replay',digest(O/'process_v3.json')==ps['process_sha256'])
 check('overall_failure_honestly_recorded',not b['overall_pass'] and b['motion_status']=='fail' and not mo['pass_'])
 check('all95witness_files_present',all((O/'witnesses'/(k+'.json')).exists() and (O/'witnesses'/(k+'.xml')).exists() for k in b['witnesses']))
 poses=[po for w in b['witnesses'].values() for po in w['poses']]
 check('accepted_pose_errors_within_binding_gate',all(e['position_mm']<=5 and e['orientation_deg']<=3 for po in poses for e in po['errors']))
 check('accepted_public_ranges_and_literal_contact_gate',all(po['public_ranges_ok'] and not po['forbidden'] for po in poses))
 check('accepted_envelope_ratios_within_one',all(po['torque_ratios'][case]['ratio']<=1 for po in poses for case in ('nominal','check')))
 check('accepted_grip_margins_at_least_one',all(g['margin']>=1 for po in poses for case in ('nominal','check') for g in po['grip'][case]))
 check('accepted_actual_flange_payload_and_COM_charts',all(v['OEM_payload_chart_ok'] for po in poses for v in po['payload']))
 check('passing_has_at_least96starts_and_verified_route',mo['passing']['pass_'] and mo['passing']['starts_tried']>=96 and mo['passing']['verified_routes']>=1)
 check('passing_uses_operating_carriage_range_and_unchanged_mechanical_geometry',mo['passing']['operating_carriage_range_m']=={'R':[-1.7,.045],'L':[-1.7,.2]} and mo['passing']['mechanical_carriage_range_m']==[-1.7,.2])
 copies={
  'sim/r02/concept2/reference.py':H/'reference.py',
  'sim/r01/concept/model.py':H/'oem_model.py'}
 hashes={src:dict(source_sha256=digest(ROOT/src),copy_sha256=digest(dst),unchanged=digest(ROOT/src)==digest(dst)) for src,dst in copies.items()}
 check('reference_and_oem_source_copies_unchanged',all(v['unchanged'] for v in hashes.values()))
 check('meal_product_specifications_unchanged',p['finished_products']==json.loads((ROOT/'sim/r02/tools/results/process_v2.json').read_text())['finished_products'])
 costs=read('cost_summary.json');timeline=read('timeline.json')
 with (O/'costs.csv').open(encoding='utf-8-sig',newline='') as file:rows=list(csv.DictReader(file))
 safety=[r for r in rows if r['item']=='Inclusive home-safety package']
 check('exactly_one_inclusive18000home_safety_package',len(safety)==1 and float(safety[0]['total_cny'])==18000)
 check('budget_matches_cost_csv',abs(sum(float(r['total_cny']) for r in rows if r['item']!='TOTAL')-costs['total_cny'])<.011)
 check('planning_timeline_matches',abs(sum(r['duration_s'] for r in timeline['rows'])/60-timeline['prep_min'])<1e-7 and timeline['verified_prep_min'] is None)
 views=['overview','passing','parked']+['Q'+str(i).zfill(2) for i in range(1,28)]
 images=[]
 for name in views:
  path=H/'renders'/(name+'.png')
  if not path.exists():issues.append('missing_render_'+name);continue
  with Image.open(path) as im:
   im.verify()
  with Image.open(path) as im:images.append(dict(file=str(path.relative_to(H)),size=list(im.size)))
 check('all30requested_renders_present_and_at_most1600px',len(images)==30 and all(max(i['size'])<=1600 for i in images))
 check('post_is_chinese_first_and_contains_english_details',(ROOT/'posts/r03/integrator.md').read_text(encoding='utf-8').startswith('本轮') and 'Final result and evidence' in (ROOT/'posts/r03/integrator.md').read_text(encoding='utf-8'))
 files=list(H.rglob('*'));size=sum(a.stat().st_size for a in files if a.is_file())
 check('output_under3GB',size<3_000_000_000)
 out=dict(schema='r03.delivery.consistency',artifact_consistency_pass=not issues,engineering_acceptance_pass=False,checks=checks,issues=issues,hashes=hashes,output_bytes=size,render_images=images,logical_static_passed=ps['logical_passed'],logical_total=ps['logical_total'],motion='fail',cost_cny=costs['total_cny'],planning_prep_min=timeline['prep_min'],note='Passing this delivery audit only establishes consistency and completeness of the reported negative evidence. It does not pass the kitchen robot.')
 (O/'deliverable_audit.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 print(json.dumps(dict(consistency=not issues,issues=issues,bytes=size,images=len(images))))
 if issues:raise SystemExit(1)
if __name__=='__main__':main()
