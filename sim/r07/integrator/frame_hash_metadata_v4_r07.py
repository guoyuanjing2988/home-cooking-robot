"""State explicitly the compiled-text hash versus Windows file-byte hash."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results'
for name in ('frame_manifest.json','executed_local_v4.json'):
 p=O/name;d=json.loads(p.read_text());model=H/d['model_xml']
 canonical=hashlib.sha256(model.read_text().encode('utf-8')).hexdigest()
 assert canonical==d['model_sha256'], 'Model contents differ beyond native newline serialization'
 d['model_hash_scope']='SHA256 of compiled XML UTF8 text with LF newlines; Windows file-byte hash separately retained'
 d['model_file_sha256']=hashlib.sha256(model.read_bytes()).hexdigest()
 p.write_text(json.dumps(d,indent=2,allow_nan=False))
print('FRAME_MODEL_HASHES_MATCH_AFTER_DECLARED_NEWLINE_NORMALIZATION')
