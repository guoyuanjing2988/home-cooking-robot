"""Complete pending policy probes, then use the fourth slot for statics."""
import subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
for script,args in [('wash_alignment_v7_r07.py',['L101']),('door_scope_check_v7_r07.py',['L101']),('progress_v7_r07.py',[]),('static_queue_v7_r07.py',['L101'])]:
 subprocess.run([sys.executable,'-B',script]+args,cwd=H,check=True)
