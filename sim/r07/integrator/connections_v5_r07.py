"""Every expanded connection runs real RRT with retained full world objects.
Conditional diagnostics are not passed off as an executed prefix.
"""
import os,sys,json,time,math,hashlib,copy
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
import persistent_v5_r07 as p
v=p.v
from motion_v5_r07 import mo
from binding_v5_r07 import Planner,grasp_window,jaw_path,exact_goal,support_hand
mo.Planner=Planner
from least_analytic_v4_r07 import solve as solve_ik
from point_bound import PointBound
O=v.O;H=v.H;ID=v.ID;out=O/'connections_v5'/ID;out.mkdir(parents=True,exist_ok=True)
rows=p.expanded();began=time.monotonic()
bundle=json.loads((O/'meal_pose_proposals_v5'/f'{ID}.json').read_text());assert bundle['complete']

def row_hand(r,last=False):
 h=copy.deepcopy(v.items[r['index']][1]['poses'][-1 if last else 0]['R']);h['roll_deg']+=r['roll_deg'];return h

def row_proposal(r,last=False):
 d=bundle['records'][r['id']][-1 if last else 0];return np.array(d['q']),d['k'],dict(file=d['source_static'],sha256=d['source_sha256'],admitted_current=d['source_admitted_template'] and d['pose_pass'],roll_deg=d['roll_deg'],endpoint_pose_pass=d['pose_pass'])

def proposal(index,last=False):
 for directory in ('static_v5/'+ID,'static_v5/L59','static_v4/L53'):
  file=O/directory/(str(index)+'.json')
  if not file.exists():continue
  d=json.loads(file.read_text());w=d.get('witness') or (d.get('best_failed') or {}).get('raw')
  if w and w.get('poses'):
   q=np.array(w['poses'][-1 if last else 0]['q']);return q,w.get('k',0),dict(file=str(file.relative_to(H)),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),admitted_current=directory=='static_v5/'+ID and bool(d.get('witness')) and d.get('complete',False))
 ch=v.scene(index);return ch.m.qpos0.copy(),0,dict(file=None,admitted_current=False)

def target(ch,h,t):
 h=p.zero(h);h.update(pos=t[:3,3].tolist(),approach=t[:3,0].tolist(),jaw_axis=(-t[:3,1]).tolist(),roll_deg=0);return h

def endpoint(ch,q,h,seconds=20):
 ch.hands={'R':h};ch.search_carriage=True;ch.lock_initial_carriage=False;ch.set_contacts(ch.hands);start=time.monotonic()
 for name,ix in ch.qa.items():
  if ch.m.jnt_limited[ch.jid[name]]:q[ix]=np.clip(q[ix],*ch.m.jnt_range[ch.jid[name]])
 candidate,err,hits,_=solve_ik(ch,q,{'R':h},0,start+seconds)
 return candidate,dict(allocated_s=seconds,actual_s=time.monotonic()-start,errors=err,blockers=hits[:8],pose_pass=all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in err),collision_pass=not hits)

def replay(ch,h,result):
 if not result['ok']:return dict(pass_=False,reason='planner rejected',states_checked=0)
 ch.contact_windows=result.get('contact_windows',[])
 pb=PointBound(ch);pl=Planner(ch,h,seconds=65);states=[];maxstep=0.;maxratio=0.;mingrip=1e9;bad=None;replay_deadline=time.monotonic()+180
 for si,(a,b) in enumerate(zip(np.array(result['path']),np.array(result['path'])[1:])):
  count=max(1,math.ceil(pb.segment_bound(a,b)/.004));maxstep=max(maxstep,pb.segment_bound(a,b)/count)
  for k in range(count+1):
   q=a+(b-a)*k/count
   if time.monotonic()>replay_deadline:bad=dict(kind='independent replay timeout',allocated_s=180);break
   if not pl.state(q,h):bad=dict(kind='gap',detail=pl.last);break
   if not all(not ch.m.jnt_limited[ch.jid[n]] or ch.m.jnt_range[ch.jid[n],0]-1e-8<=q[ix]<=ch.m.jnt_range[ch.jid[n],1]+1e-8 for n,ix in ch.qa.items()):bad=dict(kind='joint_range');break
   tq=ch.torque_multi(q,h,{'R':[0,0,0]},{'R':[0,0,0]});g=ch.grip_side(q,h['R'],[0,0,0],[0,0,0],'R')['margin'];maxratio=max(maxratio,tq['ratio']);mingrip=min(mingrip,g)
   if tq['ratio']>1 or g<1:bad=dict(kind='rated_envelope_or_grip',ratio=tq['ratio'],grip_margin=g);break
   states.append(dict(q=q.tolist(),segment=si,alpha=k/count))
  if bad:break
 return dict(pass_=bad is None,blocker=bad,states=states,states_checked=len(states),max_point_step_mm=maxstep*1000,max_envelope_ratio=maxratio,min_grip_margin=mingrip if mingrip<1e9 else None)

def planleg(world,i,name,attached,h,a,b,seed,ha=None,hb=None,pending=None):
 ch,hands=world.build(i,attached,h);ch.working_stroke=False;ch.contact_windows=[];v.s.PARK=a.copy();b=mo.shortq(ch,a,b)
 ch.staging_poses=[]
 for stage_index in (0,1,9,20,54,58):
  candidate,_,_=proposal(stage_index);stage=a.copy()
  for n in v.s.ck.ARMS['R']+['R_carriage_x']:stage[ch.qa[n]]=candidate[ch.qa[n]]
  ch.staging_poses.append(dict(name='template_'+str(stage_index),q=mo.shortq(ch,a,stage).tolist()))
 for x in (-1.4,-.8,-.2,.4):
  stage=a.copy();stage[ch.qa['R_carriage_x']]=x;ch.staging_poses.append(dict(name='carriage_first_'+str(x),q=stage.tolist()))
 ch.pending_grasp=pending
 # The original planner supplies staging-biased samples,12s restarts and16
 # shortcut trials. Near an invalid endpoint it still spends its65s budget.
 pl=Planner(ch,hands,seed=seed,seconds=65);start=time.monotonic();endchecks=[]
 for role,q in [('start',a),('goal',b)]:
  valid=pl.state(q,hands);endchecks.append(dict(role=role,collision_free=valid,blocker=copy.deepcopy(pl.last) if not valid else None))
 grasp_approach=None
 if pending:
  # A random final RRT edge almost never lies in the narrow authorized
  # insertion window. Construct the exact <=50mm normal approach backward
  # from the retained grasp frame, then plan freely to its clear end.
  approach_start=time.monotonic();goal=p.fk(ch,b);line=[b.copy()];valid=True;normal=np.array(pending['normal'])
  for step in range(1,26):
   target_pose=goal.copy();target_pose[:3,3]+=.05*step/25*normal
   qq,exact=exact_goal(ch,line[-1].copy(),target_pose)
   valid=bool(exact) and pl.edge(line[-1],qq,hands,hands,deadline=approach_start+60)
   if not valid:break
   line.append(qq.copy())
  grasp_approach=dict(kind='grasp_release_support',object_id=pending['object_id'],support_id=pending['support_id'],length_m=.05,normal=normal.tolist(),construction_pass=valid,constructed_states=len(line),actual_s=time.monotonic()-approach_start,allocated_s=60,blocker=copy.deepcopy(pl.last) if not valid else None)
  print('GRASP_APPROACH',seed,valid,len(line),round(time.monotonic()-approach_start,2),flush=True)
  if valid:
   result=pl.plan(a,line[-1],hands,hands)
   if result['ok']:result['path']+= [q.tolist() for q in list(reversed(line))[1:]]
  else:result=pl.plan(a,b,hands,hands)
 elif ha or hb:result=mo.plan_section(ch,a,b,ha or hands,hb or hands,seed,process=False)
 else:result=pl.plan(a,b,hands,hands)
 if grasp_approach:result['explicit_grasp_approach']=grasp_approach
 print('PLANNED_LEG',seed,name,result['ok'],round(result['planner_time_s'],2),flush=True)
 fresh=replay(ch,hands,result)
 model=f'models/{ID}_persistent_connection_{seed}_{name}.xml';(H/model).write_text(ch.xml)
 continuity=dict(start_matches_requested=False,end_matches_requested=False)
 if result.get('path'):continuity=dict(start_matches_requested=bool(np.max(abs(np.array(result['path'][0])-a))<=1e-8),end_matches_requested=bool(np.max(abs(np.array(result['path'][-1])-b))<=1e-8))
 return dict(name=name,planner_ran=True,allocated_budget_s=65,actual_s=time.monotonic()-start,planner=result,replay=fresh,endpoint_geometry=endchecks,grasp_window=pending,endpoint_joint_continuity=continuity,pass_=fresh['pass_'] and all(continuity.values()),model_xml=model,model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),state=world.snapshot()),ch,hands

def state_before(number):
 """Construct the explicitly conditional state after prior proposed strokes.
 Retained poses are FK results, never regenerated from the next template.
 No conditional state is marked executed. The actual executor commits only
 after all path, binding and support requirements of an edge pass.
 """
 w=p.World();trace=[]
 transformed=set()
 for r in rows[:number+1]:
  i=r['index'];h=row_hand(r,True);obj=p.identity(h);q,_,src=row_proposal(r,True)
  if w.attached and w.attached!=obj:
   old=w.attached;w.objects[old]['pose']=w.objects[old]['home'].copy();w.objects[old]['support']=w.objects[old]['home_support'];w.attached=None;trace.append(dict(operation='conditional_planned_return_to_registered_support',object_id=old,requires_checked_connection=True))
  if obj:
   try:
    change=w.reframe(obj,h)
    if change['requires_release_and_regrasp']:
     w.attached=None;change=w.reframe(obj,h,commit=True);trace.append(dict(operation='conditional_required_rigid_regrasp',event=change,executed=False))
   except ValueError as error:trace.append(dict(operation='unqualified_food_state_or_regrasp',object_id=obj,reason=str(error),executed=False))
   w.attached=obj;w.objects[obj]['pose']=p.fk(w.base,q);trace.append(dict(operation='conditional_stroke_endpoint',object_id=obj,index=i,source=src))
  else:w.attached=None
  if i in (3,18,12,30,36,45,51) and i not in transformed and r['repeat_index']==max(x['repeat_index'] for x in rows if x['index']==i):
   prod=h['product'];food='food:'+prod;station='linear_peeler_holder' if i in (3,18) else 'BFP610_processing_bowl' if i in (12,30) else 'secondary_work_face'
   # Food-only internal transfer/partition is authorized. The release and
   # guard/pusher/container operations are still required physical events.
   if w.attached==food:w.attached=None
   w.objects[food]['support']=station
   kind='peeled' if i in (3,18) else 'slices' if i in (12,30) else 'wedges' if i==51 else 'basal_root_trim' if i==36 else 'sections'
   if i in (36,45,51):
    # This is a conditional post-transfer scenario, not a committed food
    # move. The robot must have loaded the full food before this station
    # event; that required motion remains an explicit physical obligation.
    x,y,_=v.cfg['station_frames']['secondary']['new_center'];w.objects[food]['pose']=p.T([x,y,1.0],np.eye(3));trace.append(dict(operation='conditional_required_full_food_loading',object_id=food,station=station,executed=False))
   duration=6*2*.160/.0034/.20 if kind=='peeled' else None
   event=w.transform(prod,kind,station,duration,'Actuonix P16-200-256-12-P:3.4mm/s at150N;20percent duty;6 full160mm out/return strokes' if duration else 'No published per-batch duration for this exact input; not assigned a fabricated zero')
   trace.append(dict(operation='conditional_food_transformation',event=event,physical_prerequisites=['food release','guard/lid/pusher movement','normal appliance controls'],prerequisites_executed=False));transformed.add(i)
 return w,trace

indices=list(map(int,sys.argv[2:])) or list(range(len(rows)-1))
for number in indices:
 if time.monotonic()-began>950:break
 dest=out/f'{number}.json'
 if dest.exists():continue
 aa,bb=rows[number:number+2];i,j=aa['index'],bb['index'];w,trace=state_before(number);a,ka,sa=row_proposal(aa,True);b,kb,sb=row_proposal(bb);ha=p.zero(row_hand(aa,True));hb=p.zero(row_hand(bb));oa,ob=w.attached,p.identity(hb)
 if oa is None:ha.update(held='empty',held_kg=0,contacts=[],mass_offset_m=0,work_offset_m=0)
 row=dict(connection=number,from_stroke=aa,to_stroke=bb,planner_ran=False,pass_=False,executed=False,conditional_on_preceding_prefix=True,persistent_model_executable=True,source_proposals=[sa,sb],state_before=w.snapshot(),conditional_state_construction=trace,legs=[],binding_events=[],required_events=[],working_permissions_on_connection=0)
 if ob and w.objects[ob].get('bulk_output'):row['required_events'].append('Bulk output must move in a full container; direct bulk regrasp is unqualified. Planner conservatively retains the full original input geometry.')
 regrasp=False
 if ob:
  try:row['target_grasp_frame']=w.reframe(ob,hb);regrasp=row['target_grasp_frame']['requires_release_and_regrasp']
  except ValueError as error:row['required_events'].append(str(error))
 if oa==ob and not regrasp:
  leg,ch,hands=planleg(w,i,'retained_attachment',oa,ha,a,b,960000+number,ha={'R':ha} if ha.get('contacts') else None,hb={'R':hb} if hb.get('contacts') else None);row['legs'].append(leg)
  # Both template goals must be independently true in this same geometry.
  checks=[]
  for q,h,k in ((a,ha,ka),(b,hb,kb)):
   tt=p.fk(ch,q);rr=ch.target_rotation(h,k);checks.append(dict(position_mm=float(np.linalg.norm(tt[:3,3]-h['pos'])*1000),orientation_deg=float(np.degrees(Rotation.from_matrix(rr.T@tt[:3,:3]).magnitude()))))
  row['endpoint_pose_checks']=checks;row['pass_']=leg['pass_'] and all(c['position_mm']<=5 and c['orientation_deg']<=3 for c in checks)
  row['actual_roll_joint_proposals']=dict(from_deg=aa['roll_deg'],to_deg=bb['roll_deg'],geometry_relabelled=False)
 else:
  q=a.copy();proceed=True
  if oa:
   ch,hands=w.build(i,oa,ha);goal=w.objects[oa]['home'];w.objects[oa]['support']=w.objects[oa]['home_support'];release_h=support_hand(w,oa,target(ch,hands['R'],goal));goalq,exact=exact_goal(ch,q.copy(),goal);ik=dict(pose_pass=exact,method='Exact carriage-optimized IK to persistent support frame')
   if not exact:goalq,ik=endpoint(ch,q.copy(),release_h)
   leg,ch,hands=planleg(w,i,'return_to_own_support',oa,ha,q,goalq,961000+number,hb={'R':release_h});leg['endpoint_ik']=ik;row['legs'].append(leg);q=np.array(leg['planner']['path'][-1]) if leg['pass_'] else goalq;proceed=leg['pass_'] and ik['pose_pass']
   if proceed:
    actual=p.fk(ch,q);w.objects[oa]['pose']=actual
    empty,eh=w.build(i,None,ha);empty.pending_grasp=grasp_window(w,oa);q,jaw=jaw_path(empty,q,min(.09,w.objects[oa]['h']['jaw_opening_m']+.02),eh);row['binding_events'].append(jaw);proceed=jaw['pass_']
    if proceed:row['binding_events'].append(w.rebind(oa,w.objects[oa]['support'],actual))
  if oa is None or proceed:
   if ob and regrasp:
    row['binding_events'].append(w.reframe(ob,hb,commit=True))
   ch,hands=w.build(j,None,hb)
   if ob:
    goal=w.objects[ob]['pose'];grasp_h=target(ch,hands['R'],goal);grasp_h['jaw_opening_m']=min(.09,w.objects[ob]['h']['jaw_opening_m']+.020)
    q,jaw_open=jaw_path(ch,q,grasp_h['jaw_opening_m'],hands);row['binding_events'].append(jaw_open)
    goalq,exact=exact_goal(ch,b.copy(),goal);ik=dict(pose_pass=exact,method='Exact IK to retained full object frame',jaw_open_pass=jaw_open['pass_'])
    if not exact:goalq,ik=endpoint(ch,q.copy(),grasp_h)
    for label in ('minus','plus'):goalq[ch.qa['R_jaw_'+label]]=grasp_h['jaw_opening_m']/2
   else:goalq=b;ik=dict(pose_pass=True)
   leg,ch,hands=planleg(w,j,'empty_approach_existing_object',None,hb,q,goalq,962000+number,pending=grasp_window(w,ob) if ob else None);leg['endpoint_ik']=ik;row['legs'].append(leg)
   proceed=leg['pass_'] and ik['pose_pass']
   if ob and proceed:
    q=np.array(leg['planner']['path'][-1]);q,jaw=jaw_path(ch,q,w.objects[ob]['h']['jaw_opening_m'],hands);row['binding_events'].append(jaw);proceed=jaw['pass_']
    actual=p.fk(ch,q);error=float(np.max(abs(actual-w.objects[ob]['pose'])));row['binding_events'].append(dict(kind='world_pose_continuity',object_id=ob,max_matrix_error=error,pass_=error<=1e-7));proceed=proceed and error<=1e-7
    if proceed:
     try:row['binding_events'].append(w.rebind(ob,'R',actual))
     except ValueError as error:row['required_events'].append(str(error));proceed=False
     if proceed:
      departure=support_hand(w,ob,hb);loaded,_,_=planleg(w,j,'loaded_transfer_to_next_stroke',ob,hb,q,b,963000+number,ha={'R':departure});row['legs'].append(loaded);row['pass_']=loaded['pass_']
   elif not ob:row['pass_']=proceed
 row['planner_ran']=all(l['planner_ran'] for l in row['legs']) and bool(row['legs']);row['allocated_budget_s']=sum(l['allocated_budget_s'] for l in row['legs']);row['actual_planner_s']=sum(l['planner']['planner_time_s'] for l in row['legs']);row['committed']=False;row['conditional_state_after_attempt']=w.snapshot();row['mass_conserved']=abs(row['state_before']['total_food_kg']-.57)<1e-9
 row['pass_']=row['pass_'] and sa['endpoint_pose_pass'] and sb['endpoint_pose_pass']
 row['geometric_connection_pass']=row['pass_']
 if i in (3,18,12,30,36,45,51) and aa['repeat_index']==max(x['repeat_index'] for x in rows if x['index']==i):
  row['required_events'] += ['The full guard, holder/pusher and normal controls must execute before this declared food transformation; their completion is not inferred from an arm approach.']
 if row['required_events']:row['pass_']=False
 row['status']='CHECKED_CONDITIONAL_CONNECTION' if row['pass_'] else 'GEOMETRIC_PLANNER_REJECTION' if any(not l['pass_'] for l in row['legs']) else 'POSE_OR_PHYSICAL_BINDING_REJECTED_AFTER_PLANNING'
 row['blockers']=[dict(leg=l['name'],pairs=l['planner'].get('blockers',[]),last=l['planner'].get('last_rejection'),ik=l.get('endpoint_ik')) for l in row['legs'] if not l['pass_']]
 dest.write_text(json.dumps(row,indent=2,allow_nan=False,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else x.item()));print('PERSISTENT_CONNECTION',number,row['status'],'s',round(row['actual_planner_s'],2),flush=True)
