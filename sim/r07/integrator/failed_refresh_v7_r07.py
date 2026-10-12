"""Re-evaluate retained failed proposals; stale donor error summaries get no credit."""
import os,sys,json,hashlib,numpy as np
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v7_r07 as v
rows=[]
for file in (v.O/'static_v7'/v.ID).glob('*.json'):
 d=json.loads(file.read_text());b=d.get('best_failed')
 if not b or d.get('witness'):continue
 ch=v.scene(d['index']);sg=v.items[d['index']][1];ch.working_stroke=sg['action']=='process';raw=b['raw'];errors=[];hits=[]
 for pi,pose in enumerate(raw['poses']):
  hands=sg['poses'][pi];ch.hands=hands;ch.set_contacts(hands);q=np.array(pose['q']);bad,_,_=v.f.contacts(ch,q);hits+=bad
  from scipy.spatial.transform import Rotation
  pe=[]
  for side,h in hands.items():
   sid=ch.m.site(side+'_prep').id;target=ch.target_rotation(h,raw['k']);e=dict(side=side,position_mm=float(np.linalg.norm(ch.d.site_xpos[sid]-h['pos'])*1000),orientation_deg=float(np.degrees(Rotation.from_matrix(target.T@ch.d.site_xmat[sid].reshape(3,3)).magnitude())));pe.append(e);errors.append(e)
  pose['errors']=pe
 old=dict(errors=b.get('errors'),hits=b.get('hits'),score=b.get('score'));b.update(errors=errors,hits=hits[:6],score=sum(e['position_mm']+3*e['orientation_deg'] for e in errors)+sum(max(0,h['required_gap_mm']-h['real_gap_mm']) for h in hits)+1000*(len(sg['poses'])-len(raw['poses'])),fresh_failed_proposal_recheck=True,model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest())
 b.pop('failed_check',None)
 if len(raw['poses'])==len(sg['poses']):b['failed_check']=v.f.replay(ch,raw)
 d['failed_proposal_summary_refresh']=dict(previous_summary=old,reason='Initial donor failure summary could belong to an earlier scene. Recompute retained q against final full geometry/targets; earlier per-seed rows remain unchanged. No new solver-start or static credit.')
 file.write_text(json.dumps(d,indent=2));rows.append(dict(index=d['index'],new_errors=errors,new_hits=hits[:6]))
(v.O/f'failed_proposal_refresh_{v.ID}_v7.json').write_text(json.dumps(dict(layout=v.ID,rows=rows),indent=2));print('FAILED_SUMMARIES_REFRESHED',len(rows))
