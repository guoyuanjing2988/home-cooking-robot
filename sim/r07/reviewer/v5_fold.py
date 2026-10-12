from v5_common import *
from planner_r05 import Planner
data=read('idle.json');ch=v.scene(58);ch.xml=(I/data['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
ib=IndependentBound(ch);pl=Planner(ch,{},seconds=65);previous=json.loads((O/'fold.json').read_text()) if (O/'fold.json').exists() else {};rows=previous.get('routes',[]);rejects=previous.get('rejections',[])
park0=np.array(data['q'])
def run(label,path,saved):
 states=0;step=0.;bad=None;mt=0.
 for a,b in zip(np.array(path),np.array(path)[1:]):
  D=ib.segment(a,b);N=max(1,math.ceil(D/.004));step=max(step,D/N*1000)
  for k in range(N+1):
   q=a+(b-a)*k/N;states+=1
   if not pl.state(q,{}):bad=dict(kind='gap',rejection=pl.last);break
   tq=ch.torque_multi(q,{}, {})['ratio'];mt=max(mt,tq)
   if tq>1 or not all(not ch.m.jnt_limited[ch.jid[n]] or ch.m.jnt_range[ch.jid[n],0]-1e-8<=q[ix]<=ch.m.jnt_range[ch.jid[n],1]+1e-8 for n,ix in ch.qa.items()):bad=dict(kind='range/load');break
  if bad:break
 rows.append(dict(route=label,saved_path=saved,pass_=bad is None,states_checked=states,max_point_step_mm=step,max_torque_ratio=mt,blocker=bad));print(label,bad is None,states,flush=True)
for group in ('task_fold','meal_end_return_diagnostic'):
 d=data[group];idx=d['source_stroke'];work=np.array(candidate(idx)['poses'][-1 if idx==58 else 0]['q']);park=mo.shortq(ch,work,park0)
 for r in d['attempts']:
  if all(any(x['route']==group+'/'+r['name']+'/'+direction for x in rows) for direction in ('fold','unfold')):continue
  name=r['name'];points=[work]
  if name.startswith('carriage_first_'):
   x=float(name.removeprefix('carriage_first_'));a=work.copy();b=park.copy();a[ch.qa['R_carriage_x']]=x;b[ch.qa['R_carriage_x']]=x;points +=[a,b]
  elif name.startswith('working_staging_'):points.append(mo.shortq(ch,work,np.array(candidate(int(name.removeprefix('working_staging_')))['poses'][0]['q'])))
  points.append(park)
  path=[];complete=len(r['edges'])==len(points)-1 and all(e.get('path') for e in r['edges'])
  if complete:
   for e in r['edges']:path.extend(e['path'] if not path else e['path'][1:])
  else:path=[x.tolist() for x in points]
  run(group+'/'+name+'/fold',path,complete);run(group+'/'+name+'/unfold',list(reversed(path)),complete)
  for e in r['edges']:
   last=e.get('last_rejection')
   if last:rejects.append(dict(route=group+'/'+name,reproduced=not pl.state(np.array(last['q']),{}),blocker=pl.last))
  dump('fold.json',dict(routes=rows,rejections=rejects,states_checked=sum(x['states_checked'] for x in rows),full_idle_pass=False,method='Replay saved complete routes if present; otherwise exact submitted direct/staging proposal in both directions at independent <=4mm bound, stopping at rejection. No planner failure proves architectural impossibility.'))
