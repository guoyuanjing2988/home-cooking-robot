"""Copy only the immutable L101 cell, complete bowl, and selected vendor assets."""
from pathlib import Path
import json, shutil, hashlib, xml.etree.ElementTree as E
H=Path(__file__).resolve().parent
ROOT=H.parents[2]; OLD=ROOT/'sim/r07/integrator'
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8')
def main():
 for d in ['assets','models','results','renders','audit']: (H/d).mkdir(parents=True,exist_ok=True)
 tree=E.parse(OLD/'models/L101_reach_R_v7.xml')
 manifest=[]
 for mesh in tree.findall('.//mesh'):
  src=Path(mesh.get('file'));dst=H/'assets'/src.name;shutil.copy2(src,dst);mesh.set('file',str(dst))
  manifest.append(dict(source=str(src.relative_to(ROOT)),copy=str(dst.relative_to(H)),sha256=hashlib.sha256(dst.read_bytes()).hexdigest()))
 E.indent(tree);tree.write(H/'models/base.xml',encoding='unicode')
 full=E.parse(OLD/'models/L101_stroke_1.xml')
 library=E.Element('library')
 for b in full.find('worldbody').findall('body'):
  if b.get('name','').startswith('stored_bowl_') or b.get('name')=='linear_peeler_cutter': library.append(b)
 E.indent(library);E.ElementTree(library).write(H/'assets/components.xml',encoding='unicode')
 for src,dst in [('results/layouts/L101.json','assets/layout.json'),('results/layouts/L101_envelope.json','assets/envelope.json'),('results/layouts/L101_idle.json','assets/park.json')]:shutil.copy2(OLD/src,H/dst)
 process=json.loads((OLD/'results/layouts/L101_process_v7.json').read_text())
 write(H/'assets/process_contract.json',{k:process[k] for k in ('finished_products','force_models','acceptance','source_catalog')})
 admission=json.loads((OLD/'results/fresh_admission.json').read_text())
 seeds=[po['q'] for row in admission['rows'] for po in row.get('reference',{}).get('poses',[]) if row['ok']]
 write(H/'assets/seeds.json',seeds)
 for name in ['distance.py','point_bound.py','bounded.py']:shutil.copy2(OLD/name,H/name)
 for src in (OLD/'sources/menagerie/universal_robots_ur5e').glob('*'):
  if src.is_file():shutil.copy2(src,H/'assets'/src.name)
 write(H/'results/provenance.json',dict(assets=manifest,base_source='sim/r07/integrator/models/L101_reach_R_v7.xml',reference_sha256=hashlib.sha256((ROOT/'sim/r05/integrator/reference.py').read_bytes()).hexdigest(),notes='Only two complete base meshes are referenced by the compiled L101 model; OEM arm collision primitives/inertias retained byte for byte. No old solver stack copied.'))
 print('compact bootstrap complete')
if __name__=='__main__':main()
