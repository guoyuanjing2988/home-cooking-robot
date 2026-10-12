"""Foreground serial CPU renders; each process<180s/1900MiB."""
import sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent
blender='C:/Program Files/Blender Foundation/Blender 4.5/blender.exe'
for name in sys.argv[1:]:
 cmd=[sys.executable,'-B',str(H/'bounded.py'),'180','render_'+name,blender,'--background','--factory-startup','-t','2','--python',str(H/'blender_render.py'),'--',str(H/'renders'/(name+'.scene.json'))]
 r=subprocess.run(cmd,timeout=200,capture_output=True,text=True)
 print(name,r.returncode,r.stdout[-350:],r.stderr[-350:],flush=True)
 if r.returncode:raise RuntimeError('Render failed '+name)
