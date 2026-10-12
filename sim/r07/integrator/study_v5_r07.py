import sys,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parent;start=time.monotonic()
for ID in sys.argv[1:]:
 for task in ('envelope','map','certificates'):
  remain=1060-(time.monotonic()-start)
  if remain<30:raise SystemExit('Resumable study chunk ended')
  subprocess.run([sys.executable,'-B','study_task_v5_r07.py',ID,task],cwd=H,check=True,timeout=remain)
