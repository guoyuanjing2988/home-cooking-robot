"""Fresh old-branch replay as proposals, never reused96-start credit."""
import os,sys,json,copy,time,gc,hashlib
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v7_r07 as v
O=v.O;ID=v.ID;out=O/'static_v7'/ID;out.mkdir(parents=True,exist_ok=True);rows=[];start=time.monotonic()
for i,(_,sg,key) in enumerate(v.items):
 source=O/('static_v6/L84' if v.cfg.get('remove_legacy_motion_sweeps') else 'static_v5/L73')/f'{i}.json';old=json.loads(source.read_text());proposal=old.get('witness') or (old.get('best_failed') or {}).get('raw');ch=v.scene(i)
 checked=v.f.replay(ch,proposal) if proposal and len(proposal['poses'])==len(sg['poses']) else None
 valid=bool(checked and checked['ok']);row=dict(index=i,stroke=key,pass_=valid,reference=checked,source=str(source.relative_to(v.H)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest());rows.append(row)
 file=out/f'{i}.json'
 if not file.exists():
  d=dict(index=i,stroke=key,layout=ID,rows=[],starts=0,solutions_found=0,verified_witnesses=0,witness=checked if valid else None,best_failed=None,complete=False,allocated_seconds_per_unresolved_start=20,required_starts=96,warm_proposal_source=row['source'],warm_proposal_replayed=valid)
  if valid:d['witness']['k']=proposal['k']
  file.write_text(json.dumps(d,indent=2))
 del ch;gc.collect()
 (O/'layouts'/f'{ID}_screen_v7.json').write_text(json.dumps(dict(layout=ID,rows=rows,pass_count=sum(r['pass_'] for r in rows),complete=len(rows)==59,elapsed_s=time.monotonic()-start,scope='Fresh full-geometry branch replay. Numerical search starts not inherited.'),indent=2))
print('SCREEN',ID,sum(r['pass_'] for r in rows),'/59',flush=True)

