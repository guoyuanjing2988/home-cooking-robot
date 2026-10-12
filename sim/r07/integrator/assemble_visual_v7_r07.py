"""Assemble completed motion evidence and export honest simulation render scenes."""
import sys,subprocess,time,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];began=time.monotonic()
manifest=H/'renders/manifest_v7.json';before={}
if manifest.exists():
 for view in json.loads(manifest.read_text())['views']:
  scene=H/'renders'/view['scene']
  if scene.exists() and view['scene'].startswith('v7_'+ID+'/'):before[view['scene']]=hashlib.sha256(scene.read_bytes()).hexdigest()
for args in [['preflight_v7_r07.py'],['prepare_delivery_v7_r07.py',ID],['measure_export_v7_r07.py',ID]]:
 subprocess.run([sys.executable,'-B']+args,cwd=H,timeout=max(1,1040-(time.monotonic()-began)),check=True)
if before:
 comparison=[]
 for view in json.loads(manifest.read_text())['views']:
  scene=H/'renders'/view['scene'];same=before.get(view['scene'])==hashlib.sha256(scene.read_bytes()).hexdigest();comparison.append(dict(scene=view['scene'],unchanged=same,image_already_rendered=(H/'renders'/view['image']).exists()))
 result=dict(layout=ID,pass_=all(r['unchanged'] or not r['image_already_rendered'] for r in comparison),rows=comparison,scope='Already rendered views may be reused only when the complete exported scene bytes remain identical after final assembly.')
 (H/'results/render_scene_reexport_v7.json').write_text(json.dumps(result,indent=2));assert result['pass_'], 'Changed scenes require fresh images before delivery'
print('ASSEMBLED_AND_EXPORTED',ID,round(time.monotonic()-began,2),flush=True)
