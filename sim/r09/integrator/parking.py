"""Find compact folded posture, certify idle sweeps, and plan floor paths.

Floor routes are prospective until the arm fold/unfold and ownership chain pass.
All moving-base paths keep the arm frozen and inside the cart carry envelope.
"""
import time,heapq,math
import numpy as np,mujoco
from scipy.optimize import differential_evolution
from scene import build,load,save,H
from checker import Checker
from planner import carry_clear,plan,edge
from mobile import floor_check
def find_park():
 cfg=load('results/selected.json')['config'];tree,meta=build(cfg);ch=Checker(tree,meta);m,d=ch.m,ch.d
 q=m.qpos0.copy();q[:3]=[2.25,-.45,0];q[-2:]=.015
 gs=[g for g,n in enumerate(ch.gnames) if ch.robot[g]]
 def score(x):
  q[ch.arm_ids]=x;d.qpos[:]=q;mujoco.mj_forward(m,d)
  penalty=0.
  for c in d.contact[:d.ncon]:
   a,b=map(int,c.geom);req=ch.required(ch,a,b)
   if req is not None:penalty+=max(0,req[0]+.015-c.dist)*100
  ext=[]
  for g in gs:
   if ch.m.geom(g).name.startswith('R_cart_'):continue
   p=d.geom_xpos[g];r=m.geom_rbound[g]
   # Conservative enclosing spheres used only as optimization objective.
   penalty+=max(0,abs(p[0]-q[0])+r-.29)*5+max(0,abs(p[1]-q[1])+r-.24)*5
   ext.append(p[2]+r)
  return penalty+max(ext)*.02
 rows=[];best=None
 for seed in [19,20,21,22]:
  bounds=m.jnt_range[ch.arm_ids].copy()
  # A narrow upright extended arm is not a folded parking result. Search both
  # elbow-fold branches explicitly, with at least1.6rad elbow bending.
  bounds[2]=[1.6,2.792526803190927] if seed%2 else [-2.792526803190927,-1.6]
  r=differential_evolution(score,bounds,seed=seed,popsize=10,maxiter=120,polish=True,tol=1e-6)
  q[ch.arm_ids]=r.x;result=ch.check(q);carry=carry_clear(ch,q)
  rows.append(dict(seed=seed,objective=float(r.fun),q=q.tolist(),check=result,carry_clear=carry))
  if best is None or (result['ok'] and carry and not(best['check']['ok'] and best['carry_clear'])) or r.fun<best['objective'] and result['ok']==best['check']['ok']:best=rows[-1]
 bounds=[];sweep_min=1e6;walkway_clear=True
 for g in gs:
  ch.d.qpos[:]=best['q'];mujoco.mj_forward(m,d)
  lo=np.array([ch.bounds.support(g,-a)[k] for k,a in enumerate(np.eye(3))]);hi=np.array([ch.bounds.support(g,a)[k] for k,a in enumerate(np.eye(3))])
  # All upper/lower/oven sweeps remain within x<=1.80 in this reference
  # kitchen. Separating by X is a certificate independent of opening angle.
  gap=lo[0]-1.8;sweep_min=min(sweep_min,gap)
  if lo[0]<1.81 and hi[1]>-.90 and lo[1]<0:walkway_clear=False
  bounds.append(dict(name=ch.gnames[g],aabb_m=[lo.tolist(),hi.tolist()],door_sweep_separation_m=float(gap)))
 save('assets/park_mobile.json',dict(q=best['q']))
 save('results/park_search.json',dict(rows=rows,best=best,folded=abs(best['q'][5])>=1.6,robot_bounds=bounds,door_sweep_separation_m=float(sweep_min),walkway_clear=walkway_clear,site_assumption='one-metre clear right-end alcove beyond x=1.8; absent from photos; installation conditional'))
 print('park',best['check']['ok'],'carry',best['carry_clear'],'sweep',sweep_min,flush=True)
def floor_route(ch,start,goal,budget_s=65,mass=0):
 assert budget_s>=60
 beg=time.monotonic();deadline=beg+budget_s;start=np.array(start);goal=np.array(goal)
 # A* grid at fixed yaw0; four-neighbour differential-drive straight legs.
 # Grid is a proposal; final swept footprint and cable replay is <=4mm.
 if np.max(abs(start[3:]-goal[3:]))>1e-10:return dict(ok=False,reason='carry_posture_mismatch',budget_s=budget_s)
 # Cubic Hermite XY proposals impose dy/dx=tan(yaw) at both docks. The
 # nonholonomic residual of every accepted small chord is checked by edge().
 dx=goal[0]-start[0];paths=[]
 if abs(dx)>.05 and carry_clear(ch,start) and carry_clear(ch,goal):
  seq=[]
  for s in np.linspace(0,1,max(3,int(abs(dx)/.002)+1)):
   a0=2*s**3-3*s*s+1;a1=s**3-2*s*s+s;b0=-2*s**3+3*s*s;b1=s**3-s*s
   y=a0*start[1]+a1*dx*np.tan(start[2])+b0*goal[1]+b1*dx*np.tan(goal[2])
   dy=(6*s*s-6*s)*start[1]+(3*s*s-4*s+1)*dx*np.tan(start[2])+(-6*s*s+6*s)*goal[1]+(3*s*s-2*s)*dx*np.tan(goal[2])
   q=start.copy();q[:3]=[start[0]+dx*s,y,np.arctan(dy/dx)];seq.append(q)
  valid=True;clear=[];maxstep=0
  for a,b in zip(seq[:-1],seq[1:]):
   er=edge(ch,a,b,deadline,mass=mass)
   if not er['ok']:valid=False;break
   paths+=er['path'][:-1];clear+=er['clearance'][:-1];maxstep=max(maxstep,er['step_bound_m'])
  if valid:return dict(ok=True,path=paths+[goal.tolist()],clearance=clear,step_bound_m=maxstep,budget_s=budget_s,elapsed_s=time.monotonic()-beg,method='nonholonomic Hermite carry route; full footprint+cable+arm replay')
 direct=edge(ch,start,goal,deadline,mass=mass)
 if direct['ok']:return dict(**direct,budget_s=budget_s,elapsed_s=time.monotonic()-beg,method='straight carry drive with full bounded replay')
 # RRT restarts/staging/shortcuts supply the required finite search budget;
 # only base DOFs are active, arm remains literally frozen.
 prior=ch.active;ch.active=ch.base_ids
 try:r=plan(ch,start,goal,max(60,budget_s-(time.monotonic()-beg)),stages=[(start+goal)/2],seed=901,mass=mass)
 finally:ch.active=prior
 return r
def idle():
 cfg=load('results/selected.json')['config'];t,meta=build(cfg);ch=Checker(t,meta);park=np.array(load('assets/park_mobile.json')['q'])
 a=load('results/strokes/0.json');b=load('results/strokes/10.json')
 from execute import diagnostic_q
 first=diagnostic_q(a['endpoints'][0]);last=diagnostic_q(b['endpoints'][-1]);foldgoal=park.copy();foldgoal[:3]=last[:3]
 ch.active=ch.arm_ids
 fold=plan(ch,last,foldgoal,65,stages=[foldgoal],seed=912)
 drive=floor_route(ch,foldgoal,park)
 startcarry=park.copy();startcarry[:3]=first[:3]
 unfold_drive=floor_route(ch,park,startcarry)
 unfold=plan(ch,startcarry,first,65,stages=[startcarry],seed=913)
 ps=load('results/park_search.json')
 save('results/idle.json',dict(pass_=False,snapshot_pass=bool(ps['best']['check']['ok'] and ps['door_sweep_separation_m']>=.01 and ps['walkway_clear']),park_q=park.tolist(),park_search='results/park_search.json',fold=fold,drive_to_park=drive,drive_from_park=unfold_drive,unfold=unfold,reason='No connected carrot ownership/execution chain; routes are prospective only',site_conditional=True))
 print('idle diagnostics complete',flush=True)
if __name__=='__main__':
 import sys
 (find_park if sys.argv[1]=='search' else idle)()
