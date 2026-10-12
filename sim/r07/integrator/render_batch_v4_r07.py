import runpy
from pathlib import Path
H=Path(__file__).resolve().parent
s=(H/'render_batch_v2_r07.py').read_text().replace('manifest_v2.json','manifest_v4.json').replace('24 FRAMES FROM CHECKED LOCAL PATH:','24 CHECKED SIMULATION FRAMES:').replace('Full populated template | <=4 mm replay, loads and grip checked | ISOLATED PATH, NOT A MEAL','Full template | <=4 mm replay, loads and grip checked | ISOLATED PATH, NOT A MEAL').replace("source=(H/'blender_render.py').read_text();", "source=(H/'blender_render.py').read_text().replace('Blue: R arm / Orange: L arm','Blue: single UR5e / red: stove exclusion');")
p=H/'render_batch_v4_impl_r07.py';p.write_text(s);runpy.run_path(str(p))
