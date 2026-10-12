from v7_common import *
import hashlib
from planner_r05 import Planner
data=read('idle.json'); rows=[]; rejects=[]; seen=set()
for group in ('task_fold','meal_end_return_diagnostic','explicit_unfold'):
 for r in data[group]['attempts']:
  if r['name'] not in ('direct','final_direct'):continue
  model=r['motion_model_xml']; ident=(model,r['name'],tuple(r['start_q']),tuple(r['goal_q']))
  if ident in seen:continue
  seen.add(ident)
  ch=v.scene(0);ch.xml=(I/model).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
  assert hashlib.sha256(ch.xml.encode()).hexdigest()==r['motion_model_sha256']
  assert sum(n.startswith('r07_closed_door_') for n in ch.gnames)==5
  assert not any(n.startswith(('idle_full_sweep_cover_','cabinet_door_sweep_')) for n in ch.gnames)
  ib=IndependentBound(ch);pl=Planner(ch,{},seconds=65)
  a=np.array(r['start_q']);b=np.array(r['goal_q']);name=r['name'].removeprefix('final_').removeprefix('local_');points=[a]
  if name.startswith('empty_jaws_open_'):
   opening=float(name.removeprefix('empty_jaws_open_'));aa=a.copy();bb=b.copy()
   for side in ('minus','plus'):aa[ch.qa['R_jaw_'+side]]=opening;bb[ch.qa['R_jaw_'+side]]=opening
   points +=[aa,bb]
  elif name.startswith('carriage_first_'):
   x=float(name.removeprefix('carriage_first_'));aa=a.copy();bb=b.copy();aa[ch.qa['R_carriage_x']]=x;bb[ch.qa['R_carriage_x']]=x;points +=[aa,bb]
  elif name.startswith('working_staging_'):points.append(mo.shortq(ch,a,np.array(candidate(int(name.removeprefix('working_staging_')))['poses'][0]['q'])))
  points.append(b);path=[a.tolist()];complete=len(r['edges'])==len(points)-1 and all(e.get('path') for e in r['edges'])
  for ei,(_,goal) in enumerate(zip(points,points[1:])):
   e=r['edges'][ei] if ei<len(r['edges']) else {}
   path.extend(e['path'][1:] if e.get('path') else [goal.tolist()])
  for direction,route in (('forward',path),('reverse',list(reversed(path)))):
   states=0;step=0.;bad=None;mt=0.
   for aa,bb in zip(np.array(route),np.array(route)[1:]):
    D=ib.segment(aa,bb);N=max(1,math.ceil(D/.004));step=max(step,D/N*1000)
    for k in range(N+1):
     q=aa+(bb-aa)*k/N;states+=1
     if not pl.state(q,{}):bad=dict(kind='gap',rejection=copy.deepcopy(pl.last));break
     tq=ch.torque_multi(q,{}, {})['ratio'];mt=max(mt,tq)
     if tq>1 or not all(not ch.m.jnt_limited[ch.jid[n]] or ch.m.jnt_range[ch.jid[n],0]-1e-8<=q[ix]<=ch.m.jnt_range[ch.jid[n],1]+1e-8 for n,ix in ch.qa.items()):bad=dict(kind='range/load');break
    if bad:break
   rows.append(dict(group=group,route=r['name'],direction=direction,model=model,saved_complete_path=complete,pass_=bad is None,states_checked=states,max_point_step_mm=step,max_torque_ratio=mt,blocker=bad))
   print(group,r['name'],direction,bad is None,states,flush=True)
  for e in r['edges']:
   last=e.get('last_rejection')
   if last:rejects.append(dict(group=group,route=r['name'],reproduced=not pl.state(np.array(last['q']),{}),blocker=copy.deepcopy(pl.last)))
  dump('fold.json',dict(routes=rows,rejections=rejects,states_checked=sum(x['states_checked'] for x in rows),full_idle_pass=False,method='Hash-matched per-attempt closed-door model. Saved successful edge prefixes retained; missing edges are declared direct/staging rejection diagnostics. Both directions checked with independent <=4mm bound. Initial raw-food unfolding and prospective completed-food folding use their own models.'))
