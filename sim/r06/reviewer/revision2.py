"""Read-only independent second-delivery audit; run through bounded_v2.py."""
import os,sys,json,math,copy,hashlib,difflib,csv,itertools,types
from pathlib import Path
import numpy as np
import mujoco
from scipy.spatial.transform import Rotation
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2];UP=ROOT/'sim/r06/integrator';OUT=HERE/'v2';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(UP))
import rescue_cell as rc
# Reuse the reviewer's independently implemented pair policy, load equations
# and serial-chain displacement bound, not the integrator's acceptance code.
base=types.ModuleType('review_helpers');base.__file__=str(HERE/'review.py')
helper_source=(HERE/'review.py').read_text().split('ap=argparse.ArgumentParser()')[0]
# Free pan bodies are stationary in each saved connection; their coordinates
# are asserted constant below. Include their moving hinge/slide descendants.
helper_source=helper_source.replace("else:raise ValueError('Moving free/ball robot requires separate proof')","elif typ in (0,1):pass")
exec(compile(helper_source,base.__file__,'exec'),base.__dict__)
base.SUPPORTS={'wash_basin':{'wash_open_land'},'process_cell':{'process_open_land'}}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,d):(OUT/(n+'.json')).write_text(json.dumps(d,indent=2,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else x.item() if isinstance(x,np.generic) else str(x)),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
PH=read(UP/'results/phase_summary.json');PRE=read(UP/'results/executed_prefix.json');V=17
def from_xml(p):
 root=rc.E.fromstring((UP/p['xml']).read_text());held=next((b.get('name')[7:] for b in root.findall('.//body') if b.get('name','').startswith('R_held_output_')),None)
 loc={b.get('name'):np.fromstring(b.get('pos'),sep=' ').tolist() for b in root.findall('./worldbody/body') if b.get('name','').startswith('output_')}
 ch=rc.Workcell(V,held,loc)
 # Rebuilt full model must match saved collision geometry, joints and inertia.
 saved=mujoco.MjModel.from_xml_path(str(UP/p['xml']))
 for attr in ('geom_size','geom_pos','geom_quat','geom_type','body_pos','body_quat','body_mass','body_inertia','jnt_range','jnt_axis'):
  assert np.array_equal(getattr(ch.m,attr),getattr(saved,attr)),(p.get('id'),attr)
 ch.contact_windows=p.get('contact_windows',[]) if not p.get('mechanism_evidence') else []
 ch.capture_window=p.get('capture_window');return ch
def force(ch,q,heavy=False):
 hs=rc.hand(ch,ch.pose(q)[0]);hs['R']['check_forces_N']=[list(x) for x in itertools.product((-1.89,1.89),repeat=3)]
 if heavy:hs['R']['held_kg']=3.
 return hs
class AllBound(base.IndependentBound):
 def __init__(self,ch):
  mask=ch.robot.copy();ch.robot[:]=True
  try:super().__init__(ch)
  finally:ch.robot[:]=mask
def replay(ch,path,mechanism=None,save_samples=False):
 pb=AllBound(ch);count=0;maxstep=0.;res=[];ratio=0.;grip=1e30;failure=None;length=0.;bounddiff=0.;maxobserved=0.
 for si,(aa,bb) in enumerate(zip(path,path[1:])):
  aa=np.array(aa);bb=np.array(bb);bound=pb.segment(aa,bb);length+=bound;n=max(1,math.ceil(bound/.004));maxstep=max(maxstep,bound/n)
  for j in range(ch.m.njnt):
   if ch.m.jnt_type[j] in (0,1):
    adr=ch.m.jnt_qposadr[j];width=7 if ch.m.jnt_type[j]==0 else 4
    assert np.array_equal(aa[adr:adr+width],bb[adr:adr+width]),'Moving free body needs a separate bound'
  if not mechanism:bounddiff=max(bounddiff,abs(bound-rc.PointBound(ch).segment_bound(aa,bb)))
  prevpoints=None
  for k in range(n+1):
   q=aa+(bb-aa)*k/n;hits,mins,mismatch=base.gaps(ch,q);count+=1
   # FK centers provide a secondary sanity check, not the full surface bound.
   points=ch.d.geom_xpos.copy()
   if prevpoints is not None:maxobserved=max(maxobserved,float(np.max(np.linalg.norm(points-prevpoints,axis=1)))*1000)
   prevpoints=points
   tq,gr,_=base.loads(ch,q,force(ch,q));ratio=max(ratio,tq);grip=min(grip,gr)
   res.append(min((v['reserve_mm'] for cat,v in mins.items() if cat!='self'),default=0))
   physical=physical_hits(ch,mechanism,q) if mechanism else []
   if hits or mismatch or tq>1 or gr<1 or physical:
    failure=dict(segment=si,sample=k,q=q.tolist(),robot_hits=hits[:4],permission_mismatch=mismatch,physical_hits=physical[:4]);break
  if failure:break
 return dict(pass_=failure is None,states_checked=count,max_point_step_mm=maxstep*1000,max_FK_center_step_mm=maxobserved,total_displacement_bound_m=length,integrator_bound_disagreement_m=bounddiff,minimum_reserve_mm=min(res) if res else None,reserve_percentiles_mm={str(p):float(np.percentile(res,p)) for p in (0,5,25,50,75,95,100)} if res else {},fraction_ge10=sum(x>=10-1e-5 for x in res)/len(res) if res else None,max_torque_ratio=ratio,min_grip_margin=grip,first_failure=failure,**({'reserve_samples_mm':res} if save_samples else {}))
def physical_hits(ch,row,q):
 if row is None:return []
 m,d=ch.m,ch.d;j=m.joint(row['joint']).id;body=int(m.jnt_bodyid[j]);moving=[]
 for g in range(m.ngeom):
  b=int(m.geom_bodyid[g])
  while b:
   if b==body:moving.append(g);break
   b=int(m.body_parentid[b])
 bad=[];w=row.get('contact_window');mujoco.mj_forward(m,d)
 for g in moving:
  for h in range(m.ngeom):
   if h in moving or ch.robot[h] or ch.weld[g]==ch.weld[h]:continue
   if np.linalg.norm(d.geom_xpos[g]-d.geom_xpos[h])>m.geom_rbound[g]+m.geom_rbound[h]+.001:continue
   dist=mujoco.mj_geomDistance(m,d,g,h,.002,None)
   if dist>=-1e-6 or ch.bounds.pair(g,h)['lower_m']>1e-6:continue
   names={ch.gnames[g],ch.gnames[h]};allow=False
   if w and row['kind'] in ('grasp_release_support','working_stroke'):
    ident={'wash_retainer':('wash_retention_shoe','pan_carrot_right','output_carrot'),'process_retainer':('process_retention_shoe','pan_carrot_right','output_carrot'),'process_pusher':('process_pusher_plate','food_carrot','food_carrot'),'process_blade':('process_blade_full','food_carrot','food_carrot')}.get(w.get('support_id'))
    if ident and (w.get('tool_face'),w.get('object_face'),w.get('object_id'))==ident and names==set(ident[:2]) and np.allclose(w['axis'],m.jnt_axis[j]):
     travel=float(q[ch.qa[row['joint']]]-w['axis_origin_q'])
     allow=(-1e-6<=travel<=.05+1e-9) if row['kind']=='working_stroke' else (abs(q[ch.qa[row['joint']]]-row['start'])<=.05+1e-9 and abs(dist)<1e-5)
   if not allow:bad.append(dict(pair=sorted(names),signed_gap_mm=dist*1000))
 return bad
def statics():
 rows=[];stroke=[];selected={'T01_grasp','T01_release','T04_grasp','T04_release','T08_grasp','T08_release','T11_grasp','T11_release'}
 for r in PH['selected_witnesses']:
  job=r['job'];loc=copy.deepcopy(job['locations']);loc[job['object_id']]=job['origin'];empty=rc.Workcell(V,None,loc);held=rc.Workcell(V,job['object_id'],loc);empty.capture(job['object_id'],job['origin']);held.contact_windows=held.window(job['object_id'],job['station'],job['origin']);poses=[]
  for p in r['poses']:
   ch=held if p['label'].startswith('retained_') else empty;q=np.array(p['q']);pos,rot=ch.pose(q);target=rc.key_position(job['origin'],ch.cfg)+(np.array([0,0,.08]) if 'above_support' in p['label'] else 0)
   pe=float(np.linalg.norm(pos-target)*1000);oe=float(np.linalg.norm(Rotation.from_matrix(ch.rot.T@rot).as_rotvec())*180/math.pi);hits,mins,mm=base.gaps(ch,q);tq,gr,_=base.loads(ch,q,force(ch,q));payload=1.2+force(ch,q)['R']['held_kg']<=5 and np.linalg.norm(ch.com)+.09<=.35
   heavy=base.loads(ch,q,force(ch,q,True))[:2] if ch.held_id else None
   poses.append(dict(label=p['label'],pass_=pe<=5 and oe<=3 and not hits and not mm and tq<=1 and gr>=1 and payload,pose_mm=pe,pose_deg=oe,hits=hits[:3],policy_mismatch=mm,torque_ratio=tq,grip_margin=gr,heavy3kg=heavy,reserve_mm=min(v['reserve_mm'] for cat,v in mins.items() if cat!='self')))
  rows.append(dict(id=r['stroke'],pass_=all(p['pass_'] for p in poses),poses=poses))
  if r['stroke'] in selected:
   # Fresh constrained IK continuation from the retained support endpoint.
   start=np.array(next(p['q'] for p in r['poses'] if p['label']=='retained_on_own_support'));p0,R=held.pose(start);trail=[start];errors=[]
   for k in range(1,81):
    q,e=held.solve(p0+[0,0,.001*k],R,trail[-1]);trail.append(q);errors.append(e)
   rr=replay(held,trail);rr.update(id=r['stroke'],max_IK_position_mm=max(x['position_mm'] for x in errors),max_IK_orientation_deg=max(x['orientation_deg'] for x in errors));rr['pass_'] &= rr['max_IK_position_mm']<=5 and rr['max_IK_orientation_deg']<=3;stroke.append(rr)
   print('STROKE',r['stroke'],rr['pass_'],rr['states_checked'],flush=True)
  save('statics',dict(rows=rows,passed=sum(x['pass_'] for x in rows),obligations=150));save('strokes',stroke)
def paths():
 rows=[];prefix=[p for p in PRE['paths'] if not p.get('mechanism_evidence')];raw=read(UP/'v2/motion/L17_rehearsal.json')['paths'];cases=[('actual_prefix',p) for p in prefix]+[('raw_rehearsal',p) for p in raw if not p['id'].startswith('T01')]
 for scope,p in cases:
  ch=from_xml(p)
  if not p.get('path'):
   # Failed planner saved a checked state, not a successful path.
   reject=p.get('last_rejection');candidates=[]
   def walk(x):
    if isinstance(x,dict):
     if 'q' in x and isinstance(x['q'],list) and len(x['q'])==ch.m.nq:candidates.append(x['q'])
     for v in x.values():walk(v)
    elif isinstance(x,list):
     for v in x:walk(v)
   walk(p);rr=[]
   for q in candidates[:20]:
    hits,mins,mm=base.gaps(ch,np.array(q));rr.append(dict(q=q,hits=hits[:4],mismatch=mm))
   rows.append(dict(id=p['id'],scope=scope,submitted_pass=False,complete_path_available=False,rejection_replays=rr,collision_reproduced=any(x['hits'] for x in rr),budget_s=p.get('allocated_budget_s'),planner_time_s=p.get('planner_time_s')))
  else:
   rr=replay(ch,p['path'],save_samples=True);rr.update(id=p['id'],scope=scope,submitted_pass=p['ok']);rows.append(rr);print('PATH',p['id'],rr['pass_'],rr['states_checked'],flush=True)
  save('paths',rows)
def mechanisms():
 rows=[];d=read(UP/'results/mechanism_motion.json')
 for station in ('wash','process'):
  data=d[station];ch=from_xml(dict(xml=data['xml']));ch.m.geom_conaffinity[:]|=1
  for i,r in enumerate(data['rows']):
   end=np.array(r['start_q']);end[ch.qa[r['joint']]]=r['end'];rr=replay(ch,[r['start_q'],end.tolist()],r,True);rr.update(id=station+'_'+str(i)+'_'+r['joint'],submitted_pass=r['pass_'],kind=r['kind'],drive_interface_qualified=r['drive_interface_qualified'],actual_credit=station=='wash' and i<2,window=r.get('contact_window'));rows.append(rr);save('mechanisms',rows);print('MECH',rr['id'],rr['pass_'],rr['states_checked'],flush=True)
def audit():
 files=[p for folder in ('sim/r06/integrator','sim/r06/stations','sim/r04/integrator','sim/r05/integrator','inputs') for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[ROOT/'DECISIONS.md',ROOT/'posts/r06/integrator.md',ROOT/'posts/r06/stations.md']
 hashes={str(p.relative_to(ROOT)):sha(p) for p in files};save('source_hashes_before',hashes)
 diffs=[]
 for rn in ('r04','r05'):
  for b in (UP/('upstream_'+rn)).glob('*.py'):
   source=ROOT/'sim'/rn/'integrator'/b.name
   if source.exists():
    d=''.join(difflib.unified_diff(source.read_text().splitlines(True),b.read_text().splitlines(True)));(OUT/(rn+'_'+b.name+'.diff')).write_text(d);diffs.append(dict(source=str(source.relative_to(ROOT)),copy=str(b.relative_to(ROOT)),same=not d,sha256=sha(b)))
 # Preserve explicit original-input reference diff.
 (OUT/'input_reference.diff').write_text(''.join(difflib.unified_diff((ROOT/'inputs/prep_checker.py').read_text(encoding='utf-8-sig').splitlines(True),(UP/'upstream_r04/reference.py').read_text().splitlines(True))))
 row=PH['selected_witnesses'][0];job=row['job'];ch=rc.Workcell(V,job['object_id'],job['locations']);q=np.array(next(p['q'] for p in row['poses'] if p['label']=='retained_on_own_support'));orig=ch.window(job['object_id'],job['station'],job['origin']);probes=[]
 for name,mutation in [('baseline',{}),('wrong_support',{'support_id':'dock_tomato'}),('wrong_object',{'object_id':'output_tomato'}),('wrong_face',{'face':'wash_open_land'}),('sideways',{'normal':[1,0,0]}),('nonunit',{'normal':[0,0,2]}),('work_on_transit',{'kind':'working_stroke'})]:
  ch.contact_windows=copy.deepcopy(orig)
  for w in ch.contact_windows:w.update(mutation)
  ch.pose(q);mujoco.mj_forward(ch.m,ch.d);probes.append(dict(name=name,allowed=[sorted(x) for x in rc.permitted(ch)]))
 # Whole-source geometry remains full scale; replacements are inventoried.
 old=mujoco.MjModel.from_xml_path(str(UP/'history/v1/models/overview.xml'));new=rc.Workcell(17).m;geom=[]
 for g in range(old.ngeom):
  name=old.geom(g).name
  if name.startswith(('R_geom_','R_eoat_','pan_','food_','key_','lid_','insert_')):
   try:ng=new.geom(name).id
   except KeyError:geom.append(dict(name=name,preserved=False));continue
   geom.append(dict(name=name,preserved=True,type_equal=old.geom_type[g]==new.geom_type[ng],size_not_smaller=bool(np.all(new.geom_size[ng]>=old.geom_size[g]-1e-12))))
 save('audit',dict(reference_diffs=diffs,contact_probes=probes,geometry=geom,acceptance=rc.SPEC['acceptance'],declared_contact_windows=orig))
def conservation():
 rows=[];prev=None;baseline={}
 for s in PRE['states']:
  m=mujoco.MjModel.from_xml_path(str(UP/s['xml']));d=mujoco.MjData(m);d.qpos[:]=s['q'];mujoco.mj_forward(m,d);checks=[];food={};physical={}
  for g in range(m.ngeom):physical[m.geom(g).name.removeprefix('R_held_')]=(d.geom_xpos[g].copy(),d.geom_xmat[g].copy())
  for prod,mass in dict(carrot=.12,potato=.2,tomato=.15,bok_choy=.1).items():
   ids=[i for i in range(m.nbody) if m.body(i).name.removeprefix('R_held_')=='food_'+prod];checks.append(len(ids)==1);b=ids[0];owner=None
   while b:
    nm=m.body(b).name.removeprefix('R_held_')
    if nm.startswith('output_'):owner=nm;break
    b=int(m.body_parentid[b])
   geoms=[g for g in range(m.ngeom) if m.geom(g).name.removeprefix('R_held_')=='food_'+prod];checks.append(len(geoms)==1);size=m.geom_size[geoms[0]].tolist();baseline.setdefault(prod,size);checks += [size==baseline[prod],s['food'][prod]['mass_kg']==mass,s['food'][prod]['quality']=='raw_unwashed',owner==s['food'][prod]['owner']];food[prod]=dict(owner=owner,mass_kg=mass,size=size)
  for obj,v in s['containers'].items():
   ids=[b for b in range(m.nbody) if m.body(b).name.removeprefix('R_held_')==obj];checks.append(len(ids)==1);b=ids[0];checks += [np.linalg.norm(d.xpos[b]-v['position_m'])<1e-8,np.max(abs(d.xmat[b]-v['rotation']))<1e-8]
   lid=next(j for j in range(m.njnt) if m.joint(j).name.removeprefix('R_held_')=='lid_'+obj[7:]+'_joint');angle=d.qpos[m.jnt_qposadr[lid]];checks.append(abs(angle-(-1.7 if v['lid']=='open' else 0))<1e-8)
  checks.append(len(s['every_joint'])==m.njnt)
  for n,v in s['every_joint'].items():j=m.joint(n).id;checks.append(np.allclose(d.qpos[m.jnt_qposadr[j]:m.jnt_qposadr[j]+len(v)],v,atol=1e-12))
  seam=None
  if s['event'].endswith(('_attached','_supported')) and prev:
   seam=max(np.linalg.norm(physical[n][0]-prev[n][0]) for n in physical if n in prev);checks.append(seam<=1e-5)
  prev=physical;rows.append(dict(event=s['event'],pass_=bool(all(checks)),food=food,mass_kg=sum(v['mass_kg'] for v in food.values()),ownership_seam_m=seam,water=s['water'],appliance=s['appliance'],door_locked=s['door_locked'],person_inside=s['person_inside']))
 save('conservation',dict(pass_=all(r['pass_'] for r in rows),states=rows,finished_products=0,meal_pass=False))
def auxiliary():
 timing=[];seams=[]
 for p in PRE['paths']:
  ch=from_xml(p);pb=AllBound(ch);total=0.;maxacc=0.;maxspeed=0.
  for aa,bb in zip(p['path'],p['path'][1:]):
   aa=np.array(aa);bb=np.array(bb);dq=abs(bb-aa);B=pb.segment(aa,bb)
   if p.get('mechanism_evidence'):
    joint='lid_carrot_joint' if 'lid' in p['id'] else 'wash_retention_x';x=dq[ch.qa[joint]];v=.20 if 'lid' in p['id'] else .02;acc=.25 if 'lid' in p['id'] else .04
    total+=2*math.sqrt(x/acc) if x<=v*v/acc else x/v+v/acc
    continue
   lim=[(B,.10,.15)]+[(dq[ch.qa[n]],.20,.25) for n in rc.ARM]+[(dq[ch.qa[n]],.01,.02) for n in ('R_jaw_minus','R_jaw_plus')]+[(dq[ch.qa['R_carriage_x']],.06,.10)];lim=[x for x in lim if x[0]>1e-14]
   if not lim:continue
   speed=min(v/x for x,v,a in lim);acc=min(a/x for x,v,a in lim);peak=min(speed,math.sqrt(acc));total+=2/math.sqrt(acc) if 1<=speed*speed/acc else 1/speed+speed/acc
   ch.pose(aa);radii={};groups={};curv=np.zeros(ch.m.ngeom)
   for g,j,k,down in pb.rows:
    r=np.linalg.norm(ch.d.geom_xpos[g]-ch.d.xanchor[j])+ch.m.geom_rbound[g]+pb.weights[g,down]@dq[down];radii[g,k]=min(pb.weights[g,k],r);groups.setdefault(g,[]).append((k,down))
   for g,anc in groups.items():
    for k,down in anc:
     curv[g]+=radii[g,k]*dq[k]**2
     for dk in down:
      if (g,dk) in radii:curv[g]+=2*dq[k]*dq[dk]*radii[g,dk]
      elif dk in pb.slides:curv[g]+=2*dq[k]*dq[dk]
   maxacc=max(maxacc,B*acc+max(curv)*peak**2);maxspeed=max(maxspeed,B*peak)
  timing.append(dict(id=p['id'],recomputed_s=total,reported_s=p['duration_s'],difference_s=abs(total-p['duration_s']),robot_point_acceleration_bound_m_s2=None if p.get('mechanism_evidence') else maxacc,robot_point_speed_bound_m_s=maxspeed))
  i=next(i for i,s in enumerate(PRE['states']) if s['event']==p['id']);prev=PRE['states'][i-1];end=PRE['states'][i]
  # Named joint coordinates survive model ownership changes without indexing assumptions.
  def physical(state):
   m=mujoco.MjModel.from_xml_path(str(UP/state['xml']));d=mujoco.MjData(m);d.qpos[:]=state['q'];mujoco.mj_forward(m,d)
   return {m.geom(g).name.removeprefix('R_held_'):(d.geom_xpos[g].copy(),d.geom_xmat[g].copy()) for g in range(m.ngeom)}
  def compare(q,state):
   ch.pose(q);other=physical(state);return max(np.linalg.norm(ch.d.geom_xpos[g]-other[n.removeprefix('R_held_')][0]) for g,n in enumerate(ch.gnames)),max(np.max(abs(ch.d.geom_xmat[g]-other[n.removeprefix('R_held_')][1])) for g,n in enumerate(ch.gnames))
  first=compare(p['path'][0],prev);last=compare(p['path'][-1],end);seams.append(dict(id=p['id'],start_position_m=first[0],start_rotation_matrix_error=first[1],end_position_m=last[0],end_rotation_matrix_error=last[1],pass_=max(first+last)<1e-5))
 # Independently evaluate each rated-envelope witness in actual side mount.
 env=read(UP/'results/torque_envelope.json');ch=rc.Workcell(V);m,d=ch.m,ch.d
 for n in ('R_tool','R_jaw_minus','R_jaw_plus'):
  b=m.body(n).id;m.body_mass[b]=1e-9;m.body_inertia[b]=1e-12
 mujoco.mj_setConst(m,d);jp=np.zeros((3,m.nv));jr=np.zeros_like(jp);caps=[]
 for name,w in env['witnesses'].items():
  d.qpos[:]=ch.q0
  for n,x in zip(rc.ARM,w['joints_rad']):d.qpos[ch.qa[n]]=x
  mujoco.mj_forward(m,d);site=m.site('R_attachment_site').id;mujoco.mj_jacSite(m,d,jp,jr,site);R=d.site_xmat[site].reshape(3,3);F=np.array([0.,0.,-5*9.81]);moment=np.cross(R@np.array(w['CoM_flange_m']),F);tau=d.qfrc_bias-jp.T@F-jr.T@moment;value=abs(tau[ch.da[name]])
  caps.append(dict(joint=name,recomputed_Nm=value,reported_Nm=env['envelope_Nm'][name],difference_Nm=abs(value-env['envelope_Nm'][name])))
 raw=mujoco.MjModel.from_xml_path(str(UP/'sources/ur5e/ur5e.xml'));installed=rc.Workcell(V).m;oem=[]
 for b in range(1,raw.nbody):
  rb=installed.body('R_arm_'+raw.body(b).name).id;oem.append(dict(body=raw.body(b).name,mass_equal=abs(raw.body_mass[b]-installed.body_mass[rb])<1e-12,inertia_equal=bool(np.allclose(raw.body_inertia[b],installed.body_inertia[rb],atol=1e-12)),com_equal=bool(np.allclose(raw.body_ipos[b],installed.body_ipos[rb],atol=1e-12))))
 save('auxiliary',dict(timing=timing,total_prefix_s=20+sum(x['recomputed_s'] for x in timing),seams=seams,rated_envelope=caps,OEM_inertias=oem,proof='Time is synchronized trapezoid per saved segment. Point acceleration <= displacement_bound * path_acceleration + serial-chain Hessian bound * path_speed squared; hinge/slide mixed terms included. Envelope re-evaluates saved maximizing witnesses, no new global optimization claimed.'))
def metrics():
 paths=read(OUT/'paths.json');mechs=read(OUT/'mechanisms.json');stat=read(OUT/'statics.json');stroke=read(OUT/'strokes.json');v=[]
 for p in paths:
  if p['scope']=='actual_prefix' and p.get('pass_'):v+=p['reserve_samples_mm']
 for p in mechs:
  if p['actual_credit']:v+=p['reserve_samples_mm']
 def dist(x):return dict(n=len(x),min=min(x),percentiles={str(p):float(np.percentile(x,p)) for p in (5,25,50,75,95)},fraction_ge10=sum(t>=10-1e-5 for t in x)/len(x))
 costs=list(csv.DictReader((UP/'results/costs.csv').open(encoding='utf-8-sig')));sub=sum(float(x['line_cny']) for x in costs if x['id']!='RESERVE15');alltotal=sum(float(x['line_cny']) for x in costs)
 schedule=read(UP/'results/schedule.json');time=20+sum(p['duration_s'] for p in PRE['paths'] if p['ok'])
 before=read(OUT/'source_hashes_before.json');changes=[p for p,h in before.items() if sha(ROOT/p)!=h]
 allsuccessful=[p for p in paths+mechs if p.get('pass_')];longest=max(allsuccessful,key=lambda x:x['total_displacement_bound_m']);tightest=min(allsuccessful,key=lambda x:x['minimum_reserve_mm'])
 save('replay_coverage',dict(total_records=len(paths)+len(mechs),nonstationary_trajectories=sum(p.get('total_displacement_bound_m',0)>1e-8 for p in paths+mechs),nonstationary_complete_passes=sum(p.get('pass_',False) and p.get('total_displacement_bound_m',0)>1e-8 for p in paths+mechs),rejected_nonstationary_trajectories=sum(not p.get('pass_',False) and p.get('total_displacement_bound_m',0)>1e-8 for p in paths+mechs),stationary_trajectories=sum('total_displacement_bound_m' in p and p['total_displacement_bound_m']<=1e-8 for p in paths+mechs),search_without_complete_path=sum(p.get('complete_path_available') is False for p in paths),failed_trajectories_checked_through_first_failure=True))
 save('metrics',dict(static_score=[stat['passed'],150],stroke_replays=[sum(x['pass_'] for x in stroke),len(stroke)],connection_replay_records=len(paths)+len(mechs),complete_saved_paths_replayed=sum('pass_' in p for p in paths)+len(mechs),prefix_connections=[sum(p.get('pass_',False) for p in paths if p['scope']=='actual_prefix')+sum(p['pass_'] for p in mechs if p['actual_credit']),240],longest_replayed_success=longest['id'],longest_bound_m=longest['total_displacement_bound_m'],tightest_replayed_success=tightest['id'],tightest_reserve_mm=tightest['minimum_reserve_mm'],max_point_step_mm=max(p['max_point_step_mm'] for p in allsuccessful+stroke),static_reserve=dist([p['reserve_mm'] for r in stat['rows'] for p in r['poses']]),prefix_reserve=dist(v),cost_subtotal_cny=sub,cost_reserve_cny=alltotal-sub,cost_total_cny=alltotal,safety_lines=[x for x in costs if x['id']=='A13'],prefix_s=time,prep_min=None,upstream_files_changed=changes,max_torque_ratio=max(p['max_torque_ratio'] for p in allsuccessful),min_grip_margin=min(p['min_grip_margin'] for p in allsuccessful)))
task=sys.argv[1]
{'audit':audit,'statics':statics,'paths':paths,'mechanisms':mechanisms,'conservation':conservation,'auxiliary':auxiliary,'metrics':metrics}[task]()
