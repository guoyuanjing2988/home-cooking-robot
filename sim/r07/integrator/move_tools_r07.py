import json,copy
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';p=json.loads((O/'process_v3.json').read_text())
if not p.get('r07_docks_forward'):
 for g in p['installed_geometry']:
  if g['name'].startswith('dock_'):g['pos'][1]-=.35
 for ph in p['phases']:
  for sg in ph['segments']:
   docking=sg['label'].startswith(('acquire_','return_','pick_peeler'))
   if docking:
    for hands in sg['poses']:
     for h in hands.values():
      if h['held'] in ('peeler','wash_pad','eye_core_spoon'):h['pos'][1]-=.35
 p['r07_docks_forward']=dict(translation_m=[0,-.35,0],reason='Full-size tool docks and released tools clear folded helper; front-counter tools remain environmental clutter when idle.')
 (O/'process_v3.json').write_text(json.dumps(p,indent=2))
print('full-size docks shifted forward350mm, no force/product/gate changes')
