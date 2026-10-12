"""Sequential bounded CPU Blender invocations, one render worker."""
import sys,os,subprocess,time,json
from pathlib import Path
H=Path(__file__).resolve().parent
blender='C:/Program Files/Blender Foundation/Blender 4.5/blender.exe'
os.environ['BLENDER_USER_CONFIG']=str(H/'temp/blender_config')
os.environ['BLENDER_USER_SCRIPTS']=str(H/'temp/blender_scripts')
os.environ['TEMP']=os.environ['TMP']=str(H/'temp')
for key in ('BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS'):Path(os.environ[key]).mkdir(parents=True,exist_ok=True)
for name in sys.argv[1:]:
    cmd=[sys.executable,'-B',str(H/'bounded.py'),'180','render_'+name,blender,'--background','--factory-startup','-t','2','--python',str(H/'blender_render.py'),'--',str(H/'renders'/(name+'.scene.json'))]
    result=subprocess.run(cmd,timeout=200)
    if result.returncode:raise RuntimeError(name)
