"""How far do the UR5e visual meshes (MuJoCo Menagerie) stick out of the collision capsules the sim uses
(the same Menagerie collision geoms as models/base.xml)? Per visual mesh: max protrusion of any vertex
outside the union of all arm collision geoms, over random joint configurations."""
import sys,numpy as np,mujoco
MEN=sys.argv[1]
m=mujoco.MjModel.from_xml_path(MEN+'/ur5e.xml');d=mujoco.MjData(m)
col=[g for g in range(m.ngeom) if m.geom_type[g] in (mujoco.mjtGeom.mjGEOM_CAPSULE,mujoco.mjtGeom.mjGEOM_CYLINDER)]
vis=[g for g in range(m.ngeom) if m.geom_type[g]==mujoco.mjtGeom.mjGEOM_MESH]
print('collision geoms',[(mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_BODY,m.geom_bodyid[g]),int(m.geom_type[g]),m.geom_size[g][:2].round(3).tolist()) for g in col])
def sdf(P,g):
 R=d.geom_xmat[g].reshape(3,3);L=(P-d.geom_xpos[g])@R;r,h=m.geom_size[g][:2]
 if m.geom_type[g]==mujoco.mjtGeom.mjGEOM_CAPSULE:
  z=np.clip(L[:,2],-h,h);return np.linalg.norm(L-np.c_[0*z,0*z,z],axis=1)-r
 rad=np.linalg.norm(L[:,:2],axis=1)-r;ax=np.abs(L[:,2])-h
 return np.where((rad>0)&(ax>0),np.hypot(rad,ax),np.maximum(rad,ax))
rng=np.random.default_rng(0);worst={}
for k in range(40):
 d.qpos[:]=rng.uniform(-np.pi,np.pi,m.nq) if k else 0;mujoco.mj_kinematics(m,d)
 for g in vis:
  a,n=m.mesh_vertadr[m.geom_dataid[g]],m.mesh_vertnum[m.geom_dataid[g]];V=m.mesh_vert[a:a+n]
  P=d.geom_xpos[g]+V@d.geom_xmat[g].reshape(3,3).T
  s=np.min([sdf(P,c) for c in col],axis=0)
  nm=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_BODY,m.geom_bodyid[g])
  worst[nm]=max(worst.get(nm,-1),float(s.max()))
for nm,v in worst.items():print(f'{nm:18s} max protrusion {v*1000:6.1f} mm')
