import sys,urllib.request,hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent;D=H/'sources/faucet_wall_v3';D.mkdir(exist_ok=True)
url='https://www.larochenigeria.com/shop/img/product-docs/Product35617_20220616.pdf';p=D/'grohe_13303000_datasheet.pdf'
if not p.exists():p.write_bytes(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=35).read())
sys.path.insert(0,str(H/'vendor/pypdfium_v3'));import pypdfium2 as pdfium
doc=pdfium.PdfDocument(str(p))
for i in range(len(doc)):
 page=doc[i];page.render(scale=1.8).to_pil().save(D/f'page_{i}.png')
(D/'source.json').write_text(json.dumps(dict(url=url,author='GROHE manufacturer-generated datasheet, distributor-hosted copy',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pages=len(doc)),indent=2));print('SOURCE',len(doc),p.stat().st_size,flush=True)
