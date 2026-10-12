from pathlib import Path
import sys,json,hashlib
H=Path(__file__).resolve().parent;I=H.parent/'integrator';O=H/'audit_v2';O.mkdir(exist_ok=True)
sys.path.insert(0,str(I/'vendor/pdfdeps'));import fitz
rows=[]
for name,pages in [('ur5e_datasheet.pdf',[0]),('xarm_user_manual_v2.pdf',[16,236])]:
    src=I/'sources'/name;doc=fitz.open(src)
    for i in pages:
        path=O/f'{Path(name).stem}_p{i+1}.png';doc[i].get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(path);rows.append(dict(source=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),page=i+1,text=doc[i].get_text(),image=str(path)))
(O/'datasheet_extracts.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print([(x['source'],x['page']) for x in rows])
