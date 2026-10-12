"""Geometric storage/retract concept; not credited to the working cell."""
import json,time,xml.etree.ElementTree as E
import numpy as np,mujoco
import motion_check as mo
import final_check as f
from distance import Bounds
s=f.s;H=s.HERE;beg=time.monotonic();ch,hands=mo.empty_cell();root=E.fromstring(ch.xml);w=root.find('worldbody')
rail=w.find(".//body[@name='rail_structure']");rail.set('pos','0 0 .95')
for g in rail.findall('geom'):
 if g.get('name','').startswith(('wall_mount_-','wall_mount_0.18')):
  pos=np.fromstring(g.get('pos'),sep=' ');pos[2]+=.10;g.set('pos',s.model.fmt(pos))
for g in list(w):
 if g.tag=='geom' and g.get('name','').startswith('slicer_') and not g.get('name','').startswith(('slicer_bowl_land','slicer_discharge')):w.remove(g)
s.model.box(w,'household_processor_full_envelope',[.425,.10,.85+.395/2],[.230,.230,.395],robot=False)
s.model.box(w,'declared_ceiling',[-.0,.0,2.825],[5.,4.,.05],robot=False)
ch.xml=E.tostring(root,encoding='unicode');ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));oracle=Bounds(ch,f.required);rng=np.random.default_rng(881);doors=[i for i,n in enumerate(ch.gnames) if n.startswith('cabinet_door_sweep')];best=None;reasons={};tried=0
def separated(a,b):
 delta=[]
 for k,axis in enumerate(np.eye(3)):
  delta.append(max(oracle.support(a,-axis)[k]-oracle.support(b,axis)[k],oracle.support(b,-axis)[k]-oracle.support(a,axis)[k],0))
 if np.linalg.norm(delta)>=.010:return True
 return oracle.pair(a,b)['lower_m']>=.010-1e-6
def idle_hits():
 bad=[]
 for a in doors:
  for b,n in enumerate(ch.gnames):
   if b in doors or n.startswith(('upper_cabinet','north_wall','south_wall','south_cabinet','floor','declared_ceiling')) or n=='protected_stove':continue
   if not separated(a,b):bad.append([ch.gnames[a],n])
 return bad
for k in range(7000):
 tried=k+1
 if time.monotonic()-beg>320:break
 q=np.array(s.PARK);q[ch.qa['R_carriage_x']]=-1.70;q[ch.qa['L_carriage_x']]=.045
 if k:
  for n in s.ck.JOINTS:q[ch.qa[n]]=rng.uniform(*ch.m.jnt_range[ch.jid[n]])
 for n in s.ck.JAWS:q[ch.qa[n]]=.01
 ch.set_contacts(hands)
 if ch.forbidden(q):continue
 # First filter all robot AABBs intersecting the working human corridor.
 humanoid=False
 for g in np.flatnonzero(ch.robot):
  lo=np.array([oracle.support(g,-axis)[i] for i,axis in enumerate(np.eye(3))]);hi=np.array([oracle.support(g,axis)[i] for i,axis in enumerate(np.eye(3))])
  if all(hi>[-1.6,-.75,.85]) and all(lo<[.6,-.05,1.85]):humanoid=True;break
 if humanoid:continue
 if idle_hits():continue
 bad,mins,ca=f.contacts(ch,q)
 if bad:continue
 best=dict(q=q.tolist(),seed=k,min_clearance=mins);break
q=np.array(best['q'] if best else s.PARK);ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);bad,mins,ca=f.contacts(ch,q);doors_bad=idle_hits()
out=dict(status='IDLE_SNAPSHOT_PASS_ONLY' if best else 'NO_IDLE_SNAPSHOT_WITNESS',full_cell_pass=False,seeds_tried=tried,solutions_found=int(best is not None),verified_witnesses=int(best is not None),q=q.tolist(),robot_forbidden=bad,door_infringements=doors_bad,concept=dict(rail_vertical_retraction_m=.95,full_household_envelope_m=[.230,.230,.395],ceiling_underside_m=2.8,added_lift_allowance_cny=30000,spring_applied_vertical_brakes_required=True),admission='Separate storage concept only: complete lifted geometry checked at one state; vertical guides/actuator/brake hardware, fixed anchor interface, full lift path, working105stroke geometry, processor cut quality and site mounting are unverified. No pass credited to best or cheapest.',elapsed_s=time.monotonic()-beg)
(H/'results/idle_variant.json').write_text(json.dumps(out,indent=2));(H/'models/idle_variant.xml').write_text(ch.xml);print('idle concept',out['status'],tried,len(bad),len(doors_bad))
