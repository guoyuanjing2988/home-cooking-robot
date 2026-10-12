"""Vectorised conservative AABBs; original-shape narrowphase is unchanged."""
import numpy as np,mujoco
def install():
 import distance
 original=distance.Bounds.check
 # Keep original GJK and full category/pair accounting; cache support AABBs as
 # vectorized enclosing boxes (rotating a mesh local AABB is conservative).
 old_support=distance.Bounds.support
 def support(self,g,direction):
  return old_support(self,g,direction)
 # Accelerating check without changing semantics: precompute all six support
 # queries by vectorising boxes; meshes and curved primitives use exact support.
 def check(self,allowed=frozenset()):
  if not hasattr(self,'_box_ids'):self._box_ids=set(np.flatnonzero(self.m.geom_type==mujoco.mjtGeom.mjGEOM_BOX).tolist())
  m,d=self.m,self.d;self._aabb_box={}
  ids=np.array(sorted(self._box_ids),int);ext=np.einsum('gij,gj->gi',abs(d.geom_xmat[ids].reshape(-1,3,3)),m.geom_size[ids])
  for g,e in zip(ids,ext):self._aabb_box[int(g)]=(d.geom_xpos[g]-e,d.geom_xpos[g]+e)
  return original(self,allowed)
 def cached_support(self,g,direction):
  a=getattr(self,'_aabb_box',{}).get(g)
  if a is not None and np.count_nonzero(direction)==1 and np.max(abs(direction))==1:
   k=int(np.argmax(abs(direction)));r=self.d.geom_xpos[g].copy();r[k]=a[0 if direction[k]<0 else 1][k];return r
  return old_support(self,g,direction)
 # The narrowphase needs the real support point, not an AABB pseudo-point.
 old_pair=distance.Bounds.pair
 def pair(self,*args,**kwargs):
  cache=getattr(self,'_aabb_box',{});self._aabb_box={}
  try:return old_pair(self,*args,**kwargs)
  finally:self._aabb_box=cache
 distance.Bounds.check=check;distance.Bounds.support=cached_support;distance.Bounds.pair=pair
