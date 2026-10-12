"""RRT-Connect, model-derived <=4mm point step, restarts and shortcuts."""
import time,copy,numpy as np,mujoco
from collections import Counter
import final_check as f
from point_bound import PointBound
s=f.s
class Planner:
 def __init__(self,ch,hands,seed=505,seconds=65):
  self.ch=ch;self.hands=copy.deepcopy(hands);self.rng=np.random.default_rng(seed);self.seed=seed;self.seconds=max(60,seconds)
  self.names=sum(s.ck.ARMS.values(),[])+[x+'_carriage_x' for x in s.model.SIDES];self.ix=[ch.qa[n] for n in self.names]
  self.limits=np.array([ch.m.jnt_range[ch.jid[n]] for n in self.names]);self.scale=np.array([.5 if n.endswith('carriage_x') else 1. for n in self.names])
  self.limits[self.names.index('R_carriage_x'),1]=.045;self.point=PointBound(ch);self.states=0;self.edges=0;self.last=None;self.blockers=Counter();self.max_step=0;self.step=.004;self.search_max_step=0
 def state(self,q,hands=None):
  self.states+=1;self.ch.set_contacts(hands or self.hands)
  self.ch.d.qpos[:]=q;mujoco.mj_kinematics(self.ch.m,self.ch.d)
  from policy_r05 import valid_window
  work={'clamped_food','wash_food','root_brush_work_face','secondary_work_face','greens_crease_land'}
  current=hands or self.hands
  self.ch.allowed=[c for c in self.ch.allowed if getattr(self.ch,'working_stroke',False) and (c['face'] in work or c['face']=='peel_food_land' and current[c['side']]['held']=='wash_pad') or any(w['side']==c['side'] and w['face']==c['face'] and valid_window(self.ch,w) for w in getattr(self.ch,'contact_windows',[]))]
  # A bidirectional free-transit tree retains one object's geometry but may
  # approach the destination's support. Its explicit, pose-qualified arrival
  # declaration must not disappear merely because the tree started at the
  # departure endpoint. The actual contact normal/face check remains required.
  for w in getattr(self.ch,'contact_windows',[]):
   if valid_window(self.ch,w) and w['side'] in current:
    c={k:w[k] for k in ('side','face','held_parts','reason') if k in w}
    if c not in self.ch.allowed:self.ch.allowed.append(c)
  hits,mins,audit=f.contacts(self.ch,q)
  # A positive MuJoCo margin record can underestimate the actual box gap
  # (the saved endstop diagnostic is2.5mm versus a certified5mm). Transit
  # accepts such a pair only with the unchanged physical gap proved by a
  # convex separating projection. Touch/penetration and all uncertain bounds
  # remain failures. This is not an intended-contact permission. Static/final
  # endpoint f.replay is untouched and still executes the original reference.
  remaining=[]
  for h in hits:
   clear=False
   if not h.get('reason') and h.get('real_gap_mm',0)>0:
    a,b=(self.ch.gnames.index(n) for n in h['pair']);v=self.ch.bounds.pair(a,b)
    clear=v['lower_m']>=h['required_gap_mm']/1000-1e-6
   if clear:
    if not hasattr(self,'proximity_discrepancies'):self.proximity_discrepancies=[]
    if len(self.proximity_discrepancies)<20:self.proximity_discrepancies.append(dict(pair=h['pair'],mujoco_margin_gap_mm=h['real_gap_mm'],convex_lower_gap_mm=v['lower_m']*1000,convex_upper_gap_mm=v['upper_m']*1000,required_mm=h['required_gap_mm']))
   else:remaining.append(h)
  hits=remaining
  for h in hits:self.blockers[' | '.join(h['pair'])]+=1
  if hits:self.last=dict(q=q.tolist(),blockers=hits[:8])
  return not hits
 def edge(self,a,b,ha=None,hb=None,deadline=None):
  self.edges+=1;a=np.array(a);b=np.array(b);bound=self.point.segment_bound(a,b);n=max(1,int(np.ceil(bound/self.step)))
  if self.step<=.004:self.max_step=max(self.max_step,bound/n)
  else:self.search_max_step=max(self.search_max_step,bound/n)
  common=copy.deepcopy(self.hands)
  if ha is not None and hb is not None:
   for side,h in common.items():h['contacts']=[c for c in ha.get(side,{}).get('contacts',[]) if c in hb.get(side,{}).get('contacts',[])]
  # Check endpoints before costly interior checks; all intervals are sampled on
  # the same uniform bounded grid, checking centre-out for early rejection.
  order=[0,n]+list(range(1,n))
  for k in order:
   if deadline and time.monotonic()>=deadline:return False
   q=a+(b-a)*(k/n);h=ha if k==0 and ha else hb if k==n and hb else common
   if not self.state(q,h):return False
  return True
 def result(self,ok,start,path=None,**extra):
  return dict(ok=ok,method='RRT-Connect / bounded discrete reference and convex check',allocated_budget_s=self.seconds,planner_time_s=time.monotonic()-start,seeds_tried=self.restarts,solutions_found=int(ok),verified_witnesses=int(ok),states_checked=self.states,edges_checked=self.edges,max_point_step_mm=self.max_step*1000,search_only_point_step_mm=self.search_max_step*1000,path=[] if path is None else [q.tolist() for q in path],path_length_scaled=None if path is None else float(sum(np.linalg.norm((b[self.ix]-a[self.ix])/self.scale) for a,b in zip(path,path[1:]))),blockers=[dict(pair=k.split(' | '),count=v) for k,v in self.blockers.most_common(10)],last_rejection=self.last,positive_margin_discrepancies=getattr(self,'proximity_discrepancies',[]),seed=self.seed,**extra)
 def plan(self,a,b,ha=None,hb=None):
  start=time.monotonic();deadline=start+self.seconds;self.restarts=1;a=np.array(a);b=np.array(b)
  self.step=.020
  if self.edge(a,b,ha,hb,deadline):
   self.step=.004
   if self.edge(a,b,ha,hb,time.monotonic()+180):return self.result(True,start,[a,b],route='direct proposal + full4mm replay',shortcut_trials=0,verification_budget_s=180)
   self.step=.020;deadline=time.monotonic()+self.seconds
  best=None;nodes=0
  def nearest(vs,x):return int(np.argmin([np.linalg.norm((v[self.ix]-x[self.ix])/self.scale) for v in vs]))
  def trace(tree,i):
   vs,ps=tree;out=[]
   while i is not None:out.append(vs[i]);i=ps[i]
   return list(reversed(out))
  while time.monotonic()<deadline:
   trees=[([a],[None]),([b],[None])];swapped=False;restart_end=min(deadline,time.monotonic()+12);self.restarts+=1
   def extend(tree,target):
    nonlocal nodes
    vs,ps=tree;i=nearest(vs,target);delta=(target[self.ix]-vs[i][self.ix])/self.scale;norm=np.linalg.norm(delta);q=vs[i].copy();q[self.ix]+=delta*self.scale*min(1,.18/max(norm,1e-12))
    if not self.edge(vs[i],q,ha,ha,deadline=restart_end):return None,False
    vs.append(q);ps.append(i);nodes+=1;return len(vs)-1,norm<=.18
   while time.monotonic()<restart_end:
    sample=a.copy();sample[self.ix]=self.rng.uniform(self.limits[:,0],self.limits[:,1])
    bias=self.rng.random()
    if bias<.3:sample=trees[1][0][0].copy()
    elif bias<.6:
     sample=np.array(s.PARK);sample[self.ix]+=self.rng.normal(0,.2,len(self.ix))*self.scale;sample[self.ix]=np.clip(sample[self.ix],self.limits[:,0],self.limits[:,1])
    i,_=extend(trees[0],sample)
    if i is not None:
     while time.monotonic()<restart_end:
      j,reached=extend(trees[1],trees[0][0][i])
      if j is None:break
      if reached:
       best=trace(trees[0],i)+list(reversed(trace(trees[1],j)))
       if swapped:best=list(reversed(best))
       break
    if best:break
    trees.reverse();swapped=not swapped
   if best:break
  if best:
   trials=0
   for _ in range(16):
    if time.monotonic()>=deadline or len(best)<3:break
    i,j=sorted(self.rng.choice(len(best),2,replace=False));trials+=1
    if j>i+1 and self.edge(best[i],best[j],ha,hb,deadline):best=best[:i+1]+best[j:]
   self.step=.004
   # Coarse search edges are proposals only. Every accepted segment is replayed
   # on the binding <=4mm grid, including both moving arms and held objects.
   verification_deadline=time.monotonic()+180
   if all(self.edge(x,y,ha,hb,verification_deadline) for x,y in zip(best,best[1:])):
    return self.result(True,start,best,route='bidirectional trees + shortcut + full4mm replay',nodes=nodes,shortcut_trials=trials,verification_budget_s=180)
   return self.result(False,start,reason='Proposed RRT path failed full4mm replay or exhausted verification budget',nodes=nodes,proposed_nodes=len(best))
  return self.result(False,start,reason='60+s search with restarts exhausted; no accepted path',nodes=nodes)
