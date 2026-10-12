"""Preserve the accepted-as-history v2 evidence before the faucet continuation."""
from pathlib import Path
import shutil,json,hashlib,urllib.request
H=Path(__file__).resolve().parent
dst=H/'history/v2';dst.mkdir(parents=True,exist_ok=True)
for directory in ('results','renders','audit'):
 if not (dst/directory).exists():shutil.copytree(H/directory,dst/directory)
src=dst/'adapters';src.mkdir(exist_ok=True)
manifest={}
original=json.loads((H/'audit/copied_code_hashes.json').read_text())
for path in H.glob('*.py'):
 if path.name not in original:
  shutil.copy2(path,src/path.name);manifest[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
(dst/'adapter_hashes.json').write_text(json.dumps(manifest,indent=2))
url='https://www.plumbnation.co.uk/documents/grohe-eurosmart-chrome-kitchen-mixer-tap-33281003-data-sheet.pdf'
(H/'sources/faucet_v3').mkdir(exist_ok=True)
with urllib.request.urlopen(url,timeout=45) as r:(H/'sources/faucet_v3/grohe_33281003.pdf').write_bytes(r.read())
print('Archived v2; faucet manufacturer datasheet downloaded')
