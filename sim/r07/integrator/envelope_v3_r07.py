"""Reuse only same OEM arm and mounting rotation; translation cannot change gravity torque."""
import os,sys,json,copy
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v2_r07 as v
from pathlib import Path
donors=[]
for p in (v.O/'layouts').glob('L??_envelope.json'):
 d=json.loads(p.read_text());donors.append((p,d))
out={'config':v.cfg,'envelope_Nm':{},'witnesses':{},'reuse_proof':[],'method':'Exact arm/model/rotation match to retained numerical OEM rated-payload witnesses; translation leaves gravity Jacobian torque unchanged. Not continuous torque ratings.'}
for i,side in enumerate(('R','L')):
 angle=v.cfg['mount_deg' if i==0 else 'helper_mount_deg'];arm=v.cfg['arms'][i];found=None
 for path,d in donors:
  dc=d['config']
  for j,oldside in enumerate(('R','L')):
   if dc.get('arms',['UR5e','xArm6'])[j]==arm and abs(dc['mount_deg' if j==0 else 'helper_mount_deg']-angle)<1e-10:
    found=(path,d,oldside);break
  if found:break
 if not found:
  print('No exact envelope donor; compute actual mounted envelope',v.ID,arm,angle,flush=True)
  import runpy
  write=v.rt.write;v.rt.write=lambda n,o:write('layouts/'+v.ID+'_envelope.json',o) if n=='torque_envelope.json' else write(n,o)
  runpy.run_path(str(v.H/'envelope_r07.py'));sys.exit(0)
 path,d,oldside=found
 for key,value in d['envelope_Nm'].items():
  if key.startswith(oldside+'_'):
   new=side+key[1:];out['envelope_Nm'][new]=value;out['witnesses'][new]=d.get('witnesses',{}).get(key)
 out['reuse_proof'].append(dict(side=side,arm=arm,mount_deg=angle,source=str(path.relative_to(v.H)),source_side=oldside,reason='Unscaled same OEM inertia/geometry, same mount rotation; only global translation or side-name prefix changes.5kg replacesEOAT; original OEM allowedCoM bound retained.'))
(v.O/'layouts'/f'{v.ID}_envelope.json').write_text(json.dumps(out,indent=2));print('Exact mounted envelopes',v.ID,out['reuse_proof'])
