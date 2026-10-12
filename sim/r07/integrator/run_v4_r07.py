"""Use existing bounded numerical tools with the new process runtime."""
import sys,os,runpy
from pathlib import Path
H=Path(__file__).resolve().parent
script,ID,*args=sys.argv[1:];os.environ['R07_LAYOUT']=ID
import runtime_v4_r07
# Existing scripts importing runtime_v2 receive its explicitly patched state.
sys.argv=[script,ID,*args]
if script in ('park_v2_r07.py','idle_v2_r07.py','fold_continuation_v3_r07.py','fold_continuation_v4_r07.py','fold_map_v3_r07.py','passing_v3_r07.py','fixed_hardware_v2_r07.py'):
 import runtime_v2_r07 as v
 original=v.scene
 v.scene=lambda i:original(len(v.items)-1 if i==104 else i)
runpy.run_path(str(H/script),run_name='__main__')
