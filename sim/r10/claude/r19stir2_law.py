"""R19 #40: time-law helpers shared by r19stir2_join.py and r19stir2_retime.py. New file.

The same method as r19stir_cycle.py (TOPP by reachability analysis in closed form, r19smooth.timelaw erosion and
moving-average filter W, local slow-downs until every limit holds on the 2 ms grid), generalized in two ways:
 - any number of path coordinates (the join moves the cart and the 6 arm joints: 7 columns);
 - an optional per-coordinate JERK limit J (|d3q/dt3| <= J on the 2 ms grid). A jerk ratio r > 1 slows the law down
   locally like the speed / acceleration ratios do: x = s'^2 is capped by (0.98 / r)^(2/3) there (jerk ~ s'^3).
Nothing here changes a geometry: a time law never needs a new collision check (R19_SMOOTH.md)."""
import math
import numpy as np
from types import SimpleNamespace as NS
from r19stir_cycle import topp   # closed-form TOPP-RA for per-coordinate |q' s'| <= V, |q' s'' + q'' s'^2| <= A
class PathN:
 """C2 composite path q(s) with n columns: consecutive segments (callable sp(x, nu), local a, b); periodic if per"""
 def __init__(self,segs,n,per=False):
  self.segs=segs;self.n=n;self.B=np.r_[0,np.cumsum([b-a for sp,a,b in segs])];self.L=float(self.B[-1]);self.per=per
 def __call__(self,s,nu=0):
  s=np.atleast_1d(np.asarray(s,float))
  if self.per:
   r=np.mod(s,self.L);r=np.where((r<1e-12)&(s>1e-12),self.L,r);s=r
  else:s=np.clip(s,0,self.L)
  k=np.clip(np.searchsorted(self.B,s,side='right')-1,0,len(self.segs)-1);out=np.zeros((len(s),self.n))
  for j in np.unique(k):
   sp,a,b=self.segs[j];m=k==j;out[m]=sp(a+s[m]-self.B[j],nu)
  return out
def grid(path,ds=.002,reps=1):
 g=[]
 for r in range(reps):
  for j,(sp,a,b) in enumerate(path.segs):
   n=max(4,int(math.ceil((b-a)/ds)));g.append(r*path.L+path.B[j]+np.linspace(0,b-a,n+1)[:-1])
 g.append([reps*path.L]);return np.concatenate(g)
def verify(path,t,s,sd,V,A,capf,J=None):
 """speed / acceleration / jerk per coordinate and s' against its cap on the time grid: ratios per sample, peaks"""
 H=t[1]-t[0];sdd=np.gradient(sd,H);sddd=np.gradient(sdd,H)
 q1,q2,q3=path(s,1),path(s,2),path(s,3)
 v=q1*sd[:,None];a=q2*sd[:,None]**2+q1*sdd[:,None];j=q3*sd[:,None]**3+3*q2*(sd*sdd)[:,None]+q1*sddd[:,None]
 rat=dict(v=np.max(np.abs(v)/V,axis=1),a=np.max(np.abs(a)/A,axis=1),cap=sd/np.sqrt(capf(s)))
 if J is not None:rat['j']=np.max(np.abs(j)/J,axis=1)
 return rat,dict(v=np.abs(v).max(0),a=np.abs(a).max(0),j=np.abs(j).max(0),j_geometric=np.abs(q3*sd[:,None]**3).max(0))
EXP=dict(v=2.,a=1.,cap=2.,j=2./3.)
def timelaw(path,V,A,capf,x0=0.,xN=0.,W=.1,reps=1,iters=40,J=None):
 """TOPP + r19smooth.timelaw (erosion + moving-average filter W, 2 ms grid) + local slow-downs until every limit
 (and the jerk limit J if given) holds on the 2 ms grid -> dict(t, s, sd, worst ratios, peaks); as
 r19stir_cycle.timelaw (identical for J=None and 6 columns)"""
 import r19smooth as S
 sg=grid(path,reps=reps);qp,qpp=path(sg,1),path(sg,2);cap=capf(sg);kap=np.ones(len(sg));seg=NS(N=len(sg)-1,s=sg,dsv=np.diff(sg),path=NS(L=float(sg[-1])))
 for it in range(iters):
  x,_=topp(sg,qp,qpp,V,A*kap[:,None],cap*kap,x0,xN);t,s,sd=S.timelaw(seg,x,W);rat,pk=verify(path,t,s,sd,V,A,capf,J)
  worst={k_:float(v_.max()) for k_,v_ in rat.items()}
  if max(worst.values())<=1+1e-3:break
  need=np.ones(len(s))
  for k_,v_ in rat.items():need=np.minimum(need,np.where(v_>1,(.98/np.maximum(v_,1e-9))**EXP[k_],1.))
  idx=np.nonzero(need<1)[0];kn=kap.copy()
  for s_,n_,sd_ in zip(s[idx],need[idx],sd[idx]):
   sel=np.abs(sg-s_)<=sd_*W+.01;kn[sel]=np.minimum(kn[sel],kap[sel]*n_)
  kap=np.maximum(kn,1e-4)
  if reps>1:   # periodic geometry: the same slow-downs in every unrolled cycle, so the middle cycle is exactly periodic
   n_=(len(sg)-1)//reps;km=kap[:-1].reshape(reps,n_).min(0);kap[:-1]=np.tile(km,reps);kap[-1]=km[0]
 return dict(t=t,s=s,sd=sd,worst={k_:round(v_,4) for k_,v_ in worst.items()},peaks=pk,iters=it+1,kappa_min=float(kap.min()),converged=max(worst.values())<=1+1e-3)
