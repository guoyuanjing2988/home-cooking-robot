"""Persistent first-meal execution. No event is committed across a failed edge."""
from jobs import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--diagnostic-lo',type=int);p.add_argument('--diagnostic-hi',type=int);a=p.parse_args()
def statics():
 rows={}
 for f in sorted((H/'results').glob('static_chunk_*.json'),key=lambda x:x.stat().st_mtime):
  for r in json.loads(f.read_text())['rows']:
   if r['job']['targets']==JOBS[r['index']]['targets']:rows[r['index']]=r
 return rows
W=statics();WID={r['id']:r for r in W.values()}
def mapped(src,q,dst):
 z=dst.q0.copy()
 for n in dst.qa:
  if n in src.qa and src.m.jnt_type[src.jid[n]]==dst.m.jnt_type[dst.jid[n]]:
   count=7 if dst.m.jnt_type[dst.jid[n]]==0 else 1;z[dst.qa[n]:dst.qa[n]+count]=q[src.qa[n]:src.qa[n]+count]
 return z
def load_replay(ch,path,hands):
 pb=PointBound(ch);minres=1e30;maxratio=0;mingrip=1e30;calls=0;maxstep=0;trace=[];reserve_samples=[]
 for si,(x,y) in enumerate(zip(path,path[1:])):
  bound=pb.segment_bound(x,y);count=max(1,int(math.ceil(bound/.004)));maxstep=max(maxstep,bound/count)
  for k in range(count+1):
   q=np.array(x)+(np.array(y)-x)*k/count;calls+=1;hits,mins,ca=contacts(ch,q);tq,gr,cases=check_load(ch,q,hands);maxratio=max(maxratio,tq);mingrip=min(mingrip,gr)
   rv=min((v['reserve_mm'] for c,v in mins.items() if c!='self'),default=0);minres=min(minres,rv);reserve_samples.append(rv)
   if hits or tq>1 or gr<1:return dict(pass_=False,states=calls,segment=si,k=k,first_blocker=hits[:3],torque_ratio=tq,grip_margin=gr,max_point_step_mm=maxstep*1000)
   if calls%10==0:trace.append(dict(q=q.tolist(),reserve_mm=rv))
 return dict(pass_=True,states=calls,min_reserve_mm=minres,reserve_samples_mm=reserve_samples,max_torque_ratio=maxratio,min_grip_margin=mingrip,max_point_step_mm=maxstep*1000,trace=trace)
def duration(ch,path):
 pb=PointBound(ch);total=0
 def rest(dist,v,acc):return 2*math.sqrt(dist/acc) if dist<=v*v/acc else dist/v+v/acc
 for x,y in zip(path,path[1:]):
  dq=np.abs(np.array(y)-x);B=pb.segment_bound(x,y);pairs=[(B,.10,.15)]+[(dq[ch.qa[n]],.20,.25) for n in ARM]+[(dq[ch.qa[n]],.01,.02) for n in ('R_jaw_minus','R_jaw_plus')]
  moving=[(dist,v,acc) for dist,v,acc in pairs if dist>1e-14]
  if moving:total+=rest(1,min(v/dist for dist,v,acc in moving),min(acc/dist for dist,v,acc in moving))
 return total
def plan(ch,start,goal,hands,seed):
 s.PARK=np.array(start).copy();pl=Planner(ch,hands,seed=seed,seconds=65)
 # The unchanged R05 planner has a hardcoded mobile-rail proposal range.
 # R06 supplies the actual immobile mounting joint range, and contacts also
 # rejects every out-of-range state. No fictitious 45mm rail is admitted.
 for k,n in enumerate(pl.names):pl.limits[k]=ch.m.jnt_range[ch.jid[n]]
 staging=[]
 for target in ([0,.24,1.32],[-.2,.25,1.32],[0,.4,1.32]):
  z,err=ch.solve(np.array(target),ch.rot,np.array(start));hits,mins,pf=contacts(ch,z);tq,gr,fc=check_load(ch,z,hands)
  okay=err['position_mm']<=5 and err['orientation_deg']<=3 and not hits and tq<=1 and gr>=1
  staging.append(dict(target_m=target,q=z.tolist(),pass_=okay,errors=err,first_blocker=hits[:2],torque_ratio=tq,grip_margin=gr))
  if okay:s.PARK=z.copy()
 r=pl.plan(start,goal,hands,hands)
 r['additional_staging_poses']=staging
 if r['ok']:
  r['load_replay']=load_replay(ch,r['path'],hands);r['ok']=r['load_replay']['pass_']
  if r['ok']:r['duration_s']=duration(ch,r['path'])
 return r
def line(ch,start,target,hs,kind):
 # A fixed Cartesian support stroke has no geometric detour permission.
 p0,rot=ch.pose(start);delta=np.array(target)-p0;n=max(1,int(math.ceil(np.linalg.norm(delta)/.001)));path=[np.array(start).copy()];pl=Planner(ch,hs,seed=606,seconds=65);deadline=time.monotonic()+65
 for k in range(1,n+1):
  q,e=ch.solve(p0+delta*k/n,rot,path[-1]);p1,r1=ch.pose(q)
  if e['position_mm']>.01 or e['orientation_deg']>.01 or not pl.edge(path[-1],q,hs,hs,deadline):return dict(ok=False,allocated_budget_s=65,reason='Constrained straight support stroke rejected; detour would violate declared insertion axis',k=k,last_rejection=pl.last,path=[x.tolist() for x in path])
  path.append(q)
 result=load_replay(ch,path,hs);return dict(ok=result['pass_'],path=[q.tolist() for q in path],load_replay=result,allocated_budget_s=65,kind=kind,duration_s=duration(ch,path) if result['pass_'] else None)
def equiv(src,q,dst,z):
 src.pose(q);dst.pose(z);before={n.removeprefix('R_held_'):src.d.geom_xpos[g].copy() for g,n in enumerate(src.gnames)};err=[]
 for g,n in enumerate(dst.gnames):
  canon=n.removeprefix('R_held_')
  if canon in before:err.append(float(np.linalg.norm(before[canon]-dst.d.geom_xpos[g])))
 return max(err,default=0)
if a.diagnostic_lo is not None:
 # Full-budget RRT diagnostics for all retained loaded transfer endpoints.
 pairs=[]
 for i,j in enumerate(JOBS[:-1]):
  if j['admission']=='full_robot_static' and j['id'].endswith('_grasp'):
   nxt=next((x for x in JOBS[i+1:] if x['admission']=='full_robot_static'),None)
   if nxt and nxt['held']==j['held']:pairs.append((j,nxt))
 out=[]
 for pi,(ja,jb) in enumerate(pairs[a.diagnostic_lo:a.diagnostic_hi],a.diagnostic_lo):
  wa=WID.get(ja['id']);wb=WID.get(jb['id']);ch=load_cell(ja);ch.contact_windows=[]
  if wa is None or wb is None:out.append(dict(index=pi,from_=ja['id'],to=jb['id'],ok=False,reason='Missing completed 96-start static audit',allocated_budget_s=65));continue
  # The proposed connection still retains all previous foods and every container.
  dest=load_cell(jb);start=np.array(wa['selected']['poses'][-1]['q']);goal=mapped(dest,np.array(wb['selected']['poses'][0]['q']),ch);hs=hand(ch,ja['targets'][-1],ja['load']);r=plan(ch,start,goal,hs,6060+pi)
  out.append(dict(index=pi,from_=ja['id'],to=jb['id'],persistent_meal_admitted=False,**r));print('DIAGNOSTIC',pi,r['ok'],'time',round(r['planner_time_s'],1),flush=True)
  write(f'results/connection_diagnostics_{a.diagnostic_lo}_{a.diagnostic_hi}.json',dict(rows=out,scope='Isolated full-scene endpoint diagnostics only; previous unverified processing does not execute or reset food',all_connections_budget_s=65))
 exit()
initial=copy.deepcopy(LEDGER[0]);initial['status']='executed_simulation_prefix';initial['total_food_mass_kg']=.57;initial['food_quality']='raw_unwashed';initial['guard']='locked_person_outside';initial['appliances'].update(wash_lift_m=.12,brush_parking_m=.175,cell_roof_rad=-1.6,cell_header_rad=-1.6,process_door_m=.6,root_roller_parking_m=.085,blade_m=0,drive_enable=False,brakes='applied',water_volume_L=0,water_supply='off');initial['containers']['output_carrot']['world_position_m']=ORIG['output_carrot']
states=[initial];paths=[];connections=[];blocked=None;locations=copy.deepcopy(ORIG);ch=Cell(V,None,{k:ORIG[k] for k in ('output_carrot','output_potato','output_bok_choy','output_tomato','clean_leaf_basket')})
w0=WID.get('A01_00_lock_guard_and_selfcheck');w1=WID.get('A02_grasp');w2=WID.get('A03_release')
if not w0 or not w0['static_robot_ok']:blocked=dict(event='A01',reason='No checked safe initial robot pose')
else:
 q=np.array(w0['selected']['poses'][0]['q']);initial['robot_joint_q']={n:float(q[ch.qa[n]]) for n in ARM};states[0]=initial
 (H/'models/overview.xml').write_text(ch.xml)
 if not w1 or not w1['pass_']:blocked=dict(event='A02',reason='No admitted grasp/lift static stroke')
 else:
  heldch=load_cell(w1['job']);grasp=mapped(heldch,np.array(w1['selected']['poses'][0]['q']),ch);pre,err=ch.solve(np.array(w1['job']['targets'][0])+[0,0,.05],ch.rot,q)
  for n in ('R_jaw_minus','R_jaw_plus'):pre[ch.qa[n]]=-.01
  target=np.array(w1['job']['targets'][0]);cw=dict(kind='grasp_release_support',object_id='output_carrot',support_id='eoat_key_capture',normal=[0,0,1],tcp_origin_m=target.tolist(),tcp_rotation=ch.rot.tolist(),pairs=[['key_carrot','R_eoat_key_left'],['key_carrot','R_eoat_key_right']]);ch.capture_window=cw
  hs=hand(ch,[0,.24,1.32]);r=plan(ch,q,pre,hs,6061);connections.append(dict(id='initial_to_A02_pregrasp',**r))
  if not r['ok']:blocked=dict(event='A02',reason='Initial empty approach connection failed',witness=r['last_rejection'])
  else:
   paths.append(dict(id='approach_carrot',xml='models/overview.xml',**r));r=line(ch,pre,target,hs,'grasp_release_support');paths.append(dict(id='lower_to_key',xml='models/overview.xml',**r))
   if not r['ok']:blocked=dict(event='A02',reason='Own key approach failed',witness=r.get('last_rejection'))
   else:
    q=np.array(r['path'][-1]);closed=q.copy()
    for n in ('R_jaw_minus','R_jaw_plus'):closed[ch.qa[n]]=.005
    r=plan(ch,q,closed,hs,6062);paths.append(dict(id='close_key_jaws',xml='models/overview.xml',**r))
    if not r['ok']:blocked=dict(event='A02',reason='Jaw capture path failed',witness=r.get('last_rejection'))
    else:
     z=mapped(ch,closed,heldch);invariant=equiv(ch,closed,heldch,z)
     if invariant>1e-5:blocked=dict(event='A02',reason='Ownership transition would move an object',max_geom_translation_m=invariant)
     else:
      ch=heldch;q=z;hs=hand(ch,target);state=copy.deepcopy(states[-1]);state['after_event']='A02_capture';state['arm'].update(jaw='closed_key',held='output_carrot');state['attachment_invariant_m']=invariant;state['robot_joint_q']={n:float(q[ch.qa[n]]) for n in ARM};states.append(state)
      r=line(ch,q,target+[0,0,.05],hs,'grasp_release_support');paths.append(dict(id='lift_carrot',xml='models/A02_grasp.xml',**r))
      if not r['ok']:blocked=dict(event='A02',reason='Straight support lift failed',witness=r.get('last_rejection'))
      elif not w2 or not w2['pass_']:blocked=dict(event='A03',reason='No admitted wash seating static stroke')
      else:
       q=np.array(r['path'][-1]);ch.contact_windows=[];dest=load_cell(w2['job']);goal=mapped(dest,np.array(w2['selected']['poses'][0]['q']),ch);r=plan(ch,q,goal,hs,6063);connections.append(dict(id='A02_to_A03_loaded',**r));paths.append(dict(id='carry_carrot_to_wash',xml='models/A02_grasp.xml',**r))
       if not r['ok']:blocked=dict(event='A03',reason='Loaded carrot connection failed',witness=r.get('last_rejection'))
       else:
        q=np.array(r['path'][-1]);ch.contact_windows=windows(ch,'wash_basin',w2['job']['origin']);target=grip_pos('output_carrot',w2['job']['origin']);r=line(ch,q,target,hs,'grasp_release_support');paths.append(dict(id='lower_carrot_to_wash',xml='models/A02_grasp.xml',**r))
        if not r['ok']:blocked=dict(event='A03',reason='Wash support approach failed',witness=r.get('last_rejection'))
        else:
         q=np.array(r['path'][-1]);poses={k:ORIG[k] for k in ('output_carrot','output_potato','output_bok_choy','output_tomato','clean_leaf_basket')};poses['output_carrot']=w2['job']['origin'];releasech=Cell(V,None,poses);z=mapped(ch,q,releasech);invariant=equiv(ch,q,releasech,z)
         if invariant>1e-5:blocked=dict(event='A03',reason='Release would move geometry',max_geom_translation_m=invariant)
         else:
          releasech.capture_window=dict(cw,tcp_origin_m=target.tolist());opened=z.copy()
          for n in ('R_jaw_minus','R_jaw_plus'):opened[releasech.qa[n]]=-.01
          hs=hand(releasech,target);r=plan(releasech,z,opened,hs,6064);paths.append(dict(id='release_key_jaws',xml='models/released_wash.xml',**r));(H/'models/released_wash.xml').write_text(releasech.xml)
          if not r['ok']:blocked=dict(event='A03',reason='Release jaw path failed',witness=r.get('last_rejection'))
          else:
           q=np.array(r['path'][-1]);r=line(releasech,q,target+[0,0,.05],hs,'grasp_release_support');paths.append(dict(id='retreat_wash_key',xml='models/released_wash.xml',**r))
           if not r['ok']:blocked=dict(event='A03',reason='Empty key retreat failed',witness=r.get('last_rejection'))
           else:
            state=copy.deepcopy(states[-1]);state['after_event']='A03';state['arm'].update(jaw='open',held=None);state['containers']['output_carrot'].update(location='wash_basin',world_position_m=poses['output_carrot']);state['attachment_invariant_m']=invariant;states.append(state)
            blocked=dict(event='A04',reason='Wash lid/insert/water/indexed rubbing paths and cleanliness feedback not physically bound to this persistent scene; robot remains stopped with conserved raw produce. No timer is substituted for a verified wash.')
for state in states:assert abs(sum(f['mass_kg'] for f in state['food'].values())-.57)<1e-10
physical=[]
def physical_snapshot(xml,q,label):
 m=mujoco.MjModel.from_xml_path(str(H/xml));d=mujoco.MjData(m);d.qpos[:]=q;mujoco.mj_kinematics(m,d)
 joints={m.joint(j).name:np.array(q)[m.jnt_qposadr[j]:m.jnt_qposadr[j]+(7 if m.jnt_type[j]==0 else 1)].tolist() for j in range(m.njnt)}
 containers={}
 for name in ('output_carrot','output_potato','output_bok_choy','output_tomato','clean_leaf_basket'):
  attached=any(m.body(b).name=='R_held_'+name for b in range(m.nbody));bn=('R_held_' if attached else '')+name;b=m.body(bn).id
  containers[name]=dict(world_position_m=d.xpos[b].tolist(),world_quaternion_wxyz=d.xquat[b].tolist(),attached_to='R_tool' if attached else 'station',lid_joint_rad=next((v[0] for n,v in joints.items() if n=='lid_'+name.removeprefix('output_')+'_joint'),None))
 physical.append(dict(after_path=label,xml=xml,q=np.array(q).tolist(),every_joint=joints,containers=containers,food_owners={n:f['owner'] for n,f in initial['food'].items()},food_mass_kg={n:f['mass_kg'] for n,f in initial['food'].items()},food_quality='raw_unwashed',guard='locked',arm_drive_during_path=True,all_process_drives=False,stationary_end_arm_brakes='applied',water_supply='off',water_volume_L=0))
if 'q' in locals() and w0 and w0['static_robot_ok']:
 physical_snapshot('models/overview.xml',w0['selected']['poses'][0]['q'],'initial')
 for path in paths:
  if not path['ok']:break
  physical_snapshot(path['xml'],path['path'][-1],path['id'])
write('results/executed_prefix.json',dict(states=states,physical_states=physical,paths=paths,connections=connections,blocked=blocked,meal_pass=False,total_food_kg=.57,completed_meal=False,geometry_not_reset=True))
print('PREFIX',len(paths),'paths',sum(x['ok'] for x in paths),'connections',sum(x['ok'] for x in connections),'blocked',blocked['event'])
