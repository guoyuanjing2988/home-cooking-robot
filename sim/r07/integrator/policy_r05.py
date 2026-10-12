"""R05 face-only wall interfaces and binding support windows."""
import numpy as np
WALL_FACES={'wall_mount_-1.84':'rear +Y face','wall_mount_0.18':'rear +Y face','wall_mount_recess_left':'rear +Y face','wall_mount_recess_right':'rear +Y face'}
def wall_mating(ch,g):
 if ch.gnames[g] not in WALL_FACES:return False
 # The two entire plates stay on the room side; their intersection with the
 # wall can only be the explicitly named planar rear mating face.
 r=ch.d.geom_xmat[g].reshape(3,3);p=ch.d.geom_xpos[g];s=ch.m.geom_size[g]
 wall=ch.gnames.index('north_wall');wr=ch.d.geom_xmat[wall].reshape(3,3)
 wall_face=ch.d.geom_xpos[wall,1]-ch.m.geom_size[wall,1]
 return bool(np.max(abs(r-np.eye(3)))<1e-9 and np.max(abs(wr-np.eye(3)))<1e-9 and abs(p[1]+s[1]-wall_face)<1e-8 and p[1]-s[1]<wall_face-1e-3)
def valid_window(ch,w):
 side=w['side'];sid=ch.m.site(side+'_prep').id
 dp=ch.d.site_xpos[sid]-np.array(w['tcp_origin_m']);n=np.array(w['normal'])
 axial=float(dp@n);lateral=np.linalg.norm(dp-axial*n)
 rot=ch.d.site_xmat[sid].reshape(3,3)
 return bool(lateral<=0.00002 and -0.00002<=axial<=.05000001 and np.max(abs(rot-np.array(w['tcp_rotation'])))<=.0002)
def named_face_boundary(ch,w,c):
 """An edge belongs to its named closed face even if its normal is mixed.

 This is not permission for the adjacent top/side face: the witness must lie
 within20um of the named plane, within its finite rectangle, AND on an edge
 of that rectangle. Interiors still use the inherited face/normal test.
 """
 face=w['face'];g=ch.gnames.index(face)
 if ch.m.geom_type[g]!=6:return False
 p=ch.d.geom_xmat[g].reshape(3,3).T@(c.pos-ch.d.geom_xpos[g]);sz=ch.m.geom_size[g]
 axis=0 if face.startswith('peel_endstop') else 2
 sign=(1 if face.endswith('-1') else -1) if axis==0 else 1
 others=[i for i in range(3) if i!=axis]
 return bool(abs(p[axis]-sign*sz[axis])<=.00002 and all(abs(p[i])<=sz[i]+.00002 for i in others) and any(abs(abs(p[i])-sz[i])<=.00002 for i in others))
def window_pairs(ch):
 """Permissions apply only when a planner supplies a validated local window.
 Each window records the original exact-face declaration and actual TCP origin.
 Lateral/rotation departure invalidates it; >=5mm pair gaps need no permission.
 """
 out=set()
 for w in getattr(ch,'contact_windows',[]):
  side=w['side']
  if not valid_window(ch,w):continue
  face=w['face']
  if face not in ch.gnames:continue
  for part in w['held_parts']:
   name=side+'_held_'+part
   if name not in ch.gnames:continue
   a=ch.gnames.index(face);b=ch.gnames.index(name)
   # A permissible window doesn't admit side collisions or deeper insertion.
   # Validate all actual contact witnesses on this pair using unchanged face
   # and normal test. Separated proximity uses the declared straight departure.
   # MuJoCo's margin emits positive-distance proximity records too. Their
   # normals may rotate around a support edge during a legitimate departure.
   # Only actual touching/penetrating witnesses require the contact-face test;
   # separated proximity is governed by the fixed straight insertion window.
   contacts=[c for c in ch.d.contact[:ch.d.ncon] if c.dist<=0 and set(map(int,c.geom))=={a,b}]
   if contacts:
    import final_check as f
    if not all(f.intentional(ch,c) or named_face_boundary(ch,w,c) for c in contacts):continue
   gap=ch.bounds.pair(a,b)
   if gap['lower_m']>=.005-1e-6:continue
   out.add(frozenset([face,name]))
 return out
