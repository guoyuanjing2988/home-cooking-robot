import json,hashlib,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2];I=ROOT/'sim/r03/integrator'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[ROOT/p for p in ['DECISIONS.md','posts/r03/integrator.md','posts/r03/reviewer.md','posts/r02/reviewer.md','posts/r02/concept2.md','posts/r02/tools.md','posts/r02/transport.md','posts/r01/reviewer.md']]
files=inputs+list(I.rglob('*'))
manifest={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in files if p.is_file()}
(H/'audit/input_hashes.json').write_text(json.dumps(manifest,indent=2))
best=json.loads((H/'baseline/best.json').read_text());dst=H/'baseline/strokes';dst.mkdir(exist_ok=True)
for ph,stage in best['phase_source_stages'].items():
 for p in (I/'results'/stage/'strokes').glob(ph+'__*.json'):shutil.copy2(p,dst/p.name)
print('hashed',len(manifest),'copied strokes',len(list(dst.glob('*.json'))))
