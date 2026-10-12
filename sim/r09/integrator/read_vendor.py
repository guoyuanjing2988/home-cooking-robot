from pathlib import Path
import urllib.request,sys
H=Path(__file__).resolve().parent
u='https://www.zlingkj.com/Data/zlingkj/upload/file/20240102/ZLLG65ASM500%20V2.0%E5%8D%95%E5%87%BA%E8%BD%B4.pdf'
p=H/'assets/wheel.pdf'
with urllib.request.urlopen(u,timeout=25) as r:p.write_bytes(r.read())
sys.path.insert(0,str(H/'audit/pdfdeps'))
import fitz
d=fitz.open(p);page=d[0];page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(H/'audit/wheel.png')
print(page.get_text()[-1000:])
