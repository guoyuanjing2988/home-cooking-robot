"""Correct engagement direction: full food lifts off horizontal work faces."""
import json,copy
from pathlib import Path
O=Path(__file__).resolve().parent/'results/layouts'
def read(n):return json.loads((O/n).read_text())
c=read('L71.json');p=read('L71_process_v4.json');changes=[]
for i,sg in enumerate(s for ph in p['phases'] for s in ph['segments']):
 if i not in (2,8,17,26,56):continue
 for end,inside in ((0,1),(-1,-2)):
  sg['poses'][end]=copy.deepcopy(sg['poses'][inside])
  for h in sg['poses'][end].values():h['pos'][2]+=.025
 sg['checked_working_engagement'].update(axis=[0,0,1],axis_basis='Outward normal of the named horizontal brush/work face; corrected from tool approach axis.');changes.append(i)
c.update(id='L73',orientation='R07_v7_L73',reason='Persistent connection evidence found residual brush contact after sideways retreat. Lift full food/pad25mm along horizontal work-face normal for wash and secondary wipe. L71 full geometry and gates unchanged.')
for suffix,data in [('',c),('_process_v4',p),('_process_v7',p),('_process',read('L71_process.json'))]:(O/('L73'+suffix+'.json')).write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=read('L71'+suffix+'.json');d['config']=c
 if suffix=='_park_full':d.update(pass_=False,warm_start_only=True)
 (O/('L73'+suffix+'.json')).write_text(json.dumps(d,indent=2))
(O/'L73_working_engagement_changes.json').write_text(json.dumps(dict(indices=changes,rule_change=False,reason='Actual L71 connection1 goal had3mm brush penetration; lift normal instead of sideways.',evidence='results/connections_v7/L71/1.json'),indent=2))
print('L73',changes)
