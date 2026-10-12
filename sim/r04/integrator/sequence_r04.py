"""Review storyboard from actual static renders; never motion footage."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H/'renders';font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
names=['Q01','Q02','Q05','Q10','Q12','potato_wash','potato_peel','potato_cut','Q11','potato_delivery','Q13','Q14','Q15','Q16','Q17','Q19','Q20','Q21','Q24','Q25','Q27'];frames=[]
for i,name in enumerate(names):
 im=Image.open(R/(name+'.png')).convert('RGB').resize((960,640),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(960,678),'#111827');canvas.paste(im,(0,0));ImageDraw.Draw(canvas).text((12,648),f'{i+1:02}/{len(names)} {name} | UNCONNECTED STATIC STORYBOARD | MEAL FAIL',font=font,fill='white');frames.append(canvas)
frames[0].save(R/'full_meal_storyboard.gif',save_all=True,append_images=frames[1:],duration=700,loop=0,optimize=False)
manifest=json.loads((R/'manifest.json').read_text());manifest['full_meal_sequence']=dict(file='full_meal_storyboard.gif',frames=[n+'.png' for n in names],frame_duration_ms=700,status='UNCONNECTED_STATIC_STORYBOARD_NOT_EXECUTION',scope='All four foods, soaking, starch rinsing, draining and cleanup represented. Saved original rendered poses jump between frames; no smooth interpolation or object-teleporting meal is claimed. Conserved model is models/persistent_meal.xml; its unverified staging shown separately.')
(R/'manifest.json').write_text(json.dumps(manifest,indent=2));print('storyboard',len(frames),'frames',len(frames)*.7,'seconds')
