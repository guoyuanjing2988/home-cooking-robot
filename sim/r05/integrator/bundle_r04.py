import json,hashlib,collections,csv
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';P=json.loads((O/'process_v3.json').read_text());static=json.loads((O/'static_all.json').read_text());cost=json.loads((O/'cost_summary.json').read_text());schedule=json.loads((O/'schedule.json').read_text())
def write(name,obj):(O/name).write_text(json.dumps(obj,indent=2,allow_nan=False))
logical=[];instances=[]
for ph in P['phases']:
 parts=[r for r in static['rows'] if r['phase']==ph['id']];instances.append(dict(id=ph['id'],logical_id=ph['id'].split('.')[0],name=ph['name'],ok=all(r['ok'] for r in parts),parts=parts))
for i in range(1,28):
 q=f'Q{i:02}';ps=[x for x in instances if x['logical_id']==q];logical.append(dict(id=q,ok=bool(ps) and all(x['ok'] for x in ps),instances=[x['id'] for x in ps],failed_strokes=[r['stroke'] for x in ps for r in x['parts'] if not r['ok']]))
fresh=[r for r in static['rows'] if not r['source'].startswith('baseline')]
summary=dict(schema='r04.independent-static-replay.v1',logical_passed=sum(x['ok'] for x in logical),logical_total=27,instances_passed=sum(x['ok'] for x in instances),instances_total=len(instances),strokes_passed=sum(r['ok'] for r in static['rows']),strokes_total=len(static['rows']),verified_witnesses=len(static['witnesses']),selected_candidates_replayed=sum(r['replayed_candidates'] for r in static['rows']),logical_phases=logical,instances=instances,acceptance=P['acceptance'],process_sha256=hashlib.sha256((O/'process_v3.json').read_bytes()).hexdigest(),historical_seeds_tried=sum(r['archived_starts'] for r in static['rows']),historical_solver_solutions_found=sum(r['solver_solutions_found'] for r in static['rows']),fresh_search_selected_strokes=len(fresh),fresh_search_selected_seeds=sum(r['archived_starts'] for r in fresh),fresh_solver_solutions_found=sum(r['solver_solutions_found'] for r in fresh),scope='Only selected successful archived/fresh candidates independently replayed on final full geometry. Historical solver solution counts are not final verified counts. This is static acceptance, not connected paths, manufacturing, processing coverage or measured food quality.')
write('phase_summary.json',summary)
motion=json.loads((O/'motion.json').read_text()) if (O/'motion.json').exists() else dict(status='pending')
import sys;sys.path.insert(0,str(H));import model
source_stages={ph['id']:sorted(set(Path(r['source']).parts[1] if Path(r['source']).parts[0]=='results' else 'baseline' for r in static['rows'] if r['phase']==ph['id'])) for ph in P['phases']}
best=dict(schema='r04.best-static-candidate.v1',config=model.CONFIG,configuration='best_candidate',status='NOT_COMPLETE_MEAL_PASS',overall_pass=False,phases_passed=summary['logical_passed'],phases_total=27,strokes_passed=summary['strokes_passed'],strokes_total=len(static['rows']),witnesses=static['witnesses'],stroke_sources={r['stroke']:r['source'] for r in static['rows']},phase_source_stages=source_stages,cost_cny=cost['totals']['best_candidate'],motion_status=motion.get('status','pending'),connections_passed=motion.get('connections_passed',0),connections_total=104,prep_min_planning=schedule['planned_prep_min'],prep_min_verified=None,acceptance=P['acceptance'],food_quality_qualified=False,geometry_sha256=hashlib.sha256((H/'model.py').read_bytes()).hexdigest(),process_sha256=summary['process_sha256'],OEM_models_unscaled=True,UR5e_original_base_meshes_retained=True,distance_evidence='All eligible pairs have enclosing AABB or independent convex dual lower bounds; original MuJoCo contact checker also runs unchanged with explicit face mapping.')
write('best.json',best)
lowest=min(cost['totals'],key=cost['totals'].get)
write('cheapest.json',dict(schema='r04.cheapest-admitted.v1',passing_configuration=None,cost_cny=None,overall_pass=False,reason='No complete conserved meal, connected motion, idle kitchen and product-quality configuration passes. A cheapest passing configuration does not exist in these tested results.',lowest_unqualified_candidate=dict(configuration=lowest,cost_cny=cost['totals'][lowest],status='UNQUALIFIED_BUDGET_SCENARIO'),compared_configurations=cost['totals'],best_static_candidate_cny=best['cost_cny']))
contacts=[]
for ph in P['phases']:
 for sg in ph['segments']:
  for i,po in enumerate(sg['poses']):
   for side,h in po.items():
    for c in h.get('contacts',[]):contacts.append(dict(stroke=ph['id']+'__'+sg['label'].replace(' ','_'),pose_index=i,side=side,held=h['held'],product=h['product'],face=c['face'],held_parts=c['held_parts'],reason=c['reason'],geometry=c['face_geometry'],policy='own pickup/return support at grasp/release endpoint' if sg.get('action') in ['pick','place'] and c['face'].startswith(('raw_','dock_','output_','slicer_bowl')) else 'food/tool working support/face; narrow named face and geometric normal/position required'))
write('intended_contacts.json',dict(rows=contacts,no_broad_exemptions=True,face_replay='Named part pair, top/axial normal>=.85 and position within6.5mm bristle/contact-midpoint tolerance; original whole fixtures/guards/rails/walls remain checked. No non-endpoint own-support permission.'))
print('bundle',summary['logical_passed'],'/27',summary['strokes_passed'],'/105',best['cost_cny'],'cheapest',None)
