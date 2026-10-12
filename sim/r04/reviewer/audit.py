"""Read-only R04 provenance, contact, requirements, cost and schedule audit."""
from pathlib import Path
import ast, json, hashlib, difflib, collections, csv, shutil
H=Path(__file__).resolve().parent; ROOT=H.parents[2]; I=H.parent/'integrator'
A=H/'audit'; O=H/'results'; A.mkdir(exist_ok=True); O.mkdir(exist_ok=True)
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(n,v): (A/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
files=list(I.rglob('*'))+[ROOT/'DECISIONS.md',ROOT/'inputs/prep_checker.py',ROOT/'sim/r02/concept2/reference.py']
dump('input_hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in files if p.is_file()})
def funcs(p):
 return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_text(encoding='utf-8-sig'))) if isinstance(n,ast.FunctionDef)}
diffs=[]
for old,new,label in [(ROOT/'sim/r02/concept2/reference.py',I/'reference.py','r02_reference'),(ROOT/'inputs/prep_checker.py',I/'reference.py','prep_input'),(ROOT/'sim/r03/integrator/solver.py',I/'solver.py','r03_solver'),(ROOT/'sim/r03/integrator/model.py',I/'model.py','r03_model'),(ROOT/'sim/r03/integrator/final_check.py',I/'final_check.py','r03_final_check')]:
 (A/(label+'.diff')).write_text(''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile=str(old),tofile=str(new))),encoding='utf-8')
 a,b=funcs(old),funcs(new)
 diffs.append(dict(label=label,identical=old.read_bytes()==new.read_bytes(),old_sha=sha(old),new_sha=sha(new),changed=sorted(k for k in a.keys()&b.keys() if a[k]!=b[k]),added=sorted(b.keys()-a.keys()),removed=sorted(a.keys()-b.keys())))
dump('checker_diff.json',diffs)
P=read(I/'results/process_v3.json'); P3=read(ROOT/'sim/r03/integrator/results/process_v3.json'); P2=read(ROOT/'sim/r02/tools/results/process_v2.json')
rows=[]; violations=[]
own={'peeler':'dock_peeler_face','eye_core_spoon':'dock_eye_core_spoon_face','wash_pad':'dock_wash_pad_face','cut_cassette':'secondary_work_face'}
for ph in P['phases']:
 for sg in ph['segments']:
  for pi,po in enumerate(sg['poses']):
   for side,h in po.items():
    for c in h.get('contacts',[]):
     face=c['face']; typ=h['held']; parts=c['held_parts']; valid=False; kind='unclassified'
     endpoint=(sg['action']=='pick' and pi==0) or (sg['action']=='place' and pi==len(sg['poses'])-1)
     if typ=='root_food' and parts==['food'] and face in ('raw_'+h['product']+'_land','peel_food_land','peel_endstop-1','peel_endstop1','root_brush_work_face','greens_crease_land'):
      valid=True;kind='food_work_support'
      if face.startswith('raw_'):valid=sg['action']=='pick' and pi==0;kind='own_pickup_support'
     elif typ in ('peeler','eye_core_spoon') and face=='clamped_food':
      valid=set(parts)<=set(['peeler_edge','peeler_y_head'] if typ=='peeler' else ['spoon_edge','spoon_neck_work_face']);kind='tool_food_work'
     elif typ=='wash_pad' and face in ('wash_food','peel_food_land','secondary_work_face'):
      valid=parts==['wash_pad_contact'];kind='tool_work_surface'
     elif face==own.get(typ) or typ=='carried_bowl' and face in ('slicer_bowl_land','output_'+h['product']+'_land'):
      valid=endpoint;kind='own_pickup_return_support'
     row=dict(phase=ph['id'],stroke=sg['label'],pose=pi,side=side,held=typ,action=sg['action'],face=face,held_parts=parts,reason=c.get('reason'),face_geometry=c.get('face_geometry'),classification=kind,valid=bool(valid))
     rows.append(row)
     if not valid or not isinstance(parts,list) or not parts or not c.get('reason'):violations.append(row)
dump('intended_contacts.json',dict(entries=len(rows),strokes=len({(r['phase'],r['stroke']) for r in rows}),violations=violations,rows=rows))
meshes=[]
for sub in ['sources/menagerie/universal_robots_ur5e','sources/xarm6_meshes','sources/end_tool']:
 for p in (I/sub).rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(I); candidates=[ROOT/'sim/r03/integrator'/rel,ROOT/'sim/r02/concept2'/rel,ROOT/'sim/r01/concept'/rel]
  source=next((x for x in candidates if x.exists()),None)
  meshes.append(dict(file=str(rel),source=str(source.relative_to(ROOT)) if source else None,unchanged=sha(p)==sha(source) if source else None))
dump('geometry_sources.json',dict(files=meshes,mismatches=[r for r in meshes if r['unchanged'] is False],unmatched=[r for r in meshes if r['source'] is None]))
def force_parts(p):
 return {(ph['id'],sg['label']):[{side:{k:h[k] for k in ['held_kg','nominal_forces_N','check_forces_N','nominal_moments_Nm','check_moments_Nm','grip']} for side,h in po.items()} for po in sg['poses']] for ph in p['phases'] for sg in ph['segments']}
forces=dict(acceptance_equal_R03=P['acceptance']==P3['acceptance'],products_equal_R02=P['finished_products']==P2['finished_products'],force_models_equal_R02=P['force_models']==P2['force_models'],tools_equal_R03=P['tools']==P3['tools'],stroke_mass_force_grip_equal_R03=force_parts(P)==force_parts(P3),old_phase_coverage=sorted({x for ph in P['phases'] for x in ph['replaces_P']}))
dump('force_requirement_audit.json',forces)
schedule=read(I/'results/schedule.json'); jobs=schedule['rows']; conflicts=[]; dep_errors=[]; overlaps=[]
lookup={j['id']:j for j in jobs}
for j in jobs:
 for dep in j['depends']:
  if lookup[dep]['end_s']>j['start_s']+1e-8:dep_errors.append([dep,j['id']])
for i,a in enumerate(jobs):
 for b in jobs[i+1:]:
  if max(a['start_s'],b['start_s'])<min(a['end_s'],b['end_s'])-1e-8:
   row=dict(a=a['id'],b=b['id'],start_s=max(a['start_s'],b['start_s']),end_s=min(a['end_s'],b['end_s']),shared_resources=sorted(set(a['resources'])&set(b['resources'])))
   overlaps.append(row)
   if row['shared_resources']:conflicts.append(row)
conc=read(I/'results/dual_arm_concurrency.json')
conc_summary=[dict(phase=r['phase'],seeds_tried=r['seeds_tried'],solver_solutions=r['solver_solutions_found'],verified=r['verified_witnesses'],failure_counts=dict(collections.Counter('payload' if any(not p['OEM_payload_chart_ok'] for po in x['poses'] for p in po['payload']) else 'other' for x in r['independent_replays']))) for r in conc['rows']]
cost=list(csv.DictReader((I/'results/costs.csv').open(encoding='utf-8-sig'))); totals={}
for name in sorted({r['configuration'] for r in cost}):
 rs=[r for r in cost if r['configuration']==name]; base=sum(float(r['total_cny']) for r in rs if r['item'] not in ('TOTAL','One15percent project reserve'))
 totals[name]=dict(subtotal=round(base,2),reserve=round(base*.15,2),total=round(base*1.15,2),submitted=next(float(r['total_cny']) for r in rs if r['item']=='TOTAL'),home_safety_lines=[r for r in rs if 'safety' in r['item'].lower()])
dump('schedule_cost_audit.json',dict(resource_conflicts=conflicts,dependency_errors=dep_errors,all_overlaps=overlaps,makespan_s=max(j['end_s'] for j in jobs),serial_s=sum(j['duration_s'] for j in jobs),auxiliary_work_s=sum(j['duration_s'] for j in jobs if 'aux' in j['resources'] and j['id']!='clean'),concurrency_status=conc['status'],helper_substitution_summary=conc_summary,totals=totals,cheapest=read(I/'results/cheapest.json'),interpretation='Calendar conflicts are evaluated independently. No calendar can certify arm-arm geometry or an unadmitted helper substitution.'))
shutil.copyfile(I/'bounded.py',H/'bounded.py')
print(json.dumps(dict(reference_identical=diffs[0]['identical'],contacts=len(rows),violations=len(violations),meshes=len(meshes),resource_conflicts=len(conflicts),schedule_min=max(j['end_s'] for j in jobs)/60,helper_verified=sum(r['verified'] for r in conc_summary),costs=totals)))
