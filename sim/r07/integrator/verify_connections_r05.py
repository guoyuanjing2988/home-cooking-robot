"""Fresh two-scene collision, endpoint and worst supplied load replay."""
import json,copy,math,time,itertools,hashlib
import numpy as np
import final_check as f,motion_r05 as mo
from point_bound import PointBound
from planner_r05 import Planner
H=f.s.HERE;O=H/'results';motion=json.loads((O/'motion.json').read_text());ws=json.loads((O/'static_all.json').read_text())['witnesses'];rows=json.loads((O/'connection_replay.json').read_text())['rows'] if (O/'connection_replay.json').exists() else [];t0=time.monotonic()
for r in motion['between_strokes']:
 if not r.get('solver_geometry_ok',r['ok']):continue
 digest=hashlib.sha256(json.dumps(r['planner']['path'],sort_keys=True).encode()).hexdigest()
 if any(x['index']==r['index'] and x['pass_'] and x['path_sha256']==digest for x in rows):continue
 i=r['index'];ph,sg,key=mo.items[i];ph2,sg2,key2=mo.items[i+1];ha=sg['poses'][-1];hb=sg2['poses'][0];path=np.array(r['planner']['path']);chs=[mo.scene(ph,sg,i),mo.scene(ph2,sg2,i+1)];hands=[ha,hb];keys=[key,key2];bounds=[PointBound(ch) for ch in chs];checks=[Planner(ch,h,seconds=65) for ch,h in zip(chs,hands)];bad=None;states=0;ratio=0;grip=1e9
 for ch,h,k,q in zip(chs,hands,keys,[path[0],path[-1]]):
  ch.contact_windows=r['planner'].get('contact_windows',[]);oldseg=ch.seg;ch.seg=dict(oldseg,poses=[h]);v=f.replay(ch,dict(k=ws[k]['k'],poses=[dict(q=q.tolist())]));ch.seg=oldseg
  if not v['ok']:bad=dict(kind='Reference endpoint replay',scene=k,witness=v);break
 if not bad:
  for j,(a,b) in enumerate(zip(path,path[1:])):
   n=max(1,int(math.ceil(max(pb.segment_bound(a,b) for pb in bounds)/.004)))
   for k in range(n+1):
    q=a+(b-a)*k/n
    for ch,h,pl,key in zip(chs,hands,checks,keys):
     states+=1
     if not pl.state(q,h):bad=dict(kind='Full two-scene collision',scene=key,segment=j,k=k,blocker=pl.last);break
     for fs in itertools.product(*[x['check_forces_N'] for x in h.values()]):
      for ms in itertools.product(*[x['check_moments_Nm'] for x in h.values()]):
       forces=dict(zip(h,fs));moments=dict(zip(h,ms));t=ch.torque_multi(q,h,forces,moments);gs=[ch.grip_side(q,x,forces[s],moments[s],s)['margin'] for s,x in h.items()];ratio=max(ratio,t['ratio']);grip=min(grip,min(gs))
       if t['ratio']>1 or min(gs)<1:bad=dict(kind='Rated envelope or grip',scene=key,torque=t,min_grip=min(gs));break
      if bad:break
     if bad:break
    if bad:break
   if bad:break
 row=dict(index=i,pass_=not bad,states_checked=states,max_envelope_ratio=ratio,min_grip_margin=grip,blocker=bad,path_sha256=digest,max_point_step_mm=4.,persistent_meal_verified=False);rows=[x for x in rows if x['index']!=i]+[row];(O/'connection_replay.json').write_text(json.dumps(dict(rows=rows,elapsed_s=time.monotonic()-t0),indent=2));print('CONNECTION_FINAL',i,row['pass_'],'states',states,'ratio',ratio,flush=True)
