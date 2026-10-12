import json,time,sys,copy,hashlib
import numpy as np,mujoco
import r07_runtime as rt
import motion_r05 as mo
s=rt.s;H=rt.H;O=rt.O
lo,hi=map(int,sys.argv[1:3]);(O/'final_static').mkdir(exist_ok=True)
for i in range(lo,min(hi,len(mo.items))):
 ph,sg,key=mo.items[i];old=json.loads((O/'static'/f'{i}.json').read_text())
 raw=min(old['rows'],key=lambda r:sum(e['position_mm']+3*e['orientation_deg'] for p in r['raw']['poses'] for e in p['errors']))['raw']
 ch=mo.scene(ph,sg,i);ch.search_carriage=True;poses=[];q=np.array(raw['poses'][0]['q'])
 for pi,hands in enumerate(sg['poses']):
  ch.set_contacts(hands)
  if pi<len(raw['poses']):q=np.array(raw['poses'][pi]['q'])
  q,errors=ch.solve_least(q,hands,raw['k']);poses.append(dict(q=q.tolist(),errors=errors))
 check=rt.f.replay(ch,dict(k=raw['k'],poses=poses))
 out=dict(index=i,stroke=key,phase=ph['id'],logical=ph['id'].split('.')[0],label=sg['label'],ok=check['ok'],search_starts=old['starts'],fresh_continuation_solves=len(poses),poses=check['poses'],witness=check if check['ok'] else None,max_envelope_ratios=check['max_envelope_ratios'],min_grip_margin=check['min_grip_margin'],model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),process_sha256=hashlib.sha256(json.dumps(s.P,sort_keys=True).encode()).hexdigest(),scope='Full fresh pose/load/grip/all-pair replay on new geometry with retained staged raw inputs and delivered contents. A failed pose is diagnostic only.')
 rt.write('final_static/'+str(i)+'.json',out)
 print(i,key,out['ok'],'poses',len(poses),flush=True)
