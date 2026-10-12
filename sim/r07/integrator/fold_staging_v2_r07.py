"""Ordered-arm staging retries; unchanged all-part4mm and mounted load gates."""
import os,sys,json,copy,time,math
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v2_r07 as v
from motion_v2_r07 import Planner
from point_bound import PointBound
path=v.O/'layouts'/f'{v.ID}_idle.json';out=json.loads(path.read_text());(v.H/'audit'/f'{v.ID}_idle_previous_{time.time_ns()}.json').write_text(json.dumps(out,indent=2))
index=int(sys.argv[2]);sg=v.items[index][1];ch=v.scene(104);ch.xml=(v.H/out['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.working_stroke=False;ch.contact_windows=[];pb=PointBound(ch)
for row in out['fold_paths']:
 if row['pass_'] or not row['endpoint_geometry_pass']:continue
 hands=sg['poses'][row['canonical_pose']];a=np.array(row['endpoint_reference']['poses'][0]['q']);b=np.array(row['park_q_equivalent_public_range']);trials=[]
 for order in (('L','R'),('R','L')):
  mid=a.copy()
  for n in v.s.ck.ARMS[order[0]]+[order[0]+'_carriage_x']:mid[ch.qa[n]]=b[ch.qa[n]]
  ch.hands=hands;ch.set_contacts(hands);hits,_,_=v.f.contacts(ch,mid)
  trial=dict(order=order,via=mid.tolist(),via_hits=hits,legs=[],pass_=False);trials.append(trial)
  if hits:continue
  combined=[]
  for side,start,end in ((order[0],a,mid),(order[1],mid,b)):
   pl=Planner(ch,hands,seed=995000+row['index']*10+len(trials),seconds=65);pl.names=v.s.ck.ARMS[side]+[side+'_carriage_x'];pl.ix=[ch.qa[n] for n in pl.names];pl.limits=np.array([ch.m.jnt_range[ch.jid[n]] for n in pl.names]);pl.scale=np.array([.5 if n.endswith('carriage_x') else 1. for n in pl.names]);v.s.PARK=end.copy();result=pl.plan(start,end,hands,hands);trial['legs'].append(result);print('STAGED_LEG',v.ID,row['index'],order,side,result['ok'],flush=True)
   if not result['ok']:break
   combined+=result['path'][bool(combined):]
  if len(trial['legs'])==2 and all(r['ok'] for r in trial['legs']):
   ratios=[];maximum=0.;valid=True;countstates=0
   for qa,qb in zip(np.array(combined),np.array(combined)[1:]):
    bound=pb.segment_bound(qa,qb);n=max(1,math.ceil(bound/.004));maximum=max(maximum,bound/n)
    for u in np.linspace(0,1,n+1):
     q=qa+(qb-qa)*u;torque=ch.torque_multi(q,hands,{s:[0,0,0] for s in hands},{s:[0,0,0] for s in hands});ratios.append(torque['ratio']);valid=valid and torque['ratio']<=1;countstates+=1
   trial.update(pass_=valid,max_envelope_ratio=max(ratios),load_states=countstates,max_point_step_mm=maximum*1000)
   if valid:
    row.update(pass_=True,reverse_unfold_pass=True,door_sweep_path_verified=True,reason=None,max_envelope_ratio=max(ratios),load_states=countstates,max_point_step_mm=maximum*1000,planner=dict(ok=True,path=combined,allocated_budget_s=130,planner_time_s=sum(r['planner_time_s'] for r in trial['legs']),seeds_tried=sum(r['seeds_tried'] for r in trial['legs']),route='Sequential arm staging; each leg65s with restarts and shortcutting, full4mm replay',max_point_step_mm=maximum*1000))
    break
 row['staging_attempts']=trials;path.write_text(json.dumps(out,indent=2));print('STAGED_FOLD',v.ID,row['index'],row['pass_'],flush=True)
out['pass_']=out['snapshot_pass'] and out['door_sweep_pass'] and all(r['pass_'] for r in out['fold_paths']);out['status']='PASS_CHECKED_CANONICAL_FOLDS' if out['pass_'] else 'FAIL_CANONICAL_WORKING_FOLD';path.write_text(json.dumps(out,indent=2))
