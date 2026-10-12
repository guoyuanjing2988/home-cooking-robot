"""Conservative appliance motion diagnostics; never creates food or commits events."""
from jobs import *
import re
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--lo',type=int,default=0);ap.add_argument('--hi',type=int,default=10000);args=ap.parse_args()
W={}
for f in sorted((H/'results').glob('static_chunk_*.json'),key=lambda x:x.stat().st_mtime):
 for r in json.loads(f.read_text())['rows']:
  if r['job']['targets']==JOBS[r['index']]['targets']:W[r['index']]=r
class Journal(list):
 def append(self,row):
  super().append(row)
  write(f'results/mechanism_chunk_{args.lo}_{args.hi}.json',dict(rows=list(self),scope='Rejected/unqualified appliance diagnostics, not an executed conserved meal',no_food_spawn=True,no_work_contact_on_nonworking_paths=True,complete_chunk=False))
rows=Journal()
def command(job,ch):
 t=job.get('substep','');prod=job.get('pan_id')
 for cover in ('cell_roof','cell_front_header'):
  if t.startswith(cover+'_'):return (cover+'_retract_joint',-1.6,0) if 'close_before' in t else (cover+'_retract_joint',0,-1.6)
 if prod and prod.startswith('output_'):return ('lid_'+prod[7:]+'_joint',0,-1.8) if 'open' in t else ('lid_'+prod[7:]+'_joint',-1.8,0)
 if 'wash_lid' in t or t in ('close_lid','open_lid'):
  return ('wash_lid_joint',-1.7,0) if 'close' in t else ('wash_lid_joint',0,-1.7)
 if t in ('close_door','close_cell_door'):return ('cell_door_joint',.6,0)
 if t in ('open_door','open_cell_door'):return ('cell_door_joint',0,.6)
 if t.startswith('lift_insert') or 'lift_stalk_source' in t:return ('wash_lift_joint',0,.12)
 if t.startswith('lower_insert'):return ('wash_lift_joint',.12,0)
 if t.startswith('root_rotate_index_'):
  k=int(t.rsplit('_',1)[1]);return ('root_roller_joint',(k-1)*math.pi/4,k*math.pi/4)
 if t.startswith(('peel_work_pass','peeler_retract')):return ('cell_peeler_joint',0,.17) if t.startswith('peel_work') else ('cell_peeler_joint',.17,0)
 if t.startswith('feed5mm_'):
  k=int(t.rsplit('_',1)[1]);return ('follower_joint',(k-1)*.005,k*.005)
 if t.startswith(('cut5mm','terminal_cut','greens_section_cut','root_disk_cut')):return ('blade_carriage_joint',.523,.562)
 if t.startswith(('blade_retract','terminal_retract')):return ('blade_carriage_joint',.5,0)
 if 'eyer_work' in t or t=='core_work':return ('eye_core_z_joint',0,.20)
 if 'eyer_retract' in t or t=='core_retract':return ('eye_core_z_joint',.20,0)
 if 'pusher_work' in t:return ('wedger_pusher_joint',0,.23)
 if t=='pusher_retract':return ('wedger_pusher_joint',.23,0)
 if 'close_clamps' in t:return ('cell_clamp_left_joint',0,.04)
 if 'open_clamps' in t:return ('cell_clamp_left_joint',.04,0)
 return None
for i,job in enumerate(JOBS[args.lo:args.hi],args.lo):
 if job['admission']=='full_robot_static':continue
 w=W.get(i)
 if w is None:rows.append(dict(index=i,id=job['id'],pass_=False,reason='96-start prerequisite incomplete'));continue
 ch=load_cell(job);cmd=command(job,ch)
 # Robot scene masks originally request robot/environment pairs only.
 # Appliance diagnostics additionally require physical environment/environment
 # collision reporting. Enable those pairs without altering a solid or gate.
 ch.m.geom_conaffinity[:]|=1
 if cmd is None:
  rows.append(dict(index=i,id=job['id'],pass_=False,reason='No fully specified actuator trajectory / feedback / food topology for this obligation',states_checked=0,planner_budget_s=65,search_disposition='No geometric endpoints exist; planner cannot manufacture the missing physical state',static_robot_ok=w['static_robot_ok']));continue
 n,start,end=cmd
 if n not in ch.qa:rows.append(dict(index=i,id=job['id'],pass_=False,reason='No physical pan-lid actuator/joint for this object'));continue
 q=np.array(w['selected']['poses'][0]['q']);q[ch.qa[n]]=start;j=ch.jid[n];bid=int(ch.m.jnt_bodyid[j]);geoms=[]
 for g in range(ch.m.ngeom):
  b=int(ch.m.geom_bodyid[g])
  while b and b!=bid:b=int(ch.m.body_parentid[b])
  if b==bid:geoms.append(g)
 ch.pose(q);lever=max([float(np.linalg.norm(ch.d.geom_xpos[g]-ch.d.xanchor[j])+ch.m.geom_rbound[g]) for g in geoms]+[0]);bound=abs(end-start)*(lever if ch.m.jnt_type[j]==3 else 1);count=max(1,math.ceil(bound/.004));hits=[];checked=0;first=None
 # Fixed appliance stroke has no arbitrary detour. All robot geometry, foods,
 # parked lids and tools stay present. Food topology is never transformed here.
 for k in range(count+1):
  q[ch.qa[n]]=start+(end-start)*k/count;checked+=1
  if k==0 or any(ch.robot[g] for g in geoms):h,mins,ca=contacts(ch,q)
  else:
   # Only this single environment joint moves. All robot/self and other
   # robot/environment pairs are exactly the first-sample pairs. Reuse that
   # full certificate, and query EVERY changed pair at the current transform.
   ch.pose(q);h=[];lo,hi=ch.m.jnt_range[j]
   if not lo-1e-9<=q[ch.qa[n]]<=hi+1e-9:h=[dict(pair=[n,'physical_joint_limit'],reason='Physical joint range')]
   for ga in geoms:
    for gb in np.flatnonzero(ch.robot):
     req=required(ch,ga,int(gb))
     if req is None:continue
     need,cat=req;sphere=float(np.linalg.norm(ch.d.geom_xpos[ga]-ch.d.geom_xpos[gb])-ch.m.geom_rbound[ga]-ch.m.geom_rbound[gb])
     if sphere>=need+1e-8:continue
     boundpair=ch.bounds.pair(ga,int(gb))
     if boundpair['lower_m']<need-1e-6:h.append(dict(pair=[ch.gnames[ga],ch.gnames[gb]],reason='Changed pair uncertified or violates unchanged gate',lower_gap_mm=boundpair['lower_m']*1000,required_mm=need*1000))
  if h:first=dict(k=k,kind='robot/environment',blockers=h[:3]);break
  mujoco.mj_collision(ch.m,ch.d)
  for c in ch.d.contact[:ch.d.ncon]:
   ga,gb=map(int,c.geom)
   if ga not in geoms and gb not in geoms:continue
   if ch.m.body_weldid[ch.m.geom_bodyid[ga]]==ch.m.body_weldid[ch.m.geom_bodyid[gb]]:continue
   if c.dist<-.000001:
    pair={ch.gnames[ga],ch.gnames[gb]};permitted_work=False
    if job['kind']=='working_stroke' and bound<=.05:
     for declaration in SPEC['intended_contacts']:
      if declaration['kind']!='working_stroke':continue
      if declaration['object_id']!=next(e['object_id'] for e in EVENTS if e['id']==job['macro']):continue
      if any(pair=={food,tool} for food in declaration.get('object_geoms',[]) for tool in declaration.get('support_geoms',[])):permitted_work=True
    if permitted_work:continue
    # Every real collision is retained, including food contact. No generic
    # working permission is inherited by a retract or ordinary mechanism.
    first=dict(k=k,kind='appliance physical interference',pair=[ch.gnames[ga],ch.gnames[gb]],penetration_mm=float(-c.dist*1000));break
  if first:break
 rows.append(dict(index=i,id=job['id'],pass_=False,geometric_diagnostic_clear=first is None,joint=n,q_start=start,q_end=end,states_checked=checked,point_step_bound_mm=bound/count*1000,first_blocker=first,reason='Physical processing/retention/food split is unqualified; stationary-arm clearance alone never admits this event',work_contact_kind=job['kind'],long_work_contact_window_unqualified=job['kind']=='working_stroke' and bound>.05,planner_budget_s=65,robot_clearance_strategy='Full first-sample certificate; unchanged pairs invariant; every changed moving-geometry pair queried with exact original shapes'))
write(f'results/mechanism_chunk_{args.lo}_{args.hi}.json',dict(rows=rows,scope='Rejected/unqualified appliance diagnostics, not an executed conserved meal',no_food_spawn=True,no_work_contact_on_nonworking_paths=True))
print('MECHANISM OBLIGATIONS',len(rows),'geometric clear',sum(r.get('geometric_diagnostic_clear',False) for r in rows),'admitted',0)
