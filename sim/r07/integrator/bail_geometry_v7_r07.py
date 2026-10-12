"""Verify full original bowl solids and stationary shells after handle articulation."""
import sys,subprocess,json
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results'
if sys.argv[1]=='dump':
 import os
 os.environ['R07_LAYOUT']=sys.argv[2]
 import runtime_v7_r07 as v
 (H/'models'/f'{v.ID}_bail_validation_v7.xml').write_text(v.scene(0).xml)
 raise SystemExit()
ID=sys.argv[1]
for label in ('L84',ID):subprocess.run([sys.executable,'-B',__file__,'dump',label],check=True,timeout=30)
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
cfg=json.loads((O/'layouts'/f'{ID}.json').read_text())
models=[mujoco.MjModel.from_xml_path(str(H/'models'/f'{label}_bail_validation_v7.xml')) for label in ('L84',ID)];data=[mujoco.MjData(m) for m in models]
for m,d in zip(models,data):mujoco.mj_forward(m,d)
m0,m1=models;d0,d1=data;rows=[]
for i in range(m0.ngeom):
 name=m0.geom(i).name
 if not name.startswith('stored_bowl_'):continue
 j=m1.geom(name).id;dimensions=bool(m0.geom_type[i]==m1.geom_type[j] and np.max(abs(m0.geom_size[i]-m1.geom_size[j]))<1e-10);stationary=any(s in name for s in ('bowl_outer','collar','contents'))
 product=next(prod for prod in ('carrot','potato','leafy_greens','tomato') if name.startswith('stored_bowl_'+prod+'_'));yaw=Rotation.from_euler('z',cfg.get('bowl_yaw_by_product',{}).get(product,0),degrees=True);center=np.array(cfg['station_frames']['output_'+product]['new_center']);expected_pos=center+yaw.apply(d0.geom_xpos[i]-center);expected_rot=yaw.as_matrix()@d0.geom_xmat[i].reshape(3,3)
 error=max(float(np.max(abs(expected_pos-d1.geom_xpos[j]))),float(np.max(abs(expected_rot-d1.geom_xmat[j].reshape(3,3)))));rows.append(dict(part=name,original_type_and_dimensions_preserved=dimensions,stationary_shell_or_collar=error<1e-6 if stationary else None,world_matrix_error=error,declared_whole_bowl_yaw_deg=cfg.get('bowl_yaw_by_product',{}).get(product,0)))
checks=dict(full_original_solids_preserved=all(r['original_type_and_dimensions_preserved'] for r in rows),shells_and_collars_stay_in_place=all(r['stationary_shell_or_collar'] is not False for r in rows),sixteen_full_lock_solids=sum('stored_bowl_' in m1.geom(i).name and 'bail_lock_' in m1.geom(i).name for i in range(m1.ngeom))==16)
out=dict(layout=ID,pass_=all(checks.values()),checks=checks,rows=rows,added_mass_per_bowl_kg=.04,scope='Geometric preservation and modeled lock solids only. 150N/15Nm mechanical key/lock proof remains a hardware design obligation.')
(O/'bail_geometry_validation_v7.json').write_text(json.dumps(out,indent=2));print('BAIL_GEOMETRY',out['pass_'],checks);assert out['pass_']
