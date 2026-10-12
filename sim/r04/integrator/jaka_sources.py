import urllib.request,json,sys,xml.etree.ElementTree as E
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H/'vendor/pdfdeps'));import fitz
manual=H/'sources/jaka_manual_v11.pdf'
url='https://www.jaka.com/profile/upload/2025/11/25/20251125172527A001.pdf'
with urllib.request.urlopen(url,timeout=35) as r:manual.write_bytes(r.read(40*1024*1024))
d=fitz.open(manual)
for i in [8,64,65,66]:
 print('PAGE',i+1,d[i].get_text()[:1700],flush=True);d[i].get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(H/f'audit/jaka_page_{i+1}.png')
commit='f6b28c6be93f289f101c6cc3907caf7804fb1a47';base='https://raw.githubusercontent.com/JAKARobotics/jaka_ros2/'+commit+'/src/jaka_description/'
folder=H/'sources/jaka_description';folder.mkdir(exist_ok=True)
for arm in ['jaka_zu5','jaka_zu7']:
 rel='urdf/'+arm+'.urdf'
 with urllib.request.urlopen(base+rel,timeout=30) as r:data=r.read()
 p=folder/rel;p.parent.mkdir(exist_ok=True);p.write_bytes(data);u=E.fromstring(data)
 for mesh in u.findall('.//mesh'):
  fn=mesh.get('filename');rel=fn.split('jaka_description/')[-1];target=folder/rel
  if target.exists():continue
  target.parent.mkdir(parents=True,exist_ok=True)
  with urllib.request.urlopen(base+rel,timeout=30) as r:target.write_bytes(r.read(30*1024*1024))
 print('model',arm,'downloaded',flush=True)
print('source files',len(list(folder.rglob('*'))),flush=True)
