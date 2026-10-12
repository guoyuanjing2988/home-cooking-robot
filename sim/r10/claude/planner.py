"""RRT-Connect with restarts, staging bias, shortcutting and <=4 mm replay."""
import time,math
import numpy as np

def carry_clear(ch,q):
 # Safe carry requires every moving arm/held point inside a 600x500mm
 # horizontal envelope about the cart (conservative world AABB at small yaw).
 ch.d.qpos[:]=q
 import mujoco
 mujoco.mj_forward(ch.m,ch.d)
 for g,n in enumerate(ch.gnames):
  if not ch.robot[g] or not (n.startswith('R_geom_') or ch.gripper(g) or ch.held[g]):continue
  for k,half in [(0,.33),(1,.25)]:
   axis=np.eye(3)[k]
   if ch.bounds.support(g,axis)[k]>q[k]+half or ch.bounds.support(g,-axis)[k]<q[k]-half:return False
 return True
def edge(ch,a,b,deadline,step=.004,kind='transfer',mass=0,force=None):
 if np.max(abs(np.asarray(a)[:3]-np.asarray(b)[:3]))>1e-10:
  if kind=='working' or np.max(abs(np.asarray(a)[3:]-np.asarray(b)[3:]))>1e-10 or not carry_clear(ch,a) or not carry_clear(ch,b):
   return dict(ok=False,reason='base_move_requires_frozen_safe_carry',checked=0)
  delta=np.asarray(b)[:2]-np.asarray(a)[:2];yaw=(a[2]+b[2])/2
  if abs(delta@np.array([-np.sin(yaw),np.cos(yaw)]))>1e-6+1e-3*np.linalg.norm(delta):
   return dict(ok=False,reason='skid_drive_lateral_velocity',checked=0)
 bound=ch.point_bound.segment_bound(a,b);n=max(1,math.ceil(bound/step));states=[];mins=[]
 for i in range(n+1):
  if time.monotonic()>deadline:return dict(ok=False,reason='replay_timeout',checked=len(states),bound_m=bound)
  q=np.asarray(a)+(np.asarray(b)-a)*i/n;r=ch.check(q,kind=kind,mass=mass,force=force)
  states.append(q.tolist());mins.append(r['clearance'])
  if not r['ok']:return dict(ok=False,reason='rejected_state',checked=len(states),q=q.tolist(),rejection=r,bound_m=bound,step_bound_m=bound/n)
 return dict(ok=True,checked=len(states),path=states,clearance=mins,bound_m=bound,step_bound_m=bound/n)
def plan(ch,start,goal,budget_s=65,stages=(),seed=8,mass=0):
 assert budget_s>=60
 begun=time.monotonic();deadline=begun+budget_s;rng=np.random.default_rng(seed);start=np.asarray(start);goal=np.asarray(goal)
 # Endpoint failure is evidence, not an unspent-budget substitute for search.
 direct=edge(ch,start,goal,deadline,mass=mass)
 if direct['ok']:return dict(ok=True,method='direct',budget_s=budget_s,elapsed_s=time.monotonic()-begun,restarts=0,**{k:v for k,v in direct.items() if k!='ok'})
 ids=ch.active;lo=ch.m.jnt_range[ids,0];hi=ch.m.jnt_range[ids,1];attempts=0;nodes=0;best_rejection=direct
 def extend(tree,parent,target):
  arr=np.array(tree);index=int(np.argmin(np.linalg.norm((arr-target)[:,ids],axis=1)));a=arr[index]
  delta=target-a;scale=min(1.,.22/max(np.linalg.norm(delta[ids]),1e-12));b=a+delta*scale
  if np.max(abs(a[:3]-b[:3]))>1e-10 and (np.max(abs(a[3:]-b[3:]))>1e-10 or not carry_clear(ch,a)):return None
  # Coarse samples propose edges only; acceptance always uses edge() above.
  for t in np.linspace(0,1,4):
   if time.monotonic()>deadline or not ch.check(a+(b-a)*t,full=False,mass=mass)['ok']:return None
  tree.append(b);parent.append(index);return len(tree)-1
 def ancestry(tree,parent,i):
  out=[]
  while i is not None:out.append(tree[i]);i=parent[i]
  return out[::-1]
 while time.monotonic()<deadline:
  attempts+=1;A=[start];B=[goal];PA=[None];PB=[None];swapped=False;restart_end=min(deadline,time.monotonic()+10)
  while time.monotonic()<restart_end:
   q=start.copy();q[ids]=rng.uniform(lo,hi)
   if rng.random()<.20:q=(stages[int(rng.integers(len(stages)))] if stages else goal).copy()
   ia=extend(A,PA,q)
   if ia is not None:
    nodes+=1
    for _ in range(40):
     ib=extend(B,PB,A[ia])
     if ib is None:break
     nodes+=1
     if np.linalg.norm(B[ib]-A[ia])<1e-8:
      path=ancestry(A,PA,ia)+ancestry(B,PB,ib)[::-1][1:]
      if swapped:path=path[::-1]
      # Shortcut proposals must themselves pass full bounded replay.
      for _ in range(10):
       if len(path)<3 or time.monotonic()>deadline:break
       i,j=sorted(rng.choice(len(path),2,replace=False))
       if j>i+1 and edge(ch,path[i],path[j],deadline,mass=mass)['ok']:path=path[:i+1]+path[j:]
      replay=[];clear=[];maxstep=0.;ok=True
      for a,b in zip(path[:-1],path[1:]):
       e=edge(ch,a,b,deadline,mass=mass)
       if not e['ok']:best_rejection=e;ok=False;break
       replay+=e['path'][:-1];clear+=e['clearance'][:-1];maxstep=max(maxstep,e['step_bound_m'])
      if ok:return dict(ok=True,path=replay+[goal.tolist()],clearance=clear,budget_s=budget_s,elapsed_s=time.monotonic()-begun,restarts=attempts,nodes=nodes,step_bound_m=maxstep,method='RRT-Connect, staging, shortcuts, full replay')
      break
   A,B,PA,PB=B,A,PB,PA;swapped=not swapped
 return dict(ok=False,budget_s=budget_s,elapsed_s=time.monotonic()-begun,restarts=attempts,nodes=nodes,rejection=best_rejection,reason='finite_search_budget_exhausted')
def tool_rigid(ch,g):
 m=ch.m;b=int(m.geom_bodyid[g])
 return m.body(b).name in ('R_tool','R_jaw_minus','R_jaw_plus')
def slack(ch,q,cap,allowed=frozenset(),exact_self=True):
 """Min MuJoCo distance minus required gap over required pairs, capped
 (geom margins must already be raised by >=cap so those contacts exist)."""
 import mujoco
 m,d=ch.m,ch.d;d.qpos[:]=q;mujoco.mj_kinematics(m,d);mujoco.mj_comPos(m,d);mujoco.mj_collision(m,d);s=cap;seen=set()
 for c in d.contact[:d.ncon]:
  x,y=int(c.geom[0]),int(c.geom[1])
  if not(ch.robot[x] or ch.robot[y]):continue
  # Pairs rigid with each other on the tool (held item vs palm/envelope, jaws
  # fixed during transfers) cannot change along an arm path: not a level term.
  if tool_rigid(ch,x) and tool_rigid(ch,y):continue
  req=ch.required(ch,x,y)
  if req is None or frozenset((ch.gnames[x],ch.gnames[y])) in allowed:continue
  key=(min(x,y),max(x,y))
  if key in seen:continue
  seen.add(key)
  # MuJoCo distances are accurate for capsule/mesh vs box (tool boxes are meshes
  # with mesh_tool), not for arm self pairs (capsule-mesh offsets measured): those
  # use the exact convex bound of distance.py.
  if req[1]=='self' and not exact_self:continue
  dist=ch.bounds.pair(x,y)['lower_m'] if req[1]=='self' else c.dist
  # Self pairs (0 mm rule) include near-constant joint-adjacent gaps (e.g. 3.9 mm
  # base/shoulder); count >=1.5 mm self clearance as a full level.
  s=min(s,dist*cap/.0015 if req[1]=='self' else dist-req[0])
 return s
def plan_swept(ch,start,goal,budget_s=300,stages=(),seed=8,mass=0,cap=.004):
 """R10 RRT-Connect whose proposals keep a clearance level: each node has a
 level l=min(cap,slack); an edge from a node at level l is sampled every l of
 point travel (point_bound) and every sample needs slack>=l, so between
 samples a static pair keeps >=l/2. Tight roots get short, dense edges; levels
 only grow away from them. Acceptance is still the full edge() replay
 (<=4 mm, complete checker) of every edge."""
 begun=time.monotonic();deadline=begun+budget_s;rng=np.random.default_rng(seed);start=np.asarray(start,float);goal=np.asarray(goal,float)
 direct=edge(ch,start,goal,deadline,mass=mass)
 if direct['ok']:return dict(ok=True,method='direct',elapsed_s=time.monotonic()-begun,**{k:v for k,v in direct.items() if k!='ok'})
 ids=ch.arm_ids;lo=ch.m.jnt_range[ids,0];hi=ch.m.jnt_range[ids,1];m=ch.m;old=m.geom_margin.copy();best_rejection=direct;stats=dict(nodes=0,replays=0)
 def raised(f,*a):
  m.geom_margin[:]=old+cap
  try:return f(*a)
  finally:m.geom_margin[:]=old
 def level(q):return min(cap,raised(slack,ch,q,cap))
 def sweep(a,b,la):
  # Proposal only (full replay decides): samples every la of point travel; the
  # exact self-pair bound and the coarse checker run on every 4th sample.
  s=max(.0005,la);n=max(1,math.ceil(ch.point_bound.segment_bound(a,b)/s));sl=cap
  for i in range(1,n+1):
   if time.monotonic()>deadline:return None
   q=a+(b-a)*i/n;full_=(i%4==0 or i==n);sl=slack(ch,q,cap,exact_self=full_)
   if sl<la-1e-9:return None
   if full_ and not ch.check(q,full=False,mass=mass)['ok']:return None
  return min(cap,sl)
 la0,lb0=level(start),level(goal)
 if la0<=0 or lb0<=0:return dict(ok=False,reason='endpoint_without_clearance',levels=[la0,lb0],elapsed_s=time.monotonic()-begun)
 T=[dict(q=[start],p=[None],l=[la0]),dict(q=[goal],p=[None],l=[lb0])]
 def extend(t,target):
  arr=np.array(t['q']);i=int(np.argmin(np.linalg.norm((arr-target)[:,ids],axis=1)));a=arr[i];la=t['l'][i]
  delta=target-a;step=.22*max(.25,la/cap);b=a+delta*min(1.,step/max(np.linalg.norm(delta[ids]),1e-12))
  lb=raised(sweep,a,b,la)
  if lb is None:return None
  t['q'].append(b);t['p'].append(i);t['l'].append(lb);stats['nodes']+=1;return len(t['q'])-1
 def ancestry(t,i):
  out=[]
  while i is not None:out.append(t['q'][i]);i=t['p'][i]
  return out[::-1]
 swapped=False;tick=time.monotonic()
 while time.monotonic()<deadline:
  if time.monotonic()-tick>30:tick=time.monotonic();print('plan_swept',round(tick-begun),'nodes',[len(t['q']) for t in T],'levels_mm',[round(1000*max(t['l']),2) for t in T],'replays',stats['replays'],flush=True)
  A,B=T if not swapped else T[::-1]
  q=start.copy();q[ids]=rng.uniform(lo,hi)
  if stages and rng.random()<.20:q=stages[int(rng.integers(len(stages)))].copy()
  ia=extend(A,q)
  if ia is not None:
   for _ in range(60):
    ib=extend(B,A['q'][ia])
    if ib is None:break
    if np.linalg.norm(B['q'][ib]-A['q'][ia])<1e-8:
     path=ancestry(A,ia)+ancestry(B,ib)[::-1][1:]
     if swapped:path=path[::-1]
     for _ in range(12):
      if len(path)<3 or time.monotonic()>deadline:break
      i,j=sorted(rng.choice(len(path),2,replace=False))
      if j>i+1 and edge(ch,path[i],path[j],deadline,mass=mass)['ok']:path=path[:i+1]+path[j:]
     replay=[];clear=[];ok=True;stats['replays']+=1
     for a,b in zip(path[:-1],path[1:]):
      e=edge(ch,a,b,deadline,mass=mass)
      if not e['ok']:best_rejection=e;ok=False;break
      replay+=e['path'][:-1];clear+=e['clearance'][:-1]
     if ok:return dict(ok=True,path=replay+[goal.tolist()],clearance=clear,elapsed_s=time.monotonic()-begun,method='leveled RRT-Connect, shortcuts, full replay',levels=[la0,lb0],**stats)
     break
  swapped=not swapped
 return dict(ok=False,reason='finite_search_budget_exhausted',rejection=best_rejection,levels=[la0,lb0],elapsed_s=time.monotonic()-begun,**stats)
