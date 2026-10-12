"""Verify the whole-bowl trial is a rigid yaw, with no smaller geometry."""
import os,sys,json
os.environ['R07_LAYOUT']='L83'
import runtime_v7_r07 as v
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
old=mujoco.MjModel.from_xml_path(str(v.H/'models/L74_stroke_0.xml'));od=mujoco.MjData(old);mujoco.mj_forward(old,od);ch=v.scene(0);mujoco.mj_forward(ch.m,ch.d);yaw=Rotation.from_euler('z',90,degrees=True).as_matrix();rows=[]
for i in range(old.ngeom):
 name=old.geom(i).name;j=ch.m.geom(name).id;same=bool(old.geom_type[i]==ch.m.geom_type[j] and np.max(abs(old.geom_size[i]-ch.m.geom_size[j]))<1e-10)
 if name.startswith('stored_bowl_'):
  body=int(old.geom_bodyid[i])
  while old.body_parentid[body] and not old.body(body).name.startswith('stored_bowl_'):body=int(old.body_parentid[body])
  while old.body_parentid[body] and old.body(body).name.endswith('_object'):body=int(old.body_parentid[body])
  pivot=od.xpos[body];target=pivot+yaw@(od.geom_xpos[i]-pivot);rotation=yaw@od.geom_xmat[i].reshape(3,3)
 else:target=od.geom_xpos[i];rotation=od.geom_xmat[i].reshape(3,3)
 error=max(float(np.max(abs(target-ch.d.geom_xpos[j]))),float(np.max(abs(rotation-ch.d.geom_xmat[j].reshape(3,3)))));rows.append(dict(part=name,dimensions_unchanged=same,expected_rigid_pose_error=error,pass_=same and error<1e-7))
checks=dict(geom_count_unchanged=old.ngeom==ch.m.ngeom,all_solid_dimensions_and_rigid_poses=all(x['pass_'] for x in rows),tools_and_masses_unchanged=v.P['tools']==json.loads((v.O/'layouts/L74_process_v4.json').read_text())['tools'])
(v.H/'models/L83_yaw_geometry_probe.xml').write_text(ch.xml);out=dict(layout='L83',pass_=all(checks.values()),checks=checks,rows=rows,scope='Whole upright bowl/bail rigid90deg yaw around unchanged body origin; all non-bowl full geometries and original masses unchanged. No reach/path qualification.')
(v.O/'bowl_yaw_validation_v7.json').write_text(json.dumps(out,indent=2));print('BOWL_YAW_GEOMETRY',out['pass_'],checks);assert out['pass_']
