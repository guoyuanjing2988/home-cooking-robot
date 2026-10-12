"""Prepare reviewer-only v2 adapters; preserve the first review artifacts."""
from pathlib import Path
H=Path(__file__).resolve().parent
text=(H/'common.py').read_text()
text=text.replace("O=H/'results'", "O=H/'results_v2'")
text=text.replace('import r07_runtime as rt', "os.environ.setdefault('R07_LAYOUT','L13')\nimport runtime_v2_r07 as v\nrt=v.rt")
text=text.replace('f=rt.f;s=rt.s', 'mo.items=v.items\nmo.scene=lambda ph,sg,index:v.scene(index)\nf=rt.f;s=rt.s')
text=text.replace("ENV=json.loads((I/'results/torque_envelope.json').read_text())['envelope_Nm']", "ENV=json.loads((I/'results/layouts'/f'{v.ID}_envelope.json').read_text())['envelope_Nm']")
start=text.index('def seed(i):');end=text.index('def independent_pose',start)
text=text[:start]+'''def candidate(i):
    p=I/'results/static_v2'/v.ID/f'{i}.json'
    r=json.loads(p.read_text()) if p.exists() else {}
    return r.get('witness') or (r.get('best_failed') or {}).get('raw')
def seed(i):return candidate(i)['k']
'''+text[end:]
(H/'v2_common.py').write_text(text)
text=(H/'rules.py').read_text().replace('from common import *','from v2_common import *')
text=text.replace("audit=H/'audit'", "audit=H/'audit_v2'")
text=text.replace("read('final_static/'+str(idx)+'.json')",'candidate(idx)')
text=text.replace("read('park_full.json')", "read(f'layouts/{v.ID}_park_full.json')")
(H/'v2_rules.py').write_text(text)
