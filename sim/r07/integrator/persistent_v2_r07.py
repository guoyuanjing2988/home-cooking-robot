"""Rebuild the conserved proposed ledger and one relocated initial scene."""
import os,sys,json,runpy,xml.etree.ElementTree as E
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v2_r07 as v
import numpy as np,mujoco
v.rt.write('config.json',v.cfg);v.rt.write('process_v3.json',v.P)
runpy.run_path(str(v.H/'sequence_r07.py'))
original=v.s.model.build
def relocated(config=None):
 tree,meta=original(config);v.move_xml(tree.getroot(),False);return tree,meta
v.s.model.build=relocated
runpy.run_path(str(v.H/'persistent_scene.py'))
v.s.model.build=original
file=v.H/'models/persistent_meal.xml';root=E.fromstring(file.read_text());world=root.find('worldbody');model=json.loads((v.O/'persistent_model.json').read_text())
for typ in ('peeler','wash_pad','eye_core_spoon'):
 body=world.find("body[@name='meal_"+typ+"']");frame=v.cfg['station_frames']['dock_'+typ];pos=np.fromstring(body.get('pos'),sep=' ');pos[1]-=.35;pos+=np.array(frame['new_center'])-np.array(frame['old_center']);body.set('pos',v.s.model.fmt(pos));model['bindings'][typ]['initial_world_m']=pos.tolist()
for name in ('slicer_lid','slicer_pusher'):
 body=world.find("body[@name='meal_"+name+"']")
 if body is not None:world.remove(body)
 model['bindings'][name].update(geometry_complete=False,body=None,geometry_basis='Obsolete R211 proxy removed. Exact BFP610 interface absent; full conservative BFP610 exterior remains an obstacle.')
xml=E.tostring(root,encoding='unicode');compiled=mujoco.MjModel.from_xml_string(xml);file.write_text(xml)
model.update(schema='r07.v2.single-conserved-scene',layout=v.ID,compiled_ngeom=compiled.ngeom,compiled_nq=compiled.nq,mocap_bodies=compiled.nmocap,executable=False)
model['missing']+=['BFP610 exact bowl/lid/pusher/disc/unplugging interfaces and continuous unloading route; complete exterior is retained, no fabricated aperture.']
v.rt.write('persistent_model.json',model)
print('PERSISTENT',v.ID,model['ownership_pass'],'executable',model['executable'],flush=True)
