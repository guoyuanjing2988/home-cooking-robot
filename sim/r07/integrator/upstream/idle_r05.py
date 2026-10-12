"""Idle end/recess trials, full geometry retained and all doors/corridor checked."""
import json,time,copy,sys,xml.etree.ElementTree as E
import numpy as np,mujoco
import final_check as f,motion_check as mo
from distance import Bounds
s=f.s;H=s.HERE;beg=time.monotonic();rng=np.random.default_rng(50505);trials=[];repair='--repair' in sys.argv
def make(lift):
 ch,h=mo.empty_cell();root=E.fromstring(ch.xml);w=root.find('worldbody');rail=w.find(".//body[@name='rail_structure']");rail.set('pos',f'0 0 {lift}')
 # Keep all 2.8m beams and working guides. Additional side bays are tested as
 # full-length extensions, never a shortened/smaller frame.
 for g in rail.findall('geom'):
  if g.get('name','').startswith(('rail_beam_','rail_guide_','cable_chain_swept_cover_')):
   # Original split boxes remain; fill extensions as separately priced boxes.
   pass
 for i in range(2):
  z=s.model.CONFIG['height'] if i==0 else s.model.CONFIG['helper_height'];by=s.model.CONFIG['front_mount_y']-s.model.CONFIG['pitch']*i-.4
  for x in (-2.65,1.15):s.model.box(rail,f'rail_beam_idle_extension_{i}_{x}',[x,by,z+.04],[1.0,.3,.05],robot=True,mass=51.16944/2.8)
  # Guides/cable envelopes must also reach the extended carriage positions.
  # Original2.4m guide ends are[-1.95,.45]; retain their complete union and
  # append1.2m pieces to[-3.15,1.65], with original sections/mass per metre.
  for x in (-2.55,1.05):
   for sign in (-1,1):s.model.box(rail,f'rail_guide_idle_extension_{i}_{x}_{sign}',[x,by+sign*.17,z+.046],[1.2,.04,.048],robot=True,mass=1.)
   s.model.box(rail,f'cable_chain_idle_extension_{i}_{x}',[x,by-.05,z+.0795],[1.2,.245,.025],robot=True,mass=.8)
 for side in s.model.SIDES:root.find(f".//joint[@name='{side}_carriage_x']").set('range','-2.9 1.35')
 # Full guide/drive housings of the storage elevator live outside all original
 # cabinets and the person corridor. They are explicit engineering envelopes.
 if lift:
  for x in (-3.02,1.98):
   s.model.box(w,'recess_vertical_guide_'+str(x),[x,.45,1.75],[.10,.10,1.60],robot=True)
   s.model.box(w,'recess_spring_brake_drive_'+str(x),[x,.43,2.62],[.20,.22,.20],robot=True)
  s.model.box(w,'recess_upper_header',[-.52,.45,2.57],[5.1,.10,.10],robot=True)
  s.model.box(w,'declared_ceiling',[0,0,2.925],[7,4,.05],robot=False)
  if repair:
   wall=w.find("geom[@name='north_wall']");wall.set('pos','-.4 .62 1.45');wall.set('size','2.9 .02 1.45') # full original wall contained in declared5.8m x2.9m wall
   for g in rail.findall('geom'):
    name=g.get('name','')
    if name in ('wall_mount_-1.84','wall_mount_0.18'):
     p=np.fromstring(g.get('pos'),sep=' ');p[0]=-3.02 if name.endswith('-1.84') else 1.98;g.set('pos',s.model.fmt(p));g.set('name','wall_mount_recess_left' if p[0]<0 else 'wall_mount_recess_right')
   # Full appliance on a dedicated motorized 13kg lift/transfer pallet; exact
   # housing union is retained, with no arm credited with carrying it.
   for g in w.findall('geom'):
    if g.get('name','').startswith('slicer_'):
     p=np.fromstring(g.get('pos'),sep=' ');p[0]-=2.95;g.set('pos',s.model.fmt(p))
   s.model.box(w,'appliance_storage_pallet',[-2.55,.20,.875],[.50,.44,.035],robot=True)
   s.model.box(w,'appliance_storage_drive_brake',[-2.55,.30,.65],[.25,.25,.18],robot=True)
 ch.xml=E.tostring(root,encoding='unicode');ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.set_contacts(h);return ch,h
def idle_check(ch,q):
 ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);oracle=Bounds(ch,f.required);hits,mins,audit=f.contacts(ch,q);doorhits=[];human=[]
 doors=[i for i,n in enumerate(ch.gnames) if n.startswith('cabinet_door_sweep')]
 bounds={}
 for g in range(ch.m.ngeom):
  if ch.m.geom_type[g]==0:continue
  lo=np.array([oracle.support(g,-axis)[k] for k,axis in enumerate(np.eye(3))]);hi=np.array([oracle.support(g,axis)[k] for k,axis in enumerate(np.eye(3))]);bounds[g]=(lo,hi)
  if ch.robot[g] and all(hi>[-1.6,-.75,.85]) and all(lo<[.6,-.05,1.85]):human.append(ch.gnames[g])
 for a in doors:
  for b,n in enumerate(ch.gnames):
   if b not in bounds or b in doors or n.startswith(('upper_cabinet','north_wall','south_wall','south_cabinet','floor','declared_ceiling')):continue
   if n=='protected_stove':continue # logical robot exclusion volume, not a physical door obstruction; retained in robot reference gate
   delta=np.maximum(np.maximum(bounds[a][0]-bounds[b][1],bounds[b][0]-bounds[a][1]),0)
   if np.linalg.norm(delta)>=.01:continue
   v=oracle.pair(a,b)
   if v['lower_m']<.01-1e-6:doorhits.append(dict(pair=[ch.gnames[a],n],gap_lower_mm=v['lower_m']*1000,gap_upper_mm=v['upper_m']*1000))
 return dict(ok=not hits and not doorhits and not human,reference_blockers=hits,door_blockers=doorhits,human_intersections=human,min_clearance=mins)
best=None;starts=0
for lift in (0,.65,.8,.95):
 ch,h=make(lift);seed_best=None;rows=[]
 for k in range(180 if repair else 900):
  if time.monotonic()-beg>270:break
  starts+=1;q=np.array(s.PARK);q[ch.qa['R_carriage_x']]=-2.85;q[ch.qa['L_carriage_x']]=1.30
  if k:
   for n in s.ck.JOINTS:q[ch.qa[n]]=np.clip(np.array(s.PARK)[ch.qa[n]]+rng.normal(0,.45),*ch.m.jnt_range[ch.jid[n]])
  if ch.forbidden(q):continue
  result=idle_check(ch,q);rows.append(dict(seed=k,**result))
  if seed_best is None or len(result['door_blockers'])+len(result['human_intersections'])<seed_best['score']:seed_best=dict(q=q.tolist(),score=len(result['door_blockers'])+len(result['human_intersections']),result=result,seed=k)
  if result['ok']:best=dict(q=q.tolist(),lift_m=lift,result=result,seed=k,xml=ch.xml);break
 trials.append(dict(lift_m=lift,starts_tried=k+1,clear_reference_candidates=len(rows),best=seed_best))
 if best:break
 print('idle lift',lift,'checked',k+1,'candidate',bool(seed_best),flush=True)
if best is None:
 ch,h=make(.95);q=np.array(s.PARK);q[ch.qa['R_carriage_x']]=-2.85;q[ch.qa['L_carriage_x']]=1.30;result=idle_check(ch,q);best=dict(q=q.tolist(),lift_m=.95,result=result,seed=None,xml=ch.xml)
(H/'models/idle_r05.xml').write_text(best.pop('xml'))
out=dict(schema='r05.idle',status='PASS' if best['result']['ok'] else 'FAIL',pass_=best['result']['ok'],parked_snapshot=best,trials=trials,seeds_tried=starts,solutions_found=int(best['result']['ok']),verified_witnesses=int(best['result']['ok']),extra_wall_length_m=2.1,extra_counter_span_m=2.2,declared_wall_span_m=[-3.3,2.5],baseline_wall_span_m=[-1.85,1.85],baseline_counter_span_m=[-1.8,1.8],declared_ceiling_underside_m=2.9,corridor=dict(min_m=[-1.6,-.75,.85],max_m=[.6,-.05,1.85]),storage_motion_verified=False,added_geometry='Full original frame + 1m beam extension at each end per lane, two full 1.6m recess guides, two spring-brake-drive envelopes and 5.1m header',appliance_retained='Full R211 retained on motorized storage pallet in left bay' if repair else 'Full R211 retained: no smaller processor substituted. Its cabinet-door obstruction must also be solved.',elapsed_s=time.monotonic()-beg)
f.write('idle_repair.json' if repair else 'idle.json',out);print('IDLE',out['status'],'starts',starts,'doors',len(best['result']['door_blockers']),'human',len(best['result']['human_intersections']),flush=True)
