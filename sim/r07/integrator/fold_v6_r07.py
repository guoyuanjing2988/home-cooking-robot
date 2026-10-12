"""Carriage-first and arm-staging full65s paths in the populated idle scene."""
import os,sys,json,time,math,hashlib,xml.etree.ElementTree as E
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v6_r07 as v
import numpy as np,mujoco
from motion_v6_r07 import Planner,mo
from point_bound import PointBound
ID=v.ID;O=v.O;H=v.H;start=time.monotonic();idle=json.loads((O/'layouts'/f'{ID}_idle.json').read_text());initial_state=None
if '--unfold' in sys.argv:
 import persistent_v6_r07 as p
 initial_world=p.World();ch,_=initial_world.build(0,None);initial_state=initial_world.snapshot()
else:
 ch=v.scene(58);ch.xml=(H/idle['model_xml']).read_text()
root=E.fromstring(ch.xml);world=root.find('worldbody')
for g in list(world.findall('geom')):
 if g.get('name','').startswith('idle_full_sweep_cover_'):world.remove(g)
ch.xml=E.tostring(root,encoding='unicode');motion_model=f'models/{ID}_'+('return' if '--meal-end' in sys.argv else 'unfold' if '--unfold' in sys.argv else 'fold')+'_closed_doors.xml';(H/motion_model).write_text(ch.xml);ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
meal_end='--meal-end' in sys.argv;source_index=58 if meal_end else 0
work=json.loads((O/'static_v6'/ID/f'{source_index}.json').read_text())['witness'];working=np.array(work['poses'][-1 if meal_end else 0]['q']);park=mo.shortq(ch,working,np.array(idle['q']));v.s.PARK=park.copy();pb=PointBound(ch);suffix='return_v6' if meal_end else 'fold_v6';out=O/'layouts'/f'{ID}_{suffix}.json';result=json.loads(out.read_text()) if out.exists() else dict(layout=ID,pass_=False,attempts=[],model_xml=motion_model,model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),meal_end_return_executed=False,idle_all_robot_sweep_gap_mm=10,motion_door_scope="closed leaves and cabinet bodies; no sweep covers",source_stroke=source_index,scope='Prospective populated completed-meal scene; this return is not an executed meal prefix.')
if '--unfold' in sys.argv:
 working,park=park,working;v.s.PARK=park.copy();suffix='unfold_v6';out=O/'layouts'/f'{ID}_{suffix}.json';result=json.loads(out.read_text()) if out.exists() else dict(layout=ID,pass_=False,attempts=[],model_xml=motion_model,model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),meal_end_return_executed=False,idle_all_robot_sweep_gap_mm=10,motion_door_scope='closed leaves and cabinet bodies; no sweep covers',source_stroke=0,scope='Explicit empty-hand park-to-working deployment in the initial full raw-food and stored-object registry; no meal execution credit.')
 assert result['model_sha256']==hashlib.sha256(ch.xml.encode()).hexdigest(), 'Do not mix unfolding scenes in one record'
 probe=Planner(ch,{},seconds=65);clear=probe.state(working,{})
 result.update(initial_state=initial_state,initial_park_environment_check=dict(collision_free=clear,blocker=probe.last if not clear else None,full_sweep_and_front_strip_certificate='results/layouts/'+ID+'_idle.json',same_robot_configuration=True))
goals=[('direct',[])]
for opening in (.015,.025,.04):
 jaw_work=working.copy();jaw_park=park.copy()
 for side in ('minus','plus'):jaw_work[ch.qa['R_jaw_'+side]]=opening;jaw_park[ch.qa['R_jaw_'+side]]=opening
 goals.append(('empty_jaws_open_'+str(opening),[jaw_work,jaw_park]))
for x in (-1.5,-1.1,-.7,-.3,.15,.4):
 stage=working.copy();stage[ch.qa['R_carriage_x']]=x;stagepark=park.copy();stagepark[ch.qa['R_carriage_x']]=x;goals.append(('carriage_first_'+str(x),[stage,stagepark]))
for i in (1,2,20,40,5,21):
 file=O/'static_v6'/ID/f'{i}.json'
 if file.exists():
  d=json.loads(file.read_text())
  if d.get('witness'):goals.append(('working_staging_'+str(i),[mo.shortq(ch,working,np.array(d['witness']['poses'][0]['q']))]))
done={a['name'] for a in result['attempts']}
for name,middle in goals:
 if '--local-retry' in sys.argv:name='local_'+name
 if '--final' in sys.argv:name='final_'+name
 if name in done:continue
 if '--short-study' in sys.argv and len(result['attempts'])>=3:break
 if time.monotonic()-start>890:break
 row=dict(name=name,pass_=False,edges=[],states=[],states_checked=0,allocated_per_edge_s=65)
 row.update(source_static_sha256=hashlib.sha256((O/'static_v6'/ID/f'{source_index}.json').read_bytes()).hexdigest(),start_q=working.tolist(),goal_q=park.tolist(),motion_model_xml=motion_model,motion_model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest())
 points=[working]+middle+[park]
 for ei,(a,b) in enumerate(zip(points,points[1:])):
  pl=Planner(ch,{},seed=982000+len(result['attempts'])*10+ei,seconds=65);edge=pl.plan(a,b,{},{});row['edges'].append(edge)
  if not edge['ok']:break
  valid=True;step=0.;ratio=0.;states=[]
  for si,(x,y) in enumerate(zip(np.array(edge['path']),np.array(edge['path'])[1:])):
   bound=pb.segment_bound(x,y);n=max(1,math.ceil(bound/.004));step=max(step,bound/n)
   for k in range(n+1):
    q=x+(y-x)*k/n;valid=pl.state(q,{}) and all(not ch.m.jnt_limited[ch.jid[nm]] or ch.m.jnt_range[ch.jid[nm],0]-1e-8<=q[ix]<=ch.m.jnt_range[ch.jid[nm],1]+1e-8 for nm,ix in ch.qa.items());tq=ch.torque_multi(q,{}, {})['ratio'];ratio=max(ratio,tq);valid=valid and tq<=1;states.append(dict(q=q.tolist(),segment=si,alpha=k/n))
    if not valid:break
   if not valid:break
  edge['fresh_replay']=dict(pass_=valid,states_checked=len(states),max_point_step_mm=step*1000,max_envelope_ratio=ratio);row['states']+=states;row['states_checked']+=len(states)
  if not valid:break
 row['pass_']=idle['snapshot_pass'] and len(row['edges'])==len(points)-1 and all(e['ok'] and e.get('fresh_replay',{}).get('pass_') for e in row['edges'])
 if row['pass_']:row['reverse_unfold_pass']=all(pl.state(np.array(s['q']),{}) for s in reversed(row['states']));row['pass_']=row['reverse_unfold_pass']
 result['attempts'].append(row);result['pass_']=any(a['pass_'] for a in result['attempts']);out.write_text(json.dumps(result,indent=2));print('FOLD',name,row['pass_'],flush=True)
 if row['pass_']:break
