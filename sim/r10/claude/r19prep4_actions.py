"""R19 prep audit step 4 (GitHub #38): keyframes of the step-4 sets, run by r19prep4chain.py (a copy of r19prepchain.py;
the step-3 module r19prep3_actions.py is imported, never changed). Objects and layer: kitchen19p4.py. Every dwell is an
ESTIMATE; pouring itself (pieces leaving a container) is NOT simulated.

ACT=drawer  slicer output, option (a): the drawer bowl (cranked handle, kitchen19p4.dbh) gripped under the spout,
            slid out +x (XO), lifted, carried out from under the cabinet, its mouth MOUTHZ over the T2L staging pan
            (on the cart), rolled DEG about the grip axis (pour), level, back, slid in, set down.
ACT=ct2l    output transfer: the lever catch tray (step-3 'ctray') pulled out from under the blade plate, over the T2L
            pan, rolled CDEG (pour), back, slid in.
ACT=stgwok  cooking time: the T2L pan picked off its cradle (cart fixed), lifted, swung in front of the arm base to the
            wok side with the cart moving to POURC, levelled over the wok (axis (0.83, PANY), grip at POURZ), tipped TIP
            about the lug, held DWELL, levelled, returned along the same keyframes, set down.
Grasp entries: (keyframe, cfg overrides {r19, r19p4}, object in the world: True | False | 'cart')."""
import numpy as np
import kitchen16 as K,kitchen19 as K19,kitchen19p3 as P3,kitchen19p4 as P4
ACTS=('drawer','ct2l','stgwok','p2b','ct2p','p2t2l')
INFO={}
FOOD_DB=.30    # [est] one slicer batch in the drawer bowl (e.g. 2 potatoes sliced, 0.3 kg; 干锅土豆 uses 0.5 kg in two batches)
FOOD_CT=.15    # [est] lever wedges in the catch tray (step 3 PIECES)
FOOD_STG=.40   # [est] cut food for one wok dish staged in the pan
def V(KV,key,default):return np.array([float(v) for v in KV.get(key,default).split(',')])
def mouth_pose(name,Rl,mouth,deg):
 """(level R, p), (rolled R, p): container `name` rolled deg about its grip axis puts its mouth centre at `mouth`."""
 from scipy.spatial.transform import Rotation
 o=K.OBJ[name];H=P4.DBOWL['H'] if name.startswith(('dbowl','dbh')) else P4.STG_H if name.startswith('stg') else P3.CTRAY['H'] if name=='ctray' else P3.BOWL['H']
 g=np.asarray(o['grip'],float);ax=np.asarray(Rl)@np.asarray(o.get('hax',o['a']),float);Rr=Rotation.from_rotvec(ax*np.radians(deg)).as_matrix()
 p=np.asarray(mouth,float)-Rl@g-Rr@(Rl@(np.array([0,0,H])-g));R2,p2=P3.rolled_about_knob(name,Rl,p,deg);return (np.asarray(Rl,float),p),(R2,p2)
def action(ACT,KV,L,kf,scene_with,tray_objs):
 car,tom=tray_objs
 def K_(R,p,c,dw=0.,label='',load=None,com=None,**kw):
  k=kf(R,p,c,dw,label,**kw);k['load']=load;k['com']=com;return k
 t2=dict(P4.T2L,present=True);t2h=dict(P4.T2L,present=False)
 if ACT=='drawer':
  B=P4.dbh(float(KV.get('DXK',.17)),float(KV.get('DYK',.195)),float(KV.get('DZK',.237)),float(KV.get('DPD',0.)))
  XO=float(KV.get('XO',-1.49));CP=float(KV.get('CP',-1.25));deg=float(KV.get('DEG',-130.));yaw=float(KV.get('DYAW',45.));mz=float(KV.get('MOUTHZ',.12))
  I=np.eye(3);_,ps=P4.drawer_seat();_,po=P4.drawer_seat(XO);full=K19.MASS[B]+FOOD_DB;e=K19.MASS[B];com=np.array([0,0,.03])
  tgt=KV.get('DTGT','T2L');tb=None
  if tgt=='T2L':R0,p0=P4.t2l_world(CP,t2);(Rl,pl),(Rr,pr)=mouth_pose(B,K.Rz(yaw),p0+[0,0,P4.STG_H+mz],deg)
  else:   # a prep bowl on the counter (FS: the step-3 front spot by the sink; P2: plating spot 2), knob toward -x; free pour cart
   tb=dict(FS=(-.86,.15),P2=(.17,.15))[tgt];(Rl,pl),(Rr,pr)=mouth_pose(B,K.Rz(yaw),np.array([tb[0],tb[1],K19.COUNTER_TOP+P3.BOWL['H']+mz]),deg);CP='F' if 'CP' not in KV else CP
  up=po+[0,0,float(KV.get('DUP',.10))];ln=V(KV,'DLANE',','.join(str(round(v,3)) for v in (up+pl)/2+[0,0,.05]))
  Rm=K.Rz(yaw/2) if KV.get('LYAW','half')=='half' else K.Rz(float(KV['LYAW']))
  c_=lambda k:float(KV[k]) if k in KV else 'F'
  KF=[K_(I,ps+[0,0,.008],'A',0,'pick (under the spout, 8 mm)',full,com,anchor=True,seat=.008),K_(I,po+[0,0,.008],c_('SLC'),0,'slid out (8 mm over the plate)',full,com),
   K_(I,up,c_('LIFTC'),0,'lifted',full,com),*([K_(I,V(KV,'DOUT',''),c_('OUTC'),0,'out from under the cabinet',full,com)] if 'DOUT' in KV else []),K_(Rm,ln,'F',0,'lane',full,com,meet=True),K_(Rl,pl,CP,0,f'over the {tgt} target',full,com,anchor=True),
   K_(Rr,pr,CP,float(KV.get('POUR',3.)),f'rolled {deg:g} (poured)',full,com),K_(Rl,pl,CP,0,'level again',e,com),
   K_(Rm,ln,'F',0,'lane',e,com,meet=True),*([K_(I,V(KV,'DOUT',''),'F',0,'out from under the cabinet',e,com)] if 'DOUT' in KV else []),K_(I,up,c_('LIFTC'),0,'over the drawer',e,com,anchor=True),K_(I,po+[0,0,.008],'A',0,'lowered (8 mm over the plate)',e,com),
   K_(I,ps+[0,0,.008],c_('SLC2') if 'SLC2' in KV else 'A',0,'slid in, set down (8 mm)',e,com,seat=.008)]
  if KV.get('DPC'):   # planned carries (r19prep4chain): 'out' <-> 'pre-pour' joined by RRT (cart OUTC = CP on both sides); anchors: pick, pour, set down (same pose as the pick)
   pre=V(KV,'DPRE',','.join(str(round(v,3)) for v in pl+[0,0,.06]));dout=V(KV,'DOUT','-1.45,.33,1.03');oc=float(KV['OUTC']);
   KF=[K_(I,ps+[0,0,.008],'A',0,'pick (under the spout, 8 mm)',full,com,anchor=True,seat=.008),K_(I,po+[0,0,.008],c_('SLC'),0,'slid out (8 mm over the plate)',full,com),
    K_(I,up,c_('LIFTC'),0,'lifted',full,com),K_(I,dout,oc,0,'out from under the cabinet (carry start)',full,com,meet=True),K_(Rl,pre,oc,0,'pre-pour (carry end)',full,com,meet=True),
    K_(Rl,pl,oc,0,f'over the {tgt} target',full,com,anchor=True),K_(Rr,pr,oc,float(KV.get('POUR',3.)),f'rolled {deg:g} (poured)',full,com),K_(Rl,pl,oc,0,'level again',e,com),
    K_(Rl,pre,oc,0,'pre-pour (return carry start)',e,com,meet=True),K_(I,dout,oc,0,'out from under the cabinet (return carry end)',e,com,meet=True),
    K_(I,up,c_('LIFTC'),0,'over the drawer',e,com),K_(I,po+[0,0,.008],c_('SLC'),0,'lowered (8 mm over the plate)',e,com),K_(I,ps+[0,0,.008],'A',0,'slid in, set down (8 mm)',e,com,anchor=True,seat=.008)]
   KF[3]['pmeet']=True;KF[8]['pmeet']=True
  p4=dict(drawer=dict(xo=XO),drop_potato=True,**({'t2l':t2} if tgt=='T2L' else {}));w=dict(r19=scene_with(objs=[car,tom]+([('bowl',K.Rz(180.),np.array([tb[0],tb[1],K19.COUNTER_TOP]))] if tb else [])),r19p4=p4)
  INFO[ACT]=dict(obj=B,target=tgt,xo=XO,pour_cart=CP,pour_deg=deg,pour_yaw=yaw,mouth_over_pan_rim_m=mz,food_kg_est=FOOD_DB,lane=ln.tolist())
  return B,dict(r19=w['r19'],r19p4=p4),KF,[(0,w,True),(len(KF)-1,w,True)]
 if ACT=='ct2l':
  lx,ly,_=L['lever'];I=np.eye(3);s0=np.array([lx,ly,.862]);sl=float(KV.get('CSLIDE',.018));r0=s0+[0,0,sl];o=s0+[0,-.15,sl];hi=s0+[0,-.15,.11]
  kg=P3.MASS_EST['ctray']+FOOD_CT;e=P3.MASS_EST['ctray'];CP=float(KV.get('CP',-.60));deg=float(KV.get('CDEG',-120.));mz=float(KV.get('MOUTHZ',.10))
  R0,p0=P4.t2l_world(CP,t2);(Rl,pl),(Rr,pr)=mouth_pose('ctray',I,p0+[0,0,P4.STG_H+mz],deg)
  CW1=[[float(v) for v in t.split(',')] for t in KV.get('CW1','').split(';') if t];CW2=[[float(v) for v in t.split(',')] for t in KV.get('CW2','').split(';') if t]   # crossing waypoints (tray centre, CART frame, cart CP) before / after the lane meet; probes cthi_*: high in front of the base
  if 'CLANEL' in KV:ln=np.array([float(v) for v in KV['CLANEL'].split(',')])+[CP,-.21,0]   # CLANEL: the lane in the cart frame
  else:ln=V(KV,'CLANE',','.join(str(round(v,3)) for v in (hi+pl)/2+[0,0,.04]))
  cmp=V(KV,'CMOVEP',','.join(str(v) for v in hi))   # CMOVEP: the tray pose while the cart moves under it (default: the lifted pose)
  lnc=float(KV['LANEC']) if 'LANEC' in KV else 'F'   # LANEC: fixed lane cart (smoke s4/s5: free lanes drifted 0.63-0.78 m apart, the meet shuffle hit the upper arm)
  cpk=float(KV['CPICK']) if 'CPICK' in KV else 'A';chi=float(KV['CHI']) if 'CHI' in KV else 'F'   # CPICK / CHI: fixed carts of the pick and return anchors (smoke run 1: a free pick anchor took cart -1.19, 0.67 m from the pour cart; the meet shuffle hit the base plate)
  KF=[K_(I,s0+[0,0,.008],cpk,0,'pick (seated under the blade plate)',kg,None,anchor=True,seat=.008),K_(I,r0,'A',0,'raised 18 mm',kg,None),K_(I,o,'A',0,'pulled out 15 cm',kg,None),K_(I,hi,'A',0,'lifted',kg,None),*([K_(I,cmp,'A',0,'raised for the cart move',kg,None),K_(I,cmp,float(KV['CMOVE']),0,'cart moved under the held tray',kg,None)] if 'CMOVE' in KV else []),
   *[K_(I,np.array(w)+[CP,-.21,0],CP,0,f'cross {i+1}',kg,None) for i,w in enumerate(CW1)],K_(I,ln,lnc,0,'lane',kg,None,meet=True),*[K_(I,np.array(w)+[CP,-.21,0],CP,0,f'cross {i+1+len(CW1)}',kg,None) for i,w in enumerate(CW2)],K_(Rl,pl,CP,0,'over the T2L pan',kg,None,anchor=True),
   K_(Rr,pr,CP,float(KV.get('POUR',2.)),f'rolled {deg:g} (pour)',kg,None),K_(Rl,pl,CP,0,'level again',e,None),
   *[K_(I,np.array(w)+[CP,-.21,0],CP,0,f'cross {i+1+len(CW1)}',e,None) for i,w in list(enumerate(CW2))[::-1]],K_(I,ln,lnc,0,'lane',e,None,meet=True),*[K_(I,np.array(w)+[CP,-.21,0],CP,0,f'cross {i+1}',e,None) for i,w in list(enumerate(CW1))[::-1]],*([K_(I,cmp,float(KV['CMOVE']),0,'cart moved under the held tray',e,None),K_(I,cmp,chi,0,'cart back',e,None)] if 'CMOVE' in KV else []),K_(I,hi,chi,0,'in front of the lever base',e,None,anchor=True),K_(I,o,'A',0,'lowered',e,None),K_(I,r0,'A',0,'slid in (18 mm)',e,None),K_(I,s0+[0,0,.008],'A',0,'set down (8 mm)',e,None,seat=.008)]
  p4=dict(t2l=t2);w=dict(r19=scene_with('lever',objs=[car,tom]),r19p4=p4)
  INFO[ACT]=dict(pour_cart=CP,pour_deg=deg,mouth_over_pan_rim_m=mz,food_kg_est=FOOD_CT,lane=ln.tolist())
  return 'ctray',dict(r19=w['r19'],r19p4=p4),KF,[(0,w,True),(len(KF)-1,w,True)]
 if ACT=='stgwok':
  pdg=float(KV.get('SPD',0.));S_=P4.stg_pitched(pdg) if pdg else 'stg'
  C0=float(KV.get('C0',.45));CP=float(KV.get('POURC',.45));m,com=P4.stg_mass(FOOD_STG);me,come=P4.stg_mass(0.)
  R0,p0=P4.t2l_world(C0,t2h);g=K.OBJ[S_]['grip'];RL=K.Rz(float(KV.get('POUR_YAW',0.)))
  pw=np.array([float(KV.get('PANX',.83)),float(KV.get('PANY',.07)),float(KV.get('POURZ',1.38))-g[2]])
  from scipy.spatial.transform import Rotation
  tip=float(KV.get('TIP',135.));gw=pw+RL@g;ax=RL@np.asarray(K.OBJ[S_]['hax'],float);Rr=Rotation.from_rotvec(ax*np.radians(tip)).as_matrix();Rt,pt=Rr@RL,gw+Rr@(pw-gw)
  loc=lambda v,c:np.array(v,float)+[c,-.21,0.]
  # SW: swing waypoints 'x,y,z,yaw[,cart];...' (pan bottom centre in the CART frame, pan yaw deg, cart x; default cart C0):
  # default from the 96-start swing probes (r19prep4_probe stgsw_*, cart 0.45): out on the counter side of the arm base, low
  SW=[[float(v) for v in t.split(',')] for t in KV.get('SW','-.32,.05,1.05,0;-.25,.32,1.05,0;-.05,.42,1.12,45;.15,.32,1.20,0').split(';') if t]
  ln=V(KV,'SLANE','.30,.28,1.30');cl=float(KV['CLANE']) if 'CLANE' in KV else CP
  swk=lambda lab,ld,cm,rev=False:[K_(K.Rz(w[3]),loc(w[:3],w[4] if len(w)>4 else C0),w[4] if len(w)>4 else C0,0,f'{lab} {i+1}',ld,cm) for i,w in (list(enumerate(SW))[::-1] if rev else enumerate(SW))]
  KF=[K_(R0,p0+[0,0,.012],C0,0,'pick (12 mm over the cradle)',m,com,seat=.012),K_(R0,p0+[0,0,.03],C0,0,'lifted',m,com,anchor=True)]+swk('swing',m,com)+[
   K_(RL,loc(ln,cl),cl,0,'lane',m,com,meet=True),
   K_(RL,pw,CP,0,'over the wok',m,com,anchor=True),K_(Rt,pt,CP,float(KV.get('DWELL',2.)),f'tipped {tip:g} (poured)',m,com),K_(RL,pw,CP,0,'level',me,come),
   K_(RL,loc(ln,cl),cl,0,'lane',me,come,meet=True)]+swk('swing',me,come,True)+[
   K_(R0,p0+[0,0,.03],C0,0,'lowered',me,come,anchor=True),K_(R0,p0+[0,0,.012],C0,0,'set down (12 mm)',me,come,seat=.012)]
  w1=np.array(SW[0][:3]);w2=w3=w1
  ws=dict(r19=scene_with(objs=[car,tom]),r19p4=dict(t2l=t2));sc=dict(r19=scene_with(objs=[car,tom]),r19p4=dict(t2l=t2h))
  INFO[ACT]=dict(obj=S_,pick_cart=C0,pour_cart=CP,pour_axis=[pw[0],pw[1]],grip_z=pw[2]+g[2],tip_deg=tip,food_kg_est=FOOD_STG,pan=dict(r=P4.STG_R,h=P4.STG_H),t2l=P4.T2L,waypoints_cart_frame=dict(swing=SW,lane=ln.tolist(),lane_cart=cl))
  return S_,sc,KF,[(0,ws,'cart'),(len(KF)-1,ws,'cart')]
 if ACT=='ct2p':     # catch tray -> the staging pan standing on plating spot 2 (prep time; the step-3 ctray route with the pan as target)
  lx,ly,_=L['lever'];I=np.eye(3);s0=np.array([lx,ly,.862]);sl=float(KV.get('CSLIDE',.018));r0=s0+[0,0,sl];o=s0+[0,-.15,sl];hi=s0+[0,-.15,.11]
  kg=P3.MASS_EST['ctray']+FOOD_CT;e=P3.MASS_EST['ctray'];deg=float(KV.get('CDEG',-120.));mz=float(KV.get('MOUTHZ',.10))
  P2=np.array([float(v) for v in KV.get('P2','.17,.15').split(',')]+[K19.COUNTER_TOP]);Rpan=K.Rz(float(KV.get('PANYAW',0.)))
  (Rl,pl),(Rr,pr)=mouth_pose('ctray',I,P2+[0,0,P4.STG_H+mz],deg);l1=V(KV,'CLANE1','-0.40,.08,1.08');l2=V(KV,'CLANE2','0.0,.06,1.04')
  KF=[K_(I,s0+[0,0,.008],'A',0,'pick (seated under the blade plate)',kg,None,anchor=True,seat=.008),K_(I,r0,'A',0,'raised 18 mm',kg,None),K_(I,o,'A',0,'pulled out 15 cm',kg,None),K_(I,hi,'A',0,'lifted',kg,None),
   K_(I,l1,'F',0,'lane',kg,None,meet=True),K_(I,l2,'F',0,'lane right of the sink',kg,None),K_(Rl,pl,'F',0,'over the pan (plating spot 2)',kg,None,anchor=True),
   K_(Rr,pr,'A',float(KV.get('POUR',2.)),f'rolled {deg:g} (pour)',kg,None),K_(Rl,pl,'A',0,'level again',e,None),
   K_(I,l2,'F',0,'lane right of the sink',e,None,meet=True),K_(I,l1,'F',0,'lane',e,None),
   K_(I,hi,'F',0,'in front of the lever base',e,None,anchor=True),K_(I,o,'A',0,'lowered',e,None),K_(I,r0,'A',0,'slid in (18 mm)',e,None),K_(I,s0+[0,0,.008],'A',0,'set down (8 mm)',e,None,seat=.008)]
  w=dict(r19=scene_with('lever',objs=[car,tom,('stg',Rpan,P2)]))
  INFO[ACT]=dict(pan_spot=P2.tolist(),pour_deg=deg,mouth_over_pan_rim_m=mz,food_kg_est=FOOD_CT,lanes=[l1.tolist(),l2.tolist()],note='prep time (cooker off): run with PLUME=0')
  return 'ctray',w,KF,[(0,w,True),(len(KF)-1,w,True)]
 if ACT=='p2t2l':    # the filled pan from plating spot 2 onto its T2L cradle (cart CB fixed: T2L right in front of the spot); prep time
  CB=float(KV.get('CB',.49));P2=np.array([float(v) for v in KV.get('P2','.17,.15').split(',')]+[K19.COUNTER_TOP]);Rpan=K.Rz(float(KV.get('PANYAW',0.)))
  m,com=P4.stg_mass(FOOD_STG);Rt,pt=P4.t2l_world(CB,t2h);up=V(KV,'PUP',f'0,0,{.10}');ln=V(KV,'PLANE',','.join(str(round(v,3)) for v in (P2+pt)/2+[0,0,.16]))
  pck=float(KV['PCK']) if 'PCK' in KV else 'A';lc=float(KV['PLC']) if 'PLC' in KV else 'F'   # pick cart (default: the anchor's own, free solve), lane cart (default free)
  if KV.get('PCARRY'):   # planned carry (r19prep4chain): up over plating spot 2 -> high over the cradle, cart CB on both sides
   pu=V(KV,'PUP2','0,0,.15');ph=V(KV,'PHI','0,0,.15')
   KF=[K_(Rpan,P2+[0,0,.008],CB,0,'pick (plating spot 2, 8 mm)',m,com,anchor=True,seat=.008),K_(Rpan,P2+up,'A',0,'lifted',m,com),K_(Rpan,P2+pu,'A',0,'up (planned carry start)',m,com,meet=True),
    K_(Rt,pt+ph,CB,0,'high over the T2L cradle (planned carry end)',m,com,meet=True),K_(Rt,pt+[0,0,.06],CB,0,'over the T2L cradle',m,com,anchor=True),K_(Rt,pt+[0,0,.03],CB,0,'lowered',m,com),K_(Rt,pt+[0,0,.012],CB,0,'set down (12 mm)',m,com,seat=.012)]
   KF[2]['pmeet']=True
   sc=dict(r19=scene_with(objs=[car,tom]),r19p4=dict(t2l=t2h));w0=dict(r19=scene_with(objs=[car,tom]),r19p4=dict(t2l=t2h));w1=dict(r19=scene_with(objs=[car,tom]),r19p4=dict(t2l=t2))
   INFO[ACT]=dict(cart=CB,pan_spot=P2.tolist(),food_kg_est=FOOD_STG,planned_carry=True,note='prep time (cooker off): run with PLUME=0')
   return 'stg',sc,KF,[(0,w0,True),(len(KF)-1,w1,'cart')]
  KF=[K_(Rpan,P2+[0,0,.008],pck,0,'pick (plating spot 2, 8 mm)',m,com,anchor=True,seat=.008),K_(Rpan,P2+up,'A',0,'lifted',m,com),K_(Rpan,ln,lc,0,'lane',m,com,meet=True),
   K_(Rt,pt+[0,0,.10],CB,0,'over the T2L cradle',m,com,anchor=True),K_(Rt,pt+[0,0,.03],CB,0,'lowered',m,com),K_(Rt,pt+[0,0,.012],CB,0,'set down (12 mm)',m,com,seat=.012)]
  sc=dict(r19=scene_with(objs=[car,tom]),r19p4=dict(t2l=t2h));w0=dict(r19=scene_with(objs=[car,tom]),r19p4=dict(t2l=t2h));w1=dict(r19=scene_with(objs=[car,tom]),r19p4=dict(t2l=t2))
  INFO[ACT]=dict(cart=CB,pan_spot=P2.tolist(),food_kg_est=FOOD_STG,lane=ln.tolist(),note='prep time (cooker off): run with PLUME=0')
  return 'stg',sc,KF,[(0,w0,True),(len(KF)-1,w1,'cart')]
 if ACT=='p2b':      # bowl contents -> T2L pan: the step-3 prep / staging bowl on plating spot 2 (knob toward -x, as step-3 ctray's target), cart CB fixed
  CB=float(KV.get('CB',.49));I=np.eye(3);yaw=float(KV.get('BYAW',-90.));deg=float(KV.get('BDEG',-130.));mz=float(KV.get('MOUTHZ',.10))
  R0b,p0b=K.Rz(180.),np.array([.17,.15,K19.COUNTER_TOP]);kg=P3.MASS_EST['bowl']+FOOD_DB;e=P3.MASS_EST['bowl'];com=np.array([0,0,.03])
  Rp,pp=P4.t2l_world(CB,t2);(Rl,pl),(Rr,pr)=mouth_pose('bowl',K.Rz(yaw),pp+[0,0,P4.STG_H+mz],deg)
  up=p0b+[0,0,float(KV.get('BUP',.14))];Rm=K.Rz((180.+yaw)/2 if KV.get('BLYAW') is None else float(KV['BLYAW']));ln=V(KV,'BLANE',','.join(str(round(v,3)) for v in (up+pl)/2+[0,0,.04]))
  KF=[K_(R0b,p0b+[0,0,.008],CB,0,'pick (plating spot 2, 8 mm)',kg,com,anchor=True,seat=.008),K_(R0b,p0b+[0,0,.05],CB,0,'lifted',kg,com),K_(R0b,up,CB,0,'up',kg,com),
   K_(Rm,ln,CB,0,'lane',kg,com,meet=True),K_(Rl,pl,CB,0,'over the T2L pan',kg,com,anchor=True),K_(Rr,pr,CB,float(KV.get('POUR',3.)),f'rolled {deg:g} (poured)',kg,com),
   K_(Rl,pl,CB,0,'level again',e,com),K_(Rm,ln,CB,0,'lane',e,com,meet=True),K_(R0b,up,CB,0,'over plating spot 2',e,com,anchor=True),K_(R0b,p0b+[0,0,.05],CB,0,'lowered',e,com),
   K_(R0b,p0b+[0,0,.008],CB,0,'set down (8 mm)',e,com,seat=.008)]
  p4=dict(t2l=t2);w=dict(r19=scene_with(objs=[car,tom]),r19p4=p4)
  INFO[ACT]=dict(cart=CB,pour_deg=deg,pour_yaw=yaw,mouth_over_pan_rim_m=mz,food_kg_est=FOOD_DB,lane=ln.tolist(),bowl_spot=[.17,.15,180])
  return 'bowl',dict(r19=w['r19'],r19p4=p4),KF,[(0,w,True),(len(KF)-1,w,True)]
 raise KeyError(ACT)
