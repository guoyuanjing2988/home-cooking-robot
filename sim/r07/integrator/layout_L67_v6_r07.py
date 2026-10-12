import json,copy
from pathlib import Path
O=Path(__file__).resolve().parent/'results/layouts';c=json.loads((O/'L66.json').read_text());p=json.loads((O/'L66_process_v6.json').read_text())
c.update(id='L67',orientation='R07_v6_L67',peeler_lid_vertical=True,reason='Actual fold/carriage diagnostics hit the raised dock stands and horizontally stowed peeler lid. Both complete tool docks move100mm forward; same full lid parks vertically about its rear hinge. Horizontal bowl/slicer/colander grasp frames retained from L66; no solids scaled.')
for name in ('dock_wash_pad','dock_eye_core_spoon'):
 c['station_frames'][name]['new_center'][1]-=.10;c['station_overrides'][name]['new_center'][1]-=.10
for ph in p['phases']:
 for sg in ph['segments']:
  if sg['station']=='dock':
   for hands in sg['poses']:
    for h in hands.values():h['pos'][1]-=.10
# Use the already96-start admitted lateral spray targets from L61.
good=json.loads((O/'L61_process_v6.json').read_text());source=[s for ph in good['phases'] for s in ph['segments']];target=[s for ph in p['phases'] for s in ph['segments']]
for i in (35,47):target[i].update(copy.deepcopy(source[i]))
for suffix,data in [('',c),('_process_v4',p),('_process_v6',p),('_process',json.loads((O/'L66_process.json').read_text()))]:(O/('L67'+suffix+'.json')).write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=json.loads((O/('L66'+suffix+'.json')).read_text());d['config']=c
 if suffix=='_park_full':d.update(pass_=False,warm_start_only=True)
 (O/('L67'+suffix+'.json')).write_text(json.dumps(d,indent=2))
print('L67: full docks forward100mm; full360x200x6 lid vertical; no scale changes')
