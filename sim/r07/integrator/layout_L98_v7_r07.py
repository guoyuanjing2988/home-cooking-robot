"""Reject the certified85mm-lowered feed; restore full food/palm headroom."""
import json,copy
from pathlib import Path
O=Path(__file__).resolve().parent/'results/layouts'
def read(n):return json.loads((O/n).read_text())
c=read('L97.json');p=read('L97_process_v4.json');old=read('L84_process_v4.json');items=[s for ph in p['phases'] for s in ph['segments']];prior=[s for ph in old['phases'] for s in ph['segments']];oldcfg=read('L84.json');delta=[a-b for a,b in zip(c['station_frames']['slicer']['new_center'],oldcfg['station_frames']['slicer']['new_center'])]
for i in (12,30):
 items[i].update(copy.deepcopy(prior[i]))
 for hands in items[i]['poses']:
  for h in hands.values():h['pos']=[a+b for a,b in zip(h['pos'],delta)]
 for j,hands in enumerate(items[i+1]['poses']):
  h=hands['R'];source=items[i]['poses'][-1]['R'];h.update(pos=[source['pos'][0],source['pos'][1]-.10*j,source['pos'][2]+.015+.065*j],approach=source['approach'],jaw_axis=source.get('jaw_axis',[1,0,0]),roll_deg=source.get('roll_deg',0))
 items[i]['layout_fix']='Restore full original food/grasp frame at translated front-strip feed;85mm lowering was analytically obstructed by complete appliance reservation.'
c.update(id='L98',orientation='R07_v7_L98',reason='L96/L97 low-grasp certificate exposed palm/appliance intersection. Restore full original food/grasp height at front-strip processor; use upward/forward empty withdrawal. Retain full75degree bails and20mm forward peeler correction.')
c['headroom_design']['feed_tcp_offset_z_m']=0
for suffix,data in [('',c),('_process_v4',p),('_process_v7',p),('_process',read('L97_process.json'))]:(O/f'L98{suffix}.json').write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=read('L97'+suffix+'.json');d['config']=c
 if suffix=='_park_full':d.update(pass_=False,warm_start_only=True)
 (O/f'L98{suffix}.json').write_text(json.dumps(d,indent=2))
print('L98 higher lateral front feed; no dimensions reduced')
