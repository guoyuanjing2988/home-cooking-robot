"""Bidirectional RRT-Connect in 12 arm joints + 2 carriage coordinates.

Edges retain both arms and all held objects. A midpoint dual distance reserve
must exceed a global rigid-geometry displacement bound; otherwise subdivision
continues to <=0.5mm bound and unresolved edges are rejected, never accepted.
"""
import time,numpy as np
import final_check as f
s=f.s
class Planner:
 def __init__(self,ch,hands,seed=404,seconds=20):
  self.ch=ch;self.hands=hands;self.rng=np.random.default_rng(seed);self.seed=seed;self.seconds=seconds;self.calls=0;self.edges=0;self.last=None
  self.names=sum(s.ck.ARMS.values(),[])+[x+'_carriage_x' for x in s.model.SIDES];self.ix=[ch.qa[n] for n in self.names]
  self.limits=np.array([ch.m.jnt_range[ch.jid[n]] for n in self.names]);self.scale=np.array([.5 if n.endswith('carriage_x') else 1. for n in self.names])
  for j,n in enumerate(self.names):
   if n=='R_carriage_x':self.limits[j,1]=.045
 def state(self,q,hands=None):
  self.calls+=1;self.ch.set_contacts(self.hands if hands is None else hands);hits,mins,ca=f.contacts(self.ch,q)
  return hits,min(v['reserve_mm'] for v in mins.values()),mins
 def bound(self,dq):
  # 2m per angular DOF exceeds the sum of serial link offsets plus full EOAT
  # and held-body radius (<1.7m in these source models). Relative motion of
  # two moving arms is bounded by the sum over both chains.
  return 2*sum(abs(dq[self.ch.qa[n]]) for n in s.ck.JOINTS)+sum(abs(dq[self.ch.qa[x+'_carriage_x']]) for x in s.model.SIDES)+sum(abs(dq[self.ch.qa[n]]) for n in s.ck.JAWS)
 def edge(self,a,b,ha=None,hb=None,deadline=None):
  self.edges+=1;a=np.array(a);b=np.array(b);dq=b-a;B=self.bound(dq);mid={k:dict(h,contacts=[]) for k,h in self.hands.items()}
  if ha is not None and hb is not None:
   for k,h in mid.items():h['contacts']=[c for c in ha.get(k,{}).get('contacts',[]) if c in hb.get(k,{}).get('contacts',[])]
  records=[]
  for alpha,h in [(0,ha or self.hands),(1,hb or self.hands)]:
   hits,r,mins=self.state(a+alpha*dq,h)
   if hits:return dict(ok=False,reason='endpoint fails unchanged reference or distance certificate',alpha=alpha,blockers=hits[:6],states=self.calls)
  stack=[(0.,1.)];cert=0;reserve=1e9
  while stack:
   if deadline and time.monotonic()>deadline:return dict(ok=False,reason='bounded planner timeout; no accepted edge',states=self.calls)
   lo,hi=stack.pop();alpha=(lo+hi)/2;hits,r,mins=self.state(a+alpha*dq,mid);reserve=min(reserve,r)
   if hits:
    self.last=dict(ok=False,reason='gap/contact rejection',alpha=alpha,blockers=hits[:6],states=self.calls);return self.last
   half=B*(hi-lo)*500
   if self.ch.bounds.interval_certificate(dq,(hi-lo)/2):cert+=1;continue
   if B*(hi-lo)<=.0005:return dict(ok=False,reason='unproved interval at0.5mm displacement bound',interval=[lo,hi],reserve_mm=r,required_reserve_mm=half,states=self.calls)
   stack.extend([(alpha,hi),(lo,alpha)])
  return dict(ok=True,certified_intervals=cert,min_reserve_mm=reserve,states=self.calls)
 def plan(self,a,b,ha=None,hb=None,max_nodes=160):
  began=time.monotonic();deadline=began+self.seconds;a=np.array(a);b=np.array(b)
  direct=self.edge(a,b,ha,hb,min(deadline,began+4))
  if direct['ok']:return dict(ok=True,method='RRT-Connect direct certified edge',path=[a.tolist(),b.tolist()],states=self.calls,edges=self.edges,elapsed_s=time.monotonic()-began,seed=self.seed,certificate=direct)
  # Endpoint-only support contact is a discontinuity, not a sampling problem.
  permitted_work={'root_brush_work_face','clamped_food','wash_food','peel_food_land','peel_endstop-1','peel_endstop1','secondary_work_face','greens_crease_land'}
  none={k:dict(h,contacts=[c for c in h.get('contacts',[]) if c['face'] in permitted_work]) for k,h in self.hands.items()}
  self.transit_hands=none
  for q in (a,b):
   hits,_,_=self.state(q,none)
   if hits:return dict(ok=False,method='RRT-Connect endpoint feasibility precheck',reason='endpoint outside transit free space; no contact window invented',states=self.calls,edges=self.edges,direct=direct,blockers=hits[:6],elapsed_s=time.monotonic()-began)
  trees=[([a],[None]),([b],[None])];reversed_=False;nodes=2
  def nearest(vs,x):return int(np.argmin([np.linalg.norm((v[self.ix]-x[self.ix])/self.scale) for v in vs]))
  def extend(tree,target):
   nonlocal nodes
   vs,parents=tree;i=nearest(vs,target);delta=(target[self.ix]-vs[i][self.ix])/self.scale;norm=np.linalg.norm(delta);q=vs[i].copy();q[self.ix]+=delta*self.scale*min(1,.25/max(norm,1e-12))
   edge=self.edge(vs[i],q,self.transit_hands,self.transit_hands,deadline=deadline)
   if not edge['ok']:return None,False
   vs.append(q);parents.append(i);nodes+=1;return len(vs)-1,norm<=.25
  def trace(tree,i):
   vs,pa=tree;out=[]
   while i is not None:out.append(vs[i]);i=pa[i]
   return list(reversed(out))
  while nodes<max_nodes and time.monotonic()<deadline:
   sample=a.copy();sample[self.ix]=self.rng.uniform(self.limits[:,0],self.limits[:,1])
   if self.rng.random()<.25:sample=trees[1][0][0].copy()
   i,_=extend(trees[0],sample)
   if i is not None:
    while time.monotonic()<deadline:
     j,reached=extend(trees[1],trees[0][0][i])
     if j is None:break
     if reached:
      path=trace(trees[0],i)+list(reversed(trace(trees[1],j)))
      if reversed_:path=list(reversed(path))
      return dict(ok=True,method='bidirectional RRT-Connect certified edges',path=[q.tolist() for q in path],nodes=nodes,states=self.calls,edges=self.edges,elapsed_s=time.monotonic()-began,seed=self.seed)
   trees.reverse();reversed_=not reversed_
  return dict(ok=False,method='bidirectional RRT-Connect',reason='finite CPU/time budget exhausted',nodes=nodes,states=self.calls,edges=self.edges,direct=direct,last_rejection=self.last,elapsed_s=time.monotonic()-began,seed=self.seed)
