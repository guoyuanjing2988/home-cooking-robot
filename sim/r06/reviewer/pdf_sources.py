"""Read-only primary PDF inspection. All downloads/renders are reviewer artifacts."""
import os,sys,json,hashlib,urllib.request
from pathlib import Path
os.environ['PYTHONDONTWRITEBYTECODE']='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path.insert(0,str(ROOT/'sim/r04/integrator/vendor/pdfdeps'))
import fitz
items=[('ur5e','https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf',[0]),('rotato','https://www.starfrit.com/media/pdf/instrbooklet--User-manual-093209002BLCK-en2.pdf',[2,3,4]),('nemco','https://nemco.com/wp-content/uploads/2025/07/55550_Easy_Wedger_4-2012.pdf',[0])]
rows=[]
for name,url,pages in items:
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(request,timeout=30) as response:data=response.read(12*1024**2)
        target=H/'audit'/f'{name}.pdf';target.write_bytes(data);doc=fitz.open(target)
        for n in pages:
            doc[n].get_pixmap(matrix=fitz.Matrix(1.8,1.8)).save(H/'audit'/f'{name}_{n}.png')
        text='\n'.join(page.get_text() for page in doc);(H/'audit'/f'{name}.txt').write_text(text,encoding='utf-8')
        rows.append(dict(name=name,url=url,downloaded=True,sha256=hashlib.sha256(data).hexdigest(),pages=len(doc),rendered_pages=pages));print('PDF',name,len(doc),flush=True)
    except Exception as e:rows.append(dict(name=name,url=url,downloaded=False,error=str(e)));print('PDF ERROR',name,str(e),flush=True)
(H/'audit/pdf_sources.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
