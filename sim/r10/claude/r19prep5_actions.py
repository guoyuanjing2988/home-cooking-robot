"""R19 prep step 5 (GitHub #38, R19_PREP_T2L.md): keyframes of the fold-away T2L cradle sets (kitchen19p5.py), run by
r19prep5_chain.py (a copy of r19prep4chain.py). Every dwell is an ESTIMATE; the hinge (pin, bushes, end stops, detent) is
NOT modelled (it sits in the 12 mm gap between the leaf and the fixed bar, as the R17 faucet lever's hub).
ACT=fold    the leaf gripped by its knob at the deployed pose (cart fixed at FC), turned FOLD_DEG about the pin in
            STEP-degree keyframes (the leaf frame sits on the pin, so each keyframe is a pure rotation about it), released
            folded. PAN=1: the staging pan rides on the leaf (swing kind only).
ACT=unfold  the same, folded -> deployed.
Grasp entries (keyframe, cfg overrides {r19, r19p5}, 'cart'): the leaf is a CART part (kitchen19p5) at the approach / retreat,
the gripper approaches the knob along its approach axis (top knob: straight down) <= 50 mm with the jaws open."""
import numpy as np
import kitchen16 as K,kitchen19 as K19,kitchen19p4 as P4,kitchen19p5 as P5
ACTS=('fold','unfold','ct2s')
FOOD_ACTS=('fold','unfold','ct2s')   # sets that carry food: r19prep5_chain.py applies the cups' food join rule to them (as r19prep4 sets)
INFO={}
FOOD_STG=.40   # [est] as r19prep4_actions: cut food for one wok dish staged in the pan
def leaf_load(kind,knob,pan,food):
 """(kg, CoM in the leaf frame): leaf (+ pan + food), all of it carried by the arm in the sim (conservative: the pin carries
 the weight in reality, the gripper only the turning torque)."""
 parts=P5.leaf_parts(kind,None,knob,False);vol=lambda h:8*h[0]*h[1]*h[2]
 c=sum(vol(h)*np.asarray(q) for n,t,q,h,R in parts)/sum(vol(h) for n,t,q,h,R in parts);m=P5.MASS_EST['leaf'];com=m*c
 if pan:
  mp,cp=P4.stg_mass(food);Rl,pl=P4.t2l_local();o=pl-P5.hinge_local();com=com+mp*(Rl@cp+o);m+=mp
 return m,com/m
def action(ACT,KV,L,kf,scene_with,tray_objs):
 car,tom=tray_objs
 def K_(R,p,c,dw=0.,label='',load=None,com=None,**kw):
  k=kf(R,p,c,dw,label,**kw);k['load']=load;k['com']=com;return k
 if ACT=='ct2s':   # complete-flow candidate: the lever catch tray (step-3 ctray route) poured into the staging pan riding on the
  # FOLDED swing cradle (prep time, cooker off: PLUME=0); keyframes as r19prep4_actions ct2p, target = the pan on the leaf at FANG deg
  import kitchen19p3 as P3,r19prep4_actions as A4
  V=lambda key,d:np.array([float(v) for v in KV.get(key,d).split(',')])
  lx,ly,_=L['lever'];I=np.eye(3);s0=np.array([lx,ly,.862]);sl=float(KV.get('CSLIDE',.018));r0=s0+[0,0,sl];o=s0+[0,-.15,sl];hi=s0+[0,-.15,.11]
  kg=P3.MASS_EST['ctray']+A4.FOOD_CT;e=P3.MASS_EST['ctray'];deg=float(KV.get('CDEG',120.));mz=float(KV.get('MOUTHZ',.10))
  ang=float(KV.get('FANG',90.));CP=float(KV.get('CP',-.52))
  Rf,pf=P5.leaf_pose_world('swing',ang,CP);Rt,pt=P4.t2l_local();pan=Rf@(pt-P5.hinge_local())+pf   # pan bottom centre (world) at cart CP
  (Rl,pl),(Rr,pr)=A4.mouth_pose('ctray',I,pan+[0,0,P4.STG_H+mz],deg)
  ln=V('CLANE',','.join(str(round(v,3)) for v in (hi+pl)/2+[0,0,.04]));lc=float(KV['LANEC']) if 'LANEC' in KV else 'F'
  KF=[K_(I,s0+[0,0,.008],'A',0,'pick (seated under the blade plate)',kg,None,anchor=True,seat=.008),K_(I,r0,'A',0,'raised 18 mm',kg,None),K_(I,o,'A',0,'pulled out 15 cm',kg,None),K_(I,hi,'A',0,'lifted',kg,None),
   K_(I,ln,lc,0,'lane',kg,None,meet=True),K_(Rl,pl,CP,0,'over the pan on the folded cradle',kg,None,anchor=True),
   K_(Rr,pr,CP,float(KV.get('POUR',2.)),f'rolled {deg:g} (pour)',kg,None),K_(Rl,pl,CP,0,'level again',e,None),
   K_(I,ln,lc,0,'lane',e,None,meet=True),
   K_(I,hi,'F',0,'in front of the lever base',e,None,anchor=True),K_(I,o,'A',0,'lowered',e,None),K_(I,r0,'A',0,'slid in (18 mm)',e,None),K_(I,s0+[0,0,.008],'A',0,'set down (8 mm)',e,None,seat=.008)]
  p5=dict(kind='swing',knob='top',state='folded',angle=ang,pan=True);w=dict(r19=scene_with('lever',objs=[car,tom]),r19p5=p5)
  INFO[ACT]=dict(fold_angle=ang,pour_cart=CP,pan_bottom_world=pan.tolist(),pour_deg=deg,mouth_over_pan_rim_m=mz,food_kg_est=A4.FOOD_CT,lane=ln.tolist(),note='prep time (cooker off): run with PLUME=0')
  return 'ctray',w,KF,[(0,w,True),(len(KF)-1,w,True)]
 kind=KV.get('KIND','swing');knob=KV.get('KNOB','top');pan=KV.get('PAN','0')=='1';food=float(KV.get('FOOD',FOOD_STG if pan else 0.))
 fd=float(KV.get('FOLD_DEG',P5.FOLD_DEG[kind]));st=float(KV.get('STEP',15.));C=float(KV.get('FC',.172))
 obj=P5._reg(kind,knob,None,pan);m,com=leaf_load(kind,knob,pan,food)
 n=max(1,int(np.ceil(abs(fd)/st)));angs=[fd*i/n for i in range(n+1)]
 if ACT=='unfold':angs=angs[::-1]
 KF=[]
 for i,a in enumerate(angs):
  R,p=P5.leaf_pose_world(kind,a,C)
  lab='deployed' if abs(a)<1e-9 else 'folded' if abs(a-fd)<1e-9 else f'turned {a:g}'
  KF.append(K_(R,p,C,0,lab+(' (grasp)' if i==0 else ' (release)' if i==n else ''),m,com,anchor=(i==0)))
 base=dict(kind=kind,knob=knob)
 w0=dict(r19=scene_with(objs=[car,tom]),r19p5=dict(base,state='deployed' if ACT=='fold' else 'folded',pan=pan))
 w1=dict(r19=scene_with(objs=[car,tom]),r19p5=dict(base,state='folded' if ACT=='fold' else 'deployed',pan=pan))
 sc=dict(r19=scene_with(objs=[car,tom]),r19p5=dict(base,state='held',pan=False))   # play: the leaf (+ pan) is in the gripper; only the fixed bar is a cart part
 INFO[ACT]=dict(obj=obj,kind=kind,knob=knob,pan=pan,food_kg_est=food,fold_deg=fd,step_deg=st,cart=C,load_kg=round(m,3),com_leaf_frame=np.round(com,4).tolist(),
  hinge_cart_frame=P5.hinge_local().tolist(),knob_grip_leaf_frame=P5.knob_grip(kind,None,knob).tolist())
 return obj,sc,KF,[(0,w0,'cart'),(len(KF)-1,w1,'cart')]
