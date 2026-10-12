"""Map-guided deployed empty-hand poses, full populated idle scene and10mm doors.
Local deployment qualification only: never substitute it for meal-end return.
"""
import os,sys,json,time,math,copy,hashlib
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v2_r07 as v
from motion_v2_r07 import Planner,mo
from point_bound import PointBound
H=v.H;O=v.O;began=time.monotonic()
idle=json.loads((O/f'layouts/{v.ID}_idle.json').read_text());ch=v.scene(104)
ch.xml=(H/idle['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
park=np.array(idle['q']);pb=PointBound(ch);phits,pmins,_=v.f.contacts(ch,park)
dest=O/f'layouts/{v.ID}_fold_map.json';out=dict(schema='r07.v3.map-guided-folds',layout=v.ID,park_snapshot_pass=idle['snapshot_pass'],door_gap_mm=10,model_xml=idle['model_xml'],model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),map_endpoint_checks=[],routes=[],local_fold_unfold_pass=False,meal_end_return_pass=False)
if dest.exists():(H/'audit'/f'{v.ID}_fold_map_previous_{time.time_ns()}.json').write_text(dest.read_text())
def save():dest.write_text(json.dumps(out,indent=2))
candidates=[]
for side in ('R','L'):
 rows=json.loads((O/f'reachability/{v.ID}/{side}.json').read_text())['rows']
 for ri,r in enumerate(rows):
  if not r['pass_'] or r['pos'][1]>.23 or r['pos'][2]<1.02:continue
  q=park.copy();src=np.array(r['witness']['q'])
  for name in v.s.ck.ARMS[side]+[side+'_carriage_x']:q[ch.qa[name]]=src[ch.qa[name]]
  q=mo.shortq(ch,park,q);hits,mins,_=v.f.contacts(ch,q);tq=ch.torque_multi(q,{},{});valid=not hits and tq['ratio']<=1
  row=dict(side=side,map_row=ri,tcp_m=r['pos'],orientation=r['orientation'],pass_=valid,forbidden_records=len(hits),blockers=hits[:5],hold_ratio=tq['ratio'])
  out['map_endpoint_checks'].append(row)
  if valid:candidates.append((pb.segment_bound(park,q),side,ri,q,row))
save();candidates.sort(key=lambda z:z[0]);print('FULL_SCENE_DEPLOYED_ENDPOINTS',len(candidates),'of',len(out['map_endpoint_checks']),flush=True)
for order,(_,side,ri,q,row) in enumerate(candidates[:10]):
 if time.monotonic()-began>960:break
 v.s.PARK=park.copy();ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
 pl=Planner(ch,{},seed=993000+ri+order,seconds=65)
 if '--active-only' in sys.argv:
  pl.names=v.s.ck.ARMS[side]+[side+'_carriage_x'];pl.ix=[ch.qa[n] for n in pl.names];pl.limits=np.array([ch.m.jnt_range[ch.jid[n]] for n in pl.names]);pl.scale=np.array([.5 if n.endswith('carriage_x') else 1. for n in pl.names])
 result=pl.plan(q,park,{},{})
 result['inactive_arm_fixed_at_park']='--active-only' in sys.argv
 checked=[];loads=[];maxstep=0.;bad=None
 if result['ok']:
  validator=Planner(ch,{},seconds=65)
  for si,(a,b) in enumerate(zip(np.array(result['path']),np.array(result['path'])[1:])):
   bound=pb.segment_bound(a,b);n=max(1,math.ceil(bound/.004));maxstep=max(maxstep,bound/n)
   for k in range(n+1):
    state=a+(b-a)*k/n
    if not validator.state(state,{}):bad=dict(kind='gap',detail=validator.last);break
    tq=ch.torque_multi(state,{},{});loads.append(tq['ratio'])
    if tq['ratio']>1:bad=dict(kind='holding',ratio=tq['ratio']);break
    checked.append(dict(segment=si,alpha=k/n,q=state.tolist()))
   if bad:break
  # Same static geometry and symmetric speed/load limits allow reverse replay.
  if not bad:
   for sample in reversed(checked):
    if not validator.state(np.array(sample['q']),{}):bad=dict(kind='reverse_gap',detail=validator.last);break
 ok=bool(idle['snapshot_pass'] and not phits and result['ok'] and not bad)
 out['routes'].append(dict(index=order,side=side,map_row=ri,endpoint=row,pass_=ok,reverse_unfold_pass=ok,planner=result,blocker=bad,states=checked,states_checked=len(checked),max_point_step_mm=maxstep*1000,max_hold_ratio=max(loads,default=None),scope='Empty-hand deployment from a reachability-map working location; full completed-meal storage geometry. Not a process stroke or meal-end ownership witness.'))
 out['local_fold_unfold_pass']=any(x['pass_'] for x in out['routes']);save();print('MAP_FOLD',order,side,ri,ok,'states',len(checked),flush=True)
 if sum(x['pass_'] for x in out['routes'])>=2:break
out['elapsed_s']=time.monotonic()-began;save()
