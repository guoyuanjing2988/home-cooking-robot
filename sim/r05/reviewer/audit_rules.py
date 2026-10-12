"""R05 provenance, declarations, force, geometry, schedule and cost audit."""
import os,sys,json,hashlib,difflib,ast,csv,collections,math
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import numpy as np,mujoco
H=Path(__file__).resolve().parent;I=H.parent/'integrator';R=H.parents[2];sys.path.insert(0,str(I));import final_check as f
O=H/'results';A=H/'audit';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,v):(O/name).write_text(json.dumps(v,indent=2,allow_nan=False))
def funcs(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(p.read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
r04=R/'sim/r04/integrator';r02=R/'sim/r02/concept2'
diffs={}
for name in ('reference.py','final_check.py','model.py','solver.py','distance.py'):
 a=r04/name;b=I/name;d=''.join(difflib.unified_diff(a.read_text().splitlines(True),b.read_text().splitlines(True),fromfile=str(a),tofile=str(b)));(A/(name+'.diff')).write_text(d)
 aa,bb=funcs(a),funcs(b);diffs[name]=dict(byte_equal=sha(a)==sha(b),old_sha256=sha(a),new_sha256=sha(b),changed_functions=[k for k in aa.keys()&bb.keys() if aa[k]!=bb[k]],added=list(bb.keys()-aa.keys()))
assets=[]
for p in (r04/'models').rglob('*'):
 if p.is_file() and p.suffix.lower() in ('.stl','.obj','.png','.jpg'):
  q=I/'models'/p.relative_to(r04/'models')
  if q.exists():assets.append(dict(path=str(p.relative_to(r04)),equal=sha(p)==sha(q)))
for sub in ('vendor','inputs','sources'):
 for p in (r04/sub).rglob('*'):
  if p.is_file() and '__pycache__' not in str(p) and p.suffix.lower() in ('.py','.xml','.urdf','.xacro','.stl','.obj','.dae','.json'):
   q=I/sub/p.relative_to(r04/sub)
   if q.exists():assets.append(dict(path=str(p.relative_to(r04)),equal=sha(p)==sha(q)))
p4=json.loads((r04/'results/process_v3.json').read_text());p5=json.loads((I/'results/process_v3.json').read_text());p2=json.loads((R/'sim/r02/tools/results/process_v2.json').read_text())
equal={k:p4[k]==p5[k] for k in ('tools','finished_products','force_models','acceptance','installed_geometry')}
dump('rule_provenance.json',dict(diffs=diffs,original_r02_reference_equal=sha(r02/'reference.py')==sha(I/'reference.py'),assets=assets,asset_mismatches=[x for x in assets if not x['equal']],process_equality=equal,r02_force_models_equal=p2['force_models']==p5['force_models'],r02_finished_products_equal=p2['finished_products']==p5['finished_products']))

M=json.loads((I/'results/motion.json').read_text());ledger=json.loads((I/'results/intended_contacts.json').read_text())['rows'];ledger_errors=[];wins=[]
for r in ledger:
 if not r.get('reason') or not r.get('held_parts'):ledger_errors.append(r)
 if r.get('window_max_mm') is not None and r['window_max_mm']>50:ledger_errors.append(r)
 if any(x in r['face'] for x in ('guard','wall','faucet','rail','cabinet')):ledger_errors.append(r)
for kind,rs in [('internal',M['internal']),('connection',M['between_strokes'])]:
 for r in rs:
  edges=r.get('edges',[r.get('planner',{})])
  for j,e in enumerate(edges):
   for w in e.get('contact_windows',[]):
    reasons=[]
    if w.get('max_window_mm',51)>50 or not np.allclose(w['normal'],[0,0,1]):reasons.append('axis/window')
    if not w.get('insertion_axis_reason') or not w.get('reason'):reasons.append('missing geometric reason')
    names=[r.get('stroke')] if kind=='internal' else [r['from_stroke'],r['to_stroke']]
    matches=[x for x in ledger if x['stroke'] in names and x['side']==w['side'] and x['face']==w['face'] and x['held_parts']==w['held_parts']]
    if not matches:reasons.append('no per-stroke declaration')
    wins.append(dict(kind=kind,index=r['index'],edge=j,side=w['side'],face=w['face'],held_parts=w['held_parts'],max_window_mm=w['max_window_mm'],geometric_reason=w.get('insertion_axis_reason'),declaration_matches=len(matches),errors=reasons))
dump('contact_window_audit.json',dict(original_rows=len(ledger),declared_strokes=len(set(x['stroke'] for x in ledger)),ledger_errors=ledger_errors,windows=wins,window_count=len(wins),window_errors=[x for x in wins if x['errors']],scope='All retained successful and failed attempt windows; active-state straightness is independently replayed in motion results. Working declarations do not create a free-transit work exemption.'))

S=json.loads((I/'results/schedule.json').read_text());print('calendar sample',S['rows'][:1],flush=True)
rows=S['rows'];conf=[];deps=[]
for ia,a in enumerate(rows):
 for b in rows[ia+1:]:
  if max(a['start_s'],b['start_s'])<min(a['end_s'],b['end_s'])-1e-8:
   rr=set(a.get('resources',[]))&set(b.get('resources',[]))
   if rr:conf.append(dict(a=a,b=b,resources=sorted(rr)))
by={x.get('id',x.get('name')):x for x in rows}
for a in rows:
 for d in a.get('depends',a.get('dependencies',[])):
  if d in by and by[d]['end_s']>a['start_s']+1e-8:deps.append(dict(a=a,dependency=d))
costs=list(csv.DictReader((I/'results/costs.csv').open(encoding='utf-8')));cost=[]
for config in sorted(set(r['configuration'] for r in costs)):
 rr=[r for r in costs if r['configuration']==config];subtotal=sum(float(r['total_cny']) for r in rr if r['item'] not in ('TOTAL','One15percent project reserve'));total=sum(float(r['total_cny']) for r in rr if r['item']=='TOTAL');reserve=sum(float(r['total_cny']) for r in rr if r['item']=='One15percent project reserve');safety=[r for r in rr if 'safety' in r['item'].lower()]
 cost.append(dict(configuration=config,subtotal=subtotal,reserve=reserve,total=total,recomputed=round(subtotal*1.15,2),matches=abs(total-round(subtotal*1.15,2))<.02,safety=safety))
mass=161.06+35.8+27.9+4*51.16944/2.8+8+4*.8
dump('schedule_cost.json',dict(resource_conflicts=conf,precedence_errors=deps,calendar_rows=len(rows),planned_makespan_s=max(r['end_s'] for r in rows),local_two_arm_motion_seconds=S['geometric_two_arm_motion_overlap_s'],proposed_overlap=S['proposed_overlap'],costs=cost,storage_recalculation=dict(mass_kg=mass,hold_N=1.5*9.81*mass,drive_N=1.5*(9.81+.3)*mass,pallet_hold_N=1.5*9.81*30,pallet_drive_N=1.5*(9.81+.3)*30),verified_prep_min=S['verified_prep_min']))

# Compile both full working models and compare every retained named shape.
geom=[];import importlib.util
spec=importlib.util.spec_from_file_location('oldmodel',r04/'model.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
# Use the copied immutable model text, with its source paths retained.
old.CONFIG=copycfg=json.loads(json.dumps(f.s.model.CONFIG))
sg=f.s.P['phases'][0]['segments'][0];ph=f.s.P['phases'][0];newch=f.s.Checker(ph,sg)
import xml.etree.ElementTree as E
t4,_=old.build();t5,_=f.s.model.build();m4=mujoco.MjModel.from_xml_string(E.tostring(t4.getroot(),encoding='unicode'));m5=mujoco.MjModel.from_xml_string(E.tostring(t5.getroot(),encoding='unicode'));shapes=[];moved=[]
for g in range(m4.ngeom):
 name=mujoco.mj_id2name(m4,mujoco.mjtObj.mjOBJ_GEOM,g)
 if not name:continue
 g5=mujoco.mj_name2id(m5,mujoco.mjtObj.mjOBJ_GEOM,name)
 if g5<0:shapes.append(dict(name=name,error='missing'));continue
 if m4.geom_type[g]!=m5.geom_type[g5] or not np.allclose(m4.geom_size[g],m5.geom_size[g5],atol=1e-12):shapes.append(dict(name=name,error='shape/size changed',old=m4.geom_size[g].tolist(),new=m5.geom_size[g5].tolist()))
 if not np.allclose(m4.geom_pos[g],m5.geom_pos[g5],atol=1e-12):moved.append(dict(name=name,old=m4.geom_pos[g].tolist(),new=m5.geom_pos[g5].tolist()))
dump('compile_inventory.json',dict(working_geoms=newch.m.ngeom,working_joints=newch.m.njnt,model_functions=list(funcs(I/'model.py')),geometry_changes=shapes,position_changes=moved,old_geoms=m4.ngeom,new_geoms=m5.ngeom,body_mass_equal=bool(np.array_equal(m4.body_mass,m5.body_mass)),body_inertia_equal=bool(np.array_equal(m4.body_inertia,m5.body_inertia)),body_inertial_position_equal=bool(np.array_equal(m4.body_ipos,m5.body_ipos)),joint_ranges_equal=bool(np.array_equal(m4.jnt_range,m5.jnt_range))))
print('RULE_AUDIT_COMPLETE',len(ledger),len(wins),'window errors',sum(bool(w['errors']) for w in wins),'costs',len(cost),flush=True)
