"""Keep the moving principal gripper visible; change only camera, never q/solids."""
import json,runpy
from pathlib import Path
H=Path(__file__).resolve().parent;R=H/'renders';file=R/'manifest_v3.json';manifest=json.loads(file.read_text())
(H/'audit/frame_camera_before_v3.json').write_text(json.dumps(manifest,indent=2))
for view in manifest['views']:
 if not view['name'].startswith('frame_'):continue
 old=R/view['scene'];data=json.loads(old.read_text());data['focus']=[-1.15,.20,1.08];data['camera_scale']=2.7
 name=view['name']+'_detail';scene='v3/'+name+'.scene.json';(R/scene).write_text(json.dumps(data))
 view['scene']=scene;view['image']='v3/'+name+'.png'
manifest['camera_refinement']='Frame camera shifted left and widened after visual inspection so the principal gripper is not cropped. Saved q, complete solids, source path and admission are unchanged. Earlier framing files remain historical only.'
file.write_text(json.dumps(manifest,indent=2));runpy.run_path(str(H/'render_batch_v3_r07.py'))
