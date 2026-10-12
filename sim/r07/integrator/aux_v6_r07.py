import os,sys,time,json,runpy
from pathlib import Path
ID=sys.argv[1];os.environ['R07_LAYOUT']=ID;H=Path(__file__).resolve().parent;O=H/'results';start=time.monotonic()
import runtime_v6_r07 as v
from idle_model_v6_r07 import completed_scene
original=v.scene
v.scene=lambda i:completed_scene()[0] if i==58 else original(i)
# completed_scene uses World.build -> v.scene, so keep the original scene
# constructor available and guard recursive calls.
inside=False
def scene(i):
 global inside
 if i!=58 or inside:return original(i)
 inside=True
 try:return completed_scene()[0]
 finally:inside=False
v.scene=scene
def execute(script,replace=()):
 source=(H/script).read_text().replace('runtime_v4_r07','runtime_v6_r07').replace('runtime_v2_r07','runtime_v6_r07').replace('static_v4','static_v6').replace('motion_v2_r07','motion_v6_r07').replace('motion_v4_r07','motion_v6_r07').replace('scene(104)','scene(58)')
 for a,b in replace:source=source.replace(a,b)
 sys.argv=[script,ID];exec(compile(source,'v6_'+script,'exec'),{'__name__':'__main__','__file__':str(H/script)})
if '--reuse-park' not in sys.argv:
 os.environ['R07_PARK_SECONDS']='230';execute('park_single_v4_r07.py')
execute('idle_v2_r07.py',[("if '--snapshot-only' in sys.argv:","if True:"),("if g.get('name','').startswith('idle_full_sweep_cover_'):world.remove(g)","if g.get('name','').startswith(('idle_full_sweep_cover_','r07_closed_door_')):world.remove(g)")])
