"""Reuse only an exactly identical already searched per-stroke problem."""
import sys,os,json,hashlib,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';source,target=sys.argv[1:3]
os.environ['R07_LAYOUT']=target
import runtime_v5_r07 as v
oldP=json.loads((O/'layouts'/f'{source}_process_v4.json').read_text());olditems=[(ph,sg) for ph in oldP['phases'] for sg in ph['segments']];out=O/'static_v5'/target;out.mkdir(exist_ok=True)
records=[]
for i,(ph,sg,key) in enumerate(v.items):
 if str(i) in sys.argv[3:]:continue
 f=O/'static_v5'/source/f'{i}.json';dest=out/f'{i}.json'
 if not f.exists():continue
 saved=json.loads(f.read_text())
 if dest.exists():
  previous=json.loads(dest.read_text());inheritance=previous.get('inheritance',{})
  # Refresh an unadvanced exact reuse after its original worker finishes.
  # Never overwrite any independent target-layout search or a changed scene.
  if inheritance.get('source')!=str(f.relative_to(H)) or previous['starts']!=inheritance.get('source_starts') or saved['starts']<=previous['starts']:continue
 if sg!=olditems[i][1]:continue
 ch=v.scene(i);sha=hashlib.sha256(ch.xml.encode()).hexdigest()
 if sha!=saved.get('model_sha256'):continue
 replay=v.f.replay(ch,saved['witness']) if saved.get('witness') else None
 if replay and not replay['ok']:continue
 saved.update(layout=target,inheritance=dict(source=str(f.relative_to(H)),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),source_starts=saved['starts'],same_full_scene_hash=sha,same_complete_stroke_definition=True,additional_starts_claimed=0,reason='Same numerical problem; physical layout unchanged, only other stroke targets differ. Partial searches resume at the next unused seed.'),process_sha256=hashlib.sha256(json.dumps(v.P,sort_keys=True).encode()).hexdigest())
 if replay:saved['witness']=replay
 dest.write_text(json.dumps(saved,indent=2));records.append(i)
(O/'layouts'/f'{target}_exact_search_reuse.json').write_text(json.dumps(dict(source=source,target=target,indices=records,scope='No copied failed or positive result from a different geometry/target; actual source96 starts retained and fresh positives replayed.'),indent=2))
print('EXACT_PROBLEM_REUSE',source,target,records)
