"""Owned appliance interface sweeps, including physical environment contacts."""
from rescue_spec import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--variant',type=int,required=True);p.add_argument('--station',default='wash_basin');p.add_argument('--product',default='carrot');a=p.parse_args()
cfg=config(a.variant);loc=initial_locations(cfg);obj='output_'+a.product;loc[obj]=seats(cfg)[a.station];ch=Workcell(a.variant,None,loc);q=ch.q0.copy();prefix='wash' if a.station=='wash_basin' else 'process';file=H/f'v2/motion/L{a.variant}_persistent.json';actual=False
if file.exists():
 state=json.loads(file.read_text());choices=[s for s in state['states'] if s['event'].endswith('_complete')]
 if choices:
  ss=choices[-1]
  for n in ARM+['R_carriage_x']:q[ch.qa[n]]=ss['every_joint'][n][0]
  actual=np.linalg.norm(np.array(ss['containers'][obj]['position_m'])-loc[obj])<1e-5
 else:
  ss=state['states'][0]
  for n in ARM+['R_carriage_x']:q[ch.qa[n]]=ss['every_joint'][n][0]
else:
 target=np.array([0,.32,1.4]);rng=np.random.default_rng(660)
 for k in range(96):
  for n in ARM:q[ch.qa[n]]=rng.uniform(-2.5,2.5)
  r=ch.collision_solve(target,ch.rot,q)
  if r['okay']:q=np.array(r['q']);break
ch.m.geom_conaffinity[:]|=1
def descendants(b):
 out=[]
 for g in range(ch.m.ngeom):
  bb=int(ch.m.geom_bodyid[g])
  while bb:
   if bb==b:out.append(g);break
   bb=int(ch.m.body_parentid[bb])
 return out
program=[(prefix+'_retention_x',.0345,'grasp_release_support'),('lid_'+a.product+'_hinge',-1.7,'mechanism')]
if not cfg.get('integral_lid'):program.append((prefix+'_lid_lift_z',.22,'mechanism'))
actual_lid=next((n for n in ch.jid if n.startswith('lid_'+a.product)),None)
program[1]=(actual_lid,-1.7,'mechanism')
program.append(('carrier_'+a.product+'_joint',.12,'mechanism'))
if prefix=='process':
 if cfg.get('blade_lateral_park'):program.append(('process_blade_park_x',.25,'mechanism'))
 program += [('process_blade_park_y',.10,'mechanism'),('process_pusher_x',.18,'working_stroke'),('process_blade_z',.275,'working_stroke'),('process_blade_z',0,'mechanism'),('process_pusher_x',0,'mechanism')]
rows=[]
for joint,end,kind in program:
 if joint not in ch.jid:rows.append(dict(joint=joint,pass_=False,reason='Missing required actuator'));continue
 j=ch.jid[joint];bodyid=int(ch.m.jnt_bodyid[j]);moving=descendants(bodyid);ch.pose(q);start=q[ch.qa[joint]];delta=end-start
 radius=max((np.linalg.norm(ch.d.geom_xpos[g]-ch.d.xanchor[j])+ch.m.geom_rbound[g] for g in moving),default=0) if ch.m.jnt_type[j]==3 else 1
 steps=max(1,int(math.ceil(abs(delta)*radius/.004)));bad=None;minrobot=1e30;begin=q.copy();tested=0;window=dict(kind=kind,object_id=obj if 'retention' in joint else 'food_'+a.product,support_id=prefix+'_retainer' if 'retention' in joint else 'process_pusher' if 'pusher' in joint else 'process_blade' if 'blade_z' in joint else None,tool_face=prefix+'_retention_shoe' if 'retention' in joint else 'process_pusher_plate' if 'pusher' in joint else 'process_blade_full' if 'blade_z' in joint else None,object_face='pan_'+a.product+'_right' if 'retention' in joint else 'food_'+a.product,axis=ch.m.jnt_axis[j].tolist(),maximum_work_window_m=.05)
 window['axis_origin_q']=float(start)
 if kind=='working_stroke' and window['tool_face'] in ch.gnames and window['object_face'] in ch.gnames:
  tg=ch.gnames.index(window['tool_face']);fg=ch.gnames.index(window['object_face']);axis=ch.d.xaxis[j];food_near=ch.bounds.support(fg,-axis);tool_front=ch.bounds.support(tg,axis)
  window['axis_origin_q']=float(start+max(0,float((food_near-tool_front)@axis)))
 for k in range(steps+1):
  z=begin.copy();z[ch.qa[joint]]=start+delta*k/steps;hits,mins,pf=contacts(ch,z);tested+=1
  if hits:bad=dict(kind='robot_gate',sample=k,hits=hits[:4]);break
  minrobot=min(minrobot,min((v['reserve_mm'] for cat,v in mins.items() if cat!='self'),default=1e30))
  mujoco.mj_forward(ch.m,ch.d)
  for g in moving:
   for h in range(ch.m.ngeom):
    if h in moving or ch.robot[h] or ch.weld[g]==ch.weld[h]:continue
    if np.linalg.norm(ch.d.geom_xpos[g]-ch.d.geom_xpos[h])>ch.m.geom_rbound[g]+ch.m.geom_rbound[h]+.001:continue
    distance=mujoco.mj_geomDistance(ch.m,ch.d,g,h,.002,None)
    if distance>=-1e-6:continue
    if ch.bounds.pair(g,h)['lower_m']>1e-6:continue
    names={ch.gnames[g],ch.gnames[h]};allow=False
    # Explicit registry identities, no generic appliance/food exemption.
    expected={window['tool_face'],window['object_face']}
    owner=(window['support_id']==prefix+'_retainer' and window['tool_face']==prefix+'_retention_shoe' and window['object_id']==obj) or (window['support_id']=='process_pusher' and window['tool_face']=='process_pusher_plate' and window['object_id']=='food_'+a.product) or (window['support_id']=='process_blade' and window['tool_face']=='process_blade_full' and window['object_id']=='food_'+a.product)
    if names==expected and owner and kind in ('working_stroke','grasp_release_support'):
     # A local working stroke can continue only across explicitly tracked
     # <=50mm windows. No work permission on return/park paths.
     travel=float(z[ch.qa[joint]]-window['axis_origin_q'])
     allow=abs(delta)*k/steps<=.05+1e-9 and abs(distance)<.00001 if kind=='grasp_release_support' else -1e-6<=travel<=.05+1e-9
    if not allow:bad=dict(kind='appliance_physical_interference',sample=k,pair=sorted(names),signed_gap_mm=distance*1000,contact_window=window if kind in ('grasp_release_support','working_stroke') else None);break
   if bad:break
  if bad:break
 if bad is None:q=begin.copy();q[ch.qa[joint]]=end
 row=dict(joint=joint,kind=kind,start=float(start),end=float(end),start_q=begin.tolist(),pass_=bad is None,drive_interface_qualified=not joint.startswith('carrier_'),interface_note='Existing120mm carrier slide; complete station drive/latch/guide interface is not supplied' if joint.startswith('carrier_') else 'Named modeled interface; fabrication and component qualification remain open',states_checked=tested,planned_states=steps+1,max_point_step_mm=abs(delta)*radius/steps*1000,robot_min_reserve_mm=minrobot if minrobot<1e29 else None,blocker=bad,contact_window=window if kind in ('grasp_release_support','working_stroke') else None,endpoint_q=q.tolist());rows.append(row)
 print(joint,bad is None,bad,flush=True)
 # Each diagnostic starts subsequent axes from the last admitted state. A
 # blocked predecessor is never silently moved to its requested endpoint.
model=f'v2/models/L{a.variant}_{a.product}_{prefix}_mechanisms.xml';(H/model).write_text(ch.xml)
write(f'v2/mechanisms/L{a.variant}_{a.product}_{prefix}.json',dict(rows=rows,actual_prefix_reached=actual,meal_credit=False,scope='Complete moving-interface collision diagnostic; no food cleanliness/cut transition is inferred',xml=model,geometry_full_scale=True,station=a.station,product=a.product,food_mass_kg=sum([.12,.20,.10,.15]),all_food_still_raw=True))
