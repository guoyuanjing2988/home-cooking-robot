"""Fold/unfold from admitted canonical empty-hand working poses, full idle scene."""
import os,sys,json,copy,time,math
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v2_r07 as v
from motion_v2_r07 import Planner,mo
from point_bound import PointBound
from least_analytic_v2_r07 import solve as collision_ik
index=int(sys.argv[2]);path=v.O/'layouts'/f'{v.ID}_idle.json';old=json.loads(path.read_text())
(v.H/'audit'/f'{v.ID}_idle_previous_{time.time_ns()}.json').write_text(json.dumps(old,indent=2))
saved=json.loads((v.O/'static_v2'/v.ID/f'{index}.json').read_text());w=saved['witness'];assert w
sg=v.items[index][1];assert all(h['held']=='empty' for pose in sg['poses'] for h in pose.values())
ch=v.scene(104);ch.xml=(v.H/old['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.allowed=[];ch.hands={};ch.contact_windows=[];ch.working_stroke=False
park=np.array(old['q']);hits,mins,_=v.f.contacts(ch,park);hold=ch.torque_multi(park,{},{});ranges=all(ch.m.jnt_range[ch.jid[n],0]-1e-8<=park[ch.qa[n]]<=ch.m.jnt_range[ch.jid[n],1]+1e-8 for n in ch.qa)
out=copy.deepcopy(old);out.update(pass_=False,fold_paths=[],snapshot_pass=bool(old['snapshot_pass'] and not hits and hold['ratio']<=1 and ranges),snapshot_torque=hold,snapshot_public_ranges_ok=ranges,working_pose_source=f'results/static_v2/{v.ID}/{index}.json',status='CHECKING_CANONICAL_WORKING_POSES')
path.write_text(json.dumps(out,indent=2));pb=PointBound(ch)
for pi,hands in enumerate(sg['poses']):
 qwork=np.array(w['poses'][pi]['q']);qpark=mo.shortq(ch,qwork,park);ch.seg=dict(sg,poses=[hands]);ch.hands=hands;ch.set_contacts(hands);ch.contact_windows=[];ch.working_stroke=False
 endpoint=v.f.replay(ch,dict(k=w['k'],poses=[dict(q=qwork.tolist())]));ikrows=[]
 if '--refine' in sys.argv and not endpoint['ok']:
  best=(sum(len(p['forbidden']) for p in endpoint['poses']),qwork.copy(),endpoint)
  for seed in range(8):
   started=time.monotonic();rng=np.random.default_rng(986000+pi*100+seed);init=qwork.copy()
   if seed%2==0:
    for side in ('R','L'):
     if side not in hands:
      for name in v.s.ck.ARMS[side]+[side+'_carriage_x']:init[ch.qa[name]]=park[ch.qa[name]]
   if seed:
    for side in hands:
     for name in v.s.ck.ARMS[side]+[side+'_carriage_x']:
      j=ch.jid[name];init[ch.qa[name]]=np.clip(init[ch.qa[name]]+rng.normal(0,.1),*ch.m.jnt_range[j])
   trial,errors,hs,_=collision_ik(ch,init,hands,w['k'],started+20);checked=v.f.replay(ch,dict(k=w['k'],poses=[dict(q=trial.tolist())]));score=sum(len(p['forbidden']) for p in checked['poses'])+sum(e['position_mm']+e['orientation_deg'] for e in errors)
   ikrows.append(dict(seed=seed,allocated_s=20,actual_s=time.monotonic()-started,pass_=checked['ok'],errors=errors,forbidden_records=len(hs)))
   if checked['ok']:qwork=trial;endpoint=checked;break
   if score<best[0]:best=(score,trial.copy(),checked)
  if not endpoint['ok']:_,qwork,endpoint=best
  qpark=mo.shortq(ch,qwork,park)
 v.s.PARK=qpark.copy();planner=Planner(ch,hands,seed=985000+pi,seconds=65);result=planner.plan(qwork,qpark,hands,hands)
 loads=[];loadok=True;steps=[];samples=0
 if result['ok']:
  for a,b in zip(np.array(result['path']),np.array(result['path'])[1:]):
   bound=pb.segment_bound(a,b);count=max(1,math.ceil(bound/.004));steps.append(bound/count)
   for alpha in np.linspace(0,1,count+1):
    q=a+(b-a)*alpha;tq=ch.torque_multi(q,hands,{side:[0,0,0] for side in hands},{side:[0,0,0] for side in hands});loads.append(tq['ratio']);loadok=loadok and tq['ratio']<=1;samples+=1
 ok=bool(out['snapshot_pass'] and endpoint['ok'] and result['ok'] and loadok)
 out['fold_paths'].append(dict(index=pi,working_tcp_m={s:h['pos'] for s,h in hands.items()},canonical_stroke=v.items[index][2],canonical_pose=pi,endpoint_starts=saved['starts'],endpoint_refinement=ikrows,endpoint_geometry_pass=endpoint['ok'],endpoint_reference=endpoint,pass_=ok,planner=result,reverse_unfold_pass=ok,park_q_equivalent_public_range=qpark.tolist(),reason=None if ok else 'Canonical working endpoint, full populated route or load rejected',door_sweep_path_verified=bool(result['ok']),door_sweep_path_method='All five full door-sweep supersets retained as real10mm-gap obstacles; doors not checked against corridor.',max_envelope_ratio=max(loads,default=None),load_states=samples,max_point_step_mm=max(steps,default=0)*1000))
 path.write_text(json.dumps(out,indent=2));print('CANONICAL_FOLD',v.ID,pi,ok,'endpoint',endpoint['ok'],'route',result['ok'],flush=True)
out['pass_']=out['snapshot_pass'] and out['door_sweep_pass'] and all(r['pass_'] for r in out['fold_paths']);out['status']='PASS_CHECKED_CANONICAL_FOLDS' if out['pass_'] else 'FAIL_CANONICAL_WORKING_FOLD';path.write_text(json.dumps(out,indent=2))
