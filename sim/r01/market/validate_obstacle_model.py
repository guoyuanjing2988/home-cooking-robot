"""Compile the explicit obstacle subset;never execute or modify the checker."""
from pathlib import Path
import json,time,hashlib
import mujoco
ROOT=Path(__file__).resolve().parent
start=time.monotonic()
path=ROOT/'models'/'installation_obstacles.xml'
m=mujoco.MjModel.from_xml_path(str(path))
names=[m.geom(i).name for i in range(m.ngeom)]
assert {'upper_cabinet_closed_proxy','cabinet_door_full_sweep_proxy','faucet_vertical_cylinder_proxy','faucet_swivel_envelope_cylinder_proxy'}.issubset(names)
assert m.njnt==0 and m.ngeom==7
out={'date':'2026-10-07','mujoco_version':mujoco.__version__,'compiled':True,'geometry_count':m.ngeom,
 'geometry_names':names,'model_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
 'scope':'Cabinet/faucet proxy subset only;no robot,IK,collision gap acceptance or task checker evaluated',
 'elapsed_s':round(time.monotonic()-start,4)}
(ROOT/'results'/'obstacle_model_validation.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
