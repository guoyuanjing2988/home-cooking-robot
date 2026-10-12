"""Read-only R03 source, contact, geometry and accounting review."""
from pathlib import Path
import ast, json, hashlib, difflib, collections, csv, shutil
H=Path(__file__).resolve().parent
ROOT=H.parents[2]
I=ROOT/'sim/r03/integrator'
A=H/'audit'; A.mkdir(exist_ok=True)
def dump(n,v): (A/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def functions(p):
 t=ast.parse(p.read_text(encoding='utf-8-sig'))
 return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(t) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
files=[ROOT/'DECISIONS.md', ROOT/'inputs/prep_checker.py',ROOT/'sim/r02/concept2/reference.py',ROOT/'sim/r01/concept/model.py']
files += list(I.glob('*.py')) + list(I.glob('results/*.json')) + [ROOT/'posts/r03/integrator.md']
dump('source_hashes_before.json',{str(p.relative_to(ROOT)):sha(p) for p in files})
comp=[]
for old,new,label in [(ROOT/'sim/r02/concept2/reference.py',I/'reference.py','r02_reference'),(ROOT/'inputs/prep_checker.py',I/'reference.py','original_input'),(ROOT/'sim/r01/concept/model.py',I/'oem_model.py','oem_model')]:
 x=old.read_text(encoding='utf-8-sig');y=new.read_text(encoding='utf-8-sig')
 (A/(label+'.diff')).write_text(''.join(difflib.unified_diff(x.splitlines(True),y.splitlines(True),fromfile=str(old),tofile=str(new))),encoding='utf-8')
 a,b=functions(old),functions(new)
 comp.append(dict(comparison=label,byte_identical=old.read_bytes()==new.read_bytes(),old_sha256=sha(old),new_sha256=sha(new),unchanged_functions=sorted(k for k in a.keys()&b.keys() if a[k]==b[k]),changed_functions=sorted(k for k in a.keys()&b.keys() if a[k]!=b[k]),added_functions=sorted(b.keys()-a.keys()),removed_functions=sorted(a.keys()-b.keys())))
dump('checker_diff.json',comp)
p=json.loads((I/'results/process_v3.json').read_text());p2=json.loads((ROOT/'sim/r02/tools/results/process_v2.json').read_text())
rows=[];violations=[]
own_support={
 'peeler':'dock_peeler_face','eye_core_spoon':'dock_eye_core_spoon_face','wash_pad':'dock_wash_pad_face',
 'cut_cassette':'secondary_work_face'}
for ph in p['phases']:
 for sg in ph['segments']:
  for pi,po in enumerate(sg['poses']):
   for side,h in po.items():
    for c in h.get('contacts',[]):
     face=c['face'];typ=h['held'];parts=c['held_parts'];valid=False;kind='unclassified'
     if typ=='root_food' and parts==['food'] and face in ('raw_'+h['product']+'_land','peel_food_land','peel_endstop-1','peel_endstop1','root_brush_work_face','greens_crease_land'):
      valid=True;kind='food_work_support'
      if face.startswith('raw_'):
       valid=sg['action']=='pick' and pi==0;kind='own_pickup_support'
     elif typ in ('peeler','eye_core_spoon') and face=='clamped_food':
      valid=set(parts)<=set(['peeler_edge','peeler_y_head'] if typ=='peeler' else ['spoon_edge','spoon_neck_work_face']);kind='tool_food_work_face'
     elif typ=='wash_pad' and face in ('wash_food','peel_food_land','secondary_work_face'):
      valid=parts==['wash_pad_contact'];kind='tool_work_surface'
     elif face==own_support.get(typ) or (typ=='carried_bowl' and face in ('slicer_bowl_land','output_'+h['product']+'_land')):
      kind='own_pickup_return_support'
      valid=(sg['action']=='pick' and pi==0) or (sg['action']=='place' and pi==len(sg['poses'])-1)
     record=dict(phase=ph['id'],stroke=sg['label'],pose=pi,side=side,held=typ,face=face,held_parts=parts,action=sg['action'],classification=kind,permitted_by_binding_rule=bool(valid),geometric_reason=c.get('reason'),face_geometry=c.get('face_geometry'))
     rows.append(record)
     if not valid or not isinstance(parts,list) or not parts or not c.get('reason'):violations.append(record)
dump('intended_contacts.json',dict(entries=len(rows),stroke_count=len({(r['phase'],r['stroke']) for r in rows}),violations=violations,rows=rows,interpretation='Food working supports may persist during food work; non-food own support permission must be at pickup/release endpoint. Individual named held parts and exact faces audited; final replay independently checks face normals and positions.'))
meshrows=[]
for sub in ('sources/menagerie/universal_robots_ur5e','sources/xarm6_meshes','sources/end_tool'):
 for f in (I/sub).rglob('*'):
  if not f.is_file():continue
  rel=f.relative_to(I)
  candidates=[ROOT/'sim/r02/concept2'/rel,ROOT/'sim/r01/concept'/rel]
  if 'xarm6_meshes' in str(rel):candidates += [ROOT/'sim/r01/concept/sources/xarm_ros/xarm_description/meshes/xarm6'/f.parent.name/f.name]
  if 'end_tool' in str(rel):candidates += [ROOT/'sim/r01/concept/sources/xarm_ros/xarm_description/meshes/end_tool'/f.parent.name/f.name]
  src=next((c for c in candidates if c.exists()),None)
  meshrows.append(dict(file=str(rel),source=str(src.relative_to(ROOT)) if src else None,unchanged=sha(src)==sha(f) if src else None,sha256=sha(f)))
dump('geometry_sources.json',dict(files=meshrows,mismatches=[r for r in meshrows if r['unchanged'] is False],unmatched=[r for r in meshrows if r['source'] is None]))
sig=[];summary=json.loads((I/'results/phase_summary.json').read_text());trial=json.loads((I/'results/process_trial_final6.json').read_text())
for ph in p['phases']:
 oldph=next(a for a in trial['phases'] if a['id']==ph['id'])
 for sg in ph['segments']:
  oldsg=next(a for a in oldph['segments'] if a['label']==sg['label'])
  if {k:v for k,v in sg.items() if k!='loops'}!={k:v for k,v in oldsg.items() if k!='loops'}:sig.append(ph['id']+'__'+sg['label'])
with (I/'results/costs.csv').open(encoding='utf-8-sig') as f:cost=list(csv.DictReader(f))
base=sum(float(r['total_cny']) for r in cost if r['item'] not in ('TOTAL','One 15 percent project contingency'))
tm=json.loads((I/'results/timeline.json').read_text());pw=json.loads((I/'results/power.json').read_text())
dump('process_accounting.json',dict(finished_products_identical=p['finished_products']==p2['finished_products'],force_models_identical=p['force_models']==p2['force_models'],tools_identical={k:p['tools'][k]==v for k,v in p2['tools'].items()},all_P_covered=sorted({x for ph in p['phases'] for x in ph['replaces_P']}),physics_changed_final6_to_final7=sig,acceptance=p['acceptance'],starts=summary['starts_total'],solutions=summary['solutions_found'],verified_witnesses=summary['verified_witnesses'],logical_passed=summary['logical_passed'],cost_subtotal=base,cost_with_15pct=round(base*1.15,2),time_s=sum(r['duration_s'] for r in tm['rows']),time_min=sum(r['duration_s'] for r in tm['rows'])/60,power_W=sum(r['design_W'] for r in pw['items'])))
shutil.copyfile(I/'bounded.py',H/'bounded.py')
print(json.dumps(dict(reference_identical=comp[0]['byte_identical'],contacts=len(rows),contact_violations=len(violations),mesh_mismatches=len([r for r in meshrows if r['unchanged'] is False]),subtotal=base,cost=round(base*1.15,2),seconds=sum(r['duration_s'] for r in tm['rows']))))
