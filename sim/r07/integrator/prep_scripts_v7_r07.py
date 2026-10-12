"""Generate R07-owned delivery adapters; never alter copied R05 modules."""
from pathlib import Path
H=Path(__file__).resolve().parent
s=(H/'fold_alternatives_v4_r07.py').read_text().replace('runtime_v4_r07','runtime_v7_r07').replace('motion_v4_r07','motion_v7_r07').replace('static_v4','static_v7').replace("f'{ID}_fold_alternatives.json'","f'{ID}_fold_alternatives_v7.json'")
s=s.replace('import numpy as np,mujoco','from idle_model_v7_r07 import completed_scene\noriginal_scene=v.scene\ninside=False\ndef populated_scene(i):\n global inside\n if i!=58 or inside:return original_scene(i)\n inside=True\n try:return completed_scene()[0]\n finally:inside=False\nv.scene=populated_scene\nimport numpy as np,mujoco')
s=s.replace("source=(H/'park_single_v4_r07.py').read_text();", "source=(H/'park_single_v4_r07.py').read_text().replace('runtime_v4_r07','runtime_v7_r07');")
s=s.replace("sys.argv=['run_v4_r07.py','idle_snapshot_v2_r07.py',ID];runpy.run_path(str(H/'run_v4_r07.py'),run_name='__main__')", "row['requires_final_snapshot_refresh']=True")
(H/'fold_alternatives_v7_r07.py').write_text(s)
print('Generated alternative-park adapter')
