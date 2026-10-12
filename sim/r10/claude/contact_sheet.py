"""Grid of grasp-moment previews for quick visual debugging.
Usage: python contact_sheet.py out.png "<item> KEY=VAL ..." ["..."]"""
import sys,subprocess,os,tempfile
from PIL import Image,ImageDraw,ImageFont
out=sys.argv[1];ims=[];F=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
tmp=tempfile.mkdtemp()
for i,spec in enumerate(sys.argv[2:]):
 p=os.path.join(tmp,f'{i}.png');r=subprocess.run([sys.executable,os.environ.get('BENCH','foodbench.py')]+spec.split()+[f'PREVIEW={p}'],capture_output=True,text=True)
 im=Image.open(p).resize((960,240)) if os.path.exists(p) else Image.new('RGB',(960,240),(80,0,0))
 d=ImageDraw.Draw(im);d.rectangle([0,0,960,20],fill=(255,255,255));d.text((4,0),spec+('' if os.path.exists(p) else '  ERR '+r.stderr.strip().splitlines()[-1][:80] if r.stderr.strip() else '  no preview'),fill=(0,0,0),font=F);ims.append(im)
W=Image.new('RGB',(960,240*len(ims)));[W.paste(im,(0,240*i)) for i,im in enumerate(ims)];W.save(out);print(out)
