import os,sys,json,hashlib
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v7_r07 as v
rows=[];out=v.O/'final_static_v7'/v.ID;out.mkdir(parents=True,exist_ok=True)
for i,(ph,sg,key) in enumerate(v.items):
 path=v.O/'static_v7'/v.ID/f'{i}.json';saved=json.loads(path.read_text()) if path.exists() else {};w=saved.get('witness');ch=v.scene(i);digest=hashlib.sha256(ch.xml.encode()).hexdigest();r=dict(index=i,stroke=key,starts=saved.get('starts',0),complete=saved.get('complete',False),ok=False,static_witness_found=bool(w),model_sha256=digest,same_compiled_geometry=not saved or digest==saved.get('model_sha256'))
 if w:
  final=v.f.replay(ch,w);r.update(ok=bool(final['ok'] and saved.get('complete') and r['same_compiled_geometry']),reference=final,jaw_axis_branch=w['k']);(out/f'{i}.json').write_text(json.dumps(r,indent=2));(v.H/'models'/f'{v.ID}_stroke_{i}.xml').write_text(ch.xml)
 if saved.get('best_failed'):
  b=saved['best_failed'];r['best_failed']=dict(score=b['score'],errors=b['errors'],hits=b['hits'],reference_forbidden=[h for p in b.get('failed_check',{}).get('poses',[]) for h in p.get('forbidden',[])][:8])
 rows.append(r)
(v.O/'fresh_admission.json').write_text(json.dumps(dict(layout=v.ID,rows=rows,strokes_passed=sum(r['ok'] for r in rows),strokes_total=len(rows),scope='Fresh unchanged reference admission; numerator requires96 completed starts. Incomplete positive proposals separately recorded.'),indent=2,allow_nan=False));print('FRESH',sum(r['ok'] for r in rows),'/',len(rows))
