import json
from pathlib import Path
O=Path(__file__).resolve().parent/'results/layouts'
def read(n):return json.loads((O/n).read_text())
c=read('L100.json');c.update(id='L101',orientation='R07_v7_L101',height=1.1535,reason='L99/L100 wallward mount exposed4.475mm base/beam gap across carriage travel. Raise full beam/guide10mm and lower complete arm base6.5mm; full carriage top remains1.3275m under1.35m cabinet. Retain full45deg bails, side tomato approach and front-strip feed.');c['rail_centres_z'][0]=1.285
for suffix,data in [('',c),('_process',read('L100_process.json')),('_process_v4',read('L100_process_v4.json')),('_process_v7',read('L100_process_v7.json'))]:(O/f'L101{suffix}.json').write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=read('L100'+suffix+'.json');d['config']=c
 if suffix=='_envelope':d['reuse_note']='Same complete arm, payload, CoM and90deg gravity orientation; rigid world translation does not change joint gravity torques. Full rail/mount collision geometry is rechecked.'
 else:d.update(pass_=False,warm_start_only=True)
 (O/f'L101{suffix}.json').write_text(json.dumps(d,indent=2))
print('L101 full beam Z1.285 / base Y.520 Z1.1535; no acceptance credit')
