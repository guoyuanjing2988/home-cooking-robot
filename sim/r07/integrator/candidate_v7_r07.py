import subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;ID=sys.argv[1];start=time.monotonic();screen=H/'results/layouts'/f'{ID}_screen_v7.json'
if not screen.exists():subprocess.run([sys.executable,'-B','screen_v7_r07.py',ID],cwd=H,timeout=120,check=True)
for index in sys.argv[2:]:
 remaining=1040-(time.monotonic()-start)
 if remaining<40:break
 subprocess.run([sys.executable,'-B','static_v7_r07.py',ID,index,str(int(index)+1),str(remaining),'96','96'],cwd=H,timeout=remaining+10,check=True)
