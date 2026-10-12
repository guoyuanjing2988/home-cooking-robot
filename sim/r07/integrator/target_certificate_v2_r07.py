"""Exact pose-tolerance obstruction witnesses, independent of arm IK branches.

A material point of the gripper/held geometry is strictly inside a fixed box
after allowing the entire5mm/3degree pose tolerance. Such an endpoint cannot
pass for any carriage or arm configuration. Never used as a positive witness.
"""
import os,sys,json,time
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v2_r07 as v
import numpy as np,mujoco
from distance import Bounds
began=time.monotonic();rows=[]
for index,(ph,sg,key) in enumerate(v.items):
 ch=v.scene(index);m,d=ch.m,ch.d;q=m.qpos0.copy()
 for side,h in sg['poses'][0].items():
  for label in ('minus','plus'):q[ch.qa[side+'_jaw_'+label]]=h['jaw_opening_m']/2
 d.qpos[:]=q;mujoco.mj_forward(m,d);b=Bounds(ch,v.f.required)
 env=[g for g in range(m.ngeom) if not ch.robot[g] and m.geom_type[g]==6 and not ch.gnames[g].startswith('cabinet_door_sweep')]
 certs=[]
 for k in (0,1):
  found=None
  for pi,hands in enumerate(sg['poses']):
   if found:break
   for side,h in hands.items():
    for label in ('minus','plus'):q[ch.qa[side+'_jaw_'+label]]=h['jaw_opening_m']/2
   d.qpos[:]=q;mujoco.mj_forward(m,d)
   for side,h in hands.items():
    sid=m.site(side+'_prep').id;origin=d.site_xpos[sid];rotation=d.site_xmat[sid].reshape(3,3)
    target=np.array(h['pos']);desired=ch.target_rotation(h,k)
    for g,n in enumerate(ch.gnames):
     rigid_tip=m.body_weldid[m.geom_bodyid[g]]==m.body_weldid[m.site_bodyid[sid]]
     if not n.startswith(side+'_') or not(ch.gripper(g) or ch.held[g] or rigid_tip):continue
     typ=int(m.geom_type[g]);sz=m.geom_size[g];gr=d.geom_xmat[g].reshape(3,3)
     if typ==6:local=np.array([[0,0,0]]+[[x*sz[0],y*sz[1],z*sz[2]] for x in (-1,1) for y in (-1,1) for z in (-1,1)])
     elif typ in (2,3,5):local=np.array([[0,0,0]])
     elif typ==7:local=b.local[g]
     else:continue
     source=local@gr.T+d.geom_xpos[g];tcp_local=(source-origin)@rotation
     points=tcp_local@desired.T+target;displacement=.005+2*np.linalg.norm(tcp_local,axis=1)*np.sin(np.radians(3)/2)
     for e in env:
      required=v.f.required(ch,g,e)
      if required is None:continue
      if any(c['face']==ch.gnames[e] and n==side+'_held_'+part for c in h.get('contacts',[]) for part in c.get('held_parts',[])):continue
      er=d.geom_xmat[e].reshape(3,3);ep=(points-d.geom_xpos[e])@er
      radius=float(sz[0]) if typ in (2,3) else float(min(sz)) if typ==6 else float(min(sz[0],sz[1])) if typ==5 else 0
      if radius>0:
       delta=abs(ep[0])-m.geom_size[e]
       signed=float(np.linalg.norm(np.maximum(delta,0))+min(0,max(delta)))
       upper=signed-radius+displacement[0]
       if upper<required[0]-1e-6:
        found=dict(k=k,pose=pi,side=side,pair=[n,ch.gnames[e]],inscribed_sphere_center_m=points[0].tolist(),radius_m=radius,maximum_pose_tolerance_displacement_mm=float(displacement[0]*1000),maximum_possible_gap_mm=float(upper*1000),required_gap_mm=float(required[0]*1000),reason='A full sphere inside this rigid terminal-link/gripper/held primitive remains closer than the required gap to this fixed box, even at the most favourable5mm/3degree tolerance. Signed box distance is1-Lipschitz; no arm/carriage IK branch can repair this declared target.')
        break
      depth=np.min(m.geom_size[e]-abs(ep),axis=1);reserve=depth-displacement
      ix=int(np.argmax(reserve))
      if reserve[ix]>1e-6:
       found=dict(k=k,pose=pi,side=side,pair=[n,ch.gnames[e]],point_world_m=points[ix].tolist(),point_tcp_m=tcp_local[ix].tolist(),inside_box_depth_mm=float(depth[ix]*1000),maximum_pose_tolerance_displacement_mm=float(displacement[ix]*1000),remaining_inside_mm=float(reserve[ix]*1000),reason='A material point remains strictly inside this forbidden fixed box throughout the full5mm/3degree TCP tolerance. No IK branch or carriage position can repair this target.')
       break
     if found:break
    if found:break
  certs.append(found)
 row=dict(index=index,stroke=key,impossible_at_declared_targets=all(c is not None for c in certs),orientation_certificates=certs)
 rows.append(row)
 if index%10==0:print(v.ID,index,'certified blocked',sum(r['impossible_at_declared_targets'] for r in rows),flush=True)
 out=dict(layout=v.ID,rows=rows,complete=len(rows)==len(v.items),elapsed_s=time.monotonic()-began,scope='Negative endpoint certificates only. All admissible k modulo2 orientations considered. They concern the declared station/target layout; they are NOT an impossibility proof for the under-cabinet architecture.')
 (v.O/'layouts'/f'{v.ID}_target_certificates.json').write_text(json.dumps(out,indent=2))
print('CERTIFIED',sum(r['impossible_at_declared_targets'] for r in rows),'/',len(rows),flush=True)
