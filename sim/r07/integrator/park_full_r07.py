"""Full scene park optimisation, retaining every forbidden geometric pair."""
import time,json,xml.etree.ElementTree as E,copy
import numpy as np,mujoco
from scipy.optimize import differential_evolution
import r07_runtime as rt
from distance import Bounds
H=rt.H;O=rt.O;c=dict(rt.s.model.CONFIG)
tr,meta=rt.s.model.build(c);m=mujoco.MjModel.from_xml_string(E.tostring(tr.getroot(),encoding='unicode'))
ch=object.__new__(rt.s.ck.Checker);ch.desc=rt.s.ck.hand([0,0,1],jaw_axis=[0,1,0]);ch.bind_model(m);ch.allowed=[];b=Bounds(ch,rt.f.required)
if '--populated' in __import__('sys').argv:
 import motion_r05 as mo
 ch=mo.scene(*mo.items[0][:2],0);ch.allowed=[];m=ch.m;b=Bounds(ch,rt.f.required)
p=json.loads((O/('park_full.json' if (O/'park_full.json').exists() else 'park_search.json')).read_text());q=np.array(p['q'])
# Small early broadphase uses conservative rotated local mesh boxes; narrow
# distance tests retain full source shapes. No broadphase overlap is a pass.
local=np.zeros((m.ngeom,3));center=np.zeros_like(local)
for g in range(m.ngeom):
 typ=m.geom_type[g];sz=m.geom_size[g]
 if typ==7:
  verts=b.local[g];center[g]=(verts.max(0)+verts.min(0))/2;local[g]=(verts.max(0)-verts.min(0))/2
 elif typ==6:local[g]=sz
 elif typ==3:local[g]=[sz[0],sz[0],sz[0]+sz[1]]
 elif typ==5:local[g]=[sz[0],sz[0],sz[1]]
 elif typ==2:local[g]=sz[0]
 else:local[g]=sz
records=[];t0=time.monotonic()
for side in ('R','L'):
 names=meta['arms'][side];ix=[ch.qa[n] for n in names]+[ch.qa[side+'_carriage_x']]
 ids=np.array([g for g,n in enumerate(ch.gnames) if ch.robot[g] and n.startswith(side+'_')],int)
 # Keep the selected actual mounting orientation fixed during full scene
 # optimisation; torque envelopes therefore remain valid for all trials.
 pairs=np.array([(a,bb,need) for a,bb,need,cat in b.pairs if a in ids or bb in ids],float)
 aa=pairs[:,0].astype(int);bb=pairs[:,1].astype(int);needs=pairs[:,2]
 lim=[m.jnt_range[ch.jid[n]].tolist() for n in names]+[[-1.5,-.55] if side=='R' else [-.30,.46]]
 if '--folded' in __import__('sys').argv:lim[2]=[2.,float(np.radians(160))] if side=='R' else lim[2]
 if '--negative-fold' in __import__('sys').argv and side=='R':lim[2]=[-float(np.radians(160)),-2.]
 best=[None];evaluations=[0]
 def evaluate(x):
  evaluations[0]+=1;q[ix]=x;ch.d.qpos[:]=q;mujoco.mj_kinematics(m,ch.d)
  rot=ch.d.geom_xmat.reshape(-1,3,3);pos=ch.d.geom_xpos+np.einsum('gij,gj->gi',rot,center);ext=np.einsum('gij,gj->gi',abs(rot),local);lo=pos-ext;hi=pos+ext
  for g in ids:
   typ=m.geom_type[g];sz=m.geom_size[g]
   if typ in (3,5):
    z=rot[g][:,2];e=sz[0]+sz[1]*abs(z) if typ==3 else sz[0]*np.sqrt(np.maximum(0,1-z*z))+sz[1]*abs(z)
    lo[g]=pos[g]-e;hi[g]=pos[g]+e
  for g in ids:
   if m.geom_type[g]==7:
    pts=b.local[g]@rot[g].T+ch.d.geom_xpos[g];lo[g]=pts.min(0);hi[g]=pts.max(0)
  viol=np.r_[np.maximum(-1.789-lo[ids,0],0),np.maximum(hi[ids,0]-.679,0),np.maximum(.241-lo[ids,1],0),np.maximum(hi[ids,1]-.589,0),np.maximum(.861-lo[ids,2],0),np.maximum(hi[ids,2]-1.34,0)]
  dist=np.linalg.norm(np.maximum(np.maximum(lo[aa]-hi[bb],lo[bb]-hi[aa]),0),axis=1)
  close=np.flatnonzero(dist<needs+.004);coll=[]
  for k in close:
   gap=mujoco.mj_geomDistance(m,ch.d,int(aa[k]),int(bb[k]),float(needs[k]+.004),None)
   coll.append(max(0,float(needs[k])+.001-gap))
  score=float(sum(viol**2)*2000+sum(v*v for v in coll)*2000)
  if best[0] is None or score<best[0]['score']:
   best[0]=dict(score=score,q=q.tolist(),band_violation_mm=float(max(viol,default=0)*1000),max_collision_violation_mm=float(max(coll,default=0)*1000),evaluations=evaluations[0])
  return score
 for seed in (711,712,713):
  if time.monotonic()-t0>650:break
  x0=np.clip(q[ix],[l[0]+1e-7 for l in lim],[l[1]-1e-7 for l in lim])
  res=differential_evolution(evaluate,lim,popsize=10,maxiter=150,tol=1e-8,seed=seed,polish=True,workers=1,x0=x0)
  print(side,seed,best[0],flush=True)
  if best[0]['score']<1e-10:break
 q=np.array(best[0]['q']);records.append(dict(side=side,**best[0]))
ch.d.qpos[:]=q;mujoco.mj_forward(m,ch.d);hits,mins,audit=rt.f.contacts(ch,q)
out=dict(config=c,q=q.tolist(),arms=records,pass_=not hits,hits=hits,min_clearance=mins,elapsed_s=time.monotonic()-t0)
rt.write('park_full.json',out);rt.write('parking_probe.json',dict(config=c,best=dict(q=q.tolist(),ok=not hits)))
rt.write('park_full_iteration_'+str(time.time_ns())+'.json',out)
print('FINAL full scene park',not hits,'hits',len(hits),flush=True)
