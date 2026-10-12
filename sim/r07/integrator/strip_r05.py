from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
H=Path(__file__).resolve().parent;R=H/'renders';rows=json.loads((R/'manifest.json').read_text())['frames'];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
strip=Image.new('RGB',(1920,2145),'#111827');draw=ImageDraw.Draw(strip);draw.text((12,12),'R05 reference meal / 24 diagnostic frames / NOT AN EXECUTED OR CONNECTED MEAL',font=font,fill='white')
for i,row in enumerate(rows):
 im=Image.open(R/row['file']).convert('RGB').resize((480,320));x=(i%4)*480;y=(i//4)*350+45;strip.paste(im,(x,y));draw.text((x+6,y+324),f"{i+1:02}  {row['stroke'][:48]}",font=font,fill='white')
strip.save(R/'full_meal_frame_strip.png');print('24-frame strip saved')
