"""Compare every full stored-bowl solid before/after articulation."""
import sys,subprocess,json,hashlib
from pathlib import Path
import numpy as np,mujoco
H=Path(__file__).resolve().parent;O=H/'results'
if len(sys.argv)>1 and sys.argv[1]=='dump':
 import os
 os.environ['R07_LAYOUT']=sys.argv[2]
 import runtime_v6_r07 as v
 (H/'models'/f'{v.ID}_bail_validation.xml').write_text(v.scene(0).xml);raise SystemExit(0)
for label in ('L81','L82'):subprocess.run([sys.executable,'-B',__file__,'dump',label],check=True,timeout=30)
models=[mujoco.MjModel.from_xml_path(str(H/'models'/f'{label}_bail_validation.xml')) for label in ('L81','L82')];data=[mujoco.MjData(m) for m in models]
for m,d in zip(models,data):mujoco.mj_forward(m,d)
rows=[];checks={};m0,m1=models;d0,d1=data
for i in range(m0.ngeom):
 name=m0.geom(i).name
 if not name.startswith('stored_bowl_'):continue
 j=m1.geom(name).id;dimensions=bool(m0.geom_type[i]==m1.geom_type[j] and np.max(abs(m0.geom_size[i]-m1.geom_size[j]))<1e-10);stationary=any(x in name for x in ('bowl_outer','collar','contents'));error=max(float(np.max(abs(d0.geom_xpos[i]-d1.geom_xpos[j]))),float(np.max(abs(d0.geom_xmat[i]-d1.geom_xmat[j]))));rows.append(dict(part=name,full_type_and_size_preserved=dimensions,bowl_or_collar_world_pose_preserved=(error<1e-6) if stationary else None,world_matrix_error=error))
checks['all_original_solid_dimensions_preserved']=all(x['full_type_and_size_preserved'] for x in rows)
checks['upright_bowls_collars_support_poses_unchanged']=all(x['bowl_or_collar_world_pose_preserved'] is not False for x in rows)
checks['sixteen_full_new_pin_and_stop_geoms']=sum('stored_bowl_' in m1.geom(i).name and 'bail_lock_' in m1.geom(i).name for i in range(m1.ngeom))==16
out=dict(layout='L82',pass_=all(checks.values()),checks=checks,rows=rows,added_mass_per_bowl_kg=.04,key_force_capacity_N=150,key_moment_capacity_Nm=15,scope='Rigid locked60degree handle adaptation. No source part resized/removed. Pins/stops and added mass explicit. Not a fabricated supplier certification or a completed robot path.')
(O/'bail_geometry_validation_v6.json').write_text(json.dumps(out,indent=2));print('BAIL_GEOMETRY',out['pass_'],checks);assert out['pass_']
