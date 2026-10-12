"""Connect actual final empty-hand task pose to populated park with full sweeps."""
import os,sys,json,time,hashlib,math
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v4_r07 as v
import numpy as np,mujoco
from motion_v2_r07 import Planner,mo
from point_bound import PointBound
ID=v.ID;O=v.O;H=v.H;idle=json.loads((O/'layouts'/f'{ID}_idle.json').read_text());ch=v.scene(len(v.items)-1)
ch.xml=(H/idle['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
park=np.array(idle['q']);pb=PointBound(ch);rows=[]
source=O/'static_v4'/ID/'0.json';saved=json.loads(source.read_text());w=saved['witness'];assert w
working=np.array(w['poses'][0]['q']);park=mo.shortq(ch,working,park);ch.seg=dict(ch.seg,poses=[v.items[-1][1]['poses'][0]])
endpoint=v.f.replay(ch,dict(k=w['k'],poses=[dict(q=working.tolist())]));v.s.PARK=park.copy()
for seed in (84501,84502,84503):
 start=time.monotonic();pl=Planner(ch,{},seed=seed,seconds=65);result=pl.plan(working,park,{},{});states=[];maxstep=0.;maximum=0.;reserves={};ok=endpoint['ok'] and idle['snapshot_pass'] and result['ok']
 if ok:
  for si,(a,b) in enumerate(zip(np.array(result['path']),np.array(result['path'])[1:])):
   bound=pb.segment_bound(a,b);n=max(1,math.ceil(bound/.004));maxstep=max(maxstep,bound/n)
   for j in range(n+1):
    q=a+(b-a)*j/n
    if not pl.state(q,{}):ok=False;break
    tq=ch.torque_multi(q,{},{});maximum=max(maximum,tq['ratio']);ok=ok and tq['ratio']<=1
    ranges=all(ch.m.jnt_range[ch.jid[name],0]-1e-8<=q[ix]<=ch.m.jnt_range[ch.jid[name],1]+1e-8 for name,ix in ch.qa.items());ok=ok and ranges
    states.append(dict(q=q.tolist(),segment=si,alpha=j/n))
    for cat,ix in ch.bounds.catids.items():
     vals=ch.bounds.last_lower[ix]-ch.bounds.need[ix];valid=vals[vals<1e3]
     if len(valid):reserves.setdefault(cat,[]).append(float(min(valid)*1000))
   if not ok:break
  if ok:
   for state in reversed(states):
    if not pl.state(np.array(state['q']),{}):ok=False;break
 row=dict(seed=seed,allocated_s=65,elapsed_s=time.monotonic()-start,pass_=ok,planner=result,states=states,states_checked=len(states),max_point_step_mm=maxstep*1000,max_envelope_ratio=maximum,state_minimum_reserves_mm=reserves)
 rows.append(row);print('TASK_FOLD',seed,ok,len(states),flush=True)
 out=dict(layout=ID,pass_=any(r['pass_'] for r in rows),model_xml=idle['model_xml'],model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),source_witness=str(source.relative_to(H)),source_witness_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),jaw_axis_branch=w['k'],working_endpoint_reference=endpoint,attempts=rows,executed_meal_end_return=False,scope='Full folded park <-> actual final empty-hand standby target, completed-food scene, full5-door sweep covers and10mm EOAT/door gate. Actual preceding meal remains unexecuted.')
 out['periodic_park_q']=park.tolist();out['periodic_park_policy']='Equivalent full geometry with nearest admissible2pi winding, within published joint ranges; complete path still checked.'
 (O/'layouts'/f'{ID}_task_fold_periodic.json').write_text(json.dumps(out,indent=2))
 if ok:break
