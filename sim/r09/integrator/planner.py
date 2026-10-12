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
