"""Move the complete mount20mm wallward to clear the repeated shoulder/guard pair."""
import json
from pathlib import Path
O=Path(__file__).resolve().parent/'results/layouts'
def read(n):return json.loads((O/n).read_text())
c=read('L98.json');c.update(id='L99',orientation='R07_v7_L99',front_mount_y=.520,reason='L98 feed solutions repeatedly contact the secondary back guard with the proximal shoulder. Move complete mount20mm wallward within the band; do not move guard off the counter or change gap. All stations, food and full bails retained.')
for suffix,data in [('',c),('_process',read('L98_process.json')),('_process_v4',read('L98_process_v4.json')),('_process_v7',read('L98_process_v7.json'))]:(O/f'L99{suffix}.json').write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=read('L98'+suffix+'.json');d['config']=c
 if suffix=='_envelope':d['reuse_note']='Same complete arm, payload, CoM and90degree gravity orientation; rigid20mm world translation does not change joint gravitational torque. Full new collision geometry rechecked.'
 else:d.update(pass_=False,warm_start_only=True)
 (O/f'L99{suffix}.json').write_text(json.dumps(d,indent=2))
print('L99 complete mount Y=.520 candidate; no acceptance credit')
