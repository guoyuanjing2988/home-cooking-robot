"""Reuse search ONLY when the compiled scene, task and envelope are identical."""
import os,sys,json,hashlib,time
source,destination,index=sys.argv[1],sys.argv[2],int(sys.argv[3]);os.environ['R07_LAYOUT']=destination
import runtime_v2_r07 as v
def read(p):return json.loads(p.read_text())
oldfile=v.O/'static_v2'/source/f'{index}.json';newfile=v.O/'static_v2'/destination/f'{index}.json';r=read(oldfile);ch=v.scene(index)
digest=hashlib.sha256(ch.xml.encode()).hexdigest();assert digest==r['model_sha256'],'Different physical scene: no budget transfer permitted.'
source_p=read(v.O/f'layouts/{source}_process.json');source_s=[a for p in source_p['phases'] for a in p['segments']][index]
assert source_s==v.items[index][1],'Different declared task: no budget transfer permitted.'
assert read(v.O/f'layouts/{source}_envelope.json')['envelope_Nm']==read(v.O/f'layouts/{destination}_envelope.json')['envelope_Nm']
if newfile.exists():
 current=read(newfile)
 if current['starts']>=r['starts']:print('Existing coverage greater; no adoption');sys.exit(0)
 (v.H/'audit'/f'{destination}_static_{index}_preadoption_{time.time_ns()}.json').write_text(newfile.read_text())
if r.get('witness'):assert v.f.replay(ch,r['witness'])['ok']
r['equivalent_scene_reuse']=dict(source=str(oldfile.relative_to(v.H)).replace('\\','/'),source_sha256=hashlib.sha256(oldfile.read_bytes()).hexdigest(),source_layout=source,starts_reused=r['starts'],same_model_sha256=digest,same_segment=True,same_envelope=True,meaning='These starts were actually performed on exactly this compiled scene and target problem. Counted once in aggregate compute; not represented as new destination-layout CPU work.')
r['layout']=destination;r['process_sha256']=hashlib.sha256(json.dumps(v.P,sort_keys=True).encode()).hexdigest();newfile.parent.mkdir(parents=True,exist_ok=True);newfile.write_text(json.dumps(r,indent=2));print('EQUIVALENT_SEARCH',source,destination,index,r['starts'],flush=True)
