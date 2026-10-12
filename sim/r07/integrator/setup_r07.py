import json,hashlib,copy
from pathlib import Path
H=Path(__file__).resolve().parent
P=json.loads((H/'results/inherited_process_v3.json').read_text())
working={'clamped_food','wash_food','root_brush_work_face','secondary_work_face','greens_crease_land'}
ledger=[]
for ph in P['phases']:
 for sg in ph['segments']:
  for pi,hands in enumerate(sg['poses']):
   for side,h in hands.items():
    for c in h.get('contacts',[]):
     iswork=c['face'] in working or c['face']=='peel_food_land' and h['held']=='wash_pad'
     c.update(kind='working_stroke' if iswork else 'grasp_release_support',object_id=h['held']+':'+h['product'],support_id=c['face'])
     ledger.append(dict(phase=ph['id'],stroke=sg['label'],pose=pi,side=side,**c))
(H/'results/process_v3.json').write_text(json.dumps(P,indent=2))
(H/'results/intended_contacts.json').write_text(json.dumps(ledger,indent=2))
src=H.parents[2]/'r05/integrator'
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (H/'upstream').glob('*.py')}
(H/'audit/copied_code_hashes.json').write_text(json.dumps(manifest,indent=2))
print('contact declarations',len(ledger),'immutable Python modules',len(manifest))
