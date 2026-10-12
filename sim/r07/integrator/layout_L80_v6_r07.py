"""Complete lid dock relocation and low-spout clearance variant."""
import json,copy
from pathlib import Path
O=Path(__file__).resolve().parent/'results/layouts'
def read(n):return json.loads((O/n).read_text())
c=read('L74.json');p=read('L74_process_v4.json');b=read('L74_process.json')
c.update(id='L80',orientation='R07_v6_L80',reason='Full secondary lid/slot stow at far-left counter edge; full low wall spout35mm left, wash fixture/targets follow outlet. Open lid stays present, never deleted.',lid_slot_override=[-1.83,.40,.86])
c['lid_storage']['center_m']=[-1.83,.40,1.15]
c['replacement_faucet']['wall_connection_m'][0]-=.035;c['replacement_faucet']['wash_reference_pos_m'][0]-=.035;c['station_frames']['wash']['new_center'][0]-=.035
for sg in (s for ph in p['phases'] for s in ph['segments']):
 if sg['station']=='sink' and sg['poses'][0]['R']['held']=='root_food':
  for hands in sg['poses']:
   for h in hands.values():h['pos'][0]-=.035
for suffix,data in [('',c),('_process',b),('_process_v4',p),('_process_v6',p)]: (O/f'L80{suffix}.json').write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=read('L74'+suffix+'.json');d['config']=c;(O/f'L80{suffix}.json').write_text(json.dumps(d,indent=2))
print('L80 created, no evidence credited')
