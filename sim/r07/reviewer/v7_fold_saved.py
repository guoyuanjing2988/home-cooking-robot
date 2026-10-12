from v7_common import *
import hashlib
from planner_r05 import Planner
rows=[];rejects=[];seen=set();data=read('idle.json')
for group in ('task_fold','meal_end_return_diagnostic','explicit_unfold'):
 for r in data[group]['attempts']:
  model=r['motion_model_xml'];key=(model,r['name'])
  if key in seen:continue
  seen.add(key);ch=v.scene(0);ch.xml=(I/model).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False;pl=Planner(ch,{},seconds=65);ib=IndependentBound(ch)
  assert hashlib.sha256(ch.xml.encode()).hexdigest()==r['motion_model_sha256']
  for ei,e in enumerate(r['edges']):
   last=e.get('last_rejection')
   if last:rejects.append(dict(group=group,attempt=r['name'],edge=ei,reproduced=not pl.state(np.array(last['q']),{}),blocker=copy.deepcopy(pl.last)))
   if not e.get('path'):continue
   path=e['path'];states=0;step=0.;bad=None
   for direction,pth in [('forward',path),('reverse',list(reversed(path)))]:
    for a,b in zip(np.array(pth),np.array(pth)[1:]):
     D=ib.segment(a,b);N=max(1,math.ceil(D/.004));step=max(step,D/N*1000)
     for k in range(N+1):
      q=a+(b-a)*k/N;states+=1
      if not pl.state(q,{}) or ch.torque_multi(q,{},{})['ratio']>1:bad=copy.deepcopy(pl.last) or {'reason':'torque'};break
     if bad:break
    if bad:break
   rows.append(dict(group=group,attempt=r['name'],edge=ei,pass_=bad is None,states_checked=states,max_point_step_mm=step,blocker=bad));print('PREFIX',group,r['name'],ei,bad is None,states,flush=True)
  dump('fold_saved_edges.json',dict(saved_edges=rows,rejections=rejects,unique_attempts=len(seen),full_routes_passed=0,scope='Every available saved successful edge prefix replayed both directions. Every saved rejection replayed in exact closed-door source model. Missing failed edges are not paths.'))
