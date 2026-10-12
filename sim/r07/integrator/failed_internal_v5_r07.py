"""Full-budget internal-path diagnostics even when 96-start statics failed."""
import os,sys,time,json,hashlib
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np
import runtime_v5_r07 as v
from motion_v5_r07 import mo,replay
from least_analytic_v4_r07 import solve
began=time.monotonic();out=v.O/'motion_v5'/v.ID;out.mkdir(exist_ok=True)
for index in map(int,sys.argv[2:]):
 if time.monotonic()-began>870:break
 target=out/f'internal_{index}.json'
 if target.exists():continue
 source=v.O/'static_v5'/v.ID/f'{index}.json';saved=json.loads(source.read_text());assert saved['complete'] and not saved.get('witness')
 raw=saved['best_failed']['raw'];ph,sg,key=v.items[index];ch=v.scene(index);ch.search_carriage=True;ch.lock_initial_carriage=False;ch.witness_k=raw['k'];poses=[];proposals=[]
 for pi,hands in enumerate(sg['poses']):
  if pi<len(raw['poses']):q=np.array(raw['poses'][pi]['q']);e=raw['poses'][pi].get('errors',[]);hits=[];method='Retained failed-static endpoint'
  else:
   q=np.array(poses[-1]['q']);ch.hands=hands;ch.set_contacts(hands);q,e,hits,_=solve(ch,q,hands,raw['k'],time.monotonic()+20);method='20s collision-aware missing-endpoint proposal'
  poses.append(dict(q=q.tolist(),errors=e));proposals.append(dict(pose=pi,method=method,errors=e,blockers=hits[:8]))
 witness=dict(k=raw['k'],poses=poses);static=v.f.replay(ch,witness);edges=[];v.s.PARK=np.array(poses[0]['q']);ch.refine_support_endpoints=False
 for j,(pa,pb) in enumerate(zip(poses,poses[1:])):
  a=np.array(pa['q']);b=mo.shortq(ch,a,pb['q']);result=mo.plan_section(ch,a,b,sg['poses'][j],sg['poses'][j+1],997000+index*10+j,process=sg['action']=='process');edges.append(result);print('FAILED_STATIC_INTERNAL_EDGE',index,j,result['ok'],round(result['planner_time_s'],2),flush=True)
 final=replay(ch,sg,witness,edges);admitted=bool(final['pass_'] and static['ok'])
 # These diagnostics are kept distinct from the frozen admitted source set.
 row=dict(index=index,stroke=key,layout=v.ID,ok=False,diagnostic_only=True,new_unadmitted_path_candidate=admitted,edges=edges,final_replay=final,static_endpoint_reference=static,endpoint_proposals=proposals,meal_state_verified=False,jaw_axis_branch=raw['k'],endpoint_witness=witness,source_static_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),reason='Full-budget path attempt from failed96-start static evidence; no static or meal credit without a new admitted source and complete downstream replay.')
 target.write_text(json.dumps(row,indent=2));(v.H/'models'/f'{v.ID}_internal_{index}.xml').write_text(ch.xml);print('FAILED_STATIC_INTERNAL',index,'candidate',admitted,flush=True)
