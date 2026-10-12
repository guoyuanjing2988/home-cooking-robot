import sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent
for sec,name,script,args in [(120,'doors_final','doors_r05.py',[]),(180,'export_final_hinges','renders_r05.py',[])]:
 code=subprocess.call([sys.executable,'-B',str(H/'bounded.py'),str(sec),name,sys.executable,'-B',str(H/script)]+args)
 if code:raise SystemExit(code)
raise SystemExit(subprocess.call([sys.executable,'-B','-u',str(H/'render_chunk.py'),'overview','parked_doors_open']+[f'frame_{i:02}' for i in range(1,7)]))
