"""Independent R08 review. Read integrator; write only reviewer artifacts.

Run modes through reviewer/bounded.py. Synthetic adversarial probes never count
as robot motion. No random feasibility search, model edits, or upstream writes.
"""
import os,sys,json,copy,hashlib,difflib,inspect,math,time,csv
from pathlib import Path
import xml.etree.ElementTree as E
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
HERE=Path(__file__).resolve().parent
IN=HERE.parent/'integrator';ROOT=HERE.parents[2]
sys.path.insert(0,str(IN))
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
import scene,checker,verify,state,execute,planner
from checker import Checker,reference
CFG=scene.load('results/selected.json')['config']
def save(name,value):
 p=HERE/'results'/name;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(value,indent=2,allow_nan=False,default=lambda v:v.tolist() if isinstance(v,np.ndarray) else v.item()),encoding='utf-8')
def make(held=None):
 tr,meta=scene.build(CFG,held);return Checker(tr,meta),meta
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rules():
 verify.save=lambda name,value:save('submitted_regression.json',value)
 verify.main()
 diffdir=HERE/'diffs';diffdir.mkdir(exist_ok=True)
 src=ROOT/'sim/r05/integrator/reference.py'
 imported=Path(reference.__file__)
 (diffdir/'reference_import.diff').write_text(''.join(difflib.unified_diff(src.read_text().splitlines(True),imported.read_text().splitlines(True),fromfile=str(src),tofile=str(imported))),encoding='utf-8')
 import ast
 node=next(n for n in ast.parse(src.read_text()).body if isinstance(n,ast.ClassDef) and n.name=='Checker')
 old_class=src.read_text().splitlines(True)[node.lineno-1:node.end_lineno]
 (diffdir/'reference_class_vs_wrapper.diff').write_text(''.join(difflib.unified_diff(old_class,inspect.getsource(Checker).splitlines(True),fromfile='R05 Checker',tofile='R08 adapter')),encoding='utf-8')
 copied={}
 for n in ('distance.py','point_bound.py'):
  a=ROOT/'sim/r07/integrator'/n;b=IN/n
  copied[n]=dict(equal=a.read_bytes()==b.read_bytes(),sha256=sha(b))
  (diffdir/(n+'.diff')).write_text(''.join(difflib.unified_diff(a.read_text().splitlines(True),b.read_text().splitlines(True),fromfile=str(a),tofile=str(b))),encoding='utf-8')
 ch,meta=make();source=E.parse(ROOT/'sim/r07/integrator/models/L101_reach_R_v7.xml');new=E.parse(IN/'models/base.xml')
 for tr in (source,new):
  for mesh in tr.findall('.//mesh'):mesh.set('file',Path(mesh.get('file')).name)
 def canon(tr):
  return [(e.tag,dict(e.attrib)) for e in tr.iter()]
 geometry=dict(base_matches_L101=canon(source)==canon(new),processor_geoms=[n for n in ch.gnames if 'bfp' in n.lower() or 'processor' in n.lower()],sweep_geoms=[n for n in ch.gnames if 'sweep' in n.lower()],closed_leaves=[n for n in ch.gnames if n.startswith('r07_closed')])
 old=json.loads((ROOT/'sim/r07/integrator/results/layouts/L101_process_v7.json').read_text())
 contract=scene.load('assets/process_contract.json')
 save('rules.json',dict(reference_sha256=sha(src),imported_path=str(imported),reference_diff_empty=src.read_bytes()==imported.read_bytes(),copied=copied,geometry=geometry,contract_equal={k:contract[k]==old[k] for k in contract},constants={k:getattr(reference,k) for k in ('PAD','MU','SF','NORMAL_SUM_N','KEY_FORCE_N','KEY_MOMENT_NM')},wrapper_overrides=[n for n in Checker.__dict__ if callable(getattr(Checker,n))]))

def probes():
 rows=[]
 def record(name,expected_reject,accepted,detail=None):rows.append(dict(name=name,expected_reject=expected_reject,accepted=bool(accepted),pass_=bool(accepted)!=expected_reject,detail=detail))
 ch,meta=make('holder');t=scene.targets(CFG,meta)[6];R=reference.rotation([0,0,-1],[0,1,0]);ch.configure_target(t,R)
 sid=ch.m.site('R_prep').id;ch.d.site_xpos[sid]=t['points'][0];ch.d.site_xmat[sid]=R.ravel();original=copy.deepcopy(ch.windows)
 record('genuine_work_capability',False,bool(ch.permissions('working')))
 record('working_permission_on_transfer',True,bool(ch.permissions('transfer')))
 for name,key,value in [('wrong_object','object','tomato'),('wrong_support','support','wash_basket'),('wrong_part','parts',['R_held_carrot']),('missing_kind','kind',None),('wrong_origin','origin',[9,9,9]),('overlong_work','length_m',.25)]:
  ch.windows=copy.deepcopy(original)
  for w in ch.windows:w[key]=value
  record(name,True,bool(ch.permissions('working')))
 ch.windows=copy.deepcopy(original);g=ch.gnames.index('mandoline_deck');ch.d.geom_xpos[g,0]+=.001
 record('support_moved_after_registration',True,bool(ch.permissions('working')))
 ch,meta=make('holder');t=scene.targets(CFG,meta)[7];ch.configure_target(t,R);sid=ch.m.site('R_prep').id
 for distance in (0,.049,.051,.07):
  ch.d.site_xpos[sid]=np.array(t['points'][0])+[0,0,distance];ch.d.site_xmat[sid]=R.ravel()
  record('lift_at_'+str(distance)+'m',distance>.05,bool(ch.permissions('transfer')))
 ch,meta=make('carrot');g=ch.gnames.index('R_held_carrot');f=ch.gnames.index('R_finger_minus')
 record('real_carrot_grasp',False,ch.grasp_allowed(g,f))
 quat=ch.m.geom_quat[g].copy();ch.m.geom_quat[g]=Rotation.from_euler('y',90,degrees=True).as_quat()[[3,0,1,2]];mujoco.mj_forward(ch.m,ch.d)
 record('carrot_local_rotation_changed',True,ch.grasp_allowed(g,f),dict(original_quat=quat,new_quat=ch.m.geom_quat[g].copy(),identity_omits_geom_quat=True))
 ch.m.geom_quat[g]=quat;ch.m.geom_pos[g,0]+=.001
 record('carrot_local_position_changed',True,ch.grasp_allowed(g,f))
 # Recompile a forged tray part. Registry is minted from the submitted model,
 # rather than checked against the actual full tray part specification.
 tr,meta=scene.build(CFG,'catch_tray');tr.find(".//geom[@name='R_held_tray_floor']").set('size','.3 .3 .3');cc=Checker(tr,meta)
 record('forged_tray_shape_at_construction',True,cc.grasp_allowed(cc.gnames.index('R_held_tray_floor'),cc.gnames.index('R_finger_minus')))
 # A correct held part translated in world data must not keep stale capability.
 ch,meta=make('carrot');g=ch.gnames.index('R_held_carrot');f=ch.gnames.index('R_finger_minus');ch.d.geom_xpos[g,0]+=1
 record('stale_world_frame_capability',True,ch.grasp_allowed(g,f), 'Capability-level query; full check refreshes FK, so not itself a replay bypass.')
 # Independent public API transformation probes, all with rollback checks.
 sr=[]
 def transform_probe(label,mutate,args,should_reject=True):
  w=state.World();mutate(w);before=w.snapshot()
  try:w.transform(*args(w));accepted=True;err=None
  except (ValueError,KeyError) as e:accepted=False;err=str(e)
  sr.append(dict(name=label,accepted=accepted,pass_=accepted!=should_reject,rollback=not accepted and before==w.snapshot(),error=err,after=w.snapshot() if accepted else None))
 def located(w,station='mandoline'):
  w.objects['carrot'].update(pos=np.mean(w.regions[station]['input'],axis=0).tolist(),support=station)
 transform_probe('contained_carrot_slices',lambda w:located(w),lambda w:('carrot','slices','mandoline',w.regions['mandoline']['input'],1,.9),False)
 transform_probe('foreign_support',lambda w:None,lambda w:('carrot','slices','mandoline',w.regions['mandoline']['input'],1))
 transform_probe('remote_input',lambda w:w.objects['carrot'].update(pos=[9,9,9],support='mandoline'),lambda w:('carrot','slices','mandoline',w.regions['mandoline']['input'],1))
 transform_probe('partial_input_outside',lambda w:(located(w),w.objects['carrot'].update(pos=(np.mean(w.regions['mandoline']['input'],axis=0)+[.18,0,0]).tolist())),lambda w:('carrot','slices','mandoline',w.regions['mandoline']['input'],1))
 transform_probe('attached_input',lambda w:(located(w),w.objects['carrot'].update(attached=True)),lambda w:('carrot','slices','mandoline',w.regions['mandoline']['input'],1))
 transform_probe('forged_region_argument',lambda w:located(w),lambda w:('carrot','slices','mandoline',[[8,8,8],[10,10,10]],1))
 transform_probe('bulk_capacity_overflow',lambda w:located(w),lambda w:('carrot','slices','mandoline',w.regions['mandoline']['input'],1,1,.00001))
 transform_probe('peeler_wrong_operation_wedges',lambda w:located(w,'peeler'),lambda w:('carrot','wedges','peeler',w.regions['peeler']['input'],1))
 transform_probe('mandoline_wrong_operation_peeled',lambda w:located(w),lambda w:('carrot','peeled','mandoline',w.regions['mandoline']['input'],1,.9))
 # NaN and None are separately relevant: None is allowed for unknown duration,
 # but NaN is neither an appliance duration nor a schedulable unknown.
 w=state.World();w.attach('carrot',w.objects['carrot']['pos']);w.commit_path('carrot',{'ok':True,'path':[[0]]},[[9,9,9]])
 commit=dict(accepted=w.executed_connections==1,pos=w.objects['carrot']['pos'],supplied_joint_path=[[0]],no_checker_receipt=True)
 save('negative_probes.json',dict(contact=rows,transform=sr,forged_commit=commit,scope='Synthetic API/capability probes only. No robot execution or accepted saved witness is created.'))

def statics():
 ch,meta=make();ts=scene.targets(CFG,meta);rows=[]
 for i,t in enumerate(ts):
  cc,cm=make(t['held']);row=scene.load(f'results/strokes/{i}.json');er=[]
  for k,e in enumerate(row['endpoints']):
   b=e['best']
   if 'q' not in b:er.append(dict(endpoint=k,available=False,ok=False));continue
   # Failed candidates retain their start index but not rotation. Reconstruct
   # exactly the solver's four jaw orientations; no fresh pose search.
   if 'rotation' in b:R=np.array(b['rotation'])
   else:
    jaws=[(0,0,1),(0,0,-1),(1,0,0),(-1,0,0)] if abs(t['approach'][1])>.9 else [(0,1,0),(0,-1,0),(1,0,0),(-1,0,0)]
    R=reference.rotation(t['approach'],jaws[b['start']%4])
   cc.configure_target(t,R);q=np.array(b['q']);check=cc.check(q,kind=t['kind'],mass=execute.mass(t),force=t['force']);pe,re=cc.pose_error(q,t['points'][k],R)
   good=bool(check['ok'] and pe<=.005 and re<=math.radians(3))
   er.append(dict(endpoint=k,available=True,ok=good,submitted_ok=e['ok'],match=good==e['ok'],position_mm=pe*1000,orientation_deg=np.degrees(re),rotation=R,q=q,check=check))
  rows.append(dict(index=i,name=t['name'],static_ok=all(e['ok'] for e in er),endpoints=er))
  save('statics.json',dict(rows=rows,strokes_passed=sum(r['static_ok'] for r in rows),strokes_total=len(ts)))
  print('replayed',i,t['name'],[e['ok'] for e in er],flush=True)

def paths():
 cc,meta=make('carrot');ts=scene.targets(CFG,meta);row=scene.load('results/strokes/5.json');b=row['endpoints'][0]['best'];record=[];original=execute.edge
 # Capture the deterministic continuation's actual accepted/rejected states.
 def logged(ch,a,z,deadline,**kw):
  e=original(ch,a,z,deadline,**kw);record.append(dict(start=np.array(a),end=np.array(z),result=e));return e
 execute.edge=logged
 result=execute.continuation(cc,ts[5],b['q'],np.array(b['rotation']),budget=180)
 execute.edge=original
 # Recheck captured prefix with an independent global ancestry bound (the
 # integrator edge uses the tighter local bound). Interpolate to <=4mm globally.
 checked=0;maxstep=0;rejections=[];prefix=[]
 for leg in record:
  e=leg['result']
  if not e['ok']:break
  for a,z in zip(e['path'][:-1],e['path'][1:]):
   a=np.array(a);z=np.array(z);bound=cc.point_bound.bound(z-a);n=max(1,math.ceil(bound/.004));maxstep=max(maxstep,bound/n)
   for j in range(n+1):
    q=a+(z-a)*j/n;r=cc.check(q,kind=ts[5]['kind'],mass=.12)
    checked+=1;prefix.append(dict(q=q,clearance=r['clearance']))
    if not r['ok']:rejections.append(dict(sample=checked,result=r))
 save('internal_prefix.json',dict(continuation=result,segments=record,independent_global_bound_step_m=maxstep,independent_states=checked,rejections=rejections,prefix=prefix,complete_path=False))
 # No connection/fold path exists. Recheck the exact saved rejected states and
 # inspect every result, without pretending absent motion can be replayed.
 out=[]
 for i in range(10):
  row=scene.load(f'results/connections/{i}.json');p=row['planner'];cc,_=make(ts[i]['held']);rejection=p.get('rejection',{});q=rejection.get('q')
  r=cc.check(np.array(q),mass=execute.mass(ts[i])) if q is not None else None
  out.append(dict(index=i,path_present='path' in p,submitted_geometric_ok=p['ok'],executed=row['executed'],budget_s=p['budget_s'],elapsed_s=p['elapsed_s'],restarts=p['restarts'],nodes=p['nodes'],saved_rejected_state=q,reproduced_rejection=r is not None and not r['ok'],check=r))
 idle=scene.load('results/idle.json');fold={}
 for name in ('fold','unfold'):
  p=idle[name];q=p.get('rejection',{}).get('q');cc,_=make();r=cc.check(np.array(q)) if q is not None else None
  fold[name]=dict(path_present='path' in p,submitted_ok=p['ok'],budget_s=p['budget_s'],elapsed_s=p['elapsed_s'],reproduced_rejection=r is not None and not r['ok'],check=r)
 save('paths.json',dict(connections=out,fold_unfold=fold,completed_products=[],complete_carrot_replay_possible=False,reason='All ten connections and both idle routes have no saved path; all internal strokes failed. No end-to-end witness exists.'))
 print('paths complete',checked,'prefix states; full route absent',flush=True)

def engineering():
 ch,meta=make();park=np.array(scene.load('assets/park.json')['q']);check=ch.check(park)
 ext=[]
 for g,n in enumerate(ch.gnames):
  if ch.m.geom_type[g]==0:continue
  lo=np.array([ch.bounds.support(g,-a)[k] for k,a in enumerate(np.eye(3))]);hi=np.array([ch.bounds.support(g,a)[k] for k,a in enumerate(np.eye(3))]);ext.append(dict(g=g,name=n,lo=lo,hi=hi))
 robot=[e for e in ext if ch.robot[e['g']] or e['name'].startswith('door_pause_sensor')]
 hits=[];min_door=100
 for e in robot:
  lo,hi=e['lo'],e['hi'];sensor=e['name'].startswith('door_pause_sensor');gap=lo[1]-.23 if sensor else 1.35-hi[2];min_door=min(min_door,gap)
  strip=hi[0]>-1.8 and lo[0]<1.8 and hi[1]>0 and lo[1]<.23 and hi[2]>.85 and lo[2]<1.35
  corridor=hi[0]>-1.6 and lo[0]<.6 and hi[1]>-.75 and lo[1]<-.05 and hi[2]>.85 and lo[2]<1.85
  if gap<.01-1e-8 or strip or corridor:hits.append(dict(name=e['name'],gap=gap,strip=strip,corridor=corridor))
 # Reconstruct basket axis from compiled body, not the metadata assertion.
 bid=ch.m.body('wash_basket').id;R=ch.d.xmat[bid].reshape(3,3);mouth=ch.d.xpos[bid]+R@np.array([0,0,.14]);normal=R[:,2];jet=np.array(meta['jet']);direction=np.array([0,0,-1]);travel=(mouth-jet)@normal/(direction@normal);hit=jet+travel*direction
 tops={}
 for e in ext:
  b=int(ch.m.geom_bodyid[e['g']])
  while ch.m.body_parentid[b]:b=int(ch.m.body_parentid[b])
  name=ch.m.body(b).name
  if name and name.startswith(('mandoline_station','peeler_station','greens_station','tomato_station','stored_bowl')):tops[name]=max(tops.get(name,0),e['hi'][2])
 # Check vertical jet against FULL carrot target solids. The nominal target
 # has fixed orientation; pose tolerance cannot be replaced by spray spread.
 t=scene.targets(CFG,meta)[2];water=[]
 for k,p in enumerate(t['points']):
  for jaw in ((0,1,0),(0,-1,0),(1,0,0),(-1,0,0)):
   rr=reference.rotation(t['approach'],jaw);half=np.array([.0175,.0175,.08]);p=np.array(p);a=rr.T@(jet-p);v=rr.T@direction;low=0.;high=float('inf')
   for axis in range(3):
    if abs(v[axis])<1e-9:
     if abs(a[axis])>half[axis]:high=-1;break
    else:
     x,y=sorted(((-half[axis]-a[axis])/v[axis],(half[axis]-a[axis])/v[axis]));low=max(low,x);high=min(high,y)
   water.append(dict(endpoint=k,jaw=jaw,jet_intersects_carrot=bool(high>=low),carrot_center=p))
 # World region versus actual hollow catch tray; audit outputs and aggregate
 # occupancy after a legal synthetic transform with edible+scrap split.
 w=state.World();o=w.objects['carrot'];o.update(pos=np.mean(w.regions['mandoline']['input'],axis=0).tolist(),support='mandoline');w.transform('carrot','slices','mandoline',w.regions['mandoline']['input'],1,.9)
 a=w.objects['carrot'];b=w.objects['carrot:scrap:mandoline'];overlap=np.minimum(np.array(a['pos'])+np.array(a['size'])/2,np.array(b['pos'])+np.array(b['size'])/2)-np.maximum(np.array(a['pos'])-np.array(a['size'])/2,np.array(b['pos'])-np.array(b['size'])/2)
 costs=list(csv.DictReader((IN/'results/costs.csv').open(encoding='utf-8')));base=sum(float(r['total_cny']) for r in costs if not r['item'].startswith(('ONE 15%','TOTAL')))
 save('engineering.json',dict(park_snapshot=dict(pass_=bool(check['ok'] and not hits),check=check,hits=hits,min_sweep_separation_mm=min_door*1000,robot_inventory=len(robot)),station_tops_m=tops,wash=dict(compiled_mouth=mouth,compiled_normal=normal,declared_jet=jet,ray_travel_m=travel,radial_error_mm=float(np.linalg.norm(hit-mouth)*1000),jet_hits_mouth=bool(travel>=0 and np.linalg.norm(hit-mouth)<.118),nominal_work_targets=water,tilted_basket_supported=False),contained_bulk_overlap=dict(overlap_dimensions_m=overlap,positive_overlap=bool(np.all(overlap>0)),carrot=a,scrap=b),cost=dict(base_cny=base,reserve_cny=base*.15,total_cny=base*1.15),peeling_allowance_per_root_s=6*2*.160/.0034/.20,prep_min=None))
 print('engineering snapshot',check['ok'] and not hits,'jet error mm',np.linalg.norm(hit-mouth)*1000,'cost',base*1.15,flush=True)

def supplemental():
 static=json.loads((HERE/'results/statics.json').read_text());prefix=json.loads((HERE/'results/internal_prefix.json').read_text());path=json.loads((HERE/'results/paths.json').read_text())
 diagnostics=[]
 for label,held,q,result in [('holder_load_rejection','carrot',prefix['continuation']['rejection']['q'],prefix['continuation']['rejection']['rejection']),('unfold_rejection',None,scene.load('results/idle.json')['unfold']['rejection']['q'],path['fold_unfold']['unfold']['check'])]:
  ch,_=make(held);ch.check(np.array(q),mass=.12 if held else 0)
  for h in result['hits'][:3]:
   a,b=[ch.gnames.index(n) for n in h['pair']];p=ch.bounds.pair(a,b)
   diagnostics.append(dict(label=label,pair=h['pair'],reported_native_gap_mm=h['real_gap_mm'],required_mm=h['required_gap_mm'],independent_convex=p))
 # Separate finite-difference Jacobians for gravity/payload/process force.
 loads=[]
 for row in static['rows']:
  for e in row['endpoints']:
   if not e['ok']:continue
   t=scene.load(f"results/strokes/{row['index']}.json")['target'];ch,_=make(t['held']);q=np.array(e['q']);sid=ch.m.site('R_prep').id
   work=np.array(e['check']['load']['work_local_m']);com=np.array(e['check']['load']['held_com_local_m']);mass=execute.mass(t)
   for force in e['check']['load']['force_cases_N']:
    force=np.array(force);ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);tau=ch.d.qfrc_bias.copy();dp=[]
    for name in checker.ENV:
     adr=ch.qa[name];eps=1e-6;coords=[]
     for sign in (-1,1):
      ch.d.qpos[:]=q;ch.d.qpos[adr]+=sign*eps;mujoco.mj_kinematics(ch.m,ch.d);r=ch.d.site_xmat[sid].reshape(3,3);p=ch.d.site_xpos[sid];coords.append((p+r@work,p+r@com))
     dw=(coords[1][0]-coords[0][0])/(2*eps);dc=(coords[1][1]-coords[0][1])/(2*eps);j=ch.da[name]
     tau[j]-=dw@force+dc@np.array([0,0,-mass*9.81])
    direct=ch.loads(q,force,mass,.08);ratios={n:abs(tau[ch.da[n]])/v for n,v in checker.ENV.items()}
    loads.append(dict(stroke=row['index'],endpoint=e['endpoint'],force_N=force,max_ratio=max(ratios.values()),max_ratio_difference=max(abs(ratios[n]-direct['ratios'][n]) for n in ratios)))
 # Re-evaluate six retained rated-payload witnesses with full EOAT removed
 # analytically, then add the manufacturer's complete 5kg flange payload.
 ch,_=make();env=scene.load('assets/envelope.json');witnesses=[]
 for name,w in env['witnesses'].items():
  q=ch.m.qpos0.copy()
  for n,x in zip(checker.ENV,w['joints_rad']):q[ch.qa[n]]=x
  ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);tau=ch.d.qfrc_bias.copy();jp=np.zeros((3,ch.m.nv));jr=jp.copy()
  for bn in ('R_tool','R_jaw_minus','R_jaw_plus'):
   bid=ch.m.body(bn).id;mujoco.mj_jac(ch.m,ch.d,jp,jr,ch.d.xipos[bid],bid)
   tau+=jp.T@np.array([0,0,-ch.m.body_mass[bid]*9.81])
  sid=ch.m.site('R_attachment_site').id;r=ch.d.site_xmat[sid].reshape(3,3);p=ch.d.site_xpos[sid]+r@np.array(w['CoM_flange_m']);mujoco.mj_jac(ch.m,ch.d,jp,jr,p,ch.m.site_bodyid[sid]);tau-=jp.T@np.array([0,0,-5*9.81])
  val=abs(tau[ch.da[name]]);witnesses.append(dict(joint=name,recomputed_Nm=val,stored_Nm=w['static_Nm'],difference_Nm=val-w['static_Nm'],com_radius_m=float(np.linalg.norm(w['CoM_flange_m']))))
 # Deduplicated accepted diagnostic prefix samples; separate from endpoint
 # and park distributions so sample counts cannot masquerade as execution.
 unique={tuple(np.round(r['q'],12)):r for r in prefix['prefix']};dist={};under=[]
 for category in ('robot_environment','held_gripper_environment','arm_arm_or_frame','self'):
  vals=[r['clearance'][category]['reserve_mm'] for r in unique.values()];dist[category]=dict(states=len(vals),minimum_mm=min(vals),p05_mm=float(np.percentile(vals,5)),fraction_ge10=float(np.mean(np.array(vals)>=10-1e-8)))
  for k,r in enumerate(unique.values()):
   if r['clearance'][category]['reserve_mm']<2:under.append(dict(sample=k,category=category,detail=r['clearance'][category]))
 save('supplemental.json',dict(distance_disagreement=diagnostics,finite_difference_loads=loads,rated_payload_witnesses=witnesses,accepted_prefix_distribution=dist,prefix_under2mm=under,all_prefix_checks_passed=not prefix['rejections']))
 print('supplemental max load error',max(r['max_ratio_difference'] for r in loads),'max envelope error',max(abs(r['difference_Nm']) for r in witnesses),flush=True)

def idle_replay():
 idle=scene.load('results/idle.json');ch,_=make();out={}
 first=scene.load('results/strokes/0.json');last=scene.load('results/strokes/10.json')
 park=np.array(idle['park_q'])
 for name,a,b in [('unfold',park,execute.diagnostic_q(first['endpoints'][0])),('fold',execute.diagnostic_q(last['endpoints'][-1]),park)]:
  # Full direct route is proposed, then replay stops at its first rejection.
  # This is the same recorded attempt, not a newly planned route or a pass.
  bound=ch.point_bound.segment_bound(a,b);n=max(1,math.ceil(bound/.004));states=[]
  for j in range(n+1):
   q=a+(b-a)*j/n;r=ch.check(q)
   states.append(dict(sample=j,q=q,ok=r['ok'],clearance=r['clearance'],hits=r['hits']))
   if not r['ok']:break
  # Independent, more conservative subdivision of the replayed portion.
  maxstep=0;extra=0;invalid=[]
  for left,right in zip(states[:-1],states[1:]):
   qa=np.array(left['q']);qb=np.array(right['q']);nb=max(1,math.ceil(ch.point_bound.bound(qb-qa)/.004));maxstep=max(maxstep,ch.point_bound.bound(qb-qa)/nb)
   for k in range(1,nb):
    result=ch.check(qa+(qb-qa)*k/nb);extra+=1
    if not result['ok']:invalid.append(dict(left_sample=left['sample'],substep=k,hits=result['hits']))
  out[name]=dict(complete=False,recorded_samples=idle[name]['rejection']['checked'],replayed_samples=len(states),samples=states,original_step_bound_m=bound/n,independent_max_step_m=maxstep,extra_samples=extra,extra_rejections=invalid)
 save('idle_replay.json',out)
 print('idle direct replay',[(k,v['replayed_samples'],v['extra_samples']) for k,v in out.items()],flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
