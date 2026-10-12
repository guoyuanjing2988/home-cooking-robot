"""Design gallery: every finger design holding the tomato and the carrot (dyn.py PREVIEW
stills at the first grasp state). python gallery.py out.png"""
import sys,os,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont
OUT=sys.argv[1];TMP='renders/r12/_g';os.makedirs(TMP,exist_ok=True)
DES=[('','原装短指'),('L','加长平直垫'),('V','横向V槽'),('K','金字塔窝'),('R','鳍条 Fin Ray'),('D','双区指（推荐）')]
ROWS=[('AW','250,-40,.30','番茄'),('AS','250,-30,.30','胡萝卜')]
tiles={}
for P,view,_ in ROWS:
 for k,_ in DES:
  f=f'{TMP}/{P}_{k or "stock"}.png';env=dict(os.environ,PV_VIEWS=view,PREVIEW=f,NOSLIP='10')
  if k:env['FINGER']=k
  else:env.pop('FINGER',None)
  subprocess.run([sys.executable,'dyn.py',P,'0.3','40'],env=env,stdout=subprocess.DEVNULL,check=True)
  tiles[(P,k)]=Image.open(f).resize((400,300))
F='C:/Windows/Fonts/msyh.ttc';f1=ImageFont.truetype(F,24);f2=ImageFont.truetype(F,20)
img=Image.new('RGB',(90+400*len(DES),50+300*len(ROWS)),(255,255,255));dr=ImageDraw.Draw(img)
for j,(k,name) in enumerate(DES):dr.text((90+400*j+12,10),name,font=f1,fill=(20,20,20))
for i,(P,_,lab) in enumerate(ROWS):
 dr.text((14,50+300*i+130),lab,font=f1,fill=(20,20,20))
 for j,(k,_) in enumerate(DES):img.paste(tiles[(P,k)],(90+400*j,50+300*i))
img.save(OUT);print(OUT)
