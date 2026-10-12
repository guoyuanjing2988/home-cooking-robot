import sys,urllib.request,json
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H/'vendor/pdfdeps'));import fitz
url='https://www.universal-robots.com/manuals/EN/PDF/SW5_21/user-manual-UR5e-PDF_online/710-965-00_UR5e_User_Manual_en_Global.pdf'
p=H/'sources/UR5e_user_manual_SW5_21.pdf'
if not p.exists():
    with urllib.request.urlopen(url,timeout=45) as r:p.write_bytes(r.read())
doc=fitz.open(p);out=[]
for i,page in enumerate(doc):
    txt=page.get_text()
    if any(x in txt.lower() for x in ('friction clutch','mounting of the control','brakes engaged','robot arm can be mounted','power loss')):
        out.append(dict(pdf_page=i+1,text=txt));print('page',i+1,txt[:3500])
(H/'audit/UR5e_primary_extract.json').write_text(json.dumps(dict(source=url,pages=out),indent=2),encoding='utf-8')
