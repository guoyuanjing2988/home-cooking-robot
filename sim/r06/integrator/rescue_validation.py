"""Final loads, policy adversarial cases and immutable-source audit."""
from rescue_spec import *
import argparse,csv,itertools
p=argparse.ArgumentParser();p.add_argument('--variant',type=int,default=15);p.add_argument('--loads-only',action='store_true');a=p.parse_args();V=a.variant
def read(n):return json.loads((H/n).read_text())
phase=read('results/phase_summary.json');prefix=read('results/executed_prefix.json');cfg=config(V);checks=[]
def check(name,condition,detail=None):checks.append(dict(name=name,pass_=bool(condition),detail=detail))
def forcebox(h):
 h=copy.deepcopy(h);h['R']['check_forces_N']=[list(x) for x in itertools.product((-1.89,1.89),repeat=3)];h['R']['force_basis']='Conservative Cartesian box enclosing4.2kg*0.3m/s2*1.5 carry inertia, applied at assembly CoM';return h
loads=[];capability=[]
for row in phase['selected_witnesses']:
 job=row['job'];loc=copy.deepcopy(job['locations']);loc[job['object_id']]=job['origin'];empty=Workcell(V,None,loc);held=Workcell(V,job['object_id'],loc);empty.capture(job['object_id'],job['origin']);held.contact_windows=held.window(job['object_id'],job['station'],job['origin']);target=key_position(job['origin'],cfg)
 for pp in row['poses']:
  ch=held if pp['label'].startswith('retained_') else empty;q=np.array(pp['q']);hs=forcebox(hand(ch,target));tq,gr,cases=check_load(ch,q,hs);hits,mins,pf=contacts(ch,q)
  loads.append(dict(stroke=row['stroke'],pose=pp['label'],pass_=not hits and tq<=1 and gr>=1,torque_ratio=tq,grip_margin=gr,force_cases=cases,geometry_hits=hits[:3]))
  if ch.held_id:
   heavy=copy.deepcopy(hs);heavy['R']['held_kg']=3.;t,g,cs=check_load(ch,q,heavy);capability.append(dict(stroke=row['stroke'],pose=pp['label'],external_payload_kg=3.,EOAT_kg=1.2,torque_ratio=t,grip_margin=g,pass_=t<=1 and g>=1,CoM_prep_m=list(ch.com)))
write('results/final_force_witnesses.json',loads);write('results/payload_capability.json',dict(challenge_kg=3,total_flange_kg=4.2,pass_=all(x['pass_'] for x in capability),witnesses=capability,scope='Admitted handling witnesses; not a claim about every workspace configuration'))
check('selected_static_geometry_and_cartesian_force_box',all(x['pass_'] for x in loads));check('principal_arm3kg_challenge',bool(capability) and all(x['pass_'] for x in capability))
pathloads=[];load_paths=[dict(p,load_scope='actual_prefix') for p in prefix['paths']];actual_ids={p['id'] for p in prefix['paths']};raw_file=H/f'v2/motion/L{V}_rehearsal.json'
if raw_file.exists():load_paths += [dict(p,load_scope='conditional_raw_pan_rehearsal') for p in json.loads(raw_file.read_text())['paths'] if p['id'] not in actual_ids]
for path in load_paths:
 if not path['ok']:continue
 xml=E.fromstring((H/path['xml']).read_text());heldname=next((b.get('name')[7:] for b in xml.findall('.//body') if b.get('name','').startswith('R_held_output_')),None);locations={}
 for prod in PRODUCTS:
  b=xml.find(f".//worldbody/body[@name='output_{prod}']")
  if b is not None:locations['output_'+prod]=np.fromstring(b.get('pos'),sep=' ').tolist()
 ch=Workcell(V,heldname,locations);ch.contact_windows=path.get('contact_windows',[]) if not path.get('mechanism_evidence') else [];ch.capture_window=path.get('capture_window');pb=PointBound(ch);hs=forcebox(hand(ch,ch.pose(np.array(path['path'][0]))[0]));mx=0;mn=1e30;count=0;maxstep=0
 for aa,bb in zip(path['path'],path['path'][1:]):
  aa=np.array(aa);bb=np.array(bb);bound=pb.segment_bound(aa,bb);steps=max(1,math.ceil(bound/.004));maxstep=max(maxstep,bound/steps*1000)
  for k in range(steps+1):
   q=aa+(bb-aa)*k/steps;t,g,cases=check_load(ch,q,hs);mx=max(mx,t);mn=min(mn,g);count+=1
 pathloads.append(dict(id=path['id'],scope=path['load_scope'],states=count,pass_=mx<=1 and mn>=1 and maxstep<=4.00000001,maximum_torque_ratio=mx,minimum_grip_margin=mn,max_point_step_mm=maxstep,force_box_N=[-1.89,1.89],source_geometry_sha256=hashlib.sha256((H/path['xml']).read_bytes()).hexdigest()))
 print('LOAD_REPLAY',path['id'],count,mx,mn,flush=True)
write('results/final_path_loads.json',pathloads);check('every_accepted_path_cartesian_force_box',all(x['pass_'] for x in pathloads))
lookup={(x['stroke'],x['pose']):x for x in loads}
for row in phase['strokes']+phase['selected_witnesses']:
 ident=row.get('stroke',row.get('id'))
 for pose in row.get('poses',[]):
  match=lookup.get((ident,pose['label']))
  if match:pose.update(torque_ratio=match['torque_ratio'],grip_margin=match['grip_margin'],force_cases=match['force_cases'],force_evidence='results/final_force_witnesses.json; Cartesian8-corner replay supersedes raw two-sign search')
phase.update(max_admitted_torque_ratio=max(x['torque_ratio'] for x in loads),min_admitted_grip_margin=min(x['grip_margin'] for x in loads),final_force_replay_pass=all(x['pass_'] for x in loads),force_replay_evidence='results/final_force_witnesses.json');write('results/phase_summary.json',phase)
for path in prefix['paths']:
 match=next((x for x in pathloads if x['id']==path['id'] and x['scope']=='actual_prefix'),None)
 if match:path['load_replay'].update(max_torque_ratio=match['maximum_torque_ratio'],min_grip_margin=match['minimum_grip_margin'],final_cartesian_force_box_replay='results/final_path_loads.json')
write('results/executed_prefix.json',prefix)
if a.loads_only:print('LOADS_DONE');raise SystemExit(0)
row=phase['selected_witnesses'][0];job=row['job'];loc=copy.deepcopy(job['locations']);loc[job['object_id']]=job['origin'];ch=Workcell(V,job['object_id'],loc);q=np.array(next(p['q'] for p in row['poses'] if p['label']=='retained_on_own_support'));ch.contact_windows=ch.window(job['object_id'],job['station'],job['origin']);ch.pose(q);original=copy.deepcopy(ch.contact_windows);baseline=permitted(ch);check('own_registered_support_face_works',bool(baseline))
for label,mutation in [('wrong_support',dict(support_id='dock_tomato')),('wrong_face',dict(face='wash_open_land')),('wrong_object',dict(object_id='output_tomato')),('nonworking_path',dict(kind='working_stroke')),('sideways_false_normal',dict(normal=[1,0,0]))]:
 ch.contact_windows=copy.deepcopy(original)
 for w in ch.contact_windows:w.update(mutation)
 ch.working_stroke=False;check('reject_'+label,not permitted(ch))
prov=read('audit/provenance.json')
for item in prov:
 aa=ROOT/item['source'];bb=H/item['copy'];check('immutable:'+item['copy'],aa.read_bytes()==bb.read_bytes() and hashlib.sha256(bb.read_bytes()).hexdigest()==item['sha256'])
check('every_handling_problem96_independent_starts',all(x['starts']==96 for x in phase['strokes'] if 'action' in x))
check('no_fabricated_complete_time',read('results/schedule.json')['prep_min'] is None and not prefix['meal_pass'])
check('food_conserved_in_all_actual_states',all(abs(sum(x['mass_kg'] for x in s['food'].values())-.57)<1e-9 and all(x['quality']=='raw_unwashed' for x in s['food'].values()) for s in prefix['states']))
check('every_joint_recorded',all(len(s['every_joint'])==mujoco.MjModel.from_xml_path(str(H/s['xml'])).njnt for s in prefix['states']))
check('handoffs_preserve_full_geometry',all(s.get('ownership_position_invariant_m',0)<=1e-5 and s.get('ownership_rotation_invariant',0)<=1e-5 for s in prefix['states']))
check('every_actual_path4mm',all(p['load_replay']['max_point_step_mm']<=4.00000001 for p in prefix['paths'] if p['ok']))
check('six_documented_new_layouts',read('results/exit_condition.json')['condition_b'])
cost=read('results/cost_summary.json');lines=list(csv.DictReader((H/'results/costs.csv').open(encoding='utf-8-sig')));check('one_reserve_one_safety',sum(x['id']=='A13' for x in lines)==1 and sum(x['id']=='RESERVE15' for x in lines)==1 and abs(sum(float(x['line_cny']) for x in lines)-cost['total_cny'])<1e-6 and abs(cost['reserve_cny']-.15*cost['subtotal_cny'])<1e-6)
runs=[json.loads(f.read_text()) for f in (H/'audit').glob('rescue*_run.json')];edges=[]
for r in runs:
 if 'start_monotonic_s' in r:edges += [(r['start_monotonic_s'],1),(r['end_monotonic_s'],-1)]
active=0;peak=0
for t,change in sorted(edges):active+=change;peak=max(peak,active)
check('resource_bounds',peak<=4 and all(r['timeout_s']<1200 and r['peak_process_MiB']<1900.1 and r['cpu_only'] for r in runs),dict(max_concurrent_workers=peak,runs=len(runs)))
total=sum(f.stat().st_size for f in H.rglob('*') if f.is_file());check('output_under3GB',total<3*1024**3,dict(bytes=total))
write('audit/revision2_validation.json',dict(checks=checks,report_integrity_pass=all(x['pass_'] for x in checks),workstation_acceptance_pass=False,explicit_incomplete_process_obligations=phase['processing_obligations_total'],raw96_start_cartesian_X_force_results_superseded_by_this_replay=True))
print('VALIDATION',sum(x['pass_'] for x in checks),'/',len(checks),'FAILURES',[x['name'] for x in checks if not x['pass_']])
