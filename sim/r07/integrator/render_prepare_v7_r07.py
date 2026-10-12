from pathlib import Path
H=Path(__file__).resolve().parent
s=(H/'blender_render_v2_r07.py').read_text()
marker='bpy.context.preferences.filepaths.temporary_directory'
insert="""if 'meshes_file' in data:
 import hashlib
 source=(path.parent/data['meshes_file']).resolve();assert source.parent==path.parent
 blob=source.read_bytes();assert hashlib.sha256(blob).hexdigest()==data['meshes_sha256']
 data['meshes']=json.loads(blob)
"""
s=s.replace(marker,insert+marker);(H/'blender_render_v7_r07.py').write_text(s)
# Compose only after all disjoint bounded render jobs have finished.
s=(H/'render_batch_v7_impl_r07.py').read_text();start=s.index('# Derivative');stop=s.index('for view in manifest')
s=s[:start]+s[stop:];s=s.replace("str(H/'blender_render_v2_r07.py')","str(H/'blender_render_v7_r07.py')").replace('timeout=150','timeout=300')
(H/'render_compose_v7_r07.py').write_text(s)
print('V7 render-only adapters; full mesh blobs deduplicated and hash-verified')
