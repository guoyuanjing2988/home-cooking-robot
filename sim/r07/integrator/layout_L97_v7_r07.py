"""Clear the two measured bail/peeler-drive intersections by station translation."""
import json,copy
from pathlib import Path
O=Path(__file__).resolve().parent/'results/layouts'
def read(n):return json.loads((O/n).read_text())
c=read('L96.json');p=read('L96_process_v4.json');delta=-.020
for group in ('station_frames','station_overrides'):c[group]['peel']['new_center'][1]+=delta
for sg in (s for ph in p['phases'] for s in ph['segments']):
 if sg['station']=='peel':
  for hands in sg['poses']:
   for h in hands.values():h['pos'][1]+=delta
c.update(id='L97',orientation='R07_v7_L97',reason='L96 packing probe found two6.155mm bail/peeler-drive overlaps. Translate complete peeler and its targets20mm forward; full guards/actuator/tool retained. Front-strip feed and75degree full bails retained.')
for suffix,data in [('',c),('_process_v4',p),('_process_v7',p),('_process',read('L96_process.json'))]:(O/f'L97{suffix}.json').write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=read('L96'+suffix+'.json');d['config']=c
 if suffix=='_park_full':d.update(pass_=False,warm_start_only=True)
 (O/f'L97{suffix}.json').write_text(json.dumps(d,indent=2))
print('L97 full peeler moved20mm forward')
