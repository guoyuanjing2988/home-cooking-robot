from pathlib import Path
import sys,urllib.request
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'vendor/pdfdeps'))
import fitz
p=HERE/'sources/xarm_user_manual_v2.pdf'
if not p.exists():urllib.request.urlretrieve('https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf',p)
d=fitz.open(p)
for i in (16,236):
    print(i,d[i].get_text())
    d[i].get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(HERE/f'audit/oem_page_{i}.png')
