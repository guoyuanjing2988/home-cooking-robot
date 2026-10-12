"""All sampled path endpoints through the unchanged static checker, no windows."""
import json,numpy as np,sys
import motion_audit as a
rows=[]
ids=list(map(int,sys.argv[1:])) if len(sys.argv)>1 else [16,54,85,4,5,94]
for i in ids:
 r=a.M['internal'][i];ph,sg,key=a.mo.items[i];sg=r.get('segment_override',sg);ch=a.mo.scene(ph,sg,i)
 for j,e in enumerate(r['edges']):
  ch.contact_windows=[];old=ch.seg;ch.seg=dict(old,poses=[sg['poses'][j],sg['poses'][j+1]])
  out=a.f.replay(ch,dict(k=a.W[key]['k'],poses=[dict(q=e['path'][0]),dict(q=e['path'][-1])]))
  ch.seg=old;rows.append(dict(kind='internal',index=i,edge=j,pass_=out['ok'],errors=[x['errors'] for x in out['poses']],blockers=[x['forbidden'] for x in out['poses']]))
for i in ([] if len(sys.argv)>1 else [83,90]):
 r=a.M['between_strokes'][i]
 for j,q in [(i,r['planner']['path'][0]),(i+1,r['planner']['path'][-1])]:
  ph,sg,key=a.mo.items[j];ch=a.mo.scene(ph,sg,j);ch.contact_windows=[];ch.seg=dict(ch.seg,poses=[sg['poses'][-1] if j==i else sg['poses'][0]]);out=a.f.replay(ch,dict(k=a.W[key]['k'],poses=[dict(q=q)]))
  rows.append(dict(kind='connection',index=i,endpoint_scene=j,pass_=out['ok'],errors=[x['errors'] for x in out['poses']],blockers=[x['forbidden'] for x in out['poses']]))
name='endpoint_audit_'+('_'.join(map(str,ids)))+'.json' if len(sys.argv)>1 else 'endpoint_audit.json'
(a.O/name).write_text(json.dumps(dict(rows=rows,all_pass=all(r['pass_'] for r in rows),scope='Fresh unchanged static reference replay with contact_windows empty; source/goal endpoint targets use their declared phase and actual full template scene.'),indent=2));print('ENDPOINT_AUDIT',len(rows),all(r['pass_'] for r in rows))
