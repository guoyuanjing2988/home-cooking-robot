import json,shutil,hashlib,zipfile,copy,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';hist=H/'history/v4';hist.mkdir(exist_ok=True)
archive=hist/'delivery_snapshot.zip'
if not archive.exists():
 files=list(H.glob('*.py'))+list(O.glob('*.*'))+list((H/'renders').glob('*.*'))
 for directory in (O/'static_v4/L53',O/'motion_v4/L53',O/'final_static_v4/L53',H/'renders/v4_L53'):
  files+=list(directory.rglob('*'))
 files+=list((O/'layouts').glob('L53*'))+list((H/'models').glob('L53*'))
 files +=[H/'models/persistent_meal.xml']
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in dict.fromkeys(files):
   if p.is_file():z.write(p,p.relative_to(H))
 (hist/'sha256.txt').write_text(hashlib.sha256(archive.read_bytes()).hexdigest())
base=json.loads((O/'layouts/L53.json').read_text())
variants=[
 ('L54',{}, {},'Full guarded linear peeler replaces forbidden Rotato; same rail/mount and full kitchen, current160deg elbow range; baseline transfer topology.'),
 ('L55',{'height':1.150,'rail_centres_z':[1.265,1.29],'power_z':1.175}, {'peel':{'new_center':[-1.27,.145,-.147]}},'Lower shoulder and complete carriage20mm; lower guarded peel approach, increased cabinet margin.'),
 ('L56',{'mount_deg':100,'front_mount_y':.48}, {'raw':{'new_center':[-.925,.145,0]},'peel':{'new_center':[-1.29,.125,-.147]}},'Tilt100deg with20mm forward stand-off; full raw and peeling assemblies move left/forward.'),
 ('L57',{'mount_deg':80,'height':1.155,'rail_centres_z':[1.265,1.29]}, {'secondary':{'new_center':[.02,.125,0]},'peel':{'new_center':[-1.29,.125,-.147]}},'Tilt80deg lower shoulder; front secondary approach corridor, retained full guards.'),
 ('L58',{'front_mount_y':.47,'height':1.155,'rail_centres_z':[1.270,1.29],'chain_y':.3875}, {'raw':{'new_center':[-.89,.125,0]},'slicer':{'new_center':[.47,.225,0]}},'30mm forward mount, full chain15mm rearward, processor45mm right/20mm rear; target front-transfer reserve.'),
 ('L59',{'height':1.160,'rail_centres_z':[1.275,1.29],'chain_y':.3825}, {'raw':{'new_center':[-.92,.125,0]},'peel':{'new_center':[-1.30,.125,-.147]},'secondary':{'new_center':[.04,.115,0]},'slicer':{'new_center':[.46,.225,0]}},'Lower mount15mm, full chain10mm rearward; shifted full stations and vertical deliver approaches selected for carriage-first staging.'),
]
for ID,delta,frames,reason in variants:
 c=copy.deepcopy(base);c.update(delta);c.update(id=ID,orientation='R07_v5_'+ID,reason=reason,peeler_model='custom_guarded_linear',round_v5=True,ur5e_elbow_limit_deg=160,principal_model_revision='Full archived source solids/inertias retained conservatively; current OEM160deg elbow bound and151mm footprint cover added',guarded_peeler_drive='Actuonix P16-200-256-12-P')
 c['station_overrides'].update(frames)
 (O/'layouts'/f'{ID}.json').write_text(json.dumps(c,indent=2))
 subprocess.run([sys.executable,'-B','setup_stations_v2_r07.py',ID],cwd=H,check=True,timeout=30)
 subprocess.run([sys.executable,'-B','process_v4_r07.py',ID],cwd=H,check=True,timeout=30)
 c=json.loads((O/'layouts'/f'{ID}.json').read_text());p=json.loads((O/'layouts'/f'{ID}_process_v4.json').read_text());items=[s for ph in p['phases'] for s in ph['segments']]
 for i in (3,4,18,19):
  sg=items[i];x,y,z=c['station_frames']['peel']['new_center'];prod=sg['poses'][0]['R']['product'];sg.update(label=('linear_peeler_load_' if i in (3,18) else 'linear_peeler_unload_')+prod,station='appliance_approach',interface_qualified=True,qualification_scope='Executable custom fixture geometry, not physical qualification; internal food transformation declared by2026-10-09 decision')
  h=copy.deepcopy(sg['poses'][0]['R']);h.update(pos=[x,y,1.025],approach=[0,0,-1],jaw_axis=[0,1,0],contacts=[])
  sg['poses']=[{'R':dict(h,pos=[x,y,1.065])},{'R':h}]
  if i in (4,19):sg['poses'].reverse()
 for i in (15,34,46,53):
  for hands in items[i]['poses']:
   h=hands['R'];h.update(approach=[0,0,-1],jaw_axis=[0,1,0],object_rotation_deg=[0,0,0])
 for i in (35,37,38,39,41,43,47):
  if ID in ('L55','L57','L59'):
   for hands in items[i]['poses']:
    for h in hands.values():h['pos'][0]-=.07;h['pos'][1]-=.045
 p['night_process_change'].update(appliance='Custom guarded linear peeling station; P16-200-256-12-P',quality_credit='declared assumption per2026-10-09; no simulated quality proof',essential_unqualified=[])
 (O/'layouts'/f'{ID}_process_v4.json').write_text(json.dumps(p,indent=2));(O/'layouts'/f'{ID}_process_v5.json').write_text(json.dumps(p,indent=2))
 park=json.loads((O/'layouts/L53_park_full.json').read_text());park.update(config=c,pass_=False,warm_start_only=True);(O/'layouts'/f'{ID}_park_full.json').write_text(json.dumps(park,indent=2))
print('V5 archived v4 and created6 full geometry studies')
