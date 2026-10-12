"""Sequential final state/storage preparation inside one bounded CPU slot."""
import sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent
for seconds,name,script,args in [(120,'sequence_final','sequence_r05.py',[]),(120,'persistent_final','persistent_scene.py',[]),(60,'storage_loads','storage_loads_r05.py',[]),(300,'idle_complete_extensions','idle_r05.py',['--repair']),(120,'idle_deployment','idle_path_r05.py',[])]:
 code=subprocess.call([sys.executable,'-B',str(H/'bounded.py'),str(seconds),name,sys.executable,'-B',str(H/script)]+args)
 if code:raise SystemExit(code)
