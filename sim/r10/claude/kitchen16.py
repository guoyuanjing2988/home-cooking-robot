"""R16 second heat zone and handling objects (design proposal, all sizes estimated), added on
top of kitchen15 when cfg['r16'] is set. The user's reference cook (research/homestyle_meals.md)
steams, boils soup and blanches while the wok works, so the right half of the hob gets:
 - a flat 米家电磁炉2 class induction cooker (MIoT 加热档位 0-99 writable, r15_cooking_market.md),
   ~0.29 x 0.36 x 0.06 m, replacing the right gas burners (as R15 did on the left);
 - a 30 cm stainless pot (12 cm deep) on it, its centre near the hood front so the front half
   is outside the hood (hood: y >= .15, z >= 1.25); an optional 9 cm steamer tier on the pot;
 - a glass dome lid with a keyed TAB on its front rim, taken HORIZONTALLY from the front (approach
   +y): lifted 2 cm, slid toward the robot until its back edge leaves the hood, so the steam
   escapes behind it into the hood, rolled 90° about the approach axis and set upright in a lid
   rack at the counter end (lid plane y-z, tab to the front). Top-down grasps fail everywhere
   under the hood band: the PGC is ~0.2 m long and the wrist goes above it (r16walk round 1:
   lid / carrier 0 of 384 starts; the upright lid rack under the upper cabinet 0 too);
 - a plate CARRIER (steaming rack with a bail): the dish sits on a wire ring, the bail arches
   over it to a keyed block at the top centre, above the dish's centre of mass; taken from the
   front-above, approach 30° below horizontal toward the wall, so the gripper body stays out of
   the hood; a lug at the rim failed on paper: the 54 mm wide fingers would touch the tier wall;
 - a spider strainer (漏勺) and a ladle (汤勺), each with a keyed block at the handle end, and the
   R15 spatula, lying on a tool rest at the counter end in their USE orientation (bowl / blade on
   a low cradle, handle rising toward the robot), so the grasp is the working grasp and the
   grip stays low; spatula and ladle in front, the spider behind and 7 cm to the side of the
   ladle (its handle passes high over the ladle bowl; straight behind it, the arm reaching
   for the spider touched the ladle's grip block: r16chain run 3). Standing them handle-up in a caddy failed (r16walk caddy_spider, 0 of 192
   starts: the wrist above a 1.25 m grip runs into the upper cabinets); the R15 stand under the
   hood was unusable too. Caddy and lid rack take the counter end, where the base
   scene had a dish rack (the user's dish rack is on the sink leg).
Object frames: lid = rim centre (bottom of the rim ring), carrier = ring centre (bottom),
spider / ladle = bowl centre with the bowl level and the handle rising toward -y at ELEV,
spatula = its tool frame (kitchen15.spatula_tool). Each object has a grasp (point, approach,
jaw axis in its own frame); OBJ[name]['grip_part'] is left out when held (the fingers hold it).
cfg keys: r16 (bool), r16_tier (steamer tier on the pot), r16_lid ('on' | 'rack' | None),
r16_carrier ('tier' | 'pot' | 'stage' | None), r16_tools (dict name -> 'rest' | None, default all on
the rest), r16_held (dict(obj=name, T_tool_obj=4x4)), r16_bowl (soup bowl at the plate spot)."""
import numpy as np,xml.etree.ElementTree as E
from scene import box,fmt,vessel
from scipy.spatial.transform import Rotation
import kitchen15 as K15
IND2=dict(x=(1.15,1.44),y=(.03,.39),z=(.85,.91))
POT=dict(c=np.array([1.295,.21,.91]),r=.15,h=.12,rack=None);TIER_H=.09   # rack: height of a steaming rack inside the pot (None = no rack)
POT_TOP=POT['c'][2]+POT['h'];TIER_TOP=POT_TOP+TIER_H
LID_R,TAB_Y=.155,-.20
TOOL_XY=dict(spatula=(1.52,.30),ladle=(1.62,.24),spider=(1.64,.46));CRADLE_H=.02;SPAT_ELEV=50.;SPAT_YAW=0.;SPAT_ROLL=0.   # tool rest: bowl / blade centre, cradle pad height
RACK=dict(x=(1.70,1.80),y=(.08,.42),z=(.85,.86),fin_h=.06,rim_x=1.775,cy=.25,ry=-90)   # lid plane y-z, rim plane at rim_x, dome toward -x (ry=-90) or +x (ry=90, rim at 1.725); fins 19 mm off the lid
BOWL=dict(r=.10,h=.08)     # soup bowl (汤碗) at the plate spot for ladling
ELEV=dict(spider=45.,ladle=45.)   # handle elevation with the bowl level (a 60° ladle put the grip high: the arm folded onto its mast in the lane, r16chain run 6)
def Rx(a):a=np.radians(a);return np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
def Ry(a):a=np.radians(a);return np.array([[np.cos(a),0,np.sin(a)],[0,1,0],[-np.sin(a),0,np.cos(a)]])
def Rz(a):a=np.radians(a);return np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]])
def quat(R):return Rotation.from_matrix(R).as_quat()[[3,0,1,2]]
def lid_parts():
 # dome (rise 50 mm) as stacked discs; tab bar + keyed block on the front rim
 return [('r16_lid_rim','cylinder',[0,0,.005],[LID_R,.005],np.eye(3)),('r16_lid_d1','cylinder',[0,0,.02],[.125,.01],np.eye(3)),
  ('r16_lid_d2','cylinder',[0,0,.035],[.085,.008],np.eye(3)),('r16_lid_d3','cylinder',[0,0,.046],[.04,.004],np.eye(3)),
  ('r16_lid_tabbar','box',[0,-.172,.006],[.008,.018,.005],np.eye(3)),('r16_lid_tab','box',[0,TAB_Y,.008],[.015,.012,.012],np.eye(3))]
def carrier_parts():
 # wire ring + dish (plate and food envelope, 60 mm) + bail over the dish to a block at the top centre
 # (block 0.11 m up: the fingertips reach 30 mm past the TCP and stay 14 mm above the food)
 return [('r16_car_ring','cylinder',[0,0,.003],[.135,.003],np.eye(3)),('r16_car_dish','cylinder',[0,0,.036],[.12,.03],np.eye(3)),
  ('r16_car_bail1','capsule',np.r_[.132,0,.006,.03,0,.11],[.004],None),('r16_car_bail2','capsule',np.r_[-.132,0,.006,-.03,0,.11],[.004],None),
  ('r16_car_bailtop','capsule',np.r_[-.03,0,.11,.03,0,.11],[.004],None),('r16_car_block','box',[0,0,.11],[.02,.015,.012],np.eye(3))]
def tool_parts(name):
 """Spider / ladle in its use frame: bowl centre, bowl level, handle rising toward -y."""
 r,hh,L={'spider':(.07,.02,.30),'ladle':(.045,.025,.27)}[name];e=np.radians(ELEV[name])
 d=np.array([0,-np.cos(e),np.sin(e)]);a=np.array([0,-r,.01]);g=a+L*d
 Rb=np.c_[[1,0,0],d,np.cross([1,0,0],d)]   # block: y along the handle
 return [(f'r16_{name}_bowl','cylinder',[0,0,0],[r,hh],np.eye(3)),(f'r16_{name}_handle','capsule',np.r_[a,g-.02*d],[.006],None),
  (f'r16_{name}_block','box',g,[.015,.02,.012],Rb)],g,-d
def _spatula():
 parts,_,_=K15.spatula_tool(.45)
 parts=[(n.replace('R_gripper_spatula','r16_spatula'),t,p,s,R) for n,t,p,s,R in parts]
 return dict(parts=parts,grip=np.zeros(3),a=np.array([1.,0,0]),j=np.array([0,-1.,0]),grip_part=None)
def _obj():
 O=dict(lid=dict(parts=lid_parts(),grip=np.array([0,TAB_Y,.008]),a=np.array([0,1.,0]),j=np.array([1.,0,0]),grip_part='r16_lid_tab'),
  carrier=dict(parts=carrier_parts(),grip=np.array([0,0,.11]),a=np.array([0,np.cos(np.radians(30)),-np.sin(np.radians(30))]),j=np.array([1.,0,0]),grip_part='r16_car_block'))
 for n in ('spider','ladle'):
  p,g,a=tool_parts(n);O[n]=dict(parts=p,grip=g,a=a,j=np.array([1.,0,0]),grip_part=f'r16_{n}_block')
 O['spatula']=_spatula();return O
OBJ=_obj()
def set_design(pot_y=None,lid_a=None,car_a=None,pot_h=None,rack=None,rack_ry=None):
 """Design sweep (r16walk POT_Y / LID_A / CAR_A / POT_H / RACK): pot centre y (the cooker moves with
 it), the lid-tab / carrier grasp approach angle below horizontal (toward the wall; 90 = top-down),
 the pot depth and a steaming rack inside the pot (its height above the pot floor)."""
 global POT_TOP,TIER_TOP
 if pot_h is not None:POT['h']=pot_h;POT_TOP=POT['c'][2]+pot_h;TIER_TOP=POT_TOP+TIER_H
 if rack is not None:POT['rack']=rack
 if rack_ry is not None:RACK['ry']=rack_ry
 if pot_y is not None:dy=pot_y-POT['c'][1];POT['c'][1]=pot_y;IND2['y']=(IND2['y'][0]+dy,IND2['y'][1]+dy)
 for n,a in (('lid',lid_a),('carrier',car_a)):
  if a is not None:a=np.radians(a);OBJ[n]['a']=np.array([0,np.cos(a),-np.sin(a)])
def T_tool_obj(name,sign=1):
 """Object frame -> tool frame for the grasp (jaw sense sign)."""
 from checker import reference
 o=OBJ[name];Rt=reference.rotation(o['a'],sign*o['j']);T=np.eye(4);T[:3,:3]=Rt.T;T[:3,3]=-Rt.T@o['grip'];return T
def tcp_pose(name,R,p,sign=1):
 """TCP position and rotation for object pose (R, p) in the world."""
 from checker import reference
 o=OBJ[name];return p+R@o['grip'],reference.rotation(R@o['a'],sign*(R@o['j']))
def rest_R(name):
 """Tool orientation on the rest: spider / ladle in their use frame; the spatula with its handle
 SPAT_ELEV above horizontal, pointing at the robot."""
 if name=='spatula':
  from checker import reference
  e=np.radians(SPAT_ELEV);return Rz(SPAT_YAW)@reference.rotation([0,np.cos(e),-np.sin(e)],[1.,0,0])@Rx(SPAT_ROLL)   # R18: SPAT_YAW turns it on the counter, SPAT_ROLL 180 lays it the other face up
 return np.eye(3)
def _centre(name):
 """Bowl / blade centre in the object frame."""
 P=OBJ[name]['parts'];return np.mean([np.asarray(q) for n,t,q,s,_ in P if 'blade' in n],axis=0) if name=='spatula' else np.zeros(3)
def pose(name,key):
 """World pose (R, p) of an object in a named place."""
 if name=='lid':
  if key=='on':return np.eye(3),POT['c'].copy()
  if key=='rack':return Ry(RACK['ry']),np.array([RACK['rim_x'] if RACK['ry']<0 else RACK['rim_x']-.05,RACK['cy'],RACK['z'][1]+LID_R+.002])
 if name=='carrier':
  if key=='tier':return np.eye(3),np.array([POT['c'][0],POT['c'][1],POT_TOP+.003])
  if key=='pot':return np.eye(3),np.array([POT['c'][0],POT['c'][1],POT['c'][2]+.002+POT['rack']+.003])   # on the steaming rack in the pot
  if key=='stage':return np.eye(3),np.array([K15.PLATE['c'][0],K15.PLATE['c'][1],.851])
 if name in ('spider','ladle','spatula') and key=='rest':
  R=rest_R(name);P=OBJ[name]['parts']
  # bowl / blade centre over its cradle; lowest box / cylinder point (conservative: largest half size) on the cradle
  z=min((R@np.asarray(p))[2]-max(s) for n,t,p,s,_ in P if t!='capsule');c=R@_centre(name)
  return R,np.array([TOOL_XY[name][0]-c[0],TOOL_XY[name][1]-c[1],.85+CRADLE_H+.002-z])
 raise KeyError((name,key))
def lid_on(cfg):
 R,p=pose('lid','on');p=p.copy();p[2]=TIER_TOP if cfg.get('r16_tier') else POT_TOP;return R,p
def _add(parent,prefix,parts,R=np.eye(3),p=np.zeros(3),cls=('1','2'),rgba='.8 .8 .82 1'):
 for n,t,q,s,Rp in parts:
  if t=='capsule':
   ft=np.r_[R@q[:3]+p,R@q[3:]+p];E.SubElement(parent,'geom',name=prefix+n,type='capsule',fromto=fmt(ft),size=fmt(s),rgba=rgba,contype=cls[0],conaffinity=cls[1],mass='.000001')
  else:E.SubElement(parent,'geom',name=prefix+n,type=t,pos=fmt(R@np.asarray(q)+p),size=fmt(s),quat=fmt(quat(R@Rp)),rgba=rgba,contype=cls[0],conaffinity=cls[1],mass='.000001')
def add(tree,world,cfg):
 for g in list(world.iter('geom')):
  if g.get('name') in ('stove_piece2','r15_spatula_stand','dish_rack_base','dish_rack_back'):   # the counter end's dish rack moves (the user's is on the sink leg)
   for par in world.iter():
    if g in list(par):par.remove(g);break
 b=lambda n,x,y,z,c=(.8,.8,.8,1):box(world,n,[(x[0]+x[1])/2,(y[0]+y[1])/2,(z[0]+z[1])/2],[x[1]-x[0],y[1]-y[0],z[1]-z[0]],c)
 b('r16_ind2',IND2['x'],IND2['y'],IND2['z'],(.12,.12,.13,1))
 vessel(world,'r16_pot',POT['c'],r=POT['r'],height=POT['h'])
 for s in (-1,1):b(f'r16_pot_ear{s:+d}',(POT['c'][0]+s*.15+min(0,s*.035),POT['c'][0]+s*.15+max(0,s*.035)),(POT['c'][1]-.025,POT['c'][1]+.025),(POT_TOP-.03,POT_TOP-.015),(.7,.7,.72,1))
 if cfg.get('r16_tier'):vessel(world,'r16_tier',POT['c']+[0,0,POT['h']],r=POT['r'],height=TIER_H)
 if POT['rack']:E.SubElement(world,'geom',name='r16_pot_rack',type='cylinder',pos=fmt(POT['c']+[0,0,.002+POT['rack']-.003]),size=fmt([.13,.003]),rgba='.7 .7 .72 1',contype='1',conaffinity='2',mass='.000001')
 # tool rest: one low cradle pad under each bowl / blade
 for n,(x,y) in TOOL_XY.items():b(f'r16_rest_{n}',(x-.04,x+.04),(y-.04,y+.04),(.85,.85+CRADLE_H),(.5,.5,.52,1))
 # lid rack: base + two low fins
 b('r16_rack_base',RACK['x'],RACK['y'],RACK['z'],(.5,.5,.52,1))
 for k,xx in enumerate([(RACK['x'][0],RACK['x'][0]+.006),(RACK['x'][1]-.006,RACK['x'][1])]):b(f'r16_rack_fin{k}',xx,RACK['y'],(RACK['z'][1],RACK['z'][1]+RACK['fin_h']),(.5,.5,.52,1))
 if cfg.get('r16_bowl'):
  pc=np.asarray(cfg.get('r15_plate_c',K15.PLATE['c']),float);E.SubElement(world,'geom',name='r16_soup_bowl',type='cylinder',pos=fmt(pc+[0,0,BOWL['h']/2]),size=fmt([BOWL['r'],BOWL['h']/2]),rgba='.95 .95 .93 1',contype='1',conaffinity='2',mass='.000001')
 held=cfg.get('r16_held') or {}
 place=dict(lid=cfg.get('r16_lid','on'),carrier=cfg.get('r16_carrier'))
 place.update({n:'rest' for n in ('spatula','spider','ladle')});place.update(cfg.get('r16_tools',{}))
 if cfg.get('r15_spatula'):place['spatula']=None   # R15 holds the spatula at the TCP
 for n,key in place.items():
  if key is None or n==held.get('obj'):continue
  R,p=lid_on(cfg) if (n,key)==('lid','on') else pose(n,key)
  _add(world,'',OBJ[n]['parts'],R,p)
 if held:
  tool=tree.find(".//body[@name='R_tool']");T=np.asarray(held['T_tool_obj'],float);o=OBJ[held['obj']]
  _add(tool,'R_gripper_',[q for q in o['parts'] if q[0]!=o['grip_part']],T[:3,:3],T[:3,3],cls=('2','3'))
