from pathlib import Path
import subprocess,sys
H=Path(__file__).resolve().parent
for i in (52,42,49,1,2,5,7,11,20,39,50,51,56,57):
 if (H/f'results_v6/internal_{i}.json').exists():continue
 subprocess.run([sys.executable,'-B',str(H/'v6_internal.py'),str(i)],check=True,timeout=240)
