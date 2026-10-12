import json,runpy
import r07_runtime as rt
H=rt.H;O=rt.O
runpy.run_path(str(H/'sequence_r07.py'))
runpy.run_path(str(H/'persistent_scene.py'))
model=json.loads((O/'persistent_model.json').read_text())
model['schema']='r07.single-conserved-scene'
model['missing']+=['BFP610 exact removable bowl, lid, pusher, disc and unplugging interface; R211 proxy is not a substitute']
for name in ('slicer_lid','slicer_pusher'):
 model['bindings'][name]['geometry_complete']=False
 model['bindings'][name]['obsolete_R211_placeholder']=True
model['executable']=False
rt.write('persistent_model.json',model)
print('state chain errors',len(json.loads((O/'state_sequence.json').read_text())['discrete_state_chain_errors']))
