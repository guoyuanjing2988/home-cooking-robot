"""Additional search objective only. Literal final gaps are unchanged."""
import numpy as np,mujoco
from search_distance_v2_r07 import hits as normal_hits
def hits(ch,q):
 out=normal_hits(ch,q)
 if not getattr(ch,'night_robust',False):return out
 import runtime_v2_r07 as v
 v.f.contacts(ch,q);b=ch.bounds;seen={frozenset(x['pair']) for x in out}
 for i,(a,bb,need,cat) in enumerate(b.pairs):
  if need<=0 or not any(ch.gnames[g].startswith(('R_','L_')) for g in (a,bb)):continue
  if b.last_lower[i]>=need+.010:continue
  names=[ch.gnames[a],ch.gnames[bb]]
  if frozenset(names) in seen:continue
  gap=float(mujoco.mj_geomDistance(ch.m,ch.d,a,bb,need+.011,None))
  if gap<need+.010:out.append(dict(pair=names,required_gap_mm=(need+.010)*1000,real_gap_mm=gap*1000,category=cat,search_objective_only=True))
 return out
