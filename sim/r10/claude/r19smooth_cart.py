"""R19 smooth: is a cart acceleration above 0.15 m/s^2 safe for tipping? mobile.dock_stability (the
docked-cart model the checker uses: lateral +-.22 m, back line, bumper <= 250 N on the cabinet front;
inertial load (cart + arm + held) x a x 1.5 in every horizontal direction; moving masses x 1.5) with the
acceleration as a parameter and the HELD load included (the chains were checked with mass=0).
python r19smooth_cart.py ACT=wok [A=.15,.3,.5,.8]  -> prints the minimum margin over every stored state"""
import sys,json;sys.path.insert(0,'.')
import numpy as np,mujoco
import mobile
import r19smooth as S
def dock_stability_a(ch,q,mass,com,a):
 """mobile.dock_stability with the inertial acceleration a (m/s^2) instead of 0.15, held mass at com."""
 src=mobile.dock_stability.__code__
 m,d=ch.m,ch.d;d.qpos[:]=q;mujoco.mj_forward(m,d)
 root=m.body('rail_structure').id;ids=[]
 for b in range(1,m.nbody):
  anc=b
  while anc and anc!=root:anc=m.body_parentid[anc]
  if anc==root:ids.append(b)
 masses=m.body_mass[ids];centres=d.xipos[ids]
 moving=np.array([m.body(b).name.startswith('R_arm_') or m.body(b).name in ('R_tool','R_jaw_minus','R_jaw_plus') for b in ids])
 x,y=q[0],q[1];cases=[]
 for factor in [1.,1.5]:
  for axis in range(2):
   for direction in [-1,1]:
    eff=masses*np.where(moving,factor,1.);dm=mass*factor;W=float((eff.sum()+dm)*9.81)
    gm=np.sum(np.cross(centres,eff[:,None]*np.array([0,0,-9.81])),axis=0)+np.cross(com,[0,0,-dm*9.81])
    inertia=np.zeros(3);inertia[axis]=direction*(masses.sum()+mass)*a*factor
    avg=(np.sum(masses[:,None]*centres,axis=0)+mass*com)/(masses.sum()+mass)
    torque=gm+np.cross(avg,inertia);reaction=W
    zmp=np.array([torque[1]/reaction,-torque[0]/reaction]);lx,ly=zmp[0]-x,zmp[1]-y
    mx=.22-abs(lx);mback=ly-(-.22 if ch.meta.get('config',{}).get('deep_cart') else -.10)
    need=max(0.,reaction*(ly-.11)/mobile.BUMPER_H);limit=min(mobile.BUMPER_LIMIT_N,mobile.MU_FLOOR*W)
    mfront=(limit-need)*mobile.BUMPER_H/reaction if ly>.11 else .11-ly+limit*mobile.BUMPER_H/reaction
    cases.append(min(mx,mback,mfront))
 return min(cases),float(masses.sum()+mass)
if __name__=='__main__':
 KV=dict(a.split('=',1) for a in sys.argv[1:]);act=KV['ACT'];A=[float(v) for v in KV.get('A','.15,.3,.5,.8').split(',')]
 ctx=S.setup(act);ch=ctx['ch'];Q=S.unwrap(ctx['r']['play']);P,R=S.fk(ctx,Q);po,Ro=S.obj_pose(ctx,P,R)
 kf=S.r17_timing(ctx,Q)['kf_idx'];docked=ch.meta.get('config',{}).get('dock')
 out={}
 for a in A:
  worst=(1e9,None)
  for i,q in enumerate(Q):
   food=1.15 if (act=='wok' and i<=kf[5]) else .5 if (act=='wok' and kf[8]<=i<=kf[10]) else 0.
   M,c,_=S.load_parts(ctx,food);com=po[i]+Ro[i]@c if M>0 else np.zeros(3)
   mg,mt=dock_stability_a(ch,q,M,com,a)
   if mg<worst[0]:worst=(mg,i)
  # cross-check: the stock model (a=.15, mass 0) equals mobile.dock_stability
  out[a]=dict(min_margin_mm=round(worst[0]*1e3,1),state=worst[1])
  print(act,'docked' if docked else 'NOT docked','a=%.2f m/s^2: min margin %.1f mm at state %s (total mass %.1f kg)'%(a,worst[0]*1e3,worst[1],mt),flush=True)
 q=Q[0];ref=mobile.dock_stability(ch,q,[0,0,0],0.)['min_margin_m'];own=dock_stability_a(ch,q,0.,np.zeros(3),.15)[0]
 print('check vs mobile.dock_stability (state 0, mass 0, a .15): %.6f vs %.6f m'%(ref,own))
