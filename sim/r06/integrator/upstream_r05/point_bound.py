"""Model-derived global bound on displacement of every geometry point.

For a hinge, bound the distance from its centre to each downstream geometry by
the sum of fixed body offsets, geom centre offset and its enclosing radius. The
arc displacement is <=radius*|dq|. Slides contribute |dq|. Triangle inequality
then bounds each point, and the maximum is taken over all robot/held geometry.
"""
import numpy as np,mujoco
class PointBound:
 def __init__(self,ch):
  m=ch.m;self.ch=ch;self.weights=np.zeros((m.ngeom,m.nq));self.radius=0.;self.hinges=[];self.slides=[];self.levers=[]
  for j in range(m.njnt):
   if m.jnt_type[j]==mujoco.mjtJoint.mjJNT_HINGE:self.hinges.append(int(m.jnt_qposadr[j]))
   elif m.jnt_type[j]==mujoco.mjtJoint.mjJNT_SLIDE:self.slides.append(int(m.jnt_qposadr[j]))
  for g in range(m.ngeom):
   if not ch.robot[g] and not ch.held[g]:continue
   body=int(m.geom_bodyid[g]);lever=float(np.linalg.norm(m.geom_pos[g])+m.geom_rbound[g]);chain=lever;down=[]
   while body:
    for j in range(int(m.body_jntadr[body]),int(m.body_jntadr[body]+m.body_jntnum[body])):
     k=int(m.jnt_qposadr[j]);typ=m.jnt_type[j]
     if typ==mujoco.mjtJoint.mjJNT_HINGE:
      self.weights[g,k]=lever+np.linalg.norm(m.jnt_pos[j]);self.levers.append((g,j,k,np.array(down,dtype=int)))
     elif typ==mujoco.mjtJoint.mjJNT_SLIDE:self.weights[g,k]=1
     else:raise ValueError('Free/ball joints need a separate bound')
     down.append(k)
    # A downstream slide (notably an opening finger) changes its body's
    # translation. Include its full public travel in all upstream hinge radii.
    travel=sum(float(max(abs(m.jnt_range[j]))) for j in range(int(m.body_jntadr[body]),int(m.body_jntadr[body]+m.body_jntnum[body])) if m.jnt_type[j]==mujoco.mjtJoint.mjJNT_SLIDE)
    offset=float(np.linalg.norm(m.body_pos[body]))+travel
    pivot_shift=sum(2*float(np.linalg.norm(m.jnt_pos[j])) for j in range(int(m.body_jntadr[body]),int(m.body_jntadr[body]+m.body_jntnum[body])))
    lever+=offset+pivot_shift;chain+=offset+pivot_shift
    body=int(m.body_parentid[body])
   self.radius=max(self.radius,chain)
 def bound(self,dq):return float(np.max(self.weights@abs(np.asarray(dq))))
 def segment_bound(self,a,b):
  """Tighten hinge radii using the actual start and downstream-only travel.

  Current hinge motion and upstream rigid motion preserve lever distance.
  Downstream travel is bounded by the global coefficients already proved
  above. Thus R(start)+downstream_displacement bounds the hinge lever for the
  entire segment. Taking the smaller of two valid bounds remains valid.
  """
  dq=abs(np.asarray(b)-np.asarray(a));ch=self.ch;ch.d.qpos[:]=a;mujoco.mj_kinematics(ch.m,ch.d);values=np.zeros(ch.m.ngeom)
  for g,j,k,down in self.levers:
   r=float(np.linalg.norm(ch.d.geom_xpos[g]-ch.d.xanchor[j])+ch.m.geom_rbound[g])
   if len(down):r+=float(self.weights[g,down]@dq[down])
   values[g]+=r*dq[k]
  values+=self.weights[:,self.slides]@dq[self.slides]
  return min(self.bound(dq),float(max(values)))
 def curvature(self,dq):
  """Conservative |d2(point)/ds2| for q(s)=a+s*dq on a serial chain.

  Products of hinge rotations contribute <=R*(sum|dtheta|)^2. Rotated
  linear-slide terms add <=2*(sum|dtheta|)*(sum|dslide|). Using all joints and
  the largest full-chain radius overbounds every point in either arm.
  """
  dq=abs(np.asarray(dq));h=float(sum(dq[self.hinges]));s=float(sum(dq[self.slides]));return self.radius*h*h+2*h*s
