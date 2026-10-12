import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
p=json.loads((ROOT/'sim/r02/tools/results/process_v2.json').read_text(encoding='utf-8'))
t=json.loads((ROOT/'sim/r02/transport/results/transport_options.json').read_text(encoding='utf-8'))
for key in ['checker_contract','contact_mapping','force_models','counter_layout','powered_appliances','moving_geometry_states','collision_geometry_source']:
 print(key, json.dumps(p[key],ensure_ascii=True)[:12500])
for q in p['phases']:
 print(q['id'],q['name'], 'old',q['old_phase_ids'], 'segments',len(q['segments']))
 for s in q['segments']:
  print(' ',s['label'],s['station'],len(s['poses']), [(side,h['held'],h['pos'],h['intended']) for side,h in s['poses'][0].items()])
print('INSTANCE_COUNT',len(p['checker_instances']))
print('GEOMETRY',json.dumps(t['geometry']))
for o in t['options']: print('OPTION',json.dumps(o)[:3000])
