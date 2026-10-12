"""Reuse only byte-identical compiled geometry AND identical stroke target data.
Fresh reference replay is mandatory. No new starts are fabricated.
"""
import os,sys,json,hashlib,copy
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v5_r07 as v
old=json.loads((v.O/'layouts/L59_process_v5.json').read_text());before=[s for ph in old['phases'] for s in ph['segments']];out=v.O/'static_v5'/v.ID;out.mkdir(parents=True,exist_ok=True);rows=[]
for i,(_,sg,_) in enumerate(v.items):
 source=v.O/'static_v5/L59'/f'{i}.json';dest=out/f'{i}.json'
 if dest.exists() or not source.exists():continue
 r=json.loads(source.read_text())
 if sg!=before[i] or not r.get('witness') or not r.get('complete'):continue
 ch=v.scene(i);sha=hashlib.sha256(ch.xml.encode()).hexdigest()
 if sha!=r.get('model_sha256'):rows.append(dict(index=i,reused=False,reason='Compiled full geometry differs'));continue
 check=v.f.replay(ch,r['witness'])
 if not check['ok']:rows.append(dict(index=i,reused=False,reason='Fresh reference rejected',reference=check));continue
 r.update(layout=v.ID,witness=check,model_sha256=sha,process_sha256=hashlib.sha256(json.dumps(v.P,sort_keys=True).encode()).hexdigest(),reused_same_model_target=True,reuse_source=str(source.relative_to(v.H)),reuse_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),reuse_note='96 actual original L59 starts; complete model SHA and complete stroke dictionary identical; fresh full reference replay in destination. Not96 additional starts.')
 dest.write_text(json.dumps(r,indent=2));rows.append(dict(index=i,reused=True,source=r['reuse_source']))
(v.O/'layouts'/f'{v.ID}_static_reuse.json').write_text(json.dumps(rows,indent=2));print(v.ID,'identical-model reuse',sum(r['reused'] for r in rows),flush=True)
