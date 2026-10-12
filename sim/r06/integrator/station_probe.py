"""Full station solids and ordered sweeps; diagnostics never promote failures."""
from station_cell import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--variant',type=int,required=True);p.add_argument('--park-starts',type=int,default=0);a=p.parse_args()
cfg,s=register(a.variant);loc=initial_locations(cfg);loc['output_carrot']=seats(cfg)['wash_basin'];ch=StationCell(a.variant,None,loc);q=ch.q0.copy()
prior=json.loads((H/'history/v2/results/executed_prefix.json').read_text())
ss=next(st for st in prior['states'] if st['event']=='T01_complete')
for n,vals in ss['every_joint'].items():
 if n in ch.qa:q[ch.qa[n]:ch.qa[n]+len(vals)]=vals
q[ch.qa['output_carrot_joint']:ch.qa['output_carrot_joint']+3]=loc['output_carrot']
model=f'v3/models/L{a.variant}_station.xml';(H/model).parent.mkdir(parents=True,exist_ok=True);(H/model).write_text(ch.xml)

def physical(z,moving=None,windows=()):
 if windows:raise ValueError('No appliance working-contact face registry is qualified; no working exemptions are enabled')
 hits,mins,proof=contacts(ch,z);bad=[]
 if hits:bad.extend(dict(type='robot_gate',**h) for h in hits)
 ch.pose(z)
 for g in range(ch.m.ngeom):
  if ch.robot[g]:continue
  for h in range(g):
   if ch.robot[h] or ch.weld[g]==ch.weld[h]:continue
   if moving is not None and g not in moving and h not in moving:continue
   if np.linalg.norm(ch.d.geom_xpos[g]-ch.d.geom_xpos[h])>ch.m.geom_rbound[g]+ch.m.geom_rbound[h]+.002:continue
   gap=mujoco.mj_geomDistance(ch.m,ch.d,g,h,.002,None)
   if gap>=-1e-6:continue
   if ch.bounds.pair(g,h)['lower_m']>1e-6:continue
   pair=sorted([ch.gnames[g],ch.gnames[h]])
   bad.append(dict(type='mechanical_interference',pair=pair,signed_gap_mm=float(gap*1000)))
 return bad,mins

# The complete initial assembly is checked, including all pan drive solids.
# Adjacent rigid solids welded together are deliberate manufacturing joints.
initial,mins=physical(q)
park=[]
if a.park_starts:
 rng=np.random.default_rng(18018+a.variant)
 target=np.array([-.30,.20,1.43])
 for k in range(a.park_starts):
  seed=q.copy()
  for n in ARM:seed[ch.qa[n]]+=rng.normal(0,.3)
  r=ch.collision_solve(target,ch.rot,seed,20);r['initial_q']=seed.tolist();r['seed']=k;park.append(r)
  if r['okay']:q=np.array(r['q'])

def descendants(joints):
 roots={int(ch.m.jnt_bodyid[ch.jid[n]]) for n in joints};gs=set()
 for g in range(ch.m.ngeom):
  b=int(ch.m.geom_bodyid[g])
  while b:
   if b in roots:gs.add(g);break
   b=int(ch.m.body_parentid[b])
 return gs

# Full supporting predecessor states, including open lid, coupled push rods,
# retention cups, tool approach and explicitly separate non-working returns.
program=[('lid_open',{'lid_carrot_joint':-1.7}),
 ('pushrod_acquire',{'basket_lift_joint':.021}),
 ('basket_lift',{'basket_lift_joint':.141,'carrier_carrot_joint':.12}),
 ('drain_open',{'pan_drain_carrot_joint':.012}),
 ('cradle_lift',{'food_cradle_joint':.1915 if a.variant>=30 else .1315 if a.variant>=21 else .12+s['cradle_raise']}),
 ('retention_close',{'end_cup_-1_joint':.030,'end_cup_1_joint':.030}),
 ('brush_head_approach',{'service_head_joint':.04 if a.variant>=23 else .19}),
 ('brush_contact',{'brush_approach_joint':.02}),
 ('brush_sweep',{'tool_feed_joint':.16}),
 ('brush_retract',{'brush_approach_joint':0}),
 ('root_index',{'index_-1_joint':math.pi/2,'index_1_joint':math.pi/2}),
 ('peel_follower',{'peel_follower_joint':.04}),
 ('peel_sweep',{'tool_feed_joint':0}),
 ('peel_retract',{'peel_follower_joint':0}),
 ('core_approach',{'core_approach_joint':.08}),
 ('core_retract',{'core_approach_joint':0}),
 ('head_park',{'service_head_joint':0}),
 ('pusher_feed',{'slice_pusher_joint':.12}),
 ('slice_down',{'slice_blade_joint':.18}),
 ('slice_retract',{'slice_blade_joint':0}),
 ('scrap_gate',{'scrap_diverter_joint':1.1}),
 ('cradle_lower',{'food_cradle_joint':0}),
 ('basket_lower',{'basket_lift_joint':.021,'carrier_carrot_joint':0}),
 ('pushrod_release',{'basket_lift_joint':0}),
 ('drain_close',{'pan_drain_carrot_joint':0}),
 ('lid_close',{'lid_carrot_joint':0})]
if a.variant>=24:
 at=next(i for i,x in enumerate(program) if x[0]=='brush_head_approach');program.insert(at,('lower_service_head',{'service_lower_joint':.365}))
 # Drain closes while food is retained above the water, before lowering basket.
 i=next(i for i,x in enumerate(program) if x[0]=='drain_close');close=program.pop(i);j=next(i for i,x in enumerate(program) if x[0]=='basket_lower');program.insert(j,close)
if a.variant>=27:
 at=next(i for i,x in enumerate(program) if x[0]=='cradle_lift');program.insert(at,('cradle_advance',{'cradle_park_joint':.23 if a.variant>=30 else .18}))
if s.get('press_vertical',a.variant>=28):
 at=next(i for i,x in enumerate(program) if x[0]=='pusher_feed');program.insert(at,('press_lower',{'press_lower_joint':.45}))
if a.variant>=29:
 program.insert(0,('pan_retain',{'pan_retainer_-1_joint':.0345,'pan_retainer_1_joint':.0345}))
 program.append(('pan_release',{'pan_retainer_-1_joint':0,'pan_retainer_1_joint':0}))
rows=[];first_failure=None
for label,goals in program:
 before=q.copy();end=q.copy();moving=descendants(goals)
 for n,val in goals.items():end[ch.qa[n]]=val
 ch.pose(before);bound=0
 for n,val in goals.items():
  j=ch.jid[n];travel=abs(end[ch.qa[n]]-before[ch.qa[n]])
  radius=max((np.linalg.norm(ch.d.geom_xpos[g]-ch.d.xanchor[j])+ch.m.geom_rbound[g] for g in descendants([n])),default=0) if ch.m.jnt_type[j]==3 else 1
  bound+=travel*radius
 steps=max(1,math.ceil(bound/.004));failure=None;reserve=[];checked=[]
 for k in range(steps+1):
  z=before+(end-before)*k/steps;bad,mins=physical(z,moving)
  reserve.append(min((vv['reserve_mm'] for cat,vv in mins.items() if cat!='self'),default=1e20))
  if bad:failure=dict(sample=k,violations=bad[:12],q=z.tolist());break
  checked.append(z.tolist())
 passed=failure is None
 if passed:q=end
 elif first_failure is None:first_failure=label
 rows.append(dict(id=label,pass_=passed,start_q=before.tolist(),end_q=q.tolist(),requested=end.tolist(),geometry_checked_states=k+1,planned_states=steps+1,max_point_step_mm=bound/steps*1000,blocker=failure,minimum_robot_reserve_mm=min(reserve),path=checked,predecessors_pass=first_failure is None or first_failure==label,meal_credit=False,allocated_planner_budget_s=65,method='Unique commanded actuator-axis connection; collision proof at <=4mm; downstream conditional probes retain last admitted state'))
 write(f'v3/probes/L{a.variant}.json',dict(config=cfg,settings=s,xml=model,initial_interferences=initial,park_search=park,rows=rows,first_failure=first_failure,scope='Conditional mechanism diagnostic, not persistent meal execution; raw food still in basket',geometry_total=ch.m.ngeom))
 print(label,passed, failure['violations'][:2] if failure else '',flush=True)
print('INITIAL',len(initial),initial[:8]);print('STATION',a.variant,sum(r['pass_'] for r in rows),'/',len(rows))
