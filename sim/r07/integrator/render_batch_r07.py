"""Sequential CPU Blender renders within one bounded foreground worker tree."""
import json,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parent;R=H/'renders'
manifest=json.loads((R/'manifest.json').read_text())
for v in manifest['views']:
 target=R/v['image']
 if target.exists():continue
 cmd=['C:/Program Files/Blender Foundation/Blender 4.5/blender.exe','--background','--factory-startup','--threads','1','--python',str(H/'blender_render.py'),'--',str(R/v['scene'])]
 result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=150)
 if result.returncode or not target.exists():raise RuntimeError(result.stdout[-4000:])
 print(v['name'],'rendered',target.stat().st_size,flush=True)
from PIL import Image,ImageDraw,ImageFont
strip=Image.new('RGB',(1500,880),'#f0f2f4');draw=ImageDraw.Draw(strip)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
draw.text((20,12),'24 FRAMES FROM CHECKED LOCAL EMPTY-CARRIAGE SHUTTLE',font=font,fill='#172536')
draw.text((20,42),'25 mm out and back | loose food, bowls and stored tools absent | NO MEAL EXECUTION',font=small,fill='#172536')
for i in range(24):
 im=Image.open(R/f'frame_{i:02d}.png').convert('RGB');im.thumbnail((250,170))
 x=i%6*250;y=80+i//6*195;strip.paste(im,(x,y));draw.text((x+8,y+171),f'{i+1:02d}  |  accepted path sample',font=small,fill='#172536')
strip.save(R/'executed_local_strip.png')
print('24-frame strip written',flush=True)
