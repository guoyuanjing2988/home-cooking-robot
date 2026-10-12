import json, pathlib
h=pathlib.Path('sim/r06/stations/results')
s=json.loads((h/'stations.json').read_text())
print('KEYS',list(s))
for k in s:
 if k in ('bodies','food_catalog','foods','objects'):continue
 v=s[k]
 print(k, str(v)[:3000])
print('BODIES',len(s['bodies']))
for b in s['bodies']:
 print(b['id'],b.get('parent'),b.get('pose'),b.get('joint'),len(b['geometry']))
e=json.loads((h/'events_A.json').read_text())
print('EVENT_TYPE',type(e).__name__)
print(str(e)[:6500])
