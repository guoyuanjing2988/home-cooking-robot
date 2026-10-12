"""Preserve delivery six; compare six front-feed and container layouts."""
import json,copy,zipfile,hashlib,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';hist=H/'history/v6';hist.mkdir(exist_ok=True)
post=H.parents[2]/'posts/r07'
if not (post/'integrator_v6.md').exists():shutil.copy2(post/'integrator.md',post/'integrator_v6.md')
archive=hist/'delivery_snapshot.zip'
if not archive.exists():
 files=list(H.glob('*.py'))+list(O.glob('*.*'))+list((H/'renders').glob('*.*'))
 for folder in ('static_v6/L84','motion_v6/L84','connections_v6/L84'):files+=list((O/folder).rglob('*'))
 files+=list((O/'layouts').glob('L84*'))+list((H/'models').glob('L84*'))
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for f in dict.fromkeys(files):
   if f.is_file():z.write(f,f.relative_to(H))
 (hist/'sha256.txt').write_text(hashlib.sha256(archive.read_bytes()).hexdigest())
for f in H.glob('*v6*r07.py'):
 target=H/f.name.replace('v6','v7')
 if not target.exists():target.write_text(f.read_text(encoding='utf-8').replace('v6','v7'),encoding='utf-8')
base=json.loads((O/'layouts/L84.json').read_text());p0=json.loads((O/'layouts/L84_process_v4.json').read_text())
# Front edge of the unchanged 295mm-deep reservation remains on the counter.
# Bowl docks move individually; bowl acquisition is not a processor target.
variants=[(.1575,0,.180,0),(.1475,.012,.130,0),(.1475,-.035,.130,-.050),(.1575,.012,.115,-.050),(.1475,.012,.115,-.085),(.1475,-.035,.115,-.085)]
for k,(sy,dx,by,lower_tcp) in enumerate(variants):
 ID='L'+str(90+k);c=copy.deepcopy(base);p=copy.deepcopy(p0)
 c.update(id=ID,orientation='R07_v7_'+ID,round_v7=True,reason=f'Full processor front placement Y={sy}; X shift={dx}; output dock Y={by}; feed grasp offset={lower_tcp}. Closed doors during operation.',front_feed_study=True)
 c['station_frames']['slicer']['new_center']=[.46+dx,sy,0];c['station_overrides'].setdefault('slicer',{})['new_center']=[.46+dx,sy,0]
 output_delta={}
 for name,f in c['station_frames'].items():
  if name.startswith('output_'):
   output_delta[name]=[0,by-f['new_center'][1],0];f['new_center'][1]=by
   c['station_overrides'].setdefault(name,{})['new_center']=f['new_center']
 segments=[s for ph in p['phases'] for s in ph['segments']]
 for i,sg in enumerate(segments):
  h0=sg['poses'][0]['R'];delta=None
  # Genuine feed/withdraw: move the complete approach with the processor.
  if i in (12,13,30,31):delta=[dx,sy-.225,0]
  if h0['held']=='carried_bowl':
   product='carrot' if i<16 else 'potato' if i<35 else 'greens' if i<47 else 'tomato'
   delta=output_delta.get('output_'+product)
   # Existing config uses bok_choy rather than greens in some revisions.
   if delta is None and product=='greens':delta=output_delta.get('output_bok_choy',[0,by-.452,0])
  if i in (33,43):delta=[-.07,-.10,0] if k>=2 else [0,-.07,0]
  if delta:
   for hands in sg['poses']:
    for h in hands.values():h['pos']=[a+d for a,d in zip(h['pos'],delta)]
  if i in (12,30) and lower_tcp:
   from scipy.spatial.transform import Rotation
   import numpy as np
   # Shift grasp down while preserving the original full food world pose.
   # Food transform depends on the approach frame, so use the actual helper.
   # Applied later by layout_feed_frames_v7, after runtime can load the layout.
   sg['v7_grasp_offset_z']=lower_tcp
 c['headroom_design']=dict(full_processor_dimensions_m=[.395,.295,.395],processor_top_m=1.245,cabinet_front_y_m=.23,cabinet_bottom_z_m=1.35,processor_front_y_m=sy-.1475,output_dock_y_m=by,feed_tcp_offset_z_m=lower_tcp,assumption='Front strip available in operation only; full body/wrist checked by IK. No claim from TCP position alone.')
 for suffix,data in [('',c),('_process',json.loads((O/'layouts/L84_process.json').read_text())),('_process_v4',p),('_process_v7',p)]:
  (O/'layouts'/f'{ID}{suffix}.json').write_text(json.dumps(data,indent=2))
 for suffix in ('_envelope','_park_full'):
  d=json.loads((O/'layouts'/f'L84{suffix}.json').read_text());d['config']=c
  if suffix=='_park_full':d.update(pass_=False,warm_start_only=True)
  (O/'layouts'/f'{ID}{suffix}.json').write_text(json.dumps(d,indent=2))
print('V7 preserved v6; L90-L95 created; no new evidence credited')
