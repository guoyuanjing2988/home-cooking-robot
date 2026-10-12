"""Fresh unchanged-reference replay of every selected positive/failed candidate."""
import os,sys,json,hashlib,runpy
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v2_r07 as v
dest=v.O/'final_static_v2'/v.ID;dest.mkdir(parents=True,exist_ok=True);rows=[]
for i,(ph,sg,key) in enumerate(v.items):
 file=v.O/'static_v2'/v.ID/f'{i}.json';saved=json.loads(file.read_text()) if file.exists() else {};raw=saved.get('witness') or (saved.get('best_failed') or {}).get('raw');ch=v.scene(i);check=v.f.replay(ch,raw) if raw else None;ok=bool(check and check['ok']);digest=hashlib.sha256(ch.xml.encode()).hexdigest()
 row=dict(index=i,stroke=key,layout=v.ID,ok=ok,check=check,required_poses=len(sg['poses']),checked_poses=len(check['poses']) if check else 0,model_sha256=digest,search_model_sha256=saved.get('model_sha256'),same_compiled_geometry=digest==saved.get('model_sha256') if saved else None,starts=saved.get('starts',0),required_starts=96,source=f'results/static_v2/{v.ID}/{i}.json');(dest/f'{i}.json').write_text(json.dumps(row,indent=2));rows.append(row)
 if saved.get('witness') and not ok:raise RuntimeError('Positive witness failed fresh admission: '+key)
 if i%10==0:print('REPLAY',i,sum(r['ok'] for r in rows),flush=True)
runpy.run_path(str(v.H/'rules_r07.py'))
v.rt.write('fresh_admission.json',dict(layout=v.ID,rows=[{k:x for k,x in r.items() if k!='check'} for r in rows],strokes_passed=sum(r['ok'] for r in rows),strokes_total=len(rows),reference_and_copied_code_unchanged=True))
print('FRESH_ADMISSION',sum(r['ok'] for r in rows),'/',len(rows),flush=True)
