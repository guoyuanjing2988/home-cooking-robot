import json,time,copy
import numpy as np,mujoco
import motion_check as mo
import final_check as f
from distance import Bounds
s=f.s;H=s.HERE;beg=time.monotonic();ch,hands=mo.empty_cell();oracle=Bounds(ch,f.required);rng=np.random.default_rng(804);best=None;tried=0
doors=[i for i,n in enumerate(ch.gnames) if n.startswith('cabinet_door_sweep')]
def door_pairs(robot_only=False):
 out=[]
 for a in doors:
  for b,n in enumerate(ch.gnames):
   if b in doors or n.startswith(('upper_cabinet','north_wall','south_wall','south_cabinet','floor')):continue
   if robot_only and not ch.robot[b]:continue
   # Cheap circumscribed-box distance via exact support coordinates.
   lower=0
   for k in range(3):
    axis=np.eye(3)[k]
    if ch.m.geom_type[b]==0:continue
    alo=oracle.support(a,-axis)[k];ahi=oracle.support(a,axis)[k];blo=oracle.support(b,-axis)[k];bhi=oracle.support(b,axis)[k];lower+=max(alo-bhi,blo-ahi,0)**2
   if lower>=.010**2:continue
   v=oracle.pair(a,b)
   if v['lower_m']<.010-1e-6:out.append(dict(pair=[ch.gnames[a],n],gap_lower_mm=v['lower_m']*1000,gap_upper_mm=v['upper_m']*1000,required_mm=10,certified_below_required=v['upper_m']<.010-1e-6))
 return out
for k in range(1800):
 tried=k+1;q=np.array(s.PARK)
 q[ch.qa['R_carriage_x']]=-1.70;q[ch.qa['L_carriage_x']]=.045
 if k:
  for side in s.model.SIDES:
   for n in s.ck.ARMS[side]:q[ch.qa[n]]=rng.uniform(*ch.m.jnt_range[ch.jid[n]])
 for n in s.ck.JAWS:q[ch.qa[n]]=.01
 ch.set_contacts(hands);hits=ch.forbidden(q)
 if hits:continue
 bad,mins,ca=f.contacts(ch,q)
 if bad:continue
 robot_doors=door_pairs(True)
 if robot_doors:continue
 # Arms must fold to rail ends and leave the actual counter frontal zone clear.
 # This audit also reports any fixed infrastructure in a conservative torso box.
 best=dict(q=q.tolist(),min_clearance=mins,robot_door_clear=True,seed=k);break
 if time.monotonic()-beg>300:break
if best is None:
 q=np.array(s.PARK);q[ch.qa['L_carriage_x']]=.045;ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d)
else:q=np.array(best['q'])
ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);bad,mins,ca=f.contacts(ch,q);doors_bad=door_pairs()
# Torso-clearance check of FIXED rails. A user can use some local counter space
# even if this conservative full-front human-use corridor fails.
corridor=dict(min_m=[-1.6,-.75,.85],max_m=[.60,-.05,1.85]);torso=[]
for g,n in enumerate(ch.gnames):
 if not n.startswith(('rail_beam','rail_guide','cable_chain_swept')):continue
 lo=np.array([oracle.support(g,-axis)[i] for i,axis in enumerate(np.eye(3))]);hi=np.array([oracle.support(g,axis)[i] for i,axis in enumerate(np.eye(3))])
 if all(hi>=corridor['min_m']) and all(lo<=corridor['max_m']):torso.append(n)
out=dict(status='FAIL' if bad or doors_bad or torso else 'PASS',parked_robot_reference_pass=not bad,all_upper_doors_openable=not doors_bad,human_counter_corridor_clear=not torso,q=q.tolist(),seeds_tried=tried,solutions_found=int(best is not None),verified_witnesses=int(best is not None),robot_fold_witness=best,parked_blockers=bad,door_infringements=doors_bad,counter_corridor=corridor,fixed_rail_torso_intersections=torso,min_clearance=mins,limits='Door masks are exact unions of inherited conservative full sweeps, not exact hinge solids. A fold snapshot does not establish its approach path. All appliance bodies remain; R211510mm height protrudes10mm above1.35m cabinet bottom. No door/appliance exemption.',elapsed_s=time.monotonic()-beg)
(H/'results/idle.json').write_text(json.dumps(out,indent=2));(H/'models/idle.xml').write_text(ch.xml);print('idle',out['status'],'robot fold',best is not None,'doors',len(doors_bad),'torso',len(torso),'starts',tried)
