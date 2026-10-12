import os,sys,json,numpy as np
os.environ['WORK_STEP_FACTOR']=sys.argv[2]
from chain import checker,target,continuation,next_stroke
from solver import solve
preset=sys.argv[1]
t=target(preset,'holder_load');ch,_=checker(preset,'carrot');ch.active=ch.arm_ids
r=solve(ch,np.array(t['points'][0]),t['approach'],seed=7401,target=t)
print('static',r['status_counts'])
for c in r['candidates'][:3]:
 out=continuation(ch,t,c['q'],np.array(c['rotation']))
 if not out['ok']:print('holder_load',out.get('reason'));continue
 b=next_stroke(preset,'mandoline_work',out['path'][-1],c['rotation'])
 print('mandoline',b['ok'],b.get('reason'))
 rej=b.get('rejection') or {}
 if rej:
  rr=rej.get('rejection',{});print(' checked',rej.get('checked'),'hits',[(h['pair'],round(h.get('real_gap_mm',0),2),h.get('reason','')[:30]) for h in rr.get('hits',[])][:4],'load',rr.get('load',{}).get('ok'),'ratio',round(rr.get('load',{}).get('max_ratio',0),2),'stab',rr.get('stability',{}).get('ok'),'mobile',rr.get('mobile',{}).get('ok'))
 if b.get('position_mm'):print(b)
 break
