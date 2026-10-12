import os,sys,runpy
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v2_r07 as v
write=v.rt.write
v.rt.write=lambda name,obj: write('layouts/'+v.ID+'_envelope.json',obj) if name=='torque_envelope.json' else write(name,obj)
runpy.run_path(str(v.H/'envelope_r07.py'))
