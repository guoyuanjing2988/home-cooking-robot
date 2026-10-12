import sys,subprocess,time,json
from pathlib import Path
from bounded import rss,tree
H=Path(__file__).resolve().parent;start=time.monotonic()
for name in sys.argv[1:]:
 log=(H/'audit'/('render_'+name+'.log')).open('w',encoding='utf-8');cmd=['C:/Program Files/Blender Foundation/Blender 4.5/blender.exe','--background','--factory-startup','--threads','1','--python',str(H/'blender_render.py'),'--',str(H/'renders'/(name+'.scene.json'))];p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);peak=0;beg=time.monotonic()
 while p.poll() is None:
  peak=max(peak,sum(rss(pid) for pid in tree(p.pid)))
  if peak>1900 or time.monotonic()-beg>150 or time.monotonic()-start>1050:p.kill();break
  time.sleep(.25)
 p.wait(timeout=10);log.close();record=dict(name=name,elapsed_s=time.monotonic()-beg,peak_MiB=peak,exit_code=p.returncode,cpu_only=True,timeout_s=150);(H/'audit'/('render_'+name+'.resource.json')).write_text(json.dumps(record,indent=2));print(name,p.returncode,round(record['elapsed_s'],1),flush=True)
print('RENDER_CHUNK',round(time.monotonic()-start,1))
