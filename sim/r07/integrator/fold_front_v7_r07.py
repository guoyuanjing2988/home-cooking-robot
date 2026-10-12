"""Full-budget fold via collision-aware Cartesian stages in the open front strip."""
import os,sys,json,time,copy,hashlib,math
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v7_r07 as v
from motion_v7_r07 import Planner
from least_analytic_v7_r07 import solve
from point_bound import PointBound
began=time.monotonic();ID=v.ID;O=v.O;H=v.H
mode='unfold' if '--unfold' in sys.argv else 'return' if '--meal-end' in sys.argv else 'fold'
high='--high' in sys.argv;tag=mode+('_high' if high else '');height=1.50 if high else 1.20
targets=[(x,down) for x in ((-.4,0.,.3) if high else (-.8,-.4,0.,.3)) for down in (False,True)]
idle=json.loads((O/'layouts'/f'{ID}_idle.json').read_text());index=58 if mode=='return' else 0
source=O/'static_v7'/ID/f'{index}.json';work=json.loads(source.read_text())['witness'];working=np.array(work['poses'][-1 if mode=='return' else 0]['q']);park=np.array(idle['q'])
if mode=='unfold':
 import persistent_v7_r07 as p
 ch,_=p.World().build(0,None)
else:
 ch=v.scene(index);ch.xml=(H/'models'/f'{ID}_fold_closed_doors.xml').read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml))
ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False;ch.search_carriage=True;ch.lock_initial_carriage=False;ch.night_robust=False
assert not any(n.startswith(('cabinet_door_sweep_','idle_full_sweep_cover_')) for n in ch.gnames)
model=f'models/{ID}_{tag}_front_closed_doors.xml';(H/model).write_text(ch.xml);pb=PointBound(ch)
a,b=(park,working) if mode=='unfold' else (working,park)
file=O/'layouts'/f'{ID}_{tag}_front_v7.json';out=json.loads(file.read_text()) if file.exists() else dict(layout=ID,mode=mode,staging_height_m=height,pass_=False,attempts=[],model_xml=model,model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),source_static_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),scope='Explicit front-strip Cartesian staging in full closed-door scene. Prospective completed scene for fold/return, initial raw-food scene for unfold. No meal execution credit.')
assert out['model_sha256']==hashlib.sha256(ch.xml.encode()).hexdigest()
done={r['candidate'] for r in out['attempts']}
for candidate,(x,down) in enumerate(targets):
 if candidate in done or out['pass_']:continue
 if time.monotonic()-began>550:break
 h=copy.deepcopy(v.items[0][1]['poses'][0]['R']);h.update(pos=[x,-.10,height],approach=[0,0,-1] if down else [0,1,0],jaw_axis=[0,1,0] if down else [0,0,1],roll_deg=0,jaw_opening_m=0,contacts=[],held='empty',held_kg=0,mass_offset_m=0,work_offset_m=0,nominal_forces_N=[[0,0,0]],check_forces_N=[[0,0,0]],nominal_moments_Nm=[[0,0,0]],check_moments_Nm=[[0,0,0]])
 row=dict(candidate=candidate,target=h,ik=[],edges=[],states=[],pass_=False,start_q=a.tolist(),goal_q=b.tolist(),park_q=park.tolist(),allocated_per_edge_s=65,source_static_sha256=out['source_static_sha256'],motion_model_xml=model,motion_model_sha256=out['model_sha256']);stage=None
 for seed,q0 in enumerate((a,b)):
  q=q0.copy();q[ch.qa['R_jaw_minus']]=q[ch.qa['R_jaw_plus']]=0;ch.hands={'R':h};ch.set_contacts(ch.hands);ch.working_stroke=False;started=time.monotonic()
  q,errors,hits,_=solve(ch,q,{'R':h},0,started+20)
  probe=Planner(ch,{},seconds=65);clear=probe.state(q,{})
  good=clear and all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in errors)
  row['ik'].append(dict(seed=seed,allocated_s=20,elapsed_s=time.monotonic()-started,errors=errors,pass_=good,blocker=probe.last if not clear else None))
  if good:stage=q.copy();break
 if stage is not None:
  ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
  row['stage_q']=stage.tolist();valid=True;maximum_step=0.;maximum_ratio=0.;points=[a,stage]
  if not down:
   aligned=stage.copy();aligned[ch.qa['R_carriage_x']]=b[ch.qa['R_carriage_x']];probe=Planner(ch,{},seconds=65);clear=probe.state(aligned,{})
   row['carriage_alignment']=dict(q=aligned.tolist(),clear=bool(clear),blocker=None if clear else probe.last)
   if clear and np.max(abs(aligned-stage))>1e-8:points.append(aligned)
  points.append(b);row['planned_legs']=len(points)-1
  for leg,(qa,qb) in enumerate(zip(points,points[1:])):
   pl=Planner(ch,{},seed=986000+candidate*10+leg,seconds=65);v.s.PARK=qb.copy();edge=pl.plan(qa,qb,{},{});row['edges'].append(edge)
   if not edge['ok']:valid=False;break
   path=np.array(edge['path']);continuity=np.max(abs(path[0]-qa))<=1e-7 and np.max(abs(path[-1]-qb))<=1e-7
   edge['endpoint_joint_continuity']=bool(continuity);valid=bool(continuity);deadline=time.monotonic()+60;states=[];bad=None
   if valid:
    for si,(u,z) in enumerate(zip(path,path[1:])):
     bound=pb.segment_bound(u,z);n=max(1,math.ceil(bound/.004));maximum_step=max(maximum_step,bound/n)
     for k in range(n+1):
      q=u+(z-u)*k/n
      if time.monotonic()>deadline:valid=False;bad={'reason':'independent replay timeout'};break
      valid=pl.state(q,{}) and all(not ch.m.jnt_limited[ch.jid[nm]] or ch.m.jnt_range[ch.jid[nm],0]-1e-8<=q[ix]<=ch.m.jnt_range[ch.jid[nm],1]+1e-8 for nm,ix in ch.qa.items())
      ratio=float(ch.torque_multi(q,{}, {})['ratio']);maximum_ratio=max(maximum_ratio,ratio);valid=bool(valid and ratio<=1)
      if not valid:bad={'reason':'gap, joint or load','blocker':pl.last,'ratio':ratio};break
      states.append(dict(q=q.tolist(),leg=leg,segment=si,alpha=k/n))
     if not valid:break
   edge['fresh_replay']=dict(pass_=valid,states_checked=len(states),blocker=bad,max_point_step_mm=maximum_step*1000,max_envelope_ratio=maximum_ratio)
   row['states']+=states
   if not valid:break
  row.update(pass_=bool(valid and len(row['edges'])==len(points)-1 and idle['snapshot_pass']),max_point_step_mm=maximum_step*1000,max_envelope_ratio=maximum_ratio,states_checked=len(row['states']))
 out['attempts'].append(row);out['pass_']=any(r['pass_'] for r in out['attempts']);out['complete']=len(out['attempts'])==len(targets) or out['pass_'];file.write_text(json.dumps(out,indent=None,allow_nan=False));print('FRONT_STAGE',tag,candidate,row['pass_'],len(row['edges']),flush=True)
