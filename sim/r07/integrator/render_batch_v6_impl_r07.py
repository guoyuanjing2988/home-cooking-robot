"""Sequential CPU rendering of new v2 scenes; no stale v1 image reuse."""
import json,subprocess,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H/'renders';manifest=json.loads((R/'manifest_v6.json').read_text())
# Derivative render-only wrapper corrects the old hard-coded two-rail caption;
# the90 archived R05 modules, geometry and admission checker are untouched.
source=(H/'blender_render.py').read_text().replace('Blue: R arm / Orange: L arm','Blue: single UR5e / red: stove exclusion');source=source.replace("{data['config']['count']} arms, 2 rails", "{data['config']['count']} arms, {data['config'].get('lane_count',2)} rail(s)");(H/'blender_render_v2_r07.py').write_text(source)
for view in manifest['views']:
 target=R/view['image']
 if not target.exists():
  result=subprocess.run(['C:/Program Files/Blender Foundation/Blender 4.5/blender.exe','--background','--factory-startup','--threads','1','--python',str(H/'blender_render_v2_r07.py'),'--',str(R/view['scene'])],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=150)
  if result.returncode or not target.exists():raise RuntimeError(result.stdout[-4000:])
 print('RENDER',view['name'],target.stat().st_size,flush=True)
 shutil.copy2(target,R/(view['name']+'.png'))
strip=Image.new('RGB',(1500,880),'#f0f2f4');draw=ImageDraw.Draw(strip);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
frame=json.loads((H/'results/frame_manifest.json').read_text());draw.text((20,12),'24 CHECKED SIMULATION FRAMES: '+frame['stroke'],font=font,fill='#172536');draw.text((20,42),'Full template | <=4 mm replay, loads and grip checked | ISOLATED PATH, NOT A MEAL',font=small,fill='#172536')
for i in range(24):
 image=Image.open(R/f'frame_{i:02}.png').convert('RGB');image.thumbnail((250,170));x=i%6*250;y=80+i//6*195;strip.paste(image,(x,y));draw.text((x+8,y+171),f'{i+1:02} | accepted local path sample',font=small,fill='#172536')
strip.save(R/'executed_local_strip.png');shutil.copy2(R/'manifest_v6.json',R/'manifest.json');print('STRIP complete',flush=True)
