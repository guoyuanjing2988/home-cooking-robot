import json,copy
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';p=json.loads((O/'process_v3.json').read_text())
if not p.get('r07_appliance_replacement'):
 p['inherited_R05_appliance']=p['appliance']
 p['appliance']=dict(model='Breville BFP610 Kitchen Wizz9',source='https://www.breville.com/en-nz/product/bfp610',manual_source='https://assets.breville.com/BFP610/BFP610_ANZ_WEB_IB_A23_LR.pdf',published_WDH_m=[.395,.197,.23],model_external_envelope_WDH_m=[.395,.295,.395],height_policy='Use largest published dimension395mm as upright height; extra98mm depth. Matched orientation/bowl/pusher drawing unavailable: this is a conservative external candidate, not an admitted OEM internal interface.',disc_setting_mm=5.,guarding='OEM bowl/lid/large-pusher interlocks and induction-motor braking; stopped/unplugged disc removal before batch unloading',force_status='All inherited sourced process bounds retained; BFP610 feed force and actual pusher load unqualified. No blade-force rating is inferred from motor power.',mass_kg=None,power_W=None,admitted=False)
 for ph in p['phases']:
  for sg in ph['segments']:
   if sg['station']=='slicer':
    for hands in sg['poses']:
     for h in hands.values():h['pos'][2]-=.115
    sg['r07_interface_status']='External-envelope approach lowered115mm (510mm to395mm machine height). Feed aperture/pusher/lid/batch bowl internal geometry not source matched; this cannot qualify cutting or unloading.'
 p['r07_appliance_replacement']=True
def identity(h):
 typ=h['held'];prod=h['product']
 return 'food:'+prod if typ=='root_food' else 'bowl_'+prod if typ=='carried_bowl' else {'food_cup':'cup','cut_cassette':'cassette'}.get(typ,typ)
ledger=[]
for ph in p['phases']:
 for sg in ph['segments']:
  for pi,hands in enumerate(sg['poses']):
   for side,h in hands.items():
    for c in h.get('contacts',[]):
     workfaces={'clamped_food','wash_food','root_brush_work_face','secondary_work_face','greens_crease_land','peel_food_land'}
     work=c['face'] in workfaces and (h['held'] in ('peeler','wash_pad','eye_core_spoon') or h['held']=='root_food' and sg.get('action')=='process')
     c['kind']='working_stroke' if work else 'grasp_release_support'
     c['object_id']=identity(h);ledger.append(dict(phase=ph['id'],stroke=sg['label'],pose=pi,side=side,**c))
(O/'process_v3.json').write_text(json.dumps(p,indent=2))
(O/'intended_contacts.json').write_text(json.dumps(dict(rows=ledger,wall_faces=[dict(bracket=f'r07_wall_bracket_{i}',face='rear +Y') for i in range(4)],contact_policy='Explicit kind and persistent object/support identity; work excluded from free transit'),indent=2))
print('BFP610 external candidate;115mm lower approach;235 explicit persistent identities')
