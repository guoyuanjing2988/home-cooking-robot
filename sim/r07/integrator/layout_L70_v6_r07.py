"""Select the clearer peeler/tool layout, retaining successful wash changes."""
import json,copy
from pathlib import Path
O=Path(__file__).resolve().parent/'results/layouts'
def read(n):return json.loads((O/n).read_text())
c=read('L65.json');p=read('L65_process_v4.json');new=read('L69_process_v4.json');good=read('L61_process_v4.json')
items=[s for ph in p['phases'] for s in ph['segments']];ni=[s for ph in new['phases'] for s in ph['segments']];gi=[s for ph in good['phases'] for s in ph['segments']]
for i in (10,15,28,34,46,53,33,39,43):items[i].update(copy.deepcopy(ni[i]))
for i in (35,47,52,54):items[i].update(copy.deepcopy(gi[i]))
c.update(id='L70',orientation='R07_v6_L70',reason='Select the L65 rear horizontal full tool docks and rear horizontal full peeler lid: L67-L69 forward/vertical variants lost peeler and cleaning reach without a connected fold. Retain96-start successful direct washes/lid withdrawal, alternate full bowl grasps and forward/up colander drain trials. No geometry shrinking or gate changes.')
for suffix,data in [('',c),('_process_v4',p),('_process_v6',p),('_process',read('L65_process.json'))]:(O/('L70'+suffix+'.json')).write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=read('L65'+suffix+'.json');d['config']=c
 if suffix=='_park_full':d.update(pass_=False,warm_start_only=True)
 (O/('L70'+suffix+'.json')).write_text(json.dumps(d,indent=2))
print('L70 hybrid uses the stronger verified peeler layout')
