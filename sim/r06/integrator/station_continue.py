"""Continue the admitted pan path into actual station sweeps; stop on rejection."""
from station_spec import *
import argparse,ast
p=argparse.ArgumentParser();p.add_argument('--variant',type=int,default=31);a=p.parse_args();cfg,s=register(a.variant)
source=H/f'v3/motion/L{a.variant}_persistent.json';prefix=json.loads(source.read_text());assert prefix['completed_transfers']==1
loc={obj:row['position_m'] for obj,row in prefix['states'][-1]['containers'].items()};ch=StationCell(a.variant,None,loc);q=ch.q0.copy()
for n,values in prefix['states'][-1]['every_joint'].items():
 if n in ch.qa:q[ch.qa[n]:ch.qa[n]+len(values)]=values
for file,names in [('station_probe.py',['physical','descendants']),('rescue_meal.py',['replay','duration'])]:
 tree=ast.parse((H/file).read_text())
 for node in tree.body:
  if isinstance(node,ast.FunctionDef) and node.name in names:exec(compile(ast.Module(body=[node],type_ignores=[]),file,'exec'),globals())
paths=copy.deepcopy(prefix['paths']);states=copy.deepcopy(prefix['states']);model=f'v3/models/L{a.variant}_continued.xml';(H/model).write_text(ch.xml);blocked=None
hs=payload(ch,ch.pose(q)[0]);hs['R']['check_forces_N']=[list(x) for x in itertools.product((-1.89,1.89),repeat=3)]
def save():
 write(f'v3/motion/L{a.variant}_extended.json',dict(prefix,paths=paths,states=states,blocked=blocked,finished_products=0,meal_pass=False,station_extended=True,food_quality='raw_unwashed',quality_assumption_committed=False))
def record(label):
 ch.pose(q);st=copy.deepcopy(states[-1]);st.update(event=label,xml=model,q=q.tolist(),every_joint={n:q[ch.qa[n]:ch.qa[n]+(7 if ch.m.jnt_type[j]==0 else 1)].tolist() for n,j in ch.jid.items()},appliance=dict(mode=label,lift_coupled=float(q[ch.qa['basket_lift_joint']])>=.021-1e-9,pan_retained=all(q[ch.qa[f'pan_retainer_{side}_joint']]>=.0345-1e-9 for side in (-1,1)),water_inlet='closed',drain='open' if q[ch.qa['pan_drain_carrot_joint']]>.001 else 'closed',water_L=0,root_retained=False,blade_parked=q[ch.qa['slice_blade_joint']]<1e-9))
 for p in PRODUCTS:st['containers']['output_'+p]['lid']='open' if q[ch.qa['lid_'+p+'_joint']]<-.01 else 'closed'
 states.append(st)
def commit(label,path,info):
 global q,blocked
 r=dict(id=label,xml=model,path=[np.array(z).tolist() for z in path],contact_windows=[],capture_window=None,force_case=hs,allocated_budget_s=65,**info);r['load_replay']=replay(ch,r['path'],hs);r['ok']=r.get('ok',True) and r['load_replay']['pass_']
 if r['ok']:
  q=np.array(path[-1]);r['duration_s']=duration(ch,path)
  if label!='P01_robot_park':
   pairs=[];delta=abs(np.array(path[-1])-path[0])
   for n,j in ch.jid.items():
    if ch.m.jnt_type[j] not in (2,3) or delta[ch.qa[n]]<1e-14:continue
    speed=.15 if ch.m.jnt_type[j]==3 else .005;acc=.3 if ch.m.jnt_type[j]==3 else .010;pairs.append((delta[ch.qa[n]],speed,acc))
   if pairs:
    speed=min(v/dist for dist,v,acc in pairs);acc=min(acc/dist for dist,v,acc in pairs);r['duration_s']=max(r['duration_s'],2*math.sqrt(1/acc) if 1<=speed*speed/acc else 1/speed+speed/acc)
  record(label)
 else:blocked=dict(path=label,reason='Station sweep or full reference load replay rejected',witness=r.get('mechanical_blocker') or r['load_replay'])
 paths.append(r);save();print(label,r['ok'],flush=True);return r['ok']

# Real free-connection RRT budget, restarting/shortcutting/staging inherited
# unchanged from R04/R05. Candidate starts do not teleport the arm to a park.
target=np.array([-.30,.20,1.43]);candidates=[];rng=np.random.default_rng(313131)
for k in range(12):
 z=q.copy()
 for n in ARM:z[ch.qa[n]]+=rng.normal(0,.25)
 r=ch.collision_solve(target,ch.rot,z,20)
 if r['okay']:candidates.append(r)
 if candidates and candidates[-1]['reserve_mm']>=10:break
if not candidates:
 blocked=dict(path='P01_robot_park',reason='No valid parked-arm IK branch');save();raise SystemExit(0)
goal=np.array(max(candidates,key=lambda r:r['reserve_mm'])['q']);c.s.PARK=goal.copy();planner=Planner(ch,hs,seed=313131,seconds=65)
for k,n in enumerate(planner.names):planner.limits[k]=ch.m.jnt_range[ch.jid[n]]
r=planner.plan(q,goal,hs,hs)
if not r['ok']:
 blocked=dict(path='P01_robot_park',reason='65s real RRT failed',witness=r);save();raise SystemExit(0)
if not commit('P01_robot_park',r['path'],dict(ok=True,planner=r,method='65s RRT with restarts, shortcutting, staged park')):raise SystemExit(0)

# Use exactly the same explicit ordered actuator programme as the diagnostics.
tree=ast.parse((H/'station_probe.py').read_text())
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='program' for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'station_probe programme','exec'),globals())
 if isinstance(node,ast.If) and any(isinstance(n,ast.Name) and n.id=='program' for n in ast.walk(node)):exec(compile(ast.Module(body=[node],type_ignores=[]),'station_probe additions','exec'),globals())

for label,goals in program:
 before=q.copy();end=q.copy();gs=descendants(goals)
 for n,value in goals.items():end[ch.qa[n]]=value
 ch.pose(before);bound=0
 for n in goals:
  j=ch.jid[n];radius=max((np.linalg.norm(ch.d.geom_xpos[g]-ch.d.xanchor[j])+ch.m.geom_rbound[g] for g in descendants([n])),default=0) if ch.m.jnt_type[j]==3 else 1
  bound+=abs(end[ch.qa[n]]-before[ch.qa[n]])*radius
 steps=max(1,math.ceil(bound/.004));trail=[];bad=None
 for i in range(steps+1):
  z=before+(end-before)*i/steps;violations,mins=physical(z,gs)
  if violations:bad=dict(sample=i,violations=violations[:8],q=z.tolist());break
  trail.append(z)
 # A failed constrained actuator sweep receives a real65s alternative-route
 # search in cradleY/Z/cup variables. No arm or food is moved independently.
 alt=None
 if bad and label in ('cradle_advance','cradle_lift'):
  variables=['cradle_park_joint','food_cradle_joint','end_cup_-1_joint','end_cup_1_joint'];ix=[ch.qa[n] for n in variables];limits=np.array([ch.m.jnt_range[ch.jid[n]] for n in variables]);active=descendants(variables);begin=time.monotonic();deadline=begin+65;last_restart=begin;nodes=[before.copy()];parents=[-1];restarts=0;checked=0;maxstep=0;last=None;found=None
  def edge(aa,bb):
   nonlocal_dummy=None
   length=float(sum(abs((bb-aa)[ix])));count=max(1,math.ceil(length/.004))
   for j in range(count+1):
    violations,mm=physical(aa+(bb-aa)*j/count,active)
    if violations:return False
    if time.monotonic()>deadline:return False
   return True
  while time.monotonic()<deadline:
   if time.monotonic()-last_restart>12:nodes=[before.copy()];parents=[-1];restarts+=1;last_restart=time.monotonic()
   sample=end.copy() if rng.random()<.20 else before.copy()
   if not np.array_equal(sample,end):sample[ix]=rng.uniform(limits[:,0],limits[:,1])
   near=int(np.argmin([np.linalg.norm((z[ix]-sample[ix])/(limits[:,1]-limits[:,0])) for z in nodes]));candidate=sample.copy();delta=sample[ix]-nodes[near][ix];candidate[ix]=nodes[near][ix]+delta*min(1,.015/max(sum(abs(delta)),1e-12));checked+=1
   if not edge(nodes[near],candidate):continue
   nodes.append(candidate);parents.append(near)
   if np.max(abs(candidate[ix]-end[ix]))<.01 and edge(candidate,end):
    ids=[len(nodes)-1]
    while parents[ids[-1]]!=-1:ids.append(parents[ids[-1]])
    found=[nodes[j] for j in reversed(ids)]+[end];break
  shortcuts=0
  if found is not None:
   for trial in range(16):
    if len(found)<3 or time.monotonic()>=deadline:break
    ii,jj=sorted(rng.choice(len(found),2,replace=False));shortcuts+=1
    if jj>ii+1 and edge(found[ii],found[jj]):found=found[:ii+1]+found[jj:]
  alt=dict(allocated_budget_s=65,elapsed_s=time.monotonic()-begin,method='4D actuator RRT;12s restarts;15mm extensions;every edge all-moving-points<=4mm;20percent goal bias',restarts=restarts,proposals=checked,success=found is not None,shortcut_attempts=shortcuts)
  if found is not None:trail=found;bad=None
 if bad:
  # Nothing after the first failed event is committed into the persistent meal.
  commit('P01_'+label,[before,before],dict(ok=False,mechanical_blocker=bad,alternative_planner=alt,method='Rejected actuator path; attempted samples are diagnostic only',max_appliance_point_step_mm=bound/steps*1000));break
 if not commit('P01_'+label,trail,dict(ok=True,method='Fully checked commanded actuator connection',max_appliance_point_step_mm=bound/steps*1000,mechanical_states_checked=steps+1,alternative_planner=alt)):break
print('PERSISTENT',sum(p['ok'] for p in paths),'paths; all food raw; first blocker',blocked)
