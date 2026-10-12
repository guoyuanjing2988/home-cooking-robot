"""Persistent real capture/transfer execution and explicit process blockers.

No ownership or food-quality transition commits across a rejected path. A raw-pan
handling rehearsal is separately labelled and never credited as a cooked product.
"""
from rescue_spec import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--variant',type=int,required=True);p.add_argument('--transfers',type=int,default=1);p.add_argument('--rehearsal',action='store_true');p.add_argument('--resume',action='store_true');a=p.parse_args()
cfg=config(a.variant);spec=recipe(a.variant);loc=initial_locations(cfg);paths=[];states=[];blocked=None;beg=time.monotonic();ch=Workcell(a.variant);q=ch.q0.copy();food_mass=dict(carrot=.12,potato=.20,bok_choy=.10,tomato=.15)
previous=H/f'v2/motion/L{a.variant}_{"rehearsal" if a.rehearsal else "persistent"}.json'
prior=json.loads(previous.read_text()) if previous.exists() else None
if prior:write(f'v2/audit/L{a.variant}_motion_before_{int(beg)}.json',prior)
resume_count=0
if a.resume and prior:
 completed=[s for s in prior['states'] if s['event'].endswith('_complete')]
 if completed:
  last=completed[-1];resume_count=len(completed);loc={obj:v['position_m'] for obj,v in last['containers'].items()};ch=Workcell(a.variant,None,loc);q=ch.q0.copy()
  for n,values in last['every_joint'].items():
   if n in ch.qa:q[ch.qa[n]:ch.qa[n]+len(values)]=values
  states=prior['states'][:prior['states'].index(last)+1];paths=[p for p in prior['paths'] if int(p['id'][1:3])<=resume_count]
def save():
 write(f'v2/motion/L{a.variant}_{"rehearsal" if a.rehearsal else "persistent"}.json',dict(config=cfg,recipe=spec,paths=paths,states=states,blocked=blocked,completed_transfers=sum(s['event'].endswith('_complete') for s in states),food_mass_kg=food_mass,food_total_kg=sum(food_mass.values()),food_quality='raw_unwashed',finished_products=0,meal_pass=False,elapsed_s=time.monotonic()-beg,scope='Conserved raw-pan handling rehearsal; processing bypass explicitly NOT meal credit' if a.rehearsal else 'Persistent meal prefix; stops at first unqualified physical or process event'))
def model(ch,label):
 f=f'v2/models/L{a.variant}_{label}.xml';(H/f).parent.mkdir(parents=True,exist_ok=True);(H/f).write_text(ch.xml);return f
def record(event):
 ch.pose(q);joints={n:q[ch.qa[n]:ch.qa[n]+(7 if ch.m.jnt_type[j]==0 else 1)].tolist() for n,j in ch.jid.items()}
 containers={}
 for p in PRODUCTS:
  obj='output_'+p;b=ch.m.body(('R_held_' if ch.held_id==obj else '')+obj).id;containers[obj]=dict(position_m=ch.d.xpos[b].tolist(),rotation=ch.d.xmat[b].tolist(),held=ch.held_id==obj,lid='closed')
 states.append(dict(event=event,q=q.tolist(),xml=model(ch,event),every_joint=joints,containers=containers,food={p:dict(mass_kg=m,owner='output_'+p,quality='raw_unwashed') for p,m in food_mass.items()},jaw_positions=[float(q[ch.qa[n]]) for n in ('R_jaw_minus','R_jaw_plus')],held=ch.held_id,door_locked=True,person_inside=False,water='off',appliance='off_parked',food_total_kg=sum(food_mass.values())))
def replay(ch,path,hs):
 pb=PointBound(ch);res=[];ordinary=[];maxratio=0;mingrip=1e30;states_checked=0;trace=[];maxstep=0;counts=Counter()
 for aa,bb in zip(path,path[1:]):
  aa=np.array(aa);bb=np.array(bb);bound=pb.segment_bound(aa,bb);steps=max(1,int(math.ceil(bound/.004)));maxstep=max(maxstep,bound/steps)
  for k in range(steps+1):
   z=aa+(bb-aa)*(k/steps);hits,mins,proof=contacts(ch,z);tq,gr,cases=check_load(ch,z,hs);states_checked+=1;maxratio=max(maxratio,tq);mingrip=min(mingrip,gr)
   rv=min((v['reserve_mm'] for cat,v in mins.items() if cat!='self'),default=0);res.append(rv)
   if not permitted(ch):ordinary.append(rv)
   if hits or tq>1 or gr<1:return dict(pass_=False,states=states_checked,first_blocker=hits[:5],torque_ratio=tq,grip_margin=gr,q=z.tolist(),max_point_step_mm=maxstep*1000)
   if states_checked%10==0:trace.append(dict(q=z.tolist(),reserve_mm=rv))
 return dict(pass_=True,states=states_checked,min_reserve_mm=min(res,default=None),reserve_samples_mm=res,ordinary_reserve_samples_mm=ordinary,max_torque_ratio=maxratio,min_grip_margin=mingrip,max_point_step_mm=maxstep*1000,trace=trace)
def duration(ch,path):
 pb=PointBound(ch);out=0
 for aa,bb in zip(path,path[1:]):
  delta=abs(np.array(bb)-aa);pairs=[(pb.segment_bound(aa,bb),.10,.15)]+[(delta[ch.qa[n]],.20,.25) for n in ARM]+[(delta[ch.qa[n]],.01,.02) for n in ('R_jaw_minus','R_jaw_plus')]+[(delta[ch.qa['R_carriage_x']],.06,.10)]
  moving=[(d,v,acc) for d,v,acc in pairs if d>1e-14]
  if moving:
   v=min(v/d for d,v,acc in moving);acc=min(acc/d for d,v,acc in moving);out+=2*math.sqrt(1/acc) if 1<=v*v/acc else 1/v+v/acc
 return out
def commit(label,r,hs):
 global q,blocked
 r['id']=label;r['xml']=model(ch,label);r['geometry_signature']=hashlib.sha256(ch.xml.encode()).hexdigest();r['contact_windows']=copy.deepcopy(ch.contact_windows);r['capture_window']=copy.deepcopy(getattr(ch,'capture_window',None));r['force_case']=hs
 if r['ok']:
  r['load_replay']=replay(ch,r['path'],hs);r['ok']=r['load_replay']['pass_']
 if r['ok']:q=np.array(r['path'][-1]);r['duration_s']=duration(ch,r['path']);record(label)
 else:blocked=dict(path=label,reason=r.get('reason','Full geometry/load replay failure'),witness=r.get('load_replay') or r.get('last_rejection'))
 paths.append(r);save();print(label,r['ok'],r.get('planner_time_s'),r.get('load_replay',{}).get('min_reserve_mm'),flush=True)
 return r['ok']
def solve_target(target,initial):
 r=ch.collision_solve(np.array(target),ch.rot,initial,seconds=20)
 # Contact acquisition needs accurate geometry continuity, stricter than the
 # unchanged5mm/3deg pose acceptance, so refine the chosen branch to the goal.
 z=np.array(r['q']);ix=ch.ix;limits=np.array([ch.m.jnt_range[ch.jid[n]] for n in ch.variables]).T
 def fun(x):
  z[ix]=x;pos,rot=ch.pose(z);return np.r_[(pos-target)*20,Rotation.from_matrix(ch.rot.T@rot).as_rotvec()*3]
 ls=least_squares(fun,np.clip(z[ix],limits[0]+1e-9,limits[1]-1e-9),bounds=limits,max_nfev=160,ftol=1e-10,xtol=1e-10,gtol=1e-10);z[ix]=ls.x;pos,rot=ch.pose(z);hits,mins,pf=contacts(ch,z)
 valid=not hits and np.linalg.norm(pos-target)<1e-6 and np.linalg.norm(Rotation.from_matrix(ch.rot.T@rot).as_rotvec())<1e-5
 if valid:return z,True
 # A5mm admissible free-space IK pose can still be unsuitable for a real key
 # capture. Enumerate exact endpoint branches; do not pass an invalid refined
 # endpoint to RRT as if extra planning time could repair it.
 candidates=[];rng=np.random.default_rng(6700+len(paths))
 for k in range(48):
  zz=np.array(initial).copy()
  for n in ch.variables:
   lo,hi=ch.m.jnt_range[ch.jid[n]];zz[ch.qa[n]]=rng.uniform(max(-math.pi,lo),min(math.pi,hi))
  def exact(x):
   zz[ix]=x;pp,rr=ch.pose(zz);return np.r_[(pp-target)*20,Rotation.from_matrix(ch.rot.T@rr).as_rotvec()*3]
  sol=least_squares(exact,np.clip(zz[ix],limits[0]+1e-9,limits[1]-1e-9),bounds=limits,max_nfev=120,ftol=1e-9,xtol=1e-9,gtol=1e-9);zz[ix]=sol.x
  for n in ARM:
   qi=ch.qa[n];lo,hi=ch.m.jnt_range[ch.jid[n]];options=[zz[qi]+d*2*math.pi for d in (-1,0,1) if lo<=zz[qi]+d*2*math.pi<=hi];zz[qi]=min(options,key=lambda v:abs(v-initial[qi]))
  pp,rr=ch.pose(zz);hh,mm,pf=contacts(ch,zz)
  if not hh and np.linalg.norm(pp-target)<1e-6 and np.linalg.norm(Rotation.from_matrix(ch.rot.T@rr).as_rotvec())<1e-5:candidates.append(zz.copy())
 if candidates:return min(candidates,key=lambda x:np.linalg.norm(x[ix]-np.array(initial)[ix])),True
 return z,False
def free_move(label,target,hs):
 goal,valid=solve_target(np.array(target),q)
 # Invalid endpoints still receive a real65s connection search. The result
 # cannot pass merely because a layout diagnosis already exists.
 c.s.PARK=q.copy();planner=Planner(ch,hs,seed=6100+len(paths),seconds=65)
 for k,n in enumerate(planner.names):planner.limits[k]=ch.m.jnt_range[ch.jid[n]]
 staging=[]
 for point in ([0,.32,1.40],[-.30,.35,1.22],[.30,.35,1.22]):
  st,ok=solve_target(np.array(point),q);staging.append(dict(target_m=point,pass_=ok,q=st.tolist()))
  if ok:c.s.PARK=st.copy()
 r=planner.plan(q,goal,hs,hs);r['endpoint_valid']=valid;r['staging']=staging
 if not r['ok']:
  # Constant-yaw Cartesian routes can trap a wide pan against the upper arm.
  # Whole-pan yaw is allowed in free space: explicitly search orientations,
  # retaining every arm/pan point and the unchanged contact-window rotations.
  original_search=copy.deepcopy(r);orientation_attempts=[];normal_rot=ch.rot.copy();pstart,_=ch.pose(q)
  for yaw in (90,-90):
   orient=Rotation.from_euler('z',yaw,degrees=True).as_matrix()@normal_rot;stages=[(pstart,orient),(np.array([pstart[0],.25,1.22]),orient),(np.array([target[0],.25,1.22]),orient),(np.array(target),normal_rot)];trail=[q.copy()];segments=[];allok=True
   for si,(position,rotation) in enumerate(stages):
    ch.rot=rotation;end,good=solve_target(position,trail[-1]);c.s.PARK=trail[-1].copy();pp=Planner(ch,hs,seed=7100+len(paths)*10+si+(100 if yaw<0 else 0),seconds=65)
    for k,n in enumerate(pp.names):pp.limits[k]=ch.m.jnt_range[ch.jid[n]]
    seg=pp.plan(trail[-1],end,hs,hs);seg['endpoint_valid']=good;segments.append(seg)
    if not seg['ok']:allok=False;break
    trail += [np.array(x) for x in seg['path'][1:]]
   ch.rot=normal_rot;orientation_attempts.append(dict(yaw_degrees=yaw,segments=segments,pass_=allok))
   if allok:
    r=dict(ok=True,path=[x.tolist() for x in trail],allocated_budget_s=65,method='Explicit whole-pan yaw staging; each segment65s RRT budget and full4mm replay',orientation_attempts=orientation_attempts,preceding_search=original_search);break
  if not r['ok']:r['orientation_attempts']=orientation_attempts
 if not r['ok']:
  attempts=[copy.deepcopy(r)];p0,r0=ch.pose(q);target=np.array(target)
  # Explicit elevated Cartesian corridors supplement the random-tree staging
  # bias. They preserve the food pose continuously and get65s per segment.
  for height,lane in ((1.20,.17),(1.25,.20),(1.30,.32),(1.40,.32)):
   knots=[np.array([p0[0],p0[1],height]),np.array([p0[0],lane,height]),np.array([target[0],lane,height]),np.array([target[0],target[1],height]),target]
   trail=[q.copy()];failure=None;begin=time.monotonic();segment_records=[]
   for point in knots:
    ps,_=ch.pose(trail[-1]);count=max(1,int(math.ceil(np.linalg.norm(point-ps)/.002)));guard=Planner(ch,hs,seed=6891,seconds=65);deadline=time.monotonic()+65;segstart=time.monotonic()
    for k in range(1,count+1):
     pos=ps+(point-ps)*k/count;zz=trail[-1].copy();ix=ch.ix;lim=np.array([ch.m.jnt_range[ch.jid[n]] for n in ch.variables]).T
     def fun(x):
      zz[ix]=x;pp,rr=ch.pose(zz);return np.r_[(pp-pos)*20,Rotation.from_matrix(r0.T@rr).as_rotvec()*3]
     sol=least_squares(fun,np.clip(zz[ix],lim[0]+1e-9,lim[1]-1e-9),bounds=lim,max_nfev=80,ftol=1e-10,xtol=1e-10,gtol=1e-10);zz[ix]=sol.x;pp,rr=ch.pose(zz)
     if np.linalg.norm(pp-pos)>1e-6 or not guard.edge(trail[-1],zz,hs,hs,deadline):failure=dict(point=point.tolist(),sample=k,last_rejection=guard.last,position_error_m=float(np.linalg.norm(pp-pos)));break
     trail.append(zz.copy())
    segment_records.append(dict(target=point.tolist(),allocated_budget_s=65,elapsed_s=time.monotonic()-segstart,pass_=failure is None))
    if failure:break
   candidate=dict(ok=failure is None,path=[x.tolist() for x in trail],allocated_budget_s=65,method='Explicit elevated5-segment Cartesian corridor after65s RRT failure',planner_time_s=time.monotonic()-begin,segments=segment_records,last_rejection=failure,staging_height_m=height,staging_lane_y_m=lane)
   if candidate['ok']:candidate['preceding_search_attempts']=attempts;r=candidate;break
   attempts.append(candidate)
  else:r['additional_staged_attempts']=attempts[1:]
 return commit(label,r,hs)
def line(label,target,hs):
 start=q.copy();p0,r0=ch.pose(start);target=np.array(target);steps=max(1,int(math.ceil(np.linalg.norm(target-p0)/.001)));path=[start];solver=Planner(ch,hs,seed=6200+len(paths),seconds=65);deadline=time.monotonic()+65
 for k in range(1,steps+1):
  goal=p0+(target-p0)*k/steps;z=path[-1].copy();ix=ch.ix;lim=np.array([ch.m.jnt_range[ch.jid[n]] for n in ch.variables]).T
  def fun(x):
   z[ix]=x;po,ro=ch.pose(z);return np.r_[(po-goal)*20,Rotation.from_matrix(r0.T@ro).as_rotvec()*3]
  ls=least_squares(fun,np.clip(z[ix],lim[0]+1e-9,lim[1]-1e-9),bounds=lim,max_nfev=80,ftol=1e-10,xtol=1e-10,gtol=1e-10);z[ix]=ls.x;po,ro=ch.pose(z)
  if np.linalg.norm(po-goal)>1e-6 or not solver.edge(path[-1],z,hs,hs,deadline):return commit(label,dict(ok=False,path=[x.tolist() for x in path],allocated_budget_s=65,reason='Straight owned support/acquisition stroke blocked',last_rejection=solver.last,sample=k),hs)
  path.append(z)
 return commit(label,dict(ok=True,path=[x.tolist() for x in path],allocated_budget_s=65,method='Constrained straight Cartesian continuation plus full4mm reference replay'),hs)
def jaws(label,closed,hs):
 goal=q.copy()
 for n in ('R_jaw_minus','R_jaw_plus'):goal[ch.qa[n]]=.005 if closed else -.02
 return commit(label,dict(ok=True,path=[q.tolist(),goal.tolist()],method='Commanded synchronous jaw capture/release; full4mm point bound',allocated_budget_s=65),hs)
def ownership(new,held,locations):
 global ch,q,blocked
 other=Workcell(a.variant,held,locations);z=names_to_q(other,ch,q);ch.pose(q);other.pose(z)
 old={n.removeprefix('R_held_'):(ch.d.geom_xpos[i].copy(),ch.d.geom_xmat[i].copy()) for i,n in enumerate(ch.gnames)};err=0;rot_err=0
 for i,n in enumerate(other.gnames):
  canonical=n.removeprefix('R_held_')
  if canonical in old:
   err=max(err,float(np.linalg.norm(other.d.geom_xpos[i]-old[canonical][0])));rot_err=max(rot_err,float(np.max(abs(other.d.geom_xmat[i]-old[canonical][1]))))
 if err>1e-5 or rot_err>1e-5:blocked=dict(path=new,reason='Ownership would move/rotate physical geometry',maximum_position_change_m=err,rotation_matrix_error=rot_err);save();return False
 ch=other;q=z;record(new);states[-1]['ownership_position_invariant_m']=err;states[-1]['ownership_rotation_invariant']=rot_err;return True
# Select a valid declared home, not an arbitrary zero-joint teleport.
home=key_position(loc['output_carrot'],cfg)+[0,0,.20];rng=np.random.default_rng(60613);home_rows=[]
for k in range(0 if resume_count else 96):
 trial=ch.q0.copy()
 for n in ch.variables:
  lo,hi=ch.m.jnt_range[ch.jid[n]];trial[ch.qa[n]]=rng.uniform(max(-math.pi,lo),min(math.pi,hi))
 r=ch.collision_solve(home,ch.rot,trial);home_rows.append(r)
 if r['okay'] and r['reserve_mm']>=10:q=np.array(r['q']);break
else:
 if not resume_count:blocked=dict(path='home',reason='No admissible home');save();raise SystemExit(0)
if not resume_count:write(f'v2/motion/L{a.variant}_home_search.json',home_rows);record('E00_home');save()
for tr in spec['transfers'][resume_count:a.transfers]:
 if time.monotonic()-beg>700:blocked=dict(reason='Bounded run checkpoint at completed transfer; resume preserves all states');save();break
 obj=tr['object_id'];origin=loc[obj];dest=tr['dest'];grasp=key_position(origin,cfg);drop=key_position(dest,cfg);hs=hand(ch,grasp)
 ch.capture(obj,origin)
 if not free_move(tr['id']+'_empty_approach',grasp+[0,0,.08],hs):break
 if not line(tr['id']+'_key_descent',grasp,hs):break
 if not jaws(tr['id']+'_jaw_close',True,hs):break
 if not ownership(tr['id']+'_attached',obj,loc):break
 ch.contact_windows=ch.window(obj,tr['source'],origin)+ch.window(obj,tr['destination'],dest);hs=hand(ch,grasp)
 if not line(tr['id']+'_loaded_lift',grasp+[0,0,.08],hs):break
 if not free_move(tr['id']+'_loaded_transfer',drop+[0,0,.08],hs):break
 if not line(tr['id']+'_seat',drop,hs):break
 loc[obj]=list(dest)
 if not ownership(tr['id']+'_supported',None,loc):break
 ch.capture(obj,dest);hs=hand(ch,drop)
 if not jaws(tr['id']+'_jaw_open',False,hs):break
 if not line(tr['id']+'_empty_retreat',drop+[0,0,.08],hs):break
 record(tr['id']+'_complete');save()
 if not a.rehearsal and not tr['destination'].startswith('dock_'):
  blocked=dict(event='P'+tr['id'][1:],reason='At appliance: retained food cradle, complete wash/peel/cut interfaces and quality transitions must pass before committing food state',station=tr['destination']);save();break
print('MOTION',sum(p['ok'] for p in paths),'/',len(paths),'complete transfers',sum(s['event'].endswith('_complete') for s in states),'block',blocked)
