import json,xml.etree.ElementTree as E
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';r=json.loads((O/'research.json').read_text())
for model in ['JAKA_Zu5','JAKA_Zu7']:
 path=O/('arm_screen_'+model+'.json');a=json.loads(path.read_text());name='jaka_zu'+model[-1];u=E.parse(H/'sources/jaka_description/urdf'/(name+'.urdf')).getroot();mass=sum(float(x.get('value')) for x in u.findall('.//link/inertial/mass'));catalog=23 if model.endswith('5') else 22
 a.update(source_arm_mass_kg=mass,catalog_arm_mass_kg=catalog,model_mass_match=False,hardware_admitted_witnesses=0,model_admission='Public source inertias are preserved, not rescaled. Large catalogue/model mass discrepancy prevents hardware admission; numeric torque ratios apply only to that published URDF.')
 for item in a['screen']:item['hardware_admitted_witnesses']=0;item['status']='Raw published-model reference replay only, not hardware admission'
 path.write_text(json.dumps(a,indent=2))
 arm=next(x for x in r['arms'] if x['model']=='JAKA Zu'+model[-1]);arm.update(source_model_mass_kg=mass,catalog_mass_kg=catalog,torque_gate='Computed three constrained DE starts/joint at actual152.114deg with rated mass/75mm offset from OEM V11 pp65-67; source/model mass mismatch prevents hardware admission',numerical_screen='results/'+path.name,screen_solutions=[x['solutions_found'] for x in a['screen']],raw_model_verified_witnesses=sum(x['verified_witnesses'] for x in a['screen']),hardware_admitted_witnesses=0,status='Candidate rejected for unmatched inertia/model revision and incomplete task screen, not missing continuous-output torque')
(O/'research.json').write_text(json.dumps(r,indent=2))
