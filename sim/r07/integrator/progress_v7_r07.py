"""Persist current evidence after each bounded wave; no acceptance shortcuts."""
import json,csv,time
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results'
with (O/'iterations.csv').open(encoding='utf-8-sig',newline='') as f:
 r=csv.DictReader(f);fields=r.fieldnames;old=[row for row in r if not row['kind'].startswith('v7_live_')]
rows=[];layouts=[]
def load(f):
 try:return json.loads(f.read_text(encoding='utf-8-sig'))
 except (OSError,ValueError):return None
for n in range(90,102):
 ID='L'+str(n);cfg=load(O/'layouts'/f'{ID}.json')
 if not cfg:continue
 row=dict(layout=ID,reason=cfg['reason'])
 for suffix,key in [('screen_v7','screen'),('headroom_v7','headroom'),('dock_packing_v7','packing'),('target_certificates','target_certificate')]:
  f=O/'layouts'/f'{ID}_{suffix}.json';d=load(f)
  if d:
   row[key]=dict(file=str(f.relative_to(H)),complete=d.get('complete',True),pass_count=d.get('pass_count'),pass_=d.get('pass_'),penetrations=len(d.get('penetrations',[])),blocked=sum(x.get('impossible_at_declared_targets',False) for x in d.get('rows',[])))
   rows.append(dict(kind='v7_live_'+key,id=ID,layout=ID,pass_=d.get('pass_',False),status=json.dumps(row[key]),evidence=str(f.relative_to(H))))
 f=O/'reachability'/ID/'R.json';d=load(f)
 if d:row['map']=dict(complete=d['complete'],clear=sum(x['pass_'] for x in d['rows']),total=len(d['rows']));rows.append(dict(kind='v7_live_map',id=ID,layout=ID,pass_=row['map']['clear'],status=json.dumps(row['map']),evidence=str(f.relative_to(H))))
 stats=[load(f) for f in (O/'static_v7'/ID).glob('*.json')];stats=[d for d in stats if d]
 row['statics']=dict(complete96=sum(d.get('complete',False) and d['starts']>=96 for d in stats),proposals=sum(bool(d.get('witness')) for d in stats),starts=sum(d['starts'] for d in stats))
 layouts.append(row)
(O/'progress_v7.json').write_text(json.dumps(dict(updated_unix=time.time(),layouts=layouts,scope='Live checkpoint, not final delivery; full static, fold and connection work ongoing'),indent=2))
with (O/'iterations.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(old);w.writerows({k:row.get(k,'') for k in fields} for row in rows)
print(json.dumps([(x['layout'],x.get('map'),x['statics']) for x in layouts]))



