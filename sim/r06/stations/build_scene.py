"""Export only the supplied station JSON to MuJoCo; no IK, motion or simulation."""
import json
from build import HERE, RESULTS, export_station_xml

spec=json.loads((RESULTS/'stations.json').read_text(encoding='utf-8'))
assert spec['schema_version']=='r06.stations.scene.1'
export_station_xml(spec)
import mujoco
model=mujoco.MjModel.from_xml_path(str(RESULTS/'station_primitives.xml'))
data=mujoco.MjData(model)
for name,value in json.loads((RESULTS/'initial_joints.json').read_text(encoding='utf-8')).items():
    idx=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_JOINT,name)
    assert idx>=0,name
    data.qpos[model.jnt_qposadr[idx]]=value
mujoco.mj_forward(model,data)
print(json.dumps(dict(input='results/stations.json',output='results/station_primitives.xml',bodies=model.nbody,geoms=model.ngeom,joints=model.njnt,motion_simulated=False,accepted_paths=0)))
