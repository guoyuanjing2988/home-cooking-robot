"""Corrected populated idle audit and actual bounded fold/unfold diagnostics."""
import os,sys,json,copy,xml.etree.ElementTree as E,time,math
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v2_r07 as v
from motion_v2_r07 import Planner
from ik_v2_r07 import fast_ik
from least_analytic_v2_r07 import solve as collision_ik
from point_bound import PointBound
ch=v.scene(104);ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
# A conservative full sweep cover is used for folding, in addition to the
# exact vertical separation certificate for the parked snapshot. Unlike the
# old working-scene symbolic masks, these named covers are real idle obstacles.
checkroot=E.fromstring(ch.xml);checkworld=checkroot.find('worldbody')
for ci,(lo,hi) in enumerate([(-1.8,-.7),(-.1,.69),(1.47,1.8)]):
 count=2 if hi-lo>.6 else 1;width=(hi-lo)/count
 for j in range(count):
  hinge=lo if j==0 else hi;sign=1 if j==0 else -1
  v.s.model.box(checkworld,f'idle_full_sweep_cover_{ci}_{j}',[hinge+sign*width/2,.230-(width+.018)/2,1.65],[width+.036,width+.036,.60],robot=False)
ch.xml=E.tostring(checkroot,encoding='unicode');ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml))
park=json.loads((v.O/'layouts'/f'{v.ID}_park_full.json').read_text());q=np.array(park['q']);hits,mins,audit=v.f.contacts(ch,q);rows=[]
for g,n in enumerate(ch.gnames):
 if not ch.robot[g]:continue
 lo=np.array([ch.bounds.support(g,-a)[k] for k,a in enumerate(np.eye(3))]);hi=np.array([ch.bounds.support(g,a)[k] for k,a in enumerate(np.eye(3))])
 rows.append(dict(name=n,lo_m=lo.tolist(),hi_m=hi.tolist(),front_strip_clear=bool(lo[1]>=.24-1e-6),corridor_clear=bool(lo[1]>=-.04-1e-6),door_sweep_lower_gap_mm=float((1.35-hi[2])*1000),below_cabinet=bool(hi[2]<=1.34+1e-6)))
snapshot=not hits and all(r['front_strip_clear'] and r['corridor_clear'] and r['below_cabinet'] for r in rows)
root=E.fromstring(ch.xml);world=root.find('worldbody');doors=[]
for g in list(world.findall('geom')):
 if g.get('name','').startswith('idle_full_sweep_cover_'):world.remove(g)
for ci,(lo,hi) in enumerate([(-1.8,-.7),(-.1,.69),(1.47,1.8)]):
 count=2 if hi-lo>.6 else 1;width=(hi-lo)/count
 for j in range(count):
  hinge=lo if j==0 else hi;sign=1 if j==0 else -1;name=f'r07_open_door_{ci}_{j}'
  body=E.SubElement(world,'body',name=name,pos=v.s.model.fmt([hinge,.230,1.65]));E.SubElement(body,'joint',name=name+'_hinge',type='hinge',axis=v.s.model.fmt([0,0,-sign]),range='0 1.5707963267948966');v.s.model.box(body,name,[sign*width/2,-.009,0],[width,.018,.60],robot=False,mass=5.94)
  doors.append(dict(name=name,width_m=width,height_m=.6,thickness_m=.018,hinge_x_m=hinge,opening_rad=[0,float(np.pi/2)]))
(v.H/'models'/f'{v.ID}_idle.xml').write_text(ch.xml);(v.H/'models'/f'{v.ID}_idle_doors.xml').write_text(E.tostring(root,encoding='unicode'))
out=dict(schema='r07.v2.corrected-idle',layout=v.ID,pass_=False,q=q.tolist(),snapshot_pass=snapshot,snapshot_hits=hits,min_clearance=mins,robot_parts=rows,doors=doors,door_sweep_pass=all(r['door_sweep_lower_gap_mm']>=10-1e-3 for r in rows),door_sweep_method='Every full-size cabinet door remains atz>=1.35 throughout0..90deg. A robot maximumz<=1.34 is a sufficient vertical separating-plane certificate for the entire sweep.',doors_checked_against_corridor=False,front_counter_strip=dict(x_m=[-1.8,1.8],y_m=[0,.23],z_m=[.85,1.35]),person_corridor=dict(x_m=[-1.6,.6],y_m=[-.75,-.05],z_m=[.85,1.85]),fold_paths=[],scene='Completed-meal contents in four full output bowls, stored full tools and complete fixed kitchen. No duplicated raw inputs.',model_xml=f'models/{v.ID}_idle.xml',doors_model_xml=f'models/{v.ID}_idle_doors.xml',meal_end_to_park_verified=False)
dest=v.O/'layouts'/f'{v.ID}_idle.json'
if dest.exists():(v.H/'audit'/f'{v.ID}_idle_previous_{time.time_ns()}.json').write_text(dest.read_text())
dest.write_text(json.dumps(out,indent=2))
if '--snapshot-only' in sys.argv:
 out['status']='SNAPSHOT_ONLY_NOT_IDLE_ACCEPTED';dest.write_text(json.dumps(out,indent=2));print('SNAPSHOT',v.ID,snapshot,flush=True);sys.exit(0)
# Find three working seeds on the same empty-hand completed-meal scene.
# A failed park gets a real65s diagnostic, but can never pass even if an
# unrelated transit candidate is clear. No snapshot-only idle credit.
seed_source=q.copy()
refined=len(sys.argv)>2 and sys.argv[2]=='collision'
mapfile=v.O/'reachability'/v.ID/'R.json'
maprows=json.loads(mapfile.read_text())['rows'] if mapfile.exists() else []
for i,pos in enumerate([[-.6,.075,1.10],[-.4,.22,1.12],[.2,.075,1.15]]):
 hand=v.s.ck.hand(pos,held='empty',approach=[0,1,0],jaw_axis=[1,0,0]);hand['jaw_opening_m']=0.
 # Empty-hand deployment has no process wrench; copied hand() predates moments.
 for level in ('nominal','check'):
  hand[level+'_moments_Nm']=[[0.,0.,0.]]
  hand[level+'_forces_N']=[[0.,0.,0.]]
 hands={'R':hand};goal=np.array(seed_source);best=None;ikrows=[]
 near=sorted([r for r in maprows if r['pass_'] and r['orientation']=='front'],key=lambda r:np.linalg.norm(np.array(r['pos'])-pos))[:16]
 for seed in range(8 if refined else 24):
  started=time.monotonic()
  init=goal.copy();rng=np.random.default_rng(950000+i*100+seed)
  if seed:
   for name in v.s.ck.ARMS['R']+['R_carriage_x']:init[ch.qa[name]]=rng.uniform(*ch.m.jnt_range[ch.jid[name]])
  if refined and near and seed%2:
   src=near[seed%len(near)]['witness']['q']
   for name in v.s.ck.ARMS['R']+['R_carriage_x']:init[ch.qa[name]]=src[ch.qa[name]]
  if refined:trial,errors,_,_=collision_ik(ch,init,hands,0,started+20)
  else:trial,errors,_=fast_ik(ch,init,hands,0,max_iter=200)
  ch.hands=hands;ch.set_contacts(hands);hs,_,_=v.f.contacts(ch,trial);score=sum(e['position_mm']+e['orientation_deg'] for e in errors)+sum(max(0,h['required_gap_mm']-h['real_gap_mm']) for h in hs)
  ikrows.append(dict(seed=seed,allocated_s=20 if refined else None,actual_s=time.monotonic()-started,errors=errors,forbidden_records=len(hs)))
  if best is None or score<best[0]:best=(score,trial.copy(),errors,hs,seed)
  if not hs and all(e['position_mm']<=5 and e['orientation_deg']<=3 for e in errors):break
 goal=best[1];ch.hands=hands;ch.set_contacts(hands);ch.working_stroke=False;ch.contact_windows=[];v.s.PARK=goal.copy();pl=Planner(ch,hands,seed=951000+i,seconds=65);result=pl.plan(goal,q,hands,hands)
 ch.seg=dict(ch.seg,poses=[hands]);verify=v.f.replay(ch,dict(k=0,poses=[dict(q=goal.tolist())]));endpoint=verify['ok'];loads=[];loadok=True
 if result['ok']:
  pb=PointBound(ch)
  for a,b in zip(np.array(result['path']),np.array(result['path'])[1:]):
   count=max(1,math.ceil(pb.segment_bound(a,b)/.004))
   for alpha in np.linspace(0,1,count+1):
    state=a+(b-a)*alpha;tq=ch.torque_multi(state,hands,{'R':[0,0,0]},{'R':[0,0,0]});loads.append(tq['ratio']);loadok=loadok and tq['ratio']<=1
 ok=bool(snapshot and endpoint and result['ok'] and loadok)
 out['fold_paths'].append(dict(index=i,working_tcp_m=pos,endpoint_starts=seed+1,endpoint_search=ikrows,collision_aware_endpoint_search=refined,endpoint_geometry_pass=endpoint,endpoint_reference=verify,endpoint_errors=best[2],endpoint_hits=best[3],pass_=ok,planner=result,reverse_unfold_pass=ok,reason=None if ok else 'Snapshot, working endpoint, load or route failed; no idle credit',door_sweep_path_verified=bool(result['ok']),door_sweep_path_method='Full5-door rectangular sweep supersets are retained as10mm-gap obstacles throughout the<=4mm checked folding path.',max_envelope_ratio=max(loads,default=None)));dest.write_text(json.dumps(out,indent=2));print('FOLD',i,ok,flush=True)
out['pass_']=snapshot and out['door_sweep_pass'] and all(r['pass_'] for r in out['fold_paths']);out['status']='PASS_CHECKED_POPULATED_FOLDS' if out['pass_'] else 'FAIL_SNAPSHOT_OR_FOLD';dest.write_text(json.dumps(out,indent=2))
