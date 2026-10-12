"""Give working strokes their own checked engagement/disengagement motions.
The free connection starts/ends clear; no working permission leaks into it.
"""
import json,copy,math
from pathlib import Path
O=Path(__file__).resolve().parent/'results/layouts'
def read(n):return json.loads((O/n).read_text())
c=read('L70.json');p=read('L70_process_v4.json');changes=[]
for i,sg in enumerate(s for ph in p['phases'] for s in ph['segments']):
 if sg.get('action')!='process':continue
 first,last=sg['poses'][0],sg['poses'][-1]
 if not any(contact.get('kind')=='working_stroke' for hands in (first,last) for h in hands.values() for contact in h.get('contacts',[])):continue
 approach=copy.deepcopy(first);retreat=copy.deepcopy(last)
 for hands in (approach,retreat):
  for h in hands.values():
   a=h['approach'];norm=math.sqrt(sum(x*x for x in a));h['pos']=[v-.025*x/norm for v,x in zip(h['pos'],a)]
 sg['poses']=[approach]+sg['poses']+[retreat];sg['checked_working_engagement']=dict(approach_m=.025,retreat_m=.025,own_working_contact_only=True,free_connections_strip_all_working_permissions=True,force_models_unchanged=True);changes.append(i)
c.update(id='L71',orientation='R07_v6_L71',reason='L70 hardware with25mm straight engagement/disengagement inside each working stroke. Non-working connections begin/end at actual clear poses and receive no working-contact permission. Full geometry, forces and original gates retained.')
for suffix,data in [('',c),('_process_v4',p),('_process_v6',p),('_process',read('L70_process.json'))]:(O/('L71'+suffix+'.json')).write_text(json.dumps(data,indent=2))
for suffix in ('_envelope','_park_full'):
 d=read('L70'+suffix+'.json');d['config']=c
 if suffix=='_park_full':d.update(pass_=False,warm_start_only=True)
 (O/('L71'+suffix+'.json')).write_text(json.dumps(d,indent=2))
(O/'L71_working_engagement_changes.json').write_text(json.dumps(dict(indices=changes,rule_change=False,point_step_mm=4),indent=2))
print('L71 working approach/retreat indices',changes)
