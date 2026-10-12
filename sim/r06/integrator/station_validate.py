"""Final selected-scene load replay and explicit contact-policy regression."""
from station_spec import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--variant',type=int,default=32);a=p.parse_args();V=a.variant;cfg=config(V)
def read(n):return json.loads((H/n).read_text())
def forcebox(h):
 h=copy.deepcopy(h);h['R']['check_forces_N']=[list(x) for x in itertools.product((-1.89,1.89),repeat=3)];h['R']['force_basis']='Cartesian box enclosing SF1.5 * 4.2kg * 0.3m/s2 carry inertia at assembly CoM';return h
phase=read('results/phase_summary.json');prefix=read('results/executed_prefix.json');loads=[];capability=[];checks=[]
def check(name,condition,detail=None):checks.append(dict(name=name,pass_=bool(condition),detail=detail))
for row in phase['obligations']:
 if not row['pass_']:continue
 job=row['job'];loc=copy.deepcopy(job['locations']);loc[job['object_id']]=job['origin'];empty=Workcell(V,None,loc);held=Workcell(V,job['object_id'],loc);empty.capture(job['object_id'],job['origin']);held.contact_windows=held.window(job['object_id'],job['station'],job['origin']);target=key_position(job['origin'],cfg)
 for pp in row['witness']['poses']:
  ch=held if pp['label'].startswith('retained_') else empty;q=np.array(pp['q']);hs=forcebox(hand(ch,target));tq,gr,cases=check_load(ch,q,hs);hits,mins,pf=contacts(ch,q)
  rr=dict(stroke=row['id'],pose=pp['label'],pass_=not hits and tq<=1 and gr>=1,torque_ratio=tq,grip_margin=gr,force_cases=cases,geometry_hits=hits[:3]);loads.append(rr);pp.update(torque_ratio=tq,grip_margin=gr,force_cases=cases,force_evidence='results/final_force_witnesses.json')
  if ch.held_id:
   heavy=copy.deepcopy(hs);heavy['R']['held_kg']=3.;t,g,cs=check_load(ch,q,heavy);capability.append(dict(stroke=row['id'],pose=pp['label'],external_payload_kg=3.,EOAT_kg=1.2,torque_ratio=t,grip_margin=g,pass_=t<=1 and g>=1,CoM_prep_m=list(ch.com)))
write('results/final_force_witnesses.json',loads);write('results/payload_capability.json',dict(challenge_kg=3,total_flange_kg=4.2,pass_=bool(capability) and all(x['pass_'] for x in capability),witnesses=capability,scope='Admitted handling witnesses; not every workspace configuration'))
check('selected_static_geometry_and_cartesian_force_box',bool(loads) and all(x['pass_'] for x in loads));check('principal_arm3kg_challenge',bool(capability) and all(x['pass_'] for x in capability))
pathloads=[]
for path in prefix['paths']:
 if not path['ok']:continue
 xml=E.fromstring((H/path['xml']).read_text());heldname=next((b.get('name')[7:] for b in xml.findall('.//body') if b.get('name','').startswith('R_held_output_')),None);locations={}
 for prod in PRODUCTS:
  b=xml.find(f".//worldbody/body[@name='output_{prod}']")
  if b is not None:locations['output_'+prod]=np.fromstring(b.get('pos'),sep=' ').tolist()
 ch=Workcell(V,heldname,locations);ch.contact_windows=path.get('contact_windows',[]);ch.capture_window=path.get('capture_window');pb=PointBound(ch);hs=forcebox(hand(ch,ch.pose(np.array(path['path'][0]))[0]));mx=0;mn=1e30;count=0;maxstep=0
 for aa,bb in zip(path['path'],path['path'][1:]):
  aa=np.array(aa);bb=np.array(bb);bound=pb.segment_bound(aa,bb);steps=max(1,math.ceil(bound/.004));maxstep=max(maxstep,bound/steps*1000)
  for k in range(steps+1):
   q=aa+(bb-aa)*k/steps;t,g,cases=check_load(ch,q,hs);mx=max(mx,t);mn=min(mn,g);count+=1
 rr=dict(id=path['id'],states=count,pass_=mx<=1 and mn>=1 and maxstep<=4.00000001,maximum_torque_ratio=mx,minimum_grip_margin=mn,max_robot_point_step_mm=maxstep,max_appliance_point_step_mm=path.get('max_appliance_point_step_mm'),force_box_N=[-1.89,1.89],source_geometry_sha256=hashlib.sha256((H/path['xml']).read_bytes()).hexdigest());pathloads.append(rr);path['load_replay'].update(max_torque_ratio=mx,min_grip_margin=mn,final_cartesian_force_box_replay='results/final_path_loads.json');print('LOAD',path['id'],count,mx,mn,flush=True)
write('results/final_path_loads.json',pathloads);check('every_accepted_path_cartesian_force_box',all(x['pass_'] for x in pathloads))
phase.update(max_admitted_torque_ratio=max(x['torque_ratio'] for x in loads),min_admitted_grip_margin=min(x['grip_margin'] for x in loads),final_force_replay_pass=all(x['pass_'] for x in loads),force_replay_evidence='results/final_force_witnesses.json');write('results/phase_summary.json',phase);write('results/executed_prefix.json',prefix)
motion=read('results/motion.json');motion['paths']=prefix['paths'];write('results/motion.json',motion)
row=next(r for r in phase['obligations'] if r['pass_']);job=row['job'];loc=copy.deepcopy(job['locations']);loc[job['object_id']]=job['origin'];ch=Workcell(V,job['object_id'],loc);q=np.array(next(p['q'] for p in row['witness']['poses'] if p['label']=='retained_on_own_support'));ch.contact_windows=ch.window(job['object_id'],job['station'],job['origin']);ch.pose(q);original=copy.deepcopy(ch.contact_windows);baseline=permitted(ch);check('own_registered_support_face_works',bool(baseline))
for label,mutation in [('wrong_support',dict(support_id='dock_tomato')),('wrong_face',dict(face='wash_open_land')),('wrong_object',dict(object_id='output_tomato')),('nonworking_path',dict(kind='working_stroke')),('sideways_false_normal',dict(normal=[1,0,0]))]:
 ch.contact_windows=copy.deepcopy(original)
 for w in ch.contact_windows:w.update(mutation)
 ch.working_stroke=False;check('reject_'+label,not permitted(ch))
write('audit/revision3_load_validation.json',dict(checks=checks,pass_=all(x['pass_'] for x in checks),workstation_acceptance_pass=False));print('VALIDATE',sum(x['pass_'] for x in checks),'/',len(checks))
