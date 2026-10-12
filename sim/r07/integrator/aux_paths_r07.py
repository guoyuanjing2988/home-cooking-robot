"""Verified local empty-arm diagnostic; never credited as meal or idle."""
import json,time,xml.etree.ElementTree as E,copy
import numpy as np,mujoco
import r07_runtime as rt
from planner_r05 import Planner
from point_bound import PointBound
H=rt.H;O=rt.O;s=rt.s
bare=[]
for file in O.glob('park_full_iteration_*.json'):
 p=json.loads(file.read_text())
 if p.get('pass_') and abs(p['config'].get('helper_y',0)-.427)<1e-8:bare.append(p)
assert bare
p=bare[-1];q=np.array(p['q']);tr,meta=s.model.build()
ch=object.__new__(rt.Checker);ch.desc=s.ck.hand([0,0,1],jaw_axis=[0,1,0]);ch.bind_model(mujoco.MjModel.from_xml_string(E.tostring(tr.getroot(),encoding='unicode')));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
base_hits,mins,audit=rt.f.contacts(ch,q);rows=[];path=None
for side,delta in [('R',.025),('R',-.025),('L',.025),('L',-.025)]:
 goal=q.copy();goal[ch.qa[side+'_carriage_x']]+=delta
 pl=Planner(ch,{},seed=727,seconds=65)
 if base_hits or not pl.edge(q,goal):continue
 result=pl.plan(q,goal)
 if result['ok']:
  path=result['path']+[q.tolist()];break
if path:
 pb=PointBound(ch);samples=[];bad=[]
 for a,b in zip(np.array(path),np.array(path)[1:]):
  n=max(1,int(np.ceil(pb.segment_bound(a,b)/.004)))
  for k in range(n+1):
   v=a+(b-a)*k/n
   if not pl.state(v):bad.append(pl.last);break
   tq=ch.torque_multi(v,{},{});samples.append(dict(q=v.tolist(),torque_ratio=tq['ratio']))
   if tq['ratio']>1:bad.append(tq);break
  if bad:break
 out=dict(pass_=not bad,path=path,samples=samples,planner=result,blockers=bad,model_xml='models/aux_empty_fixed_kitchen.xml',scope='Executed kinematic local empty-carriage shuttle with original fixed kitchen, full OEM arms, new rails/chains and full installed fixtures/appliance. Stored loose tools/bowls/raw food are absent. This is neither a meal path nor populated idle evidence.',full_meal_state_verified=False)
else:out=dict(pass_=False,path=[],blockers=base_hits,reason='No fully checked local shuttle',scope='Fixed-kitchen diagnostic only')
rt.write('aux_paths.json',out)
(H/'models/aux_empty_fixed_kitchen.xml').write_text(E.tostring(tr.getroot(),encoding='unicode'))
# Explicit passing attempt with the same complete fixed hardware. Even empty
# source/goal tucks do not establish loaded passing or a conserved meal.
goal=q.copy();a=ch.qa['R_carriage_x'];b=ch.qa['L_carriage_x'];goal[a],goal[b]=q[b],q[a]
pl2=Planner(ch,{},seed=728,seconds=65);passing=pl2.plan(q,goal)
rt.write('passing.json',dict(pass_=passing['ok'],planner=passing,q_crossing=((q+goal)/2).tolist(),scope='Empty-arm fixed-kitchen crossing diagnostic; no loaded or meal passing credit',full_meal_state_verified=False))
print('aux local',out['pass_'],'passing',passing['ok'],flush=True)
