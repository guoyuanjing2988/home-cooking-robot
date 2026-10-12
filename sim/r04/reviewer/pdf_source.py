"""Read-only public OEM PDF visual/text inspection, reviewer-only outputs."""
from pathlib import Path
import sys,json
H=Path(__file__).resolve().parent;I=H.parent/'integrator';A=H/'audit'
sys.path.insert(0,str(I/'vendor/pdfdeps'))
import fitz
doc=fitz.open(I/'sources/jaka_manual_v11.pdf')
for index in [64,65,66]:
 page=doc[index];page.get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(A/('jaka_manual_'+str(index)+'.png'))
 (A/('jaka_manual_'+str(index)+'.txt')).write_text(page.get_text(),encoding='utf-8')
brake=[]
for index,page in enumerate(doc):
 txt=page.get_text()
 if any(k in txt for k in ['断电','抱闸','制动器']):brake.append(dict(page_index=index,paragraphs=[line for line in txt.splitlines() if any(k in line for k in ['断电','抱闸','制动器'])]))
(A/'jaka_brake_text.json').write_text(json.dumps(brake,indent=2,ensure_ascii=False),encoding='utf-8')
print('JAKA pages rendered',len(doc),'pages;',len(brake),'brake-text pages')
