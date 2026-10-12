"""Fresh layout-specific negative reach evidence; no geometry or gate edits."""
import sys,time,subprocess,json
from pathlib import Path
H=Path(__file__).resolve().parent;start=time.monotonic()
for ID in sys.argv[1:]:
 flag=H/'audit'/f'{ID}_certificates_v6_complete.json'
 if flag.exists():continue
 remain=1040-(time.monotonic()-start)
 if remain<120:break
 p=subprocess.run([sys.executable,'-B','study_task_v6_r07.py',ID,'certificates'],timeout=remain)
 if p.returncode:raise SystemExit(p.returncode)
 flag.write_text(json.dumps(dict(layout=ID,closed_door_scope=True,full_geometry=True,negative_only=True)))
