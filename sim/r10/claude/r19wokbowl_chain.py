"""Mac 2026-10-13: r19bowl_chain.py copy with ACT=wokbowl (WOK_TIP_HOLDING_BOWL): the r17chain wok keyframes up to
the level frame after the tip, into the holding bowl at plating spot 2, then back to the cooker via the lanes (no sink).
Options: SPOT, BH (lower bowl height), DY, LIP, L1X, RLANE=x,y,z (a separate return lane). Output results/mac/wok_tip_holding_bowl_<TAG>.json.

R19 (Mac, Claude): r19cup_chain.py copy with ACT=bowl added (2026-10-13): the holding bowl (bowlobj.py) from the
2nd plating spot (x .17) to the wok, tip by a wrist roll about the tab (pour, heat off), level, back, set down.
Bowl options: SPOT=x,y,z (bottom centre on the counter), POUR=x,y,z (bottom centre over the wok, upright), TIP (deg),
LANE=x,y,z, LIFT (m above the spot), FOOD (kg, default .25), PORTC (fixed pick/place cart), ONE=1 (as the cup).
Output: results/mac/chain_bowl_<TAG>.json.

R19 (Mac, Claude): r17chain.py copy with ACT=cup, the seasoning cup from the R14 port pad to the wok
(pour by a wrist roll, 2 s dwell) and back to the pad (cupobj.py registers the cup and the pad).
Output: results/mac/chain_cup_<TAG>.json. Options for the cup: POUR=x,y,z (cup bottom centre at the
wok, upright), TIP (deg, roll about the approach axis), LANE=x,y,z, OUTY (m toward the robot from the pad),
JAW_HELD (default .014 as the R14 cup probes).
R17 whole actions as continuous checked paths (kitchen17.py: the user's single-lever faucet, the
wok rinsed at the sink). Method as r16chain.py: object keyframes; between them the object moves in a
straight line (rotation slerp) every <= 1 cm / 2° while the cart moves linearly between the keyframe
values; the arm follows by IK continuation from the previous joint vector; the unchanged checker
(10 mm robot-environment, 5 mm gripper/held-environment, joint ranges) runs at every step (full
Bounds check every 5th step and at every keyframe). Two changes:
 - ANCHORS are solved here: 96-start collision-aware IK (solver.solve, SEEDS seeds, one grasp sense;
   cart free) at the anchor's pose; up to TRIES candidates (best reserve first) are followed to their
   meets on both sides and up to KEEP that follow are kept. Then one candidate per anchor is chosen
   so that every meet join is clear, with the least total joint travel (dynamic programming over the
   anchors; run 1 took the first candidate that followed and the arm met itself on another branch).
 - The cart may move while the arm holds the object out over the counter (user decision 2026-10-12,
   every step checked); the R10 dock carry envelope is not reported any more.
Between two anchors there is always a MEET keyframe in an open lane; the two arrivals there are joined
by a straight joint-space move (cart fixed, nearest equivalent angles), checked every <= 1° of the
largest joint, the held object staying within 5 cm / 15° of the meet pose; if the two arrivals have
different carts, the cart first moves under the object held still at the meet (IK continuation,
1 cm steps). PLAN=1 tries RRT-Connect (planner.py) for a blocked join.
Cart of a keyframe: a number, None (lane rule: CART_OFF left of the object), 'A' (the cart of the
anchor the piece is followed from) or 'F' (free: on the way to this keyframe the cart is an IK
variable too, cheaper to move than the joints, so it carries the object and the arm keeps its posture); an anchor with a number is solved with the cart there (so the
arm does not cross over its own base on the way to the lane).
Grasp approach / release retreat: the empty gripper (jaws open to JAW_OPEN, default 25 mm per jaw) moves APPROACH_M along the
grasp approach axis to / from the grasp, with the object in the world, by IK continuation from the
anchor state, checked the same way; the cart takes the along-counter (x) part of that move.
Actions:
 wok    from the cooker (pick 8 mm up): lift, carry left, tip 90° toward the robot over the plate
        (lip 3 cm above the plate, as r15tipwalk.py), level, carry left to the sink, lower under the
        running faucet (5 s), tip 90° to empty it into the sink, level, lift, carry back, set down
 lever  open the faucet: the lever end block gripped, lifted LEVER_OPEN (close = the same path reversed)
 spider the spider from its rest (SPX, SPY; default R17 front spot, handle toward the robot as in use)
        to the pot (scoop, drain 5 s), to the plate (tip 110° about the handle), back to the rest;
        the ladle is off the rest unless LADLE=x,y puts it elsewhere
 lid    the R16 lid action in the R17 layout (spider at the front of the counter end)
Held load (own model, as r15reach.py pour): wok 1.5 kg (CoG 45 mm above the bottom), handle + block
0.3 kg, plus the food (1.15 kg, the heaviest R15 dish) until it is tipped out, or 0.5 kg of rinse
water at the sink; PGC moment about the TCP (limit 7 N.m) and joint torque ratios at every keyframe.
Timing (ASSUMPTIONS as r16chain.py): TCP <= 0.10 m/s, rotation <= 45°/s, joints <= 60°/s, cart
<= 0.25 m/s, joins at 60°/s + 0.6 s, grasp / release 0.8 s each, dwells.
python r17chain.py ACT=wok|lever [SIGN=1|-1] [SEEDS=1|2] [TRIES=6] [PLAN=1 PLAN_S=120] [TAG=..]
-> results/r17/chain_<ACT>[_SIGN][_TAG].json (pieces, joins, approaches, loads, time, playback q)"""
import sys,os,json,time,numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation,Slerp
import chain
from scene import build,save
from checker import Checker
from solver import solve
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
import cupobj   # R19: registers OBJ cup and the port pad (wraps kitchen17.add)
import bowlobj   # R19: registers OBJ bowl and a bowl on the counter (wraps kitchen17.add)
KV=dict(a.split('=',1) for a in sys.argv[1:]);ACT=KV['ACT'];SIGN=int(KV.get('SIGN',1))
SEEDS=(14,15,16)[:int(KV.get('SEEDS',2))];TRIES=int(KV.get('TRIES',6))
DESIGN=dict(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.set_design(**DESIGN)
VW,WW,QW,CW,CART_OFF=.10,45.,60.,.25,.30
import arms;ARM=arms.current();QW=min(QW,min(arms.speeds(ARM)))   # R19: ARM=<id> (default ur5e); the joint cap never exceeds the arm's slowest joint (60 for ur5e/fr5)
APPROACH_M=.06;JAW_HELD=float(KV.get('JAW_HELD',.014 if ACT=='cup' else .015));JAW_OPEN=float(KV.get('JAW_OPEN',.025))   # 10 mm each side of a 30 mm block; at .040 a finger at the spider's front rest met the arm's own base cover
I=np.eye(3)
def kf(R,p,c=None,dw=0.,label='',anchor=False,meet=False,load=0.,seat=0.,walk=None):
 """seat: height of this pose above the object's support (grasp approach / release from the seated object);
 walk: (R16 walk name, path index) whose arm state is tried first as this anchor's start"""
 return dict(R=np.asarray(R,float),p=np.asarray(p,float),c=c,dw=dw,label=label,anchor=anchor,meet=meet,load=load,seat=seat,walk=walk)
def rolled(name,R,p,deg):
 o=K.OBJ[name];g=p+R@o['grip'];ax=R@o['a'];Rr=Rotation.from_rotvec(ax*np.radians(deg)).as_matrix();return Rr@R,g+Rr@(p-g)
if 'GTILT' in KV:K17.set_wok_tilt(float(KV['GTILT']))   # wok grasp leaned toward the robot
if KV.get('GRASP')=='end':K17.set_wok_end_grasp()   # wok grasp along the handle
if 'SPX' in KV:K.TOOL_XY['spider']=(float(KV['SPX']),float(KV['SPY']))
if 'LADLE' in KV:K.TOOL_XY['ladle']=tuple(float(v) for v in KV['LADLE'].split(','))
if KV.get('SPAT','off')!='off':K.TOOL_XY['spatula']=tuple(float(v) for v in KV['SPAT'].split(','))
if 'SPATREST' in KV:K.TOOL_XY['spatula']=tuple(float(v) for v in KV['SPATREST'].split(','))   # R18: the spatula on its rest here, in every action's scene
if 'SPATELEV' in KV:K.SPAT_ELEV=float(KV['SPATELEV'])   # R18: handle elevation of the spatula on its rest (R16: 50°)
if 'SPATYAW' in KV:K.SPAT_YAW=float(KV['SPATYAW'])   # R18: turned on the counter (0 = handle toward the robot)
if 'SPATROLL' in KV:K.SPAT_ROLL=float(KV['SPATROLL'])   # R18: 180 = the other face up
def tip(piv,a):
 R=K.Rx(a);return R,piv-R@np.array([0,0,K15.DEPTH])
def action():
 """object, scene extras (world objects), keyframes, grasp/release list (keyframe index, world cfg for the empty gripper)"""
 if ACT=='wok':
  W0=K15.WOK0;PC=np.array(K15.PLATE['c'],float);PC[0]=float(KV.get('PX',PC[0]));FOOD=1.15;WATER=.5
  PH=float(KV.get('PH',K15.PLATE['h']));target=PC+[0,0,PH+.03]+[0,.05,0];piv=target-K.Rx(90)@np.array([0,-K15.A_RIM,0]);o0=piv-[0,0,K15.DEPTH]
  # lift 13.5 cm in the cooker bowl before moving left: lower, the wok bottom met the handle bracket
  # (top 1.0 m) at the lane (run 1); the sink carry height is lower (rim under the spout)
  # run 2: lifted 13.5 cm in place the rim met the drum holder; under the upper cabinet the raised
  # grip put the wrist into the door. Run 3: lift 4 cm, slide 15 cm toward the robot (the bracket is
  # then 15 cm off the wok axis, under the raised wall), then left in front of the cabinets
  # run 4: cart further left in the lanes (the vertical gripper over a grip 0.16 m from the arm mount
  # could not follow); the sink pose is the carry height, so the wok is not lowered into the sink
  # run 5: no single lane cart suited every candidate (base plate / reach) -> run 6: the cart stays with
  # each anchor and moves at the meets under the held wok; the wok is emptied 7 cm forward of the tap
  # (at the tap its back rim met the spout when tipped toward the robot)
  # run 6: sliding the wok 15 cm toward the robot put its grip 0.15 m from the arm mount (the arm
  # folded onto its base plate) -> run 7: up 9 cm in place (drum holder raised), then left over the bracket
  # run 9: the handle bracket is gone (keyed slot in the cooker rim); lifted 5 cm (clear of a concave
  # cooker's bowl rim) the wok goes straight left, its grip kept low under the upper cabinets
  # run 11: grasp sense -1 (the plate tip needs it, R15) has no top-grasp start at the cooker below
  # 20° tilt, and lifted in place its wrist met the hood edge -> leave the cooker diagonally up-left
  S=K17.SINK_WOK;sp=S+[0,0,K15.DEPTH];zs=S[2];fwd=W0+[-.05,0,.05];lane1=[.62,W0[1],fwd[2]];lane2=[float(KV.get('L2X',-.15)),.18,.93];Sd=S+[0,-.07,.06];spd=Sd+[0,0,K15.DEPTH]   # run 12: the lane by the sink, clear of the upper cabinet (at x .10 the sink-side elbow met its door); run 14: emptied 6 cm higher, at the plating height (lower, the wrist met the sink's front rim)
  # run 10: the cart is free on the carry frames ('F')
  KF=[kf(I,W0+[0,0,.008],'A',0,'pick',load=FOOD,seat=.008),kf(I,W0+[0,0,.03],'F',0,'lifted',anchor=True,load=FOOD),kf(I,fwd,'F',0,'up and left'),
   kf(I,lane1,'F',0,'lane',meet=True,load=FOOD),kf(I,o0,'F',0,'over the plate',anchor=True,load=FOOD),
   kf(*tip(piv,90),'F',2.,'tipped 90 (plated)',load=FOOD),kf(I,o0,'F',0,'level'),
   kf(I,lane2,'F',0,'lane',meet=True),
   kf(I,S,float(KV['SINKC']) if 'SINKC' in KV else 'F',5.,'under the tap',anchor=True,load=WATER),kf(I,Sd,'F',0,'forward',load=WATER),kf(*tip(spd,90),'F',1.,'emptied',load=WATER),kf(I,Sd,'F',0,'level'),
   kf(I,lane2,'F',0,'lane',meet=True),kf(I,lane1,'F',0,'lane'),kf(I,fwd,'F',0,''),
   kf(I,W0+[0,0,.03],'F',0,'lowered',anchor=True),kf(I,W0+[0,0,.008],'A',0,'set down',seat=.008)]
  # grasp at the first keyframe, release at the last: the empty gripper with the wok on the cooker;
  # the faucet was opened before (lever up) and is closed after
  sc=dict(r17_lever=K17.LEVER_OPEN,**({'r15_plate_h':PH} if 'PH' in KV else {}),**({'r15_plate_c':PC.tolist()} if 'PX' in KV else {}))   # PH: a soup bowl (8 cm) at the plating spot instead of a plate
  return 'wok',sc,KF,[(0,sc),(len(KF)-1,sc)]
 if ACT=='spider':
  fl=K.POT['c'][2]+.002+K.POT['rack'];PX,PY=K.POT['c'][0],K.POT['c'][1];PC=np.array(K15.PLATE['c'],float)
  Rt,pt=K.pose('spider','rest');bs=np.array([PX,PY+.02,fl+.035]);ds=PC+[0,0,K15.PLATE['h']+.16];Rd,pd=rolled('spider',I,ds,-110)
  out_=pt+[0,-.10,.15];lane=[1.40,0,1.15];mid=[(PX+ds[0])/2,0,1.12]
  KF=[kf(Rt,pt+[0,0,.008],'A',0,'pick',anchor=True,seat=.008),kf(Rt,pt+[0,0,.03],'A'),kf(I,out_,'A',0,'out and up'),kf(I,lane,None,0,'lane',meet=True),
   kf(I,bs+[0,0,.12],'A',0,'over the pot'),kf(I,bs,'A',0,'scoop',anchor=True),kf(I,bs+[0,0,.12],'A',5.,'drain'),kf(I,[PX,0,1.12],'A',0,'lane'),
   kf(I,mid,None,0,'lane middle',meet=True),kf(I,[ds[0],0,1.12],'A'),kf(I,ds,.18,0,'over the plate',anchor=True),kf(Rd,pd,'A',0,'tip 110 deg'),
   kf(I,ds,'A',0,'level again'),kf(I,[ds[0],0,1.12],'A',0,'lane'),kf(I,mid,None,0,'lane middle',meet=True),kf(I,lane,None,0,'lane'),
   kf(I,out_,'A',0,'out and up'),kf(Rt,pt+[0,0,.03],'A'),kf(Rt,pt+[0,0,.008],'A',0,'on the rest',anchor=True,seat=.008)]
  tools=dict(K17.R17_TOOLS_OFF)   # R17: spatula and ladle off the rest unless SPAT / LADLE put them somewhere
  if 'LADLE' in KV:tools.pop('ladle')
  if KV.get('SPAT','off')!='off':tools.pop('spatula')
  return 'spider',dict(r16_tools=tools),KF,[(0,dict(r16_tools=tools)),(len(KF)-1,dict(r16_tools=tools))]
 if ACT=='lid':   # the R16 lid action (r16chain.py) in the R17 layout: off the pot, slid out of the hood, up, rolled upright, carried high to the rack
  R2,p2=K.lid_on({});Rk,pk=K.pose('lid','rack');hi=p2+[0,-.23,.27];Rr,pr=rolled('lid',R2,hi,90)
  KF=[kf(R2,p2+[0,0,.008],'A',0,'lift off',anchor=True,seat=.008,walk=('lid_off_pot_f',0)),kf(R2,p2+[0,0,.02],'A'),kf(R2,p2+[0,-.23,.02],'A',0,'slide out'),kf(R2,hi,'A',0,'up'),kf(Rr,pr,'A',0,'roll 90 deg'),
   kf(Rr,[pr[0]+.12,-.10,1.36],None,0,'carry',meet=True),kf(Rk,[pk[0],-.10,1.36],None),kf(Rk,pk+[0,0,.08],'A',0,'over the rack',anchor=True),kf(Rk,pk+[0,0,.004],'A',0,'in the rack',seat=.004)]
  # run 16: lane-rule carts at the carry (a cart move under the raised lid was blocked)
  return 'lid',{},KF,[(0,dict(r16_lid='on')),(len(KF)-1,dict(r16_lid='rack'))]
 if ACT=='spatula':   # R18: spatula from its rest to the first R15 stir stroke start in the wok (back = reverse)
  Rr,pr=K17.spatula_rest_blade();keys=json.load(open('results/r15/stir_h_scrape_dice_keys.json'))['keys'];k0=keys[0]
  Rb0=np.array(k0['R']);pw=np.array(k0['p']);nrm=K15.SP.C-pw;nrm/=np.linalg.norm(nrm);pb0=pw+.01*nrm+K15.WOK0   # 1 cm off the steel, as r15stirwalk2 LIFT
  W0=K15.WOK0;mid=[(pr[0]+W0[0])/2,-.02,1.15]
  Rl=Slerp([0,1],Rotation.from_matrix([Rr,Rb0]))(float(KV.get('SPATLANE',0))).as_matrix()   # R18: the lane carries the spatula this far turned from its rest toward the stroke start
  lc=KV.get('SPATLANEC','F');lc={'F':'F','lane':None}[lc] if lc in ('F','lane') else float(lc)   # R18: the lane's cart (F free, lane = lane rule, or a number)
  KF=[kf(Rr,pr+[0,0,.008],'A',0,'pick',anchor=True,seat=.008),kf(Rr,pr+[0,0,.06],'A',0,'lifted'),kf(Rr,pr+[0,-.08,.18],'F',0,'out and up'),
   kf(Rl,mid,lc,0,'lane',meet=True),kf(Rb0,pb0+[0,-.05,.15],'F',0,'over the wok'),kf(Rb0,pb0,'F',0,'stroke start',anchor=True)]
  return 'spatula_b',{},KF,[(0,{'r16_tools':{'ladle':None}})]
 if ACT=='cup':   # R19: seasoning cup, port pad -> wok -> pour -> back on the pad
  P0=np.array([float(v) for v in KV['PORT'].split(',')]) if 'PORT' in KV else cupobj.PORT_CUP.copy();L=float(KV.get('LIQ',.06))   # up to 60 g liquid
  pw=np.array([float(v) for v in KV.get('POUR','.80,.04,1.035').split(',')]);TIP=float(KV.get('TIP',120));Rp,pp=rolled('cup',I,pw,TIP)
  out_=P0+[0,0 if KV.get('OUTY')=='none' else -float(KV.get('OUTY',.20)),.03];lane=np.array([float(v) for v in KV.get('LANE','.66,0,1.12').split(',')])
  hw=pw+[0,0,float(KV.get('HOVER',0))]   # optional approach height over the rim before lowering to the pour pose
  ONE=KV.get('ONE')=='1'   # ONE=1: the pour is not an anchor; the port anchor's state is followed through the pour to the return lane
  NO=KV.get('OUTY')=='none';PC=float(KV['PORTC']) if 'PORTC' in KV else 'A';WC=float(KV['POURC']) if 'POURC' in KV else 'F'   # fixed anchor carts (optional)
  LZ=float(KV.get('LIFT',.03))   # OUTY=none: straight from the lift to the lane
  KF=[kf(I,P0+[0,0,.008],PC,0,'pick at the port',anchor=True,load=L,seat=.008),kf(I,P0+[0,0,LZ],'A',0,'lifted',load=L)]+([] if NO else [kf(I,out_,'F',0,'out from under the cabinet',load=L)])+[
   kf(I,lane,'F',0,'lane',meet=not ONE,load=L)]+([kf(I,hw,'F',0,'over the wok',load=L)] if 'HOVER' in KV else [])+[kf(I,pw,WC,0,'low at the wok rim',anchor=not ONE,load=L),kf(Rp,pp,'F',2.,f'tipped {TIP:.0f} deg (pour)',load=L),kf(I,pw,'F',0,'level (empty)')]+([kf(I,hw,'F',0,'up')] if 'HOVER' in KV else [])+[
   kf(I,lane,'F',0,'lane',meet=True)]+([] if NO else [kf(I,out_,'F',0,'out from under the cabinet')])+[kf(I,P0+[0,0,LZ],'A',0,'over the pad'),kf(I,P0+[0,0,.008],PC,0,'back on the port',anchor=True,seat=.008)]
  sc=dict(r19_port=P0.tolist());w=dict(r19_cup='port',**sc)
  return 'cup',sc,KF,[(0,w),(len(KF)-1,w)]
 if ACT=='wokbowl':   # Mac 2026-10-13: r17chain ACT=wok keyframes up to 'level' after the tip, into the holding bowl at spot 2, then
  # back to the cooker via the lanes WITHOUT the sink. The bowl (bowlobj, 190 x 70 mm; BH overrides the height) stands
  # at SPOT (default plating spot 2) as a world object; the tip target is r17chain's: lip 3 cm above the bowl rim, 5 cm
  # beyond its centre (+y), tipped 90 deg toward the robot (sense -1, as R15/R17/R18).
  W0=K15.WOK0;P0=np.array([float(v) for v in KV['SPOT'].split(',')]) if 'SPOT' in KV else bowlobj.SPOT2.copy();FOOD=1.15
  BH=float(KV.get('BH',bowlobj.BOWL_H));DY=float(KV.get('DY',.05))
  if 'BH' in KV:   # a lower bowl, same diameter and tab (stated in the report)
   bowlobj.BOWL_H=BH;bowlobj.TAB_Z=BH-.015;K.OBJ['bowl']['parts']=bowlobj.bowl_parts()
  target=P0+[0,0,BH+float(KV.get('LIP',.03))]+[0,DY,0];piv=target-K.Rx(90)@np.array([0,-K15.A_RIM,0]);o0=piv-[0,0,K15.DEPTH]
  fwd=W0+[-.05,0,.05];lane1=[float(KV.get('L1X',.62)),W0[1],fwd[2]]
  RL=[float(v) for v in KV['RLANE'].split(',')] if 'RLANE' in KV else lane1   # return lane (default: the outbound lane)
  KF=[kf(I,W0+[0,0,.008],'A',0,'pick',load=FOOD,seat=.008),kf(I,W0+[0,0,.03],'F',0,'lifted',anchor=True,load=FOOD),kf(I,fwd,'F',0,'up and left',load=FOOD),
   kf(I,lane1,'F',0,'lane',meet=True,load=FOOD),kf(I,o0,'F',0,'over the bowl',anchor=True,load=FOOD),
   kf(*tip(piv,90),'F',2.,'tipped 90 (into the bowl)',load=FOOD),kf(I,o0,'F',0,'level'),
   kf(I,RL,'F',0,'lane (return)',meet=True)]+([kf(I,lane1,'F',0,'lane')] if 'RLANE' in KV else [])+[kf(I,fwd,'F',0,''),
   kf(I,W0+[0,0,.03],'F',0,'lowered',anchor=True),kf(I,W0+[0,0,.008],'A',0,'set down',seat=.008)]
  sc=dict(**({} if KV.get('NOSTATION')=='1' else dict(r19_port=[.45,.30,1.085],r19_cup='port')),r19_bowl='spot',r19_bowl_at=P0.tolist())   # NOSTATION=1: no cup pad/post/cup; bowl at spot 2, the cup on its pad, faucet closed (no sink trip), the plate at spot 1 stays
  return 'wok',sc,KF,[(0,sc),(len(KF)-1,sc)]
 if ACT=='bowl':   # R19: holding bowl, 2nd plating spot -> wok -> tip (pour) -> back on the spot
  P0=np.array([float(v) for v in KV['SPOT'].split(',')]) if 'SPOT' in KV else bowlobj.SPOT2.copy();L=float(KV.get('FOOD',.25))   # up to 0.25 kg food
  pw=np.array([float(v) for v in KV.get('POUR','.83,.14,1.06').split(',')]);TIP=float(KV.get('TIP',110));Rp,pp=rolled('bowl',I,pw,TIP)
  lane=np.array([float(v) for v in KV.get('LANE','.50,.08,1.10').split(',')]);LZ=float(KV.get('LIFT',.05))
  ONE=KV.get('ONE','1')=='1';PC=float(KV['PORTC']) if 'PORTC' in KV else 'A';WC=float(KV['POURC']) if 'POURC' in KV else 'F'
  KF=[kf(I,P0+[0,0,.008],PC,0,'pick at the spot',anchor=True,load=L,seat=.008),kf(I,P0+[0,0,LZ],'A',0,'lifted',load=L),
   kf(I,lane,'F',0,'lane',meet=not ONE,load=L),kf(I,pw,WC,0,'low over the wok',anchor=not ONE,load=L),kf(Rp,pp,'F',2.,f'tipped {TIP:.0f} deg (pour)',load=L),kf(I,pw,'F',0,'level (empty)'),
   kf(I,lane,'F',0,'lane',meet=True),kf(I,P0+[0,0,LZ],'A',0,'over the spot'),kf(I,P0+[0,0,.008],PC,0,'set down',anchor=True,seat=.008)]
  sc=dict(r19_port=[.45,.30,1.085],r19_cup='port',r19_bowl_at=P0.tolist());w=dict(r19_bowl='spot',**sc)   # the seasoning cup stays on its pad (as chain_cup_final)
  return 'bowl',sc,KF,[(0,w),(len(KF)-1,w)]
 if ACT=='lever':
  KF=[kf(*K17.lever_pose(0.),'A',0,'closed',anchor=True),kf(*K17.lever_pose(K17.LEVER_OPEN),'A',0,'open')]
  return 'lever',{},KF,[(0,dict(r17_lever=0.)),(1,dict(r17_lever=K17.LEVER_OPEN))]
OBJ,SCENE,KF,GR=action()
BASE=dict(r19_station=True,r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools=dict(K17.R17_TOOLS_OFF))   # R17: the pour drum is swung away from the rim except while stirring
if KV.get('NOSTATION')=='1':BASE.pop('r19_station')   # wokbowl: the seasoning-cup station left out (isolates the bowl question)
if 'TOOLS_OFF' in KV:BASE['r16_tools']={t:None for t in KV['TOOLS_OFF'].split(',')}   # tools not on the rest
if 'SPATREST' in KV:BASE['r16_tools']={'ladle':None}   # R18: spatula on its rest at SPATREST
if 'PLATE2' in KV:BASE['r17_plate2']=[float(KV['PLATE2']),K15.PLATE['c'][1],K15.PLATE['c'][2]]   # R18: a second plate (a finished dish waiting)
def model(extra):
 cfg=chain.chain_cfg('SD',**{**BASE,**SCENE,**extra});tree,meta=build(cfg,None);return Checker(tree,meta)
ch=model(K17.held_cfg(OBJ,SIGN));m,d=ch.m,ch.d;ids=ch.arm_ids;sid=m.site('R_prep').id
lo=np.array([m.jnt_range[j,0] for j in range(m.njnt)])[ids];hi_=np.array([m.jnt_range[j,1] for j in range(m.njnt)])[ids]
def solve_to(c,q,pt_,Rt_):
 q=np.array(q,float)
 def res(x):
  q[ids]=x;c.d.qpos[:]=q;mujoco.mj_kinematics(c.m,c.d)
  return np.r_[(c.d.site_xpos[sid]-pt_)*10,Rotation.from_matrix(Rt_@c.d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
 x0=np.clip(q[ids],lo+1e-8,hi_-1e-8);sol=least_squares(res,x0,bounds=(lo+1e-9,hi_-1e-9),max_nfev=200,xtol=1e-10,ftol=1e-10)
 q[ids]=sol.x;pe,re=c.pose_error(q,pt_,Rt_);return q,pe,re,float(np.degrees(np.max(abs(sol.x-x0))))
W_CART,W_ARM=.02,.05   # 'F' frames: weights of the cart (per m) and the joints (per rad) in the step regularization
def solve_free(c,q,pt_,Rt_):
 """IK step with the cart as a variable too ('F' frames): pose error plus a small cost on the change
 of every variable, the cart cheaper than the joints, so the cart carries the object along the
 counter and the arm keeps its posture."""
 q=np.array(q,float);v=[0]+list(ids);x0=q[v].copy();x0[1:]=np.clip(x0[1:],lo+1e-8,hi_-1e-8);x0[0]=np.clip(x0[0],-1.48+1e-6,1.46-1e-6)
 w=np.r_[W_CART,np.full(len(ids),W_ARM)]
 def res(x):
  q[v]=x;c.d.qpos[:]=q;mujoco.mj_kinematics(c.m,c.d)
  return np.r_[(c.d.site_xpos[sid]-pt_)*10,Rotation.from_matrix(Rt_@c.d.site_xmat[sid].reshape(3,3).T).as_rotvec(),w*(x-x0)]
 sol=least_squares(res,x0,bounds=(np.r_[-1.48,lo+1e-9],np.r_[1.46,hi_-1e-9]),max_nfev=300,xtol=1e-10,ftol=1e-10)
 q[v]=sol.x;pe,re=c.pose_error(q,pt_,Rt_);return q,pe,re,float(np.degrees(np.max(abs(sol.x[1:]-x0[1:])))),float(abs(sol.x[0]-x0[0]))
def state(c,q,full):
 r=c.check(q,full=full,mass=0.);rmin=min((v['reserve_mm'] for cat,v in r['clearance'].items() if cat!='self'),default=None) if full else None
 return r['hits'],rmin
def cart_of(k,cA):
 c=KF[k]['c'];return cA if c in ('A','F') else float(np.clip(KF[k]['p'][0]-CART_OFF,-1.48,1.46)) if c is None else float(c)
def follow(a,b,q):
 """Keyframes a -> b (either direction) by IK continuation from q (the state at KF[a])."""
 q=np.array(q,float);cA=q[0];out=[];st=1 if b>a else -1
 for i in range(a,b,st):
  A_,B_=KF[i],KF[i+st];ca,cb=cart_of(i,cA),cart_of(i+st,cA)
  ang=np.degrees(np.linalg.norm(Rotation.from_matrix(B_['R']@A_['R'].T).as_rotvec()));dist=np.linalg.norm(B_['p']-A_['p'])
  n=max(1,int(np.ceil(max(dist/.01,ang/2,abs(cb-ca)/.01))));sl=Slerp([0,1],Rotation.from_matrix([A_['R'],B_['R']]))
  for k in range(1,n+1):
   pt_,Rt_=K.tcp_pose(OBJ,sl(k/n).as_matrix(),A_['p']+(B_['p']-A_['p'])*k/n,SIGN)
   if B_['c']=='F':q,pe,re,dq,dc=solve_free(ch,q,pt_,Rt_)
   else:q[0]=ca+(cb-ca)*k/n;q,pe,re,dq=solve_to(ch,q,pt_,Rt_);dc=abs(cb-ca)/n
   hits,rmin=state(ch,q,k%5==0 or k==n)
   dt=max(dist/n/VW,ang/n/WW,dq/QW,dc/CW)+(B_['dw'] if k==n and st>0 else 0.)+(A_['dw'] if k==1 and st<0 else 0.)
   out.append(dict(kf=i+st if k==n else None,cart=round(q[0],3),step_deg=round(dq,2),pose_mm=round(pe*1000,2),reserve_mm=None if rmin is None else round(rmin,1),dt=dt,hits=[h['pair'] for h in hits][:3],q=q.tolist()))
   if pe>.005 or re>np.radians(3) or hits or dq>10:return out,dict(at=f"{A_['label']}->{B_['label']}",**{k_:v for k_,v in out[-1].items() if k_!='q'})
 return out,None
JOIN_DEV=(.05,15.)   # a join may move the held object at most 5 cm / 15° off the meet pose (food stays in)
FOOD_OBJ=('wok','spider','ladle','carrier','cup','bowl')   # objects with food in them (the lid and the lever may swing in a join)
def dev(q,x):
 """TCP deviation (m, deg) of state q from the TCP pose of the object at keyframe x."""
 pt_,Rt_=K.tcp_pose(OBJ,KF[x]['R'],KF[x]['p'],SIGN);d.qpos[:]=q;mujoco.mj_kinematics(m,d)
 return float(np.linalg.norm(d.site_xpos[sid]-pt_)),float(np.degrees(np.linalg.norm(Rotation.from_matrix(Rt_@d.site_xmat[sid].reshape(3,3).T).as_rotvec())))
def shuffle(q,x,c):
 """At meet x: the cart moves to c (1 cm steps) while the arm holds the object at the meet pose."""
 q=np.array(q,float);c0=q[0];n=max(1,int(np.ceil(abs(c-c0)/.01)));out=[];pt_,Rt_=K.tcp_pose(OBJ,KF[x]['R'],KF[x]['p'],SIGN)
 for k in range(1,n+1):
  q[0]=c0+(c-c0)*k/n;q,pe,re,dq=solve_to(ch,q,pt_,Rt_);hits,rmin=state(ch,q,k%5==0 or k==n)
  out.append(dict(q=q.tolist(),dq=dq,reserve_mm=rmin))
  if pe>.005 or re>np.radians(3) or hits or dq>10:return out,dict(cart=round(q[0],3),pose_mm=round(pe*1000,2),hits=[h['pair'] for h in hits][:3])
 return out,None
def meet_join(qa,qb,x,plan=False):
 """Join the two arrivals at meet x: if their carts differ, first move the cart under the held object
 (shuffle, from either side), then the straight joint-space join (cart fixed)."""
 qa,qb=np.array(qa,float),np.array(qb,float)
 if abs(qa[0]-qb[0])<1e-6:return join(qa,qb,plan,x)
 why=[]
 for frm,to,rev in ((qa,qb,False),(qb,qa,True)):
  out,f=shuffle(frm,x,to[0])
  if f:why.append(dict(side='b' if rev else 'a',shuffle=f));continue
  j=join(np.array(out[-1]['q']),to,plan,x) if not rev else join(to,np.array(out[-1]['q']),plan,x)
  if not j['ok']:why.append(dict(side='b' if rev else 'a',join={k_:v for k_,v in j.items() if k_!='qs'}));continue
  ts=sum(max(.01/CW,o['dq']/QW) for o in out);sq=[o['q'] for o in out]
  j.update(cart_m=round(abs(qa[0]-qb[0]),3),shuffle_s=round(ts,1),s=round(j['s']+ts,2),arm_deg=round(j['arm_deg']+sum(o['dq'] for o in out),1),qs=(sq+j['qs']) if not rev else (j['qs']+sq[::-1]))
  return j
 return dict(ok=False,arm_deg=1e3,cart_m=round(abs(qa[0]-qb[0]),3),reason='shuffle or join blocked from both sides',why=why)
def join(qa,qb,plan=None,x=None):
 """Straight joint-space move qa -> qb (cart fixed), checked every <= 1° of the largest joint; each
 joint takes the nearest equivalent angle (+-360°) that stays in its range. With a meet x, the held
 object may leave the meet pose by at most JOIN_DEV on the way."""
 qa,qb=np.array(qa),np.array(qb)
 for j in range(6):
  c=[qb[3+j]+k*2*np.pi for k in (-2,-1,0,1,2) if lo[j]-1e-9<=qb[3+j]+k*2*np.pi<=hi_[j]+1e-9];qb[3+j]=min(c,key=lambda v:abs(v-qa[3+j]))
 dq=np.degrees(np.max(abs(qb[3:9]-qa[3:9])));n=max(1,int(np.ceil(dq)))
 for k in range(1,n):
  hits,_=state(ch,qa+(qb-qa)*k/n,False)
  if x is not None and not hits and OBJ in FOOD_OBJ:
   dm,dg=dev(qa+(qb-qa)*k/n,x)
   if dm>JOIN_DEV[0] or dg>JOIN_DEV[1]:return dict(ok=False,arm_deg=round(float(dq),1),at=round(k/n,2),reason=f'object moves {dm*1000:.0f} mm / {dg:.0f} deg in the join')
  if hits:
   if (KV.get('PLAN') if plan is None else plan):
    import planner;ch.active=ch.arm_ids;r=planner.plan(ch,qa,qb,budget_s=float(KV.get('PLAN_S',120)),seed=8)
    if r['ok']:
     P=np.array(r['path']);sweep=float(np.degrees(np.sum(np.max(abs(np.diff(P[:,3:9],axis=0)),axis=1))))
     return dict(ok=True,method='planned',arm_deg=round(float(dq),1),path_joint_deg=round(sweep,1),s=round(sweep/QW+.6,2),qs=P.tolist())
    return dict(ok=False,method='planner failed',arm_deg=round(float(dq),1),reason=r.get('reason'))
   return dict(ok=False,arm_deg=round(float(dq),1),at=round(k/n,2),hits=[h['pair'] for h in hits][:3])
 return dict(ok=True,arm_deg=round(float(dq),1),s=round(dq/QW+.6,2),qs=[(qa+(qb-qa)*k/n).tolist() for k in range(0,n+1,max(1,n//20))])
_empty={}
def approach(k,world,q):
 """Empty gripper, jaws open, object in the world (cfg world): from the grasp at KF[k] (object at its
 support, i.e. without the 8 mm lift) back APPROACH_M along the grasp approach axis."""
 key=json.dumps(world,sort_keys=True)
 if key not in _empty:_empty[key]=model(world)
 c=_empty[key];R,p=KF[k]['R'],KF[k]['p']-[0,0,KF[k]['seat']]
 pt0,Rt=K.tcp_pose(OBJ,R,p,SIGN);q=np.array(q,float);q[-2:]=JAW_OPEN;c0=q[0];out=[];n=int(round(APPROACH_M/.01))
 for s in range(n+1):
  dp=-Rt[:,0]*APPROACH_M*s/n;q[0]=c0+dp[0];q,pe,re,dq=solve_to(c,q,pt0+dp,Rt);hits,rmin=state(c,q,s%3==0 or s==n)
  out.append(dict(step=s,pose_mm=round(pe*1000,2),step_deg=round(dq,2),reserve_mm=None if rmin is None else round(rmin,1),hits=[h['pair'] for h in hits][:3],q=q.tolist()))
  if pe>.005 or re>np.radians(3) or hits:return dict(ok=False,kf=k,stop=s,hits=out[-1]['hits'],pose_mm=out[-1]['pose_mm'],qs=[o['q'] for o in out])
 rm=[o['reserve_mm'] for o in out if o['reserve_mm'] is not None]
 return dict(ok=True,kf=k,min_reserve_mm=min(rm) if rm else None,time_s=round(APPROACH_M/VW,1),qs=[o['q'] for o in out])
MASS=dict(wok=[(1.5,np.array([0,0,.045])),(.3,(K15.HANDLE['root']+K15.HANDLE['end'])/2-K15.WOK0)],lever=[],spider=[(.45,np.zeros(3))],spatula_b=[(.3,np.zeros(3))],lid=[(.8,np.array([0,0,.025]))],cup=[(cupobj.CUP_MASS,np.array([0,0,.035]))],bowl=[(bowlobj.BOWL_MASS,np.array([0,0,.03]))])
def load(q,k):
 parts=MASS[OBJ]+([(KF[k]['load'],np.array([0,0,.02]))] if KF[k]['load'] else [])
 if not parts:return None
 mass=sum(m_ for m_,_ in parts);com=KF[k]['p']+KF[k]['R']@(sum(m_*c for m_,c in parts)/mass)
 d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d);bid=m.site_bodyid[sid];jp=np.zeros((3,m.nv));jr=jp.copy();mujoco.mj_jac(m,d,jp,jr,com,bid)
 tau=d.qfrc_bias-jp.T@np.array([0,0,-mass*9.81]);ratios={n:float(abs(tau[ch.da[n]])/v) for n,v in ch.env.items()}
 return dict(kf=KF[k]['label'],held_kg=round(mass,2),max_joint_ratio=round(max(ratios.values()),3),pgc_moment_Nm=round(float(np.linalg.norm(np.cross(com-d.site_xpos[sid],[0,0,-mass*9.81]))),2))
# ---- anchors: candidates, then the pieces on both sides ----
A=[i for i,k_ in enumerate(KF) if k_['anchor']];M=[i for i,k_ in enumerate(KF) if k_['meet']]
def sides(a):
 """Targets of the pieces followed from anchor a: the meet before / after it, or the path ends."""
 before=[x for x in M if x<a];after=[x for x in M if x>a]
 prev_a=max([x for x in A if x<a],default=None);next_a=min([x for x in A if x>a],default=None)
 t=[]
 if prev_a is None:
  if a>0:t.append(0)
 else:assert before and before[-1]>prev_a,('no meet between anchors',prev_a,a);t.append(before[-1])
 if next_a is None:
  if a<len(KF)-1:t.append(len(KF)-1)
 else:assert after and after[0]<next_a,('no meet between anchors',a,next_a);t.append(after[0])
 return t
_cands={}
def candidates(k):
 key=(tuple(np.round(KF[k]['p'],4)),tuple(np.round(KF[k]['R'].ravel(),4)))
 if key in _cands:return _cands[key]
 pt_,Rt_=K.tcp_pose(OBJ,KF[k]['R'],KF[k]['p'],SIGN);out=[];stat={}
 for seed in SEEDS:
  t=dict(name=f'{ACT}_{k}',points=[list(pt_)]*2,held=None,kind='transfer',force=None,approach=list(Rt_[:,0]),jaws=[tuple(SIGN*(KF[k]['R']@K.OBJ[OBJ]['j']))],jaw_q=JAW_HELD)
  if isinstance(KF[k]['c'],float):t['cart_x']=KF[k]['c']   # anchor with a fixed cart
  r=solve(ch,pt_,list(Rt_[:,0]),target=t,seed=seed)
  for k_,v in r['status_counts'].items():stat[k_]=stat.get(k_,0)+v
  out+=[dict(q=c_['q'],reserve_mm=c_['reserve_mm']) for c_ in r['candidates']]
 out=sorted(out,key=lambda c_:-c_['reserve_mm'])
 if KF[k].get('walk') and ARM=='ur5e':   # a checked R16 walk state (UR5e joint values; not for another arm) of the same pose and grasp sense goes first
  w=json.load(open(f"results/r16/walk_{KF[k]['walk'][0]}.json"))
  if w['jaw_sign']==SIGN:out=[dict(q=w['path'][KF[k]['walk'][1]]['q'],reserve_mm=-1.)]+out
 _cands[key]=(out,stat);return _cands[key]
t0=time.monotonic();pieces={};anchors={};log=[];good={};KEEP=int(KV.get('KEEP',6))
for a in A:
 cs,stat=candidates(a);print(KF[a]['label'],'start candidates',len(cs),stat,flush=True);good[a]=[]
 for i,c_ in enumerate(cs[:TRIES]):
  got={};bad=None
  for b in sides(a):
   out,f=follow(a,b,c_['q'])
   got[b]=out
   if f:bad=f;break
  log.append(dict(anchor=KF[a]['label'],cand=i,start_reserve_mm=round(c_['reserve_mm'],1),cart=round(c_['q'][0],3),ok=bad is None,fail=bad))
  print(' cand',i,'cart',round(c_['q'][0],2),'ok' if bad is None else bad,flush=True)
  if bad is None:
   good[a].append((c_,got))
   if len(good[a])>=KEEP:break
 if not good[a]:anchors[a]=dict(ok=False,n_candidates=len(cs),start_status=stat)
# ---- one candidate per anchor with every meet join clear (DP over the anchors) ----
segs=[(a,b,[mm for mm in M if a<mm<b][0]) for a,b in zip(A,A[1:])];pairs={}
for a,b,x in segs:
 for i,(ca,ga) in enumerate(good[a]):
  for j,(cb,gb) in enumerate(good[b]):pairs[(a,b,i,j)]=meet_join(ga[x][-1]['q'],gb[x][-1]['q'],x,plan=False)
 if 'DEBUGJ' in KV:
  for k_,v in pairs.items():
   if k_[:2]==(a,b) and k_[2]<2 and k_[3]<2:print('  pair',k_[2:],'qa',np.round(good[a][k_[2]][1][x][-1]['q'][:9],2).tolist(),'qb',np.round(good[b][k_[3]][1][x][-1]['q'][:9],2).tolist(),{kk:vv for kk,vv in v.items() if kk!='qs'},flush=True)
 print('joins at',KF[x]['label'],sorted([(round(v['arm_deg']),v['ok']) for v in [pairs[(a,b,i,j)] for i in range(len(good[a])) for j in range(len(good[b]))]])[:6],flush=True)
def dp():
 cost={A[0]:{i:0. for i in range(len(good[A[0]]))}};back={}
 for a,b,x in segs:
  cost[b]={}
  for j in range(len(good[b])):
   opts=[(cv+pairs[(a,b,i,j)]['arm_deg'],i) for i,cv in cost[a].items() if pairs[(a,b,i,j)]['ok']]
   if opts:cost[b][j],back[(b,j)]=min(opts)
 if not cost[A[-1]]:return None
 j=min(cost[A[-1]],key=cost[A[-1]].get);sel={A[-1]:j}
 for a,b,x in reversed(segs):j=back[(b,j)];sel[a]=j
 return sel
sel=dp() if all(good[a] for a in A) else None
if sel is None and KV.get('PLAN') and all(good[a] for a in A):   # plan the closest blocked pairs
 for a,b,x in segs:
  blocked=sorted([k_ for k_ in pairs if k_[:2]==(a,b) and not pairs[k_]['ok']],key=lambda k_:pairs[k_]['arm_deg'])
  if any(pairs[k_]['ok'] for k_ in pairs if k_[:2]==(a,b)):continue
  for k_ in blocked[:int(KV.get('PLAN_N',2))]:
   r_=meet_join(good[a][k_[2]][1][x][-1]['q'],good[b][k_[3]][1][x][-1]['q'],x,plan=True);print('planned',KF[x]['label'],k_[2:],r_['ok'],r_.get('method'),flush=True)
   if r_['ok']:pairs[k_]=r_;break
 sel=dp()
dp_ok=sel is not None
if sel is None:sel={a:0 for a in A if good[a]}
for a in A:
 if a in sel:
  c_,got=good[a][sel[a]];anchors[a]=dict(ok=True,cand=sel[a],q=c_['q'],cart=round(c_['q'][0],3),start_reserve_mm=round(c_['reserve_mm'],1))
  for b,out in got.items():pieces[(a,b)]=out
joins={}
for a,b,x in segs:
 if a in sel and b in sel:j=dict(pairs[(a,b,sel[a],sel[b])]);j['at']=KF[x]['label'];j['best_pair_deg']=min(v['arm_deg'] for k_,v in pairs.items() if k_[:2]==(a,b));joins[x]=j
# ---- grasp approach / release retreat ----
apps=[]
def q_at(k):
 if k in anchors:return anchors[k]['q'] if anchors[k]['ok'] else None
 return next((s_['q'] for out in pieces.values() for s_ in out if s_['kf']==k),None)
for k,world in GR:
 q=q_at(k)
 if q is None:apps.append(dict(ok=False,kf=k,reason='no arm state at this keyframe'));continue
 apps.append(approach(k,world,q))
# ---- playback order, time, loads ----
ok=all(v['ok'] for v in anchors.values()) and len(joins)==len([x for x in M if x>min(A) and x<max(A)]) and all(j['ok'] for j in joins.values()) and all(p_['ok'] for p_ in apps)
play=[];tsum=0.;loads=[]
if ok:
 def seq(a,b):return pieces[(a,b)] if (a,b) in pieces else None
 order=[]
 if A[0]>0:order+=list(reversed(pieces[(A[0],0)]))+[dict(q=anchors[A[0]]['q'],dt=0.)]
 else:order.append(dict(q=anchors[A[0]]['q'],dt=0.))
 for a,b in zip(A,A[1:]):
  x=[mm for mm in M if a<mm<b][0];order+=pieces[(a,x)]
  j=joins[x];order+=[dict(q=qq,dt=j['s']/max(1,len(j['qs']))) for qq in j['qs']]
  back=pieces[(b,x)];order+=[dict(q=s_['q'],dt=s_['dt']) for s_ in reversed(back[:-1])]+[dict(q=anchors[b]['q'],dt=back[0]['dt'])]
 if A[-1]<len(KF)-1:order+=pieces[(A[-1],len(KF)-1)]
 tsum=sum(s_['dt'] for out in pieces.values() for s_ in out)+sum(j['s'] for j in joins.values())+2*.8+sum(p_['time_s'] for p_ in apps)
 play=[s_['q'] for s_ in order]
 for (a,b),out in pieces.items():
  for s_ in out:
   if s_['kf'] is not None:loads.append(load(np.array(s_['q']),s_['kf']))
 for a in A:loads.append(load(np.array(anchors[a]['q']),a))
 loads=[l_ for l_ in loads if l_]
def summ(out):
 rs=[s_['reserve_mm'] for s_ in out if s_['reserve_mm'] is not None]
 return dict(steps=len(out),time_s=round(sum(s_['dt'] for s_ in out),1),min_reserve_mm=min(rs) if rs else None,max_step_deg=max(s_['step_deg'] for s_ in out),cart=[out[0]['cart'],out[-1]['cart']])
res=dict(act=ACT,obj=OBJ,**({} if ARM=='ur5e' else dict(arm=ARM)),grasp_sense=SIGN,design=DESIGN,scene=SCENE,wok_tilt=float(KV.get('GTILT',0)),wok_grasp=KV.get('GRASP','top'),tool_xy={k_:list(v) for k_,v in K.TOOL_XY.items()},ok=ok,time_s=round(tsum,1),elapsed_s=round(time.monotonic()-t0),
 keyframes=[dict(i=i,label=k_['label'],p=np.round(k_['p'],3).tolist(),c=k_['c'],anchor=k_['anchor'],meet=k_['meet']) for i,k_ in enumerate(KF)],
 anchors={KF[a]['label']+f'#{a}':{k_:v for k_,v in an.items() if k_!='q'} for a,an in anchors.items()},
 pieces=[dict(frm=KF[a]['label']+f'#{a}',to=KF[b]['label']+f'#{b}',**summ(out)) for (a,b),out in pieces.items()],
 joins=[{k_:v for k_,v in j.items() if k_!='qs'} for j in joins.values()],approaches=[{k_:v for k_,v in p_.items() if k_!='qs'} for p_ in apps],
 min_reserve_mm=min([summ(o)['min_reserve_mm'] for o in pieces.values() if summ(o)['min_reserve_mm'] is not None],default=None),
 max_pgc_moment_Nm=max([l_['pgc_moment_Nm'] for l_ in loads],default=None),max_joint_ratio=max([l_['max_joint_ratio'] for l_ in loads],default=None),
 loads=loads,tries=log,play=play,approach_qs=[p_.get('qs') for p_ in apps])
os.makedirs('results/mac',exist_ok=True);fn=(f'results/mac/wok_tip_holding_bowl_' if ACT=='wokbowl' else f'results/mac/chain_{ACT}_')+KV.get('TAG',f's{SIGN:+d}')+arms.tag(ARM)+'.json';save(fn,res)
print(fn);print(json.dumps({k_:v for k_,v in res.items() if k_ not in ('play','approach_qs','loads','keyframes','tries')},default=str,ensure_ascii=False))
