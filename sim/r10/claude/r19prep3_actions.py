"""R19 prep audit step 3 (GitHub #38): keyframes of the basket, soak-tub and output-transfer sets, run by
r19prepchain.py (ACT=basket|baspour|tubfill|soak|tubempty|ctray|bascarrot) with its unchanged method. New file.
Objects and the prep-time layout: kitchen19p3.py. Every dwell (rinse, drain, fill, soak, pour) is an ESTIMATE.

Prep-time layout (R19_PREP_STEP3.md): the work spot of kitchen19.LAYOUT holds one fetched item at a time (lever
base | cold box | soak set). The soak set is the tub at TUBP (back half of the work spot, under the cabinet front
plane) with the wash basket nested in it when idle, plus the basket's front spot FRONTP (used only while the tub
is filled, emptied or soaking). The staging bowl for cooking stands on the T1 strip behind the plating spots
(the R19 cups plan's T1), knob toward the sink.
Extra keyframe keys read by r19prepchain.load(): load = kg held at that keyframe, com = its CoM (object frame)."""
import numpy as np
import kitchen16 as K,kitchen19 as K19,kitchen19p3 as P3
TUBP=dict(x=-0.86,y=.40,yaw=-20.);FRONTP=dict(x=-0.86,y=.15,yaw=-90.);T1B=dict(x=.30,y=.38,yaw=180.)
BYAW=-90.            # the basket's handle points at the robot (grasp approach toward the wall) wherever it is: one arm posture, the cart follows
FOOD_KG=.50          # [est] the largest basket load in meals A/B/C (500 g soup ribs, B; broccoli 400 g, A; R19_PREP_AUDIT 2.1-2.3)
RINSE_WATER=.30      # [est] water standing in the basket under the running tap (drain holes; R19_PREP_STEP3.md 4)
WET=.05              # [est] water film on drained produce
COM_B=np.array([0,0,.04]);COM_T=np.array([0,0,.03])   # [est] CoM of basket + food, of tub + water (object frame)
ACTS=('basket','baspour','tubfill','soak','tubempty','ctray','bascarrot')
def tub_pose():return K.Rz(TUBP['yaw']),np.array([TUBP['x'],TUBP['y'],K19.COUNTER_TOP])
def nest_pose():return K.Rz(BYAW),np.array([TUBP['x'],TUBP['y'],K19.COUNTER_TOP+P3.TUB['t']])
def front_pose():return K.Rz(FRONTP['yaw']),np.array([FRONTP['x'],FRONTP['y'],K19.COUNTER_TOP])
def t1_pose():return K.Rz(T1B['yaw']),np.array([T1B['x'],T1B['y'],K19.COUNTER_TOP])
def tub_water_kg():return P3.water_kg(P3.TUB['R']-P3.TUB['t'],P3.TUB['water_h'])
def V(KV,key,default):return np.array([float(v) for v in KV.get(key,default).split(',')])
def action(ACT,KV,L,kf,scene_with,tray_objs):
 """(object, scene extras, keyframes, grasp list) for a step-3 set; kf is r19prepchain.kf."""
 FO=K19.FAUCET_OUT;car,tom=tray_objs;RINSE=float(KV.get('RINSE',3.));DRAIN=float(KV.get('DRAIN',4.))
 def K_(R,p,c,dw=0.,label='',load=None,com=None,**kw):
  k=kf(R,p,c,dw,label,**kw);k['load']=load;k['com']=com;return k
 Rt,pt=tub_pose();Rn,pn=nest_pose();Rf,pf=front_pose();Rb1,pb1=t1_pose()
 tub=('tub',Rt,pt);bowl=('bowl',Rb1,pb1);bas_front=('basket',Rf,pf)
 dry=P3.MASS_EST['basket']+FOOD_KG;wet=dry+WET;rin=dry+RINSE_WATER
 lane=V(KV,'BLANE','-0.62,.30,.98')                                       # basket / tub floor centre in the lane by the sink
 TAP=np.array([FO[0],float(KV.get('TAPY',.30)),float(KV.get('TAPZ',.94))])   # basket floor centre under the outlet (rim 6 cm under the spout)
 if ACT=='basket':   # BASKET_WASH: out of the tub -> under the running tap (3 rinse dwells) -> drain + shake -> back into the tub
  D=TAP+[0,-.06,.04];up=pn+[0,0,.11]
  KF=[K_(Rn,pn+[0,0,.008],'A',0,'pick (nested in the tub)',dry,COM_B,anchor=True,seat=.008),K_(Rn,pn+[0,0,.05],'A',0,'lifted',dry,COM_B),
   K_(Rn,up,'A',0,'out of the tub',dry,COM_B),K_(Rn,lane,'F',0,'lane',dry,COM_B,meet=True),
   K_(Rn,TAP,'F',RINSE,'under the tap',rin,COM_B,anchor=True),K_(Rn,TAP+[.04,.02,0],'F',RINSE,'rinse, right',rin,COM_B),
   K_(Rn,TAP+[-.04,.02,0],'F',RINSE,'rinse, left',rin,COM_B),K_(Rn,TAP,'F',0,'centre',rin,COM_B),
   K_(Rn,D,'F',DRAIN,'drain (out of the stream)',rin,COM_B)]
  for i in range(3):KF+=[K_(Rn,D-[0,0,.015],'A',0,f'shake {i+1} down',wet,COM_B),K_(Rn,D,'A',0,f'shake {i+1} up',wet,COM_B)]
  KF+=[K_(Rn,lane,'F',0,'lane',wet,COM_B,meet=True),K_(Rn,up,'F',0,'over the tub',wet,COM_B,anchor=True),
   K_(Rn,pn+[0,0,.05],'A',0,'lowered',wet,COM_B),K_(Rn,pn+[0,0,.008],'A',0,'in the tub (8 mm)',wet,COM_B,seat=.008)]
  w=scene_with(objs=[car,tom,tub]);return 'basket',dict(r19=w),KF,[(0,w,True),(len(KF)-1,w,True)]
 if ACT=='baspour':  # BASKET_POUR: out of the tub -> over the staging bowl on T1 -> rolled POURDEG about the handle (dwell, shake) -> back
  yb=float(KV.get('PYAW',-90.));Rp=K.Rz(yb);deg=float(KV.get('POURDEG',130.));kz=float(KV.get('PKZ',.14))
  kn=pb1+[0,0,P3.BOWL['H']+kz]+Rp@np.array([K.OBJ['basket']['grip'][0],0,0]);Rl,pl=P3.at_knob('basket',Rp,kn);Rr,pr=P3.rolled_about_knob('basket',Rl,pl,deg)
  Rm=K.Rz(float(KV.get('MYAW',(BYAW+yb)/2)));l1=lane;l2=V(KV,'PLANE','0.0,.15,1.06')
  up=pn+[0,0,.11];empty=P3.MASS_EST['basket']+.02
  KF=[K_(Rn,pn+[0,0,.008],'A',0,'pick (nested in the tub)',wet,COM_B,anchor=True,seat=.008),K_(Rn,pn+[0,0,.05],'A',0,'lifted',wet,COM_B),
   K_(Rn,up,'A',0,'out of the tub',wet,COM_B),K_(Rn,l1,'F',0,'lane by the sink',wet,COM_B),K_(Rm,l2,'F',0,'lane right of the sink',wet,COM_B,meet=True),
   K_(Rl,pl,'F',0,'over the staging bowl',wet,COM_B,anchor=True),K_(Rr,pr,'A',float(KV.get('POUR',2.)),f'rolled {deg:g} (pour)',wet,COM_B),
   K_(Rr,pr+[0,0,.015],'A',0,'shake up',empty,COM_B),K_(Rr,pr,'A',0,'shake down',empty,COM_B),K_(Rl,pl,'A',0,'level again',empty,COM_B),
   K_(Rm,l2,'F',0,'lane right of the sink',empty,COM_B,meet=True),K_(Rn,l1,'F',0,'lane by the sink',empty,COM_B),
   K_(Rn,up,'F',0,'over the tub',empty,COM_B,anchor=True),K_(Rn,pn+[0,0,.05],'A',0,'lowered',empty,COM_B),
   K_(Rn,pn+[0,0,.008],'A',0,'in the tub (8 mm)',empty,COM_B,seat=.008)]
  w=scene_with(objs=[car,tom,tub,bowl]);return 'basket',dict(r19=w),KF,[(0,w,True),(len(KF)-1,w,True)]
 if ACT=='tubfill':  # SOAK 1: the empty tub from its spot -> under the running tap (FILL s) -> back, full
  full=P3.MASS_EST['tub']+tub_water_kg();e=P3.MASS_EST['tub'];TT=np.array([FO[0],float(KV.get('TTAPY',.31)),float(KV.get('TTAPZ',.95))]);tl=lane+[0,0,-.01]
  KF=[K_(Rt,pt+[0,0,.008],'A',0,'pick',e,COM_T,anchor=True,seat=.008),K_(Rt,pt+[0,0,.04],'A',0,'lifted',e,COM_T),K_(Rt,tl,'F',0,'lane',e,COM_T,meet=True),
   K_(Rt,TT,'F',float(KV.get('FILL',27.)),'under the tap (filling)',full,COM_T,anchor=True),K_(Rt,TT+[0,-.06,.02],'F',0,'out of the stream',full,COM_T),
   K_(Rt,tl,'F',0,'lane',full,COM_T,meet=True),K_(Rt,pt+[0,0,.04],'F',0,'over its spot',full,COM_T,anchor=True),
   K_(Rt,pt+[0,0,.008],'A',0,'set down (8 mm)',full,COM_T,seat=.008)]
  w=scene_with(objs=[car,tom,bas_front]);return 'tub',dict(r19=w),KF,[(0,w,True),(len(KF)-1,w,True)]
 if ACT=='soak':     # SOAK 2: the basket from the front spot -> into the filled tub (SOAK s; release / regrasp checked) -> lifted, drained -> back
  mid=V(KV,'SLANE',f"{(pf[0]+pn[0])/2+.06},{(pf[1]+pn[1])/2},.97");upn=pn+[0,0,.12];upf=pf+[0,0,.06]
  KF=[K_(Rf,pf+[0,0,.008],'A',0,'pick (front spot)',dry,COM_B,anchor=True,seat=.008),K_(Rf,pf+[0,0,.05],'A',0,'lifted',dry,COM_B),
   K_(Rf,pf+[0,0,.12],'A',0,'up',dry,COM_B),K_(Rn,mid,'F',0,'lane',dry,COM_B,meet=True),K_(Rn,upn,'F',0,'over the tub',dry,COM_B,anchor=True),
   K_(Rn,pn+[0,0,.05],'A',0,'lowering into the water',dry,COM_B),
   K_(Rn,pn+[0,0,.008],'A',float(KV.get('SOAK',10.)),'in the tub, soaking (8 mm)',dry,COM_B,seat=.008),
   K_(Rn,pn+[0,0,.09],'A',DRAIN,'lifted out, draining over the tub',rin,COM_B),K_(Rn,mid,'F',0,'lane',wet,COM_B,meet=True),
   K_(Rf,upf,'F',0,'over the front spot',wet,COM_B,anchor=True),K_(Rf,pf+[0,0,.008],'A',0,'set down (8 mm)',wet,COM_B,seat=.008)]
  w=scene_with(objs=[car,tom,tub]);return 'basket',dict(r19=w),KF,[(0,w,True),(6,w,True),(len(KF)-1,w,True)]
 if ACT=='tubempty': # SOAK 3: the full tub from its spot -> over the sink -> rolled EDEG about its handle (emptied) -> back, empty
  full=P3.MASS_EST['tub']+tub_water_kg();e=P3.MASS_EST['tub'];tl=lane+[0,0,-.01]
  E=np.array([FO[0]+float(KV.get('EDX',-.02)),float(KV.get('EY',.27)),float(KV.get('EZ',.95))]);Re,pe_=P3.rolled_about_knob('tub',Rt,E,float(KV.get('EDEG',-120.)))
  KF=[K_(Rt,pt+[0,0,.008],'A',0,'pick (full)',full,COM_T,anchor=True,seat=.008),K_(Rt,pt+[0,0,.04],'A',0,'lifted',full,COM_T),K_(Rt,tl,'F',0,'lane',full,COM_T,meet=True),
   K_(Rt,E,'F',0,'over the sink',full,COM_T,anchor=True),K_(Re,pe_,'A',float(KV.get('EMPTY',3.)),'rolled (emptied into the sink)',full,COM_T),
   K_(Rt,E,'A',0,'level again',e,COM_T),K_(Rt,tl,'F',0,'lane',e,COM_T,meet=True),K_(Rt,pt+[0,0,.04],'F',0,'over its spot',e,COM_T,anchor=True),
   K_(Rt,pt+[0,0,.008],'A',0,'set down (8 mm)',e,COM_T,seat=.008)]
  w=scene_with(objs=[car,tom,bas_front]);return 'tub',dict(r19=w),KF,[(0,w,True),(len(KF)-1,w,True)]
 if ACT=='ctray':    # OUTPUT_XFER: the lever's catch tray (cut pieces) pulled out -> over the staging bowl on T1 -> rolled -> back, slid in
  lx,ly,_=L['lever'];I=np.eye(3);s0=np.array([lx,ly,.862]);o=s0+[0,-.15,.008];hi=s0+[0,-.15,.11];kg=P3.MASS_EST['ctray']+float(KV.get('PIECES',.15));e=P3.MASS_EST['ctray']
  kn=pb1+[0,-float(KV.get('CDY',.10)),P3.BOWL['H']+float(KV.get('CKZ',.10))];Rl,pl=P3.at_knob('ctray',I,kn);Rr,pr=P3.rolled_about_knob('ctray',Rl,pl,float(KV.get('CDEG',-120.)))
  l1=V(KV,'CLANE1','-0.40,.08,1.08');l2=V(KV,'CLANE2','0.05,.15,1.06')
  KF=[K_(I,s0+[0,0,.008],'A',0,'pick (seated under the blade plate)',kg,None,anchor=True,seat=.008),K_(I,o,'A',0,'pulled out 15 cm',kg,None),K_(I,hi,'A',0,'lifted',kg,None),
   K_(I,l1,'F',0,'lane',kg,None,meet=True),K_(I,l2,'F',0,'lane right of the sink',kg,None),K_(Rl,pl,'F',0,'over the staging bowl',kg,None,anchor=True),
   K_(Rr,pr,'A',float(KV.get('POUR',2.)),'rolled (pour)',kg,None),K_(Rl,pl,'A',0,'level again',e,None),
   K_(I,l2,'F',0,'lane right of the sink',e,None,meet=True),K_(I,l1,'F',0,'lane',e,None),
   K_(I,hi,'F',0,'in front of the lever base',e,None,anchor=True),K_(I,o,'A',0,'lowered',e,None),K_(I,s0+[0,0,.008],'A',0,'slid in (8 mm)',e,None,seat=.008)]
  w=scene_with('lever',objs=[car,tom,bowl]);return 'ctray',dict(r19=w),KF,[(0,w,True),(len(KF)-1,w,True)]
 if ACT=='bascarrot':  # PIECE INTO THE BASKET: carrot off the rib tray -> upright over the basket on the front spot -> lowered -> released
  c0=K19.tray('carrot',L['tray_dxy']);cy=float(KV.get('BCAPP',30.));Rv=K.Rz(cy)@K.Ry(90);rim=K19.COUNTER_TOP+P3.BASKET['H']
  bc=pf+Rf@np.array([float(v) for v in KV.get('BOFF','0,0').split(',')]+[0.]);lnc=V(KV,'CLANE','-1.05,.06,1.12')
  KF=[kf(np.eye(3),c0+[0,0,.008],'A',0,'pick',anchor=True,seat=.008),kf(np.eye(3),c0+[0,0,.05],'A',0,'lifted'),kf(np.eye(3),c0+[0,-.04,.15],'F',0,'out and up'),
   kf(np.eye(3),lnc,'F',0,'lane',meet=True),kf(Rv,bc+V(KV,'BCUP','.05,-.087,.20')+[0,0,rim-K19.COUNTER_TOP],'F',0,'upright, in front of the basket'),
   kf(Rv,[bc[0],bc[1],rim-.02+K19.CARROT_HL+.08],'F',0,'over the basket',anchor=True),kf(Rv,[bc[0],bc[1],rim-.02+K19.CARROT_HL],'A',0,'in the basket (bottom 20 mm under the rim)')]
  w0=scene_with(objs=[tom,('basket_open',Rf,pf)]);return 'carrot',dict(r19=w0),KF,[(0,w0,True),(len(KF)-1,w0,False)]
 raise KeyError(ACT)
