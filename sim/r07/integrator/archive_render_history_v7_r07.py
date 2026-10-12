"""Lossless archive of historical render-source duplicates to obey3GB cap."""
import sys,json,hashlib,zipfile
from pathlib import Path
H=Path(__file__).resolve().parent;version=sys.argv[1] if len(sys.argv)>1 else 'v1';assert version in ('v1','v2','v3')
base=(H/'history'/version/'renders').resolve();assert base.is_relative_to((H/'history').resolve()) and base.is_dir()
files=sorted(base.rglob('*.scene.json'));batches=[];batch=[];size=0
for f in files:
 assert f.resolve().is_relative_to(base)
 if batch and size+f.stat().st_size>40_000_000:batches.append(batch);batch=[];size=0
 batch.append(f);size+=f.stat().st_size
if batch:batches.append(batch)
records=[]
manifest=H/'history'/version/'render_sources_archival_v7.json'
if manifest.exists():
 print('ARCHIVE_ALREADY_VERIFIED',version);raise SystemExit(0)
for i,group in enumerate(batches):
 archive=H/'history'/version/f'render_sources_v7_{i:02}.zip'
 rows=[dict(original=f.relative_to(H).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in group]
 if not archive.exists():
  with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for f,row in zip(group,rows):z.write(f,row['original'])
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  for row in rows:assert hashlib.sha256(z.read(row['original'])).hexdigest()==row['sha256']
 # Only individually verified render-source files in the exact historical
 # directory are removed. Images, results, code, posts and R05 stay intact.
 for f,row in zip(group,rows):
  assert f.resolve().is_relative_to(base) and f.suffix=='.json' and f.name.endswith('.scene.json')
  assert hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256'];f.unlink()
 records.append(dict(archive=str(archive.relative_to(H)),sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),members=rows,compressed_bytes=archive.stat().st_size,original_bytes=sum(r['bytes'] for r in rows)))
out=dict(version=version,archives=records,original_bytes=sum(r['original_bytes'] for r in records),compressed_bytes=sum(r['compressed_bytes'] for r in records),lossless_verified=True,scope='Historical render-source JSON duplicates only; restore exact member paths from zip. All historical posts/images and simulation evidence remain. Current v6/v7 render sources untouched.')
(H/'history'/version/'render_sources_archival_v7.json').write_text(json.dumps(out,indent=2));print('ARCHIVED_RENDER_HISTORY',version,out['original_bytes'],out['compressed_bytes'])
