from pathlib import Path
import shutil,hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
for n in ('upstream_r04','upstream_r05','models','results','audit','renders','sources'):(H/n).mkdir(exist_ok=True)
rows=[]
for rnd in ('r04','r05'):
 src=ROOT/'sim'/rnd/'integrator'
 for name in ('reference.py','final_check.py','solver.py','model.py','oem_model.py','distance.py','planner.py','motion_check.py','envelope.py','envelope_repair.py','planner_r05.py','point_bound.py','policy_r05.py','motion_r05.py'):
  p=src/name
  if not p.exists():continue
  dst=H/('upstream_'+rnd)/name;shutil.copy2(p,dst)
  rows.append(dict(source=str(p.relative_to(ROOT)),copy=str(dst.relative_to(H)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),identical=p.read_bytes()==dst.read_bytes()))
src=ROOT/'sim/r05/integrator/sources/menagerie/universal_robots_ur5e'
shutil.copytree(src,H/'sources/ur5e',dirs_exist_ok=True)
for p in src.rglob('*'):
 if p.is_file():rows.append(dict(source=str(p.relative_to(ROOT)),copy=str((H/'sources/ur5e'/p.relative_to(src)).relative_to(H)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),identical=p.read_bytes()==(H/'sources/ur5e'/p.relative_to(src)).read_bytes()))
for n in ('stations.json','events_A.json','state_ledger_A.json','food_catalog.json','products.json','initial_joints.json','bom.csv'):
 p=ROOT/'sim/r06/stations/results'/n;shutil.copy2(p,H/'sources'/n)
 rows.append(dict(source=str(p.relative_to(ROOT)),copy='sources/'+n,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),identical=True))
(H/'audit/provenance.json').write_text(json.dumps(rows,indent=2))
print('Immutable copies',len(rows),'bytes',sum(p.stat().st_size for p in H.rglob('*') if p.is_file()))
