"""R15 cooking station (design proposal, all sizes estimated), added on top of kitchen14
when cfg['r15'] is set:
 - the two left gas burners give way to a countertop concave (wok-shaped) 3.5 kW induction
   cooker (美的 MC-E35D2 / 九阳 N3501 class, 20 A point); its power knob is turned by a
   bolt-on servo on the cooker front (no arm time, no mains modification);
 - a 34 cm round-bottom carbon-steel wok (sphere radius 0.20 m, rim radius 0.17 m, 95 mm deep)
   seated in the cooker bowl, with a SHORT handle pointing left (-x) that ends in a keyed grip
   block 0.235 m from the wok axis (form fit for the PGC, like the R11 holder key); the handle
   rests on a bracket on the cooker, so spatula strokes cannot spin the wok. A long handle put
   the full wok's weight 0.39 m from the TCP (10.9 N.m on the PGC, limit 7);
 - a plate (or oil cup) spot on the counter just left of the hood (PLATE): the arm lifts the
   wok by its block, the cart moves left and the wok is tipped toward the robot over the plate
   (r15tipwalk.py); under the hood (23 cm above the rim) or right of the cooker it cannot tip;
 - a spatula stand right of the cooker (r15reach: the arm cannot use it, the upright handle
   reaches into the hood), a servo pour-drum holder on the cooker's right side (r15reach: the
   arm cannot load it there; a spot behind the wok works, cfg r15_drum_c), and a thermal +
   colour camera under the hood front.
Optional cfg keys:
 r15_drum_taken (the holder's drum is in the gripper, not the cradle);
 r15_spatula (float, grip-to-edge length m): the spatula is held at the TCP (gripper class),
   r15_spatula_jaw = +-1 picks which way round its keyed block sits in the fingers;
 r15_wok_held (dict(T_tool_wok=4x4)): the wok is held at the TCP by its grip block instead of
   sitting on the cooker (its geoms move to R_tool); r15_plate (bool, default True), r15_plate_c
   (plate position, default PLATE['c']), r15_plate_h (its height: R16 waste bucket for the wok rinse); the slicer out-bowl is left out (cooking-time layout)
   unless r15_keep_slicer_bowl.
Wok frame: origin at the wok's inner bottom point WOK0, axes = world axes."""
import numpy as np,xml.etree.ElementTree as E
from scene import box,fmt
from scipy.spatial.transform import Rotation
WOK0=np.array([.83,.17,.925]);RS,A_RIM=.20,.17;DEPTH=RS-np.sqrt(RS**2-A_RIM**2);RIM_Z=WOK0[2]+DEPTH
COOKER=dict(x=(.63,1.03),y=(.0,.42),z=(.85,.92))
KNOB=dict(x=(.95,1.01),y=(-.035,.0),z=(.86,.91))
HANDLE=dict(root=np.array([.655,.17,1.012]),end=np.array([.617,.17,1.022]),r=.011)
GRIP=dict(c=np.array([.595,.17,1.025]),half=np.array([.022,.015,.015]))   # keyed block 0.235 m from the wok axis, PGC grips across y
PLATE=dict(c=np.array([.43,.13,.85]),r=.12,h=.025)   # plating spot left of the hood (the slicer out-bowl spot); right of the cooker failed (hood + arm base)
STAND=dict(c=np.array([1.12,.36,.85]),r=.035,h=.12)
CAM=dict(x=(.78,.88),y=(.15,.19),z=(1.21,1.25))
# servo pour-drum holder on the cooker's right side: the arm drops a loaded R14 pour drum (Ø80 x 140,
# axis along y) into the cradle before the stir-fry; a servo rolls it on time, so seasoning bursts and
# rim pours (锅边淋: the slots empty onto the right wall) need no arm trip while the arm keeps stirring.
DRUM_HOLD=dict(c=np.array([1.005,.17,1.105]),r=.042,half=.07,post=dict(x=(1.035,1.075),y=(.27,.31),z=(.92,1.15)),servo=dict(x=(1.035,1.085),y=(.245,.27),z=(1.07,1.14)))   # post behind the drum: the fingers take the knob end from the front
def quat(R):return Rotation.from_matrix(R).as_quat()[[3,0,1,2]]
def wok_parts(offset=.003,naz=12):
 """Wok shell as (name, type, pos, size, R) in the wok frame. The tiles' inner faces sit
 offset m outside the true sphere: the spatula's working edge rides 3 mm off the steel in
 the stir bench, so this declares that working gap instead of counting it as a clearance
 violation. Flat tiles tangent to the sphere lie outside it, so they never intrude."""
 P=[('r15_wok_t0','cylinder',[0,0,-offset-.002],[RS*np.sin(np.radians(10)),.002],np.eye(3))]
 C=np.array([0,0,RS]);edges=np.radians([10,22,34,46,58.2])
 for i in range(len(edges)-1):
  tm=(edges[i]+edges[i+1])/2
  for k in range(naz):
   ph=2*np.pi*(k+.5)/naz;r=np.array([np.sin(tm)*np.cos(ph),np.sin(tm)*np.sin(ph),-np.cos(tm)])
   et=np.array([np.cos(tm)*np.cos(ph),np.cos(tm)*np.sin(ph),np.sin(tm)]);ep=np.array([-np.sin(ph),np.cos(ph),0])
   P.append((f'r15_wok_t{i+1}_{k}','box',C+(RS+offset+.002)*r,[RS*np.sin(tm)*np.pi/naz*1.05,RS*(edges[i+1]-edges[i])/2*1.02,.002],np.c_[ep,et,r]))
 return P
def handle_parts():
 """Long handle + keyed grip block, in the wok frame."""
 a,b=HANDLE['root']-WOK0,HANDLE['end']-WOK0
 return [('r15_wok_handle','capsule',np.r_[a,b],[HANDLE['r']],None),('r15_wok_grip','box',GRIP['c']-WOK0,GRIP['half'],np.eye(3))]
def _add(parent,prefix,parts,T=np.eye(4),cls=('1','2'),rgba='.16 .16 .18 1',mass='.000001'):
 for n,t,p,s,R in parts:
  if t=='capsule':
   ft=(T[:3,:3]@p[:3]+T[:3,3]).tolist()+(T[:3,:3]@p[3:]+T[:3,3]).tolist()
   E.SubElement(parent,'geom',name=prefix+n,type='capsule',fromto=fmt(ft),size=fmt(s),rgba=rgba,contype=cls[0],conaffinity=cls[1],mass=mass)
  else:
   E.SubElement(parent,'geom',name=prefix+n,type=t,pos=fmt(T[:3,:3]@np.asarray(p)+T[:3,3]),size=fmt(s),quat=fmt(quat(T[:3,:3]@R)),rgba=rgba,contype=cls[0],conaffinity=cls[1],mass=mass)
# ---- spatula: the same geometry as the stir bench (spatula15.py) ----
import spatula15 as SP
HD=SP.HD
def spatula_tool(grip,jaw_sign=1):
 """Spatula parts in the TOOL frame for a grip point grip m from the blade edge along the
 blade then the handle, plus the blade-frame -> tool-frame rotation. Tool approach (+X) points
 from the grip toward the blade along the handle; the jaws close across the handle (blade
 width); jaw_sign picks which way round the keyed block sits in the fingers."""
 from checker import reference
 b=SP.grip_point(grip)
 Rt=reference.rotation(-HD,[jaw_sign,0,0])    # tool axes in the blade frame
 to_tool=lambda p:Rt.T@(np.asarray(p)-b)
 parts=[(f'R_gripper_spatula_blade{k}','box',to_tool(c),h,Rt.T) for k,(c,h) in enumerate(SP.blade_parts())]
 parts.append(('R_gripper_spatula_handle','capsule',np.r_[to_tool([0,SP.BH,0]),to_tool(b-HD*.03)],[.008],None))
 return parts,Rt,b
def add(tree,world,cfg):
 for g in list(world.iter('geom')):
  if g.get('name') in ('r14_wok','stove','stove_piece1','gas_knob'):
   for par in world.iter():
    if g in list(par):par.remove(g);break
 if not cfg.get('r15_keep_slicer_bowl'):   # cooking-time layout: the slicer's output bowl has been emptied into the wok and parked; its spot is the plating spot
  for g in list(world.iter('geom')):
   if g.get('name','').startswith('slicer_out_bowl'):
    for par in world.iter():
     if g in list(par):par.remove(g);break
 b=lambda n,x,y,z,c=(.8,.8,.8,1):box(world,n,[(x[0]+x[1])/2,(y[0]+y[1])/2,(z[0]+z[1])/2],[x[1]-x[0],y[1]-y[0],z[1]-z[0]],c)
 b('r15_cooker',COOKER['x'],COOKER['y'],COOKER['z'],(.1,.1,.11,1))
 b('r15_knob_servo',KNOB['x'],KNOB['y'],KNOB['z'],(.25,.25,.28,1))
 b('r15_handle_bracket',(.622,.648),(.155,.185),(.92,1.0),(.4,.4,.42,1))
 b('r15_camera',CAM['x'],CAM['y'],CAM['z'],(.2,.2,.22,1))
 DH=dict(DRUM_HOLD,c=np.asarray(cfg.get('r15_drum_c',DRUM_HOLD['c']),float))
 if cfg.get('r15_drum_c') is None:b('r15_drum_post',DH['post']['x'],DH['post']['y'],DH['post']['z'],(.55,.55,.58,1));b('r15_drum_servo',DH['servo']['x'],DH['servo']['y'],DH['servo']['z'],(.25,.25,.28,1))
 if cfg.get('r15_drum_c') is None:b('r15_drum_arm',(1.035,1.075),(.24,.31),(1.14,1.15),(.55,.55,.58,1))   # cradle arm reaches the drum's back end only
 else:b('r15_drum_mount',(DH['c'][0]-.02,DH['c'][0]+.02),(DH['c'][1]+.075,DH['c'][1]+.11),(DH['c'][2]-.01,1.25),(.55,.55,.58,1))   # alternative spot: hangs from the hood
 if not cfg.get('r15_drum_taken'):E.SubElement(world,'geom',name='r15_drum',type='cylinder',pos=fmt(DH['c']),size=fmt([DH['r'],DH['half']]),quat='.707106781187 .707106781187 0 0',rgba='.88 .9 .93 1',contype='1',conaffinity='2',mass='.000001')
 sc=STAND['c'];E.SubElement(world,'geom',name='r15_spatula_stand',type='cylinder',pos=fmt(sc+[0,0,STAND['h']/2]),size=fmt([STAND['r'],STAND['h']/2]),rgba='.6 .6 .62 1',contype='1',conaffinity='2',mass='.000001')
 if cfg.get('r15_plate',True):
  pc=np.asarray(cfg.get('r15_plate_c',PLATE['c']),float);ph=cfg.get('r15_plate_h',PLATE['h']);E.SubElement(world,'geom',name='r15_plate',type='cylinder',pos=fmt(pc+[0,0,ph/2]),size=fmt([PLATE['r'],ph/2]),rgba='.95 .95 .93 1',contype='1',conaffinity='2',mass='.000001')
 T=np.eye(4);T[:3,3]=WOK0
 held=cfg.get('r15_wok_held')
 if held is None:_add(world,'',wok_parts()+handle_parts(),T)
 else:
  # wok held by its grip block: wok-frame parts expressed in the tool frame, given the
  # wok pose relative to the tool (held['T_tool_wok'], 4x4); the grip block is the grasp
  tool=tree.find(".//body[@name='R_tool']")
  _add(tool,'R_gripper_',[p for p in wok_parts(offset=0.)+handle_parts() if p[0]!='r15_wok_grip'],np.asarray(held['T_tool_wok']),cls=('2','3'),mass='.000001')
 if cfg.get('r15_spatula'):
  tool=tree.find(".//body[@name='R_tool']");parts,_,_=spatula_tool(float(cfg['r15_spatula']),cfg.get('r15_spatula_jaw',1))
  for n,t,p,s,R in parts:
   if t=='capsule':E.SubElement(tool,'geom',name=n,type='capsule',fromto=fmt(p),size=fmt(s),rgba='.75 .76 .8 1',contype='2',conaffinity='3',mass='.000001')
   else:E.SubElement(tool,'geom',name=n,type=t,pos=fmt(p),size=fmt(s),quat=fmt(quat(R)),rgba='.75 .76 .8 1',contype='2',conaffinity='3',mass='.000001')
