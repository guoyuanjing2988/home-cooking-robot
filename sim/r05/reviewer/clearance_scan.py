"""Rank every retained path waypoint by unexempted clearance reserve."""
import json,numpy as np,time
import motion_audit as a
rows=[];t0=time.monotonic()
for r in a.M['internal']:
 if not r['ok']:continue
 i=r['index'];ph,sg,key=a.mo.items[i];sg=r.get('segment_override',sg);ch=a.mo.scene(ph,sg,i);worst=None;states=0
 for j,e in enumerate(r['edges']):
  ch.contact_windows=e.get('contact_windows',[]);ha=sg['poses'][j];hb=sg['poses'][j+1];common={side:dict(h,contacts=[c for c in h.get('contacts',[]) if c in hb.get(side,{}).get('contacts',[])]) for side,h in ha.items()}
  for k,q in enumerate(e['path']):
   h=ha if k==0 else hb if k==len(e['path'])-1 else common;hits,mins,_,_=a.state(ch,np.array(q),h,sg['action']=='process');states+=1
   for cat,v in mins.items():
    if cat=='self':continue
    if worst is None or v['reserve_mm']<worst['reserve_mm']:worst=dict(edge=j,waypoint=k,category=cat,**v)
 rows.append(dict(index=i,stroke=key,states=states,minimum=worst));print('CLEARANCE',i,states,round(worst['reserve_mm'],7),flush=True)
 (a.O/'clearance_scan.json').write_text(json.dumps(dict(rows=rows,tightest=min(rows,key=lambda x:x['minimum']['reserve_mm']),scope='All retained waypoint geometries, ranking of saved proposals. Fully bounded state replay is recorded separately for the selected tightest path.',elapsed_s=time.monotonic()-t0),indent=2))
