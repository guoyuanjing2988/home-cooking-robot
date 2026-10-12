"""Deploy from a valid park by Cartesian continuation; all real bodies retained."""
import os,sys,json,time,math,hashlib,xml.etree.ElementTree as E
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v2_r07 as v
from least_analytic_v4_r07 import solve
from motion_v2_r07 import Planner,mo
from point_bound import PointBound
H=v.H;O=v.O;began=time.monotonic();idle=json.loads((O/f'layouts/{v.ID}_idle.json').read_text())
ch=v.scene(104);root=E.fromstring((H/idle['model_xml']).read_text())
# The canonical final-water scene names only R's zero-load marker sites.
# Add L's zero-mass/zero-wrench markers at its unchanged tool origin so the
# literal payload replay can evaluate empty-hand L deployment too. No body,
# mass, collision solid, joint, range or physical frame is changed.
for side in v.s.model.SIDES:
 for suffix in ('work','mass'):
  if root.find(f".//site[@name='{side}_{suffix}']") is None:E.SubElement(root.find(f".//body[@name='{side}_tool']"),'site',name=side+'_'+suffix,pos='0 0 0',size='.003')
ch.xml=E.tostring(root,encoding='unicode');model_xml=f'models/{v.ID}_idle_deployment.xml';(H/model_xml).write_text(ch.xml)
ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
park=np.array(idle['q']);pb=PointBound(ch);out=dict(schema='r07.v3.continued-deployment',layout=v.ID,model_xml=model_xml,model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),door_gap_mm=10,attempts=[],pass_=False,meal_end_return_pass=False)
dest=O/f'layouts/{v.ID}_fold_continuation.json'
if dest.exists():(H/'audit'/f'{v.ID}_fold_continuation_previous_{time.time_ns()}.json').write_text(dest.read_text())
def save():dest.write_text(json.dumps(out,indent=2))
for side,dx,dz in [('R',0,-.03),('R',-.08,-.08),('R',.08,-.08),('R',-.12,-.04),('R',.12,-.04),('R',0,-.10)]:
 if time.monotonic()-began>870:break
 q=park.copy();ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);sid=ch.m.site(side+'_prep').id;p0=ch.d.site_xpos[sid].copy();rot=ch.d.site_xmat[sid].reshape(3,3).copy();goal=p0+np.array([dx,.08-p0[1],dz]);steps=max(1,math.ceil(np.linalg.norm(goal-p0)/.005));path=[q.tolist()];rows=[];replays=[];bad=None
 for k in range(1,steps+1):
  if time.monotonic()-began>920:bad='foreground budget';break
  target=p0+(goal-p0)*k/steps;h=v.s.ck.hand(target,held='empty',approach=rot[:,0].tolist(),jaw_axis=(-rot[:,1]).tolist(),opening=0,check=[[0,0,0]])
  h.update(nominal_moments_Nm=[[0,0,0]],check_moments_Nm=[[0,0,0]],contacts=[],product='carrot');hands={side:h};ch.hands=hands;ch.set_contacts(hands);ch.lock_initial_carriage=False
  start=time.monotonic();trial,errors,hits,evals=solve(ch,q.copy(),hands,0,start+20);trial=mo.shortq(ch,q,trial)
  row=dict(step=k,ik_s=time.monotonic()-start,errors=errors,blockers=hits[:5]);rows.append(row)
  if hits or any(e['position_mm']>5 or e['orientation_deg']>3 for e in errors):bad='continuation IK rejected';break
  ch.seg=dict(ch.seg,poses=[hands]);reference=v.f.replay(ch,dict(k=0,poses=[dict(q=trial.tolist())]));row['reference_pass']=reference['ok']
  if not reference['ok']:bad='reference endpoint rejected';break
  v.s.PARK=q.copy();planner=Planner(ch,{},seed=996000+k,seconds=65);route=planner.plan(q,trial,{},{});row['planner']=route
  if not route['ok']:bad='full4mm route rejected';break
  path+=route['path'][1:];q=trial.copy()
  if k%10==0:print('CONTINUE',side,k,'/',steps,flush=True)
 validator=Planner(ch,{},seconds=65);states=[];maxstep=0.;ratios=[]
 for si,(a,b) in enumerate(zip(np.array(path),np.array(path)[1:])):
  bound=pb.segment_bound(a,b);n=max(1,math.ceil(bound/.004));maxstep=max(maxstep,bound/n)
  for kk in range(n+1):
   state=a+(b-a)*kk/n
   if not validator.state(state,{}):bad='final populated gap replay';break
   tq=ch.torque_multi(state,{},{});ratios.append(tq['ratio'])
   if tq['ratio']>1:bad='holding envelope';break
   states.append(dict(segment=si,alpha=kk/n,q=state.tolist()))
  if bad in ('final populated gap replay','holding envelope'):break
 complete=not bad and k==steps
 if complete:
  for state in reversed(states):
   if not validator.state(np.array(state['q']),{}):bad='reverse unfold check';complete=False;break
 attempt=dict(side=side,start_tcp_m=p0.tolist(),goal_tcp_m=goal.tolist(),steps=rows,pass_=bool(complete and idle['snapshot_pass']),path=path,states=states,states_checked=len(states),max_point_step_mm=maxstep*1000,max_hold_ratio=max(ratios,default=None),blocker=bad,reverse_fold_pass=bool(complete and idle['snapshot_pass']),scope='Meaningful empty-hand deployment toY=.08m from populated park, preserved park orientation. Full door sweeps10mm, complete storage, independent forward/reverse replay. Not a canonical food task or a meal return.')
 out['attempts'].append(attempt);out['pass_']=any(r['pass_'] for r in out['attempts']);save();print('DEPLOYMENT',side,complete,len(path),'bad',bad,flush=True)
 if out['pass_']:break
out['elapsed_s']=time.monotonic()-began;save()
