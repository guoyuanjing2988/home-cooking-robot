"""CPU rendering in a new directory; old frames never reused as new evidence."""
import runpy,json
from pathlib import Path
H=Path(__file__).resolve().parent
frame=json.loads((H/'results/frame_manifest.json').read_text());caption='Checked deployment PREFIX; full fold failed; NOT A MEAL' if frame.get('prefix_only') else 'Complete isolated template path; <=4 mm, load and grip replay; NOT A MEAL'
s=(H/'render_batch_v2_r07.py').read_text().replace('manifest_v2.json','manifest_v3.json').replace("'24 FRAMES FROM CHECKED LOCAL PATH: '","'24 FRAMES FROM CHECKED SIMULATED MOTION: '").replace('Full populated template | <=4 mm replay, loads and grip checked | ISOLATED PATH, NOT A MEAL',caption).replace('accepted local path sample','checked simulated sample')
p=H/'render_batch_v3_impl_r07.py';p.write_text(s);runpy.run_path(str(p))
