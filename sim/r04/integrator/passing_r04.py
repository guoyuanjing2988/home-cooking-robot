"""Full-carriage passing search and convex swept-translation certificate."""
import json,time
import numpy as np,mujoco
import motion_check as mo
import final_check as f
from distance import Bounds
s=f.s;H=s.HERE;beg=time.monotonic();ch,hands=mo.empty_cell();rng=np.random.default_rng(831);old=json.loads((H/'baseline/motion.json').read_text())['passing'];qsource=np.array(old['q_crossing']);tried=0;solutions=0;best=None;last=[]
def quick(q):
 ch.set_contacts(hands);return ch.forbidden(q)
def certify(a,b):
 # Both arm configurations are constant; only world-X carriages translate.
 ch.d.qpos[:]=a;mujoco.mj_forward(ch.m,ch.d);oracle=Bounds(ch,f.required);motion=np.zeros(ch.m.ngeom)
 for g in range(ch.m.ngeom):
  body=int(ch.m.geom_bodyid[g]);parents=[]
  while body:parents.append(body);body=int(ch.m.body_parentid[body])
  for side in ['R','L']:
   if ch.m.body(side+'_carriage').id in parents:motion[g]=b[ch.qa[side+'_carriage_x']]-a[ch.qa[side+'_carriage_x']]
 lo=np.zeros((ch.m.ngeom,3));hi=lo.copy()
 for g in range(ch.m.ngeom):
  if ch.m.geom_type[g]==0:lo[g]=-1e6;hi[g]=1e6;continue
  for k,axis in enumerate(np.eye(3)):lo[g,k]=oracle.support(g,-axis)[k];hi[g,k]=oracle.support(g,axis)[k]
 narrow=0;mins={};reject=[]
 for u,v,need,cat in oracle.pairs:
  dx=motion[u]-motion[v];alo=lo[u].copy();ahi=hi[u].copy();alo[0]+=min(0,dx);ahi[0]+=max(0,dx)
  lower=float(np.linalg.norm(np.maximum(np.maximum(alo-hi[v],lo[v]-ahi),0)))
  if lower<need+1e-7:
   result=oracle.pair(u,v,translation=np.array([dx,0,0]));lower=max(lower,result['lower_m']);narrow+=1
  if lower<need-1e-6:reject.append(dict(pair=[ch.gnames[u],ch.gnames[v]],gap_lower_mm=lower*1000,required_mm=need*1000))
  if cat not in mins or lower<mins[cat]['lower_mm']/1000:mins[cat]=dict(pair=[ch.gnames[u],ch.gnames[v]],lower_mm=lower*1000,required_mm=need*1000)
 return dict(ok=not reject,narrow_queries=narrow,eligible_pairs=len(oracle.pairs),min_clearance=mins,blockers=reject[:12],method='Continuous convex distance of A-B plus the relative carriage translation segment; includes every time in the edge, no absent-contact claim')
for k in range(1600):
 if time.monotonic()-beg>140:break
 tried=k+1;q=qsource.copy() if k==0 else np.array(s.PARK);q[ch.qa['R_carriage_x']]=-.80;q[ch.qa['L_carriage_x']]=-.80
 if k:
  for n in s.ck.JOINTS:q[ch.qa[n]]=rng.uniform(*ch.m.jnt_range[ch.jid[n]])
 for n in s.ck.JAWS:q[ch.qa[n]]=.01
 hits=quick(q)
 if hits:last=hits[:6];continue
 bad,mins,ca=f.contacts(ch,q)
 if bad:last=bad[:6];continue
 solutions+=1;a=q.copy();b=q.copy();a[ch.qa['R_carriage_x']]=-1.70;a[ch.qa['L_carriage_x']]=.045;b[ch.qa['R_carriage_x']]=.045;b[ch.qa['L_carriage_x']]=-1.70
 bad=None
 for alpha in np.linspace(0,1,49):
  hits=quick(a+(b-a)*alpha)
  if hits:bad=dict(alpha=float(alpha),blockers=hits[:6]);break
 if bad:last=[bad];continue
 cert=certify(a,b)
 if not cert['ok']:last=cert['blockers'];continue
 best=dict(q_crossing=q.tolist(),q_start=a.tolist(),q_end=b.tolist(),seed=k,continuous_certificate=cert,reference_samples=49,max_carriage_step_mm=1745/48);break
if best is None:best=dict(q_crossing=qsource.tolist(),reference_samples=0)
out=dict(pass_=bool(best.get('continuous_certificate',{}).get('ok')),seeds_tried=tried,solutions_found=solutions,verified_witnesses=int('continuous_certificate' in best),**best,first_blockers=last,elapsed_s=time.monotonic()-beg,scope='Full idle-template cell, both OEM arms and all staged raw foods/stored bowls/tools. Exact swept-carriage edge is a RRT-Connect direct-edge special case with unchanged gaps; no food or tool attachment transition. Not a conserved-meal certificate.')
(H/'results/passing.json').write_text(json.dumps(out,indent=2));print('passing',out['pass_'],'seeds',tried,'free crossing solutions',solutions,flush=True)
