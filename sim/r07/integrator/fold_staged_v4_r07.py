"""Full completed-food scene, explicit checked staging postures,65s per edge."""
import sys,os,json,hashlib,time,math
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v4_r07 as v
import numpy as np,mujoco
from motion_v4_r07 import Planner,mo
from point_bound import PointBound
ID=v.ID;H=v.H;O=v.O;idle=json.loads((O/'layouts'/f'{ID}_idle.json').read_text());ch=v.scene(len(v.items)-1);ch.xml=(H/idle['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
working_record=json.loads((O/'static_v4'/ID/'0.json').read_text());working=np.array(working_record['witness']['poses'][0]['q']);park=mo.shortq(ch,working,np.array(idle['q']));pb=PointBound(ch);rows=[];started=time.monotonic();v.s.PARK=park.copy()
for index in (1,2,20,40,5,21):
 if time.monotonic()-started>940:break
 file=O/'static_v4'/ID/f'{index}.json'
 if not file.exists():continue
 record=json.loads(file.read_text());w=record.get('witness')
 if not w or not record.get('complete'):continue
 stage=mo.shortq(ch,park,np.array(w['poses'][0]['q']));pre=Planner(ch,{},seconds=65);stage_ok=pre.state(stage,{})
 row=dict(staging_stroke=index,source_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),stage_full_scene_clear=stage_ok,stage_rejection=pre.last if not stage_ok else None,pass_=False,edges=[],path=[],states_checked=0,scope='Same empty-hand completed-food scene; task pose is a staging proposal only; all sweeps10mm.')
 if stage_ok:
  points=[park,stage,mo.shortq(ch,stage,working)]
  for ei,(a,b) in enumerate(zip(points,points[1:])):
   pl=Planner(ch,{},seed=951500+index*10+ei,seconds=65);result=pl.plan(a,b,{},{});row['edges'].append(result)
   if not result['ok']:break
   path=np.array(result['path']);valid=True;states=0;maxratio=0.;step=0.
   for x,y in zip(path,path[1:]):
    bound=pb.segment_bound(x,y);n=max(1,math.ceil(bound/.004));step=max(step,bound/n)
    for k in range(n+1):
     q=x+(y-x)*k/n
     if not pl.state(q,{}):valid=False;break
     ratio=ch.torque_multi(q,{}, {})['ratio'];maxratio=max(maxratio,ratio);valid=valid and ratio<=1 and all(not ch.m.jnt_limited[ch.jid[name]] or ch.m.jnt_range[ch.jid[name],0]-1e-8<=q[ix]<=ch.m.jnt_range[ch.jid[name],1]+1e-8 for name,ix in ch.qa.items());states+=1
     if not valid:break
    if not valid:break
   result['fresh_replay']=dict(pass_=valid,states=states,max_envelope_ratio=maxratio,max_point_step_mm=step*1000)
   if not valid:break
   row['path']+=result['path'] if not row['path'] else result['path'][1:];row['states_checked']+=states
  row['pass_']=bool(len(row['edges'])==2 and all(e['ok'] and e.get('fresh_replay',{}).get('pass_') for e in row['edges']))
  if row['pass_']:
   for x,y in zip(np.array(row['path'])[::-1],np.array(row['path'])[::-1][1:]):
    n=max(1,math.ceil(pb.segment_bound(x,y)/.004))
    if not all(pl.state(x+(y-x)*k/n,{}) for k in range(n+1)):row['pass_']=False;break
 rows.append(row);(O/'layouts'/f'{ID}_fold_staged.json').write_text(json.dumps(dict(layout=ID,pass_=any(r['pass_'] for r in rows),attempts=rows,model_xml=idle['model_xml'],model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),executed_meal_end_return=False,scope='Fold/unfold from actual empty-hand standby using explicit full-scene checked staging postures. Complete preceding meal remains unexecuted.'),indent=2));print('STAGED_FOLD',index,row['pass_'],row['states_checked'],flush=True)
 if row['pass_']:break
