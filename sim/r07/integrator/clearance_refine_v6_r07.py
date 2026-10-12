"""Refine conservative hull bounds to assess10mm extra reserve, without gate changes."""
import os,sys,json,time,hashlib,gc
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v6_r07 as v
import numpy as np
from motion_v6_r07 import Planner
H=v.H;O=v.O;ID=v.ID;start=time.monotonic();records=[];stats={};counts={'static':0,'path':0};complete=True
motion_files=sorted((O/'motion_v6'/ID).glob('internal_*.json'))
source_hashes={str(f.relative_to(H)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [O/'fresh_admission.json',H/'runtime_v6_r07.py',H/'clearance_refine_v6_r07.py']+motion_files}
checkpoint=O/'clearance_refinement_v6.json';chunks=[]
if checkpoint.exists():
 prior=json.loads(checkpoint.read_text())
 if prior.get('layout')==ID and prior.get('source_hashes')==source_hashes:
  records=prior['rows'];chunks=prior.get('chunks_s',[])
  for row in records:
   counts[row['kind']]+=1
   for cat,value in row['minima'].items():stats.setdefault(row['kind'],{}).setdefault(cat,[]).append(value['reserve_mm'])
done={(r['kind'],r['index'],r['state']) for r in records}
def assess(ch,kind,index,state_id):
 b=ch.bounds;lower=b.last_lower.copy();narrow=0;upper={}
 for i in np.flatnonzero((b.need>0)&(lower<b.need+.010001)&(lower<1000)):
  a,bb,need,cat=b.pairs[i];d=b.pair(a,bb,tol=1e-7);lower[i]=max(lower[i],d['lower_m']);upper[i]=d['upper_m'];narrow+=1
 minima={}
 for cat,ix in b.catids.items():
  valid=ix[lower[ix]<1000]
  if not len(valid):continue
  i=int(valid[np.argmin(lower[valid]-b.need[valid])]);a,bb,need,_=b.pairs[i];reserve=float((lower[i]-need)*1000);minima[cat]=dict(pair=[ch.gnames[a],ch.gnames[bb]],lower_gap_mm=float(lower[i]*1000),upper_gap_mm=float(upper[i]*1000) if i in upper else None,required_mm=float(need*1000),reserve_mm=reserve)
  stats.setdefault(kind,{}).setdefault(cat,[]).append(reserve)
 records.append(dict(kind=kind,index=index,state=state_id,model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),minima=minima,additional_GJK_queries=narrow));counts[kind]+=1
fresh=json.loads((O/'fresh_admission.json').read_text());assert fresh['layout']==ID
for row in fresh['rows']:
 if not row['ok']:continue
 i=row['index'];ch=v.scene(i);sg=v.items[i][1]
 for pi,pose in enumerate(row['reference']['poses']):
  if ('static',i,pi) in done:continue
  ch.hands=sg['poses'][pi];ch.set_contacts(ch.hands);ch.working_stroke=sg['action']=='process';hits,_,_=v.f.contacts(ch,np.array(pose['q']));assert not hits
  assess(ch,'static',i,pi)
 del ch;gc.collect()
for file in motion_files:
 row=json.loads(file.read_text())
 if not row['ok']:continue
 i=row['index'];ch=v.scene(i);sg=v.items[i][1];ch.working_stroke=sg['action']=='process';pl=Planner(ch,sg['poses'][0],seconds=65)
 for ni,state in enumerate(row['final_replay']['states']):
  if ('path',i,ni) in done:continue
  if time.monotonic()-start>1000:complete=False;break
  ei=state['edge'];edge=row['edges'][ei];ha,hb=sg['poses'][ei:ei+2];ch.contact_windows=edge.get('contact_windows',[]);hands=ha if state['segment']==0 and state['alpha']==0 else hb if state['segment']==len(edge['path'])-2 and state['alpha']==1 else {s:dict(h,contacts=[c for c in h.get('contacts',[]) if c in hb[s].get('contacts',[])]) for s,h in ha.items()};assert pl.state(np.array(state['q']),hands)
  assess(ch,'path',i,ni)
 if not complete:break
 del ch,pl;gc.collect()
distribution={kind:{cat:dict(samples=len(x),min_mm=min(x),p05_mm=float(np.percentile(x,5)),median_mm=float(np.median(x)),p95_mm=float(np.percentile(x,95)),max_mm=max(x),fraction_at_least10mm=float(np.mean(np.round(np.array(x),9)>=10))) for cat,x in categories.items()} for kind,categories in stats.items()}
expected={'static':sum(len(r['reference']['poses']) for r in fresh['rows'] if r['ok']),'path':sum(d['final_replay']['states_checked'] for d in [json.loads(f.read_text()) for f in motion_files] if d['ok'])}
complete=complete and counts==expected
chunks.append(time.monotonic()-start)
record=dict(layout=ID,complete=complete,counts=counts,distribution=distribution,rows=records,elapsed_s=time.monotonic()-start,method='Retain original valid lower bounds. For every non-intended positive-gate pair with less than10mm certified extra, compute full unchanged convex support GJK primal/dual bounds(tolerance1e-7m); take max of valid lower certificates. Gate and geometry never change. Self is separately reported at its original gate. One sample is a category minimum at a checked state, not every distant pair.')
record.update(source_hashes=source_hashes,chunks_s=chunks,total_elapsed_s=sum(chunks),expected_counts=expected)
(O/'clearance_refinement_v6.json').write_text(json.dumps(record,indent=2,allow_nan=False))
if '--defer-merge' not in sys.argv:
 clear=json.loads((O/'clearance.json').read_text());clear['refined_reserve_assessment']=dict(complete=complete,counts=counts,distribution=distribution,method=record['method'],source='results/clearance_refinement_v6.json');(O/'clearance.json').write_text(json.dumps(clear,indent=2,allow_nan=False))
print('CLEARANCE_REFINED',counts,complete,distribution,flush=True)
