"""Path-derived speed accounting; no executed full-meal time is invented."""
import json,csv,math,sys,runpy
import numpy as np
import final_check as f
import motion_r05 as mo
from point_bound import PointBound
H=f.s.HERE;O=H/'results';runpy.run_path(str(H/'schedule_cost.py'));planned=json.loads((O/'schedule.json').read_text());motion=json.loads((O/'motion.json').read_text());items=[(ph,sg) for ph in f.s.P['phases'] for sg in ph['segments']];catalog=[]
def trapezoid(d,v,a):return 2*math.sqrt(d/a) if d<v*v/a else d/v+v/a
for r in motion['internal']:
 if not r['ok']:catalog.append(dict(stroke=r['stroke'],pass_=False,duration_s=None,reason='No complete verified geometric path'));continue
 ph,sg=items[r['index']];sg=r.get('segment_override',sg);ch=f.s.Checker(ph,sg);bound=PointBound(ch);dur=0;length=0;arms={'R':0,'L':0};segments=[]
 for e in r['edges']:
  path=np.array(e['path'])
  for a,b in zip(path,path[1:]):
   dq=abs(b-a);vs=[];acc=[]
   for n in f.s.ck.JOINTS:
    d=float(dq[ch.qa[n]])
    if d>1e-12:vs.append(.35/d);acc.append(.35/d)
   for side in f.s.model.SIDES:
    payload=sg['poses'][0].get(side,{}).get('held','empty');v=.2 if payload=='empty' else .1;d=float(dq[ch.qa[side+'_carriage_x']])
    if d>1e-12:vs.append(v/d);acc.append(.3/d)
   point=bound.bound(b-a);curve=bound.curvature(b-a)
   if point>1e-12:vs.append(.05/point);acc.append(.15/point)
   if curve>1e-12:vs.append(math.sqrt(.15/curve))
   T=trapezoid(1,min(vs),min(acc)) if vs else 0;active=[side for side in f.s.model.SIDES if any(dq[ch.qa[n]]>1e-8 for n in f.s.ck.ARMS[side]+[side+'_carriage_x'])];segments.append(dict(local_start_s=dur,local_end_s=dur+T,active_arms=active,duration_s=T,max_point_bound_m=point,point_curvature_bound_m=curve,common_scalar_speed_limit=min(vs) if vs else 0,common_scalar_accel_limit=min(acc) if acc else 0));dur+=T;length+=point
   for side in f.s.model.SIDES:
    if any(dq[ch.qa[n]]>1e-12 for n in f.s.ck.ARMS[side]+[side+'_carriage_x']):arms[side]+=T
 catalog.append(dict(stroke=r['stroke'],pass_=True,duration_s=dur,point_arc_length_upper_m=length,arm_duration_s=arms,segments=segments,basis='Rest-to-rest common scalar trapezoid at every retained waypoint, synchronized for both arms. Joint0.35rad/s and0.35rad/s2, rail0.2empty/0.1loaded m/s and0.3m/s2, every point<=0.05m/s and0.3m/s2. Point acceleration bound=D*sddot+C*sdot2, with0.15m/s2 allocated to each term. Conservative engineering home limits, not OEM performance claims.'))
connections=[]
for r in motion['between_strokes']:
 if not r['ok']:connections.append(dict(index=r['index'],pass_=False,duration_s=None));continue
 i=r['index'];ph,sg,_=mo.items[i];ph2,sg2,_=mo.items[i+1];ch=mo.scene(ph,sg,i);ch2=mo.scene(ph2,sg2,i+1);pb=PointBound(ch);pb2=PointBound(ch2);h=sg['poses'][-1];duration=0;length=0;segments=[]
 for a,b in zip(np.array(r['planner']['path']),np.array(r['planner']['path'])[1:]):
  dq=abs(b-a);vs=[];acc=[]
  for name in f.s.ck.JOINTS:
   d=float(dq[ch.qa[name]])
   if d>1e-12:vs.append(.35/d);acc.append(.35/d)
  for side in f.s.model.SIDES:
   d=float(dq[ch.qa[side+'_carriage_x']]);v=.2 if h.get(side,{}).get('held','empty')=='empty' else .1
   if d>1e-12:vs.append(v/d);acc.append(.3/d)
  point=max(pb.bound(b-a),pb2.bound(b-a));curve=max(pb.curvature(b-a),pb2.curvature(b-a))
  if point>1e-12:vs.append(.05/point);acc.append(.15/point)
  if curve>1e-12:vs.append(math.sqrt(.15/curve))
  T=trapezoid(1,min(vs),min(acc)) if vs else 0;active=[side for side in f.s.model.SIDES if any(dq[ch.qa[n]]>1e-8 for n in f.s.ck.ARMS[side]+[side+'_carriage_x'])];segments.append(dict(local_start_s=duration,local_end_s=duration+T,duration_s=T,active_arms=active,max_point_bound_m=point));duration+=T;length+=point
 connections.append(dict(index=i,pass_=True,duration_s=duration,point_arc_length_upper_m=length,segments=segments,scope='Isolated dual-scene geometry/load witness; not a conserved meal connection'))
new=dict(planned,schema='r05.path-derived-schedule',verified_prep_min=None,prep_min=None,planned_process_calendar_min=planned['planned_prep_min'],executability='FAIL: there is no executed connected path; no finished-meal timeline can be reported',path_catalog=catalog,verified_geometric_path_seconds=sum(x['duration_s'] for x in catalog if x['pass_']),missing_paths=[x['stroke'] for x in catalog if not x['pass_']],explicit_event_paths_missing=motion['required_event_paths_total'],two_arm_overlap_achieved=False,paired_pose_verified=False,overlap=[],proposed_overlap=planned['overlap'],process_times_source='Copied R04 recipe: same filling501.6s, soaking600s, three fresh potato rinses/drain30s, slow proxy-bound cuts, inspection and300s cleaning. Retained estimates; no force adjusted to pass.',speed_limits=dict(joint_rad_s=.35,joint_rad_s2=.35,rail_empty_m_s=.2,rail_loaded_m_s=.1,rail_m_s2=.3,max_point_m_s=.05,max_point_m_s2=.3),timeline_status='Geometric path durations are computed, but incomplete routes and unverified concurrency prevent execution-based makespan')
(O/'schedule.json').write_text(json.dumps(new,indent=2))
new['connection_path_catalog']=connections;new['verified_isolated_connection_seconds']=sum(x['duration_s'] for x in connections if x['pass_']);new['geometric_two_arm_motion_overlap_s']=sum(s['duration_s'] for x in catalog+connections if x['pass_'] for s in x.get('segments',[]) if len(s['active_arms'])==2);new['local_timelines_scope']='Each path starts its own clock at zero. Local simultaneous motion is shown; these disconnected paths are not concatenated into an executed full-meal timeline.'
(O/'schedule.json').write_text(json.dumps(new,indent=2))
costs=list(csv.DictReader((O/'costs.csv').open(encoding='utf-8')));base=[dict(r,configuration='recess_storage_candidate') for r in costs if r['configuration']=='best_candidate' and r['item'] not in ('TOTAL','One15percent project reserve')];extra=[('Full-size end-bay beam/guide/chain extensions',9000),('Vertical recess guides/drives/spring brakes',18000),('13kg appliance lift/transfer pallet with brake',12000),('Extra bay/header/site assembly',6000)]
for row in costs+base:row['status']='UNQUALIFIED_FOR_CONNECTED_MEAL; '+row['status']
for name,val in extra:base.append(dict(configuration='recess_storage_candidate',item=name,quantity=1,total_cny=val,basis='R05 engineering allowance; geometry/static snapshot only, deployment paths and installation not admitted',status='PLANNING_ONLY_NOT_PASSING'))
total=sum(float(r['total_cny']) for r in base);base.extend([dict(configuration='recess_storage_candidate',item='One15percent project reserve',quantity=1,total_cny=round(total*.15,2),basis='one reserve, home safety18k appears once',status='PLANNING_ONLY_NOT_PASSING'),dict(configuration='recess_storage_candidate',item='TOTAL',quantity=1,total_cny=round(total*1.15,2),basis='Includes45000 additional storage mechanism allowance before one15percent reserve',status='PLANNING_ONLY_NOT_PASSING')]);costs.extend(base)
with (O/'costs.csv').open('w',newline='',encoding='utf-8') as fp:w=csv.DictWriter(fp,fieldnames=list(costs[0]));w.writeheader();w.writerows(costs)
(O/'cost_summary.json').write_text(json.dumps(dict(totals={r['configuration']:float(r['total_cny']) for r in costs if r['item']=='TOTAL'},selected_working_static_candidate_cny=472879.95,recess_storage_candidate_cny=round(total*1.15,2),cheapest_passing_cny=None,source='R04 historical/planning allowances carried forward; R05 additional mechanisms are transparent engineering allowances, not prices/quotes'),indent=2));print('path durations',new['verified_geometric_path_seconds'],'executed prep null','storage budget',round(total*1.15,2))
