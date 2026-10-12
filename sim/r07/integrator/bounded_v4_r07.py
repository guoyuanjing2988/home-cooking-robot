"""R07 cache settings around the byte-identical copied R05 timeout runner."""
import os,sys,runpy
from pathlib import Path
H=Path(__file__).resolve().parent
for key,folder in [('MPLCONFIGDIR','matplotlib'),('TEMP','temp'),('TMP','temp'),('XDG_CACHE_HOME','xdg'),('BLENDER_USER_CONFIG','blender')]:
 directory=H/'audit/runtime_cache'/folder;directory.mkdir(parents=True,exist_ok=True);os.environ[key]=str(directory)
sys.argv[0]=str(H/'bounded.py');runpy.run_path(str(H/'bounded.py'),run_name='__main__')
