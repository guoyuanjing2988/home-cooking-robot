from v2_common import *
R05=I.parents[1]/'r05/integrator';old=mujoco.MjModel.from_xml_path(str(R05/'models/witnesses/Q01__water_on.xml'));ch=v.scene(0);new=ch.m
names={mujoco.mj_id2name(old,mujoco.mjtObj.mjOBJ_GEOM,i):i for i in range(old.ngeom)};rows=[]
for j,n in enumerate(ch.gnames):
    if n not in names or not n.startswith(('north_wall','upper_cabinet','counter','sink','sensor_faucet','stove','floor','south_wall')):continue
    i=names[n];keys=('geom_type','geom_size','geom_pos','geom_quat');rows.append(dict(name=n,unchanged=all(np.array_equal(getattr(old,k)[i],getattr(new,k)[j]) for k in keys),original_size=old.geom_size[i].tolist(),size=new.geom_size[j].tolist()))
dump('fixed_geometry.json',dict(parts=rows,all_unchanged=all(x['unchanged'] for x in rows),scope='Original fixed kitchen geometry compared to R05 compiled scene; declared rail and appliance replacements assessed separately.'))
print('FIXED',len(rows),[x for x in rows if not x['unchanged']])
