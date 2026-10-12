"""Preserve v5 and start six scoped, full-geometry layout studies."""
import json,copy,shutil,zipfile,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';hist=H/'history/v5';hist.mkdir(exist_ok=True)
post=H.parents[2]/'posts/r07';saved=post/'integrator_v5.md'
if not saved.exists():shutil.copy2(post/'integrator.md',saved)
archive=hist/'delivery_snapshot.zip'
if not archive.exists():
 files=list(H.glob('*.py'))+list(O.glob('*.*'))+list((H/'renders').glob('*.*'))
 for directory in (O/'static_v5/L73',O/'motion_v5/L73',O/'connections_v5/L73',H/'renders/v5_L73'):files+=list(directory.rglob('*'))
 files+=list((O/'layouts').glob('L73*'))+list((H/'models').glob('L73*'))+[H/'models/persistent_meal.xml']
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for f in dict.fromkeys(files):
   if f.is_file():z.write(f,f.relative_to(H))
 (hist/'sha256.txt').write_text(hashlib.sha256(archive.read_bytes()).hexdigest())
for f in H.glob('*v5*r07.py'):
 target=H/f.name.replace('v5','v6')
 if not target.exists():target.write_text(f.read_text(encoding='utf-8').replace('v5','v6'),encoding='utf-8')
base=json.loads((O/'layouts/L73.json').read_text());process=json.loads((O/'layouts/L73_process_v4.json').read_text());baseline=json.loads((O/'layouts/L73_process.json').read_text())
variants=[('L74',{},'Corrected closed-door motion scope; identical full appliances and mounts.'),('L75',{'slicer':[.012,0,0]},'Full BFP reservation and insertion targets move12mm right, retaining stove gap.'),('L76',{'slicer':[0,.020,0]},'Full processor moves20mm rearward to open parked wrist corridor.'),('L77',{'slicer':[.012,.015,0]},'Combined12mm right/15mm rearward processor move; full solids retained.'),('L78',{'slicer':[.012,.015,0],'secondary':[-.035,-.030,0]},'Move complete secondary station35mm left/30mm forward to separate processor and guard approaches.'),('L79',{'slicer':[.012,.015,0],'secondary':[-.035,-.030,0],'dock_wash_pad':[0,-.020,0],'dock_eye_core_spoon':[0,-.020,0]},'Add20mm forward full tool-dock relocation, away from carriage and shoulder.')]
for ID,moves,reason in variants:
 c=copy.deepcopy(base);p=copy.deepcopy(process);b=copy.deepcopy(baseline);c.update(id=ID,orientation='R07_v6_'+ID,reason=reason,round_v6=True,motion_door_scope='closed_leaves_and_cabinet_bodies_only',idle_door_scope='full_sweeps_10mm',door_open_pause_sensors=True,layout_moves_from_L73=moves)
 for name,delta in moves.items():
  f=c['station_frames'][name];f['new_center']=[a+d for a,d in zip(f['new_center'],delta)];c['station_overrides'].setdefault(name,{})['new_center']=f['new_center']
 for sg in (sg for ph in p['phases'] for sg in ph['segments']):
  station=sg['station'];h=sg['poses'][0]['R'];group='slicer' if station=='slicer' else 'secondary' if station=='secondary' else 'dock_'+h['held'] if station=='dock' else None
  if group in moves:
   for hands in sg['poses']:
    for h in hands.values():h['pos']=[a+d for a,d in zip(h['pos'],moves[group])]
 for suffix,data in [('',c),('_process',b),('_process_v4',p),('_process_v6',p)]: (O/'layouts'/f'{ID}{suffix}.json').write_text(json.dumps(data,indent=2))
 for suffix in ('_envelope','_park_full'):
  d=json.loads((O/'layouts'/f'L73{suffix}.json').read_text());d['config']=c
  if suffix=='_park_full':d.update(pass_=False,warm_start_only=True)
  (O/'layouts'/f'{ID}{suffix}.json').write_text(json.dumps(d,indent=2))
print('V6: archived v5; six layout configurations created; no evidence credited yet')
