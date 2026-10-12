"""One-time clean R09 bootstrap. Reads R08, writes only beside this file."""
from pathlib import Path
import xml.etree.ElementTree as E
import copy,hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
t=E.parse(ROOT/'sim/r08/integrator/models/base.xml');w=t.find('worldbody')
mount=copy.deepcopy(t.find(".//body[@name='R_mount']"));mount.set('quat','1 0 0 0');mount.set('pos','0 0 .85')
# Complete OEM arm, fingers and adapter retained. Wall hardware is replaced.
old=w.find("body[@name='wall_anchor']")
for g in old.findall('.//geom'):
 if g.get('name','').startswith('appliance_power_'):w.append(copy.deepcopy(g))
w.remove(old)
cart=E.SubElement(w,'body',name='rail_structure') # immutable reference root ABI
E.SubElement(cart,'joint',name='R_carriage_x',type='slide',axis='1 0 0',range='-1.48 2.46')
E.SubElement(cart,'joint',name='base_y',type='slide',axis='0 1 0',range='-.60 -.30')
E.SubElement(cart,'joint',name='base_yaw',type='hinge',axis='0 0 1',range='-3.14159265359 3.14159265359')
def box(n,p,s,m,c='.2 .3 .4 1'):
 return E.SubElement(cart,'geom',name=n,type='box',pos=p,size=s,mass=str(m),rgba=c,contype='2',conaffinity='3',margin='.01')
box('R_cart_chassis','0 0 .165','.30 .25 .075',18)
box('R_cart_ballast','0 0 .255','.27 .22 .025',46.6,'.25 .25 .28 1')
box('R_cart_controller','0 0 .419','.2375 .2115 .134',13.6)
box('R_cart_electrics','0 -.16 .595','.20 .07 .042',5)
box('R_cart_mast','0 0 .695','.06 .06 .142',6)
# Four corner tyres; front pair differential drive, rear swivel casters.
for x in [-.24,.24]:
 for y in [-.20,.20]:
  E.SubElement(cart,'geom',name=f'R_cart_wheel_{x}_{y}',type='cylinder',pos=f'{x} {y} .0825',size='.0825 .025',quat='.707106781187 .707106781187 0 0',mass='2.5',rgba='.08 .08 .08 1',contype='2',conaffinity='3',margin='.01')
cart.append(mount)
for mesh in t.findall('.//mesh'):mesh.set('file',str(H/'assets'/Path(mesh.get('file')).name))
E.indent(t);t.write(H/'models/base.xml',encoding='unicode')
manifest={str(p.relative_to(H)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (H/'assets').glob('*') if p.is_file()}
(H/'results/provenance.json').write_text(json.dumps(dict(reference_sha256=hashlib.sha256((ROOT/'sim/r05/integrator/reference.py').read_bytes()).hexdigest(),copied_assets=manifest,source='R08 I09 full arm geometry and stations; wall rail removed; upright mobile mount',root_abi='rail_structure name retained solely for unchanged R05 classification'),indent=2))
print('R09 mobile base created')
