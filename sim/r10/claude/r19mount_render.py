"""R19 #42: pictures of the mount options on the UR5e wrist (new file; reads only). The wrist (UR5e enc2 collision hulls),
the PGC housing (scene.oem_pgc_drawing) and the bracket pieces of each option, side view across the jaw plane (looking
along -y_F) and a 3/4 view, flange frame at the origin. Only the arm's last links, R_tool and the bracket are drawn.
python r19mount_render.py -> results/r19/mount/view_<arm>.png"""
import sys,os
sys.path.insert(0,'.')
import numpy as np,mujoco,xml.etree.ElementTree as E
from PIL import Image
def view(arm):
 os.environ['ARM']=arm
 import chain,kitchen16 as K
 from scene import build
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},arm=arm)
 tree,meta=build(cfg,None);m=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));d=mujoco.MjData(m);mujoco.mj_forward(m,d)
 keep={m.body(n).id for n in ('R_arm_wrist_2_link','R_arm_wrist_3_link','R_tool','R_jaw_minus','R_jaw_plus')}
 for g in range(m.ngeom):
  if m.geom_bodyid[g] not in keep:m.geom_rgba[g,3]=0
  else:
   n=m.geom(g).name;m.geom_group[g]=0
   m.geom_rgba[g]=[.85,.55,.15,1] if 'mount' in n else [.2,.25,.3,.9] if n.startswith('R_gripper_oem') else [.6,.62,.65,.55] if m.geom_bodyid[g] in (m.body('R_arm_wrist_2_link').id,m.body('R_arm_wrist_3_link').id) else [.4,.45,.5,1]
 fl=m.site('R_attachment_site').id;pf=d.site_xpos[fl].copy();Rf=d.site_xmat[fl].reshape(3,3).copy()
 r=mujoco.Renderer(m,480,480);imgs=[]
 opt=mujoco.MjvOption();opt.geomgroup[:]=1
 for az,el,dirF in ((0,0,np.array([0,-1.,0])),(0,0,np.array([.6,-.6,.35]))):
  cam=mujoco.MjvCamera();cam.type=mujoco.mjtCamera.mjCAMERA_FREE;cam.lookat[:]=pf+Rf@np.array([0.02,0,.06]);cam.distance=.42
  dw=Rf@dirF;dw/=np.linalg.norm(dw);cam.azimuth=float(np.degrees(np.arctan2(-dw[1],-dw[0])));cam.elevation=float(np.degrees(np.arcsin(-dw[2])))
  r.update_scene(d,cam,opt);imgs.append(r.render())
 os.makedirs('results/r19/mount',exist_ok=True);fn=f'results/r19/mount/view_{arm}.png';Image.fromarray(np.concatenate(imgs,1)).save(fn);print(fn)
if __name__=='__main__':
 for a in (sys.argv[1:] or ['ur5e_enc2_pgc','ur5e_enc2_pgc_m1','ur5e_enc2_pgc_m2','ur5e_enc2_pgc_m3']):view(a)
