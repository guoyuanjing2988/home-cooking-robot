import json,time,copy,xml.etree.ElementTree as E
import numpy as np,mujoco
import r07_runtime as rt
import motion_r05 as mo
from planner_r05 import Planner
from point_bound import PointBound
from distance import Bounds
H=rt.H;O=rt.O;s=rt.s
p=json.loads((O/'park_full.json').read_text());q=np.array(p['q'])
ph,sg,key=mo.items[0];ch=mo.scene(ph,sg,0);ch.set_contacts(sg['poses'][0]);ch.allowed=[]
hits,mins,audit=rt.f.contacts(ch,q);b=ch.bounds;rows=[]
for g,n in enumerate(ch.gnames):
 if not ch.robot[g]:continue
 lo=np.array([b.support(g,-v)[k] for k,v in enumerate(np.eye(3))]);hi=np.array([b.support(g,v)[k] for k,v in enumerate(np.eye(3))])
 rows.append(dict(name=n,lo_m=lo.tolist(),hi_m=hi.tolist(),front_strip_clear=bool(lo[1]>=.24-1e-6),corridor_clear=bool(lo[1]>=-.04-1e-6),door_sweep_lower_gap_mm=float((1.35-hi[2])*1000),below_cabinet=bool(hi[2]<=1.34+1e-6)))
snapshot=not hits and all(r['front_strip_clear'] and r['corridor_clear'] and r['below_cabinet'] for r in rows)
doors=[]
root=E.fromstring(ch.xml);w=root.find('worldbody')
for ci,(lo,hi) in enumerate([(-1.8,-.7),(-.1,.69),(1.47,1.8)]):
 count=2 if hi-lo>.6 else 1;width=(hi-lo)/count
 for j in range(count):
  hinge=lo if j==0 else hi;sign=1 if j==0 else -1;n=f'r07_open_door_{ci}_{j}'
  body=E.SubElement(w,'body',name=n,pos=s.model.fmt([hinge,.230,1.65]));E.SubElement(body,'joint',name=n+'_hinge',type='hinge',axis=s.model.fmt([0,0,-sign]),range='0 1.5707963267948966')
  s.model.box(body,n,[sign*width/2,-.009,0],[width,.018,.60],robot=False,mass=5.94)
  doors.append(dict(name=n,width_m=width,height_m=.6,thickness_m=.018,hinge_x_m=hinge,opening_rad=[0,np.pi/2]))
(H/'models/idle_doors_open.xml').write_text(E.tostring(root,encoding='unicode'))
out=dict(schema='r07.corrected-idle',pass_=False,status='PENDING_FOLD_PATHS' if snapshot else 'FAIL_SNAPSHOT',q=q.tolist(),snapshot_pass=snapshot,snapshot_hits=hits,min_clearance=mins,robot_parts=rows,doors=doors,door_sweep_pass=all(r['door_sweep_lower_gap_mm']>=10-1e-3 for r in rows),door_sweep_method='Every full-size leaf remains atz>=1.35m throughout0..90deg. Exact support of every robot part isz<=1.34m: vertical separating-plane proof covers all angles, without checking doors against corridor.',front_counter_strip=dict(x_m=[-1.8,1.8],y_m=[0,.23],z_m=[.85,1.35]),person_corridor=dict(x_m=[-1.6,.6],y_m=[-.75,-.05],z_m=[.85,1.85]),doors_checked_against_corridor=False,fold_paths=[],checked_scene='All original kitchen + replacement processor + complete stored tools/bowls + staged full raw produce; no working-contact permissions')
rt.write('idle.json',out);print('populated snapshot',snapshot,'hits',hits[:4],flush=True)
# Empty-hand deployed poses use this SAME populated compiled scene. Their
# contacts remain empty; the helper can move jointly with the principal.
ha=copy.deepcopy(sg['poses'][0]);plhands={side:dict(h,contacts=[]) for side,h in ha.items()}
for side in ('R','L'):
 if side not in plhands:
  h=copy.deepcopy(ha['R']);h.update(held='empty',held_kg=0,contacts=[]);plhands[side]=h
for index,pos in enumerate([[-.60,.015,1.12],[-.40,.22,1.16],[.20,.015,1.23]]):
 target=copy.deepcopy(ha['R']);target.update(pos=pos,held='empty',held_kg=0,contacts=[],nominal_forces_N=[[0,0,0]],check_forces_N=[[0,0,0]])
 ch.seg=dict(sg,poses=[{'R':target}]);ch.hands={'R':target};ch.search_carriage=True;ch.set_contacts(ch.hands)
 goals=[]
 for seed in range(16):
  rng=np.random.default_rng(71700+index*30+seed);init=q.copy()
  if seed:
   for n in s.ck.ARMS['R']:init[ch.qa[n]]=rng.uniform(*ch.m.jnt_range[ch.jid[n]])
   init[ch.qa['R_carriage_x']]=rng.uniform(-1.5,.045)
  goal,err=ch.solve_least(init,{'R':target},seed);verify=rt.f.replay(ch,dict(k=seed,poses=[dict(q=goal.tolist())]))
  if verify['ok']:goals.append((goal,verify));break
 row=dict(index=index,working_tcp_m=pos,endpoint_starts=seed+1,goal_verified=bool(goals),allocated_planner_budget_s=65,pass_=False)
 if goals and snapshot:
  ch.hands={'R':target};ch.contact_windows=[];ch.working_stroke=False
  pl=Planner(ch,plhands,seed=71800+index,seconds=65);result=pl.plan(goals[0][0],q,plhands,plhands)
  row.update(pass_=result['ok'],planner=result,working_witness=goals[0][1],reverse_unfold_pass=result['ok'])
 else:row['reason']='No reference-admitted working endpoint or populated parked snapshot'
 out['fold_paths'].append(row);rt.write('idle.json',out);print('fold',index,row['pass_'],'endpoint',bool(goals),flush=True)
out['pass_']=snapshot and out['door_sweep_pass'] and all(r['pass_'] for r in out['fold_paths'])
out['status']='PASS_CHECKED_UNLOADED_FOLD_PATHS' if out['pass_'] else 'FAIL_FOLD_OR_SNAPSHOT'
out['meal_end_to_park_verified']=False
rt.write('idle.json',out)
