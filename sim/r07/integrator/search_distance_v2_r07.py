"""Fast full-geometry proposals only; final admission remains literal+Bounds."""
import numpy as np,mujoco

def hits(ch,q):
 import runtime_v2_r07 as v
 from policy_r05 import window_pairs
 if not hasattr(ch,'bounds'):v.f.contacts(ch,q)
 b=ch.bounds;m,d=ch.m,ch.d
 d.qpos[:]=q;mujoco.mj_kinematics(m,d);mujoco.mj_comPos(m,d);mujoco.mj_collision(m,d)
 if not hasattr(b,'proposal_local'):
  ctr=m.geom_aabb[:,:3].copy();ext=m.geom_aabb[:,3:].copy()
  for g,vs in b.local.items():ctr[g]=(vs.max(0)+vs.min(0))/2;ext[g]=(vs.max(0)-vs.min(0))/2
  b.proposal_local=(ctr,ext)
 ctr,ext=b.proposal_local;rot=d.geom_xmat.reshape(-1,3,3)
 center=d.geom_xpos+np.einsum('gij,gj->gi',rot,ctr);half=np.einsum('gij,gj->gi',abs(rot),ext)
 lo=center-half;hi=center+half
 planes=np.flatnonzero(m.geom_type==0);lo[planes]=-1e6;hi[planes]=1e6
 gap=np.linalg.norm(np.maximum(np.maximum(lo[b.aa]-hi[b.bb],lo[b.bb]-hi[b.aa]),0),axis=1)
 allowed=set(window_pairs(ch))
 for c in d.contact[:d.ncon]:
  if v.f.intentional(ch,c):allowed.add(frozenset(ch.gnames[g] for g in c.geom))
 result=[]
 for i in np.flatnonzero(gap<b.need+.003):
  a,bb,need,cat=b.pairs[i]
  if frozenset((ch.gnames[a],ch.gnames[bb])) in allowed:continue
  if m.geom_type[a]==0 or m.geom_type[bb]==0:
   dist=b.pair(a,bb)['lower_m']
  else:dist=mujoco.mj_geomDistance(m,d,a,bb,float(need+.012),None)
  if dist<need-1e-6:result.append(dict(pair=[ch.gnames[a],ch.gnames[bb]],real_gap_mm=float(dist*1000),required_gap_mm=float(need*1000)))
 return result
