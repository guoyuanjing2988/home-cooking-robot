"""R17 layout survey: every geom of the R16 cooking-time scene that sits on or above the counter
(world AABB, z top >= 0.84), sorted by x, plus a top-down still of the counter run.
python r17layout.py [out.png]"""
import sys,numpy as np,mujoco
from PIL import Image
import chain
from scene import build
from dress import dress,HIDE
cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True);tree,_=build(cfg,None)
m=dress(tree)
d=mujoco.MjData(m);d.qpos[0]=-1.4;mujoco.mj_forward(m,d)
rows=[]
for g in range(m.ngeom):
 if m.geom_bodyid[g]!=0:continue   # world geoms only (the robot is not listed)
 n=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_GEOM,g) or f'#{g}'
 c=d.geom_xpos[g];R=d.geom_xmat[g].reshape(3,3);t=m.geom_type[g];s=m.geom_size[g]
 if t==mujoco.mjtGeom.mjGEOM_BOX:h=np.abs(R)@s
 elif t==mujoco.mjtGeom.mjGEOM_CYLINDER:h=np.abs(R)@np.array([s[0],s[0],s[1]])
 elif t==mujoco.mjtGeom.mjGEOM_SPHERE:h=np.full(3,s[0])
 elif t==mujoco.mjtGeom.mjGEOM_CAPSULE:h=np.abs(R)@np.array([s[0],s[0],s[1]+s[0]])
 else:h=np.array([m.geom_rbound[g]]*3)
 lo,hi=c-h,c+h
 if hi[2]<.84 or lo[2]>2.2 or lo[1]>.7:continue
 rows.append((lo[0],n,lo,hi))
for _,n,lo,hi in sorted(rows,key=lambda r:r[0]):
 if n.startswith('r15_wok_t'):continue
 print(f'{n:28s} x {lo[0]:6.2f}..{hi[0]:5.2f}  y {lo[1]:5.2f}..{hi[1]:5.2f}  z {lo[2]:5.2f}..{hi[2]:5.2f}')
if len(sys.argv)>1:
 rr=mujoco.Renderer(m,500,1600);c=mujoco.MjvCamera();c.lookat[:]=[0,.25,.9];c.azimuth,c.elevation,c.distance=90,-89.9,3.0
 o=mujoco.MjvOption();o.geomgroup[:]=1;o.geomgroup[HIDE]=0;rr.update_scene(d,c,o);Image.fromarray(rr.render()).save(sys.argv[1]);print(sys.argv[1])
