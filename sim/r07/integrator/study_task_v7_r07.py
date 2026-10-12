import os,sys,runpy
from pathlib import Path
ID,task=sys.argv[1:3];os.environ['R07_LAYOUT']=ID;H=Path(__file__).resolve().parent
import runtime_v7_r07 as v
if task=='envelope':
 if (v.O/'layouts'/f'{ID}_envelope.json').exists():raise SystemExit()
 original=v.rt.write;v.rt.write=lambda n,o:original('layouts/'+ID+'_envelope.json',o) if n=='torque_envelope.json' else original(n,o)
 source=(H/'envelope_r07.py').read_text().replace("for side in ('R','L'):","for side in rt.s.model.SIDES:").replace('tr,meta=rt.s.model.build(c)','from runtime_v7_r07 import full_transport\ntr,meta=full_transport(c)')
 exec(compile(source,'mounted_envelope_v7','exec'))
elif task=='map':
 sys.argv=['reach_v7_r07.py',ID,'R'];runpy.run_path(str(H/'reach_v7_r07.py'),run_name='__main__')
else:
 for script in ('fixed_hardware_v2_r07.py','target_certificate_v2_r07.py'):
  source=(H/script).read_text().replace('runtime_v2_r07','runtime_v7_r07').replace('range(105)','range(59)').replace('scene(104)','scene(58)')
  sys.argv=[script,ID];exec(compile(source,'v7_'+script,'exec'),{'__name__':'__main__','__file__':str(H/script)})
